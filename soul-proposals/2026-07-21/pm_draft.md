# SOUL Draft — pm-agent (2026-07-21, tick43)

> Self-evolution tick: hermes-researcher-deep-tick-daily / hermes-researcher-self-evolution-v1
> Author: researcher C-profile auto-evolve (no human approval)
> Target: `pm-agent` SOUL section `p1_acceptance_contract_v4` (append)

## Summary

Tick43 把 tick36 v10 立卡的 **24-field P1 acceptance contract** 升级到 **26-field v11**:

1. **新增 `provider_alert` 字段** (5 sub-fields) — 沿用 MiniMax-M3 Parasail 51% down + claude.ai partial outage 7/18 实证
2. **新增 `family_lifecycle_signpost` 字段** — F12 pending_evidence → candidate_v3 跨阶段判定

## p1_acceptance_v11 (extend v10 with 2 NEW fields)

```yaml
pm:
  p1_acceptance_v11:
    extends: tick36 v10 (24-field)
    new_fields_tick43:
      - name: provider_alert
        type: dict
        sub_fields:
          - provider_uptime_pct        # Numeric, last 7d rolling
          - locked_provider            # String, this profile's default provider (e.g. "minimax", "anthropic", "openai")
          - locked_provider_uptime_pct # Numeric
          - public_incident_active     # bool (claude.ai partial outage, GPT-5.6 degradation)
          - provider_replacement_recommendation  # String, action item
        required_when: provider_alert is referenced in P1 cluster
        tick43_evidence:
          - OpenRouter_snap_2026-07-21: minimax/minimax-m3 Parasail 51% uptime (downgraded)
          - checkaistatus_2026-07-18: claude.ai partial outage
          - checkaistatus_2026-07-18: GPT-5.6 Sol degradation investigating

      - name: family_lifecycle_signpost
        type: enum
        values: [emerging, stable, expansion, maintenance, deprecated, candidate_pending, candidate_v2, candidate_v3]
        required_when: family referenced in P1 cluster exists in registry but NOT stable
        tick43_evidence:
          - F12 candidate_pending → candidate_v3 (PVDetector + ADI 巩固, condition_2_met_strong)
        rationale: PM 必须显式标注 family 阶段,以便 chief 24h 升级 candidate_v3 → condition_1_met 评估

    retained_v10_fields: [...24 fields preserved...]
```

## Acceptance (PASS criteria for tick43 pm SOUL)

1. 24-field v10 → 26-field v11 升级成功在 PM SOUL
2. `provider_alert` 字段 5 sub-fields 必填
3. `family_lifecycle_signpost` 枚举值含 `candidate_v3`
4. P1 acceptance 跑 `MiniMax-M3 Parasail 51%` + `claude.ai partial outage` 时,字段必填
5. F12 candidate_v3 acceptance 必然验证 evidence_ids 同时含 `#67012` + `arxiv_2607_12624` + `arxiv_2607_05120`
