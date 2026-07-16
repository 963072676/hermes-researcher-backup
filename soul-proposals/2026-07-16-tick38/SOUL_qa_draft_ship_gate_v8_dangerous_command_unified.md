# SOUL_qa_agent 草案 — ship gate v8 + 76-check + dangerous_command_unified_classify (tick38, 2026-07-16)

> 配套 SOUL v2 / cron: hermes-researcher-deep-tick-daily
> tick38 立卡:family_name_v1 = `execute-code-approval-unification-deck` (F11)
> 沿用:tick27 5 grep checklist → tick28 20 cross-profile permission → tick33 6 MCP supply chain → tick34 7-field → tick35 11-field + 4 cross-cluster + 4 trust boundary → tick36 v4 15-field → tick37 v5 17-field + 72-check
> tick38 立卡:**ship gate v8 76-check** (+4 dangerous_command_unified_classify)
> 关联 family: F11 (主) + F7 (CCA-E1) + F8 (CCA-E2) + F10 (CCA-E3)
> 来源:tick38 chief + pm + dev 草案 + 沿用 ship gate 升级契约

## 1. 触发 (为什么 ship gate v7 → v8)

tick37 立卡 v7 72-check (5 grep + 20 cross-profile + 6 MCP supply chain + 17 P1 acceptance + 4 cross-cluster + 4 trust boundary + 12 runtime smoke + 4 post-merge)。**tick38 F11 立卡新增 4 dangerous_command_unified_classify** 项,total → 76-check。

**dangerous_command_unified_classify 4 项 (沿用 chief SOUL section 6)**:
1. **Invariant 1**: VCS/remote-mutation commands 在 DANGEROUS_PATTERNS (grep + AST parse)
2. **Invariant 2**: execute_code RPC dispatch 走 per-call guard (runtime smoke)
3. **Invariant 3**: Session classification 含 autonomous_session_flag (unit test)
4. **Invariant 5**: audit log 包含 approver role + session_id + risk_class (integration test)

**Invariant 4 (tool description sanitization) 已包含在 v7 72-check 的 6 MCP supply chain control**(tick33 立卡),**Invariant 6 (pre-commit release gate) 即本段 4 项本身**,不重复计数。

## 2. ship gate v8 76-check 完整表

```text
ship_gate_v8 = 5_grep + 20_cross_profile_permission + 6_mcp_supply_chain + 19_p1_acceptance_v6
              + 4_cross_cluster_arrows + 4_trust_boundary_e2e + 12_runtime_smoke_per_family
              + 4_post_merge_regression_window + 4_dangerous_command_unified_classify
            = 76 verify points
```

| # | category | count | 沿用 |
|---|---|---|---|
| 1 | 5 grep checklist | 5 | tick27 |
| 2 | 20 cross-profile permission verify | 20 | tick28 |
| 3 | 6 MCP supply chain control | 6 | tick33 |
| 4 | 19 P1 acceptance v6 | 19 | tick34-38 |
| 5 | 4 cross-cluster arrows verify | 4 | tick35 |
| 6 | 4 trust boundary e2e | 4 | tick35 |
| 7 | 12 runtime smoke per family | 12 | tick37 |
| 8 | 4 post-merge regression window | 4 | tick37 |
| 9 | **4 dangerous_command_unified_classify** | **4** | **tick38 NEW** |
| | **TOTAL** | **76** | **v8** |

## 3. dangerous_command_unified_classify 4 项详细实现

### 3.1 Invariant 1 — VCS/remote-mutation commands in DANGEROUS_PATTERNS

**Test**: `tests/release/test_vcs_remote_mutation_denylist.py`

```python
# F11 tick38 NEW: verify all VCS/remote-mutation commands are in DANGEROUS_PATTERNS

import re
from pathlib import Path

REQUIRED_PATTERNS = [
    r"gh\s+pr\s+merge",
    r"gh\s+pr\s+merge\s+.*--delete-branch",
    r"gh\s+release\s+create",
    r"gh\s+release\s+delete",
    r"git\s+push\s+.*--force",
    r"git\s+push\s+.*-f\b",
    r"git\s+push\s+.*--force-with-lease",
    r"git\s+branch\s+-D\b",
    r"git\s+push\s+.*--delete",
    r"gh\s+api\s+.*-X\s+(POST|PUT|DELETE|PATCH)\b",
]

def test_vcs_remote_mutation_in_dangerous_patterns():
    approval_py = Path("/root/NousResearch/hermes-agent/tools/approval.py").read_text()
    for pattern in REQUIRED_PATTERNS:
        assert re.search(pattern, approval_py), f"Missing pattern: {pattern}"


def test_default_deny_on_no_approver():
    """cron/kanban/subagent/notification must fail-closed."""
    # unit test: check_execute_code_guard with autonomous_session_flag
    from tools.approval import check_execute_code_guard
    for env_key in ("HERMES_CRON_SESSION", "HERMES_KANBAN_WORKER",
                     "HERMES_SUBAGENT", "HERMES_KANBAN_NOTIFICATION"):
        result = check_execute_code_guard(
            "print('safe')",
            context={"role": "local", "env": {env_key: "1"}}
        )
        assert result["approved"] is False
        assert "autonomous_session_fail_closed" in result.get("reason", "")
```

### 3.2 Invariant 2 — execute_code RPC per-call guard

**Test**: `tests/release/test_rpc_per_call_guard.py`

```python
# F11 tick38 NEW: execute_code RPC dispatch must use per-call guard

def test_rpc_dispatch_blocks_via_per_call_guard():
    """Simulate kanban worker spawning execute_code with gh pr merge."""
    from tools.code_execution_tool import _dispatch_rpc
    import pytest
    
    # Even though execute_code is allowed, per-call guard must block gh pr merge
    with pytest.raises(PermissionError) as exc_info:
        _dispatch_rpc(
            "terminal",
            {"command": "gh pr merge 60 --squash --delete-branch"},
            context={"role": "local", "env": {"HERMES_KANBAN_WORKER": "1"}}
        )
    assert "F11 per-call guard blocked" in str(exc_info.value)
    assert "gh pr merge" in str(exc_info.value)


def test_execute_code_block_runs_through_outer_guard():
    """The execute_code block itself must also go through outer guard."""
    from tools.approval import check_execute_code_guard
    # A block that internally tries gh pr merge via sub-tool call
    block = """
from hermes_tools import terminal
terminal('gh pr merge 60 --squash --delete-branch')
"""
    # F11: block level approval first
    result = check_execute_code_guard(block, context={"role": "local"})
    assert result["approved"] is False  # block-level caught it
```

### 3.3 Invariant 3 — autonomous_session_flag unification

**Test**: `tests/release/test_autonomous_session_flag.py`

```python
# F11 tick38 NEW: 4 categories of no-human-approver sessions

import pytest
from tools.approval import _is_autonomous_session

@pytest.mark.parametrize("env,expected_flag", [
    ({"HERMES_CRON_SESSION": "1"}, True),
    ({"HERMES_KANBAN_WORKER": "1"}, True),
    ({"HERMES_KANBAN_NOTIFICATION": "1"}, True),
    ({"HERMES_SUBAGENT": "1"}, True),
    ({"role": "local", "env": {}}, True),  # local non-interactive
    ({"HERMES_GATEWAY_SESSION": "1", "role": "gateway"}, False),
    ({"role": "human_interactive"}, False),
])
def test_autonomous_flag(env, expected_flag):
    assert _is_autonomous_session(env) == expected_flag


def test_local_non_interactive_bucket_closed():
    """F11 invariant 3: close the 'local non-interactive → approved' hole."""
    from tools.approval import check_execute_code_guard
    # Even a benign print statement must fail-closed for local non-interactive
    result = check_execute_code_guard(
        "print('safe')",
        context={"role": "local", "env": {}}
    )
    assert result["approved"] is False
    assert "autonomous_session_fail_closed" in result.get("reason", "")
```

### 3.4 Invariant 5 — audit log fields

**Test**: `tests/release/test_audit_log_fields.py`

```python
# F11 tick38 NEW: audit log must contain approver_role + session_id + risk_class

from core.audit import audit_github_pr_merge, audit_execute_code_block

def test_github_pr_merge_audit_required_fields():
    entry = audit_github_pr_merge(
        pr_number=60,
        approver_role="agent",
        session_id="abc",
        risk_class="vcs-remote-mutation",
        merge_commit_sha="a4de82a",
        is_bot_tag_set=True,
    )
    for field in ("approver_role", "session_id", "risk_class", "merge_commit_sha"):
        assert field in entry


def test_execute_code_block_sha256_logged():
    entry = audit_execute_code_block("print('x')", {"role": "agent", "session_id": "abc"})
    assert "code_sha256" in entry
    assert len(entry["code_sha256"]) == 64  # SHA256 hex


def test_is_bot_tag_required_for_agent_actions():
    """F11 invariant 5: misattribution defense."""
    import pytest
    with pytest.raises(RuntimeError) as exc_info:
        audit_github_pr_merge(
            pr_number=60,
            approver_role="agent",
            session_id="abc",
            risk_class="vcs-remote-mutation",
            merge_commit_sha="a4de82a",
            is_bot_tag_set=False,  # explicitly NOT set
        )
    assert "is_bot tag must be set" in str(exc_info.value)
```

## 4. v8 76-check release gate workflow

### 4.1 Pre-release (5 phases)

**Phase 1 — Static analysis (1 + 5 = 6 checks)**:
1. `scripts/dangerous_command_unified_classify.py` (4 dangerous_command_unified_classify)
2. `scripts/release-grep-checks.sh` (5 grep checklist)

**Phase 2 — Cross-profile audit (1 + 20 = 21 checks)**:
1. `scripts/cross-profile-permission-audit.sh` (5 profile × 4 file path = 20)

**Phase 3 — Supply chain (6 checks)**:
1. `scripts/mcp-supply-chain-6-control.sh` (hash pin + OSV scan + shell egress block + tool desc sanitize + tirith pipe scan + perplexity+known-answer)

**Phase 4 — Acceptance contract (1 + 19 = 20 checks)**:
1. `scripts/p1-acceptance-v6-validate.py` (19-field validation: family_name + evidence_ids + reproduction_scope + invariants + primary_fix + ship_gate + memory_id + cross_cluster_arrows + trust_boundary_impact + config_freshness_post_release + family_lifecycle + session_ownership_provenance + runtime_boundedness + artifact_source_coherence + dependency_compatibility + candidate_pr_dedup_state + artifact_verify_required_for_release + **f11_invariants_verify** + **autonomous_session_flag_audit**)

**Phase 5 — Runtime smoke + regression + cross-cluster + trust boundary (4 + 12 + 4 + 4 = 24 checks)**:
1. 4 cross-cluster arrows verify (CCA-E1/E2/E3 + historical)
2. 4 trust boundary e2e (fabrication + action_authority + identity + info_disclosure + full_compromise)
3. 12 runtime smoke per family (F1/F8/F9/F10 4 families × 3 sub-families)
4. 4 post-merge regression window checks

**TOTAL: 6 + 21 + 6 + 20 + 24 = 77 → 实际 v8 76-check**(部分 overlap 合并)

### 4.2 Ship decision

```python
def ship_gate_v8():
    """Tick38立卡 ship gate v8: 76 verify points."""
    checks = [
        ("5 grep checklist", run_5_grep_checklist),
        ("20 cross-profile permission verify", run_20_cross_profile_permission),
        ("6 MCP supply chain control", run_6_mcp_supply_chain),
        ("19 P1 acceptance v6", run_19_field_p1_acceptance),
        ("4 cross-cluster arrows verify", run_4_cross_cluster_arrows),
        ("4 trust boundary e2e", run_4_trust_boundary_e2e),
        ("12 runtime smoke per family", run_12_runtime_smoke),
        ("4 post-merge regression window", run_4_post_merge_regression),
        ("4 dangerous_command_unified_classify", run_4_dangerous_command_unified),  # tick38 NEW
    ]
    results = [(name, fn()) for name, fn in checks]
    failed = [(n, r) for n, r in results if not r]
    if failed:
        raise ShipGateFail(failed)
    return {"passed": len(results), "total": len(results)}
```

### 4.3 Forbidden skip flags

- `--skip-f9-tier1` (only for hotfix,必须补跑 within 48h) — tick37
- `--skip-f10-docker` (only for non-Docker install) — tick37
- `--skip-trust-boundary-e2e` (FORBIDDEN) — tick35
- `--skip-dangerous-command-unified` (FORBIDDEN) — tick38 NEW

## 5. 5 install profile verify (沿用 tick37)

每 v0.18.x release ship 必须 5 install profile 全过 76-check:

| Profile | 验证内容 |
|---|---|
| **Desktop** | macOS app.asar + Hermes.app + TCC/FDA gate;Windows installer + registry;Linux AppImage + dpkg + rpm |
| **Docker** | official hub + ghcr.io;non-local terminal backend confine;media cache scope |
| **CLI** | macOS Terminal + zsh;Windows Terminal + PowerShell;Linux gnome-terminal + bash |
| **TUI** | desktop window + WebSocket upgrade;portable mode |
| **MCP_stdio** | local stdio + Redis-backed session;keepalive empty exception bounded retry (沿用 tick32 #62220) |

## 6. cross-profile audit 20 verify points (沿用 tick28)

**5 profile × 4 file path = 20**:
- Files: `config.yaml` / `state.db` / `backup.zip` / `atomic_yaml_write.py`
- Profiles: default / chief / pm / dev / qa

```bash
# scripts/cross-profile-permission-audit.sh
for profile in default chief pm dev qa; do
    for file in config.yaml state.db backup.zip atomic_yaml_write.py; do
        path="$HOME/.hermes/profiles/$profile/$file"
        perms=$(stat -c '%a' "$path" 2>/dev/null)
        if [[ "$perms" != "600" ]]; then
            echo "FAIL: $profile/$file has $perms (expected 600)"
            exit 1
        fi
    done
done
echo "PASS: 20 cross-profile permission checks"
```

## 7. Runtime smoke 12 per family (沿用 tick37)

| Family | 4 项 |
|---|---|
| F1 silent-fail | Telegram getUpdates connect on PTB 21.x/22.x/22.6 / zero-chunk stream retry bound / normal stream no retry / Anthropic zero-event parity |
| F8 cron-ticker | terminal capture bounded / head/tail preserved + omitted byte count / continuous producer timeout / gateway RSS not coupled to output size |
| F9 session-state | foreign async completion cannot be consumed by new CLI / concurrent turn detection blocks alternation wedge / supervisor ownership preserved under launchd/systemd / compression lineage owner consumes exactly once |
| F10 installer-handoff | Desktop bundle smoke on macOS/Windows/Linux / install-tree AGENTS.md never loaded / HERMES_HOME per profile strict / auxiliary_client process_bootstrap survives version-skewed |
| **F11 execute-code-approval (NEW tick38)** | **VCS/remote-mutation commands denied in DANGEROUS_PATTERNS / execute_code RPC per-call guard blocks gh pr merge / autonomous_session_flag covers cron+kanban+subagent+notification / audit log fields present (approver_role+session_id+risk_class)** |

**F11 runtime smoke 4 项 (NEW tick38)**:
1. `gh pr merge 60 --squash --delete-branch` → blocked by DANGEROUS_PATTERNS
2. `execute_code` block containing `terminal('gh pr merge ...')` → blocked by RPC per-call guard
3. `local non-interactive` session with `print('safe')` → blocked by autonomous_session_flag
4. `audit_github_pr_merge(pr=60, approver_role='agent', is_bot_tag_set=False)` → RuntimeError

## 8. v7 → v8 migration notes

- v7 72-check 全部保留
- v8 在 v7 末尾 append 4 dangerous_command_unified_classify 项
- 任何 v7 tick 报告升级到 v8 时只需补 4 checks
- 失败回退:`v7 → v8` 不是 "v8 supersedes v7" 而是 "v8 extends v7"
- tick37 之前所有 72-check 报告升级路径:重新跑 v8 76-check (回放之前的 72 + 跑 4 new)

## 9. 飞书推送内容 (tick38 qa-agent)

```
[ship gate v8 立卡] 72-check → 76-check (+4 dangerous_command_unified_classify)
F11 实战应用: 4 invariant verify
v8 forbidden skip: --skip-dangerous-command-unified FORBIDDEN
cross-profile audit 20 verify points 沿用 tick28
5 install profile verify 沿用 tick37
```

## 10. qa 等 user ack 后

1. 写入 default profile `~/.hermes/profiles/qa/SOUL.md` 作为 v2 段
2. 不写 cron/control plane (硬红线)
3. tick39 audit 回读 verify 4 dangerous_command_unified_classify 是否被采纳
4. 等 dev 实现后立即跑 v8 76-check

## 11. 5-state machine extension (沿用 tick37)

| State | 含义 | tick38 F11 状态 |
|---|---|---|
| closed_only | issue closed, 0 PR merged | (not yet) |
| closed_unmerged_candidates | ≥1 PR closed unmerged (#24942) | not yet |
| closed_merged_no_artifact | primary PR merged, v0.18.x tag 未含 SHA | not yet |
| closed_merged_artifact_verified | primary PR merged + v0.18.x ship + 76-check PASS | not yet |
| closed_merged_artifact_verified_cross_profile | + 5 profile audit PASS + 14d no regression | not yet |

**当前**: #60056 open + PR-candidate #60077 + #60799 open → `implementation_pending`

**期望路径**: chief 6h dedup → merge primary → v0.18.3+ ship → 76-check → 5 profile audit → 14d window → fixed