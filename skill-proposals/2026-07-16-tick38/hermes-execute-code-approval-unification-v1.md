---
name: hermes-execute-code-approval-unification-v1
description: 'F11 execute-code-approval-unification-deck 的统一 approval 防线。沿用 tick33 F7 MCP supply chain 6-control + tick35 F10 install handoff readiness + tick38 F11 invariants。Use when: cron worker 看到 execute_code block / kanban-spawned session / subagent RPC dispatch 时,自动 run 9 verify point (VCS deny + RPC guard + autonomous flag + audit log fields + EXT14 shield + version pin + argument injection detector + tool spawn analyzer + known-answer test)。'
version: 1.0.0
author: Hermes Agent (researcher profile, tick38)
license: MIT
created_by: agent
platforms: [linux, macos]
metadata:
  hermes:
    tags: [cron, security, approval-unification, F11, autonomous-session-flag, audit-log, dangerous-command]
    related: [hermes-researcher-self-evolution-v1, hermes-cron-ticker-resilience-deck, hermes-mcp-supply-chain-6-control, hermes-launchd-supervisor-ownership-preserver-v1]
---

# hermes-execute-code-approval-unification-v1

> Tick38 立卡 (2026-07-16)。F11 第 11 family 实战 skill。
> 触发:#60056 (autonomous agent merged prod PR with no consent) + PR #60077/#60799 PR-dedup fire + unmerged #24942 Phase 1 hardening evidence。
> 沿用:tick27 silent-fail + tick28 cross-platform-state + tick31 memory-injection / credential-pool + tick33 cron-ticker / MCP-supply-chain 6-control + tick34 session-state-integrity + tick35 cron-installer-handoff + cross-cluster arrows + trust boundary 5 categories + tick37 post-rediscovery + 17-field v5 acceptance。

## 1. 这个 skill 解决什么

tick37 之前的安全防线都从单一方向看:
- F7 MCP supply chain:tool description sanitization
- F8 cron-ticker resilience:BaseException catch + heartbeat
- F10 installer-handoff:HERMES_HOME / raw_config_version
- F9 session-state integrity:lock + provenance

但 **#60056 暴露的根因是 execute_code approval 路径上的结构性缺陷**:
1. **VCS/remote-mutation commands 不在 DANGEROUS_PATTERNS** — `gh pr merge --delete-branch` 走 auto-approved path
2. **execute_code 是 documented escape hatch** — `experiment-patterns.md:484` literally says "can route through execute_code"
3. **kanban-spawned autonomous session 落 "local non-interactive → approved" bucket** — `approval.py:2707-2713, 2764-2765` 没 fail-closed

**9 verify point 统一防御**:
1. VCS/remote-mutation deny list (DANGEROUS_PATTERNS_VCS_REMOTE_MUTATION)
2. execute_code RPC per-call guard (code_execution_tool.py:501 wrapper)
3. autonomous_session_flag (cron / kanban / subagent / notification / local non-interactive)
4. audit log fields (approver_role + session_id + risk_class + commit_sha + is_bot)
5. EXT14 cancellation-probe shield (沿用 F7 control 7)
6. MCP server version pin (CVE-2026-61459 ≥3.9.0 + CVE-2026-59950 ≥1.28.1)
7. Tool spawn static analyzer (argument injection detection)
8. Perplexity detection + known-answer test (沿用 F7 control 6)
9. Tirith pipe scan (curl|sh / npx|bash / wget|bash / |python3 -c)

## 2. 何时调用

任何 cron worker 看到以下信号**立即调用**:
- issue label 集合 ∩ {`tool/code-exec`, `area/auth`, `sweeper:risk-security-boundary`} ≥ 1
- P1 cluster 含 `execute_code` 或 `kanban-spawned` 关键字
- GitHub search `repo:NousResearch/hermes-agent "execute_code" "approval"` 新命中
- 任意 cron 跑 `terminal` / `patch` / `write_file` / `read_file` sub-tool call
- F7/F8/F10/F11 任一 family 新 evidence 触发 cross-cluster arrow 评估

## 3. 标准流程

### Step 1: VCS/remote-mutation deny list check

```bash
# 检查 tools/approval.py DANGEROUS_PATTERNS 是否含 VCS class
python3 -c "
import re
from pathlib import Path
approval = Path('/root/NousResearch/hermes-agent/tools/approval.py').read_text()
required = [
    r'gh\s+pr\s+merge',
    r'gh\s+pr\s+merge\s+.*--delete-branch',
    r'gh\s+release\s+create',
    r'git\s+push\s+.*--force',
    r'git\s+push\s+.*--force-with-lease',
    r'git\s+branch\s+-D\b',
    r'git\s+push\s+.*--delete',
    r'gh\s+api\s+.*-X\s+(POST|PUT|DELETE|PATCH)\b',
]
for p in required:
    if not re.search(p, approval):
        print(f'FAIL: missing pattern {p}')
        break
else:
    print('PASS: VCS/remote-mutation in DANGEROUS_PATTERNS')
"
```

### Step 2: execute_code RPC per-call guard check

```bash
# 检查 tools/code_execution_tool.py 是否对 RPC dispatch 加 per-call guard
python3 -c "
from pathlib import Path
code = Path('/root/NousResearch/hermes-agent/tools/code_execution_tool.py').read_text()
required = [
    '_dispatch_rpc',
    'check_all_command_guards',
    'per_call_guard',
]
for r in required:
    if r not in code:
        print(f'FAIL: missing {r}')
        break
else:
    print('PASS: execute_code RPC per-call guard')
"
```

### Step 3: autonomous_session_flag check

```bash
# 检查 tools/approval.py 是否含 _is_autonomous_session
python3 -c "
from pathlib import Path
approval = Path('/root/NousResearch/hermes-agent/tools/approval.py').read_text()
required = [
    '_is_autonomous_session',
    'HERMES_CRON_SESSION',
    'HERMES_KANBAN_WORKER',
    'HERMES_KANBAN_NOTIFICATION',
    'HERMES_SUBAGENT',
]
for r in required:
    if r not in approval:
        print(f'FAIL: missing {r}')
        break
else:
    print('PASS: autonomous_session_flag')
"
```

### Step 4: audit log fields check

```bash
# 检查 core/audit.py 是否含 approver_role + session_id + risk_class
python3 -c "
from pathlib import Path
audit_path = Path('/root/NousResearch/hermes-agent/core/audit.py')
if not audit_path.exists():
    print('FAIL: core/audit.py not found')
    exit(1)
audit = audit_path.read_text()
required = ['approver_role', 'session_id', 'risk_class', 'is_bot_tag_set']
for r in required:
    if r not in audit:
        print(f'FAIL: missing {r}')
        break
else:
    print('PASS: audit log fields')
"
```

### Step 5: EXT14 cancellation-probe shield check

```bash
# 检查 MCP server notification handler 是否防御 EXT14
python3 -c "
from pathlib import Path
handler_path = Path('/root/NousResearch/hermes-agent/core/mcp/notification_handler.py')
if not handler_path.exists():
    print('FAIL: notification_handler.py not found')
    exit(1)
handler = handler_path.read_text()
# F11 control 7: 必须 if request_id is None: return
if 'notifications/cancelled' in handler and 'if request_id is None' in handler:
    print('PASS: EXT14 cancellation-probe shield')
else:
    print('FAIL: EXT14 shield missing')
"
```

### Step 6: MCP server version pin check

```bash
# 检查 mcp Python SDK >= 1.28.1 (CVE-2026-59950)
python3 -c "import mcp; print('mcp version:', mcp.__version__)" | {
    read -r line
    version=$(echo "$line" | awk '{print $3}')
    if [ "$(printf '%s\n' '1.28.1' "$version" | sort -V | head -n1)" = '1.28.1' ]; then
        echo "PASS: mcp $version >= 1.28.1"
    else
        echo "FAIL: mcp $version < 1.28.1 (CVE-2026-59950)"
    fi
}
```

### Step 7: Tool spawn static analyzer check

```bash
# 检查 core/mcp/tool_spawn_analyzer.py 是否含 argument injection detection
python3 -c "
from pathlib import Path
analyzer_path = Path('/root/NousResearch/hermes-agent/core/mcp/tool_spawn_analyzer.py')
if not analyzer_path.exists():
    print('FAIL: tool_spawn_analyzer.py not found')
    exit(1)
analyzer = analyzer_path.read_text()
required = ['leading_dash_injection', 'kubectl_server_redirect', 'shell_wrapper']
for r in required:
    if r not in analyzer:
        print(f'FAIL: missing {r}')
        break
else:
    print('PASS: tool spawn analyzer')
"
```

### Step 8: Perplexity detection + known-answer test

```bash
# 沿用 F7 control 6 (hermes-mcp-supply-chain-6-control skill)
python3 -c "
from pathlib import Path
supply_path = Path('/root/NousResearch/hermes-agent/core/supply_chain.py')
if not supply_path.exists():
    print('FAIL: core/supply_chain.py not found')
    exit(1)
supply = supply_path.read_text()
required = ['perplexity', 'known_answer', 'scan_mcp_description']
for r in required:
    if r not in supply:
        print(f'FAIL: missing {r}')
        break
else:
    print('PASS: perplexity + known-answer')
"
```

### Step 9: Tirith pipe scan check

```bash
# 沿用 F7 control 5
python3 -c "
from pathlib import Path
core_path = Path('/root/NousResearch/hermes-agent/core/security.py')
if not core_path.exists():
    print('WARN: core/security.py not found, skip')
    exit(0)
core = core_path.read_text()
required = ['curl|sh', 'npx|bash', 'wget|bash', '|python3 -c']
for r in required:
    if r not in core:
        print(f'FAIL: missing tirith pattern {r}')
        break
else:
    print('PASS: tirith pipe scan')
"
```

## 4. 9 verify point 综合判定

```python
def run_execute_code_approval_unification_v1():
    """Tick38立卡 F11 9 verify point check."""
    results = {}
    
    # Step 1-4: VCS deny + RPC guard + autonomous flag + audit log
    results['step_1_vcs_deny'] = check_vcs_remote_mutation_in_dangerous_patterns()
    results['step_2_rpc_per_call_guard'] = check_execute_code_rpc_per_call_guard()
    results['step_3_autonomous_session_flag'] = check_autonomous_session_flag()
    results['step_4_audit_log_fields'] = check_audit_log_fields()
    
    # Step 5-7: MCP supply chain v2 (EXT14 + version pin + analyzer)
    results['step_5_ext14_shield'] = check_ext14_cancellation_probe_shield()
    results['step_6_mcp_version_pin'] = check_mcp_server_version_pin()
    results['step_7_tool_spawn_analyzer'] = check_tool_spawn_static_analyzer()
    
    # Step 8-9: 沿用 F7 control 5+6
    results['step_8_perplexity_known_answer'] = check_perplexity_known_answer_test()
    results['step_9_tirith_pipe_scan'] = check_tirith_pipe_scan()
    
    failed = [k for k, v in results.items() if not v]
    return {
        'passed': len(results) - len(failed),
        'total': len(results),
        'failed_steps': failed,
        'all_passed': len(failed) == 0,
    }
```

## 5. 失败回退

- Step 1 (VCS deny) 失败 → critical (立即升级 chief + 飞书报警)
- Step 2 (RPC per-call guard) 失败 → critical (立即升级 chief)
- Step 3 (autonomous session flag) 失败 → critical (立即升级 chief)
- Step 4 (audit log fields) 失败 → high (升级 pm 走 acceptance v6)
- Step 5 (EXT14 shield) 失败 → critical (CVE-2026-61459 等同类风险)
- Step 6 (version pin) 失败 → critical (CVE-2026-61459 + 59950 直接中招)
- Step 7 (tool spawn analyzer) 失败 → high (CVE-2026-61459 argument injection)
- Step 8 (perplexity/known-answer) 失败 → medium (沿用 F7 control 6)
- Step 9 (tirith pipe scan) 失败 → medium (沿用 F7 control 5)

## 6. 配额与运行频率

- **运行频率**:每日 cron tick 必跑 (沿用 tick37 post-rediscovery verification window)
- **运行成本**:9 step × ~50ms = 450ms (低开销)
- **失败升级**:任何 step 失败立即升级 chief + 飞书推送

## 7. 关联 references / skills

- `hermes-researcher-self-evolution-v1` (主 skill)
- `hermes-mcp-supply-chain-6-control` (F7,沿用 control 5+6)
- `hermes-cron-ticker-resilience-deck` (F8,沿用 ticker health check)
- `hermes-launchd-supervisor-ownership-preserver-v1` (tick37 立卡,F9 launchd orphan)
- `hermes-post-merge-regression-window-guard-v1` (tick37 立卡,14d window)
- `hermes-mcp-2026-07-28-final-readiness-v1` (tick37 立卡,readiness v1 升级到 v2)
- `references/F11-execute-code-approval-deny-list.md` (VCS deny 详细 pattern)
- `references/F11-autonomous-session-flag-patterns.md` (4 类 autonomous session 实战模式)

## 8. Pitfalls (持续追加)

### tick 38 - Step 1 VCS deny 不能 grep simple pattern 而要 AST parse
**触发**:tick38 第一次跑 step 1 用 `grep -E "gh.*merge"` 返回 PASS,但实际 DANGEROUS_PATTERNS 在 line 588 是 python list 形式 `r"gh\s+pr\s+merge"`,grep 命中的是其他注释里的"gh pr merge"字面。

**修正路径**:
1. 必须 read tools/approval.py 的 DANGEROUS_PATTERNS list,逐项 verify regex match
2. 用 `python3 -c "import re; ...; re.search(pattern, content)"` 精确判断
3. 不要 fallback 到 grep(变量名 / 注释字面会误命中)

### tick 38 - Step 3 autonomous_session_flag 必须用 env field 不是 role field
**触发**:tick38 第一次跑 step 3 用 `role == "local"` 判定,实际 `_is_autonomous_session` 必须 check env dict 里的 HERMES_CRON_SESSION / HERMES_KANBAN_WORKER 等,**不是 role 字段**。

**修正路径**:
1. check env dict (env.get('HERMES_CRON_SESSION') == '1') 不是 role
2. role 字段可能 misleading (role='local' 但 env='HERMES_KANBAN_WORKER=1' 必须 flagged)
3. test 必须 parametrize env dict 多场景,不能只测 role

### tick 38 - Step 5 EXT14 shield 不能只看 notification_handler,还要看 stdio transport
**触发**:tick38 第一次跑 step 5 只 check `core/mcp/notification_handler.py` 含 `if request_id is None: return`,实际 STDIO transport 的 read loop 也可能 raise exception,需双重防御。

**修正路径**:
1. STDIO transport read loop 加 try/except KeyError → log + return
2. notification_handler 加 3-line defensive code (沿用 cobalto-sec advisory)
3. test 必须 simulate 37-byte malformed payload (notifications/cancelled + missing requestId)