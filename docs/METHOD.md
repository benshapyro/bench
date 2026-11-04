# How we get these numbers

<!-- Draft for the site's method page (spec section 3.5). The site adds the last-checked date. -->

Bench answers one question: which AI model should run this job, and what will it cost each month? Here is where every number comes from, and where our own judgment comes in.

## Where each number comes from

Every number on Bench carries one of four labels:

- **Lab-reported:** published by the company that made the model, on its launch page or in its technical report. Labs choose how to test their own models, so we treat these with care.
- **Independent:** published by a third party that tested the model itself, such as Vals AI or Surge AI. When an independent score and a lab's score cover the same test under the same conditions, we use the independent one.
- **Measured by Bench:** something we measured ourselves. Today that is how much text each model produces while thinking.
- **Estimated:** something we calculated from other numbers. Estimates always say so.

Each number links to its source and shows the date we recorded it.

## How jobs become test scores

There's no single test for "customer service" or "writing a report." For each kind of job, we picked one public test that's closest to the real work and has been run on the most models under the same conditions:

| Job | Test we use | Who runs it |
|---|---|---|
| General business work (finance, coding, legal, tax) | Vals Index | Vals AI |
| Customer service | τ³-Banking | Sierra, published by Mercor |
| Using software for you | OSWorld 2.0, offline set | Each model's lab |
| Building software | Terminal-Bench 4.0 | Vals AI, one setup for every model |
| Reading charts and documents | GDP.pdf | Surge AI |

Matching a job to a test is our judgment, not a fact. Other tests appear under "Show details."

A test score is not a measure of how a model will do on your work. That's why every recommendation ends the same way: try the top choices on 20 of your own real tasks before you decide.

## Comparing like with like

A score only means something next to scores taken under the same conditions: the same version of the test, the same set of tasks, the same tools. For each job we fix one set of conditions. Only scores that meet them can be named best or best value. Other scores still appear, marked with a warning, but they never decide.

If a model has no score under those conditions, we leave it out and say so: "Compared 6 of 15 models."

## "% of the best"

We show each model's score as a share of the top score for that job. If the leader scores 80% and another model scores 68%, the second model is at 85% of the best. When a new leader arrives, everyone else's share goes down. That's expected.

Some tests rate models against each other, like chess ratings, so their numbers aren't percentages. For those we show how often a model would win a head-to-head against the leader instead.

On multiple-choice tests, guessing alone earns some points, so we subtract the guessing score before comparing. None of the current main tests is multiple choice.

## "Good enough" and best value

You choose what good enough means, from 50% to 100% of the best score. Bench starts at **85%**: close to the best, while still leaving room for a cheaper option.

**Best value** is the cheapest model and thinking level that reaches your bar. If only the leader reaches it, the leader is also the best value.

## What a month costs

AI companies charge by the amount of text a model reads and writes, counted in **tokens** (a token is about three-quarters of a word). We turn that into a monthly bill:

1. **Your task size.** Each job starts with a typical task, measured in pages (one page is about 500 words). You can change it.
2. **What the model reads**, priced at the company's input price.
3. **What the model writes, plus its "thinking."** Many models think before they answer, and that thinking is billed like writing. It can be many times longer than the answer itself. We measured how much each model thinks at three settings (low, the default, and high) on eight typical business tasks. Settings in between are estimated from those.
4. **Savings from repeated text.** When the same text is sent again within a few minutes, such as a company policy re-read on every customer reply, most companies charge much less for it. We count this only when the repeat would really happen in time at your volume. You can switch it off.
5. **Times your monthly volume.** Bench starts at **2,000 tasks a month**.

Prices are each company's published list prices, with the date we checked them. For open-weight models, which many companies host at different prices, we use the maker's own price, or otherwise the middle price among the major hosts. Promotional prices are used while they last, with the date they end.

Money is rounded, as in "about $1,200 a month." These are estimates of the model's bill only, not the cost of building or running the rest of the project.

## How the takeaway is written

The recommendation sentence is filled in from fixed templates by simple rules. No AI writes it, so the same inputs always give the same answer.

## Keeping it current

Data is checked by hand when a major model launches. The date at the top of this page is the last time we checked every number. Found something wrong? [contact link]
