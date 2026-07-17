# default SOUL 草案 (tick39 — 2026-07-17)

## 背景

tick38 立的 MCP 2026-07-28 readiness v2 9-control 在 tick39 必须升级到 v3:
- #65102 暴露: API session identity alias resolve 早绑定问题
- 新增 control 10: API session identity early-bind + cross-surface verification

## diff

```
- 9-control v2: ... EXT14 shield + MCP server version pin + tool spawn static analyzer
+ 10-control v3: + API session identity early-bind + cross-surface verify
```

## 新增段落 (default)

```
mcp_2026_07_28_readiness_v3_10_control (tick39):
- 10 control list:
  1-9. (沿用 tick38 SOUL_default 草案 v2)
  10. (NEW tick39) API session identity early-bind: any API turn that maps to a configured alias MUST build native SessionContext prompt + toolset before AIAgent construction (per #65102 review). Reject configured aliases that resolve to recursive or unsupported destinations. Reject profile / scope_id aliases until canonical session keys represent workspace scope without collisions.

ship gate: mcp_v3_10_control_verify must exit 0 for v0.18.x+ ship
```

## rationale

- #65102 暴露: PR 已 ship identity alias resolve, 但仍缺 native SessionContext prompt build (review 标 P2 follow-up)
- tick38 v2 9-control 未覆盖 API turn 与 native session binding 一致性
- v3 控制 10 是 critical 跨-surface 风险 (沿用 tick35 CCA-5 F2<->F9)

## bind cross-family

- F2 (cross-platform-state) <-> F11 (execute-code-approval-unification) NEW
- F9 (session-state-integrity) <-> F2 (cross-platform-state) 沿用 CCA-5 severity-C
