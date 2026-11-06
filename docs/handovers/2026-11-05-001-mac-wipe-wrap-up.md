# Session Handover — Bench wrap-up before the Mac wipe

**Date:** 2026-11-05
**Branch:** `docs/handover-2026-11-05` (off `main` at `ad9d984`)
**Supersedes:** none (first handover in this repo)

## TL;DR

- Ben is wiping his Mac (BS-MBP-16). This session checked that every Bench file on it is saved elsewhere.
- Result: nothing Bench-related lives only on the Mac. Every local file is on GitHub or, byte-identical, in Claude's cloud project storage.
- The Mac never had a git checkout of Bench; `~/Projects/personal/bench` is a plain folder of older copies.
- No Bench work was in progress on the Mac, so the only new commit is this handover.
- First next action: decide whether to merge the method-page draft (PR #1) and the site draft (PR #2).

## Current state and verification

**[V]** = checked by command this session. **[A]** = taken from the project's notes, not re-checked.

- Mac folder `~/Projects/personal/bench`: **[V]** not a git repo; 16 files, 416 KB; no `.env`, no API key patterns found.
- GitHub `benshapyro/bench`: **[V]** public, Ben's personal account; no `.vercel/` folder on any branch.
- Branches on GitHub **[V]**:
  - `main` at `ad9d984` (includes PR #3, public-safe Phase 0 research, merged)
  - `claude/method-and-defaults` at `47af409`, draft PR #1, open
  - `claude/site-v0` at `6b32149`, draft PR #2, open (stacked on PR #1's commits)
  - Both PR branches start from `15a51ab`, before PR #3 merged; they will need `main` merged in or a rebase.
- How each Mac file is backed up **[V]** (content hash or byte compare):
  - `data/*` (6 files): identical on `main` and both PR branches.
  - `phase0/models*`, `phase0/osworld*` (4 files): identical on `main` under `docs/phase0/`.
  - `phase0/coverage*`, `phase0/usage*`, `phase0/DATA-CHECK-REPORT.md`: byte-identical in cloud project storage under `knowledge/claude/phase0/`. The coverage and usage files are Artificial Analysis data and must stay out of the repo.
  - `BENCH-SPEC.md`: an older draft (24 KB). The current spec (33 KB) is on GitHub at `docs/BENCH-SPEC.md` and in cloud storage. A second older copy (32 KB) sits in `~/Downloads/`. Neither old copy needs saving.
- Permission emails draft (`phase1/permission-emails.md`): **[V]** exists only in cloud project storage, not on the Mac and not on GitHub (by design).
- Usage run: **[A]** never run. Waits on five API keys. **[V]** no Bench keys exist on the Mac (no `.env` in the folder; none of the five key names set in the shell or shell config files).
- Deployed: **[A]** not deployed; Vercel not connected.
- Tests: none run (no code changed).

## What changed

Only this handover file, on a new branch, with a draft PR. Nothing else in the repo was touched.

## Decisions

- Committed the handover on its own branch rather than on `main`, because Ben asked that unfinished work stay off `main`, and so it can merge independently of PRs #1 and #2.
- Did not copy the Mac's Phase 0 Artificial Analysis files or the old spec into the repo. The first are banned from the public repo; the second is superseded.
- Did not add the Mac's `phase0/DATA-CHECK-REPORT.md` (9,757 bytes) to the repo. `main` already has a 9,672-byte version at `docs/DATA-CHECK-REPORT.md`, and the Mac copy is safe in cloud storage. Not compared line by line.

## Failures and dead ends

- The machine session was opened in an unrelated Cadre folder (`~/Projects/cadre/internal/cadre-hamilton-brain/docs`). It was not used for Bench work. A fresh clone in a temporary folder was used to commit this file.

## Next actions

1. Review and merge draft PR #1 (method page, defaults: 85% quality bar, 2,000 tasks a month), then PR #2 (the site, in `site/`). Bring both up to date with `main` first.
2. Check rows 10 to 12 of `data/SPOT-CHECK.md` (the three unconfirmed "Using software" scores).
3. Decide what to do if Artificial Analysis data can't be used (the fallback decision).
4. Create the five API keys (Anthropic, OpenAI, Gemini, xAI, OpenRouter) on the new machine, export them, then run, from `usage-run/`:
   `python run_usage.py probe`
   then the full run (estimated about $14; see `usage-run/README.md`).
5. Connect Vercel to the site for bench.shapyro.com.
6. At launch, send the permission emails (the draft is in cloud project storage at `phase1/permission-emails.md`).

## Do not redo

- The backup check above. Every Mac file has been matched to a GitHub or cloud-storage copy by content.
- Searching the Mac for Bench API keys: there are none to recover.

## Key files

| File | Purpose |
|---|---|
| `docs/BENCH-SPEC.md` | The current spec |
| `data/SPOT-CHECK.md` | The 12-score spot check; rows 10 to 12 open |
| `usage-run/README.md` | How to run the usage measurement and what it costs |
| `docs/handovers/2026-11-05-001-mac-wipe-wrap-up.md` | This handover |

## Rule candidates captured

- None.

## Next-session note

```text
STATUS:
- benshapyro/bench main at ad9d984. Draft PR #1 (method page and defaults, branch claude/method-and-defaults) and draft PR #2 (site, branch claude/site-v0) open, unmerged, both behind main.
- Vercel not connected. Usage run never run; no API keys exist yet.
- Before Ben's Mac wipe (planned weekend of 2026-11-07), every Bench file on it was confirmed to be on GitHub or in cloud project storage.

READ FIRST (before any reply, even a status summary):
- docs/handovers/2026-11-05-001-mac-wipe-wrap-up.md

DO NEXT:
1. Bring PR #1 and PR #2 up to date with main; ask Ben to review and merge them.
2. Ask Ben to check rows 10 to 12 of data/SPOT-CHECK.md.
3. Ask Ben about the fallback if Artificial Analysis data can't be used.
4. Once the five API keys exist: python run_usage.py probe in usage-run/, then the full run (about $14, ask first).

DO NOT REDO:
- The pre-wipe backup check of the old Mac.

NEVER:
- Commit phase1/permission-emails.md or any Artificial Analysis data (phase0 coverage.json, usage.json, usage-notes.md, coverage-notes.md).
- Commit API keys or .env files.
- Spend on the usage run without Ben's go-ahead.
```
