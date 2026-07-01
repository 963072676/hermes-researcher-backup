---
name: gateway-multiplexed-session-fence
description: Enforce session isolation across multiplexed gateway profiles (desktop+telegram+matrix in one process). Use when: (a) PR labels include sweeper:risk-session-state or sweeper:risk-message-delivery; (b) reviewer sees HOOKS_DIR/SKILLS_DIR resolved at import time; (c) session-bleed bug report from user.
---

# gateway-multiplexed-session-fence

> Hermes cross-profile isolation enforcement (v0.17.1 readiness, 2026-07-02).
> Triggered by GH #56456 (P1 session context bleeding) + #56508/#56523 (P2 multiplexed env).

## When to invoke

Run this skill BEFORE approving any PR or releasing any patch that touches:
- `gateway/hooks.py` (HOOKS_DIR, HERMES_HOME)
- `tools/skills_sync.py` (HERMES_HOME, SKILLS_DIR, MANIFEST_FILE)
- `tui_gateway/server.py` (clarify.respond, multiplexed session state)
- Any file with `get_hermes_home()` at module-import level

Also run on user reports of "tool call from another session appearing in my chat".

## Standard flow

1. **Detect**: grep for `_HERMES_HOME_OVERRIDE` and `get_hermes_home()` in changed files
2. **Verify**: each resolution point must be inside a per-request function, NOT at module scope
3. **Repro**: start 3 sessions on the same Hermes profile via desktop tui_gateway + telegram gateway + matrix gateway, fire concurrent tool calls
4. **Assert**: tool call response must route back to the originating session's chat surface
5. **Fail-fast**: any tool call routed to wrong surface → block merge

## How to write the verification script

```python
# scripts/verify_session_fence.py
import os
os.environ['HERMES_TEST_MULTIPLEX'] = '1'
# start 3 gateways in subprocess
# send tool call from session A, verify response surfaces in A
# send tool call from session B, verify response surfaces in B
# cross-check: session A's tool call NEVER appears in session B's transcript
```

## When NOT to invoke

- Single-session scenarios (CLI direct, no gateway)
- Web dashboard sessions (not multiplexed)
- Pre-v0.17 environments (ContextVar pattern not yet introduced)

## Pitfalls

- Do not assume `__pycache__` is enough; reset Python path between tests
- Use `subprocess.run` not thread — multiprocess isolation needed
- matrix gateway + telegram gateway sharing one process is the worst case, must test that combo

## Verification

- [ ] script exits 0 when fence is correct
- [ ] script exits 1 + dumps cross-session leak when fence is broken
- [ ] CI integrates the script for any `comp/gateway` PR

## Reference

- GH #56456 — P1 session context bleeding (closed but multiplexed path still open)
- GH #56508 / #56523 — P2 import-time resolve bug
- Tick22/23/24 daily-digest reports (researcher cron)
