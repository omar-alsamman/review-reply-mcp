# Official MCP Registry — status (2026-11-12)

Server: `io.github.omar-alsamman/review-reply` (v1.0.1)
Repo: https://github.com/omar-alsamman/review-reply-mcp
Package (not yet published): `review-reply-mcp` 1.0.1 on PyPI

## What is ready

- `server.json` written at repo root, version 1.0.1, matching `pyproject.toml`
  and `packages[0].version`. Schema:
  `https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json`
  (current official schema, confirmed 2026-11-12).
  `packages[0]` = `{registryType: "pypi", identifier: "review-reply-mcp",
  version: "1.0.1", transport: {type: "stdio"}}`.
  Repository = `{url: "https://github.com/omar-alsamman/review-reply-mcp",
  source: "github"}`. Description 71 chars (limit 100).
- README.md carries the PyPI ownership marker (HTML comment, top of file):
  `<!-- mcp-name: io.github.omar-alsamman/review-reply -->`. The registry
  verifies PyPI ownership by finding the exact string
  `mcp-name: io.github.omar-alsamman/review-reply` in the package README
  (which becomes the PyPI project description, since `pyproject.toml` sets
  `readme = "README.md"`). Verified against the official Package Types guide
  (https://modelcontextprotocol.io/registry/package-types, updated 2026-11-09).
- `mcp-publisher` v1.8.9 downloaded from the official releases
  (modelcontextprotocol/registry, SHA-256 verified against the release
  checksums: `4d527ca8f1ced0394c962dc925c2a4a4addef441cbefd62501c875e9481823a8`).
  `mcp-publisher validate` → **✅ server.json is valid**. First attempt failed
  with a transient registry network error (`Post
  "https://registry.modelcontextprotocol.io/v0/validate": EOF`); the retry
  passed. No login or publish was run.
- Package builds: `python -m build` produces
  `review_reply_mcp-1.0.1.tar.gz` (sdist) and
  `review_reply_mcp-1.0.1-py3-none-any.whl`. This needed a packaging fix:
  setuptools could not auto-discover the flat-layout module, so
  `[tool.setuptools] py-modules = ["server"]` was added to `pyproject.toml`.
  No server logic changed in v1.0.1.
- Wheel verified: installed in a fresh venv, version 1.0.1, the `review-reply`
  console script answers `initialize` → `tools/list`
  (`draft_review_reply`, `classify_review`) → `tools/call` with a correct
  1-star draft. WHEEL SMOKE TEST PASSED.
- Tests: `python test_review_reply.py` → **31 passed, 0 failed** on v1.0.1
  (see TEST_EVIDENCE.md). No runtime dependency changed.
- Built artifacts (`dist/`, `build/`, `*.egg-info/`) are NOT committed
  (added to `.gitignore`). The parent pushes the source only.

## What is BLOCKED — the exact Omar-only step

Publish is blocked on **PyPI account creation + 2FA, which only Omar can do**
(PyPI mandates 2FA on new accounts; it needs his authenticator). No PyPI
account was created, nothing was uploaded, no `mcp-publisher login` was run.

Exact steps remaining, in order (all $0):

1. **Omar creates a PyPI account** (https://pypi.org/account/register) and
   **enables 2FA with his authenticator app**. This is the only step that
   needs him; everything after it is agent work.
2. Agent: `python -m build` (already verified working) then
   `twine upload dist/*` with a PyPI API token from the new account.
   Confirm `https://pypi.org/project/review-reply-mcp/1.0.1/` exists and its
   description contains `mcp-name: io.github.omar-alsamman/review-reply`.
3. Agent: `mcp-publisher login github` (GitHub device flow, Omar's GitHub
   account `omar-alsamman` — proves the `io.github.omar-alsamman/` namespace).
4. Agent: `mcp-publisher publish` from the repo directory.
5. Agent: verify live at
   `https://registry.modelcontextprotocol.io/v0.1/servers/io.github.omar-alsamman%2Freview-reply`
   and record the URL. PulseMCP auto-ingests from the Official Registry when
   it reopens (its submissions are paused; do not submit there directly).

## Vulnerability fix — mcp-marketplace.io scan (6.2/10 Moderate, 5 high, 0 critical)

### Finding (honest version)

`pip-audit` in a fresh venv with `mcp[cli]>=1.0,<2` installed (Python 3.12.3)
reported **"Found 12 known vulnerabilities in 1 package" — the ONLY flagged
package was pip 24.0 itself**. No runtime dependency was flagged: mcp 1.30.0
and its whole tree (anyio 4.16.0, httpx 0.28.1, pydantic 2.14.3, starlette
1.10.0, etc.) came back clean. pip-audit lists each CVE twice (two
advisory sources), so the 12 entries are **6 unique CVEs**:

| CVE (PYSEC ID) | Fix version | One-line description |
|---|---|---|
| PYSEC-2026-1795 | 25.3 | Tar extraction may not check symlinks stay inside the target dir (PEP 706 fallback; Python 3.12 already implements PEP 706, so this code path is not used here) |
| PYSEC-2026-1796 | 26.0 | Malicious wheel archive may extract files outside the install dir (path traversal limited to install-dir prefixes) |
| PYSEC-2026-2875 | 26.1 | Concatenated tar+ZIP files treated as ZIP regardless of filename |
| PYSEC-2026-2876 | 26.1 | Self-update check runs after wheel install, importing freshly installed modules |
| PYSEC-2026-196 | 26.1.2 | console_scripts/gui_scripts treated as paths, installed outside the install dir |
| PYSEC-2026-3721 | 26.2 | Doubly-encoded package URLs from an index may install files to arbitrary locations (needs a malicious index; mainly affects `pip download --only-binary`) |

The marketplace scan's "5 high" is consistent with these pip CVEs under a
different counting/severity mapping (6 unique pip CVEs, 0 in runtime code).
The scan detail was not visible, so this is stated as consistency, not as a
verified one-to-one match. **No runtime vulnerability was found, so no
runtime dependency was changed and no fix was faked.**

### Fix

- pip is the installer, not a shipped runtime dependency of this package, so
  there is nothing to pin in `pyproject.toml` dependencies. The fix is in the
  install environment: upgrade pip to **26.2 or newer** (26.3 installed and
  verified here — the highest fix version among the six CVEs is 26.2).
- Documented in three places: README.md install steps
  (`python -m pip install --upgrade "pip>=26.2"` before installing
  requirements), a comment in `requirements.txt`, and this file.
- mcp stays on 1.x (`mcp[cli]>=1.0,<2`, installed 1.30.0) — no migration to
  SDK 2.x.

### Before / after pip-audit output

BEFORE (fresh venv, pip 24.0, 2026-11-12):

```
Found 12 known vulnerabilities in 1 package
Name Version ID              Fix Versions
---- ------- --------------- ------------
pip  24.0    PYSEC-2026-1795 25.3
pip  24.0    PYSEC-2026-1796 26.0
pip  24.0    PYSEC-2026-2875 26.1
pip  24.0    PYSEC-2026-2876 26.1
pip  24.0    PYSEC-2026-196  26.1.2
pip  24.0    PYSEC-2026-3721 26.2
(each ID listed twice by pip-audit — 12 entries, 6 unique CVEs)
```

AFTER (`pip install --upgrade pip` → pip 26.3, same venv, same deps):

```
No known vulnerabilities found
```

### Unfixable items

None. All 6 unique CVEs have fixed versions and are cleared by pip >= 26.2.
No runtime dependency vulnerability was found to fix.

### Follow-up

The mcp-marketplace.io security score (6.2/10) was computed against v1.0.0.
After the parent pushes v1.0.1, the listing should be re-checked — if the
scanner re-runs on the new commit it should clear the pip findings; if it
still flags 5 high, get its per-package detail before changing anything.
