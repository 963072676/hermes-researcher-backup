# SOUL Draft — chief-agent (2026-07-24, tick45)

> Target: `chief-agent` SOUL `family_arbiter_v4`，仅草稿，不写生产 profile。
> Streak: 21 days zero-adoption。
> Release: v0.19.0 ship 后约 71.4h，仍在 72h 强观察窗内。

## 升级建议卡

【优先级】P0/P1

【新证据】
- GH #70216：Bedrock Converse 未设置 prompt cache breakpoint，被标 P0；这是成本灾难，不是凭据边界事件。
- GH #70218 + PR #62811：MCP keepalive probe 绕过 per-server RPC lock，可与长时 tool call 交错；PR 仍 open、mergeable。
- GH #70211 / #70201：更新器在 dirty editable tree 上可能破坏 workspace；POSIX 可热改正在运行的 venv，造成 mixed runtime。
- GH #70206 / #70185 / #70221 / #68358：Desktop session-state 同日多症状复发，覆盖 render key、archive cascade、navigation、失败重投错 session。
- arXiv 2607.05744：8/8 metadata techniques 到达模型上下文；TAG-block 是唯一同时绕过 sanitizer 与人工审批视图的技术；TOCTOU 变更 0/8 触发重新审批。

【family 归类】
- F7 MCP-supply-chain-protocol-migration：新增 approval-view byte fidelity / tool-metadata digest re-consent 缺口。
- F9 session-state-integrity-deck：4 条 Desktop/session 证据强化为 expansion，不新建同义 family。
- F10 cron-installer-handoff-state：dirty-tree update + POSIX mixed-runtime 进入 catastrophic update-coherence 子链。
- F11 execute-code-approval-unification：审批视图与模型实际接收 bytes 不一致，触发 invariant 10 candidate。
- F12 保持 candidate：论文证据很强，但 `>=5 GH issues 同 root cause` 的 condition_1 未验证，不升 family。

## 建议追加段落

```yaml
chief:
  family_arbiter_v4:
    tick45:
      release_window:
        tag: v2026.7.20
        hours_since_ship: 71.4
        rule_1_hit: true
      tier_1_5_active:
        - F10_update_coherence_dirty_tree_and_live_venv
        - F7_F11_approval_view_byte_fidelity
      family_updates:
        F7:
          invariant_candidate: approval_view_byte_fidelity
          evidence: [arxiv_2607_05744, GH_70218, PR_62811]
        F9:
          lifecycle: expansion
          evidence: [GH_70206, GH_70185, GH_70221, GH_68358]
        F10:
          lifecycle: expansion
          evidence: [GH_70211, GH_70201, PR_68805]
        F11:
          invariant_10_candidate: approval_bytes_equal_model_bytes
        F12:
          lifecycle: candidate
          condition_1_met: false
          anti_inflation_binding: true
      cross_cluster_arrows_new:
        - CCA-F7-F11-approval-view-byte-mismatch
        - CCA-F7-F9-keepalive-rpc-session-corruption
        - CCA-F10-F9-live-update-session-corruption
        - CCA-F9-F1-desktop-failure-retry-misdelivery
      chief_24h_decisions:
        - choose_primary_PR_62811_for_keepalive_lock
        - require_dirty_tree_update_fail_closed
        - require_live_venv_holder_guard_all_platforms
        - require_metadata_digest_change_reconsent
```

## 验收

1. F12 不因单篇论文提前转正。
2. `closed` 或 `open PR` 均不得写成 fixed；#62811/#68805 当前只算 implementation_pending。
3. approval UI 必须展示模型实际接收的规范化 bytes 哈希；digest 变化必须重新授权。
4. F10/F9 联动进入 chief tier-1.5，不派成单一 Desktop cosmetic bug。
