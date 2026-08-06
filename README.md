# News

An LLM-maintained personal news wiki with a daily AI-narrated commute podcast.

The human curates sources and asks questions; Claude Code does all the wiki writing, cross-referencing, and maintenance. Obsidian is the reading UI. Every day the pipeline fetches new articles, integrates them into an interlinked knowledge base, and turns the relevant ones into a 45–90 minute two-host podcast.

## How it works

```
FT articles ──> fetch_articles.py ──> raw/           (immutable source clips)
                                        │
                                     Claude ingest
                                        │
                                      wiki/           (sources, entities, storylines, topics)
                                        │
                            user rates relevance 1–5 in Obsidian
                                        │
                                Claude podcast script
                                        │
                                 make_audio.py ──> podcast/YYYY-MM-DD.mp3
                                (Chatterbox TTS)
```

- **`raw/`** — clipped/fetched articles, never edited. The source of truth.
- **`wiki/`** — Claude-generated pages: one page per source, plus entities (people/orgs), storylines (evolving narratives with "where this stands" summaries), topics (background explainers), and briefings (saved query answers). `wiki/index.md` catalogs everything; `wiki/log.md` is the append-only operation history; `wiki/beats.md` defines the standing topics being followed.
- **`podcast/`** — daily scripts and rendered mp3s ("Drive Podcast", two hosts: Resnene = energetic anchor, Bee = dry analyst).
- **`scripts/`** — the automation (see below).
- **`CLAUDE.md`** — the schema: page conventions and the Ingest / Query / Sweep / Lint / Podcast workflows Claude follows. This file is what makes the LLM a disciplined wiki maintainer instead of a chatbot.

The design follows the "LLM wiki" pattern: instead of RAG-ing raw documents on every question, the LLM compiles knowledge once into a persistent, interlinked wiki that compounds with every source added. Contradictions get flagged, superseded claims get updated (not silently deleted), and every claim cites its source page.

## Pipeline scripts

| Script | What it does |
|---|---|
| `scripts/fetch_articles.py` | Drives a real Firefox (dedicated `news-automation` profile, so content-access extensions run) over each source index page in `scripts/config.json`, extracts articles with Mozilla Readability, writes clipper-style markdown to `raw/`. Dedupes via `scripts/state/seen.json`; blocked articles retry across runs (up to 5 attempts). Flags: `--dry-run`, `--limit N`, `--headless`. |
| `scripts/make_audio.py` | Parses a `podcast/YYYY-MM-DD script.md` dialogue (`A:` / `B:` turns), synthesizes each turn through a local Chatterbox TTS server (OpenAI-compatible `/v1/audio/speech`, one voice per host), concats with ffmpeg, embeds `podcast/thumbnail.png` + "Drive Podcast N" metadata. Chunk-cached and resumable. |
| `scripts/config.json` | Sources (index URL + link-scope CSS selector + paywall markers), vault paths, Firefox binary/profile, TTS server URL and host voices/seeds. |

## Setup

One-time steps (details in `scripts/SETUP.md`):

1. `py -m pip install selenium markdownify requests` (Python 3.10+; Selenium ≥ 4.6 auto-manages geckodriver). ffmpeg on PATH.
2. Create a dedicated Firefox profile (`about:profiles` → `news-automation`), install your content-access extensions in it, and put its root directory path in `config.json` → `firefox_profile`.
3. Run a [Chatterbox TTS Server](https://github.com/devnen/Chatterbox-TTS-Server) locally (default expected at `http://localhost:8090`); pick two predefined voices in `config.json`.
4. Point Obsidian Web Clipper at `raw/` for manual clipping alongside the automated fetch.

## Daily flow

```
py scripts/fetch_articles.py                      # new articles -> raw/
# Claude Code: "ingest"                           # raw/ -> wiki pages + digest
# (rate new sources 1-5 in Obsidian)              # trains future auto-relevance
# Claude Code: "podcast"                          # wiki -> podcast/YYYY-MM-DD script.md
py scripts/make_audio.py "podcast/<date> script.md"   # script -> mp3
```

The manual ratings are training data: once enough accumulate, ingest will add a `relevance_pred:` prediction per source and manual rating can retire. A scheduled Claude Code job wiring the whole sequence into one unattended morning run is the planned next step (see CLAUDE.md → Planned).

## Repo notes

- Generated mp3s are ~40 MB per episode — consider whether you want them in git history (`podcast/*.mp3` in `.gitignore`, or use Git LFS).
- `scripts/state/` (dedupe + audio chunk cache) and `.obsidian/workspace.json` are runtime state — safe to ignore.
- `raw/` and `wiki/` are the valuable, diffable content; CLAUDE.md is the system's brain. Those are the reason to version this repo.
