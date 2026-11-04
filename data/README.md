# Bench v0 score data (Phase 1b and 1g)

Recorded 2026-10-29. Covers the 15 v0 models on each job's main benchmark, stored as spec section 6.2 describes.

| File | What it holds |
|---|---|
| `results.json` | 80 scores. Each has the model, reasoning level (lab name + position), benchmark, score, test conditions, label, source link and date, date recorded, cost per attempt where published, and a `check` field saying how the number was confirmed |
| `models.json` | The 15 models with prices (carried over from Phase 0; Gemini 3.1 Pro dropped) and reasoning levels with positions |
| `benchmarks.json` | The 5 main benchmarks with reference conditions and guessing score (0 for all; none is multiple choice) |
| `jobs.json` | The 5 jobs. Preset tasks are still empty; they come from step 1(c) |

Artificial Analysis-only numbers are left out completely (they stay in `phase0/` for private use).

## How to read a result

- `kind: main` is the score that counts. `reference_conditions_met: true` means it's eligible for leader and best value.
- `kind: full_pass` is the full-completion rate shown beside the OSWorld partial-credit score.
- `non_reference`, `competitor_run`, `older_version`, `superseded_snapshot` and `unverified_candidate` rows go under details with a warning. They never decide.
- `check.status` is `checked` (read on the original page today), `seen earlier` (seen on the original page Oct 17, not visible now), or `unverified` (secondary source only; needs a browser check).

## Coverage

| Job | Main benchmark | Models compared | Left out |
|---|---|---|---|
| Building software | Terminal-Bench 4.0 (Vals AI run, updated Oct 26) | 13 of 15 | Gemini 3.5 Flash-Lite, Qwen3.8-27B (not run by Vals) |
| General business work | Vals Index v2.2 (updated Oct 27) | 12 of 15 | Fable 5.1 (on v2.1, missing from v2.2), Flash-Lite, Qwen3.8-27B |
| Reading charts and documents | GDP.pdf (Surge AI) | 12 of 15 | Haiku 5.5, MiMo-V2.6-Flash, Qwen3.8-27B |
| Using software for you | OSWorld 2.0, offline set, partial credit | 6 of 15 | Opus 5.5 (see below), Fable 5.1, Gemini 3.8 Flash (other task set or release), and 6 models with no OSWorld 2.0 score |
| Customer service | τ³-Banking (Sierra board via Mercor) | 5 of 15 | Everyone else: the board shows only its top 5, and the rest of the data is Artificial Analysis-only |

## What changed since Phase 0

- **Vals Index moved to v2.2 on Oct 27.** Every score changed (Sonnet 5.5 now leads at 70.85%, not Argon). All v2.1 numbers were replaced. Fable 5.1 isn't on v2.2.
- **DeepSeek V4.1 Flash now has a newer snapshot, "1017",** which is what DeepSeek's API serves. Vals scores it much higher: 31.82% vs 19.70% on Terminal-Bench, 61.26% on Vals Index. I used 1017 as the main score and kept the old snapshot under details.
- **Gemini 4 Argon joined the τ³-Banking board at 58.1%** and leads it. That pushed Gemini 3.8 Flash (48.8%) off the visible top 5, so its number is marked "seen earlier."
- **Every Anthropic chart value is now exact.** The Haiku, Opus, Sonnet and Fable pages embed each chart's raw data, so the level-by-level OSWorld and Terminal-Bench numbers and costs come straight from Anthropic, not from secondary write-ups. All matched Phase 0.
- **Gemini 4 Argon's OSWorld score is best of 3 runs,** confirmed in Google's methodology PDF.

## Still unverified (needs a browser)

My tools can't open openai.com or the system-card PDFs. These numbers rest on secondary write-ups:

1. **Opus 5.5 OSWorld 87.2% (offline).** On no Anthropic web page. A write-up attributes it to the Haiku 5.5 system card, section 8.9.3, page 127. Left out of the job until confirmed. Anthropic's own Opus page shows 81.8%, which looks like the full task set.
2. **GPT-6 Luna OSWorld at 5 levels** (8.3, 31.5, 41.4, 46.7, 52.7) from OpenAI's Sol and Luna post chart.
3. **GPT-6.1 Sol OSWorld 71.4%** at Max from OpenAI's 6.1 Sol post chart (one secondary source, but it agrees with the page's own text).
4. **GPT-6 Astra OSWorld 72.6%** from OpenAI's Astra page text (Google's Argon card repeats the same number).
5. **Full-pass rates** for Haiku 5.5 (37.1%) and Sonnet 5.5 (48.8%), from the Haiku 5.5 system card.

## Calls I made

- **GPT-6 Luna on OSWorld:** OpenAI's own run is the main score; Anthropic's re-run sits under details. This matches how every other model is sourced (its own lab), but it's the less certain of the two numbers.
- **τ³-Banking version:** the board doesn't say which version it uses. The spec asks for v1.0.1 or later. I kept the scores, with a note.
- **Reasoning level not stated:** Vals AI doesn't publish the effort level, so those rows have a null level. Surge, Mercor and the labs do, and are recorded as shown.
