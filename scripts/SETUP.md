# Pipeline setup (one-time)

## Already done (2026-08-05)

- Python env: uv project at the vault root (`pyproject.toml` + `uv.lock`, Python 3.12 pinned in `.python-version`; set up 2026-08-11 — replaces the earlier system-Python `pip install`). Recreate anytime with `uv sync`; deps: selenium, markdownify, requests (Selenium ≥4.6 auto-manages geckodriver)
- `scripts/readability.js` vendored from mozilla/readability
- Chatterbox TTS Server verified at `http://localhost:8090/` (OpenAI-compatible `/v1/audio/speech`)

## You: create the Firefox automation profile

1. In Firefox, open `about:profiles` → **Create a New Profile** → name it `news-automation`.
2. Launch it ("Launch profile in new browser"), then in that window:
   - install the content-access extension you use for FT (and log in to ft.com if you have an account);
   - open https://www.ft.com/artificial-intelligence once and confirm an article is fully readable.
3. Back in `about:profiles`, copy the profile's **Root Directory** path and paste it into
   `scripts/config.json` → `"firefox_profile"` (use forward slashes or doubled backslashes).

Note: the daily run launches Firefox with this profile, so it must not already be open
in another Firefox window when the script runs (your main browsing profile is unaffected).

## Podcast voices (chosen 2026-08-05)

Host A = `ResNene.wav` (energetic, enthusiastic — the anchor), host B = `Bee.wav` (calmer — analysis).
Both female; scripts are written with sarcastic streaks for both. To change voices later, edit
`tts.hosts.A.voice` / `tts.hosts.B.voice` in `config.json` (voice **filenames** from the
Chatterbox UI at http://localhost:8090/). The `seed` values keep each host's delivery consistent
across chunks — leave them.

## Daily pipeline (what the routine will run)

1. `uv run scripts/fetch_articles.py` — new FT articles → `raw/`
2. Claude: Ingest workflow (source/entity/storyline pages, digest)
3. Claude: Podcast workflow → `podcast/YYYY-MM-DD script.md`
4. `uv run scripts/make_audio.py "podcast/YYYY-MM-DD script.md"` → `podcast/YYYY-MM-DD.mp3`

## Paywalled articles: the archive.today fallback

When Readability still sees a paywall/blocked banner after `article_timeout_s`, the run opens
`archive.today/newest/<article url>` in a second tab (reusing whichever mirror host the bypass
banner links to) and extracts from the snapshot instead. Files written this way get
`archive_url:` and `via: archive.today` in their frontmatter; `seen.json` records `via`.

**The security check is yours to click.** archive.today gates some sessions behind a reCAPTCHA.
The script detects it, beeps, prints a prompt, and waits (`archive.captcha_wait_s`, default 180s)
for you to tick the box in the Firefox window it already has open — it never answers one itself.
Solving it once normally covers the rest of the run, since the cookie lands in the
`news-automation` profile. Because of this the archive stage is skipped under `--headless`.

Articles with no snapshot are reported (`no archived snapshot for this article`) and counted as
failures, same as before. Tune under `archive` in `config.json`; `--no-archive` disables the whole
fallback for a run.

## Testing commands

- `uv run scripts/fetch_articles.py --dry-run` — list new article links only
- `uv run scripts/fetch_articles.py --limit 3` — small test batch
- `uv run scripts/fetch_articles.py --limit 1 --no-archive` — direct extraction only (no archive tab)
- `uv run scripts/make_audio.py <script.md>` — resumable; re-run after a crash and it continues
