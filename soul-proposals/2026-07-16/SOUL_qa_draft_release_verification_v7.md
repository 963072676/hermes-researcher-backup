# SOUL qa-worker 草稿 — release verification v7 (post-rediscovery window) (tick37)

> 目标 profile: `qa-worker`
> 来源: tick37 post-rediscovery verification window
> 变更类型: append-only 草稿
> 风险: P1 / trust boundary `identity + info_disclosure + action_authority`

## 升级建议卡

| 字段 | 内容 |
|---|---|
| 结论 | tick36 的 68-point ship gate v6 在 #64593 / #64574 / #64552 / #64617 merged 后要求新增 4 项 post-merge verify checks (regression window tracking + artifact smoke + cross-cluster arrow propagation + MCP 2026-07-28 readiness)。总门数 68 + 4 = 72。 |
| 证据 | #64593 (PR merged #64484) / #64574 (PR merged #64482+#64694) / #64552 (PR merged #64420+#64435 via streaming) / #64617 (PR merged #64333) |
| 关键约束 | v0.18.3 ship 前所有 P1 必过 72 checks; install profile 5 个 (Desktop/Docker/CLI/TUI/MCP stdio) 各跑全量 |

## Before / After diff

```diff
 qa:
   release_verification_v6:
     total: 68
+  release_verification_v7:
+    total: 72
+    new_groups:
+      post_merge_regression_window_tracking: 4
+    kept_groups:
+      grep_checklist: 5
+      cross_profile_permissions: 20
+      mcp_supply_chain: 6
+      p1_acceptance_contract_v5: 17
+      cross_cluster_arrows: 4
+      trust_boundary_e2e: 4
+      runtime_smoke_per_family: 12
```

## 可粘贴 SOUL 完整段落

```yaml
qa:
  release_verification_v7:
    extends: release_verification_v6
    baseline_groups:
      grep_checklist: 5
      cross_profile_permissions: 20
      mcp_supply_chain: 6
      p1_acceptance_contract_v5: 17
      cross_cluster_arrows: 4
      trust_boundary_e2e: 4
      runtime_smoke_per_family: 12
    note: "v6 的 68 checks 全部保留 + 4 项 post-merge verify checks → total 72"
    new_post_merge_groups:
      post_merge_regression_window_tracking: 4
    total_checks: 72

    post_merge_regression_window_checks:
      - each_merged_p1_pr_has_artifact_manifest
      - each_merged_p1_pr_has_cross_profile_smoke
      - each_merged_p1_pr_observed_in_production_14_days
      - each_closed_unmerged_pr_not_counted_as_fix

    runtime_smoke_per_family_checks:
      F1_silent_fail:
        - Telegram getUpdates connect on PTB 21.x / 22.x / 22.6
        - zero-chunk stream retry bound (max 3 attempts)
        - normal stream no retry overhead
        - Anthropic zero-event parity
      F8_cron_ticker:
        - terminal capture bounded at configured max_bytes
        - head/tail preserved + omitted byte count
        - continuous producer timeout under wall clock
        - gateway RSS not coupled to output size
      F9_session_state:
        - foreign async completion cannot be consumed by new CLI
        - concurrent turn detection blocks alternation wedge
        - supervisor ownership preserved under launchd/systemd
        - compression lineage owner consumes exactly once
      F10_installer_handoff:
        - Desktop bundle smoke on macOS/Windows/Linux
        - install-tree AGENTS.md never loaded as project context
        - HERMES_HOME per profile strict
        - auxiliary_client process_bootstrap survives version-skewed

    p1_acceptance_contract_v5_updates:
      - 17 字段全必填
      - candidate_pr_dedup_state 必填, closed_unmerged_count 必须 ≤ total - 1
      - artifact_verify_required_for_release 必填, install_profiles_affected 不得为空
      - cross_profile_audit_required=true 时 v0.18.3 ship 必须 5 profile 全过

    hard_fail_rules:
      - any trust boundary e2e fail => reject ship
      - any closed_unmerged counted as fix => reject ship
      - any missing artifact_verify for merged P1 PR => reject ship
      - any regression observed in 14-day window => reject ship
      - cross-cluster arrow verification fails => chief triage before ship
      - skip-trust-boundary-e2e flag forbidden
      - skip-post-merge-regression-window flag forbidden

    per_install_profile_run:
      Desktop:
        - macOS: app.asar + Hermes.app + macOS TCC/FDA gate
        - Windows: app.asar + installer + registry entries
        - Linux: AppImage + dpkg + rpm
      Docker:
        - official hub + ghcr.io
        - non-local terminal backend confine
        - media cache scope
      CLI:
        - macOS Terminal + zsh
        - Windows Terminal + PowerShell
        - Linux gnome-terminal + bash
      TUI:
        - desktop window + WebSocket upgrade
        - portable mode
      MCP_stdio:
        - local stdio + Redis-backed session
        - keepalive empty exception bounded retry

    result_semantics_v7:
      - issue closed + primary PR unmerged => verification_pending
      - primary PR merged but artifact_verify not done => release_verify_pending
      - artifact_verify PASS + cross_profile_audit PASS + 14-day window no regression => ship_candidate
      - 14-day window regression observed => reopen issue + new PR + restart window

    v6_to_v7_migration_notes:
      - v6 68 checks 全部保留
      - v7 在 v6 末尾 append 4 checks, 不替换
      - 任何 v6 tick 报告升级到 v7 时只需补 4 checks
      - tick37 之前所有 68-point 报告升级路径: 重新跑 v6 + 加 4 项 post-merge

    current_tick37_status:
      merged_p1_prs_to_verify:
        - 64593: F9 + CLI async delegation
        - 64574: F1 + F10 + Telegram PTB 22.6
        - 64552: F1 + F8 + zero-chunk stream retry
        - 64617: F10 + auxiliary_client process_bootstrap
      open_p1_to_track_for_v0_18_3:
        - 64934: F9 + alternation wedge
        - 64778: F9 + launchd orphan
        - 64590: F10 + install-tree AGENTS.md
        - 64333 (closed-via-#64617): artifact_verify_pending
        - 63978: F9 + -p <profile> regression
      closed_unmerged_prs_not_counted:
        - 64006 (-p <profile> regression fix)
        - 64524 (terminal bounded)
        - 64448 (BoundedOutputCollector)
        - 64506 (Telegram subclass re-tag rejected)
        - 64359 (auxiliary_client backward compat)
        - 64420 (zero-chunk stream first attempt)
```

## 数量校正

tick36 audit 的总数算法:5 grep + 20 cross-profile + 6 MCP supply chain + 17 P1 acceptance v5 (升级自 v4 15) + 4 cross-cluster arrows + 4 trust boundary e2e + 12 runtime smoke per family = 68。tick37 v7 在 v6 68 之上加 4 post-merge regression window checks = **72**。

```text
5 + 20 + 6 + 17 + 4 + 4 + 12 + 4 = 72
```

本草稿最终 gate 是 **72-point**, 不是 v6 的 68。

## 实际 release 验收关注 (tick37)

- #64593 merged → v0.18.3 必须含 commit 53c3709c, artifact_verify 必跑。
- #64574 merged → v0.18.3 必须含 commit bd8d9d3e, Telegram connect smoke 必跑。
- #64552 merged → v0.18.3 必须含 commit cc9bf710, zero-chunk stream 必跑。
- #64617 merged → v0.18.3 必须含 commit f3ec7996, Desktop bundle smoke 必跑。
- #63219 merged (tick36 close #63207) → ws_orphan_reap verify 必跑 (F9).
- #63422 merged → compression state probe fail-closed (F9).
- #63533 merged → credential pool validate after provider auto-detect (F4 expansion awareness).
- #64365 merged → cron long-running one-shot double-fire prevent (F8).
- #64362 merged → gateway never prune when active-process check fail (F9).
- #64381 / #64370 / #64368 / #64361 / #64355 / #64348 → Telegram + state + conversation_loop cluster, v6 verify 已覆盖。
- #64004 merged → CLI persist close transcript without history alias (F9).
- #63402 merged → cron keep live one-shots when running-set check fails (F8).
- latest release 仍 v0.18.2 (2026-07-08T03:11:22Z); 本地 v0.18.0; main 1464 commits ahead。

## v0.18.3 readiness checklist

- [ ] v0.18.3 release branch cut from main @ 53c3709c
- [ ] 4 merged P1 PRs commit SHAs 在 release artifact manifest
- [ ] 5 install profile 全跑通 72 checks
- [ ] #64934 / #64778 / #64590 / #63978 4 open P1 全部有 primary PR open or merged
- [ ] cross-cluster arrows 验证 PASS (chief triage 6h 内)
- [ ] MCP 2026-07-28 final spec compatibility matrix PASS (沿用 tick35)
- [ ] cross-profile permission audit (tick28 v6) PASS
- [ ] 14-day post-merge regression window PASS for all 4 merged P1
- [ ] no closed_unmerged PR counted as fix
- [ ] ship 后 48h 内用户 reproducible report 同 root cause 不再出现 ≥ 14 days