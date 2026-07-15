# tick37 deliverables (2026-07-16)

> hermes-researcher-self-evolution-v1 / tick37 anchor for tick38+ worker.

## 产出快照

- 5 SOUL drafts: chief / pm / dev / qa / default
- 3 skill drafts:
  - `hermes-post-merge-regression-window-guard-v1`
  - `hermes-mcp-2026-07-28-final-readiness-v1`
  - `hermes-launchd-supervisor-ownership-preserver-v1`
- impact graph: 4 cross-cluster arrows (1 severity-A + 2 severity-B + 1 severity-C)
- audit: zero-adoption streak=13, v4 rules 2+3+4+5 四 rule 同命中
- family registry: 维持 10, 不立 F11

## tick37 P1 signals

### Merged 4 (release_verify_pending)

| Signal | Merged | Family | Regression window until |
|---|---|---|---|
| #64593 closes #64484 (async ownership) | 2026-07-15T05:14Z | F9 | 2026-07-29T05:14Z |
| #64574 closes #64482+#64694 (Telegram PTB) | 2026-07-15T04:25Z | F1+F10 | 2026-07-29T04:25Z |
| #64552 salvage #64420+#64435 (zero-chunk) | 2026-07-15T05:28Z | F1+F8 | 2026-07-29T05:28Z |
| #64617 closes #64333 (auxiliary_client) | 2026-07-15T14:47Z | F10 | 2026-07-29T14:47Z |

### Open 4 (implementation_pending)

| Signal | State | Family | Fix candidate | Dedup |
|---|---|---|---|---|
| #64934 alternation wedge | open | F9 | #64935 + #64936 | dual, chief 6h |
| #64778 launchd orphan | open | F9 (F11 cand) | #65105 | single |
| #64590 install-tree AGENTS.md | open | F10 (F11 cand) | #64603 + #64611 | dual, chief 6h |
| #63978 -p <profile> regression | open | F9 | NO live fix (#64006 closed unmerged) | reopen required |

## 4 cross-cluster arrows

1. `F9-F1-concurrent-turn-alternation` — severity-A (chief 6h triage)
2. `F9-F1-launchd-supervisor-misroute` — severity-B (chief 24h joint review)
3. `F10-F1-install-tree-context-poisoning` — severity-B (chief 24h joint review)
4. `F9-F1-durable-restoration-after-merge` — severity-C (daily report)

## Contract upgrades

- P1 acceptance: 15-field v4 → **17-field v5**
- 新字段:
  1. `candidate_pr_dedup_state` (5 sub-fields: total / primary_selected / closed_unmerged / dedup_decision_made_by / dedup_window_hours)
  2. `artifact_verify_required_for_release` (6 sub-fields: release_target / install_profiles_affected / manifest_required / import_smoke_target_paths / runtime_smoke_target_surfaces / cross_profile_audit_required)
- ship gate: 68 → **72** (+4 post-merge regression window checks)
- 4-state machine extension: closed_only / closed_unmerged_candidates / closed_merged_no_artifact / closed_merged_artifact_verified / closed_merged_artifact_verified_cross_profile

## 5 install profile verify (v0.18.3 readiness)

| Profile | Required smoke |
|---|---|
| Desktop | macOS app.asar + Hermes.app + TCC/FDA gate; Windows installer + registry; Linux AppImage + dpkg + rpm |
| Docker | official hub + ghcr.io; non-local terminal backend confine; media cache scope |
| CLI | macOS Terminal + zsh; Windows Terminal + PowerShell; Linux gnome-terminal + bash |
| TUI | desktop window + WebSocket upgrade; portable mode |
| MCP_stdio | local stdio + Redis-backed session; keepalive empty exception bounded retry |

## MCP 2026-07-28 readiness (12 天倒计时)

6 SEPs 影响 default profile:
- SEP-2575 (initialize handshake removed)
- SEP-2567 (Mcp-Session-Id removed)
- SEP-2243 (Mcp-Method + Mcp-Name headers mandatory)
- SEP-2260 + SEP-2322 (long-lived SSE removed, multi-round-trip)
- SEP-2164 (-32002 → -32602 error code)
- 6 auth SEPs (iss validation + application_type + issuer binding)

本 default profile 保持 stable SDK, branch-only exact-pin beta SDK 仅 dev profile。

## 5 profile SOUL 升级摘要

- **chief**: post-rediscovery verification window v1 (4-state machine)
- **pm**: acceptance v5 17-field (candidate_pr_dedup_state + artifact_verify_required_for_release)
- **dev**: post-merge invariant verification v1 (4 merged PR 14d window + 4 open P1 implementation plans)
- **qa**: release verification v7 72-check (4 post-merge regression window checks)
- **default**: post-rediscovery safe defaults v1 (profile switching HERMES_HOME 显式 + Telegram disable + zero-chunk 显式 timeout)

## tick38+ 启动必跑

1. 读取本文件 + tick36 deliverables + tick35 deliverables.
2. 检查 4 merged P1 PR (#64593 / #64574 / #64552 / #64617) 的 14d regression window 状态.
3. 检查 4 open P1 的 PR-dedup 进展 (chief 6h / 24h SLA).
4. 检查 MCP 2026-07-28 final 倒计时 (12d → tick38 11d).
5. 检查 v0.18.3 是否 ship (含 4 P1 PR commit SHA).
6. 沿用 17-field v5 + 72-check ship gate v7.
7. v4 self-downgrade rule 1-8 逐条记录 (current 4 rules hit).
8. MCP context 固定 `org=gc-hermes / project=gc-hermes-config / agent=gc-hermes-researcher`; 只 propose.
9. 任何 closed_unmerged PR 不得计入 fixed; artifact verify 必跑.
10. regression_window_until 14d 后才能升级 fix_candidate → fixed.

## 状态校正 (沿用 tick36)

- closed != merged; 必须等 artifact verify.
- primary PR merged but artifact verify not done → release_verify_pending (NOT fixed).
- 本机 v0.18.0 不自动升级 (沿用 #60685 redline).
- MCP beta 仅 branch + exact pin (沿用 tick28).
- Telegram adapter 本机维持 disable (因 #64574 merged but not in v0.18.0).