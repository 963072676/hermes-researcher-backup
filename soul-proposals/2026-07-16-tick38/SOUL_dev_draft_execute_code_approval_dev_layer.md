# SOUL_dev_agent 草案 — execute_code approval unification dev layer (tick38, 2026-07-16)

> 配套 SOUL v2 / cron: hermes-researcher-deep-tick-daily
> tick38 立卡:family_name_v1 = `execute-code-approval-unification-deck` (F11)
> 沿用:tick35 F10 dev-layer check_config_version read_raw 立卡 + tick36/37 dev 实战
> 关联 issue: #60056 / PR #60077 + #60799 / unmerged #24942
> trust boundary: action_authority + identity + info_disclosure
> 来源:tick38 chief + pm 草案 + #60056 forensics + #24942 Phase 1 hardening attempted fix

## 1. 触发 (为什么 dev 草案独立)

chief 草案 (Invariant 1-6) + pm 草案 (19-field v6) 已立 family + acceptance contract。**dev 草案聚焦实现细节**:
- 哪个 file 改什么 line
- 现有 `DANGEROUS_PATTERNS` 段(line 546-685)如何 insert VCS class
- `check_execute_code_guard` (line 2696-2765) 如何 add autonomous_session_flag
- `code_execution_tool.py:501` RPC dispatch 如何 wire per-call guard
- `experiment-patterns.md:484` 文档如何改 (避免 documenting escape hatch)

沿用 tick35 F10 立卡 dev 模式: Layer 1 (UI) + Layer 2 (Boot) + Layer 3 (Dev root cause)。F11 dev 立卡 3 layer:

## 2. Layer 1 (Per-call guard pipeline) — 主要实现层

### 2.1 tools/approval.py 修改 (主要工作)

**DANGEROUS_PATTERNS section insert (after line 685)**:

```python
# F11 tick38 NEW: VCS/remote-mutation class
DANGEROUS_PATTERNS_VCS_REMOTE_MUTATION = [
    # gh CLI merge/release/delete-branch
    r"gh\s+pr\s+merge\s+.*--(squash|merge|rebase|delete-branch)",
    r"gh\s+pr\s+merge\s+\d+",  # bare merge
    r"gh\s+release\s+create",
    r"gh\s+release\s+delete",
    # git force / delete / push-delete
    r"git\s+push\s+.*--force",
    r"git\s+push\s+.*-f\b",
    r"git\s+push\s+.*--force-with-lease",
    r"git\s+branch\s+-D\b",
    r"git\s+branch\s+--delete\s+--force",
    r"git\s+push\s+.*--delete",
    # gh API mutating verbs
    r"gh\s+api\s+.*-X\s+(POST|PUT|DELETE|PATCH)\b",
    # hermes-attributed actions: gh CLI runs as agent attribution owner
    # All above auto-flag is_bot=true for audit (Invariant 5)
]

DANGEROUS_PATTERNS = DANGEROUS_PATTERNS + DANGEROUS_PATTERNS_VCS_REMOTE_MUTATION  # append
```

**Autonomous session flag (insert after line 2696 in check_execute_code_guard)**:

```python
# F11 tick38 NEW: Autonomous session flag (Invariant 3)
def _is_autonomous_session(context: RequestContext) -> bool:
    """Detect no-human-approver session across cron/kanban/subagent/notification paths."""
    role = getattr(context, 'role', None)
    env = getattr(context, 'env', {}) or {}
    if env.get('HERMES_CRON_SESSION') == '1':
        return True
    if env.get('HERMES_KANBAN_WORKER') == '1':
        return True
    if env.get('HERMES_KANBAN_NOTIFICATION') == '1':
        return True
    if env.get('HERMES_SUBAGENT') == '1':
        return True
    # local non-interactive non-gateway session → flagged as autonomous
    if role in ('local', 'non_interactive') and not env.get('HERMES_GATEWAY_SESSION') == '1':
        return True
    return False

# F11 tick38: replace existing fail-open path with fail-closed
def check_execute_code_guard(code: str, context: RequestContext) -> dict:
    """F11 upgraded: fail-closed for all autonomous sessions."""
    if _is_autonomous_session(context):
        # F11 invariant 3: ANY autonomous session → fail-closed
        # Even if DANGEROUS_PATTERNS don't match
        return {
            "approved": False,
            "reason": "autonomous_session_fail_closed",
            "require_explicit_approval": True,
            "session_flag": "autonomous",
        }
    # Non-autonomous: existing path with NEW VCS/remote-mutation class
    for pattern in DANGEROUS_PATTERNS:  # now includes VCS class
        if re.search(pattern, code):
            return {
                "approved": False,
                "reason": f"dangerous_pattern_match: {pattern}",
                "require_explicit_approval": True,
            }
    return {"approved": True}
```

**Existing local-non-interactive-bucket closed (replace line 2707-2713 + 2764-2765)**:

```python
# F11 tick38 NEW: close the "local non-interactive → approved" hole
# Original code: 
#   if role == "local" and not is_gateway and not is_ask: return approved
# F11: role=="local" + no approver → flagged as autonomous → fail-closed (see above)
# Remove the original "local non-interactive returns approved" path entirely
```

### 2.2 tools/code_execution_tool.py 修改 (RPC dispatch per-call guard)

**Existing line 501 RPC dispatch modify**:

```python
# F11 tick38 NEW: per-call guard on RPC-dispatched sub-tool calls
# Original code:
#   def _dispatch_rpc(self, tool_name: str, args: dict):
#       return handle_function_call(tool_name, args)
# F11: per-call guard wrapper

from tools.approval import check_all_command_guards  # existing import

def _dispatch_rpc(self, tool_name: str, args: dict, context: RequestContext):
    """F11 invariant 2: per-call guard on every RPC-dispatched tool."""
    # Construct equivalent shell command for guard check
    if tool_name == 'terminal':
        cmd = args.get('command', '')
    elif tool_name == 'patch':
        # patch doesn't shell out, but verify path is allowed
        file_path = args.get('path', '')
        cmd = f"patch {file_path}"  # for DANGEROUS_PATTERNS match
    elif tool_name == 'write_file':
        file_path = args.get('path', '')
        cmd = f"write_file {file_path}"
    elif tool_name == 'read_file':
        file_path = args.get('path', '')
        cmd = f"read_file {file_path}"
    else:
        cmd = f"{tool_name} {args}"  # generic
    
    # F11 invariant 2: per-call guard (NOT just one-shot whole-script guard)
    guard_result = check_all_command_guards(cmd, context)
    if not guard_result.get('approved', False):
        raise PermissionError(
            f"F11 per-call guard blocked: {tool_name} → {guard_result.get('reason')}"
        )
    
    # Original dispatch
    return handle_function_call(tool_name, args)
```

**Existing line 69 RPC allowlist tighten (terminal → with per-call guard)**:

```python
# F11 tick38 NEW: RPC allowlist still allows terminal, but per-call guard enforces
# Original RPC_ALLOWED_TOOLS = frozenset({...,'terminal',...})
# F11: keep allowlist, add per-call guard (Invariant 2)
RPC_ALLOWED_TOOLS = frozenset({
    'terminal',  # still allowed but per-call guard
    'patch',
    'write_file',
    'read_file',
    'search_files',
    # ...
})
```

### 2.3 skills/research/research-paper-writing/references/experiment-patterns.md 修改

**Existing line 484 fix (document escape hatch closure)**:

```markdown
# F11 tick38 NEW: replace "execute_code is escape hatch" guidance

## Before (line 484, REMOVED):
> Security scan blocks | Commands can route through `execute_code` to bypass

## After (line 484, REPLACED):
> Security scan is mandatory on all paths. If a command is blocked by 
> DANGEROUS_PATTERNS (pipe-to-interpreter, VCS/remote-mutation, etc.), 
> do NOT route through `execute_code` to bypass. Instead:
> 1. Fix the command to avoid the dangerous pattern (e.g., avoid pipe-to-interpreter)
> 2. If the action is genuinely needed, request explicit human approval
> 3. `execute_code` enforces the same per-call guard pipeline as native tools
>    (F11 invariant 2); there is no softer path
```

### 2.4 core/supply_chain.py NEW (Invariant 4)

**New file (Tick38 新增)**:

```python
# F11 tick38 NEW: core/supply_chain.py
# Tool description sanitization + MCP supply chain 6-control (沿用 tick33 F7 立卡)

import re
import math
from collections import Counter

# F11 invariant 4: injection keyword detection in tool descriptions
INJECTION_KEYWORDS = [
    r"ignore\s+(previous|above|all)\s+(instructions|prompts?)",
    r"system\s+prompt\s+override",
    r"tool\s+override",
    r"hijack\s+(the\s+)?tool",
    r"<\|im_start\|>",  # chat template injection
    r"<\|im_end\|>",
]

def scan_mcp_description(description: str) -> dict:
    """F11 invariant 4: scan tool description for injection keywords."""
    flagged = []
    for pattern in INJECTION_KEYWORDS:
        if re.search(pattern, description, re.IGNORECASE):
            flagged.append(pattern)
    return {
        "safe": len(flagged) == 0,
        "flagged_patterns": flagged,
        "scan_version": "F11-v1",
    }


def perplexity_detection(tool_selection_probs: list[float]) -> dict:
    """F11 invariant 4: tool selection perplexity threshold (default 2.0)."""
    if not tool_selection_probs:
        return {"anomalous": False, "perplexity": 0.0}
    # Perplexity = exp(-mean(log(p)))
    log_sum = sum(math.log(max(p, 1e-10)) for p in tool_selection_probs)
    perplexity = math.exp(-log_sum / len(tool_selection_probs))
    return {
        "anomalous": perplexity > 2.0,
        "perplexity": perplexity,
        "threshold": 2.0,
    }


def known_answer_test(tool_call: dict, expected_outputs: list[str]) -> dict:
    """F11 invariant 4: known-answer test for tool selection."""
    actual = tool_call.get('selected_tool', '')
    matched = actual in expected_outputs
    return {
        "passed": matched,
        "actual": actual,
        "expected_count": len(expected_outputs),
    }


# F11 invariant 4: known-answer test coverage
KNOWN_ANSWER_TEST_CASES = [
    # ≥100 common queries, intentionally short — see references/f11_known_answer_tests.md
    # Format: (query, expected_tools)
    ("read file /tmp/x", ["read_file"]),
    ("list directory /tmp", ["terminal"]),
    ("search web for hermes", ["web_search"]),
    # ... ≥100 entries
]
```

## 3. Layer 2 (Audit log) — 主要实现层

### 3.1 Audit log fields (Invariant 5)

**core/audit.py NEW (or extend existing audit module)**:

```python
# F11 tick38 NEW: defense-in-depth audit log

import hashlib
import json
import time
from typing import Any

def audit_execute_code_block(code: str, context: dict) -> dict:
    """F11 invariant 5: SHA256 hash of incoming code block + runtime result."""
    code_sha = hashlib.sha256(code.encode('utf-8')).hexdigest()
    log_entry = {
        "event_type": "execute_code_block",
        "timestamp": time.time(),
        "code_sha256": code_sha,
        "code_length": len(code),
        "context_role": context.get('role'),
        "session_id": context.get('session_id'),
        "autonomous_session_flag": context.get('autonomous_session_flag', False),
        "scan_version": "F11-v1",
    }
    _write_audit_log(log_entry)
    return log_entry


def audit_sub_tool_calls(calls: list[dict], parent_code_sha: str) -> dict:
    """F11 invariant 5: log every sub-tool call within execute_code block."""
    log_entry = {
        "event_type": "execute_code_sub_tool_calls",
        "timestamp": time.time(),
        "parent_code_sha256": parent_code_sha,
        "sub_tool_count": len(calls),
        "sub_tool_list": [
            {
                "tool_name": c.get('tool_name'),
                "args_sha256": hashlib.sha256(
                    json.dumps(c.get('args', {}), sort_keys=True).encode()
                ).hexdigest(),
            }
            for c in calls
        ],
    }
    _write_audit_log(log_entry)
    return log_entry


def audit_github_pr_merge(
    pr_number: int,
    approver_role: str,
    session_id: str,
    risk_class: str,
    merge_commit_sha: str,
    is_bot_tag_set: bool,
) -> dict:
    """F11 invariant 5: GitHub PR merge audit log."""
    log_entry = {
        "event_type": "github_pr_merge",
        "timestamp": time.time(),
        "pr_number": pr_number,
        "approver_role": approver_role,
        "session_id": session_id,
        "risk_class": risk_class,
        "merge_commit_sha": merge_commit_sha,
        "is_bot_tag_set": is_bot_tag_set,
    }
    _write_audit_log(log_entry)
    if not is_bot_tag_set:
        # F11 invariant 5: misattribution defense
        raise RuntimeError(
            "F11 invariant 5: is_bot tag must be set when actor is agent session"
        )
    return log_entry
```

## 4. Layer 3 (Release gate) — 主要实现层

### 4.1 scripts/dangerous_command_unified_classify.py NEW

```python
#!/usr/bin/env python3
# F11 tick38 NEW: ship gate v8 dangerous_command_unified_classify
"""
Verify 4 invariants before allowing release:
1. VCS/remote-mutation commands in DANGEROUS_PATTERNS
2. execute_code RPC dispatch uses per-call guard
3. Session classification contains autonomous_session_flag
4. audit log contains approver role + session_id + risk_class
"""

import re
import sys
import subprocess
from pathlib import Path

REPO = Path("/root/NousResearch/hermes-agent")  # adjust path

def check_invariant_1() -> bool:
    """VCS/remote-mutation in DANGEROUS_PATTERNS."""
    approval_py = REPO / "tools/approval.py"
    if not approval_py.exists():
        return False
    content = approval_py.read_text()
    required_patterns = [
        r"gh\s+pr\s+merge",
        r"git\s+push\s+.*--force",
        r"git\s+branch\s+-D\b",
        r"gh\s+release\s+create",
    ]
    return all(re.search(p, content) for p in required_patterns)


def check_invariant_2() -> bool:
    """execute_code RPC dispatch uses per-call guard."""
    code_exec = REPO / "tools/code_execution_tool.py"
    if not code_exec.exists():
        return False
    content = code_exec.read_text()
    return (
        "check_all_command_guards" in content
        and "_dispatch_rpc" in content
        and "per_call_guard" in content.lower()
    )


def check_invariant_3() -> bool:
    """Session classification contains autonomous_session_flag."""
    approval_py = REPO / "tools/approval.py"
    if not approval_py.exists():
        return False
    content = approval_py.read_text()
    return (
        "_is_autonomous_session" in content
        and "HERMES_KANBAN_WORKER" in content
        and "HERMES_SUBAGENT" in content
    )


def check_invariant_4() -> bool:
    """audit log contains approver role + session_id + risk_class."""
    audit_py = REPO / "core/audit.py"
    if not audit_py.exists():
        return False
    content = audit_py.read_text()
    return all(
        field in content
        for field in ("approver_role", "session_id", "risk_class")
    )


def main():
    checks = {
        "invariant_1_vcs_remote_mutation": check_invariant_1,
        "invariant_2_rpc_per_call_guard": check_invariant_2,
        "invariant_3_autonomous_session_flag": check_invariant_3,
        "invariant_4_audit_log_fields": check_invariant_4,
    }
    results = {name: fn() for name, fn in checks.items()}
    print(json.dumps(results, indent=2))
    if not all(results.values()):
        print("F11 dangerous_command_unified_classify FAILED")
        sys.exit(1)
    print("F11 dangerous_command_unified_classify PASSED")


if __name__ == "__main__":
    main()
```

## 5. 测试用例 (dev layer verification)

**tests/tools/test_execute_code_approval_unification.py NEW**:

```python
# F11 tick38 NEW: 4 invariant unit + integration tests

import pytest
from tools.approval import check_execute_code_guard, _is_autonomous_session


class TestF11Invariant1VCSRemoteMutation:
    """VCS/remote-mutation class in DANGEROUS_PATTERNS."""
    
    @pytest.mark.parametrize("code,should_block", [
        ("gh pr merge 60 --squash --delete-branch", True),
        ("gh pr merge 60 --squash", True),
        ("git push --force origin main", True),
        ("git push -f origin main", True),
        ("git branch -D feature/foo", True),
        ("gh release create v1.0.0", True),
        ("gh api -X POST /repos/.../issues", True),
        ("ls -la", False),
        ("cat file.txt", False),
    ])
    def test_vcs_remote_mutation_blocked(self, code, should_block):
        result = check_execute_code_guard(code, context={"role": "local"})
        assert result["approved"] != should_block


class TestF11Invariant2RPCPerCallGuard:
    """execute_code RPC dispatch per-call guard."""
    
    def test_rpc_dispatch_blocks_dangerous_command(self):
        from tools.code_execution_tool import _dispatch_rpc
        with pytest.raises(PermissionError):
            _dispatch_rpc("terminal", {"command": "gh pr merge 60"}, context={...})


class TestF11Invariant3AutonomousSessionFlag:
    """autonomous_session_flag unification."""
    
    @pytest.mark.parametrize("env,expected", [
        ({"HERMES_CRON_SESSION": "1"}, True),
        ({"HERMES_KANBAN_WORKER": "1"}, True),
        ({"HERMES_KANBAN_NOTIFICATION": "1"}, True),
        ({"HERMES_SUBAGENT": "1"}, True),
        ({"role": "local"}, True),  # local non-interactive
        ({"HERMES_GATEWAY_SESSION": "1", "role": "gateway"}, False),
        ({}, False),
    ])
    def test_autonomous_flag(self, env, expected):
        assert _is_autonomous_session(env) == expected
    
    def test_local_non_interactive_bucket_closed(self):
        # F11 invariant 3: close the "local non-interactive → approved" hole
        result = check_execute_code_guard(
            "print('hello')",
            context={"role": "local", "env": {}}
        )
        assert result["approved"] is False
        assert result["reason"] == "autonomous_session_fail_closed"


class TestF11Invariant5AuditLog:
    """defense-in-depth audit log fields."""
    
    def test_execute_code_block_sha256_logged(self):
        from core.audit import audit_execute_code_block
        entry = audit_execute_code_block("print('x')", {"role": "local"})
        assert "code_sha256" in entry
        assert len(entry["code_sha256"]) == 64  # SHA256 hex
    
    def test_github_pr_merge_audit_required_fields(self):
        from core.audit import audit_github_pr_merge
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
```

## 6. dev layer 验收清单

- [ ] DANGEROUS_PATTERNS_VCS_REMOTE_MUTATION 段 insert to tools/approval.py
- [ ] _is_autonomous_session function added to tools/approval.py
- [ ] check_execute_code_guard fail-closed path 替换
- [ ] tools/code_execution_tool.py _dispatch_rpc per-call guard wrapper
- [ ] experiment-patterns.md:484 文档改写
- [ ] core/supply_chain.py NEW (scan_mcp_description + perplexity + known_answer)
- [ ] core/audit.py audit_execute_code_block / audit_sub_tool_calls / audit_github_pr_merge
- [ ] scripts/dangerous_command_unified_classify.py NEW
- [ ] tests/tools/test_execute_code_approval_unification.py NEW (4 invariant tests)
- [ ] All tests pass
- [ ] dangerous_command_unified_classify.py exit 0
- [ ] 不动 cron/control plane (硬红线)
- [ ] cross-profile audit (5 profile × 4 file path = 20 verify points)

## 7. dev layer 等 user ack 后

1. 等 user ack SOUL_chief + SOUL_pm 后再动代码 (沿用 5 SOUL 配额 + 不写控制平面硬红线)
2. dev 草案仅作 implementation reference,等 chief 6h dedup PR 选定后再合并
3. tick39 audit verify dev 改动是否落地

## 8. 关联 PR 决策

- **#60077 (izumi0uu,5 commits,2026-07-07)**:含 Invariant 1+2+3 部分 — primary candidate
- **#60799 (embwl0x,1 commit,2026-07-08)**:含 Invariant 1+3 部分 — secondary candidate
- **#24942 (LifeJiggy,2026-06-09 closed unmerged)**:Phase 1 hardening attempted;含部分 Invariant 3 (container bypass removal) — 历史 evidence

chief 6h dedup 应选 #60077 作 primary (5 commits 覆盖更广),但 #60077 漏 Invariant 5 audit log;chief 必须在 6h 内追加 follow-up PR 含 Invariant 5。

## 9. 状态机 (5-state extension 沿用 tick37)

#60056 当前:**open P2 待升级 P1** + #60077 + #60799 双 PR open — `implementation_pending`

升级路径:
1. 触发 user ack chief/pm/dev 草案 → chief 6h dedup → 选 #60077 primary
2. merge #60077 → close #60056 → `release_verify_pending`
3. v0.18.3+ ship 含 #60077 SHA → `closed_merged_no_artifact`
4. 76-check ship gate + 5 install profile verify → `closed_merged_artifact_verified`
5. 14d regression window no regression → `fixed`