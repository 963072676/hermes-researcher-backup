# SOUL proposal (dev profile) — 2026-06-30

## Trigger
PR #55030 (open 2026-06-30, P0 comp/agent): MoA aggregator prompt placement breaks KV-cache affinity.

## Affected surface
- `agent/moa_loop.py` — aggregator prompt construction
- `hermes_cli/moa_config.py` — preset definitions
- `tools/mixture_of_agents_tool.py` — legacy tool (deprecated in v0.17.0)

## Drafted rule (proposed add to dev SOUL)
> MoA aggregator prompts MUST place all variable content (user query, reference materials) at the END of the prompt, after a stable prefix. Reference blocks MUST be appended last, not interspersed. This preserves OpenRouter/Anthropic prompt_cache_key stability and reduces cache miss cost.

## Why this rule
Dev profile runs MoA tests heavily. Cache miss = full price (1.20 per million completion tokens). PR #55030 ships the fix; SOUL rule documents the invariant for future aggregator PRs.

## Affected files
- `~/.hermes/profiles/dev/SOUL.md` (append)

## Status
PROPOSAL — pending dev profile user approval.
