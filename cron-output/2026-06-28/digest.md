# 🧬 Researcher Self-Evolution Daily Digest · 2026-06-28 (tick19)

**Cron**: hermes-researcher-deep-tick-daily · **Profile**: researcher · **Model**: xai-oauth/grok-4.3
**Backup**: https://github.com/963072676/hermes-researcher-backup/commit/a6f8472
**Snapshot**: `memory-snapshots/tick19.json` · **Audit**: `docs/audit/2026-06-28.md`

## Scan Summary

| Source | Items | Notable |
|---|---|---|
| GitHub (last 3d) | 100 (27 issues + 73 PRs) | **#53715 P1** secret leak, **#53667 P1** tool collapse, 2x P2 |
| HN Algolia | 18 (5 queries) | "Skillmaxxing" 2pts, "Smart routing" 193pts |
| OpenRouter | 91/339 Chinese (27%) | M3 stable $0.30/M, GLM-5.2/Qwen3.7 new |
| arxiv | 0 | export endpoint issue (retry tick20) |
| Repo | pushed_at 2026-06-27 16:53Z | active dev, v0.17.0 still latest |

## Top P1 Findings (v0.17.0 silent degradation wave)

### #53715 — Terminal subprocess env leaks AUXILIARY/GATEWAY_RELAY secrets (P1, open PR, MERGEABLE)
- **Severity**: P1 security boundary
- **Mechanism**: name-based exact match in `_HERMES_PROVIDER_ENV_BLOCKLIST` misses `AUXILIARY_*_API_KEY` (gateway/run.py:1564-1570) and `GATEWAY_RELAY_SECRET` (gateway/relay/__init__.py:553-555)
- **Impact**: any terminal command in gateway session leaks these to child processes, logs, envs
- **Fix in PR**: `_is_hermes_internal_secret(name)` helper + substring match, 3 files +110/-3
- **Profiles affected**: dev / qa / researcher / default (4/5)

### #53667 — Tool loader collapses to cronjob-only in v0.17.0 fresh install (P1)
- **Severity**: P1 functional regression
- **Mechanism**: import failure `cannot import name 'get_environment' from 'tools.environment'` — doctor reports OK but runtime silent drops web/file/terminal
- **Impact**: default profile hermes-self-evolution-digest completely fails on fresh install (no web_search/terminal/file)
- **Mitigations**: 1-line sentinel + fallback to urllib GitHub/HN/OpenRouter

## 5 SOUL drafts (cap=5)

1. **dev / Security Boundary** — terminal env leak pre-check (P1)
2. **chief / P1 Triage Workflow** — affected-range matrix required (P1)
3. **researcher / MCP write tool preference** — MCP tool > mcp_writer.py urllib (P2)
4. **default / v0.17.0 fresh install defensive check** — 1-line sentinel (P1)
5. **qa / in-tick backup sentinel** — disk_cleanup_plugin defense (P1)

## 3 skill drafts (cap=3)

1. **secret-leak-pre-check** — terminal 调用前 env 自检 (covers GH #53715)
2. **hermes-tool-loader-sanity** — tool loader silent collapse sentinel (covers GH #53667)
3. **cron-output-backup-sentinel** — in-tick backup before any cron output write (covers GH #49271)

## 4 MCP memory proposals (pending_review, role=agent)

| # | memory_id | type | confidence |
|---|---|---|---|
| 1 | 0133bb27-c474-4a71-a955-3c718948b8cc | bug_impact_matrix (GH #53715) | 1.0 |
| 2 | 3b32b920-1c65-4da7-a5c6-34defd6a6b16 | bug_impact_matrix (GH #53667) | 0.9 |
| 3 | 1381567b-fc94-4a42-87dd-9508d0f106e9 | release_summary (v0.17.0 status) | 1.0 |
| 4 | f5671010-e34d-4f28-a6e4-11827a163248 | platform_api (OpenRouter 91/339) | 1.0 |

researcher role=agent cannot commit per skill rules — await chief/user batch commit.

## User review (回 ✅/❌/✏️/🔇)

**Top 3 suggestions**:
1. GH #53715 PR open + mergeable — 是否在 merge 前手动把 dev/qa SOUL 加 pre-check 段?
2. GH #53667 v0.17.0 fresh install — 是否回滚到 v0.16.1, 等 v0.17.1?
3. 5 SOUL 草稿已铺到 5 profile — 哪些你立刻采纳?

Review path: https://github.com/963072676/hermes-researcher-backup/tree/main/soul-proposals/2026-06-28

## Next steps (tick20)

- Monitor PR #53715 merge (search Hermes main nightly)
- arxiv export endpoint retry with simpler query
- Track user ack rate on tick19 SOUL drafts (24h window)
- 若连续 3 天 0 ack → 触发降频到隔日 (skill spec §失败回退)
