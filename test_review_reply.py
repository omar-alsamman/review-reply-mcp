"""Tests for review-reply MCP server.

Run:  python test_review_reply.py
Covers the quality bar from the brief (5-star / 3-star / 1-star with
specifics, <=600 chars, no invented facts, 1-2 star escalation) plus a
live MCP stdio smoke test: initialize -> tools/list -> tools/call.
"""

import json
import subprocess
import sys

sys.path.insert(0, ".")
from server import build_draft, classify  # noqa: E402

PASS = []
FAIL = []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f" — {detail}" if detail and not cond else ""))


def test_five_star():
    print("5-star thank-you:")
    r = build_draft(
        "Amazing food and the staff were so friendly! Best pizza in town, highly recommend.",
        5, "Mario's Pizzeria", "restaurant", reviewer_name="Sarah",
    )
    print(f"    {r['draft_reply']}")
    check("5-star <=600 chars", r["draft_chars"] <= 600, str(r["draft_chars"]))
    check("5-star names reviewer", "Sarah" in r["draft_reply"])
    check("5-star references specifics (food/staff/pizza)", any(w in r["draft_reply"].lower() for w in ("food", "staff", "pizza")))
    check("5-star quotes a specific detail", "pizza" in r["specific_detail_quoted"].lower())
    check("5-star no escalation", r["escalation_needed"] is False)
    check("5-star no invented discount/refund", "discount" not in r["draft_reply"].lower() and "refund" not in r["draft_reply"].lower())


def test_three_star():
    print("3-star mixed:")
    r = build_draft(
        "Food was good but the place was noisy and service was slow.",
        3, "Mario's Pizzeria", "restaurant",
    )
    print(f"    {r['draft_reply']}")
    check("3-star <=600 chars", r["draft_chars"] <= 600)
    check("3-star acknowledges mixed feedback", "honest feedback" in r["draft_reply"].lower() or "hear you" in r["draft_reply"].lower())
    check("3-star no escalation", r["escalation_needed"] is False)


def test_one_star():
    print("1-star complaint (wait + rude + overcharged):")
    r = build_draft(
        "Waited 40 minutes, staff were rude, and we were overcharged. Never going back.",
        1, "Mario's Pizzeria", "restaurant",
    )
    print(f"    {r['draft_reply']}")
    check("1-star <=600 chars", r["draft_chars"] <= 600, str(r["draft_chars"]))
    check("1-star apologises", "sorry" in r["draft_reply"].lower())
    check("1-star names the issue (wait)", "wait" in r["draft_reply"].lower())
    check("1-star escalation flagged", r["escalation_needed"] is True)
    check("1-star human review required", r["human_review_required"] is True)
    check("1-star invites direct contact", "reach out" in r["draft_reply"].lower())
    check("1-star no invented discount/refund", "discount" not in r["draft_reply"].lower() and "refund" not in r["draft_reply"].lower())
    check("1-star does not argue", "wrong" not in r["draft_reply"].lower() and "actually" not in r["draft_reply"].lower())
    check("1-star topics detected", "wait_time" in r["detected_topics"] and "price" in r["detected_topics"], str(r["detected_topics"]))


def test_two_star_plumber():
    print("2-star (non-restaurant, trades):")
    r = build_draft(
        "Technician arrived late and left a mess. Work itself was fine but communication was poor.",
        2, "Radiant Plumbing & Air", "plumbing company",
    )
    print(f"    {r['draft_reply']}")
    check("2-star <=600 chars", r["draft_chars"] <= 600)
    check("2-star escalation flagged", r["escalation_needed"] is True)


def test_validation():
    print("Validation:")
    for name, fn in [
        ("rating 0 rejected", lambda: build_draft("ok", 0, "Biz")),
        ("rating 6 rejected", lambda: build_draft("ok", 6, "Biz")),
        ("empty review rejected", lambda: build_draft("  ", 5, "Biz")),
        ("empty business rejected", lambda: build_draft("ok", 5, "  ")),
    ]:
        try:
            fn()
            check(name, False, "no error raised")
        except ValueError:
            check(name, True)


def test_classify():
    print("Classify:")
    c = classify("Waited 40 minutes, staff were rude, overcharged.", 1)
    print(f"    {c}")
    check("classify 1-star = negative/high", c["band"] == "negative" and c["priority"] == "high")
    c2 = classify("Amazing food, friendly staff, highly recommend!", 5)
    check("classify 5-star = positive/low", c2["band"] == "positive" and c2["priority"] == "low")


def _rpc(proc, method, params=None, req_id=1):
    # MCP stdio transport is newline-delimited JSON-RPC, NOT LSP framing.
    msg = {"jsonrpc": "2.0", "id": req_id, "method": method}
    if params is not None:
        msg["params"] = params
    proc.stdin.write((json.dumps(msg) + "\n").encode())
    proc.stdin.flush()
    while True:
        line = proc.stdout.readline().decode().strip()
        if not line:
            raise RuntimeError("server closed stdout waiting for " + method)
        data = json.loads(line)
        if data.get("id") == req_id:
            return data
        # else: a server notification — skip it and keep reading.


def test_mcp_stdio():
    print("MCP stdio smoke test (initialize -> tools/list -> tools/call):")
    proc = subprocess.Popen(
        [sys.executable, "server.py"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    try:
        init = _rpc(proc, "initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "1.0"},
        })
        check("initialize returns serverInfo", "result" in init and "serverInfo" in init["result"], str(init)[:200])
        proc.stdin.write((json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n").encode())
        proc.stdin.flush()
        tools = _rpc(proc, "tools/list", {}, req_id=2)
        names = [t["name"] for t in tools["result"]["tools"]]
        print(f"    tools: {names}")
        check("tools/list has draft_review_reply", "draft_review_reply" in names)
        check("tools/list has classify_review", "classify_review" in names)
        call = _rpc(proc, "tools/call", {
            "name": "draft_review_reply",
            "arguments": {
                "review_text": "Waited 40 minutes, staff were rude, and we were overcharged.",
                "rating": 1, "business_name": "Mario's Pizzeria",
                "business_type": "restaurant",
            },
        }, req_id=3)
        text = call["result"]["content"][0]["text"]
        data = json.loads(text)
        print(f"    tools/call draft: {data['draft_reply']}")
        check("tools/call returns draft <=600", len(data["draft_reply"]) <= 600)
        check("tools/call escalation true", data["escalation_needed"] is True)
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


if __name__ == "__main__":
    test_five_star()
    test_three_star()
    test_one_star()
    test_two_star_plumber()
    test_validation()
    test_classify()
    test_mcp_stdio()
    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        print("FAILED:", FAIL)
        sys.exit(1)
    print("ALL TESTS PASSED")
