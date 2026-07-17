# pm SOUL 草案 (tick39 — 2026-07-17)

## 背景

tick38 立的 19-field P1 acceptance v6 在 tick39 必须升级到 v7:
- 新增字段: arrow_worsening_check (cross-cluster arrow 副作用 verify 结构)

## diff

```
- 19-field v6: ... f11_invariants_verify + autonomous_session_flag_audit
+ 20-field v7: + arrow_worsening_check (NEW tick39)
```

## 新增段落 (pm)

```
p1_acceptance_contract_v7_20_field (tick39):
- 19-field v6 -> 20-field v7
- NEW field: arrow_worsening_check
  - type: list[{from_family, to_family, before_side_effect, after_side_effect, severity_predicted, severity_measured}]
  - required_when: any fix PR touches >= 2 family OR has cross-cluster arrow
  - skip_when: family_count == 1 AND arrow_count == 0
  - PM enforces: arrow_worsening_check 不为空时 PM acceptance ⚠ -> 等 chief triage

binding: v6 (19-field) 已被 v7 (20-field) 升级推翻, tick39+ 任何 cron worker 跑 P1 acceptance 必须 20-field
```

## rationale

- tick35 立的 cross-cluster arrows 至今缺 binding audit 字段
- tick39 #57563 (BWS multiplexing) 跨 F2 + F10, F2 <-> F10 arrow 必须 recorded
- PM acceptance 不验 cross-cluster arrow 时, chief dedup SLA 会漏
