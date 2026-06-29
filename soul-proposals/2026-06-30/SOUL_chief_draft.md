# SOUL proposal (chief profile) — 2026-06-30

## Trigger
PR #55013 (open 2026-06-30, P0 comp/gateway): cross-process lock contention on session_id switch.

## Affected surface
- `gateway/cross_process.py` — lock acquisition
- `cron/tick_runner.py` — cron→manual handoff
- `delegation/subagent.py` — manual→subagent handoff

## Drafted rule (proposed add to chief SOUL)
> Cross-process locks MUST be session-scoped, not auth-scoped. When auth remains constant but session_id changes (cron→manual, manual→subagent), the lock MUST be released by the previous process and acquired by the new process without contention. Stale locks are a resource leak.

## Why this rule
Chief profile runs cron + manual + subagent in parallel. A stale lock blocks downstream tasks. PR #55013 ships the fix; SOUL rule prevents the regression from coming back.

## Affected files
- `~/.hermes/profiles/chief/SOUL.md` (append)

## Status
PROPOSAL — pending chief profile user approval.
