# OSWorld feasibility: "Using software for you"

Checked 2026-10-17. Raw rows are in `osworld.json`.

## Verdict
Like-for-like data exists for about 6 of 17 roster models. OSWorld has split into two benchmarks that cannot be compared:
- **OSWorld-Verified** (v1, binary success, 100 steps). Frontier labs no longer report it.
- **OSWorld 2.0** (108 long tasks, 500 steps). It has partial and binary scores, full and offline sets, and three releases.

## Recommended reference
**OSWorld 2.0, offline set, partial score, release v2026.08.08 or v2.1, one score per reasoning level.** Show binary as a second number. Label the release on every score.

## Coverage under the reference
| Model | Eligible | Levels | Cost |
|---|---|---|---|
| Haiku 5.5 | Yes | 5 | Yes |
| Sonnet 5.5 | Yes | 5 | Yes |
| GPT-6 Luna | Yes, two sources | 5+5 | Yes |
| GPT-6.1 Sol | Yes | 1 | Yes |
| GPT-6 Astra | Yes | 1 | Yes |
| Gemini 4 Argon | Yes (best of 3 runs) | 1 | No |
| Opus 5.5 | Secondary source only | 1 | No |
| Fable 5.1, Gemini 3.8 Flash, Kimi K3 | No (other release or set) | – | No |
| Qwen3.8-27B, MiMo-V2.6-Flash, Gemini 3.1 Pro, 3.5 Flash-Lite | OSWorld-Verified only | – | No |
| Grok 4.7, DeepSeek V4.1 Flash/V4 Pro, GLM-5.3-Flash, Mistral Large 3 | None | – | – |

No source publishes tokens per attempt. The official OSWorld 2 leaderboard has token and cost axes, but our tools could not read it.

## Do labs agree on rivals' scores?
Mostly not.
- **GPT-6 Luna at Max:** OpenAI reports 52.7%. Anthropic, running Luna itself, reports 48.9%. At Low, the two report 8.3% and 19.2%.
- **GPT-6 Astra:** OpenAI's own pages give 72.6 and 73.5.
- **Claude Opus 5:** seven figures exist, from 60.3 to 77.67.
- **Claude Sonnet 5:** Google's own run gave 42.6. Anthropic reports 57.0.

When a lab copies a rival's published number, it matches. When a lab re-runs a rival's model, the result differs.

## Surprises
- Anthropic's launch pages say "OSWorld 2.1". Its system cards call the same thing OSWorld 2.0, release v2.1.
- Opus 5.5 scores 81.8 on what looks like the full set and 87.2 on the offline set.
- Partial and binary scores are far apart: Haiku 5.5 scores 72.4% partial but only 37.1% binary.
- Google left out Anthropic models, saying Anthropic does not report the offline set alone. That stopped being true on Oct 7.
- The open-weight Qwen3.8 flagship is text-only. The 86.1 score belongs to the hosted Qwen3.8-Max.

## Evidence limits
- Per-level values were read from charts through secondary write-ups. Two sources agree on Haiku. Sonnet, Luna (OpenAI) and 6.1 Sol each rest on one source.
- Our tools truncated the system-card PDFs before the OSWorld section, so binary scores are secondary quotes.
- Next step: confirm these values in a browser.
