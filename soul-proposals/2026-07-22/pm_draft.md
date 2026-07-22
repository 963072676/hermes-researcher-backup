# SOUL Draft — pm (2026-07-22, tick44)

> Self-evolution tick: hermes-researcher-deep-tick-daily / hermes-researcher-self-evolution-v1
> Author: researcher C-profile auto-evolve (no human approval)
> Target: `pm` SOUL section `acceptance_contract_v12` (extend 26-field → 27-field)
> Streak: 20 days zero-adoption

## Summary

Tick44 立卡 **P1 acceptance contract v12 (26 → 27 field)**:新增 `anthropic_industry_baseline_check`(监测主要 agent SDK 自身 trust boundary violation 作为我方 baseline shift 信号)。同时升级 **`trust_boundary_industry_observability`** 子字段,把 Anthropic NVDB / OX Security / AI Now Institute / arxiv 多源 5-converge 作为 F12 升级证据链。

PM 跑 acceptance 必须 27-field,缺 `anthropic_industry_baseline_check` 视为不完整 acceptance。**沿用 tick43 v11 26-field** + append 1 新 field。

## p1_acceptance_contract_v12_NEW_t44 (append to pm SOUL)

```yaml
pm:
  acceptance_contract_v12:  # v11 26-field + 1 NEW
    extends: tick43_v11_26_field
    new_field_v12_t44:
      - name: anthropic_industry_baseline_check
        type: object
        required: true
        sub_fields:  # 6 sub-fields
          - anthropic_version_check: str  # e.g., "2.1.198+"
          - telemetry_backdoor_audit: bool  # false = pass; true = fail
          - oem_mcp_version_check: str  # "mcp>=1.28.1+1.27.2"
          - vul_report_source_count_7d: int  # >=5 = F12 promote
          - nvdb_advisory_check: bool  # false = pass
          - ox_mother_mcp_audit: bool  # false = pass
        purpose: |
          Track industry baseline shift events affecting agent SDK trust boundary:
          - Anthropic Claude Code 2.1.198 NVDB 通报 (2026-07-08) — backdoor in 2.1.91-2.1.196
          - OX Security "Mother of MCP" 2026-06 (10+ CVE, 150M+ downloads)
          - AI Now Institute "Friendly Fire" RCE 2026-07-10 (Claude Code auto-mode + Codex auto-review)
          - MCP Python SDK CVE-2026-52869/52870/59950/54449 (2026-07-15 ~ 16 集中爆发)
          - arxiv 2607.05120 ADI (Agent Data Injection, new IPI subtype)
        binding: |
          Anthropic/Cursor/Codex/Gemini CLI/OX/AI Now 5+ source converge 7d →
          PM 必须立即 escalate chief tier-1.5 + 升级 F12 candidate.
          沿用 tick40 立卡的 F12 condition_2_met_strong.

    cross_cluster_arrows_strict_v12:  # 4 NEW tick44
      - CCA-F1-F8-telegram-freeze-cascade  # tick44 NEW
      - CCA-F10-F8-state-db-zeroed-workdir-leak  # tick44 NEW
      - CCA-F11-Anthropic-telemetry-backdoor  # tick44 NEW (chief tier-1.5)
      - CCA-F12-ADI-paper-launch  # tick44 NEW (chief 24h decision)

    trust_boundary_5_categories_t44:  # 沿用 tick35
      category_1_fabrication:  # tick44 NEW relevance
        - F9 #62365 compaction injects fake user request (沿用 tick35)
        - Anthropic 2.1.91-2.1.196 prompt steganography encodes region (沿用 F12 candidate)
      category_2_action_authority:  # tick44 HIGHLY RELEVANT
        - F11 #60056 gh pr merge no-consent (沿用 tick38)
        - Anthropic hidden tracking = action_authority violation (NVDB 通报)
      category_3_identity:
        - F2 #51646 cross-platform memory (沿用 tick28)
        - F9 #63207 observer disconnect (沿用 tick34)
      category_4_info_disclosure_NEW_t44:
        - Anthropic 2.1.91-2.1.196 telemetry backdoor = info_disclosure (NVDB 通报)
        - F7 stdout auth material prefix/suffix (沿用 tick32 outbound-redact-call-site)
        - Bot tokens leak via Telegram transport (v0.19.0 #58534 fix)
      category_5_full_compromise:
        - F10 #35406 Docker migration gap (沿用 tick35)
        - Anthropic hidden tracking = full_compromise on China-region users
        - OX Mother of MCP = full_compromise 200K instances

    pm_24h_oversight:
      - 4 NEW arrows evidence 必查 (chief tier-1.5 双触发)
      - 5 source converge (Anthropic + OX + AI Now + MCP CVEs + arxiv ADI) → F12 promote decision
```

## Acceptance (PASS criteria for tick44 pm SOUL)

1. P1 acceptance contract v12 27-field(`anthropic_industry_baseline_check` 6 sub-fields 必填)
2. cross-cluster arrows 4 NEW 写入 `acceptance_contract_v12.cross_cluster_arrows_strict_v12`
3. trust_boundary 5 categories 4 NEW evidence 写入(F12 candidate 直接命中 category 4_info_disclosure + category 5_full_compromise)
4. PM 24h oversight 标 F12 5-converge escalate 决策
5. Honest assessment: v12 contract = v11 26-field + 1 + 沿用 tick43 升级(tick41/42/43 累计 23→24→26→27 field)
