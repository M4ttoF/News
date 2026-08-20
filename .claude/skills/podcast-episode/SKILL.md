---
name: podcast-episode
description: Run the full Drive Podcast episode pipeline for the News vault, end to end - fetch new FT articles into raw/, ingest them into the wiki, write a titled two-host script, render it to mp3 via the local chatterbox TTS server, and verify the finished file's metadata (episode title + track number + cover art). Use this whenever the user asks to make an episode, create a new podcast, run the podcast pipeline, do "today's episode", "fetch and make the podcast", or any request that combines fetching news with producing audio. Also use it for partial runs - "just write the script", "re-render the episode", "the render died, resume it" - by entering the pipeline at the right stage.
---

# Podcast Episode Pipeline

Produce one episode of the Drive Podcast: fetch → ingest → script → render → verify. Each stage leaves durable state, so the pipeline is resumable — always check what already exists before redoing a stage.

CLAUDE.md is the authority on wiki schema and script format; this skill adds the operational knowledge (failure modes, timing, verification) that CLAUDE.md doesn't carry.

## Stage 0 — Determine where you're entering

Check state and skip completed stages:

- Unprocessed raw files? `grep` raw filenames against `wiki/sources/` frontmatter `raw:` fields (a raw file is unprocessed if no source page references it).
- Script already written? Look for `podcast/YYYY-MM-DD script.md` newer than the last `podcast` entry in `wiki/log.md`.
- Render in progress or interrupted? Chunk cache at `scripts/state/audio_cache/<script stem>/` — if it has wavs but no mp3 exists, resume by re-running the render (it picks up where it left off).

## Stage 1 — Fetch

```bash
uv run scripts/fetch_articles.py
```

Run it in the background (it drives visible Firefox; ~20s per article plus index load). Then read the run summary and expect these failure modes:

- **Index page timeout** ("Navigation timed out"): transient — retry once. Nothing was fetched, no state changed.
- **Paywalled results**: normal on the first pass. Failed URLs are *not* marked seen and retry on the next run (up to `max_fetch_attempts`). **Run the script again if the first pass leaves paywalled links** — second passes routinely recover several more articles (in one real run: 6 of 25 on pass one, 6 more on pass two). Stop when a pass recovers nothing new.
- **Barrier pages that pass the length check**: a subscription page can exceed `min_article_chars` and get saved as a "successful" fetch — and marked seen, so it will never be retried. Before ingesting, open any suspiciously short raw file (< ~1,500 chars) and check for subscription boilerplate ("Subscribe to read", "What our readers say"). If found: don't ingest it, add its distinctive strings to `paywall_markers` in `scripts/config.json`, log a `lint` entry, and note that its URL must be manually removed from `scripts/state/seen.json` to re-attempt.

Report the fetch hit rate to the user — a degrading paywall-bypass rate is a maintenance signal, not just noise.

## Stage 2 — Ingest

Follow the CLAUDE.md Ingest workflow exactly (source pages → entity/storyline/topic pages → index → one log entry per source → chat digest). Skill-specific additions:

- **Newsletter raws** (Due Diligence etc.): ingest only the on-beat segments; say so on the source page and in the log.
- **Opinion columns**: mark them as commentary on the source page so the script treats them as color, not evidence.
- **Contradictions between sources** are podcast material — flag them in the digest and consider them for the script (two sourced accounts of the same event make a good segment).
- Leave `relevance:` blank on every new source page; the user rates in Obsidian.

## Stage 3 — Script

Selection per CLAUDE.md: sources since the last `podcast` log entry with `relevance:` ≥ 3; while ratings are sparse, use all recent sources. Pull the affected storyline/entity pages — wiki context is what makes segments richer than article summaries.

Write `podcast/YYYY-MM-DD script.md`. Frontmatter now carries the episode title:

```yaml
---
type: podcast-script
title: <episode title — becomes the mp3 title tag>
created: YYYY-MM-DD
sources: <count>
target_minutes: <target>
---
```

**Title convention**: every episode gets a real title. Propose 3–5 candidates to the user before rendering *if they're available*; in an unattended run, pick the best one yourself and flag the choice in the digest. Good titles are short, concrete, and taken from the episode's strongest image or line ("The Bank of AI", "A Desk Beside Brin") — not theme summaries ("AI News Roundup August 12"). The episode *number* is not in the title; it's preserved as the `track` metadata tag, derived from the script's position among all `* script.md` files (never rename or delete old scripts — numbering shifts).

Format rules that have burned us (all because the TTS reads text literally):

- `A:` / `B:` dialogue lines only; `---` between segments; **no headings** inside dialogue.
- **No bracketed stage directions** — chatterbox reads `[laughs]` aloud. Write the reaction into the words ("Ha! That's the whole thing, isn't it."). (The parked S2/fish backend *does* interpret `[tags]` — that's a backend difference to reconcile if switching.)
- Spell out numbers, currencies, abbreviations as speech: "forty-five billion dollars", "K K R", "S and P", "Gov dot U K".
- Personas: A is named **Nene** (voice Resnene) — anchors: energetic, drives transitions. B is named **Bee** (voice Bee) — drier: analysis, skepticism, the deflating fact. In dialogue text spell Nene's name **"Naynay"** (TTS mispronounces "Nene"); metadata and page text keep "Nene". Both sarcastic without undercutting facts. Give them real disagreements and let one correct the other.
- Length: 8,000–14,000 words. Empirical rate: **~178 words/min** (13,600 words → 76 min), so 8k ≈ 45 min, 14k ≈ 80 min.
- Structure: cold open + headline rundown → one deep segment per major story → quick hits → sign-off. Cross-reference earlier episodes when a story develops ("last week we said X — that undersold it").

If new articles land mid-pipeline (e.g., a fetch retry recovers more), judge whether they change the episode. If yes: stop the render early (`TaskStop`), ingest, revise the script, re-render — cached chunks up to the first changed turn are reused.

## Stage 4 — Render

Preflight, then render in the background:

```bash
uv run scripts/make_audio.py "podcast/YYYY-MM-DD script.md"
```

- Preflight: chatterbox must answer at `http://localhost:8090/v1/models`; `podcast/thumbnail.png` should exist (embedded automatically as cover art).
- Monitor via chunk count in `scripts/state/audio_cache/<stem>/`, not by waiting. Chunks cache individually — an interrupted or killed render resumes with no lost work; only chunks after an edit point re-render.
- The script prints a duration warning outside 45–90 min; it deletes the chunk cache only after success.

## Stage 5 — Verify and deliver

Never report the render done without checking the artifact:

```bash
ffprobe -v error -show_entries "format_tags=title,artist,album,track,date" -show_entries "stream=codec_type,codec_name" -of default=noprint_wrappers=1 "podcast/YYYY-MM-DD.mp3"
```

Expect: the frontmatter `title` as the title tag (fallback `Drive Podcast N` for untitled scripts), `artist=Resnene & Bee`, `album=Drive Podcast`, `track=<episode N>`, `date=<year>`, and an `mjpeg` video stream (the embedded cover). A missing mjpeg stream means `thumbnail.png` wasn't found at render time.

Then:

1. Append the `podcast` log entry to `wiki/log.md` (episode title, source count, word count, duration, segments, judgment calls).
2. Send the mp3 to the user with duration and title in the caption.
3. Close with the digest if the run included fetch/ingest: sources in, pages touched, contradictions flagged, anything left un-fetched.

## Timing expectations (set these with the user up front)

| Stage | Rough cost |
|---|---|
| Fetch | 5–15 min per pass, often 2 passes |
| Ingest + script | the thinking work — varies |
| Render | minutes-per-chunk varies with server load; 500+ chunks for a full episode. Check chunk-count progress early rather than trusting projections; past wall-clock estimates have been badly wrong in both directions |
| Verify | seconds |
