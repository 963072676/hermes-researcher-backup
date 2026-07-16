# SOUL_pm_agent 草案 — P1 acceptance contract v5 → v6 + F11 实战 (tick38, 2026-07-16)

> 配套 SOUL v2 / cron: hermes-researcher-deep-tick-daily
> tick38 立卡:family_name_v1 = `execute-code-approval-unification-deck` (F11,沿用 chief 草案)
> 沿用:tick34 P1 acceptance v2 7-field → tick35 v3 11-field → tick36 v4 15-field → tick37 v5 17-field
> tick38 立卡:**v6 19-field** (+2 字段:F11-specific invariants verify + autonomous_session_flag audit)
> 关联 family: F11 (主) + F7 (CCA-E1) + F8 (CCA-E2) + F10 (CCA-E3)
> 来源:tick38 chief SOUL draft + IterInject arxiv 2605.24659 + CVE-2026-61459 / 59950

## 1. 触发(为什么升级 acceptance contract v5 → v6)

tick37 立卡 17-field v5 在 F11 实战应用时暴露 2 缺口:
1. **缺 F11-specific invariants verify 字段**: F11 6 invariant (chief 草案 section 2) 需独立 verify 字段,不能只放在 invariants (现有字段) 内的 free text
2. **缺 autonomous_session_flag audit 字段**: F11 Invariant 3 要求 audit log 含 approver role / session_id / risk_class,17-field 没独立字段

**沿用 tick34/35/36/37 立卡流程**:
- v2 7-field → v3 11-field (tick35):+cross_cluster_arrows +trust_boundary_impact +config_freshness_post_release +family_lifecycle
- v3 11-field → v4 15-field (tick36):+session_ownership_provenance +runtime_boundedness +artifact_source_coherence +dependency_compatibility
- v4 15-field → v5 17-field (tick37):+candidate_pr_dedup_state +artifact_verify_required_for_release
- **v5 17-field → v6 19-field (tick38)**:+f11_invariants_verify +autonomous_session_flag_audit

## 2. 19-field v6 contract (tick38 立卡)

```python
# 19-field v6 canonical (tick38)
ACCEPTANCE_V6_FIELDS = [
    # tick34 v2 7-field
    "family_name",            # tick34
    "evidence_ids",           # tick34
    "reproduction_scope",     # tick34
    "invariants",             # tick34
    "primary_fix",            # tick34
    "ship_gate",              # tick34
    "memory_id",              # tick34
    # tick35 v3 11-field (新增 4)
    "cross_cluster_arrows",   # tick35
    "trust_boundary_impact",  # tick35
    "config_freshness_post_release",  # tick35
    "family_lifecycle",       # tick35
    # tick36 v4 15-field (新增 4)
    "session_ownership_provenance",   # tick36
    "runtime_boundedness",   # tick36
    "artifact_source_coherence",  # tick36
    "dependency_compatibility",  # tick36
    # tick37 v5 17-field (新增 2)
    "candidate_pr_dedup_state",  # tick37
    "artifact_verify_required_for_release",  # tick37
    # tick38 v6 19-field (新增 2)
    "f11_invariants_verify",  # tick38 NEW
    "autonomous_session_flag_audit",  # tick38 NEW
]
```

### 2.1 f11_invariants_verify (NEW tick38)

**field structure**:
```python
f11_invariants_verify = {
    "invariant_1_vcs_remote_mutation": {
        "deny_list_complete": bool,  # VCS/remote-mutation commands 在 DANGEROUS_PATTERNS
        "default_deny_on_no_approver": bool,  # cron/kanban/subagent/notification 全部 fail-closed
        "evidence_id": str  # 关联 issue/PR
    },
    "invariant_2_execute_code_rpc_per_call_guard": {
        "rpc_dispatch_uses_check_all_guards": bool,
        "hermes_tools_terminal_in_execute_code_bypass_blocked": bool,
        "experiment_patterns_doc_updated": bool,  # experiment-patterns.md:484
        "evidence_id": str
    },
    "invariant_3_session_classification_unification": {
        "autonomous_session_flag_added": bool,
        "all_no_approver_classes_fail_closed": bool,  # cron/kanban/subagent/notification
        "local_non_interactive_bucket_closed": bool,  # approval.py:2707-2713, 2764-2765
        "evidence_id": str
    },
    "invariant_4_tool_description_sanitization": {
        "core_supply_chain_py_added": bool,
        "scan_mcp_description_implemented": bool,
        "perplexity_detection_threshold": float,  # default 2.0
        "known_answer_test_coverage": int,  # default ≥100
        "evidence_id": str
    },
    "invariant_5_defense_in_depth_audit_log": {
        "execute_code_block_sha256_logged": bool,
        "sub_tool_calls_list_logged": bool,
        "github_pr_merge_audit_fields": list,  # [approver_role, session_id, risk_class, commit_sha]
        "is_bot_tag_set_on_agent_actions": bool,
        "evidence_id": str
    },
    "invariant_6_pre_commit_release_gate": {
        "dangerous_command_unified_classify_added_to_ship_gate": bool,
        "ship_gate_version": str,  # v8
        "default_deny_on_absent_flag": bool,
        "evidence_id": str
    }
}
```

### 2.2 autonomous_session_flag_audit (NEW tick38)

**field structure**:
```python
autonomous_session_flag_audit = {
    "flag_definition": str,  # "autonomous_session_flag = cron OR kanban_worker OR subagent OR notification_spawned"
    "fail_closed_coverage": {
        "cron": bool,  # 现有
        "kanban_worker": bool,  # F11 NEW
        "kanban_notification_spawned": bool,  # F11 NEW
        "subagent": bool,  # F11 NEW
        "local_non_interactive": bool  # F11 关闭
    },
    "audit_log_fields_required": list,  # [session_id, role, flag_value, risk_class, approver_role]
    "github_pr_merge_audit_required": bool,  # Invariant 5
    "evidence_id": str
}
```

## 3. P1 acceptance v6 实战应用示例 (F11 #60056)

| 字段 | 实战填值 |
|---|---|
| family_name | execute-code-approval-unification-deck |
| evidence_ids | #60056 + #60077 + #60799 + #24942 + #57890 |
| reproduction_scope | default profile / kanban worker / subagent / cron / notification-spawned session — `local non-interactive → approved` bucket |
| invariants | 6 invariant (chief SOUL draft section 2) |
| primary_fix | (TBD chief 6h dedup, candidate #60077 vs #60799) |
| ship_gate | v8 76-check (tick38 立卡) |
| memory_id | (after MCP propose) |
| cross_cluster_arrows | CCA-E1 (F7) severity-B + CCA-E2 (F8) severity-C + CCA-E3 (F10) severity-C |
| trust_boundary_impact | action_authority + identity + info_disclosure (3 of 5) |
| config_freshness_post_release | {requires_migrate: false, profiles_affected: [default, chief, dev, qa, pm], raw_config_version_check: optional} |
| family_lifecycle | emerging |
| session_ownership_provenance | autonomous_session_flag (cron / kanban worker / subagent / notification) |
| runtime_boundedness | execute_code block ≤ 30s default / 60s kanban / 300s cron;sub-tool call per-call guard < 100ms |
| artifact_source_coherence | tools/approval.py:2696-2765 + tools/code_execution_tool.py:501 + core/supply_chain.py (4 file coherence) |
| dependency_compatibility | hermes-python >= 3.12;PyYAML >= 6.0;mcp-sdk >= 1.28.1 |
| candidate_pr_dedup_state | {total: 2, candidates: [#60077, #60799], primary: TBD, closed_unmerged: [#24942], dedup_decision_made_by: chief, dedup_window_hours: 24} |
| artifact_verify_required_for_release | {release_target: "v0.18.3+", profiles: [Desktop, Docker, CLI, TUI, MCP_stdio], manifest_required: true, import_smoke_paths: [tools/approval.py, tools/code_execution_tool.py, experiment-patterns.md], runtime_smoke_surfaces: [kanban, cron, subagent, notification], cross_profile_audit_required: true} |
| **f11_invariants_verify** | **6 invariant verify objects (结构见 2.1)** |
| **autonomous_session_flag_audit** | **flag_definition + fail_closed_coverage + audit_log_fields + github_pr_merge_audit + evidence_id (结构见 2.2)** |

## 4. PM 11-step P1 acceptance workflow (升级)

1. 收集 P1 cluster evidence (issue + PR + security advisory)
2. 归类 family (本 tick → F11,沿用 tick36/37 anti-inflation 准则)
3. 填 19-field v6 acceptance (本 tick F11 实战)
4. 评估 cross-cluster arrows (沿用 tick35 立卡 protocol)
5. 评估 trust_boundary_impact 5 categories (沿用 tick35 立卡)
6. 评估 family_lifecycle 5 段 (沿用 tick35 立卡)
7. 评估 ship_gate 升级 (本 tick → v8 76-check)
8. 触发 chief 6h dedup SLA (PR ≥ 2 candidates)
9. 等 chief decision 后填 primary_fix
10. ship gate 全 verify (5 grep + 20 cross-profile + 6 MCP + 19 acceptance + 4 cross-cluster + 4 trust boundary + 12 runtime smoke + 4 post-merge + 4 dangerous_command_unified = **76 checks**)
11. 最终 acceptance pass → 写 memory_id + receipt verify (沿用 tick36 review_pending 回读 + tick37 coordinator role 唯一可行 path)

## 5. v5 → v6 migration notes

- v5 17-field 全部保留
- v6 在 v5 末尾 append 2 字段 (f11_invariants_verify + autonomous_session_flag_audit),不替换
- 任何 v5 tick 报告升级到 v6 时只需补 2 字段,不重写整张表
- tick37 之前所有 17-field 报告升级路径:重新拉 receipt + 补 2 字段

## 6. ship_gate v8 升级 (本 tick + chief 立卡)

```text
v7 72-check (tick37) + 4 dangerous_command_unified_classify = v8 76-check

dangerous_command_unified_classify 4 项:
1. VCS/remote-mutation commands 在 DANGEROUS_PATTERNS (grep + AST parse)
2. execute_code RPC dispatch 走 per-call guard (runtime smoke: kanban worker spawn + 模拟 gh pr merge 拦截)
3. Session classification 含 autonomous_session_flag (unit test: cron / kanban / subagent / notification 4 类)
4. audit log 包含 approver role + session_id + risk_class (integration test: 模拟 merge 成功 verify log 含 3 字段)
```

**判定准则**:
- v8 76-check 任一失败立即升级 chief + 飞书报警
- dangerous_command_unified_classify 失败 = ship 拒绝 (即使其他 72 个 PASS)
- skip-dangerous_command_unified_classify flag FORBIDDEN

## 7. 飞书推送内容 (tick38 pm-agent)

```
[P1 acceptance v6 升级] 17-field → 19-field
新增 2 字段: f11_invariants_verify + autonomous_session_flag_audit
F11 实战应用: 6 invariant verify + autonomous_session_flag audit
ship gate v7 → v8 (76-check)
PM 11-step workflow 升级 (加 invariant verify + flag audit)
```

## 8. 关联 family 影响

- **F11 (主)**: execute-code-approval-unification-deck
- **F7 (CCA-E1, severity-B)**: MCP-supply-chain-protocol-migration — F11 修复须 extend F7 tool description sanitization
- **F8 (CCA-E2, severity-C)**: cron-ticker-resilience-deck — F11 kanban-spawned session 走 execute_code 路径,可触发 cron silent die
- **F10 (CCA-E3, severity-C)**: cron-installer-handoff-state — F11 须 verify F10 setup.py pin (#60685) 不被 execute_code 绕过

## 9. 等待 user ack 后

1. 写入 default profile `~/.hermes/profiles/pm/SOUL.md` 作为 v2 段
2. 不写 cron/control plane
3. tick39 audit 回读 verify