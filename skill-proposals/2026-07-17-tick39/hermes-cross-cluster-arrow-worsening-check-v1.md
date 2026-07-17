# cross-cluster-arrow-worsening-check v1 (2026-07-17 tick39)

## 触发

任何 PR 涉及 family A + family B 联动时立即触发:
- 任意 PR label set 包含 >= 2 个 sweeper:risk-*
- 任意 fix 在 multi-family issue (#57563 模式)
- chief 6h dedup SLA 验 multi-family PR 时

## 流程

```python
def arrow_worsening_check(pr_id, families_touched):
    """Build arrow_worsening audit entry."""
    arrows = []
    for from_f, to_f in cross_cluster_pairs(families_touched):
        before = measure_side_effect(from_f, to_f, before_pr=pr_id)
        # apply PR simulation in dry-run mode
        after = predict_side_effect(from_f, to_f, after_pr=pr_id)
        arrows.append({
            "from_family": from_f,
            "to_family": to_f,
            "before_side_effect": before,
            "after_side_effect": after,
            "severity_predicted": severity_eval(from_f, to_f, after),
            "severity_measured": None
        })
    return {"arrow_worsening_check": arrows}
```

## 输出

```json
{
  "pr_id": 57890,
  "families_touched": ["F11", "F1"],
  "arrow_worsening_check": [
    {
      "from_family": "F11",
      "to_family": "F1",
      "before_side_effect": "execute_code 3 gap",
      "after_side_effect": "vision sandbox unified but execute_code subprocess still bypass approval",
      "severity_predicted": "severity-B",
      "severity_measured": "severity-A"
    }
  ],
  "action": "ABORT_SHIP"
}
```

## 判定

- severity_measured > severity_predicted -> ABORT ship
- severity_measured == severity_predicted -> ship with audit log
- severity_measured < severity_predicted -> ship with downgrade note

## 1-line rationale

把 tick35 cross-cluster arrows 立卡从 design-time 升级到 enforcement-time
