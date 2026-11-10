# Marketplace listing research — review-reply MCP server

Researched 2026-11-10 via web search. No accounts created, nothing paid,
nothing submitted. All four targets below are FREE to list; paid tiers are
NOT configured anywhere.

## 1. MCPize — submit first (hosting + payments + listing in one)

- Publish page: https://mcpize.com/developers/publish-mcp-server
- What it needs: a free developer account (email verification only, no card);
  install the MCPize CLI, run `mcpize init`, deploy with `mcpize deploy`;
  pricing in `mcpize.yaml` or the dashboard. Free servers need NO Stripe
  account — Stripe is only for paid tiers.
- Revenue: creator keeps **80%** (85% Founding Member rate only for servers
  monetized before 2026-06-10 — that window has closed, so 80% applies).
- Free hosting tier: figures found conflict — the lane brief says 25K req/mo,
  a directory listing says 250K req/mo on the Free plan (0.5 vCPU, 512 MB).
  **Verify the actual free-tier limit on the MCPize dashboard at signup.**
- Our file: `mcpize.yaml` in this repo (free tier only, 100 calls/day).
- Listing checklist: [ ] create MCPize account with ionixselonita@gmail.com
  (Google sign-in first if offered) [ ] `mcpize init` + `mcpize deploy` from
  the GitHub repo [ ] confirm listing is live + free, no Stripe connected.

## 2. mcp-marketplace.io — submit second (curated, Stripe checkout)

- Creator page: https://mcp-marketplace.io/for-creators
- Docs: https://mcp-marketplace.io/docs
- What it needs: fill out the listing form (server details, pricing free or
  paid); an instant security scan validates it as a real MCP server.
  Free and open-source servers explicitly welcome; Stripe Connect is only
  connected during onboarding for paid servers.
- Revenue: creators keep **85%** (85/15 split); one-time or subscription.
- Listing checklist: [ ] submit the listing form as FREE [ ] pass the
  security scan [ ] confirm live listing, do NOT connect Stripe.

## 3. Smithery — submit third (directory, Claude Desktop / Cursor install UI)

- Submit a GitHub repo URL at smithery.ai/submit.
- What it needs: `smithery.yaml` in the repo root (done — see `smithery.yaml`;
  no config required, no API keys, so the config form is empty), plus
  `pyproject.toml` metadata (done — description becomes the listing card text).
  Smithery's crawler verifies within minutes to hours; it re-crawls weekly
  and can drop the verified badge if the server regresses.
- Quality notes: tool descriptions are verb-first ("Draft…", "Classify…"),
  server `instructions` are sent on initialize, config schema is minimal —
  all three score well on Smithery's quality audit.
- **Change since the brief:** Smithery's hosted proxy shut down 2026-10-31 —
  `run.tools` / `server.smithery.ai` URLs no longer work; smithery.ai now
  runs as a plain directory (Arcade.dev). So Smithery gives discovery, not
  hosting — the server stays a stdio/GitHub install.
- Listing checklist: [ ] push repo to GitHub [ ] submit repo URL at
  smithery.ai/submit [ ] confirm verified listing appears.

## 4. PulseMCP — DO NOT submit directly (submissions paused)

- PulseMCP's submit page (note dated 2026-09-03, confirmed by checks on
  2026-10-07 and 2026-10-31) says it is **not taking new servers or listing
  changes right now** and tells authors to publish to the Official MCP
  Registry instead — it will pick servers up automatically when it reopens.
  No reopening date given.
- Route instead: **Official MCP Registry** (registry.modelcontextprotocol.io)
  — free, no review queue. Publish with the `mcp-publisher` CLI and a
  `server.json`. Namespace via GitHub login is `io.github.omar-alsamman/...`
  (GitHub username `omar-alsamman` is verified from the existing
  omar-alsamman.github.io Pages site). A `server.json` is NOT yet written —
  it needs the live GitHub repo URL + a published package, so the parent
  should generate it with `mcp-publisher init` after the repo exists.
- Listing checklist: [ ] create GitHub repo [ ] `mcp-publisher init` +
  publish to the Official Registry [ ] watch for PulseMCP auto-ingest later;
  do not pay anyone for a "fast lane".

## Still unknown (not verified in this research)

- **dotMCP** and **Global Agentic Market Exchange** (95% keep, daily Stripe
  Connect payouts above $10, from the lane brief): listing flow, free-tier
  terms and revenue share NOT re-verified here. Check before submitting.
- MCPize free-tier request limit (25K vs 250K/mo — see §1).
- Whether MCPize's CLI deploy accepts a pure-stdio Python server as-is or
  wants an HTTP wrapper — test with `mcpize deploy` on the free tier.

## Order of operations for the parent

1. Create GitHub repo `omar-alsamman/review-reply-mcp` (public), push this
   directory, add the `mcp-server` GitHub topic (helps PulseMCP / MCP.so
   discovery), set repo description from `pyproject.toml`.
2. MCPize free deploy → confirm live.
3. mcp-marketplace.io free listing form → confirm live.
4. Smithery submit → confirm verified.
5. Official MCP Registry publish via `mcp-publisher` → covers PulseMCP later.
6. Record live URLs + install counts in the lane GOAL.md. Paid tier only
   after installs appear AND only with Omar's explicit go-ahead.
