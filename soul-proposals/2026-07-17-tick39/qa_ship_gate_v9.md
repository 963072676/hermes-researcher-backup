# qa SOUL 草案 (tick39 — 2026-07-17)

## 背景

tick38 ship gate v8 76 checks 在 tick39 必须升级到 v9:
- 新增 verify: cross_cluster_arrow_worsening_verify (4 verify points)

## diff

```
- v8 76 checks = 5 grep + 20 permission + 6 MCP + 20 P1 acceptance (v6 19+1) + 4 cross-cluster arrows + 4 trust boundary + 17 runtime smoke + 4 post-merge regression
+ v9 80 checks = v8 76 + 4 NEW arrow_worsening_verify
```

## 新增段落 (qa)

```
ship_gate_v9_80_check (tick39):
- 4 NEW arrow_worsening_verify checks:
  1. arrow_worsening_audit_log_field_present (verify audit log has arrow_worsening_check for any multi-family PR)
  2. arrow_worsening_before_after_capture (verify before_side_effect AND after_side_effect both present)
  3. arrow_worsening_severity_check (verify severity_measured <= severity_predicted)
  4. arrow_worsening_emergency_stop (verify if severity_measured > severity_predicted -> ship MUST abort)

binding: v8 (76) 已被 v9 (80) 升级推翻, tick39+ 任何 cron worker 跑 ship gate 必须 80 checks
forbidden flag: --skip-arrow-worsening-verify FORBIDDEN (同 --skip-trust-boundary-e2e 沿用 tick38)
```

## rationale

- #57563 cross-family fix 缺 arrow audit 字段, qa ship gate 必须 verify
- arrow_worsening_severity_check (verify 3) 是 tick35 severity-A -> severity-实测 上升的 catch gate
- emergency stop (verify 4) 是 chief 6h SLA 的 ship-time gate
