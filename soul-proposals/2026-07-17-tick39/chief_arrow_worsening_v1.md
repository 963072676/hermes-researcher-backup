# chief-agent SOUL 草案 (tick39 — 2026-07-17)

## 背景

F11 (execute-code-approval-unification-deck, tick38 立卡) 在 tick39 必须升级:
- sweeper:risk-execute-code-approval-unification 标记
- 6 invariant 必备 (沿用 tick38 SOUL_chief 草案)
- 新增 invariant 7: cross-cluster arrow worsening mandate (tick39 立卡)

## diff

```
- 5. Defense-in-depth audit log: approver_role + session_id + risk_class + commit_sha + is_bot_tag
+ 5. Defense-in-depth audit log: approver_role + session_id + risk_class + commit_sha + is_bot_tag + arrow_worsening_check (NEW tick39)
+ 7. (NEW tick39) Cross-cluster arrow worsening prevent
```

## 新增段落 (chief-agent)

```
family_audit_arrow_worsening_v1 (tick39):
- When any fix PR addresses family A AND family B simultaneously, audit log MUST include arrow_worsening_check field
- arrow_worsening_check format: {from_family, to_family, before_side_effect, after_side_effect, severity_predicted, severity_measured}
- If severity_measured > severity_predicted -> chief 6h SLA escalation (no ship until re-evaluated)
- Cross-cluster F9<->F5 (CCA-1 severity-A), F7<->F10 (CCA-2 severity-B), F9<->F8 (CCA-3 severity-B) MUST audit on every PR touching either side
```

## rationale

- tick39 发现 #65102 (session identity alias) + #57563 (BWS multiplexing) + #60897 (Telegram approval) 同时跨 family 但缺 arrow 联动 audit
- arrow_worsening_check 是 tick35 cross-cluster arrows 立卡的 binding enforcement 缺失部分
- chief-agent 必须在 PR dedup 6h SLA 时同时验证 cross-cluster arrow 副作用

## cross-cluster arrows (tick39 新立)

| arrow_id | from_family | to_family | severity |
|---|---|---|---|
| CCA-F11-F1 | execute-code-approval-unification | silent-fail | severity-B (approval swallow -> silent drop) |
| CCA-F11-F10 | execute-code-approval-unification | cron-installer-handoff-state | severity-B (BWS multiplexing stale config) |
| CCA-F2-F11 | cross-platform-state | execute-code-approval-unification | severity-C (cross-platform approval rule_key parity) |
