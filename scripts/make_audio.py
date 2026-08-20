"""Render a two-host podcast script to a single mp3 via the local Chatterbox TTS server.

Script format (see CLAUDE.md "Podcast" workflow): dialogue lines tagged
`A: ...` / `B: ...`; untagged lines continue the current speaker's turn;
`---` lines and YAML frontmatter are ignored.

Usage:
  uv run scripts/make_audio.py "podcast/2026-08-05 script.md"
  uv run scripts/make_audio.py "podcast/2026-08-05 script.md" --out "podcast/2026-08-05.mp3"

Chunks are cached in state/audio_cache/<script name>/ so an interrupted run
resumes where it left off; the cache is deleted after a successful render.
"""

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import requests

# Windows consoles often default to a legacy codepage (e.g. cp932) that can't
# print em-dashes in progress lines; never let logging kill a render.
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout.reconfigure(errors="replace")
    sys.stderr.reconfigure(errors="replace")

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = SCRIPT_DIR / "config.json"


def parse_dialogue(text):
    """Return list of (speaker, text) turns."""
    # strip frontmatter
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4:]
    turns = []
    speaker = None
    buf = []

    def flush():
        nonlocal buf
        if speaker and buf:
            joined = " ".join(buf).strip()
            if joined:
                turns.append((speaker, joined))
        buf = []

    for line in text.splitlines():
        line = line.strip()
        if not line or line == "---" or line.startswith("#"):
            continue
        m = re.match(r"^\*{0,2}([AB])\*{0,2}\s*:\s*(.*)$", line)
        if m:
            flush()
            speaker = m.group(1)
            buf = [m.group(2)]
        elif speaker:
            buf.append(line)
    flush()
    return turns


def chunk_text(text, max_chars):
    """Split on sentence boundaries into pieces <= max_chars."""
    if len(text) <= max_chars:
        return [text]
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks, cur = [], ""
    for s in sentences:
        if cur and len(cur) + len(s) + 1 > max_chars:
            chunks.append(cur)
            cur = s
        else:
            cur = f"{cur} {s}".strip()
    if cur:
        chunks.append(cur)
    return chunks


def synthesize(tts_cfg, speaker, text, out_path):
    host = tts_cfg["hosts"][speaker]
    resp = requests.post(
        f"{tts_cfg['base_url'].rstrip('/')}/v1/audio/speech",
        json={
            "model": tts_cfg.get("model", "chatterbox"),
            "input": text,
            "voice": host["voice"],
            "response_format": "wav",
            "speed": tts_cfg.get("speed", 1.0),
            "seed": host.get("seed"),
        },
        timeout=600,
    )
    resp.raise_for_status()
    out_path.write_bytes(resp.content)


def episode_number(script_path):
    """Episode N = this script's position among all '* script.md' files, by date order."""
    scripts = sorted(p.name for p in script_path.parent.glob("* script.md"))
    try:
        return scripts.index(script_path.name) + 1
    except ValueError:
        return len(scripts) + 1


def script_title(text):
    """Episode title from the script's YAML frontmatter (`title:`), or None."""
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    m = re.search(r"^title:\s*[\"']?(.+?)[\"']?\s*$", text[3:end], re.M)
    return m.group(1) if m else None


def probe_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)],
        capture_output=True, text=True)
    try:
        return float(out.stdout.strip())
    except ValueError:
        return 0.0


def main():
    ap = argparse.ArgumentParser(description="Podcast script -> mp3 via Chatterbox")
    ap.add_argument("script", help="path to the podcast script .md")
    ap.add_argument("--out", help="output mp3 path (default: alongside script, date.mp3)")
    args = ap.parse_args()

    cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    tts = cfg["tts"]
    script_path = Path(args.script)
    if not script_path.exists():
        sys.exit(f"script not found: {script_path}")

    if args.out:
        out_path = Path(args.out)
    else:
        m = re.match(r"(\d{4}-\d{2}-\d{2})", script_path.stem)
        stem = m.group(1) if m else script_path.stem
        out_path = script_path.parent / f"{stem}.mp3"

    script_text = script_path.read_text(encoding="utf-8")
    turns = parse_dialogue(script_text)
    if not turns:
        sys.exit("no dialogue turns found (expected lines starting with 'A:' or 'B:')")

    pieces = []
    for speaker, text in turns:
        for chunk in chunk_text(text, tts.get("max_chunk_chars", 1500)):
            pieces.append((speaker, chunk))
    print(f"{len(turns)} turns -> {len(pieces)} TTS chunks")

    cache = SCRIPT_DIR / "state" / "audio_cache" / script_path.stem
    cache.mkdir(parents=True, exist_ok=True)

    wav_paths = []
    for i, (speaker, chunk) in enumerate(pieces):
        digest = hashlib.sha1(f"{speaker}|{tts['hosts'][speaker]['voice']}|{chunk}"
                              .encode("utf-8")).hexdigest()[:16]
        wav = cache / f"{i:04d}_{speaker}_{digest}.wav"
        if not wav.exists():
            print(f"  [{i + 1}/{len(pieces)}] {speaker}: {chunk[:60]}...")
            synthesize(tts, speaker, chunk, wav)
        wav_paths.append(wav)

    list_file = cache / "concat.txt"
    list_file.write_text(
        "".join(f"file '{p.resolve().as_posix()}'\n" for p in wav_paths),
        encoding="utf-8")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    n = episode_number(script_path)
    # Episode title from script frontmatter; the number lives on as the track tag.
    title = script_title(script_text) or f"Drive Podcast {n}"
    m = re.match(r"(\d{4})-\d{2}-\d{2}", script_path.stem)
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
           "-i", str(list_file)]
    thumb = script_path.parent / "thumbnail.png"
    if thumb.exists():
        cmd += ["-i", str(thumb), "-map", "0:a", "-map", "1:0",
                "-c:v", "mjpeg", "-disposition:v", "attached_pic",
                "-metadata:s:v", "title=Album cover",
                "-metadata:s:v", "comment=Cover (front)"]
    cmd += ["-id3v2_version", "3",
            "-metadata", f"title={title}",
            "-metadata", "artist=Resnene & Bee",
            "-metadata", "album=Drive Podcast",
            "-metadata", f"track={n}"]
    if m:
        cmd += ["-metadata", f"date={m.group(1)}"]
    cmd += ["-c:a", "libmp3lame", "-b:a", "128k", str(out_path)]
    subprocess.run(cmd, check=True)

    minutes = probe_duration(out_path) / 60
    print(f"\nwrote {out_path}  ({minutes:.1f} min)  [{title}"
          f"{', cover embedded' if thumb.exists() else ', no thumbnail.png found'}]")
    if not 45 <= minutes <= 90:
        print(f"WARNING: duration outside the 45-90 min target")
    shutil.rmtree(cache, ignore_errors=True)


if __name__ == "__main__":
    main()
