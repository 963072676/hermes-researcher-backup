# dev SOUL 草案 (tick39 — 2026-07-17)

## 背景

tick39 发现: 已 ship 的 fix PR (例 #57890 vision sandbox escape) 后续仍可能漏覆盖 sibling code path
- 例: #60056 execute_code 3 gap root cause, 虽 #57890 close vision 但 execute_code 未 audit
- 需要 dev profile 加 family-touch verification 强制 sibling scan

## diff

```
- 7 invariant 必备 (沿用 tick35/tick38)
+ 7 invariant 必备 + invariant 8: family sibling sweep 强制
```

## 新增段落 (dev)

```
family_sibling_sweep_v1 (tick39):
- When any fix PR closes a P1 with sweeper:risk-X label, dev MUST run sweep across all code paths under same family_name registry
- Sweep rule: for each entry in family registry (F1-F11), grep for unresolved family label on issue that should have been closed when PR merged
- Tool: python3 scripts/family_sibling_sweep.py --family F11
- Output: list of sibling issues that may need re-evaluation
- Tick-level: weekly sweep batch on Sundays 06:00 UTC
```

## rationale

- tick38 立卡 F11 时只拉 5+ evidence, 但 dev fix (例 #57890 merged F11 invocation) 不会扫 sibling
- #60056 open 21 天仍无 fix 是 dev 未 sweep 结果
- 升级 dev SOUL 把 sibling sweep 从 optional 改 binding
