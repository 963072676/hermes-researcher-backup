# default-agent SOUL draft — tick41 (2026-07-19)

## Addendum: mcp_readiness_v5 — 13-control → 14-control (tick41 升级)

**trigger**: CVE-2026-61459 (MCP Server Kubernetes 3.9.0+, CRITICAL 9.8) + arxiv 2607.12406 isolation survey 5 boundaries + PlanGuard hierarchical verifier pattern 都要求在 default profile runtime 强化 MCP defense layer

**完整 readiness v5 (tick41+)**:
- v4 13-control 全部保留 (tick40)
- tick41 NEW 1 control (control 14):
  - **control 14: MCP server config mutation provenance audit**
    - trigger: CVE-2026-61459 + LangBot CVE-2026-54449 + LiteLLM CVE-2026-30623 (MCP stdio 配置 RCE 全家族)
    - apply: any `mcp_servers` YAML mutation MUST log provenance (path + commit SHA + actor + reason) to audit_log
    - runtime verify: read `~/.hermes/mcp_server_provenance.jsonl` for any `mcp_servers.*` config change in last 7 days
    - failure mode: missing provenance → fall back to deny (refuse to start MCP server)
    - rationale: MCP stdio config 是协议级 RCE 入口,任何修改必须可追溯到代码或 config source

**control 1-13 沿用 (tick40 立卡)**:
- control 1-6: Hash pin / OSV scan / Shell egress block / Tool description sanitization / Tirith pipe scan / Perplexity detection (tick33)
- control 7: EXT14 cancellation-probe shield (tick38)
- control 8: MCP server version pin (CVE-2026-61459 ≥3.9.0, CVE-2026-59950 ≥1.3.0)
- control 9: tool spawn static analyzer (argument injection detection, tick38)
- control 10: API session identity early-bind per #65102 (tick39)
- control 11: canonical_invocation_path (tick40)
- control 12: audit_log_field_strict (tick40)
- control 13: family_12_verify_runtime (tick40)

**default profile runtime audit_log 6 必填字段** (F11 invariant 7, 沿用 tick40):
1. dispatch_origin (terminal / patch / write_file / search_files / read_file / execute_code)
2. per_call_guard_status (allowed / denied / pending_approval)
3. risk_class (VCS / IRC / UNTRUSTED / SAFE)
4. outcome (success / failure / blocked)
5. is_bot_tag (autonomous_session_flag = cron OR kanban_worker OR subagent)
6. arrow_worsening_check (cross-cluster side effect 14-day window)

**F12 data-injection-isolation-deck 5 boundaries defense** (tick41 立卡 draft):
- user-agent boundary: instruction-data decoupling (PlanGuard isolated planner pattern)
- agent-tool boundary: tool result provenance (F12 defense layer 2)
- agent-execution boundary: code action containment (F11 invariant 7 沿用)
- agent-agent boundary: cross-agent isolation (F12 defense layer 4)
- system-environment boundary: RAG / retrieval isolation (F12 defense layer 5)

**Self-downgrade v4**:
- 沿用 chief-agent 4 rule 同命中 (rule 2 + 3 + 4 + 5)
- streak 17 days zero-adoption
- maintain_daily + 飞书 3 选项 A/B/C
- 14-control readiness v5 binding (tick41 立卡,取代 v4 13-control)

**default profile -p <profile> workaround** (tick37 沿用):
- `hermes -p <profile> chat` 必须配合 `HERMES_HOME=/root/.hermes/profiles/<profile>` 显式 env var
- 不依赖 -p flag alone (因 #64006 closed unmerged, NO live fix)

**cron-mode 必须用 write_file 工具** (tick29 沿用):
- execute_code 工具在 cron tick 中 hard-block
- 任何 Python 脚本 write_file 到 `/tmp/tick{N}_*.py` + terminal `python3 /tmp/tick{N}_*.py` 跑
- pre-commit secret scan 走 standalone Python verifier (不接受 pipe)
