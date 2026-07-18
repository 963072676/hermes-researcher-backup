---
name: hermes-canonical-invocation-path-v1
description: 'F11 execute-code-approval-unification-deck invariant 7 配套 skill。强制 audit log 5 必填字段 (dispatch_origin / per_call_guard_status / risk_class / outcome / is_bot_tag + arrow_worsening_check) 在 canonical_invocation_path 任何路径都必填,跨 5 install profile 全 verify。Use when: F11 issue (#60056 + #21563 + #63183 + #34497 + #30882) acceptance 必须 verify execute_code dispatch 任何 origin (terminal/patch/write_file/search_files/read_file) 都走 dangerous_command_unified_classify。'
version: 1.0.0
author: hermes-researcher (auto-generated tick40)
license: MIT
created_by: agent
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [cron, self-evolving, F11, execute-code-approval, canonical-invocation-path, audit-log]
    family: F11
    tick: 40
    related: [hermes-researcher-self-evolution-v1, hermes-cross-cluster-arrow-worsening-check-v1, hermes-data-injection-isolation-deck-v1]
---

# hermes-canonical-invocation-path-v1

## 触发

任何 F11 关联 issue (#60056 + #21563 + #63183 + #34497 + #30882 同 root cause cluster) acceptance 必跑:
- 任意 PR 涉及 execute_code RPC dispatch path
- 任意 audit log 字段缺失
- 任意 cross-cluster arrow worsening 字段缺失
- chief 6h dedup SLA 时

## 流程

```python
def canonical_invocation_path_audit(issue_id, pr_id=None):
    """Build canonical_invocation_path_audit entry for F11 issue acceptance."""
    audit = {
        "issue_id": issue_id,
        "pr_id": pr_id,
        "audit_timestamp": now_utc(),
        "dispatch_paths": {},
        "cross_profile_audit": {},
        "audit_log_fields": {},
        "arrow_worsening_check": [],
    }
    # 5 dispatch paths (F11 invariant 7)
    for origin in ["terminal", "patch", "write_file", "search_files", "read_file", "execute_code"]:
        guard = invoke_dangerous_command_unified_classify(origin, issue_id)
        audit["dispatch_paths"][origin] = {
            "per_call_guard_status": guard.status,
            "risk_class": guard.risk_class,
            "outcome": guard.outcome,
            "audit_only": guard.outcome == "audit_only",
        }
    # 5 install profile verify
    for profile in ["Desktop", "Docker", "CLI", "TUI", "MCP_stdio"]:
        smoke = run_install_profile_smoke(profile, issue_id)
        audit["cross_profile_audit"][profile] = {
            "smoke_status": smoke.status,
            "smoke_evidence": smoke.evidence[:200],
        }
    # audit log field strict validation
    log = fetch_audit_log(issue_id, pr_id)
    required_fields = ["dispatch_origin", "per_call_guard_status", "risk_class", "outcome", "is_bot_tag", "arrow_worsening_check"]
    audit["audit_log_fields"] = {f: log.get(f) is not None for f in required_fields}
    audit["audit_log_complete"] = all(audit["audit_log_fields"].values())
    # arrow worsening check (沿用 tick39)
    audit["arrow_worsening_check"] = arrow_worsening_check(pr_id, families_touched=["F11"])
    return audit
```

## 输出

```json
{
  "issue_id": 60056,
  "pr_id": 60799,
  "audit_timestamp": "2026-07-18T18:30:00Z",
  "dispatch_paths": {
    "terminal": {"per_call_guard_status": "pass", "risk_class": "VCS", "outcome": "blocked", "audit_only": false},
    "execute_code": {"per_call_guard_status": "fail", "risk_class": "VCS", "outcome": "allowed", "audit_only": false}
  },
  "cross_profile_audit": {
    "Desktop": {"smoke_status": "pass", "smoke_evidence": "macOS TCC gate verified"},
    "Docker": {"smoke_status": "pass", "smoke_evidence": "ghcr.io confine verified"},
    "CLI": {"smoke_status": "pass", "smoke_evidence": "bash/zsh verified"},
    "TUI": {"smoke_status": "pass", "smoke_evidence": "WebSocket upgrade verified"},
    "MCP_stdio": {"smoke_status": "pass", "smoke_evidence": "Redis-backed session verified"}
  },
  "audit_log_fields": {
    "dispatch_origin": true,
    "per_call_guard_status": true,
    "risk_class": true,
    "outcome": true,
    "is_bot_tag": true,
    "arrow_worsening_check": false
  },
  "audit_log_complete": false,
  "arrow_worsening_check": [
    {
      "from_family": "F11",
      "to_family": "F1",
      "before_side_effect": "execute_code 3 gap",
      "after_side_effect": "vision sandbox unified but execute_code subprocess still bypass approval",
      "severity_predicted": "severity-B",
      "severity_measured": null
    }
  ],
  "action": "INCOMPLETE_ACCEPTANCE"
}
```

## 判定

- `audit_log_complete=false` → REJECT acceptance (PM 必 reject)
- `cross_profile_audit[*].smoke_status != pass` → REJECT acceptance
- `arrow_worsening_check[*].severity_measured > severity_predicted` → ABORT_SHIP
- 全部 pass → SHIP with audit log
- 任一 failure → 飞书报 chief + PM

## 6 invariant 必备 (沿用 tick38 F11)

1. VCS/remote-mutation class 独立 deny list
2. execute_code RPC dispatch 走同一 per-call guard pipeline
3. Session-classification unification (autonomous_session_flag)
4. Tool description sanitization (MCP 6-control)
5. Defense-in-depth audit log (5 必填字段 + arrow_worsening_check)
6. Pre-commit release gate (dangerous_command_unified_classify exit 0)
7. (NEW tick40) canonical_invocation_path 任何 origin 都走 guard

## 5 install profile (沿用 tick37)

- Desktop: macOS app.asar + Hermes.app + TCC/FDA gate
- Docker: official hub + ghcr.io; non-local terminal backend confine
- CLI: macOS Terminal + zsh; Windows Terminal + PowerShell; Linux gnome-terminal + bash
- TUI: desktop window + WebSocket upgrade; portable mode
- MCP_stdio: local stdio + Redis-backed session; keepalive empty exception bounded retry

## 1-line rationale

把 F11 invariant 7 (chief 草案) + PM 21-field v8 canonical_invocation_path_audit 字段 + QA ship gate v10 4 verify 整合到一个可执行 skill, F11 acceptance 必跑。

## pitfalls

- canonical_invocation_path_audit 5 dispatch paths 必须 5/5 invoke dangerous_command_unified_classify (execute_code 自身 origin 必跑, 不要 skip)
- cross_profile_audit 5 install profile smoke 必须 exit 0 (沿用 tick37 立卡 skip FORBIDDEN)
- audit_log_complete 任一字段缺失视为 incomplete, PM reject 不允许 ship
- arrow_worsening_check 必填 (沿用 tick39), 缺视为 incomplete

## 相关 references

- `references/cron-tick-mcp-writer.md` — tick32 canonical MCP writer
- `references/cron-tick-execution-recipe.md` — tick execution 9 步
- `references/tick39-deliverables.md` — tick39 invariant 7 baseline
- `references/tick38-deliverables.md` — F11 立卡