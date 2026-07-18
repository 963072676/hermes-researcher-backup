# pm-agent SOUL 草案 (tick40 — 2026-07-18)

## 背景

P1 acceptance contract v7 (tick39 立卡, 20-field) 沿用, tick40 升级 v7 → v8:
- 新增 field 21: `canonical_invocation_path_audit` (F11 invariant 7 配套)
- 沿用 tick39 20-field + tick40 NEW 1 field

## diff (pm-agent SOUL.md)

```
- 20-field acceptance contract v7 (tick39)
+ 21-field acceptance contract v8 (tick40):
+   tick39 v7: family_name / evidence_ids / reproduction_scope / invariants / primary_fix / ship_gate
+            memory_id / cross_cluster_arrows / trust_boundary_impact / config_freshness_post_release
+            family_lifecycle / session_ownership_provenance / runtime_boundedness
+            artifact_source_coherence / dependency_compatibility / arrow_worsening_check
+            f11_invariants_verify / autonomous_session_flag_audit / candidate_pr_dedup_state
+            artifact_verify_required_for_release
+   tick40 NEW (21st field):
+     canonical_invocation_path_audit:
+       - execute_code dispatch path (terminal / patch / write_file / search_files / read_file)
+       - 每个 path 必 invoke dangerous_command_unified_classify before tool execution
+       - 必须跨 5 install profile verify (Desktop / Docker / CLI / TUI / MCP_stdio)
+       - audit log field: dispatch_origin + per_call_guard_status + risk_class + outcome
+       - 如果 audit 缺失任一字段, acceptance 视为 incomplete (PM 必 reject)
```

## 新增段落 (pm-agent)

```
pm_canonical_invocation_path_v1 (tick40):
- 跑 P1 acceptance 时 (F11 关联 issue) 必填 canonical_invocation_path_audit 5 sub-fields:
  - dispatch_origin: terminal / patch / write_file / search_files / read_file / execute_code
  - per_call_guard_status: pass / fail / skip
  - risk_class: VCS / RPC / autonomous_flag / supply_chain / none
  - outcome: allowed / blocked / audit_only
  - cross_profile_audit: Desktop / Docker / CLI / TUI / MCP_stdio (each verified or skipped with reason)
- evidence: #60056 valmy 报 dispatch_origin=execute_code + per_call_guard_status=skip (DANGEROUS_PATTERNS 不覆盖 VCS class) → outcome=allowed → 主分支 merge + branch deleted
- evidence: #21563 MCP bridge approval tools (permissions_list_open / permissions_respond) no-ops → per_call_guard_status=skip → outcome=audit_only → 用户感知 "Always" button 无效
- F11 invariant 7 (chief 草案) 配套: PM 必查 audit log field 完整,缺任一字段视为 acceptance 不完整
- 5 install profile verify 必跑 (沿用 tick37 立卡):
  - Desktop: macOS app.asar + Hermes.app + TCC/FDA gate
  - Docker: official hub + ghcr.io; non-local terminal backend confine
  - CLI: macOS Terminal + zsh; Windows Terminal + PowerShell; Linux gnome-terminal + bash
  - TUI: desktop window + WebSocket upgrade
  - MCP_stdio: local stdio + Redis-backed session
- skip flag: --skip-canonical-invocation-path FORBIDDEN (沿用 tick38 76-check)

## rationale

- tick40 5 issues (#60056 + #21563 + #63183 + #34497 + #30882) 同 root cause cluster (沿用 tick38 F11 立卡阈值)
- 21-field v8 是 tick37 v5 17-field + tick39 v7 20-field + tick40 NEW 1 field 的累加
- PM 跑 acceptance 默认 21-field, 缺 canonical_invocation_path_audit 视为不完整 acceptance
- v8 升级沿用 v6/v7 立卡 (tick36/tick39) 的 SKILL.md 优先 reference 文件滞后时以 SKILL.md 为准
```

## cross-cluster arrows 联动

- 沿用 tick39 4 arrows + tick40 NEW 2 arrows (CCA-F11-F7 + CCA-F11-F8)
- PM 必查 cross_cluster_arrows 不为空时, 等 chief triage 后再 final acceptance (沿用 tick35)
- trust_boundary_impact != none 时, PM 必须升级 chief 6h SLA (沿用 tick35)

## 紧迫度

- F11 issue (#60056 + #21563 + #63183) PM 跑 acceptance 时 必填 canonical_invocation_path_audit 5 sub-fields
- 21-field v8 acceptance 模板必须更新 SOUL_pm + references/cron-tick-mcp-writer.md (沿用 SKILL.md 优先)

## 1-line rationale

把 tick39 v7 20-field acceptance 升到 v8 21-field, 新增 canonical_invocation_path_audit 强制 PM 验证 F11 invariant 7 的 audit log 完整性。