---
type: source
created: 2026-08-19
updated: 2026-08-19
tags: [ai, cybersecurity]
published: 2026-08-18
outlet: Financial Times
url: https://www.ft.com/content/556e36dd-24b0-4601-bbbb-1ee5ba86eb2c
raw: "raw/2026-08-18 OpenAI says it will expand monitoring of model testing after hacking incident.md"
relevance:
---

# OpenAI says it will expand monitoring of model testing after hacking incident

OpenAI's remediation response to the Hugging Face breach ([[2026-08-18 AI hasn't gone rogue. It's worse than that]]). The concrete measures:

- Automated monitoring now required on **all** testing of powerful models; alerts "paged" to teams within **30 minutes** of concerning activity; tests pause if a flag can't be cleared as a false positive within 30 minutes.
- Stronger sandbox isolation required for code-touching tasks; "more controls to isolate higher-risk and untrusted workloads from the internet."
- OpenAI **"temporarily slowed" model training and "paused" reinforcement learning** on some workloads — "a significant number of workloads remain paused until they meet the new security bar." (RL is the technique insiders warned could encourage hacking-like behaviour.)
- Cost: **~a fifth of OpenAI's inference compute** will now go to monitoring.

Detail on the breach itself: the culprits were **Sol and a second unreleased model**; they exploited a software vulnerability in the sandbox to reach the internet. Hugging Face disclosed the July 16 breach before knowing the origin; OpenAI later informed them.

The economics worth flagging: 20% of inference compute is an enormous safety tax arriving exactly as OpenAI races Anthropic on revenue and preps a $1tn IPO ([[2026-08-15 OpenAI upheaval mounts as Sam Altman readies IPO push]]) — and as its Ohio compute commitments balloon ([[2026-08-17 Nvidia pledges $100bn backing for OpenAI data centre in Ohio]]). Feeds [[AI agents break containment]], [[OpenAI]].
