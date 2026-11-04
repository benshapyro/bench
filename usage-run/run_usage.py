"""Bench usage run: how many tokens each model reads, writes and thinks on 8 business tasks.

Answers are not graded. Each lab's response reports its own token counts; this
script records them. Anthropic, OpenAI and Google requests go through their
batch APIs (half price). xAI and OpenRouter have no batch discount, so their
requests are sent directly, a few at a time.

    pip install anthropic openai google-genai
    export ANTHROPIC_API_KEY=... OPENAI_API_KEY=... GEMINI_API_KEY=... XAI_API_KEY=... OPENROUTER_API_KEY=...

    python run_usage.py plan               # what will be sent, and the estimated cost. No keys needed.
    python run_usage.py probe              # one tiny request per model and level, to catch bad IDs or level names (< $0.10)
    python run_usage.py submit             # start the run; prints a run id
    python run_usage.py status  RUN_ID     # check the batches
    python run_usage.py collect RUN_ID     # download results into runs/RUN_ID/results.csv and summary.csv

Every command takes --models (keys from models.json) and --providers to limit it.
`submit --dry-run` writes the request payloads to runs/RUN_ID/ without sending anything.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
TASKS_DIR = HERE / "tasks"
RUNS_DIR = HERE / "runs"
BATCH_PROVIDERS = {"anthropic", "openai", "google"}
SYNC_WORKERS = 4

# Output ceilings. Thinking counts toward them, so they are set high enough that
# the highest levels are not cut off; a cut-off answer is flagged as truncated.
MAX_OUTPUT = {"anthropic": 64000, "openai": 64000, "google": 65536, "xai": 64000, "openrouter": 32000}

# Assumed thinking tokens per task, used only by `plan` to estimate cost.
ASSUMED_THINKING = {"lowest": 800, "default": 3000, "highest": 12000}

KEY_ENV = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "google": "GEMINI_API_KEY",
    "xai": "XAI_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
}


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def load_tasks() -> list[dict]:
    return [json.loads(p.read_text()) for p in sorted(TASKS_DIR.glob("*.json"))]


def load_models(args) -> list[dict]:
    models = json.loads((HERE / "models.json").read_text())["models"]
    if args.models:
        wanted = set(args.models.split(","))
        models = [m for m in models if m["key"] in wanted]
    if args.providers:
        wanted = set(args.providers.split(","))
        models = [m for m in models if m["provider"] in wanted]
    return models


def build_requests(tasks, models, repeats=1) -> list[dict]:
    reqs = []
    for m in models:
        for rank, lvl in enumerate(m["levels"], 1):
            for t in tasks:
                for r in range(repeats):
                    rid = f"{m['key']}__{lvl['name']}__{t['id']}" + (f"__r{r + 1}" if repeats > 1 else "")
                    reqs.append({
                        "custom_id": rid.replace(".", "_"),  # Anthropic custom_id allows [a-zA-Z0-9_-]
                        "model_key": m["key"],
                        "provider": m["provider"],
                        "api_model": m["api_model"],
                        "level": lvl["name"],
                        "level_role": lvl["role"],
                        "level_rank": rank,
                        "task_id": t["id"],
                        "job": t["job"],
                        "system": t["system"],
                        "user": t["user"],
                    })
    return reqs


# ---------------------------------------------------------------------------
# Request bodies, one function per provider
# ---------------------------------------------------------------------------

def anthropic_params(r, max_tokens=None):
    return {
        "model": r["api_model"],
        "max_tokens": max_tokens or MAX_OUTPUT["anthropic"],
        "system": r["system"],
        "messages": [{"role": "user", "content": r["user"]}],
        "thinking": {"type": "adaptive"},
        "output_config": {"effort": r["level"]},
    }


def openai_body(r, max_tokens=None):
    return {
        "model": r["api_model"],
        "input": [{"role": "system", "content": r["system"]}, {"role": "user", "content": r["user"]}],
        "reasoning": {"effort": r["level"]},
        "max_output_tokens": max_tokens or MAX_OUTPUT[r["provider"]],
        "store": False,
    }


def google_request(r, max_tokens=None):
    return {
        "contents": [{"role": "user", "parts": [{"text": r["user"]}]}],
        "config": {
            "system_instruction": {"parts": [{"text": r["system"]}]},
            "thinking_config": {"thinking_level": r["level"]},
            "max_output_tokens": max_tokens or MAX_OUTPUT["google"],
        },
        "metadata": {"key": r["custom_id"]},
    }


def openrouter_kwargs(r, max_tokens=None):
    extra = {"usage": {"include": True}}
    if r["level"] != "default":
        extra["reasoning"] = {"effort": r["level"]}
    return {
        "model": r["api_model"],
        "messages": [{"role": "system", "content": r["system"]}, {"role": "user", "content": r["user"]}],
        "max_tokens": max_tokens or MAX_OUTPUT["openrouter"],
        "extra_body": extra,
    }


# ---------------------------------------------------------------------------
# Clients
# ---------------------------------------------------------------------------

def client_for(provider):
    if provider == "anthropic":
        import anthropic
        return anthropic.Anthropic()
    if provider == "openai":
        import openai
        return openai.OpenAI()
    if provider == "google":
        from google import genai
        return genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    if provider == "xai":
        import openai
        return openai.OpenAI(api_key=os.environ["XAI_API_KEY"], base_url="https://api.x.ai/v1")
    if provider == "openrouter":
        import openai
        return openai.OpenAI(api_key=os.environ["OPENROUTER_API_KEY"], base_url="https://openrouter.ai/api/v1")
    raise ValueError(provider)


def check_keys(providers):
    missing = [KEY_ENV[p] for p in sorted(providers) if not os.environ.get(KEY_ENV[p])]
    if missing:
        sys.exit("Missing API keys: " + ", ".join(missing))


# ---------------------------------------------------------------------------
# Normalizing usage into one row
# ---------------------------------------------------------------------------

def _get(obj, *path):
    for p in path:
        if obj is None:
            return None
        obj = obj.get(p) if isinstance(obj, dict) else getattr(obj, p, None)
    return obj


def row_base(r):
    return {k: r[k] for k in ("custom_id", "model_key", "provider", "api_model", "level", "level_role", "level_rank", "task_id", "job")}


def norm_anthropic(r, msg, client=None):
    """msg: a Message (object or dict)."""
    u = _get(msg, "usage")
    out = _get(u, "output_tokens") or 0
    thinking = _get(u, "output_tokens_details", "thinking_tokens")
    method = "reported"
    text = "".join(_get(b, "text") or "" for b in (_get(msg, "content") or []) if _get(b, "type") == "text")
    if thinking is None and client is not None:
        # Older responses without the breakdown: count the visible answer and subtract.
        visible = count_anthropic_text(client, r["api_model"], text)
        thinking = max(0, out - visible)
        method = "output minus counted visible text"
    stop = _get(msg, "stop_reason")
    return {
        **row_base(r),
        "input_tokens": (_get(u, "input_tokens") or 0) + (_get(u, "cache_read_input_tokens") or 0) + (_get(u, "cache_creation_input_tokens") or 0),
        "cached_input_tokens": _get(u, "cache_read_input_tokens") or 0,
        "output_tokens_total": out,
        "thinking_tokens": thinking,
        "visible_output_tokens": None if thinking is None else out - thinking,
        "visible_output_chars": len(text),
        "thinking_method": method,
        "stop_reason": stop,
        "truncated": stop == "max_tokens",
        "served_by": "anthropic",
        "error": "",
    }


def count_anthropic_text(client, model, text):
    base = client.messages.count_tokens(model=model, messages=[{"role": "user", "content": "."}]).input_tokens
    full = client.messages.count_tokens(model=model, messages=[{"role": "user", "content": "." + text}]).input_tokens
    return full - base


def norm_openai_responses(r, body):
    """body: a Responses API response (object or dict). Used for OpenAI and xAI."""
    u = _get(body, "usage")
    out = _get(u, "output_tokens") or 0
    thinking = _get(u, "output_tokens_details", "reasoning_tokens")
    status = _get(body, "status")
    reason = _get(body, "incomplete_details", "reason")
    text = ""
    for item in _get(body, "output") or []:
        if _get(item, "type") == "message":
            for c in _get(item, "content") or []:
                text += _get(c, "text") or ""
    return {
        **row_base(r),
        "input_tokens": _get(u, "input_tokens") or 0,
        "cached_input_tokens": _get(u, "input_tokens_details", "cached_tokens") or 0,
        "output_tokens_total": out,
        "thinking_tokens": thinking,
        "visible_output_tokens": None if thinking is None else out - thinking,
        "visible_output_chars": len(text),
        "thinking_method": "reported" if thinking is not None else "missing",
        "stop_reason": reason or status,
        "truncated": reason == "max_output_tokens",
        "served_by": r["provider"],
        "error": "",
    }


def norm_google(r, resp):
    """resp: a GenerateContentResponse (object or dict)."""
    u = _get(resp, "usage_metadata")
    visible = _get(u, "candidates_token_count") or 0
    thinking = _get(u, "thoughts_token_count") or 0
    cands = _get(resp, "candidates") or []
    finish = _get(cands[0], "finish_reason") if cands else None
    finish = getattr(finish, "name", finish)
    text = ""
    if cands:
        for p in _get(cands[0], "content", "parts") or []:
            if not _get(p, "thought"):
                text += _get(p, "text") or ""
    return {
        **row_base(r),
        "input_tokens": _get(u, "prompt_token_count") or 0,
        "cached_input_tokens": _get(u, "cached_content_token_count") or 0,
        "output_tokens_total": visible + thinking,
        "thinking_tokens": thinking,
        "visible_output_tokens": visible,
        "visible_output_chars": len(text),
        "thinking_method": "reported",
        "stop_reason": finish,
        "truncated": finish == "MAX_TOKENS",
        "served_by": "google",
        "error": "",
    }


def norm_openrouter(r, resp):
    u = _get(resp, "usage")
    out = _get(u, "completion_tokens") or 0
    thinking = _get(u, "completion_tokens_details", "reasoning_tokens")
    choice = (_get(resp, "choices") or [None])[0]
    finish = _get(choice, "finish_reason")
    text = _get(choice, "message", "content") or ""
    extra = getattr(resp, "model_extra", None) or {}
    return {
        **row_base(r),
        "input_tokens": _get(u, "prompt_tokens") or 0,
        "cached_input_tokens": _get(u, "prompt_tokens_details", "cached_tokens") or 0,
        "output_tokens_total": out,
        "thinking_tokens": thinking,
        "visible_output_tokens": None if thinking is None else out - thinking,
        "visible_output_chars": len(text),
        "thinking_method": "reported" if thinking is not None else "missing",
        "stop_reason": finish,
        "truncated": finish == "length",
        "served_by": "openrouter:" + str(extra.get("provider", "?")),
        "error": "",
    }


def error_row(r, msg):
    return {**row_base(r), "input_tokens": None, "cached_input_tokens": None, "output_tokens_total": None,
            "thinking_tokens": None, "visible_output_tokens": None, "visible_output_chars": None,
            "thinking_method": "", "stop_reason": "", "truncated": "", "served_by": r["provider"], "error": str(msg)[:500]}


# ---------------------------------------------------------------------------
# Direct (non-batch) calls: xAI, OpenRouter, and every provider during `probe`
# ---------------------------------------------------------------------------

def call_direct(client, r, max_tokens=None):
    p = r["provider"]
    try:
        if p == "anthropic":
            return norm_anthropic(r, client.messages.create(**anthropic_params(r, max_tokens)), client)
        if p in ("openai", "xai"):
            return norm_openai_responses(r, client.responses.create(**openai_body(r, max_tokens)))
        if p == "google":
            g = google_request(r, max_tokens)
            return norm_google(r, client.models.generate_content(model=r["api_model"], contents=g["contents"], config=g["config"]))
        if p == "openrouter":
            return norm_openrouter(r, client.chat.completions.create(**openrouter_kwargs(r, max_tokens)))
    except Exception as e:  # recorded in the results; the run continues
        return error_row(r, f"{type(e).__name__}: {e}")
    raise ValueError(p)


def run_direct(reqs, max_tokens=None, workers=SYNC_WORKERS):
    clients = {p: client_for(p) for p in {r["provider"] for r in reqs}}
    with ThreadPoolExecutor(workers) as pool:
        return list(pool.map(lambda r: call_direct(clients[r["provider"]], r, max_tokens), reqs))


# ---------------------------------------------------------------------------
# Batch submit and collect
# ---------------------------------------------------------------------------

def submit_anthropic(reqs, run_dir):
    client = client_for("anthropic")
    batch = client.messages.batches.create(requests=[{"custom_id": r["custom_id"], "params": anthropic_params(r)} for r in reqs])
    return [{"provider": "anthropic", "id": batch.id, "count": len(reqs)}]


def submit_openai(reqs, run_dir):
    client = client_for("openai")
    path = run_dir / "openai_batch_input.jsonl"
    with path.open("w") as f:
        for r in reqs:
            f.write(json.dumps({"custom_id": r["custom_id"], "method": "POST", "url": "/v1/responses", "body": openai_body(r)}) + "\n")
    with path.open("rb") as f:
        upload = client.files.create(file=f, purpose="batch")
    batch = client.batches.create(input_file_id=upload.id, endpoint="/v1/responses", completion_window="24h")
    return [{"provider": "openai", "id": batch.id, "count": len(reqs)}]


def submit_google(reqs, run_dir):
    client = client_for("google")
    jobs = []
    for model in sorted({r["api_model"] for r in reqs}):
        mine = [r for r in reqs if r["api_model"] == model]
        job = client.batches.create(model=model, src=[google_request(r) for r in mine],
                                    config={"display_name": f"bench-usage-{run_dir.name}-{model}"})
        jobs.append({"provider": "google", "id": job.name, "model": model, "count": len(mine),
                     "order": [r["custom_id"] for r in mine]})
    return jobs


SUBMITTERS = {"anthropic": submit_anthropic, "openai": submit_openai, "google": submit_google}


def batch_status(job):
    p = job["provider"]
    c = client_for(p)
    if p == "anthropic":
        b = c.messages.batches.retrieve(job["id"])
        return b.processing_status == "ended", f"{b.processing_status} {b.request_counts}"
    if p == "openai":
        b = c.batches.retrieve(job["id"])
        return b.status in ("completed", "failed", "expired", "cancelled"), f"{b.status} {b.request_counts}"
    if p == "google":
        b = c.batches.get(name=job["id"])
        state = getattr(b.state, "name", str(b.state))
        return state in ("JOB_STATE_SUCCEEDED", "JOB_STATE_FAILED", "JOB_STATE_CANCELLED", "JOB_STATE_EXPIRED"), state
    raise ValueError(p)


def collect_batch(job, by_id):
    p = job["provider"]
    c = client_for(p)
    rows = []
    if p == "anthropic":
        for res in c.messages.batches.results(job["id"]):
            r = by_id[res.custom_id]
            if res.result.type == "succeeded":
                rows.append(norm_anthropic(r, res.result.message, c))
            else:
                rows.append(error_row(r, f"{res.result.type}: {getattr(res.result, 'error', '')}"))
    elif p == "openai":
        b = c.batches.retrieve(job["id"])
        for file_id in (b.output_file_id, b.error_file_id):
            if not file_id:
                continue
            for line in c.files.content(file_id).text.splitlines():
                item = json.loads(line)
                r = by_id[item["custom_id"]]
                resp = item.get("response") or {}
                if resp.get("status_code") == 200:
                    rows.append(norm_openai_responses(r, resp["body"]))
                else:
                    rows.append(error_row(r, item.get("error") or resp.get("body")))
    elif p == "google":
        b = c.batches.get(name=job["id"])
        inlined = (b.dest.inlined_responses if b.dest else None) or []
        for i, item in enumerate(inlined):
            key = _get(item, "metadata", "key") or job["order"][i]  # results keep request order
            r = by_id[key]
            if item.error:
                rows.append(error_row(r, item.error))
            else:
                rows.append(norm_google(r, item.response))
    return rows


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

FIELDS = ["custom_id", "model_key", "provider", "api_model", "level", "level_role", "level_rank", "task_id", "job",
          "input_tokens", "cached_input_tokens", "output_tokens_total", "thinking_tokens", "visible_output_tokens",
          "visible_output_chars", "thinking_method", "stop_reason", "truncated", "served_by", "error"]


def write_rows(path, rows):
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for row in sorted(rows, key=lambda x: x["custom_id"]):
            w.writerow({k: row.get(k) for k in FIELDS})


def write_summary(run_dir, rows, tasks):
    """Per model and level: thinking per task, and real tokens per page of input for each lab."""
    words = {t["id"]: len((t["system"] + " " + t["user"]).split()) for t in tasks}
    groups = {}
    for row in rows:
        if row["error"] or row["thinking_tokens"] is None:
            continue
        groups.setdefault((row["model_key"], row["level_rank"], row["level"]), []).append(row)
    out = []
    for (model, rank, level), rs in sorted(groups.items()):
        n = len(rs)
        pages = sum(words[x["task_id"]] for x in rs) / 500  # the spec's page: 500 words
        out.append({
            "model_key": model, "level_rank": rank, "level": level, "tasks_measured": n,
            "mean_thinking_tokens": round(sum(x["thinking_tokens"] for x in rs) / n),
            "min_thinking_tokens": min(x["thinking_tokens"] for x in rs),
            "max_thinking_tokens": max(x["thinking_tokens"] for x in rs),
            "thinking_tokens_per_input_page": round(sum(x["thinking_tokens"] for x in rs) / pages),
            "mean_visible_output_tokens": round(sum(x["visible_output_tokens"] for x in rs) / n),
            "input_tokens_per_page": round(sum(x["input_tokens"] for x in rs) / pages),
            "truncated": sum(1 for x in rs if str(x["truncated"]) == "True"),
        })
    with (run_dir / "summary.csv").open("w", newline="") as f:
        if out:
            w = csv.DictWriter(f, fieldnames=list(out[0]))
            w.writeheader()
            w.writerows(out)
    return out


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_plan(args):
    tasks, models = load_tasks(), load_models(args)
    reqs = build_requests(tasks, models, args.repeats)
    approx_in = {t["id"]: t["approx_tokens_in"] for t in tasks}
    approx_out = {t["id"]: t["target_pages_out"] * 650 for t in tasks}
    total = 0.0
    print(f"{len(tasks)} tasks x {len(models)} models x 3 levels x {args.repeats} repeat(s) = {len(reqs)} requests\n")
    print(f"{'model':<24}{'route':<12}{'levels':<28}{'est. cost':>10}")
    for m in models:
        mine = [r for r in reqs if r["model_key"] == m["key"]]
        discount = 0.5 if m["provider"] in BATCH_PROVIDERS else 1.0
        cost = sum(
            (approx_in[r["task_id"]] * m["price_in"] + (approx_out[r["task_id"]] + ASSUMED_THINKING[r["level_role"]]) * m["price_out"]) / 1e6
            for r in mine
        ) * discount
        total += cost
        route = "batch" if discount < 1 else "direct"
        print(f"{m['key']:<24}{route:<12}{', '.join(l['name'] for l in m['levels']):<28}{cost:>10.2f}")
    print(f"\nEstimated total: ${total:.2f}")
    print(f"(Assumes thinking of {ASSUMED_THINKING} tokens per task; the run measures the real numbers.)")
    if args.worst_case:
        worst = sum((approx_in[r["task_id"]] * m["price_in"] + MAX_OUTPUT[m["provider"]] * m["price_out"]) / 1e6
                    * (0.5 if m["provider"] in BATCH_PROVIDERS else 1.0)
                    for m in models for r in reqs if r["model_key"] == m["key"] and r["level_role"] == "highest")
        print(f"Worst case if every highest-level request used its full output ceiling: ${worst + total:.2f}")


def cmd_probe(args):
    """One short request per model and level, sent directly, to check IDs and level names."""
    models = load_models(args)
    check_keys({m["provider"] for m in models})
    probe_task = {"id": "PROBE", "job": "probe", "system": "Answer in one short sentence.",
                  "user": "A train leaves at 9:40 and the trip takes 2 hours 35 minutes. When does it arrive?"}
    reqs = build_requests([probe_task], models)
    rows = run_direct(reqs, max_tokens=4000, workers=8)
    bad = 0
    for row in rows:
        ok = not row["error"]
        bad += not ok
        detail = row["error"] if not ok else f"in {row['input_tokens']}, out {row['output_tokens_total']}, thinking {row['thinking_tokens']} ({row['thinking_method']})"
        print(f"{'OK ' if ok else 'BAD'} {row['model_key']:<24}{row['level']:<10}{detail}")
    print(f"\n{len(rows) - bad} of {len(rows)} passed." + (" Fix models.json before submitting." if bad else ""))
    sys.exit(1 if bad else 0)


def cmd_submit(args):
    tasks, models = load_tasks(), load_models(args)
    reqs = build_requests(tasks, models, args.repeats)
    run_id = args.run_id or datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    with (run_dir / "requests.jsonl").open("w") as f:
        for r in reqs:
            f.write(json.dumps({k: v for k, v in r.items() if k not in ("system", "user")}) + "\n")
    if args.dry_run:
        for p in sorted({r["provider"] for r in reqs}):
            mine = [r for r in reqs if r["provider"] == p]
            payload = {"anthropic": anthropic_params, "openai": openai_body, "xai": openai_body,
                       "google": google_request, "openrouter": openrouter_kwargs}[p]
            with (run_dir / f"dry_run_{p}.jsonl").open("w") as f:
                for r in mine:
                    f.write(json.dumps({"custom_id": r["custom_id"], "body": payload(r)}) + "\n")
        print(f"Dry run: wrote {len(reqs)} request payloads to {run_dir}. Nothing was sent.")
        return
    check_keys({r["provider"] for r in reqs})
    state = {"run_id": run_id, "created": datetime.now(timezone.utc).isoformat(), "repeats": args.repeats, "jobs": []}
    for p in sorted(BATCH_PROVIDERS & {r["provider"] for r in reqs}):
        state["jobs"] += SUBMITTERS[p]([r for r in reqs if r["provider"] == p], run_dir)
        print(f"Submitted {p} batch(es).")
    (run_dir / "state.json").write_text(json.dumps(state, indent=2))
    direct = [r for r in reqs if r["provider"] not in BATCH_PROVIDERS]
    if direct:
        print(f"Sending {len(direct)} direct requests (xAI, OpenRouter)...")
        rows = run_direct(direct)
        write_rows(run_dir / "direct_results.csv", rows)
        errors = sum(1 for x in rows if x["error"])
        print(f"Direct requests done, {errors} errors.")
    print(f"\nRun id: {run_id}\nBatches usually finish within an hour. Then: python run_usage.py collect {run_id}")


def cmd_status(args):
    state = json.loads((RUNS_DIR / args.run_id / "state.json").read_text())
    for job in state["jobs"]:
        done, detail = batch_status(job)
        print(f"{job['provider']:<10}{job.get('model', ''):<24}{'done' if done else 'running':<9}{detail}")


def cmd_collect(args):
    run_dir = RUNS_DIR / args.run_id
    state = json.loads((run_dir / "state.json").read_text())
    tasks = load_tasks()
    models = json.loads((HERE / "models.json").read_text())["models"]
    by_id = {r["custom_id"]: r for r in build_requests(tasks, models, state.get("repeats", 1))}
    rows = []
    for job in state["jobs"]:
        done, detail = batch_status(job)
        if not done:
            sys.exit(f"{job['provider']} batch {job['id']} is still running ({detail}). Try again later.")
        rows += collect_batch(job, by_id)
    direct = run_dir / "direct_results.csv"
    if direct.exists():
        with direct.open() as f:
            for row in csv.DictReader(f):
                for k in ("input_tokens", "cached_input_tokens", "output_tokens_total", "thinking_tokens", "visible_output_tokens", "visible_output_chars", "level_rank"):
                    row[k] = int(row[k]) if row[k] not in ("", None) else None
                rows.append(row)
    write_rows(run_dir / "results.csv", rows)
    summary = write_summary(run_dir, rows, tasks)
    errors = [x for x in rows if x["error"]]
    missing_thinking = [x for x in rows if not x["error"] and x["thinking_tokens"] is None]
    print(f"{len(rows)} results, {len(errors)} errors, {len(missing_thinking)} without a thinking count.")
    print(f"Wrote {run_dir / 'results.csv'} and {run_dir / 'summary.csv'} ({len(summary)} model-level rows).")
    if errors:
        print("Errored requests can be re-sent with: python run_usage.py submit --models <keys>")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("plan", "probe", "submit", "status", "collect"):
        sp = sub.add_parser(name)
        if name in ("status", "collect"):
            sp.add_argument("run_id")
        else:
            sp.add_argument("--models", help="comma-separated model keys from models.json")
            sp.add_argument("--providers", help="comma-separated: anthropic, openai, google, xai, openrouter")
            sp.add_argument("--repeats", type=int, default=1, help="requests per task, model and level (default 1)")
        if name == "submit":
            sp.add_argument("--dry-run", action="store_true", help="write payloads, send nothing")
            sp.add_argument("--run-id", help="name for the run folder (default: timestamp)")
        if name == "plan":
            sp.add_argument("--worst-case", action="store_true", help="also show the cost if every highest-level answer hit its ceiling")
    args = ap.parse_args()
    {"plan": cmd_plan, "probe": cmd_probe, "submit": cmd_submit, "status": cmd_status, "collect": cmd_collect}[args.cmd](args)


if __name__ == "__main__":
    main()
