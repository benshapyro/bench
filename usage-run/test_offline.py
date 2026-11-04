"""Offline check of the whole run with fake API servers: submit, status, collect.

Uses the real SDKs with a mocked HTTP layer, so it catches request-shape and
parsing mistakes without API keys or spend. It does not prove the labs accept
the model IDs and level names; `run_usage.py probe` does that.

    python test_offline.py
"""

import csv
import json
import os
import re
import shutil
import sys
from types import SimpleNamespace

import httpx

import run_usage as ru

SEEN = {"anthropic": [], "openai": [], "google": [], "xai": [], "openrouter": []}
STORE = {}


def fake_tokens(body_text):
    n = len(body_text) // 4
    return n, 300 + n // 10, 500  # input, thinking, visible


def anthropic_handler(req):
    path = req.url.path
    if path == "/v1/messages/batches" and req.method == "POST":
        body = json.loads(req.content)
        STORE["anthropic_batch"] = body["requests"]
        SEEN["anthropic"] += [r["params"] for r in body["requests"]]
        return httpx.Response(200, json={"id": "msgbatch_1", "type": "message_batch", "processing_status": "in_progress",
                                         "request_counts": {"processing": len(body["requests"]), "succeeded": 0, "errored": 0, "canceled": 0, "expired": 0},
                                         "created_at": "2026-10-29T00:00:00Z", "expires_at": "2026-10-30T00:00:00Z", "ended_at": None,
                                         "cancel_initiated_at": None, "archived_at": None, "results_url": None})
    if path == "/v1/messages/batches/msgbatch_1":
        n = len(STORE["anthropic_batch"])
        return httpx.Response(200, json={"id": "msgbatch_1", "type": "message_batch", "processing_status": "ended",
                                         "request_counts": {"processing": 0, "succeeded": n, "errored": 0, "canceled": 0, "expired": 0},
                                         "created_at": "2026-10-29T00:00:00Z", "expires_at": "2026-10-30T00:00:00Z", "ended_at": "2026-10-29T00:30:00Z",
                                         "cancel_initiated_at": None, "archived_at": None,
                                         "results_url": "https://api.anthropic.com/v1/messages/batches/msgbatch_1/results"})
    if path == "/v1/messages/batches/msgbatch_1/results":
        lines = []
        for i, r in enumerate(STORE["anthropic_batch"]):
            inp, th, vis = fake_tokens(json.dumps(r["params"]))
            usage = {"input_tokens": inp, "output_tokens": th + vis, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}
            if i % 2 == 0:  # half report the breakdown, half exercise the count_tokens fallback
                usage["output_tokens_details"] = {"thinking_tokens": th}
            msg = {"id": f"msg_{i}", "type": "message", "role": "assistant", "model": r["params"]["model"],
                   "content": [{"type": "thinking", "thinking": "", "signature": "x"}, {"type": "text", "text": "answer " * vis}],
                   "stop_reason": "end_turn", "stop_sequence": None, "usage": usage}
            lines.append(json.dumps({"custom_id": r["custom_id"], "result": {"type": "succeeded", "message": msg}}))
        return httpx.Response(200, content="\n".join(lines).encode())
    if path == "/v1/messages/count_tokens":
        body = json.loads(req.content)
        return httpx.Response(200, json={"input_tokens": len(body["messages"][0]["content"]) // 7 + 3})
    return httpx.Response(404, json={"error": path})


def responses_payload(body, i=0):
    inp, th, vis = fake_tokens(json.dumps(body))
    return {"id": f"resp_{i}", "object": "response", "created_at": 0, "model": body["model"], "status": "completed",
            "output": [{"type": "message", "id": "m", "role": "assistant", "status": "completed",
                        "content": [{"type": "output_text", "text": "answer", "annotations": []}]}],
            "parallel_tool_calls": False, "tool_choice": "auto", "tools": [],
            "usage": {"input_tokens": inp, "input_tokens_details": {"cached_tokens": 0}, "output_tokens": th + vis,
                      "output_tokens_details": {"reasoning_tokens": th}, "total_tokens": inp + th + vis}}


def openai_handler(req):
    path = req.url.path
    if path == "/v1/files" and req.method == "POST":
        raw = req.content.decode(errors="ignore")
        STORE["openai_lines"] = [json.loads(l) for l in raw.splitlines() if l.startswith("{\"custom_id\"")]
        SEEN["openai"] += [l["body"] for l in STORE["openai_lines"]]
        return httpx.Response(200, json={"id": "file_in", "object": "file", "bytes": 1, "created_at": 0, "filename": "x.jsonl", "purpose": "batch", "status": "processed"})
    batch = {"id": "batch_1", "object": "batch", "endpoint": "/v1/responses", "input_file_id": "file_in", "completion_window": "24h",
             "created_at": 0, "status": "completed", "output_file_id": "file_out", "error_file_id": None,
             "request_counts": {"total": 1, "completed": 1, "failed": 0}}
    if path in ("/v1/batches", "/v1/batches/batch_1"):
        return httpx.Response(200, json=batch)
    if path == "/v1/files/file_out/content":
        out = [json.dumps({"id": f"r{i}", "custom_id": l["custom_id"], "response": {"status_code": 200, "body": responses_payload(l["body"], i)}, "error": None})
               for i, l in enumerate(STORE["openai_lines"])]
        return httpx.Response(200, content="\n".join(out).encode())
    if path == "/v1/responses":  # xAI direct
        body = json.loads(req.content)
        SEEN["xai"].append(body)
        return httpx.Response(200, json=responses_payload(body))
    return httpx.Response(404, json={"error": path})


def openrouter_handler(req):
    body = json.loads(req.content)
    SEEN["openrouter"].append(body)
    inp, th, vis = fake_tokens(json.dumps(body))
    return httpx.Response(200, json={"id": "gen-1", "object": "chat.completion", "created": 0, "model": body["model"], "provider": "FakeHost",
                                     "choices": [{"index": 0, "finish_reason": "stop", "message": {"role": "assistant", "content": "answer"}}],
                                     "usage": {"prompt_tokens": inp, "completion_tokens": th + vis, "total_tokens": inp + th + vis,
                                               "completion_tokens_details": {"reasoning_tokens": th}}})


def google_handler(req):
    path = req.url.path
    m = re.match(r".*/models/([^:]+):batchGenerateContent", path)
    if m:
        body = json.loads(req.content)
        reqs = body["batch"]["inputConfig"]["requests"]["requests"]
        STORE.setdefault("google", {})[m.group(1)] = reqs
        SEEN["google"] += reqs
        return httpx.Response(200, json={"name": f"batches/{m.group(1)}", "metadata": {"name": f"batches/{m.group(1)}", "state": "BATCH_STATE_PENDING"}})
    m = re.match(r".*/batches/(.+)$", path)
    if m:
        model = m.group(1)
        inlined = []
        for r in STORE["google"][model]:
            inp, th, vis = fake_tokens(json.dumps(r))
            inlined.append({"metadata": r.get("metadata"), "response": {
                "candidates": [{"content": {"role": "model", "parts": [{"text": "answer"}]}, "finishReason": "STOP"}],
                "usageMetadata": {"promptTokenCount": inp, "candidatesTokenCount": vis, "thoughtsTokenCount": th, "totalTokenCount": inp + th + vis}}})
        return httpx.Response(200, json={"name": f"batches/{model}", "metadata": {"name": f"batches/{model}", "state": "BATCH_STATE_SUCCEEDED",
                                         "output": {"inlinedResponses": {"inlinedResponses": inlined}}},
                                         "done": True, "response": {"inlinedResponses": {"inlinedResponses": inlined}}})
    return httpx.Response(404, json={"error": path})


def fake_client_for(provider):
    import anthropic
    import openai
    from google import genai
    if provider == "anthropic":
        import httpx2  # anthropic 1.x+ is built on httpx2
        def h2(req):
            r = anthropic_handler(req)
            return httpx2.Response(r.status_code, content=r.content, headers={"content-type": "application/json"})
        return anthropic.Anthropic(api_key="x", http_client=httpx2.Client(transport=httpx2.MockTransport(h2)))
    if provider == "openai":
        return openai.OpenAI(api_key="x", http_client=httpx.Client(transport=httpx.MockTransport(openai_handler)))
    if provider == "xai":
        return openai.OpenAI(api_key="x", base_url="https://api.x.ai/v1", http_client=httpx.Client(transport=httpx.MockTransport(openai_handler)))
    if provider == "openrouter":
        return openai.OpenAI(api_key="x", base_url="https://openrouter.ai/api/v1", http_client=httpx.Client(transport=httpx.MockTransport(openrouter_handler)))
    if provider == "google":
        return genai.Client(api_key="x", http_options={"httpx_client": httpx.Client(transport=httpx.MockTransport(google_handler))})


def main():
    ru.client_for = fake_client_for
    for env in ru.KEY_ENV.values():
        os.environ.setdefault(env, "test")
    run_id = "offline-test"
    shutil.rmtree(ru.RUNS_DIR / run_id, ignore_errors=True)
    args = SimpleNamespace(models=None, providers=None, repeats=1, dry_run=False, run_id=run_id)
    ru.cmd_submit(args)
    ru.cmd_status(SimpleNamespace(run_id=run_id))
    ru.cmd_collect(SimpleNamespace(run_id=run_id))

    with (ru.RUNS_DIR / run_id / "results.csv").open() as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 360, len(rows)
    assert not [r for r in rows if r["error"]], [r["error"] for r in rows if r["error"]][:3]
    assert all(r["thinking_tokens"] not in ("", None) for r in rows)
    assert {r["thinking_method"] for r in rows if r["provider"] == "anthropic"} == {"reported", "output minus counted visible text"}
    # Request shapes the labs expect
    a = SEEN["anthropic"][0]
    assert a["thinking"] == {"type": "adaptive"} and "effort" in a["output_config"] and "temperature" not in a
    o = SEEN["openai"][0]
    assert o["reasoning"]["effort"] in ("low", "medium", "max") and o["max_output_tokens"] == 64000
    g = SEEN["google"][0]
    tc = g["request"]["generationConfig"]["thinkingConfig"]  # the SDK sends snake_case here; proto JSON accepts both
    assert (tc.get("thinkingLevel") or tc.get("thinking_level")) in ("LOW", "MINIMAL", "MEDIUM", "HIGH"), g
    defaults = [b for b in SEEN["openrouter"] if "reasoning" not in b]
    assert len(defaults) == 4 * 8, len(defaults)  # the default level sends no reasoning setting
    with (ru.RUNS_DIR / run_id / "summary.csv").open() as f:
        summary = list(csv.DictReader(f))
    assert len(summary) == 45, len(summary)
    print(f"\nOffline test passed: 360 requests across 5 providers, 45 model-level summary rows.")
    shutil.rmtree(ru.RUNS_DIR / run_id, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
