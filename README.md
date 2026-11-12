# review-reply

<!-- mcp-name: io.github.omar-alsamman/review-reply -->

> MCP server for drafting professional replies to local-business reviews. Exposes 2 tools to help a small business answer Google reviews quickly and consistently.

Local businesses get reviews every day and answer them late, generically, or not at all. This server drafts a paste-ready reply in seconds — specific to what the reviewer actually said, never inventing discounts, staff names, refunds or promises, and always flagging 1–2 star reviews for a human to follow up.

**Free. No API keys. No network calls at runtime. Works fully offline.**

## Tools

| Tool | What it does |
|---|---|
| `draft_review_reply` | Draft a professional reply to one review (under 600 characters, paste-ready for Google), plus escalation flag, suggested follow-up, and what-not-to-say guidance. |
| `classify_review` | Triage a review: positive / mixed / negative band, sentiment score, detected topics, escalation flag, priority. |

`draft_review_reply` inputs: `review_text` (required), `rating` 1–5 (required), `business_name` (required), `business_type` (optional, e.g. "restaurant"), `tone` (optional: `warm` / `professional` / `apologetic`, default `warm`), `reviewer_name` (optional).

Safety rules in every draft:

- Never invents facts — no fake staff names, discounts, refunds or promises.
- Never admits legal fault, never blames the reviewer, never argues.
- 1–2 star reviews always flag `escalation_needed: true` and require human review before posting.

## Installation

Requires Python 3.10+.

```bash
git clone https://github.com/omar-alsamman/review-reply-mcp.git
cd review-reply-mcp
python -m pip install --upgrade "pip>=26.2"   # pip 24.0 has 6 known CVEs (PYSEC-2026-1795, -1796, -2875, -2876, -196, -3721); 26.2+ clears them all
pip install -r requirements.txt
python server.py
```

## Configuration

No configuration. No environment variables, no API keys, no accounts.

| Variable | Required | Description |
|---|---|---|
| — | — | None. The server is self-contained. |

## Usage

### Claude Desktop

Add to your Claude Desktop config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "review-reply": {
      "command": "python",
      "args": ["/absolute/path/to/review-reply-mcp/server.py"]
    }
  }
}
```

### Example

Review: *"Waited 40 minutes, staff were rude, and we were overcharged. Never going back."* — 1 star, Mario's Pizzeria (restaurant)

Reply drafted:

> Thank you for bringing this to our attention. We're very sorry — the wait should have been much better, and we understand your frustration. We take this seriously and would like the chance to make it right. Please reach out to us directly so we can look into it. — The team at Mario's Pizzeria

With `escalation_needed: true` and follow-up: owner/manager to contact the reviewer privately within 24 hours.

## Development

```bash
python test_review_reply.py   # unit tests + live MCP stdio smoke test
```

## Pricing

Free. A paid tier (if ever offered) would only add bulk triage / tone presets — the free draft tool stays free. No paid tier exists today.

## License

MIT — see [LICENSE](LICENSE).
