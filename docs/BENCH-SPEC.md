# Bench — v0 Spec

**Status:** Agreed in interview (Oct 8–17, 2026), reviewed cold, fixes applied. Data check (Phase 0) done Oct 17; spec updated Oct 27 with its decisions (#24–31). Next step: Phase 1 (full data, usage measurement run, permission emails).
**Owner:** Ben Shapiro
**Working name:** Bench
**Address:** bench.shapyro.com

---

## 1. What Bench is

Bench helps a business buyer approve an AI project. The buyer picks the kind of work the project does and how many tasks it will run each month. They can also enter the model a vendor proposed. Bench answers in plain English:

- the best model overall,
- the cheapest model that is good enough, where the buyer sets what "good enough" means,
- what each one would cost per month, and how that compares to the model they were offered,
- a direct recommendation, with one next step.

The numbers behind every answer are one click away, with their sources.

### The problem it solves
Today's benchmark sites show raw tables of scores and token prices. The reader has to work out what each test measures, how two scores compare, and what a token price becomes on a monthly bill. Builders and AI enthusiasts can do that work. Business buyers can't, and they are often the ones approving the spend. Bench does that work for them.

### Who it is for
- **Main user:** a business buyer or other non-technical person approving an AI project that their team or a vendor will build. Example: a vendor proposes a support bot on Sonnet 5.5. The buyer wants to know whether that's the right choice and what it will cost.
- **Second user:** builders (developers, PMs, technical founders). They get full detail behind "Show details."

### What it is for right now
Bench is a portfolio piece first, built so it can grow into a product. v0 should be polished and live soon. The data structure is designed so later versions can expand without a rebuild.

---

## 2. Principles

1. **Answer first, data second.** Every screen leads with the conclusion.
2. **Plain language first, details on click.** No jargon on the main screens. Benchmark names, raw scores and sources sit under "Show details."
3. **Every number shows where it came from.** Each is labeled **Lab-reported**, **Independent**, **Measured by Bench** or **Estimated**, with a source link and the date it was recorded.
4. **Like-for-like only when choosing.** Only scores measured under the same conditions can decide a recommendation. Others are shown, with a warning, but never pick the winner.
5. **Say the limits out loud.** A benchmark is not the buyer's work. Every recommendation ends with a next step to test on real tasks.
6. **Same inputs, same output.** Takeaways are written by fixed rules, not by an AI.

---

## 3. v0 screens

### 3.1 Home: "Pick a model for a job"
**Inputs:**
1. **Job:** one of the 5 jobs (section 4).
2. **Monthly volume:** for example, "about 2,000 tasks a month."
3. **Model you were offered** (optional): a picker. Leave it empty if there's no proposal yet.
4. **Quality bar slider:** "Good enough means at least __% of the best score." Range 50–100%, in steps of 5. The default (likely 85–90%) is set in Phase 1.

**The answer card:**
- **Best overall:** the highest score for this job, and its monthly cost.
- **Best value:** the cheapest model and reasoning level that reaches the bar, and its monthly cost.
- **The model you were offered:** its score as % of the leader, its monthly cost, and whether it clears the bar. Shown only if one was entered.
- **Recommendation:** one sentence from the templates in section 5.4, plus one next step.
- **Caveat line:** "A test score is not a direct measure of quality on your work."
- **Coverage line:** how many models were compared, for example "Compared 6 of 15 models."
- **Left out:** a short list of models with no usable score for this job (section 5.1). For example: "Not included: Model X (no score on this test)."

Changing any input updates the answer immediately. Money is rounded to 2 significant figures, for example "about $1,200 a month."

### 3.2 Cost-versus-score chart, one per job
- **Vertical axis:** score, as % of the leader for this job.
- **Horizontal axis:** monthly cost at the buyer's volume and task size, on a log scale. A log scale gives each tenfold step in price the same width, so cheap and expensive models fit on one chart.
- **Lines:** each model is a line of dots, one dot per reasoning level, ordered from least to most thinking.
- **Hover:** shows the lab's own level name (e.g. "Xhigh") and the note "More thinking is slower and costs more, and usually scores higher." Bench does not invent a shared reasoning scale across labs.
- **Mismatched scores:** dots measured under different conditions from the job's reference conditions (section 5.1) are drawn hollow, with a warning on hover. They can't be marked best overall or best value.
- **Markers:** best overall, best value and the offered model are marked. The quality bar is a horizontal line that moves with the slider.

### 3.3 Cost breakdown
For the selected model and level, the monthly bill is shown line by line:
- text the model reads, in pages,
- text the model writes, in pages,
- "thinking" text (charged at the output price),
- **savings from repeated text** (prompt caching): its own line, with a one-line explanation and an off switch. It only counts reuse that actually happens before the cached copy expires (section 5.2). At low volume it may read "Caching wouldn't save much at this volume,"
- a long-document note, when a task goes over the model's long-prompt threshold.

The buyer can edit pages in, pages out, volume and the caching switch. Each job starts from a preset typical task (section 4). **These edits apply on every screen**: the answer card, the chart and Compare.

### 3.4 Compare
- **Columns:** 2–4 models, added and removed from a picker. The offered model is added automatically if one was entered.
- **Rows:** the 5 jobs. Each cell shows % of the leader as a short bar plus the monthly cost.
- **"Best" in a row** means the highest like-for-like score. Ties go to the cheaper option.
- **Missing data:** a model with no score shows "No score."
- **Details:** "Show details" opens each job into its benchmark rows. Any benchmark row can be added or removed.
- **Reasoning level:** each model starts at the highest level its lab published, labeled, with a switch to change it.
- **Mismatched conditions:** numbers measured under different conditions show a warning mark and a one-line note, and aren't eligible for "best."

### 3.5 "How we get these numbers"
A plain-English page covering:
- the three labels,
- how jobs map to benchmarks, and that the mapping is Bench's judgment,
- the like-for-like rule,
- how costs, estimates and caching are calculated (section 5),
- the guessing-score adjustment,
- the "last checked" date.

### 3.6 Across the site
- **Shareable links:** every view has a link that reproduces it exactly: job, volume, offered model, bar, task size, caching switch, and the chosen models and levels.
- **Printing:** the answer page prints cleanly on one page.
- **Keyboard:** a ⌘K menu jumps to any model or job.

---

## 4. Jobs (v0)

Set after the Phase 0 data check (`phase0/DATA-CHECK-REPORT.md`). Coverage counts are out of the 15 v0 models (plus legacy entries in the data).

| Job (what the buyer sees) | Example of the work | Main benchmark and reference conditions | Comparable models (Oct 17) | Under details |
|---|---|---|---|---|
| Writing and analysis | Reports, memos, research summaries | **GDPval-AA v2.1** (Artificial Analysis), if AA permits; until then **Vals Index**, with the job shown as "General business work (finance, coding, legal, tax)" | 15 (Vals Index) | AA-Briefcase (if permitted) |
| Customer service agents | Answering customers while following company policy | **τ³-Banking**, pass^1, v1.0.1 or later (τ²-bench is maxed out at about 99%) | 4–5 | τ²-bench |
| Using software for you | Filling in forms, moving data between apps | **OSWorld 2.0**, offline set, partial-credit score, release v2026.08.08 or v2.1; full-pass rate shown beside it where published | 6 (all Lab-reported) | OSWorld-Verified (older version, not comparable) |
| Building software | Writing and fixing code | **Terminal-Bench 4.0, Vals AI's run** (one setup for every model, average of 3 runs) | 15 | FrontierCode 1.1 |
| Reading charts and documents | Pulling numbers from charts, scans, PDFs | **GDP.pdf** (Surge AI), share of tasks meeting every required fact | 13 | Chartography (no tools; never mixed with its with-tools score) |

- **One main benchmark per job.** The job score is that benchmark's score. Other benchmarks appear under details.
- **All 5 jobs launch in v0, gaps and all.** A job with few comparable models shows the ones it has and lists the rest under "Left out" with the reason. The answer card says how many models were compared, for example: "Compared 6 of 15 models."
- **Dropped:** SWE-bench (no current lab reports it), MMMU-Pro and CharXiv (labs stopped reporting them).
- **Writing and analysis, two notes.** (1) GDPval-AA is the best fit but is run by Artificial Analysis, so it's shown only if AA permits (section 6.1). (2) Vals Index is 52% finance, 37% coding, 8% legal and 3% tax, so while it's the main benchmark, the job is named for what it measures, not "writing."
- **Humanity's Last Exam is not a job.** It appears under details as "general reasoning."
- **Preset typical task.** Each job stores pages in, pages out, and how much of the input repeats (used for caching). Presets are set in Phase 1. Example: customer service reads about 3 pages (policy plus the chat), writes about half a page, and most of the input is repeated policy text.

---

## 5. How the numbers are calculated

### 5.1 Score
- **Reference conditions:** each job's main benchmark has one set of reference conditions (for example, the full test, tools on). These are chosen in Phase 0 as the conditions most models were tested under.
- **Like-for-like:** only scores measured under the reference conditions are eligible for leader, best value and "best" in Compare. Other scores are shown with a warning but never decide.
- **Which score wins:** when both an Independent and a Lab-reported score exist for the same model, level and conditions, the Independent score is used and shown first. The Lab-reported score sits under details.
- **Missing scores:** a model, or a reasoning level, with no eligible score for a job is left out of the leader, the best-value choice and the chart for that job. It's listed under "Left out" on the answer card and shows "No score" in Compare.
- **Guessing adjustment:** on multiple-choice tests, random guessing already earns some score (about 25% with four options). For those tests, Bench subtracts the guessing score before comparing: adjusted score = (score − guessing score) ÷ (100 − guessing score). The method page explains this. Tests without a guessing floor are not adjusted.
- **Leader:** the highest eligible (adjusted) score across all v0 models and levels. If two are tied, the cheaper one is the leader.
- **% of the leader** = eligible score ÷ leader score. The raw score appears under details. This number changes whenever a new leader is added. That's expected, and the method page says so.
- **Rating-style benchmarks** (GDPval-AA, AA-Briefcase, if used) are relative ratings like chess ratings, not percentages, and their zero point is arbitrary. For these, "% of the leader" is replaced by "wins __% of head-to-head comparisons against the leader," computed from the rating gap with the standard Elo formula: win rate = 1 ÷ (1 + 10^((leader rating − model rating) ÷ 400)). The quality bar applies to this win rate. Ratings from different versions (e.g. v2 vs v2.1) are never compared.
- **Partial credit vs full pass** (Using software for you): the partial-credit score decides; the full-pass rate is shown beside it in plain words, for example "fully finished 37 of 100 tasks."

### 5.2 Monthly cost
**Cost per task** = (text read × input price, with repeated text at the cache price) + ((text written + thinking text) × output price)
**Monthly cost** = cost per task × tasks per month

The bill uses **the buyer's task size**, not the size of the benchmark's tasks. Benchmark data only tells Bench how much "thinking" text each model and level produces. (Confirmed by Ben.)

- **Pages to tokens.** A token is the unit labs charge by, about three-quarters of a word. 1 page is about 500 words, which is about 650 tokens. Each lab counts tokens slightly differently; the usage run (below) records real counts per model, which replace this rule of thumb.
- **Thinking text per task.** Phase 0 found that no source publishes this by reasoning level in a form Bench may display (only Artificial Analysis covers every model, and its terms forbid republishing). So Bench measures it:
  - **The usage run (v0, light):** 8 typical business tasks (2 to 3 per job, sized like the job presets) × 3 reasoning levels per model (lowest, the lab's default, highest) × 15 models, about 360 requests. Each lab's response reports exactly how many tokens were read, written and spent thinking; Bench records those counts. Answers are not graded. Labs' batch discounts are used where offered. Estimated cost: $25–40 (inferred from list prices and assumed thinking lengths).
  - **Labels:** measured levels are labeled **Measured by Bench**. Levels between the measured ones are interpolated from them and labeled **Estimated**.
  - **Re-runs:** a model version's usage doesn't change once released, so only new or updated models are measured, at about $1–10 each. Later, the launch agent (section 11) triggers this automatically.
  - **Before the run finishes:** where no measurement exists yet, Bench uses lab-published cost per attempt where available (Estimated), otherwise the same lab's nearest model at the same named level (Estimated). Bench never estimates across labs.
  - **Scaling to the buyer's task:** thinking tokens are taken per task from the measured task closest in size to the buyer's preset, scaled by the ratio of input pages. This is a simple rule, labeled Estimated whenever the buyer's task size differs from the measured one by more than 2×.
- **Caching.** A lab keeps a cached copy of repeated text only for a limited time: 5 minutes at Anthropic (1 hour at a higher write price) and at least 30 minutes at OpenAI. Google, xAI and the open-weight providers don't publish it, so Bench assumes 5 minutes for them and says so. Bench counts savings only for reuse inside that window: within a single task (for example, several turns of one support conversation), or across tasks that arrive within the window at the buyer's volume, assuming tasks are spread evenly over business hours. Bench also counts the extra cost of writing text into the cache.
- **Long-prompt pricing.** If a task goes over a model's long-prompt threshold (100,000 tokens, about 150 pages, for Haiku 5.5), Bench follows that lab's published rule on what counts toward the threshold and which part is charged the higher price.
- **Prices.** Each lab's published list price is used, with source and date. For **open-weight models**, which have no single list price because each hosting company sets its own, Bench uses the model maker's own price if there is one. Otherwise it uses the middle price among the major hosting companies, labeled with which hosts were used.
- **Temporary prices.** Promotional or introductory prices (e.g. Gemini 4 Argon until Nov 30, 2026; Gemini 3.8 Flash until Jan 1, 2027) are used while in force, with a note: "Price rises to $__ on [date]."
- **Peak and off-peak prices** (DeepSeek): the peak price is used, with a note that off-peak hours (which cover US business hours) cost half.

### 5.3 Best value
Best value = the lowest monthly cost, among eligible model-and-level combinations, whose % of the leader is at or above the buyer's bar.
- If only the leader clears the bar, the leader is also best value.
- Ties go to the higher score.

### 5.4 Takeaway templates
The takeaways are fixed sentences filled in from the numbers. They are not written by an AI.

| Situation | Template |
|---|---|
| Best value ≠ best overall | "For your bar (__% of the best), use **[Best value]**. It costs about $__ a month instead of about $__ for **[Best overall]**, and scores __% as high." |
| Best value = best overall | "**[Model]** is both the best and the best value for your bar. Nothing cheaper reaches __% of its score." |
| Offered model given, and it is the recommendation | "**[Offered]** is a good choice for your bar. It's the cheapest option that reaches __% of the best score." |
| Offered model given, and it is not the recommendation | "Switching from **[Offered]** to **[Best value]** would change your bill from about $__ to about $__ a month. Its score would be __% of the best, compared with __% for [Offered]." The switch may make the score higher or lower; the sentence says which. |
| Offered model has no eligible score | "Bench doesn't have a like-for-like score for **[Offered]** on this job, so it can't compare it." |

**Next step, always:** "Test both on 20 of your own real tasks before deciding."
If any number in the sentence is Estimated, the sentence ends with "(cost estimated)."

---

## 6. Data

### 6.1 Sources and permission
Scores are facts and are shown with credit and a link to the source. Bench honors explicit bans in a source's terms. (Ben's position, Oct 2026; an informed view, not legal advice.)

| Source | Label | Status |
|---|---|---|
| Lab launch pages and model cards | Lab-reported | Shown, cited to the lab's page. Includes Artificial Analysis numbers a lab republished on its own page, cited to that page |
| Vals AI (Terminal-Bench 4.0 run, Vals Index) | Independent | Shown with credit and link; courtesy note sent to Vals AI |
| Surge AI (GDP.pdf) | Independent | Shown with credit and link; courtesy note sent to Surge AI |
| Epoch AI, OpenRouter | Independent | Shown (CC BY 4.0, credit required) |
| Artificial Analysis (numbers only they publish) | Independent | **Not shown until AA gives permission.** Their terms forbid republishing. Bench asks for permission and a license quote. Used privately only to sanity-check Bench's own measurements |
| Bench's usage run | Measured by Bench | Shown |

### 6.2 What is stored with every number
Each **result** records:
- model,
- reasoning level (the lab's name and its position from least to most thinking),
- benchmark,
- score,
- test conditions (subset, tools on or off, other settings),
- label,
- source link,
- date recorded,
- cost per attempt and text used per attempt, where published.

Each **model** records:
- lab,
- release date,
- whether it's open-weight (its model files are public, so any hosting company can run it),
- prices: input, output, cache read, cache write, cache lifetime, long-prompt threshold and rule, and long-prompt prices,
- the source, date and (for open-weight models) the hosting companies used.

Each **benchmark** records:
- plain-English description,
- job,
- whether it's the job's main benchmark,
- reference conditions,
- guessing score (0 if none).

Each **job** records:
- plain name,
- example,
- main benchmark,
- preset task (pages in, pages out, repeated share).

All of this is stored as plain text files in the project, so every change is recorded with who changed what and when.

### 6.3 Who enters the data
- Claude gathers and enters the v0 data with source links, and Ben spot-checks a sample.
- In v0, data is updated by hand when a major model launches.
- The site shows a "last checked" date.

### 6.4 Models (v0, confirmed in Phase 0)
| Lab | Models |
|---|---|
| Anthropic | Claude Opus 5.5, Sonnet 5.5, Haiku 5.5, Fable 5.1 |
| OpenAI | GPT-6 Astra, GPT-6.1 Sol, GPT-6 Luna |
| Google | Gemini 4 Argon (replaces Gemini 3.1 Pro, which is still a preview), Gemini 3.8 Flash, Gemini 3.5 Flash-Lite |
| xAI | Grok 4.7 |
| Open-weight | DeepSeek V4.1 Flash, GLM-5.3-Flash, MiMo-V2.6-Flash, Qwen3.8-27B (chosen by actual usage on OpenRouter over 30 days, plus downloads) |

Optional addition: DeepSeek V4 Pro, if Bench wants a top-tier open-weight model. Prices and sources are in `phase0/models.json`.

---

## 7. Design

Changed Oct 29, 2026 (Ben): Bench lives at bench.shapyro.com, so it uses Ben's shapyro brand (the `brand` skill), not a Linear look.

- **Style:** the shapyro brand. Obsidian canvas in dark, warm linen in light. Cormorant Garamond for headings and the answer, DM Sans for everything else. Amber marks the recommendation (our pick) and money; sage marks the bar, links and "offered."
- **Calm, not dense.** At rest the home page shows only the question (a fill-in-the-blanks sentence), the answer as one large headline, two numbers (our pick vs. what you were offered, or vs. the best), and the next step. Everything else (every model, the bill, sources) sits in "Show details" drawers, closed by default.
- **Dark and light:** follows the visitor's device setting, with the brand's sunrise/sunset theme toggle. Dark is the reference look.
- **Never:** pie charts, hype-y gradients, decorative animation. A faint amber glow behind the answer is the one atmospheric touch.
- **Loading:** skeletons instead of spinners.
- **Color is never the only signal:** meaning never depends on color alone, and pages still read in grayscale.
- **Devices:** desktop first, and the home page reads well on a phone.
- **Prototype:** /mnt/project-files/phase2/prototypes/bench-home.html (earlier three-direction exploration: v1-three-directions.html).

---

## 8. Tech and hosting

- **Static site at bench.shapyro.com.** Pre-built pages with no database or server to run, on a free host such as Vercel.
- **Data:** text files in the project. The site rebuilds when data changes.
- **No accounts or logins.**
- **Stack:** chosen in Phase 2. A mainstream web framework is the default.

---

## 9. What "v0 is done" means

1. Live at bench.shapyro.com.
2. 3–5 non-technical people each pick a model for a job and explain why in **under 2 minutes, without help**.

---

## 10. Build plan

| Phase | What | Exit check |
|---|---|---|
| **0. Data check** ✓ (Oct 17) | One job filled in depth; coverage scan of the others; model list and prices; usage-data search. See `phase0/DATA-CHECK-REPORT.md` | Done. Decisions #24–31 |
| 1. Full data | (a) Send permission emails: courtesy notes to Vals AI and Surge AI, a permission and license request to Artificial Analysis. (b) Fill all 5 jobs on their main benchmarks. (c) Write the 8 usage-run tasks and set the job presets from them. (d) Run the usage measurement (~360 requests, ~$25–40; needs Ben's API keys for Anthropic, OpenAI, Google, xAI and OpenRouter). (e) Set the default bar and default volume. (f) Write the method page. (g) Confirm unverified numbers (chart values read via secondary sites, Opus 5.5's OSWorld score) against original pages in a browser. | Ben spot-checks a sample |
| 2. Design and build | The screens in section 3, built on real data. Choose the accent color and the stack. | Ben reviews a live preview |
| 3. Test and launch | Test with 3–5 non-technical people. Fix what blocks them. Launch. | Section 9 |

---

## 11. Later (not v0)

- **Automated updates.** A model launch triggers an agent that reads the launch page, proposes data changes, and runs the usage measurement for the new model. Ben approves or rejects each change before it goes live, the same way code changes are reviewed.
- **Full usage run:** 25 tasks at every reasoning level (~$200–400), replacing interpolated levels with measured ones.
- Artificial Analysis data, if a license is agreed (unblocks GDPval-AA for writing and wider customer-service coverage).
- Comparing app subscriptions (ChatGPT vs Claude vs Gemini seats).
- Paste a sample task, and Bench measures its size.
- PDF export of the answer.
- Speed and response time, history charts, more models, and Bench running its own quality tests (grading answers, not just measuring usage).
- Possibly its own domain, if it becomes a product.

---

## 12. Open items, settled during the build

| Item | Phase |
|---|---|
| Main benchmark and reference conditions per job | ✓ Phase 0 (section 4) |
| Exact model list | ✓ Phase 0 (section 6.4) |
| Caching formula; thinking-text method | ✓ Phase 0 (section 5.2) |
| Artificial Analysis permission (decides Writing job's benchmark) | 1 |
| The 8 usage-run tasks; preset task sizes; default bar; default volume | 1 |
| Stack (accent settled: shapyro amber, Oct 29) | 2 |

---

## 13. Risks

| Risk | What we do about it |
|---|---|
| Too few models have like-for-like scores on a job's main benchmark | Confirmed for Customer service (4–5) and Using software (6). Jobs launch anyway, showing "Compared X of 15 models" and listing the rest |
| Artificial Analysis says no | Writing job stays on Vals Index, named "General business work" |
| A source objects to its scores being shown | Remove them promptly; the site shows the gap |
| Labs disagree when they re-run each other's models (e.g. GPT-6 Luna 52.7% vs 48.9%) | A lab's own result for its own model is preferred; rival re-runs go under details |
| Labs report favorably and test under different conditions | Labels, Independent scores preferred, and only like-for-like scores decide |
| Interpolated thinking levels are off | Labeled Estimated; replaced by the full usage run later |
| A benchmark isn't the buyer's real work | Stated on the answer card and method page; the next step is always "test on your own tasks" |
| Cost estimates are off because thinking text varies | Labeled Estimated; published usage data is used wherever it exists |
| Caching savings overstated | Only reuse inside the cache lifetime is counted |
| Data goes stale after launches | "Last checked" date; manual updates in v0; automated updates later |

---

## 14. Glossary

| Term | Meaning |
|---|---|
| Benchmark | A standard test that labs run models on, such as a set of coding tasks |
| Token | The unit labs charge by; about three-quarters of a word |
| Reasoning level | How long a model "thinks" before answering. Labs name these differently (Low, High, Xhigh, Max) |
| Prompt caching | When the same text is sent with every task, the lab stores it briefly and charges much less to reuse it |
| Open-weight model | A model whose files are public, so any hosting company can run it and set its own price |
| Lab-reported / Independent / Measured by Bench / Estimated | Who produced a number: the model's maker, a third party, Bench's own measurement, or Bench's own calculation |
| Rating-style benchmark | A test scored like chess ratings: the number only means something compared with another model's rating |
| Partial credit / full pass | Partial credit counts how much of each task was done; full pass counts only tasks finished completely |
| Reference conditions | The single set of test settings a job's scores must match to decide a recommendation |
| "Offline subset" | An example of a different test condition: only part of a benchmark was run |
| Cost per attempt | What one try at one benchmark task cost |
| Log scale | A chart axis where each tenfold step takes the same width |
| Skeleton | A gray outline of content shown while a page loads |
| ⌘K | A keyboard shortcut that opens a search menu |

---

## 15. Decision log

| # | Decision | Options considered | Choice | Why |
|---|---|---|---|---|
| 1 | Main audience | Builders; business buyers; Ben only; AI enthusiasts | Business buyers first, builders second | Existing sites already serve builders; buyers are left out |
| 2 | Purpose | Public product; portfolio only; personal tool; portfolio then product | Portfolio first, then product | Ship polished soon without closing off growth |
| 3 | Front door | Pick a model for a job; compare A vs B; chart; what changed | Pick a model for a job | Leads with the answer |
| 4 | Buyer's decision | AI project; AI app; both | Approving an AI project | Cost-per-score fits here; app subscriptions are different data |
| 5 | Detail level | Plain + details on click; Simple/Expert switch; plain only | Plain first, details on click | One product; builders can still check |
| 6 | v0 data entry | By hand; automated | By hand, stored for later automation | Ship now |
| 7 | Sources | Labs + independent; independent only; labs only; paid Artificial Analysis | Labs + independent, every number labeled | Honest; no license cost |
| 8 | Missing cost per task | Estimate; leave blank | Estimate, labeled | A blank chart is useless |
| 9 | Automated updates (later) | Approval queue; live unverified; live | Wait for Ben's approval | A misread launch page would mislead buyers |
| 10 | Jobs | 5 proposed; 3; custom | The 5 proposed | Covers main buyer use cases |
| 11 | Job score | One main benchmark; blend | One main benchmark | Traceable; no invented formula |
| 12 | Quality display | % of leader; tiers; raw score | % of leader | Drives value comparisons |
| 13 | Best value | Cheapest good enough; fixed rule; score per dollar | Cheapest good enough, buyer sets the bar | Trade-off visible and adjustable |
| 14 | Cost unit | Monthly at volume; per attempt | Monthly at buyer's volume | No multiplication left to the buyer |
| 15 | Task size input | Presets in pages; blank fields; paste a sample | Presets, adjustable in pages | Buyers don't know tokens |
| 16 | Takeaway style | Recommend + next step; neutral facts | Recommend + next step | Actionable and honest |
| 17 | Model count | ~8; ~15; 30+ | ~15 | Covers what buyers are offered |
| 18 | Done means | Buyers can use it; feature-complete | 3–5 non-technical people decide in under 2 min | Tests the core promise |
| 19 | Hosting | bench.shapyro.com static; own domain; Mac Mini | bench.shapyro.com, static | Free, reliable, change history |
| 20 | Build order | Data check first; design first | Data check first | Data availability is the biggest unknown |
| 21 | Bill basis | Buyer's task size; benchmark cost × volume | Buyer's task size (confirmed) | Keeps every screen consistent; presets matter |
| 22 | Mismatched test conditions | Shown but don't decide; count with warning | Shown, but don't decide | Recommendations rest only on equal tests |
| 23 | Offered model field | Optional field; none | Optional "Model you were offered" | It's the main use case |
| 24 | Showing third-party scores | Ask everyone first; show everything; show with credit and ask AA | Show with credit and link; ask Artificial Analysis before using numbers only they publish | Scores are facts; honor AA's explicit ban |
| 25 | Thinking-usage data | Measure ourselves; cost ranges; wait for AA license | Measure ourselves, light run now (~$25–40), full run later | No displayable source exists; budget is tight now |
| 26 | Re-measuring usage | Re-run everything regularly; only new or updated models | Only new or updated models | A model version's usage doesn't change once released |
| 27 | v0 job lineup | Only jobs with 8+ comparable models; all 5 with gaps | All 5, gaps shown | Ben's call: show what exists and say what's missing |
| 28 | Google model | Gemini 3.1 Pro; Gemini 4 Argon | Gemini 4 Argon | Current stable flagship; 3.1 Pro is still a preview |
| 29 | Open-weight picks | Flagships; most-used | Most-used (DeepSeek V4.1 Flash, GLM-5.3-Flash, MiMo-V2.6-Flash, Qwen3.8-27B) | Matches what businesses actually build on |
| 30 | Main benchmarks | (see section 4) | Terminal-Bench 4.0 (Vals run), GDP.pdf, τ³-Banking, OSWorld 2.0 offline partial, GDPval-AA or Vals Index | Most comparable models on one consistent setup |
| 31 | Rating-style scores | % of leader; head-to-head win rate | Head-to-head win rate | % of leader misleads when the zero point is arbitrary |

**Calls Claude made, which Ben didn't object to:**
- caching applied automatically as a visible line, counting only real reuse within the cache lifetime;
- long-prompt tier applied by each lab's own rule;
- no invented shared reasoning scale, and no estimates across labs;
- highest published level as the default in Compare;
- Humanity's Last Exam under details, not a job;
- models with missing scores left out of the answer and listed;
- Independent scores preferred over Lab-reported for the same result;
- guessing score subtracted on multiple-choice tests;
- open-weight prices from the model maker, or the middle price among major hosts;
- dark/light follows the device setting;
- ⌘K menu;
- PDF export later.
- (Phase 0) Cache lifetime assumed to be 5 minutes where a lab doesn't publish it.
- (Phase 0) DeepSeek's peak price used, with an off-peak note.
- (Phase 0) Promotional prices used while in force, with a "price rises on" note.
- (Phase 0) OSWorld's full-pass rate shown beside the partial-credit score.
- (Phase 0) A lab's own result for its own model preferred over a rival lab's re-run.
