# SOUL proposal (qa profile) — 2026-06-30

## Trigger
20+ sweep-tagged P0/P1 PRs (label: sweeper) opened 2026-06-30: #55013, #55016, #55025, #55026, #55029, #55030, #55045, #54997, #54979, #55003, #55050, #55049, #54994, #54969, etc.

## Affected surface
- `tests/sweeper/` — regression detection suite
- `tests/conftest.py` — fixtures
- `qa/regression_catalog.md` — known regressions

## Drafted rule (proposed add to qa SOUL)
> Sweep-tagged PRs MUST add a regression test to tests/sweeper/ in the same PR. The test MUST reproduce the bug on the prior commit and pass on the fix commit. Sweep PRs without a regression test are blocked at review. The regression catalog MUST be updated to mark the bug as "sweep-detected, fix-in-PR-N".

## Why this rule
QA profile owns the sweeper suite. 20+ sweep PRs in one day indicates active regression hunt; without a regression test per PR, regressions can re-appear. SOUL rule enforces test-before-merge.

## Affected files
- `~/.hermes/profiles/qa/SOUL.md` (append)

## Status
PROPOSAL — pending qa profile user approval.
