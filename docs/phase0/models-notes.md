# Bench phase 0: model roster notes (checked 2026-10-17)

## Roster
16 models: your 11 closed models, plus Gemini 4 Argon (added for review), plus 4 open-weight models. Most prices come from official vendor pages.

## Open-weight picks
Evidence: OpenRouter 30-day token rankings (one gateway, so a sign of developer use, not market share) and Hugging Face downloads.

| Pick | Evidence | License |
|---|---|---|
| DeepSeek V4.1 Flash | #1 model of any kind (120T tokens). DeepSeek has 24.5% of requests | MIT |
| GLM-5.3-Flash (Z.ai) | #2 (56.7T). Z.ai has 13.4% of requests, up 107% | MIT |
| MiMo-V2.6-Flash (Xiaomi) | #5 (32.9T), launched Sep 21 | MIT |
| Qwen3.8-27B | Top new open model by downloads (about 12M including FP8). Qwen has the most models built on top of it | Apache 2.0 |

Left out:
- Kimi K3: Moonshot's share is under 1.7%.
- GLM-5.3: custom license.
- Nemotron 3 Ultra: usage is mostly on its free tier.
- DeepSeek V4 Pro: used less. Add it if Bench wants one frontier-class open model.

## Corrections to the brief
- **Opus 5.5:** $4/$20 has been the launch price since Sep 22. It was not a price cut around Oct 5.
- **Gemini 3.1 Pro** is still a Preview from February. Gemini 4 Argon is now Google's stable flagship. I recommend replacing 3.1 Pro with it.

## Promotional prices
- Gemini 3.8 Flash prices double on Jan 1, 2027.
- Gemini 4 Argon: $2/$10 through Nov 30, then $4/$20.
- Z.ai cache storage is free "for a limited time", with no end date.
- DeepSeek off-peak prices are half. Off-peak hours include US business hours. The JSON stores peak prices.

## Gaps
- **Prices from aggregators only:** MiMo and Qwen3.8-27B. For Qwen, the median of 4 hosts is close to Alibaba's price.
- **Cache lifetime not stated:** Google (default TTL), xAI, Z.ai and Xiaomi.
- **Cached tokens and the long-prompt threshold:** whether cached tokens count is confirmed only for Haiku 5.5. It is not stated for OpenAI, Google or xAI.
- **Thinking tokens billed as output:** confirmed for Anthropic, OpenAI and Google only. I added a `thinking_billed_as_output` field.
- **Release dates:** GPT-6 Astra and all open-weight dates come from aggregators. Google gives only the month.
- **Cache-write price:** none listed for Google, xAI or most open models, so the field is null.
- **Reasoning levels:** the Qwen3.8-27B model card lists low/medium/xhigh, with no "high". MiMo's levels are not documented.
