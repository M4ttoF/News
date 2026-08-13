# News Wiki — Schema

This vault is an LLM-maintained news wiki. The human curates sources and asks questions; Claude does all wiki writing, cross-referencing, and maintenance. Obsidian is the reading UI, so **always use `[[wikilinks]]`** for internal links.

## Layers

- `raw/` — immutable source material (clipped articles, fetched pages). **Never edit or delete anything in `raw/`.** Images live in `raw/assets/`.
- `wiki/` — Claude-generated pages. Claude owns this layer entirely.
- `CLAUDE.md` — this schema. Evolve it with the user as conventions settle.

## Wiki structure

- `wiki/index.md` — catalog of every wiki page, by category, one line each. Update on every ingest. Read it first when answering questions.
- `wiki/log.md` — append-only chronology. Entry format (parseable): `## [YYYY-MM-DD] <op> | <title>` where `<op>` is `ingest`, `query`, `lint`, or `sweep`. Never rewrite old entries.
- `wiki/beats.md` — the beats (standing topics) the user follows. Drives web sweeps and the future auto-clipper. User-directed; Claude edits only on request.
- `wiki/sources/` — one page per ingested source. Filename: `YYYY-MM-DD <short title>.md` (date = publication date, fallback ingest date).
- `wiki/entities/` — people, organizations, places, products. One page per entity that appears in 2+ sources or clearly will recur.
- `wiki/storylines/` — evolving multi-source narratives (the heart of a news wiki), e.g. "Fed rate path 2026". Dated developments, newest first.
- `wiki/topics/` — stable background/concept pages (explainer-style, not time-driven).
- `wiki/briefings/` — filed answers to queries: digests, comparisons, analyses worth keeping.

## Page conventions

Every wiki page gets YAML frontmatter:

```yaml
---
type: source | entity | storyline | topic | briefing
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: []          # broad subject tags, e.g. [economy, ai]
---
```

Source pages additionally: `published: YYYY-MM-DD`, `outlet:`, `url:`, `raw: "<path in raw/>"`, `relevance:` (leave blank on creation — the **user** fills in 1–5 in Obsidian; never set or change it). Ratings are training data for future automatic relevance filtering: once enough accumulate, Claude will add a `relevance_pred:` prediction at ingest (calibrated against the manual ratings + `beats.md`), and manual rating retires when predictions track well.

- Every factual claim on an entity/storyline/topic page must be traceable: cite the source page inline like `([[2026-08-05 Fed holds rates]])`.
- News goes stale: when a new source supersedes a claim, **update the claim and note the change** ("previously reported as X per [[...]]; superseded"). Don't silently delete; don't leave contradictions unflagged.
- Storyline pages: lead with a 2-3 sentence "Where this stands" current-state summary (keep it current), then a dated timeline of developments, newest first.
- Link liberally between pages. Orphan pages are lint findings.

## Workflows

### Ingest (batch, review-after)
The user drops clips into `raw/` (Obsidian Web Clipper) or pastes URLs (fetch → save markdown copy to `raw/` first). A raw file is unprocessed if no `wiki/sources/` page references it in `raw:` frontmatter — check with grep.

For each unprocessed source: read it → write its source page → create/update affected entity, storyline, and topic pages → then once per batch: update `index.md`, append one `ingest` log entry per source, and **end with a chat digest**: sources ingested, pages created/updated, contradictions or notable developments flagged. The user reviews in Obsidian afterward.

Work autonomously through the batch; don't stop to ask per-article questions — flag judgment calls in the digest instead.

### Query
Read `index.md` → open relevant pages → answer with citations to source pages. If the answer is durable/valuable (comparison, analysis, digest), file it into `wiki/briefings/` and index it, logging a `query` entry.

### Sweep (beat search)
On request: read `beats.md`, web-search each beat for significant news since the last `sweep` log entry, present candidate articles with one-line rationales. Fetch approved ones into `raw/` and run Ingest. Log a `sweep` entry.

### Lint
On request: check for contradictions between pages, stale "Where this stands" summaries, orphan pages, entities/storylines mentioned 2+ times without a page, broken wikilinks, unrated source pages (no `relevance:` value), and gaps worth a web search. Fix mechanical issues directly; report judgment calls. Log a `lint` entry.

### Podcast
On request (and later daily): produce a two-host commute podcast from recent sources.

1. Select sources: today's (or since the last `podcast` log entry) with `relevance:` ≥ 3; while ratings are sparse, use all recent sources.
2. Pull in the affected storyline/entity pages — the wiki context is what makes segments richer than single-article summaries.
3. Write `podcast/YYYY-MM-DD script.md`. Format (parsed by `scripts/make_audio.py`):
   - Dialogue lines tagged `A: ...` / `B: ...` — two hosts (both female voices), natural conversational register, disagreements and questions welcome. A (voice Resnene) is the anchor/driver: energetic, enthusiastic. B (voice Bee) is calmer, drier: analysis and color. Both lean on sarcasm — wry asides, deadpan skepticism about hype — without undercutting the facts.
   - `---` between segments; no headings inside dialogue (they'd be read aloud); spell out numbers/abbreviations as speech ("forty-five billion dollars", not "$45bn").
   - Target 8,000–14,000 words ≈ 45–90 min of audio.
   - Structure: cold open + headline rundown → one deep segment per major story → quick hits → sign-off.
4. Run `uv run scripts/make_audio.py "podcast/YYYY-MM-DD script.md"` → `podcast/YYYY-MM-DD.mp3`. The script embeds `podcast/thumbnail.png` as cover art and tags the mp3 `title: Drive Podcast N` / `album: Drive Podcast` / `artist: Resnene & Bee` (N = the script's position among all `* script.md` files by date — don't rename or delete old scripts or numbering shifts). Log a `podcast` entry (add `podcast` to the log ops).

## Pipeline scripts

`scripts/` holds the automation (see `scripts/SETUP.md` for one-time setup and the daily sequence):

- `fetch_articles.py` — drives Firefox (dedicated `news-automation` profile so the user's content-access extensions run) over each source in `scripts/config.json` (initially the FT AI page), extracts articles with Readability, writes clipper-style markdown to `raw/`. Dedupe state in `scripts/state/seen.json`. Flags: `--dry-run`, `--limit N`, `--headless`.
- `make_audio.py` — renders a podcast script to mp3 via the local Chatterbox TTS server (`http://localhost:8090`, OpenAI-compatible `/v1/audio/speech`), one voice per host, ffmpeg concat. Resumable via chunk cache.
- `config.json` — sources, paths, Firefox profile, TTS voices. `podcast/` — scripts + mp3s.

## Planned

- Daily routine: scheduled local Claude Code job running fetch → Ingest → Podcast → make_audio, ending with a chat digest. Wire up once the manual end-to-end pass is proven.
- Automatic relevance: `relevance_pred:` at ingest once manual ratings accumulate (see Page conventions).
