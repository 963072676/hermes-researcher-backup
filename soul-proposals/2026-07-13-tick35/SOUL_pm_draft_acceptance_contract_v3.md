# SOUL pm 草稿 — P1 acceptance contract v3 (tick35)

> 来源:hermes-researcher-self-evolution-v1 / 2026-07-13 tick35
> 目标 profile:pm
> 适用版本:tick34 立的 7-field contract 升级 v3
> 触发:cross-cluster F10 + #35406 Docker migration gap + F9 #62365 trust boundary

## 背景

tick34 立的 7-field P1 acceptance contract(family_name / evidence_ids / reproduction_scope / invariants / primary_fix / ship_gate / memory_id)在 tick35 跑 cross-cluster 评估时**不够**:

| 缺口 | 触发证据 |
|---|---|
| 缺 cross_cluster_arrows 字段 | tick35 F9 #63128 ↔ F5 #41935 severity-A 联动,7-field 没有联动字段,PM 无法表达 |
| 缺 trust_boundary 字段 | F9 #62365 compaction fabricates user intent 是**信任边界**破坏,不是普通 P1;acceptance 应该有 trust_boundary_impact 子字段 |
| 缺 config_freshness_post_release 字段 | F10 #35406 Docker migration gap,acceptance 必须标"release 后 5 profile × config.yaml 是否需要重跑 migrate" |
| 缺 family_lifecycle 字段 | F1/F9 family 在 30 天内已升级多次,acceptance 必须标 family 是否进入 stable/maintenance/expansion 阶段 |

## 草稿段落(append to pm SOUL)

```yaml
pm:
  p1_acceptance_contract_v3:
    extends: tick34 v2 (7-field)
    new_fields:
      - cross_cluster_arrows: list of {target_family, severity, interaction_type}
      - trust_boundary_impact: enum {none, info_disclosure, action_authority, identity, fabrication, full_compromise}
      - config_freshness_post_release: {requires_migrate: bool, profiles_affected: list, raw_config_version_check: bool}
      - family_lifecycle: enum {emerging, stable, expansion, maintenance, deprecated}
    cross_cluster_severity_enum:
      - severity-A: family A fix 副作用直接加重 family B 的 bug (chief 6h triage)
      - severity-B: family A fix 必须配合 family B fix 才完整 (chief 24h joint review)
      - severity-C: 独立但需 chief dedup 协调 (进 daily report)
    trust_boundary_impact_examples:
      - fabrication: F9 #62365 compaction injects user request never made → 信任边界破坏
      - action_authority: F7 MCP supply chain → unauthorized command execution
      - identity: F2 #51646 cross-platform memory loss → 跨 surface identity confusion
    config_freshness_post_release_examples:
      - F10 #35406: requires_migrate=true, profiles_affected=[default, chief, dev, pm, qa], raw_config_version_check=true
    family_lifecycle_signals:
      - emerging: < 14 days 立卡 + < 3 issues
      - stable: ≥ 14 days + 5+ issues consolidated + ≥ 1 fix PR merged
      - expansion: 跨 ≥ 2 family 联动触发 cross-cluster
      - maintenance: fix PR 全 merged + 30 days no new evidence
      - deprecated: 90 days no evidence + upstream signal "obsolete"
    current_family_lifecycle_tick35:
      - F1 silent-fail: maintenance (cross-month recurrence 仍是 maintenance,不是 expansion,等 cross-cluster arrows 重新分类)
      - F2 cross-platform-state: stable
      - F3 memory-injection-cross-platform: stable
      - F4 credential-pool-stale-snapshot: stable
      - F5 cron-session-leak-closed-state: expansion (与 F9 联动)
      - F6 outbound-redact-call-site: maintenance
      - F7 MCP-supply-chain: expansion (与 F10 联动)
      - F8 cron-ticker-resilience: stable
      - F9 session-state-integrity: expansion (trust_boundary_impact=fabrication)
      - F10 cron-installer-handoff-state (NEW): emerging
```

## Why this matters

- 7-field 表达"family 内 single-fix 是否完成",v3 表达"family 联动是否完成 + 信任边界是否守住 + 跨 release config freshness"
- v3 让 PM 能产出"cross-cluster acceptance plan",而不是"5 个 family 各 accept 一次"的孤立判断
- trust_boundary_impact 字段让 chief 知道哪些 P1 需要立刻升级(tier-1 SLA),哪些可以下放 PM 跟踪

## Acceptance criteria

1. PM 跑 P1 acceptance 时,默认产出 11-field v3 contract (含 4 新字段)
2. cross_cluster_arrows 不为空时,PM 必须等 chief triage 后再 final acceptance
3. trust_boundary_impact != none 时,PM 必须升级 chief 6h SLA
4. config_freshness_post_release.requires_migrate=true 时,PM 必须 verify 5 profile × config.yaml 全部跑 migrate 后再 final acceptance
5. 5 SOUL 配额中此条占 pm 段