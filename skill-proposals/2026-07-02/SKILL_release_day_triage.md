---
name: v0-release-day-triage
description: Coordinate 5-profile acceptance + upgrade checklist when a new Hermes release lands. Use when: (a) GitHub Releases listing shows new tag; (b) cron detects `commits_ahead > 1000` + `last push < 24h`; (c) user announces release window.
---

# v0-release-day-triage

> Hermes release coordination across chief/pm/dev/qa/default (v0.17.1 readiness, 2026-07-02).
> Triggered by: 1945 commits ahead of v0.17.0, latest release 13d old, daily-digest continuous major signal.

## When to invoke

- A new tag appears in `https://github.com/NousResearch/hermes-agent/releases`
- `commits_ahead_of_main > 1000` AND `pushed_at < 24h ago` AND `first_seen_daily > 20`
- User explicitly announces "准备升级" / "ship day" in Feishu DM

## Standard flow

1. **Detect release**:
   ```bash
   curl -sL --noproxy '*' https://api.github.com/repos/NousResearch/hermes-agent/releases/latest
   ```
2. **Pre-test gate** (parallel, 6h before release ship):
   - chief → `security_context_isolation_check` on all 5 profiles
   - pm → write release notes digest to Feishu oc_c653562b
   - dev → run `verify_session_fence` against the candidate SHA
   - qa → run session-bleed regression suite
   - default → `hermes --version` + compare local `~/.hermes/profiles/*/SOUL.md` against release `## Breaking changes` section
3. **Ship gate** (user-triggered `hermes update`):
   - record pre-upgrade `hermes --version` output
   - run upgrade
   - run post-upgrade health check (`hermes cron list` + `hermes tools`)
   - re-run pre-test gate; log delta
4. **Post-ship**:
   - 24h monitor for first-seen P0/P1 issues mentioning upgrade
   - update `~/.hermes/memories/MEMORY.md` with new version

## Deliverables

- `~/.hermes/cron/output/release-day/YYYY-MM-DD/acceptance-criteria.md` (pm)
- `~/.hermes/cron/output/release-day/YYYY-MM-DD/security-check.md` (chief)
- `~/.hermes/cron/output/release-day/YYYY-MM-DD/verify-session-fence.log` (dev)
- `~/.hermes/cron/output/release-day/YYYY-MM-DD/regression-suite.log` (qa)
- `~/.hermes/cron/output/release-day/YYYY-MM-DD/post-upgrade-health.md` (default)

## When NOT to invoke

- patch releases < 100 commits — too small for full triage, just default profile health check
- pre-v0.16 environments (no 5-profile structure)

## Pitfalls

- `hermes update` may take 5-15min on slow connections — don't kill process early
- New release may have new SOUL/skills schema — check before copying old proposals
- Don't commit `QUARANTINE/` files in the same commit as release artifacts

## Verification

- [ ] 4 deliverables generated and pushed to backup repo
- [ ] Feishu DM to oc_c653562b sent with release notes + acceptance status
- [ ] post-upgrade `hermes --version` matches new tag

## Reference

- GH releases API: https://api.github.com/repos/NousResearch/hermes-agent/releases
- Tick11 (release-version-skip-pattern.md)
- Tick22-24 daily-digest reports
