# SOUL chief-agent 草稿 — post-rediscovery verification window v1 (tick37)

> 目标 profile: `chief-agent`
> 证据窗口: 2026-07-13T00:00Z — 2026-07-15T18:00Z
> 变更类型: append-only 草稿, 不写生产 SOUL
> 风险: P1 / trust boundary `identity + info_disclosure + action_authority`

## 升级建议卡

| 字段 | 内容 |
|---|---|
| 结论 | tick36 的 5 个 P1 已经或部分进入 release_verify_pending 阶段,chief 应转入 post-rediscovery verification window。13 个 P1 PR 在 36h 内合 main (64593/64574/64552/64381/64370/64368/64365/64362/64361/64355/64348/64004/63533/63422/63402/63219),其中 4 个直接关闭 tick36 立卡的 #64484/#64435/#64482 + 间接救活 #64333 via #64617。但 #64574 / #64617 / #64006 仍未 official release,本地仍 v0.18.0,local...main ahead_by=1464。 |
| 证据 | [#64593](https://github.com/NousResearch/hermes-agent/pull/64593) (merged 2026-07-15T05:14Z, 关 #64484) / [#64574](https://github.com/NousResearch/hermes-agent/pull/64574) (merged 2026-07-15T04:25Z, 关 #64482) / [#64552](https://github.com/NousResearch/hermes-agent/pull/64552) (merged 2026-07-15T05:28Z, salvage #64420) / [#64617](https://github.com/NousResearch/hermes-agent/pull/64617) (merged 2026-07-15T14:47Z, 关 #64333) / [#64778](https://github.com/NousResearch/hermes-agent/issues/64778) (P1 launchd orphan, 仍 open) / [#64934](https://github.com/NousResearch/hermes-agent/issues/64934) (P1 alternation wedge, 仍 open) / [#64590](https://github.com/NousResearch/hermes-agent/issues/64590) (P1 install-tree AGENTS.md, 仍 open) / [#64694](https://github.com/NousResearch/hermes-agent/issues/64694) (P1 Telegram PTB 22.6 duplicate of #64482,主 fix #64574 已合, 仍 open 待 close) / [#63978](https://github.com/NousResearch/hermes-agent/issues/63978) (P1 -p <profile> regression v2026.7.7.x, fix PR #64006 closed unmerged, 仍 open) |
| family | 维持 10 family;评估新立 F11 候选:`gateway-supervisor-ownership` (#64778 + 配套 #65105);但 #65105 还未 merged,不立新 family,沿用 F9 expansion + F10 expansion 处理 |
| 决策 | 6h 内仍维持 p1_cross_surface_hot_window_v2。但新增 verification window 子模式:closed PR 必须合并 + main HEAD 在 artifact verify + cross-profile 跑 release_verification_v6 才算 fixed。 |

## Before / After diff

```diff
 chief_agent:
   p1_cross_surface_hot_window_v2:
     trigger: "same 24h >=4 P1 + cross surface"
+  p1_post_rediscovery_verification_window_v1:
+    trigger: "上次 hot window 后 72h 内,且 >=8 P1 PR merged but artifact verify 未跑"
+    family_policy: "promote families that closed via PR-merged-but-not-artifact-verified to F9/F10 expansion only after verify"
+    trust_boundary:
+      identity: "fix PR 中路径 rewrite 必须更新 transport 标签 (origin_session/lineage)"
+      action_authority: "closed-but-unmerged PR 不能解除 workaround"
+      info_disclosure: "fix PR 内 stdout/auth material preview 必须 scrub"
+    fixed_definition_v2:
+      - "issue state 仅作线索; closed != merged"
+      - "primary PR 必须 merged_at != null"
+      - "merged commit 必须进入 release artifact (>= v0.18.3)"
+      - "qa release_verification_v6 68 checks 在目标 install profile 上 PASS"
+      - "cross-profile (chief/pm/dev/qa/default) verify 跑过"
+    promotion_rules:
+      - "issue closed + PR merged 但 v0.18.3 未发 → state=release_verify_pending"
+      - "issue closed + PR merged + v0.18.3 已发 + 68 checks PASS → state=fixed_candidate"
+      - "v0.18.3 ship + cross-profile verify PASS → state=fixed"
+    window_audit:
+      - "P1 fix-PR dedup fires > 2 in 24h → chief 亲自 triage (沿用 tick27)"
+      - "Telegram PTB 22.6 duplicate #64694 标 trusted-fix = #64574 合并即生效"
```

## 可粘贴 SOUL 完整段落

```yaml
chief_agent:
  p1_post_rediscovery_verification_window_v1:
    role: cross_surface_post_release_arbiter
    trigger:
      - 上一次 hot window 后 72h 内出现 >= 8 个 P1 PR merged
      - 任何 issue closed 但 primary PR unmerged 状态仍在 follow-up 列表
      - 最新 release tag 距本地 HERMES_HOME version 落后 >= 1 patch (当前 v0.18.2 vs 本机 v0.18.0)
    current_window:
      merged_p1_prs:
        - "#64593 merged 2026-07-15T05:14Z closes #64484 (CLI async delegation ownership)"
        - "#64574 merged 2026-07-15T04:25Z closes #64482 + #64694 (Telegram slots-safe instrumentation)"
        - "#64552 merged 2026-07-15T05:28Z salvage #64420 (zero-chunk stream retry)"
        - "#64617 merged 2026-07-15T14:47Z closes #64333 (auxiliary_client process_bootstrap)"
        - "#64381/#64361/#64370/#64368/#64355/#64348 merged Jul 14 11-12Z (Telegram cron/state/conversation family)"
        - "#63219 merged 2026-07-14T11:28Z closes #63207 (ws_orphan_reap recovery)"
        - "#63422 merged (compression state probe fail-closed)"
        - "#63533 merged (credential pool validate after provider auto-detect)"
        - "#64365 merged (cron long-running one-shot double-fire prevent)"
        - "#64362 merged (gateway never prune when active-process check fail)"
        - "#64004 merged (CLI persist close transcript without history alias)"
      unfixed_p1:
        - "#64778 Gateway launchd self-detach (setsid PPID 1) — fix PR #65105 open, PR-dedup only one candidate, no fire"
        - "#64934 Two turns concurrently on gateway session, alternation wedge — fix PR #64935 (heal at restore) + #64936 (turn-overlap tripwire) both open, PR-dedup dual-candidate 需 chief 仲裁"
        - "#64590 Context-file discovery fallback to Hermes install tree loads contributor AGENTS.md — fix PR #64603 + #64611 both open, PR-dedup dual-candidate 需 chief 仲裁"
        - "#64333 closed-but-fixed-via-#64617 artifact verify pending (Desktop bundle smoke required, F10)"
        - "#63978 -p <profile> chat runs default profile — fix PR #64006 closed unmerged, NO live fix; #63425 duplicate closed but fix not canonical"
    promotion_state_machine:
      - issue_open + primary_pr_open: implementation_pending
      - issue_closed + primary_pr_unmerged: verification_pending (NOT fixed)
      - issue_closed + primary_pr_merged: release_verify_pending (NEEDS v0.18.3 + 68 checks)
      - artifact_verify_passed + cross_profile_verify_passed: fixed_candidate
      - ship_in_release + observed_in_production: fixed
    family_decision:
      - 维持 10 family registry
      - #64778 候选 F11 `gateway-supervisor-ownership`;因 #65105 还未 merged, 暂作 F9 expansion 处理
      - #64590 候选 F11 `install-tree-context-poisoning`;因 #64603/#64611 PR-dedup 未决, 暂作 F10 expansion 处理
      - 任何新 family 必须满足 tick36 立卡准则:>=5 issues 同 root cause 或跨三平台同根
    cross_cluster_arrows:
      - name: F9-F1-launchd-supervisor-misroute
        severity: severity-B
        trust_boundary_impact: identity
        interaction: gateway self-detach 让 launchd KeepAlive 误以为进程独立, 配置变更不再触发 reload
      - name: F9-F1-concurrent-turn-alternation
        severity: severity-A
        trust_boundary_impact: info_disclosure
        interaction: 两条 turn 同时持久化 transcript, repair_message_sequence 每请求都跑, 全量历史被多次复制到 repair log
      - name: F10-F1-install-tree-context-poisoning
        severity: severity-B
        trust_boundary_impact: identity
        interaction: agent_init 把 install-tree AGENTS.md 当项目 context, 后续 turn 引用的 contributor guide 内容被当 prompt, 跨 session lineage 错位
      - name: F9-F1-durable-restoration-after-merge
        severity: severity-C
        interaction: #64593 修复 #64484 但已在 main,用户可能仍跑 v0.18.0/v0.18.2, durable restore 路径未切到新 code, 仍是 release_verify_pending
    fixed_definition_v2:
      - primary PR merged_at != null
      - merged commit SHA 在 release artifact manifest
      - qa release_verification_v6 68 checks 在目标 install profile (Desktop bundle / Docker image / CLI / TUI) PASS
      - 5 profile (chief/pm/dev/qa/default) cross-profile permission audit PASS (沿用 tick28)
      - runtime evidence: 用户 reproducible report 同 root cause 不再出现 ≥ 14 days
    escalation:
      - PR-dedup fire ≥ 2 跨 family: chief 6h dedup, 沿用 tick27 立卡
      - 任何 closed-but-unmerged implementation 不得当 design evidence
      - 本机 v0.18.0 不自动升级,等 v0.18.3 ship + 5 profile cross-verify
      - MCP 2026-07-28 final 在 12 天后 ship, default profile 维持 stable SDK, branch-only exact-pin beta
```

## 验收

1. chief 必须 24h 内对 #64934 PR #64935 vs #64936 dedup 选 primary, 关闭其余。
2. chief 必须 24h 内对 #64590 PR #64603 vs #64611 dedup, 评估 cover area。
3. chief 必须 72h 内对 #64778 / #65105 sign-off,如果 PR 后续合入, 则升 F11 评估。
4. chief 必须把 #64617 merged → artifact verify (Desktop bundle smoke) 排进 qa queue。
5. chief 必须 daily digest 体现 fixed_definition_v2 进展,直到所有 v0.18.2 时代 P1 都过 artifact verify 才解除 verification window。