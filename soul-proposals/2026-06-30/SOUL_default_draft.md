# SOUL proposal (default profile) — 2026-06-30

## Trigger
PR #55029 (open 2026-06-30, P0 comp/gateway): cross-session agent-cache leak when session_id switches under same auth.

## Affected surface
- `feishu_dm.py` handler — multi-session DM routing
- `gateway/agent_cache.py` — cache key derivation
- `mcp_project_memory` — cached agent state

## Drafted rule (proposed add to default SOUL)
> Cross-session agent-cache is forbidden by default. Cache key MUST include session_id. When session_id switches under same auth, the old cache entry MUST be evicted before the new agent instance is constructed. Cross-session cache reuse is a security boundary violation.

## Why this rule
Default profile routes MiniMax-M3 responses to multiple feishu DM users. A cache leak could serve user A's response to user B — security incident. PR #55029 ships the fix; SOUL rule makes the invariant explicit for future regressions.

## Affected files
- `~/.hermes/agents/default/SOUL.md` (append)
- `~/.hermes/profiles/default/memory/agent-cache-policy.md` (new)

## Status
PROPOSAL — pending default profile user approval.
