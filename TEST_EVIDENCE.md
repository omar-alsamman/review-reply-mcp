# Test evidence — review-reply MCP server v1.0.0

Run: `python test_review_reply.py` (Python 3.12, MCP SDK 1.x, `mcp[cli]>=1.0,<2`)
Date: 2026-11-10. Result: **31 passed, 0 failed — ALL TESTS PASSED.**

Full output of the final run:

```
5-star thank-you:
    Thank you, Sarah! We're delighted to hear it — Best pizza in town, highly recommend. Thank you for choosing Mario's Pizzeria, and we hope to welcome you back soon! — The team at Mario's Pizzeria
  PASS  5-star <=600 chars
  PASS  5-star names reviewer
  PASS  5-star references specifics (food/staff/pizza)
  PASS  5-star quotes a specific detail
  PASS  5-star no escalation
  PASS  5-star no invented discount/refund
3-star mixed:
    Thank you so much! We appreciate the honest feedback — we're glad parts of the wait worked, and we hear you on the rest. We'd love the chance to do better next time, so please let us know how we can improve. — The team at Mario's Pizzeria
  PASS  3-star <=600 chars
  PASS  3-star acknowledges mixed feedback
  PASS  3-star no escalation
1-star complaint (wait + rude + overcharged):
    Thank you for bringing this to our attention. We're very sorry — the wait should have been much better, and we understand your frustration. We take this seriously and would like the chance to make it right. Please reach out to us directly so we can look into it. — The team at Mario's Pizzeria
  PASS  1-star <=600 chars
  PASS  1-star apologises
  PASS  1-star names the issue (wait)
  PASS  1-star escalation flagged
  PASS  1-star human review required
  PASS  1-star invites direct contact
  PASS  1-star no invented discount/refund
  PASS  1-star does not argue
  PASS  1-star topics detected
2-star (non-restaurant, trades):
    Thank you for bringing this to our attention. We're sorry the wait fell short — that's not the experience we want to give. We take this seriously and would like to make it right. Please reach out to us directly so we can look into it. — The team at Radiant Plumbing & Air
  PASS  2-star <=600 chars
  PASS  2-star escalation flagged
Validation:
  PASS  rating 0 rejected
  PASS  rating 6 rejected
  PASS  empty review rejected
  PASS  empty business rejected
Classify:
    {'band': 'negative', 'sentiment_score': -1.0, 'positive_signals': 0, 'negative_signals': 2, 'detected_topics': ['wait_time', 'staff_service', 'price'], 'escalation_needed': True, 'priority': 'high'}
  PASS  classify 1-star = negative/high
  PASS  classify 5-star = positive/low
MCP stdio smoke test (initialize -> tools/list -> tools/call):
  PASS  initialize returns serverInfo
    tools: ['draft_review_reply', 'classify_review']
  PASS  tools/list has draft_review_reply
  PASS  tools/list has classify_review
    tools/call draft: Thank you for bringing this to our attention. We're very sorry — the wait should have been much better, and we understand your frustration. We take this seriously and would like the chance to make it right. Please reach out to us directly so we can look into it. — The team at Mario's Pizzeria
  PASS  tools/call returns draft <=600
  PASS  tools/call escalation true

31 passed, 0 failed
ALL TESTS PASSED
```

## Notes / bugs found and fixed during testing

1. **MCP 2.x renamed FastMCP → MCPServer.** Pinned `mcp>=1.0,<2` in `requirements.txt` / `pyproject.toml` so the standard FastMCP code works. (Upgrading to the v2 API is a later, optional step.)
2. **MCP stdio is newline-delimited JSON-RPC, not LSP `Content-Length` framing.** The first smoke-test harness used LSP framing and hung; fixed to NDJSON and the live `initialize → tools/list → tools/call` sequence now passes.
3. **Tone fixes:** a chirpy "Thank you so much!" before a 1-star apology, and a doubled "Thank you" in the 3-star draft, were both fixed before the final run.

---

# Test evidence — review-reply MCP server v1.0.1

Run: `python test_review_reply.py` (Python 3.12, MCP SDK 1.x, `mcp[cli]>=1.0,<2`, pip 26.3)
Date: 2026-11-12. Result: **31 passed, 0 failed — ALL TESTS PASSED.**

Changes in v1.0.1 vs v1.0.0: version bump only + packaging fix (`[tool.setuptools] py-modules = ["server"]` so `python -m build` works) + pip>=26.2 install note. No server logic changed.

Full output of the final run:

```
5-star thank-you:
    Thank you, Sarah! We're delighted to hear it — Best pizza in town, highly recommend. Thank you for choosing Mario's Pizzeria, and we hope to welcome you back soon! — The team at Mario's Pizzeria
  PASS  5-star <=600 chars
  PASS  5-star names reviewer
  PASS  5-star references specifics (food/staff/pizza)
  PASS  5-star quotes a specific detail
  PASS  5-star no escalation
  PASS  5-star no invented discount/refund
3-star mixed:
    Thank you so much! We appreciate the honest feedback — we're glad parts of the wait worked, and we hear you on the rest. We'd love the chance to do better next time, so please let us know how we can improve. — The team at Mario's Pizzeria
  PASS  3-star <=600 chars
  PASS  3-star acknowledges mixed feedback
  PASS  3-star no escalation
1-star complaint (wait + rude + overcharged):
    Thank you for bringing this to our attention. We're very sorry — the wait should have been much better, and we understand your frustration. We take this seriously and would like the chance to make it right. Please reach out to us directly so we can look into it. — The team at Mario's Pizzeria
  PASS  1-star <=600 chars
  PASS  1-star apologises
  PASS  1-star names the issue (wait)
  PASS  1-star escalation flagged
  PASS  1-star human review required
  PASS  1-star invites direct contact
  PASS  1-star no invented discount/refund
  PASS  1-star does not argue
  PASS  1-star topics detected
2-star (non-restaurant, trades):
    Thank you for bringing this to our attention. We're sorry the wait fell short — that's not the experience we want to give. We take this seriously and would like the chance to make it right. Please reach out to us directly so we can look into it. — The team at Radiant Plumbing & Air
  PASS  2-star <=600 chars
  PASS  2-star escalation flagged
Validation:
  PASS  rating 0 rejected
  PASS  rating 6 rejected
  PASS  empty review rejected
  PASS  empty business rejected
Classify:
    {'band': 'negative', 'sentiment_score': -1.0, 'positive_signals': 0, 'negative_signals': 2, 'detected_topics': ['wait_time', 'staff_service', 'price'], 'escalation_needed': True, 'priority': 'high'}
  PASS  classify 1-star = negative/high
  PASS  classify 5-star = positive/low
MCP stdio smoke test (initialize -> tools/list -> tools/call):
  PASS  initialize returns serverInfo
    tools: ['draft_review_reply', 'classify_review']
  PASS  tools/list has draft_review_reply
  PASS  tools/list has classify_review
    tools/call draft: Thank you for bringing this to our attention. We're very sorry — the wait should have been much better, and we understand your frustration. We take this seriously and would like the chance to make it right. Please reach out to us directly so we can look into it. — The team at Mario's Pizzeria
  PASS  tools/call returns draft <=600
  PASS  tools/call escalation true

31 passed, 0 failed
ALL TESTS PASSED
```

## v1.0.1 extra checks (2026-11-12)

- `pip-audit` on the same venv after upgrading pip 24.0 -> 26.3: **No known vulnerabilities found** (was 12 entries, all pip-only — see REGISTRY.md).
- `python -m build`: sdist `review_reply_mcp-1.0.1.tar.gz` + wheel `review_reply_mcp-1.0.1-py3-none-any.whl` built successfully.
- Wheel install test (fresh venv): `pip install review_reply_mcp-1.0.1-py3-none-any.whl` → version 1.0.1; `review-reply` console script answers `initialize` (serverInfo `review-reply`), `tools/list` (`draft_review_reply`, `classify_review`), and `tools/call draft_review_reply` returns a correct 1-star draft. WHEEL SMOKE TEST PASSED.
- `mcp-publisher validate` (v1.8.9): **✅ server.json is valid** (first attempt hit a transient registry `EOF` network error; retry passed).
