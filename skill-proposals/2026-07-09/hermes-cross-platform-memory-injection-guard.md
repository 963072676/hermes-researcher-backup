---
name: hermes-cross-platform-memory-injection-guard
description: 'Hermes Agent cross-platform memory injection guard implementation skill。用于 #40170 + #40967 (wiring missing) + #41003 family 立卡。Use when: 任何 customer-facing gateway (telegram/discord/slack/whatsapp/signal/matrix) 部署需要防止 Honcho memory 自动注入 user-facing prompt,或在 PR review 时识别 _skip_memory_injection wiring 缺失的 fix PR。'
version: 0.1.0
author: Hermes researcher (tick31)
license: MIT
created_by: agent
metadata:
  hermes:
    tags: [memory-injection, cross-platform, gateway, security, v0.18.2]
    related: [hermes-pr-dedup-arbitrator, hermes-mcp-tool-library-validator, hermes-installer-post-install-smoke]
---

# hermes-cross-platform-memory-injection-guard

## 这个 skill 解决什么

tick31 立卡 family `memory-injection-cross-platform`(NEW),与 tick28 `cross-platform-state` family 并列但 root cause 不同。

**关键观察**:
- #40170 (2026-06-07) Honcho memory leak on customer-facing gateways (WhatsApp/Telegram/Discord/Slack/Signal/Matrix)
- #40967 (closed 2026-06-07) fix PR **wired but wiring missing** — 仅含 guard check,无 platform detection logic
- #41003 follow-up: 必须含完整 diff (gateway/run.py L12713 platform detection)
- 30d ≥ 1 hit → 跨 platform ≥ 2 platform 同时中招 → 新立卡 family

**核心缺陷**:
1. `agent._skip_memory_injection` 默认 False
2. `getattr(agent, "_skip_memory_injection", False)` 永远返回 False
3. memory prefetch 路径不区分 CLI/cron session 和 customer-facing gateway session

## 触发条件

- cron worker 自检时发现 PR 含 `_skip_memory_injection` 但 wiring 缺失
- chief 触发 6h SLA dedup,fix PR 涉及 memory injection 路径
- qa 跑 cross-platform memory injection 60 test 失败
- self-evolution cron 看到新立卡 `memory-injection-cross-platform` family

## 标准流程

### Step 1: 验证 PR 是否含完整 wiring

```bash
PR_NUMBER=$1
gh pr view $PR_NUMBER --json files,title,body

# 必查 3 处
gh pr diff $PR_NUMBER -- agent/memory_manager.py  # guard check
gh pr diff $PR_NUMBER -- agent/agent_init.py     # injection 路径
gh pr diff $PR_NUMBER -- gateway/run.py          # platform detection wiring
```

### Step 2: 实施完整 guard

```python
# agent/memory_manager.py (guard check)
def memory_provider_tools_enabled(agent):
    if getattr(agent, "_skip_memory_injection", False):
        return False
    if agent.enabled_toolsets is None:
        return True
    if "memory" in agent.enabled_toolsets:
        return True
    return False

# gateway/run.py (platform detection wiring)
CUSTOMER_FACING_PLATFORMS = {
    "telegram", "discord", "slack",
    "whatsapp", "signal", "matrix"
}

def instantiate_agent(platform_key: str):
    agent = AIAgent(...)
    if platform_key in CUSTOMER_FACING_PLATFORMS:
        agent._skip_memory_injection = True
    return agent

# agent/agent_init.py (injection 路径)
def inject_memory_provider_tools(agent):
    if not memory_provider_tools_enabled(agent):
        return
    # ... existing injection logic
```

### Step 3: 60 test 验证 (6 platform × 10 case)

沿用 qa-agent SOUL `cross_platform_memory_injection_test_v1` 段:
- test_1_prefetch_trigger (首次 turn / session resume / 命令重启)
- test_2_cache_path (memory.read 是否被屏蔽)
- test_3_direct_call (用户 session memory.read 直接调用)
- test_4_cross_session (cross-session 注入防御)
- test_5_malicious_write (malicious memory write detection)
- test_6_operator_isolation (operator-level memory isolation)
- test_7_tool_available (memory.read / memory.write 工具仍可用)
- test_8_no_cached_prompt (customer-facing prompt 不含 cached context)
- test_9_multi_turn_persistence (multi-turn session memory persistence)
- test_10_session_cleanup (session cleanup cache invalidation)

### Step 4: regression 防御

- 任何 PR 含 `_skip_memory_injection` 但 diff 不含 gateway/run.py → reject
- chief dedup 决议必须 explicit 标 "wiring verified"
- cross-platform smoke test runner 必须 pass

## 评分模板 (per PR candidate)

```yaml
pr_candidate:
  number: #X
  files_modified:
    - agent/memory_manager.py: yes/no  # guard check
    - agent/agent_init.py: yes/no      # injection 路径
    - gateway/run.py: yes/no           # platform detection wiring (REQUIRED)
    - tests/agent/test_skip_memory_injection_guard.py: yes/no
  scores:
    wiring_complete: 0-3  # 0=wiring missing, 3=完整 3 处
    platform_coverage: 0-3  # 0=0 platform, 3=6 platform
    test_coverage: 0-3
    rollback_safety: 0-3
  decision: primary | non_primary | reject
  rationale: "reasoning"
```

## 失败回退

- gh CLI 不可用 → 用 git log + manual file inspect
- wiring 缺失 → 立即 reject PR,要求补 diff
- 60 test 失败 → 不允许 ship,要求回归
- rollback safety 缺失 → 标记 P1 (默认 False)

## Pitfalls

### tick31 - #40967 closed 但 wiring missing

**触发**: #40967 PR body 描述 `gateway/run.py` 应有 platform detection,但 diff 不含。`_skip_memory_injection` 永远 False,vulnerability 未修。

**修正路径**: review 时必查 3 处文件 (memory_manager / agent_init / gateway_run),任何 PR 缺 wiring 即 reject。

### tick31 - 60 test 框架需 mock 6 platform

**触发**: 真实 6 platform 部署成本高,QA 必须用 mock。

**修正路径**: 用 hermes gateway mock 框架 (沿用 qa-agent SOUL) 模拟 6 platform,跑 60 test。

## 关联 references

- 沿用 qa-agent SOUL `cross_platform_memory_injection_test_v1` 段
- 沿用 dev-agent SOUL `cross_platform_memory_injection_guard_v1` 段
- 沿用 chief-agent SOUL `memory_injection_cross_platform_v1` family 立卡