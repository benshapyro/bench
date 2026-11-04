# Bench — Phase 0 Data Check Report

**Date:** October 17, 2026
**Scope:**
- the model list and prices,
- one job filled in depth ("Using software for you," OSWorld),
- a coverage scan of the other four jobs,
- where "thinking" text usage is published.

**Raw data:** `models.json`, `osworld.json`, `coverage.json` and `usage.json`, each with a notes file, all in this folder.

---

## Bottom line

1. **Permission is the main blocker, not whether data exists.** The best independent scores come from two sources:
   - **Artificial Analysis**, whose terms forbid republishing without a license,
   - **Vals AI**, whose pages say "all rights reserved."

   Scores the labs publish themselves can be cited, but each lab picks its tests and measures competitors itself. That last point is an inference, not legal advice.
2. **No one publishes, in a form we can show, how much "thinking" each model does at each reasoning level.** For accurate monthly bills, Bench has to measure this itself.
3. **Two jobs have strong data. Three are thin or a poor fit:**
   - Building software and Reading charts and documents each cover 13–15 models on one consistent test.
   - Customer service and Using software for you have only 4–6 comparable models.
   - Writing and analysis has no good displayable benchmark (details below).
4. **A test score can be measured in very different ways.** Labs disagree when they re-run each other's models. Partial-credit and full-pass scores can differ by about two times. Some writing benchmarks are relative ratings, not percentages.

---

## 1. Model list (confirmed)

| Lab | Models | Price per million tokens (in / out) | Notes |
|---|---|---|---|
| Anthropic | Opus 5.5, Sonnet 5.5, Haiku 5.5, Fable 5.1 | $4/$20, $2/$10, $0.10/$0.50, $10/$50 | Haiku 5.5: the whole request costs $0.50/$2.50 once a prompt passes 100K tokens, and cached text counts toward the 100K |
| OpenAI | GPT-6 Astra, GPT-6.1 Sol, GPT-6 Luna | $10/$50, $2/$10, $0.10/$0.50 | Over 272K tokens: 2× input, 1.5× output |
| Google | **Gemini 4 Argon** (replaces 3.1 Pro), 3.8 Flash, 3.5 Flash-Lite | $2/$10, $0.75/$3.75, $0.30/$2.50 | Argon rises to $4/$20 on Nov 30. 3.8 Flash doubles on Jan 1, 2027 |
| xAI | Grok 4.7 | $2/$6 | Doubles at 200K+ tokens |
| Open-weight | DeepSeek V4.1 Flash, GLM-5.3-Flash, MiMo-V2.6-Flash, Qwen3.8-27B | $0.30/$1.20, $0.15/$0.50, $0.14/$0.28, ~$0.42/$2.60 | Chosen by actual usage (OpenRouter, last 30 days) and downloads. DeepSeek is half price off-peak, which covers US business hours. MiMo and Qwen prices come from aggregator sites only |

**Caching gaps:** how long cached text stays cheap is published only by Anthropic (5 minutes, or 1 hour at a higher price) and OpenAI (at least 30 minutes). Google, xAI and the open-weight providers don't state it.

## 2. Coverage by job

| Job | Best main benchmark | Comparable models | Source and permission | Verdict |
|---|---|---|---|---|
| Building software | Terminal-Bench 4.0, Vals AI's run (one setup for every model, average of 3 runs) | 15 of 17 | Vals AI: "all rights reserved"; permission needed | **Strong** if permitted |
| Reading charts and documents | GDP.pdf (Surge AI; real professional PDFs, graded on all required facts) | 13 of 17 | Surge's public leaderboard; license not stated (Epoch republishes it but notes the original license applies) | **Strong** if permitted |
| Writing and analysis | GDPval-AA (Artificial Analysis) | 17 of 17 | Needs an Artificial Analysis license | **Poor fit without a license.** The fallback, Vals Index, is 52% finance, 37% coding, 8% legal and 3% tax, so it isn't a writing test |
| Customer service | τ³-Banking (τ²-bench is maxed out at ~99%) | 4–5 displayable | Mostly Artificial Analysis | **Thin** |
| Using software for you | OSWorld 2.0, offline set, partial credit | 6 of 15 (all lab-reported) | Lab pages | **Thin** (details below) |

Not usable: SWE-bench (no current lab reports it) and MMMU-Pro and CharXiv (labs stopped reporting them).

## 3. The in-depth job: Using software for you (OSWorld)

- **The test has split into two versions** that can't be compared:
  - OSWorld-Verified (older, pass/fail),
  - OSWorld 2.0 (longer tasks, partial credit).

  The big labs now report only 2.0.
- **Comparable scores exist for 6 models:**
  - Haiku 5.5, Sonnet 5.5 and GPT-6 Luna: 5 reasoning levels each, with cost per attempt,
  - GPT-6.1 Sol, GPT-6 Astra and Gemini 4 Argon: 1 level each.

  Opus 5.5's 87.2% has been found only in a secondary write-up so far. Google reports Argon's best of 3 runs, which flatters it against single-run scores.
- **Labs disagree when they test each other's models.** GPT-6 Luna at Max scored 52.7% when OpenAI ran it and 48.9% when Anthropic ran it. At Low the figures were 8.3% vs 19.2%. This supports the like-for-like rule.
- **Partial credit vs full pass:** Haiku 5.5 gets 72.4% partial credit but fully completes 37.1% of tasks. A buyer would read these very differently.
- **No source publishes tokens per attempt** for this test.

**Checked directly against Anthropic's Haiku 5.5 page:**
- OSWorld 2.1 offline subset, partial credit: Haiku 5.5 72.4%, GPT-6 Luna 48.9%, Sonnet 5.5 83.9%.
- The full Haiku 5.5 price table and the 100K threshold.

The level-by-level chart values come from secondary write-ups. Two sources agree on Haiku's values. The others rest on one source each.

## 4. Thinking-text usage (what the monthly bill depends on)

| Source | Coverage of our models | Detail by reasoning level | Can we display it? |
|---|---|---|---|
| Artificial Analysis | All 15, about 52 model-and-level combinations | Yes | No, not without a license |
| Lab launch charts (cost per attempt) | 7 (Claude models, Astra, 6.1 Sol, Luna) | Yes, as chart images only | Citable as facts (inference); lab-chosen tests |
| Epoch AI | 4 | No token or cost data | Yes (CC BY) |
| OpenRouter | Most | Total tokens only; no split between thinking and visible text | Yes (CC BY) |

How big the effect is:
- Thinking can be about 1 to over 100 times the length of the visible answer, depending on the model, level and task.
- Specific ratios by model and level came from Artificial Analysis and are kept private, since its terms forbid republishing.


---

## 5. Decisions needed from Ben

1. **Ask for permission to display scores.** Email Vals AI, Surge AI and Artificial Analysis to ask for permission to display their scores with credit and a link. Ask Artificial Analysis for a license quote. Until a source says yes, its numbers are used privately to build and test, not published. *Recommended.*
2. **Measure thinking usage ourselves.** Run about 25 typical business tasks on each model at each reasoning level, about 1,500 runs. Inferred cost: a few hundred dollars in lab fees. This gives real, publishable usage numbers sized to business tasks. It reverses the spec's "no running our own tests in v0." *Recommended.*
3. **Set a minimum coverage rule for v0 jobs.** A job launches only if at least 8 models have comparable, displayable scores. Other jobs appear as "Coming soon," with a note on what's missing. With today's data, only Building software and Reading charts and documents qualify, and only once permitted. *Recommended.*

## 6. Calls made (no decision needed unless Ben disagrees)

- **Model list:** Gemini 4 Argon replaces Gemini 3.1 Pro. The open-weight picks are chosen by real usage.
- **DeepSeek price:** uses the peak price (the cautious figure), with an off-peak note.
- **Reference conditions:**
  - Terminal-Bench 4.0 via Vals AI's run,
  - GDP.pdf, all-criteria score,
  - OSWorld 2.0, offline set, partial credit, with the full-pass rate shown alongside where it exists.
- **Rating-style benchmarks** (GDPval-AA, if licensed) are shown as "wins X% of head-to-heads against a fixed reference model," not "% of the leader." Their zero point is arbitrary, so % of the leader would mislead.
- **Writing and analysis:** if Artificial Analysis declines, rename the job to match what Vals Index measures ("General business work: finance, coding, legal, tax") rather than call it writing.
- **Partial credit vs full pass** for "Using software for you" is decided only if that job reaches the coverage bar.

## 7. Spec changes these findings imply (not yet made)

- Section 4 (jobs): update the main benchmarks and the reference conditions.
- Section 5.1 (score): add the head-to-head exception for rating-style benchmarks.
- Section 5.2 (cost): thinking text comes from Bench's own measurements; estimates fall back to these.
- Section 6.1 (sources): the permission status of each source.
- Section 11 (later): move "running Bench's own tests" into v0 for usage only, if decision 2 is yes.
- Section 13 (risks): add "permission refused" and "labs disagree on rival re-runs."

---

## Sources (main)

- [Anthropic: Claude Haiku 5.5](https://www.anthropic.com/claude-haiku-5-5), checked directly
- [Vals AI: Vals Index](https://vals.ai/benchmarks/vals_index), checked directly
- [Vals AI: Finance Agent](https://vals.ai/benchmarks/finance_agent)
- [Epoch AI: GDP.pdf](https://epoch.ai/benchmarks/gdp-pdf)
- [Epoch AI: Use this data](https://epoch.ai/benchmarks/use-this-data)
- [Artificial Analysis data API](https://artificialanalysis.ai/data-api)
- [ActuIA: AI API pricing in October 2026](https://www.actuia.com/en/news/ai-api-pricing-in-october-2026-050-to-50-for-output/)
- [MorphLLM: OpenAI API pricing](https://www.morphllm.com/openai-api-pricing)
- [Mem0: Gemini API pricing](https://mem0.ai/library/llms-and-models/gemini-api-pricing)
- [BenchLM: xAI API pricing](https://benchlm.ai/xai/api-pricing)
- Full source links per number are in the JSON files.
