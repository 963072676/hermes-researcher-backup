# SOUL proposal (pm profile) — 2026-06-30

## Trigger
PR #55019 (closed-not-merged 2026-06-30) + PR #55017 (open): feishu multi-app session isolation + multiplex_profiles per-group require_mention.

## Affected surface
- `platforms/feishu/multi_app.py` — multi-app routing
- `platforms/feishu/multiplex.py` — profile multiplexing
- `platforms/feishu/group_policy.py` — per-group rules

## Drafted rule (proposed add to pm SOUL)
> Feishu multi-app sessions MUST be isolated by app_id. multiplex_profiles MUST honor per-group require_mention flag. A group that sets require_mention=false MUST NOT receive bot replies unless explicitly @mentioned. Per-group overrides take precedence over default config.

## Why this rule
PM profile coordinates multi-app feishu bots across groups. Without isolation, app A's session state leaks into app B. Without per-group require_mention, bot spams groups that want silent observation. PR #55019 closed-not-merged; PR #55017 is the new attempt. SOUL rule codifies expected behavior.

## Affected files
- `~/.hermes/profiles/pm/SOUL.md` (append)

## Status
PROPOSAL — pending pm profile user approval.
