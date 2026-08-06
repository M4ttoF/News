---
type: log
created: 2026-08-05
---

# Log

Append-only record of wiki operations. Entry format: `## [YYYY-MM-DD] <op> | <title>` — ops: `ingest`, `query`, `lint`, `sweep`.

## [2026-08-05] setup | Vault scaffolded
Created wiki structure (sources, entities, storylines, topics, briefings), index, log, beats, and CLAUDE.md schema. No sources ingested yet.

## [2026-08-06] setup | Pipeline scripts built
Added `scripts/fetch_articles.py` (Selenium + Firefox → raw/, FT AI page first source, paywall-aware, dedupe via state/seen.json), `scripts/make_audio.py` (two-host podcast script → mp3 via local Chatterbox TTS at :8090, voices ResNene/Bee), config, SETUP.md. Schema gained `relevance:` rating convention and the Podcast workflow. Verified: link collection (44 links), paywall rejection, TTS render + ffmpeg concat. Pending: user creates `news-automation` Firefox profile with content-access extension.

## [2026-08-06] ingest | Who needs consultants in the age of AI
Source page + fed [[AI and white-collar work]] (new topic).

## [2026-08-06] ingest | Google DeepMind CEO Demis Hassabis steps aside
Source page + new entities [[Google DeepMind]], [[Demis Hassabis]]; Kavukcuoglu succession, Jeff Dean exit.

## [2026-08-06] ingest | Europe must do more to harness its AI ambitions
Source page + new storyline [[Europe's AI push - regulation and sovereignty]].

## [2026-08-06] ingest | LinkedIn time travellers and AI skills
Source page + fed [[AI and white-collar work]].

## [2026-08-06] ingest | Progressive Democrat wins Michigan Senate primary
Source page only — off-beat (US politics; fetched before link scoping fix). Candidate for relevance rating 1.

## [2026-08-06] ingest | OpenAI hits back at Apple trade secrets fight
Source page + new storyline [[OpenAI–Apple trade secrets fight]]; entities [[OpenAI]], [[Apple]].

## [2026-08-06] ingest | Palantir forecasts greater US demand for AI software
Source page + new entity [[Palantir]]; fed sovereignty storyline and [[AI investment boom and bubble fears]].

## [2026-08-06] ingest | Olix triples valuation to 3.3bn
Source page + new storyline [[Nvidia challengers - the AI chip startup wave]].

## [2026-08-06] ingest | Apple struggles with AI bug hunters
Source page + new storyline [[AI and cybersecurity]].

## [2026-08-06] ingest | Situational Awareness got the future right
Source page + new entity [[Situational Awareness]]; anchors [[AI investment boom and bubble fears]].

## [2026-08-06] ingest | EU AI labels cookie banner moment
Source page + new topic [[EU AI Act]].

## [2026-08-06] ingest | Amazon completes 50bn investment in OpenAI
Source page + new entities [[Amazon]], [[Anthropic]] (backfilled across batch), [[OpenAI]].

## [2026-08-06] podcast | Episode 1: sovereignty everywhere
First episode. 10 sources (relevance ≥ 3 per user ratings), ~7,700 words / ~50 min target. Segments: DeepMind shake-up; Amazon–OpenAI $50bn + Situational Awareness fire-sale + chip startup wave; OpenAI–Apple lawsuit; AI × security (Apple bug caps); EU AI Act labels + sovereignty summit + Palantir; consultants quick hit; "connecting the dots" (sovereignty theme). Script: podcast/2026-08-06 script.md. Excluded (relevance 1): LinkedIn time-travel piece, Michigan primary.
