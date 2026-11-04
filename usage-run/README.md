# Bench usage run (Phase 1c and 1d)

**Status, Oct 29 2026:** tasks written, presets proposed, script built and tested offline. Not run yet: it needs API keys for Anthropic, OpenAI, Google, xAI and OpenRouter.

The run measures how many tokens each of the 15 v0 models reads, writes and spends thinking on 8 typical business tasks, at 3 reasoning levels each (spec 5.2). Answers are not graded.

## What's here

| File | What it is |
|---|---|
| `tasks/*.json` | The 8 tasks, frozen. Each has a system prompt, a user message, its job, and its size |
| `build_tasks.py` | Rebuilds `tasks/` exactly (fixed seed). Only needed if a task is edited |
| `models.json` | The 15 models, their API IDs and the 3 levels measured for each |
| `presets.json` | Proposed preset task for each job (pages in, pages out, repeated share) |
| `run_usage.py` | The runner: `plan`, `probe`, `submit`, `status`, `collect` |
| `test_offline.py` | Runs submit, status and collect against fake APIs. Passes for all 360 requests |

## The 8 tasks

Two tasks for the three jobs with the most comparable models, one for the two thin jobs (Customer service has 4–5 comparable models, Using software has 6). Each task has a trap or judgment call, so models think the way they would on real work.

| ID | Job | Task | In (pages) | Out (pages) |
|---|---|---|---|---|
| W1 | Writing and analysis | Turn a quarter's sales tables, regional notes, margin bridge and inventory into a one-page leadership memo | 4.1 | 1 |
| W2 | Writing and analysis | Compare two vendor proposals against an RFP: 3-year cost with growth, risky clauses, unmet requirements, a recommendation | 4.0 | 2 |
| C1 | Customer service | Reply to a customer with four issues (a burn from a skillet, final-sale towels, late express shipping, a sleep-trial question), following a 2-page policy and naming action codes | 2.6 | 0.5 |
| U1 | Using software for you | One step of an agent creating an invoice from an email: the customer search shows the wrong entity highlighted, the PO and terms differ from the defaults, and the detention rule conflicts with the contract | 2.7 | 0.3 |
| S1 | Building software | Fix a proration bug from failing tests and a support ticket (`timedelta.seconds` instead of `total_seconds()`, in two places). The tests pass once fixed | 3.4 | 1 |
| S2 | Building software | Add a finance-only, streaming CSV export to a Flask expense app, safe against spreadsheet formula injection | 5.0 | 3 |
| R1 | Reading charts and documents | Pull 12 facts from a messy annual-report PDF extraction, including a leverage ratio that doesn't match the company's own figure | 4.1 | 1 |
| R2 | Reading charts and documents | Three-way match of an OCR'd PO, packing slip and invoice (short shipment, price change, arithmetic error, freight and tax the PO excludes) | 1.4 | 0.5 |

Sizes are estimates (about 4 characters per token, 650 tokens per page). The run records each lab's real counts, which also give each lab's tokens per page.

**Known gap:** all tasks are text. Reading charts and scans with images would cost differently, because each lab counts image tokens its own way. Image tasks can be added later.

## Proposed presets

| Job | One task means | Pages in | Pages out | Repeated |
|---|---|---|---|---|
| Writing and analysis | one report, memo or brief | 4 | 1.5 | 10% |
| Customer service | one conversation, about 4 replies | 12 | 2 | 85% |
| Using software for you | one job in an app, about 12 steps | 32 | 3.5 | 85% |
| Building software | one bug fix or small feature | 20 | 3 | 60% |
| Reading charts and documents | one document or set checked | 3 | 0.75 | 10% |

Reasons are in `presets.json`. Two choices to check:
- **Customer service counts a conversation, not a reply.** The spec's example (3 pages in, half a page out) is one reply. Buyers count conversations, so the preset is 4 replies. The repeated share is high because the policy and earlier turns are re-sent within minutes.
- **The three agent-style jobs are multi-step.** U1, S1 and S2 are single requests. The presets are whole tasks, so thinking is scaled up from the measured step by the ratio of pages in (spec 5.2). Those costs will carry the Estimated label, as the spec requires when sizes differ by more than 2×.

## Levels measured

Lowest level that thinks, the lab's default, and the highest level. Levels where thinking is off (OpenAI's `none`) are not measured: their thinking is zero by definition.

| Lab | Lowest | Default | Highest | Route |
|---|---|---|---|---|
| Anthropic (4 models) | low | medium (Opus, Haiku) or high (Sonnet, Fable) | max | Batch, half price |
| OpenAI (3) | low | medium | max | Batch, half price |
| Google (3) | low (Argon), minimal (Flash, Flash-Lite) | medium | high | Batch, half price |
| xAI Grok 4.7 | low | high | xhigh | Direct, no batch discount offered |
| Open-weight via OpenRouter (4) | low | no setting (host's default) | high | Direct, no batch API |

Checked against lab docs: Anthropic's levels, GPT-6 Luna's levels and default, Gemini 4 Argon's levels and default, and the OpenRouter slugs for DeepSeek, GLM and MiMo. Assumed and marked `verify` in `models.json`: the GPT-6 Astra and GPT-6.1 Sol IDs, the two Gemini Flash IDs and their `minimal` level, Grok 4.7's levels (from a secondary write-up), and the Qwen3.8-27B slug. `probe` checks all of these for a few cents before the real run.

## Cost

`python run_usage.py plan` estimates **about $14** for all 360 requests, assuming 800, 3,000 and 12,000 thinking tokens per task at the three levels. If every highest-level answer used its full output ceiling, the cost would be about $59. The spec's $25–40 assumed longer thinking. The real number depends on how much the top levels think, which is what this run measures.

## How to run

```
pip install anthropic openai google-genai
export ANTHROPIC_API_KEY=... OPENAI_API_KEY=... GEMINI_API_KEY=... XAI_API_KEY=... OPENROUTER_API_KEY=...

python run_usage.py plan          # matrix and cost estimate, no keys needed
python run_usage.py probe         # 45 tiny requests; fix models.json for anything marked BAD
python run_usage.py submit        # starts batches and sends the xAI and OpenRouter requests; prints a run id
python run_usage.py status RUN_ID
python run_usage.py collect RUN_ID
```

Batches usually finish within an hour (24 hours at most). `collect` writes `runs/RUN_ID/results.csv` (one row per request) and `summary.csv` (one row per model and level: mean, min and max thinking tokens, thinking per input page, and tokens per page). Every command takes `--models` and `--providers` to run part of the matrix, for example to re-send failures. `submit --dry-run` writes every payload to disk without sending.

What gets recorded per request: tokens read (and how many were cached), tokens written in total, thinking tokens, visible answer tokens, why it stopped, whether it hit the output ceiling, and which host served it (OpenRouter). Thinking counts come from each lab's own usage report. If an Anthropic response lacks the breakdown, the visible answer is counted with Anthropic's free token counter and subtracted, and the row says so.

## Notes

- One sample per task, model and level, as the spec's light run says. Thinking length varies between runs, so a later full run could use `--repeats 3`.
- Prompt caching is not used in the run. The repeated share in the presets drives the caching line on the bill, not the measurement.
- OpenRouter picks a host per request. The host is recorded, since thinking length should not depend on the host but cost and limits can.
