# qa-agent SOUL 草案 (tick40 — 2026-07-18)

## 背景

qa-agent SOUL 在 tick39 升级 ship gate v8 → v9 (80-check), tick40 升级 v9 → v10:
- v9 baseline: 5 grep + 20 cross-profile permission + 6 MCP supply chain + 17-field P1 acceptance v5 + 4 cross-cluster arrows + 4 trust boundary e2e + 12 runtime smoke per family + 4 post-merge regression window = 80
- v10 (tick40): v9 80 + 4 canonical invocation path verify (F11 invariant 7) + 4 family 12 verify (F11 + F12 candidate + F8 sibling + 6-control MCP runtime) = 88

## diff (qa-agent SOUL.md)

```
- ship gate v9 (tick39): 80 verify points
+ ship gate v10 (tick40): 88 verify points
+   v9 80 verify points (沿用 tick39 立卡, 全部保留)
+   tick40 NEW 8 verify:
+     - 4 canonical invocation path verify (F11 invariant 7):
+       1. execute_code RPC dispatch path coverage (terminal/patch/write_file/search_files/read_file 都必过 dangerous_command_unified_classify)
+       2. MCP bridge approval IPC functional (permissions_list_open 必须返回非空 + permissions_respond 必须 resolve)
+       3. autonomous_session_flag audit log field 完整 (cron/kanban_worker/subagent/notification_spawned/local_non_interactive 5 分类全 verify)
+       4. cross_profile audit (Desktop/Docker/CLI/TUI/MCP_stdio 5 install profile 全 verify)
+     - 4 family 12 verify (沿用 tick37 runtime smoke per family):
+       5. F11 execute-code-approval-unification-deck smoke (4 sub-check):
+         - VCS deny class effective (gh pr merge --delete-branch blocked)
+         - execute_code RPC per-call guard fires
+         - MCP bridge IPC functional
+         - autonomous_session_flag fail-closed
+       6. F8 cron-ticker-resilience-deck smoke 拉新 (沿用 tick37):
+         - #61674 lazy jobs.json path verify
+         - #39782 timeout containment verify (no overlap same job)
+       7. F12 candidate verify (F12 pending evidence, family anti-inflation 沿用 tick37)
+       8. 6-control MCP runtime verify (沿用 tick33 supply chain baseline)
+ skip flags:
+   --skip-canonical-invocation-path FORBIDDEN (tick40 NEW)
+   --skip-family-12-verify FORBIDDEN (沿用 tick37)
+   --skip-arrow-worsening FORBIDDEN (沿用 tick39)
```

## 新增段落 (qa-agent)

```
qa_ship_gate_v10 (tick40):
- ship gate v9 (80) + v10 (8) = 88 verify points
- 任一 verify 失败 → 立即升级 chief + 飞书报警
- 4 canonical invocation path verify 必跑 (F11 invariant 7):
  - canonical_invocation_path_audit 字段必填 5 sub-fields (沿用 tick40 PM v8)
  - cross-profile 5 install profile smoke 必跑 (沿用 tick37)
  - audit log field: dispatch_origin + per_call_guard_status + risk_class + outcome 必填
- 4 family 12 verify (沿用 tick37 runtime smoke per family):
  - F11 execute-code-approval-unification-deck 4 sub-check
  - F8 cron-ticker-resilience-deck 4 sub-check (含 #61674 + #39782 拉新)
  - F12 candidate 4 sub-check (family anti-inflation 验证)
  - 6-control MCP runtime 4 sub-check (沿用 tick33)
- emergency skip flag (FORBIDDEN):
  - --skip-canonical-invocation-path
  - --skip-family-12-verify
  - --skip-arrow-worsening
- v10_to_v9 migration:
  - v9 80 verify 全部保留
  - v10 在 v9 末尾 append 8 verify, 不替换
  - 任何 v9 tick 报告升级到 v10 时只需补 8 verify

## rationale

- tick40 evidence: #60056 + #21563 + #63183 + #61674 + #39782 = 5 P1 同 root cause cluster → ship gate 必须 enforce canonical invocation path
- v10 = v9 (80) + 4 canonical invocation path + 4 family 12 = 88, total cost 与 v9 8-check 升级对齐 (沿用 tick38 v7 → v8 4-check 升级)
- trust boundary e2e 不能 skip (沿用 tick35 + tick36 + tick38 立卡)
- family anti-inflation 沿用 tick37, F12 candidate 满足 ≥ 5 evidence 后升 family, 否则维持 candidate
```

## 紧迫度

- v10 ship gate 必跑 88 verify points 才能 ship
- emergency skip flag 必须全部 FORBIDDEN
- F11 + F8 sibling cluster 升级 ship gate 是 release blocker

## 1-line rationale

把 qa ship gate v9 80-check 升级到 v10 88-check, 新增 4 canonical invocation path verify + 4 family 12 verify, F11 invariant 7 enforcement。