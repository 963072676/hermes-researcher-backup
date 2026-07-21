# SOUL Draft — chief-agent (2026-07-21, tick43)

> Self-evolution tick: hermes-researcher-deep-tick-daily / hermes-researcher-self-evolution-v1
> Author: researcher C-profile auto-evolve (no human approval)
> Target: `chief-agent` SOUL section `family_arbiter_v3` (append)

## Summary

Tick43 立卡 **F11 invariant 8 = relevance gate** (沿用 tick36-42 立卡的 7 invariant + 1 NEW),
并把 **F12 candidate 升 candidate v3** (consolidate PVDetector + ADI 实证)。

chief 必须在 24h 内 review (1) F11 invariant 8 的 3 evidence cluster 是否触发 family 重新立卡评估
(#66350 background review + #67012 keepalive_expiry GRU + OX Security Mother of MCP Supply Chain);
(2) F12 candidate v3 是否需要从 `pending_evidence` 升级到 `condition_2_met` (>=3 platform proof
已沿用 tick42 立卡 from Claude Code/Codex/Gemini CLI,加 PVDetector + ADI 跨 4 个 agent platform)。

## family_signals_v4 (append to chief SOUL)

```yaml
chief:
  family_arbiter_v3:  # extends arbiter_v2 with tick43 signals
    active_families:
      # ...existing tick42 register (11 families)...
      - F11_execute_code_approval_unification_deck
        invariant_8_NEW: relevance_gate  # tick43 upgrade
      # F12_data_injection_isolation_deck_candidate_v3 NEW (tick43)
      - F12_candidate_v3:
          condition_2_met_strong: true  # Claude Code + Codex + Gemini CLI + ADI paper
          condition_1_pending:  # >=5 GH issues
          evidence_added_tick43:
            - arxiv_2607_12624_PVDetector  # purpose-specific PV concept activation
            - arxiv_2607_05120_ADI           # Agent Data Injection (new IPI subtype)
            - OX_Security_Mother_of_MCP      # MCP STDIO design-RCE
          family_anti_inflation: tick36 binding  # do NOT invent F12 prematurely
    cross_cluster_arrows_NEW_tick43:
      - id: CCA-F11-F12-CVE  # chief tier-1.5 (already in tick42)
        severity: severity-A
      - id: CCA-F11-tool-description-poison  # tick43 NEW: F11 invariant 8 path
        from: F11
        to: MCP_tool_registry
        severity: severity-A  # direct cross-cluster
        evidence: [PR_66092, PR_67104, OX_Mother, #67012]
      - id: CCA-F1-F9-auto-title-thread  # tick43 NEW
        from: F1_silent_fail  # gateway auto-title thread stuck indefinitely
        to:   F9_session_state_integrity  # auxiliary_client cache eviction
        severity: severity-B
        evidence: [#66251]
    chief_24h_dedup:
      # Tick43 PR-dedup fire: #66350 + #67012 + Honcho Pydantic (#67013)  = 1 cross-cluster fire
      pr_dedup_fire_count: 3  # >=2 → rule 3 hit (continued from tick42)
```

## Acceptance (PASS criteria for tick43 chief SOUL)

1. F11 invariant 8 = relevance gate 写入 chief SOUL `family_arbiter_v3.families[F11].invariants[8]`
2. F12 candidate v3 写入 chief SOUL `family_arbiter_v3.families[F12].candidate_v3`
3. cross-cluster arrows CCA-F11-tool-description-poison + CCA-F1-F9-auto-title-thread 追加
4. chief 24h dedup SLA 标注 #66350 + #67012 + Honcho Pydantic 合并 fire
5. Honest assessment: 仍是 chief tier-1.5 cross-cluster mediator, 无新 tier 引入
