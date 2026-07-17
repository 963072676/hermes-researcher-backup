# family-sibling-sweep v1 (2026-07-17 tick39)

## 触发

任何 cron worker / dev / pm 看到以下任一条件立即触发:
- fix PR 关闭 P1 带有 sweeper:risk-X label, 但同 family code path 上有 unresolved issue
- 一段时间内同 family 复发 issue (沿用 tick27 silent-fail 模式)
- chief-agent 周日 06:00 UTC 自动跑 weekly sweep

## 流程

```bash
# 1. 拉 family registry
hermes-researcher-data family registry --version v11

# 2. 跑 sibling sweep
python3 scripts/family_sibling_sweep.py --family <F1-F11> --since 30d

# 3. 输出未 resolve siblings
```

## 输出

```json
{
  "family": "F11",
  "swept_at": "2026-07-17T06:00:00Z",
  "siblings": [
    {"issue": 60056, "label": "P2", "sweeper": "risk-execute-code-approval-unification", "status": "open", "evidence": "3 gap root cause + sibling of #57890 vision sandbox"},
    {"issue": 35164, "label": "P1", "sweeper": "risk-security-boundary", "status": "open", "evidence": "duplicate of #29159 but fix PR #29307 merged then re-surfaced"}
  ],
  "action": "promote_to_p1_if_recurring"
}
```

## 判定

- siblings count >= 1 -> chief 6h SLA evaluation
- siblings count >= 3 (recurring) -> expand family (revise sweeper marker)
- 0 siblings -> close sweep cycle

## 1-line rationale

防止 fix PR 关闭一个 issue 但漏同 family code path 上其他 issue
