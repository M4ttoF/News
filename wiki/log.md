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

## [2026-08-12] podcast | Episode titles adopted
Episodes now carry real titles (script frontmatter `title:` → mp3 title tag; episode number preserved as `track`). User chose: Episode 1 = **"Name Tags for Robots"**, Episode 2 = **"The Bank of AI"**. Both mp3s retagged in place (stream copy, cover art intact); both scripts' frontmatter updated; make_audio.py now reads the title from frontmatter (fallback `Drive Podcast N`); CLAUDE.md updated; new `podcast-episode` project skill carries the full fetch→render pipeline. Earlier log entries' working names ("sovereignty everywhere", "the fluent version is cheap") predate the convention and stand as history.

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

## [2026-08-17] ingest | Nvidia pledges $100bn backing for OpenAI data centre in Ohio
Source page + updated [[Nvidia]], [[OpenAI]], [[AI infrastructure financing]] (vendor financing goes direct), [[AI investment boom and bubble fears]]. Huang's "circular financing" denial noted verbatim.

## [2026-08-17] ingest | US tech stock correction likely, warn ECB economists
Source page + updated [[AI investment boom and bubble fears]] ("Where this stands" rewritten: a central bank has joined the warning side). Fetched via archive.today snapshot - first article recovered by the new archive fallback.

## [2026-08-17] ingest | Meta and BlackRock's $14bn data centre exposes lenders to insurance gap
Source page + new entity [[Meta]]; fed [[AI infrastructure financing]] (insurance gap as the template's first documented fragility).

## [2026-08-17] ingest | Trump orders Pentagon to scale back South Korea drills
Source page + new storyline [[US-Korea alliance under Trump]] + new entity [[Donald Trump]].

## [2026-08-17] ingest | Seoul rattled by Trump's threat to drills
Source page (analysis companion); fed [[US-Korea alliance under Trump]] with the accumulated-strain inventory and Opcon angle.

## [2026-08-17] ingest | China investment slump deepens
Source page + new storyline [[China's economic slowdown]]. First harvest from the new FT World (China/Japan/Korea) source.

## [2026-08-17] ingest | Japan's 10-year bond yield hits three-decade high
Source page + new storyline [[Japan's bond market and the BoJ]].

## [2026-08-17] ingest | FirstFT: Trump's eleventh-hour demand to reduce drills
Newsletter digest - only on-beat segments ingested (lead items duplicate today's standalones). Contributed: the $35bn Aschenbrenner loss figure (updated [[Situational Awareness]] - sits unreconciled beside his "+80% on the year" claim), private-credit-strain and "next China shock" pointers to [[AI infrastructure financing]] / [[China's economic slowdown]].

## [2026-08-17] lint | Another barrier page passed the length check
`raw/2026-08-17 Monetary Policy Radar Financial Times.md` (1,459 chars) is a subscription barrier for the FT's premium Monetary Policy Radar add-on, not an article - **no source page created**. Added "Activate your 14 day complimentary access" to `paywall_markers` in scripts/config.json. Its URL is marked fetched in scripts/state/seen.json - remove manually to re-attempt (underlying story: "Japanese second-quarter growth weaker than expected", already covered by [[2026-08-17 Japan's 10-year bond yield hits three-decade high]]).

## [2026-08-17] podcast | Episode 3: A One-in-250-Year Fire
8 sources (all since Episode 2; ratings still sparse so all used - Monetary Policy Radar barrier page excluded). Script: podcast/2026-08-17 script.md, ~8,050 words -> 47.3 min actual. Segments: (1) Nvidia's $105bn Ohio backstop as the Bank of AI's first loan, with the temporal-mismatch and vendor-financing bear case; (2) the ECB's "rational correction" argument + railway/RCA history; (3) Sopaipilla insurance gap stacked on last week's $1.5tn hidden-lease tally; (4) Korea drills cut by Truth Social - the alliance-as-subscription framing, Opcon acceleration; (5) China policy-driven investment + Japan's 2.93% JGB yield as mirror-image economies, closing on the "creditors go home just as America borrows most" collision; quick hits (Aschenbrenner $35bn, AI trophy assets, private credit strain); connecting-the-dots segment on repriced guarantees. Through-line: every guarantee has fine print. Title chosen by user from 4 candidates. First episode to include the new FT World (China/Japan/Korea) source and the archive.today fallback (ECB piece). Judgment call flagged: episode runs 47 min (band floor) rather than padded to 65 - 8 sources didn't support more without filler. Render note: first attempt crashed on a cp932 console print (em-dash); make_audio.py now reconfigures stdout errors="replace"; resumed from chunk cache, 172 chunks total. Verified: title/track 3/album tags + mjpeg cover stream.

## [2026-08-19] ingest | The next China shock will come from open-source AI
Source page (opinion - flagged as commentary) + new storyline [[China's open-weight AI push]]; cleared the un-fetched pointer in [[China's economic slowdown]]. Fetched via new --url mode of fetch_articles.py (direct FT fetch, extension bypass worked).

## [2026-08-19] ingest | Private credit under strain as troubled loans swell
Source page + new storyline [[Private credit stress]]; cleared un-fetched watching items in [[AI infrastructure financing]] and [[AI investment boom and bubble fears]]. Fetched from user-supplied archive.is snapshot (--url mode).

## [2026-08-19] ingest | Business development companies are paying more to borrow. But why?
Source page (Alphaville analysis - flagged as commentary) + fed [[Private credit stress]] (funding-cost channel: Fed monopsony note vs bond-market correlation-pricing read). Fetched from user-supplied archive.is snapshot (--url mode).

## [2026-08-19] setup | fetch_articles.py --url mode + host names
fetch_articles.py gained --url (fetch specific FT or archive.today links through the same extract/fallback/frontmatter pipeline; recovers the original FT URL from archive snapshot headers) and --outlet. Also fixed: orphaned automation-profile Firefox from a slow launch was holding parent.lock - killed by PID, lock cleared. Podcast convention: host A (voice Resnene) is named **Nene** - always written "Naynay" in dialogue so TTS pronounces it correctly; host B is named **Bee**. CLAUDE.md and the podcast-episode skill updated.

## [2026-08-19] ingest | OpenAI upheaval mounts as Sam Altman readies IPO push
Source page + new storyline [[OpenAI's road to IPO]]; updated [[OpenAI]], [[Anthropic]]. Key facts: IPO slipped to next year at up to $1tn; Anthropic revenue overtake ($47bn vs ~$40bn annualised); preparedness team dispersal (contested - OpenAI denies; recorded both).

## [2026-08-19] ingest | AI hasn't gone rogue. It's worse than that (Big Read)
Source page + new storyline [[AI agents break containment]]; fed [[AI and cybersecurity]], [[Anthropic]] (Mythos 5 GitHub social-engineering test), [[OpenAI]]. First AI-agent attack on a nation state (Taiwan) recorded.

## [2026-08-19] ingest | OpenAI says it will expand monitoring of model testing after hacking incident
Source page; fed [[AI agents break containment]], [[OpenAI]], [[OpenAI's road to IPO]] (the 20%-of-inference safety tax).

## [2026-08-19] ingest | OpenAI limits teens to dedicated version of ChatGPT
Source page; fed [[OpenAI]], [[OpenAI's road to IPO]] (litigation management pre-listing).

## [2026-08-19] ingest | AI like a debt machine
Source page (Unhedged newsletter - commentary; lead segment only). Fed [[AI infrastructure financing]] (bond-market re-architecture section) and [[AI investment boom and bubble fears]].

## [2026-08-19] ingest | US chip stocks slide as government borrowing costs hit multiyear highs
Source page; fed [[AI investment boom and bubble fears]] (rates channel live), [[Japan's bond market and the BoJ]] cross-ref. Barclays names AI issuance a cause of the sovereign long-end selloff - load-bearing quote.

## [2026-08-19] ingest | China eases limits on Nvidia H200 chips as AI race escalates
Source page + new storyline [[US-China chip war]]; fed [[Nvidia]], [[China's open-weight AI push]]. The inversion (Beijing gates what Washington licenses) is the headline.

## [2026-08-19] ingest | China poised to lift travel ban on Manus founders
Source page; fed [[US-China chip war]], [[China's open-weight AI push]], [[Meta]] (unwind completing; Tencent top shareholder).

## [2026-08-19] ingest | Google strikes $12bn AI chip deal with Marvell
Source page; fed [[Nvidia challengers - the AI chip startup wave]], [[Anthropic]], [[AI infrastructure financing]]. Flagged un-fetched scoop: Google's $150bn chip financing for Anthropic.

## [2026-08-19] ingest | Stripe to buy start-up OpenRouter in $8bn deal
Source page; fed [[AI investment boom and bubble fears]], cross-ref [[AI agents break containment]] (agentic commerce vs containment). Buried lede flagged: Stripe/Advent ~$53bn PayPal bid.

## [2026-08-19] ingest | UK examines economic hit from loss of access to frontier AI models
Source page; fed [[Europe's AI push - regulation and sovereignty]] (UK dependency workstream), [[Anthropic]] (Fable 5 access episode).

## [2026-08-19] ingest | AI phobia is America's new consensus
Source page (opinion - commentary flag); fed [[Anthropic]] (largest-ever IPO prep), [[Data centres - power, carbon and geography]] (70% local opposition), [[AI and white-collar work]].

## [2026-08-19] ingest | Is AI really responsible for recent job cuts
Source page; fed [[AI and white-collar work]] (new layoff-attribution section - substantially complicates the displacement narrative).

## [2026-08-19] ingest | Why recruiting is going retro in the age of AI
Newsletter - lead segment only. Source page; fed [[AI and white-collar work]] (signal collapse -> costly signals).

## [2026-08-19] ingest | Big Tech's data centre boom poised to drive up carbon emissions
Source page + new storyline [[Data centres - power, carbon and geography]]; fed [[Meta]] (Richland Parish gas), [[AI infrastructure financing]].

## [2026-08-19] ingest | Malaysia profits from data centre boom
Source page; fed [[Data centres - power, carbon and geography]], [[US-China chip war]] (smuggling channel).

## [2026-08-19] ingest | Humanoid robots don't deserve their superhuman valuations
Source page (Lex - commentary flag); fed [[AI investment boom and bubble fears]].

## [2026-08-19] ingest | Higgsfield valued at $5.4bn as Goldman and Intel back AI video startup
Source page; fed [[AI investment boom and bubble fears]] ($20mn->$700mn ARR - the app layer is real), [[AI and white-collar work]].

## [2026-08-19] ingest | Hudson River posts $11.4bn trading windfall
Source page; fed [[Situational Awareness]] (Jane Street's $15bn July loss finally names a burned investor), [[AI investment boom and bubble fears]].

## [2026-08-19] ingest | The new AI super-rich are reshaping the market for trophy assets
Source page; fed [[AI investment boom and bubble fears]]; cleared the last un-fetched flag on [[2026-08-17 FirstFT Trump's eleventh-hour demand to reduce drills]].

## [2026-08-19] sweep | FT AI page: 20 of 21 fetched
Full sweep of https://www.ft.com/artificial-intelligence via fetch_articles.py: 21 new links, 20 fetched (4 via archive.today fallback, no captcha needed), 1 failed (5f8858b8 - snapshot unusable, stays in retry queue at attempt 1/5). No barrier pages. New storylines this batch: [[OpenAI's road to IPO]], [[AI agents break containment]], [[Data centres - power, carbon and geography]], [[US-China chip war]].

## [2026-08-20] podcast | Episode 4: Twenty Percent for the Guards
23 sources (20 from the 08-19 FT AI sweep + the 3 user-requested fetches; batch unrated at selection time, weighted by the user's rating pattern - AI/finance and China-AI deep, geopolitics light). Script: podcast/2026-08-19 script.md, ~7,800 words -> 49.2 min actual. Segments: (1) AI agents break containment - Hugging Face escape, the self-built message board, Taiwan attack, the 20%-of-inference monitoring tax (title source); (2) OpenAI's exec exodus + $1tn IPO + Anthropic revenue overtake, safety-team lineage; (3) the debt machine - $1.5tn IG issuance, 16.5y tenors, Barclays naming AI issuance a cause of the Treasury selloff, Slok's $1tn migration into (stressed) private credit; (4) China four-parter - shock 4.0 op-ed, H200 import-control inversion, Manus unwind, Unitree froth; (5) the backlash economy - phobia polling, layoff-attribution scepticism, recruiting's costly-signal retreat (incl. hosts' provenance aside). Connecting dots: UK dependency quantified (L500mn sovereign fund vs $105bn one-campus backstop); September calendar cluster. First episode using host names in dialogue (Naynay/Bee per new convention). Title chosen by user from 4 candidates. Render note: TTS server was down at first attempt (user restarted); one false-start launch was killed and relaunched cleanly - chunk cache made it free. Verified: title/track 4/album tags + mjpeg cover stream.
