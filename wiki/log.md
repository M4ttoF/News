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

## [2026-08-12] ingest | Just how big is the hidden leverage of AI hyperscalers
Source page + fed [[AI infrastructure financing]] (new "template: Meta's Beignet" section) and [[AI investment boom and bubble fears]]. Goldman's $1.5tn lease commitments / $1tn uncommenced; Morgan Stanley's $982bn purchase commitments; GAAP ASC 842 mechanics; Fitch/Moody's vs S&P split.

## [2026-08-12] ingest | Google's AI shake-up boosts Brin as Hassabis steps aside
Source page + new storyline [[Google's AI reorganisation]]; new entities [[Sergey Brin]], [[Koray Kavukcuoglu]]; updated [[Google DeepMind]], [[Demis Hassabis]]. **Supersedes the framing** of the 2026-08-05 ingest: this is a London→Silicon Valley relocation of control, not just a title change. Two sourced and mutually contradictory accounts of why Hassabis stepped back — recorded both without adjudicating. Notable detail: AlphaFold's free release logged internally as poor commercial return.

## [2026-08-12] ingest | Google seeks a sharper focus in AI after Hassabis move
Source page + new topic [[Agentic AI and automated science]]; fed [[Google's AI reorganisation]]. Waters's argument that the competitive frontier is moving to agent harnesses + domain data.

## [2026-08-12] ingest | Europe must create an AI money-mobilisation machine
Source page + substantially expanded [[Europe's AI push - regulation and sovereignty]]; cross-linked as the mirror image of [[AI infrastructure financing]] (US over-mobilises, Europe can't mobilise — same week).

## [2026-08-12] ingest | Boehly's Eldridge rolls out AI across portfolio
Source page + fed [[AI infrastructure financing]]. Key transferable fact: Blackstone/Apollo→Anthropic and Bain/TPG/Brookfield→OpenAI, i.e. the AI lenders are also AI buyers and owners of disruptable businesses.

## [2026-08-12] lint | Paywall barrier passed the length check
`raw/2026-08-06 Alibaba's latest AI model puts it back in the great game.md` is a Lex subscription barrier page (756 chars), not an article — it cleared `min_article_chars: 500` and was marked seen, so it will never be retried. **No source page created.** Added "Subscribe to read Lex" / "Subscribe to Premium for access to our flagship investment column" / "What our readers say" to `paywall_markers` in scripts/config.json. Its entry remains in scripts/state/seen.json — remove it manually to re-attempt the fetch.

## [2026-08-12] podcast | Episode 2: the fluent version is cheap
11 sources (all new since Episode 1; ratings still sparse so all used). Script: podcast/2026-08-12 script.md, ~13,600 words — top of the 8,000–14,000 band, ~85–90 min. Segments: (1) Nvidia's $500bn compute financing + the ~$2tn of off-balance-sheet hyperscaler obligations, with the vendor-financing precedent; (2) Google's reorganisation — Brin's untitled return, the AlphaFold detail, four departures, and why they all went to AI-for-science; (3) Stanford Evo 2 synthetic phages + the biosecurity governance split; (4) OpenAI's motion to dismiss (the personal-iCloud allegation); (5) UK police AI misconduct + AI-written tenant complaints as one story. Quick hits: Europe's capital problem as the mirror of segment 1; Eldridge/Boehly. Through-line: the cost of producing fluent text collapsed, the cost of checking it didn't. Cold open and sign-off lean on the Shrimsley column — Altman proposed exactly this show, which the hosts address directly. Rendered via chatterbox (the S2/fish work is parked); no inline `[tags]` since chatterbox reads brackets aloud. Output: podcast/2026-08-12.mp3, **76.2 min**, 521 chunks, cover art embedded (verified: mjpeg 1024×1024 stream + `Drive Podcast 2` tags).

## [2026-08-12] ingest | Nvidia becomes the bank of AI
Source page + new entity [[Nvidia]] and new storyline [[AI infrastructure financing]]; fed [[AI investment boom and bubble fears]]. Note: raw is a *Due Diligence* newsletter; only the Nvidia segment ingested (other segments off-beat). The underlying FT scoop on the $500bn raise is still paywalled in the fetch queue.

## [2026-08-12] ingest | AI creates first synthetic viruses
Source page + new topic [[AI in the life sciences]]. Flagged the direct contradiction between the Stanford team's risk assessment and the Johns Hopkins biosecurity commentary in the same *Science* issue.

## [2026-08-12] ingest | OpenAI says Apple lawsuit aims to stop employees leaving
Source page + updated [[OpenAI–Apple trade secrets fight]], [[OpenAI]], [[Apple]]. Motion to dismiss; October hearing. Noted the 400+ vs "hundreds" employee-count discrepancy as contested framing.

## [2026-08-12] ingest | Senior UK detective under investigation for alleged misuse of AI
Source page + new storyline [[AI in courts and law enforcement]]; fed [[AI and white-collar work]].

## [2026-08-12] ingest | UK letting agents under pressure from AI-assisted tenant complaints
Source page + fed [[AI in courts and law enforcement]], [[AI and white-collar work]] (new "cost shifted, not removed" section), [[AI and cybersecurity]] (same pattern cross-ref).

## [2026-08-12] ingest | Can AI improve my parenting
Source page + one line on [[OpenAI]]. Opinion column — flagged on the page as commentary, not evidence. Likely relevance 1–2.

## [2026-08-06] podcast | Episode 1: sovereignty everywhere
First episode. 10 sources (relevance ≥ 3 per user ratings), ~7,700 words / ~50 min target. Segments: DeepMind shake-up; Amazon–OpenAI $50bn + Situational Awareness fire-sale + chip startup wave; OpenAI–Apple lawsuit; AI × security (Apple bug caps); EU AI Act labels + sovereignty summit + Palantir; consultants quick hit; "connecting the dots" (sovereignty theme). Script: podcast/2026-08-06 script.md. Excluded (relevance 1): LinkedIn time-travel piece, Michigan primary.
