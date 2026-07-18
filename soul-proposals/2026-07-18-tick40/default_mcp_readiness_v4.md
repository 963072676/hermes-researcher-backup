# default-agent SOUL 草案 (tick40 — 2026-07-18)

## 背景

default profile MCP 2026-07-28 readiness v3 (tick39, 10-control) 沿用, tick40 升级 v3 → v4:
- v3 baseline: 10-control (tick33 6-control + tick38 3 NEW + tick39 control 10 API session identity early-bind)
- v4 (tick40): v3 10-control + control 11 (canonical_invocation_path 沿用 F11 invariant 7) + control 12 (audit log field strict validation) + control 13 (family 12 verify runtime check)

## diff (default-agent SOUL.md)

```
- MCP 2026-07-28 readiness v3 (tick39): 10-control
+ MCP 2026-07-28 readiness v4 (tick40): 13-control
+   v3 10-control (沿用 tick39 立卡, 全部保留)
+   tick40 NEW 3 control:
+     11. canonical_invocation_path_control (F11 invariant 7):
+       - execute_code RPC dispatch 必走同一 per-call guard pipeline (terminal/patch/write_file/search_files/read_file)
+       - dangerous_command_unified_classify 必须 exit 0
+       - 5 install profile verify (Desktop/Docker/CLI/TUI/MCP_stdio)
+     12. audit_log_field_strict_validation:
+       - 必填字段: dispatch_origin + per_call_guard_status + risk_class + outcome + is_bot_tag + arrow_worsening_check
+       - 缺任一字段 → reject (沿用 tick39 PM 21-field v8)
+       - audit log retention ≥ 90 days
+     13. family_12_verify_runtime:
+       - F11 smoke 4 sub-check (沿用 tick40 QA v10)
+       - F8 smoke 4 sub-check (#61674 lazy jobs.json + #39782 timeout containment)
+       - F12 candidate verify (family anti-inflation 沿用 tick37)
+       - 6-control MCP runtime 4 sub-check (沿用 tick33)
+ trust_policy.strict: true (沿用 tick28)
+ untrusted_repo_self_approval: false (沿用 tick28)
+ pending_label: "Pending approval" (沿用 tick28)
+ --skip-control-N FORBIDDEN (任意 control)
```

## 新增段落 (default-agent)

```
default_mcp_readiness_v4 (tick40):
- v3 10-control (tick39 baseline, 全部保留):
  1. Hash pin (immutable ref)
  2. OSV scan
  3. Shell egress pattern block
  4. Tool description sanitization
  5. Tirith pipe scan (tick33 NEW)
  6. Perplexity detection + Known-answer test
  7. EXT14 cancellation-probe shield (tick38)
  8. MCP server version pin CVE-2026-61459 ≥3.9.0 + CVE-2026-59950 ≥1.28.1 (tick38)
  9. Tool spawn static analyzer argument injection detection (tick38)
  10. API session identity early-bind (tick39 #65102 review)
- v4 13-control (tick40 NEW):
  11. canonical_invocation_path_control (F11 invariant 7)
  12. audit_log_field_strict_validation
  13. family_12_verify_runtime
- readiness gate (default profile):
  - 启动前必过 13 control + 5 install profile verify
  - audit log 必填字段验证 (control 12)
  - family 12 verify runtime check (control 13)
  - 任一 control 失败 → fail-closed, 不允许 cron / gateway 启动

## rationale

- tick40 evidence: #60056 + #21563 + #63183 触发 F11 invariant 7, default profile readiness 必须 enforce
- v4 13-control 是 v3 10-control + 3 NEW 的累加 (沿用 tick33/38/39 立卡)
- 控制 11 配合 F11 chief draft invariant 7, 控制 12 配合 PM 21-field v8 acceptance contract
- 控制 13 配合 QA ship gate v10 family 12 verify
- skip flag FORBIDDEN 全部 13 control (沿用 tick38)
```

## cross-profile 5 install profile verify (沿用 tick37)

- Desktop: macOS app.asar + Hermes.app + TCC/FDA gate; Windows installer + registry; Linux AppImage + dpkg + rpm
- Docker: official hub + ghcr.io; non-local terminal backend confine; media cache scope
- CLI: macOS Terminal + zsh; Windows Terminal + PowerShell; Linux gnome-terminal + bash
- TUI: desktop window + WebSocket upgrade; portable mode
- MCP_stdio: local stdio + Redis-backed session; keepalive empty exception bounded retry

## 紧迫度

- v4 readiness 必跑 13 control + 5 install profile verify
- 任一 control 失败 → fail-closed
- emergency skip FORBIDDEN

## 1-line rationale

把 default MCP readiness v3 10-control 升级到 v4 13-control, 新增 canonical_invocation_path + audit_log_field_strict + family_12_verify_runtime, F11 invariant 7 全 enforce。