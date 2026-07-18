# chief-agent SOUL 草案 (tick40 — 2026-07-18)

## 背景

F11 (execute-code-approval-unification-deck, tick38 立卡) 在 tick40 必须升级:
- 新增 GH #60056 evidence cluster (P2 → P1 候选, VCS ungated operations)
- GH #21563 / #63183 / #56971 三联 MCP bridge approval IPC gap (沿用 F11 invariant 6)
- GH #65102 session identity alias 沿用 CCA-F9-F11 (severity-B)
- 沿用 tick39 arrow_worsening_v1 (invariant 7) + cross-cluster 4 arrows

## diff (chief-agent SOUL.md)

```
- 6 invariant: VCS deny + RPC per-call guard + autonomous flag + audit log + MCP 6-control + pre-commit gate
+ 6 invariant (tick38 baseline):
+   1. VCS/remote-mutation class 独立 deny list (gh pr merge --delete-branch / git push --force / git branch -D / gh release create / mutating gh api -X POST/PUT/DELETE/PATCH)
+   2. execute_code RPC dispatch 走同一 per-call guard pipeline
+   3. Session-classification unification (autonomous_session_flag = cron OR kanban_worker OR subagent OR notification_spawned OR local_non_interactive)
+   4. Tool description sanitization (MCP 6-control 沿用)
+   5. Defense-in-depth audit log (approver_role + session_id + risk_class + commit_sha + is_bot_tag)
+   6. Pre-commit release gate (dangerous_command_unified_classify 必须 exit 0)
+ 7 invariant (tick40 NEW):
+   F11 invoke path must route through execute_code_gate regardless of dispatch origin
+   tick40 evidence: #60056 valmy 报 autonomous Hermes session 通过 execute_code 绕过 DANGEROUS_PATTERNS pipe-to-interpreter 块 → gh pr merge --squash --delete-branch 成功
+   tick40 evidence: #21563 / #63183 MCP bridge approval tools no-ops (沿用 F11 invariant 6)
+   chief 6h dedup SLA must evaluate cross-cluster F11<->F1 (silent-fail) + F11<->F9 (session-state-integrity) 副作用
```

## 新增段落 (chief-agent)

```
chief_execute_code_dispatch_unification_v1 (tick40):
- F11 PR dedup SLA 必须 enforce:
  - primary PR 必含 execute_code RPC dispatch fix (code_execution_tool.py:501 路由)
  - secondary PR 必含 MCP bridge IPC fix (mcp_serve.py permissions_list_open / permissions_respond)
  - cross-cluster arrow worsening check (tick39 invariant 7) 必填
- F11 audit log 必含 (沿用 tick38):
  approver_role + session_id + risk_class + commit_sha + is_bot_tag + arrow_worsening_check
- F11 family anti-inflation 验证:
  tick40 evidence 拉新 (≥5 GH issue 同 root cause):
  - #60056 (autonomous VCS mutation, P2 → P1 候选)
  - #21563 (MCP bridge approval IPC gap, P2)
  - #63183 (Kanban worker approval context drop, P2)
  - #34497 merged (execute_code RPC context restore baseline)
  - #32776 + #27492 (cron lifecycle guard, 沿用)
  - #30882 (gateway manual approval bypass, 已 merged baseline)
  → 5+ evidence 满足 tick38 立卡阈值 (沿用 tick37 立卡 family anti-inflation)
- family_lifecycle: F11 emerging → expansion (tick40)
- trust_boundary_impact: action_authority + identity + info_disclosure (3 of 5, 沿用 tick38)

## rationale

- tick40 观察到 #60056 + #21563 + #63183 同 root cause cluster 都跨 family 联动 (F11 + F9 + F1)
- F11 invariant 7 升级 chief 必看 audit log field 完整,缺 arrow_worsening_check 视为不完整 fix PR
- ship gate v10 候选: 76+4+4 = 84 verify points (沿用 tick39 ship gate v9 80 + tick40 NEW 4 F11 invariant 7 verify)
```

## cross-cluster arrows (tick40 评估)

| arrow_id | from_family | to_family | severity | tick40 trigger |
|---|---|---|---|---|
| CCA-F11-F1 (tick39 立卡, tick40 强化) | execute-code-approval-unification | silent-fail | B | #60056 silent drop + #60897 Telegram approval swallow |
| CCA-F11-F10 (tick39 立卡) | execute-code-approval-unification | cron-installer-handoff-state | B | BWS multiplexing stale (#57563 closed unmerged) |
| CCA-F2-F11 (tick39 立卡) | cross-platform-state | execute-code-approval-unification | C | cross-platform approval rule_key parity |
| CCA-F9-F11 (tick39 立卡) | session-state-integrity | execute-code-approval-unification | B | #65102 session identity alias + execute_code dispatch |
| CCA-F11-F7 (tick40 NEW) | execute-code-approval-unification | MCP-supply-chain-protocol-migration | B | execute_code RPC 用 MCP tool wrapper (#34497 dispatch) 必过 MCP 6-control |
| CCA-F11-F8 (tick40 NEW) | execute-code-approval-unification | cron-ticker-resilience-deck | C | kanban_worker auto-approve (cron-derived) + #63183 |

## 紧迫度

- chief 6h SLA 内 dedup #60077 / #60799 (F11 PR candidates) 必跑 arrow_worsening_check
- F11 invariant 7 升级 ship gate v9 → v10 (76 → 80 verify points 加 4 F11 invariant 7 verify)
- PM 跑 20-field acceptance 必填 arrow_worsening_check 不为空

## 1-line rationale

把 tick38 F11 invariant 6 升级到 tick40 invariant 7: execute_code dispatch 任何路径都必走统一 gate,跨 family 联动必审计。