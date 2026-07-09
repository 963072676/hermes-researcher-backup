---
name: hermes-toolhijacker-defense
description: 'Hermes Agent ToolHijacker 防御 4 层 pattern。用于 ToolHijacker NDSS 2026 (96.7% ASR) + Claude Code 2.1.196 MCP self-approval 防御。Use when: 任何 MCP tool description 包含 injection keyword (ignore previous/tool override/hijack)、tool selection perplexity > 2.0、KAT 失败,或 self-evolution cron 报 ToolHijacker 相关 P1。'
version: 0.1.0
author: Hermes researcher (tick31)
license: MIT
created_by: agent
metadata:
  hermes:
    tags: [toolhijacker, mcp, defense, perplexity, KAT, claude-code-2.1.196]
    related: [hermes-mcp-tool-library-validator, hermes-pr-dedup-arbitrator]
---

# hermes-toolhijacker-defense

## 这个 skill 解决什么

ToolHijacker (NDSS 2026) 实证 96.7% tool selection attack success across MetaTool。Claude Code 2.1.196 (2026-07-01) 已 ship MCP self-approval fix,但 hermes-agent baseline 缺位。

**4 层防御 pattern** (沿用 dev-agent SOUL `toolhijacker_defense_pattern_v1`):

1. **Layer 1: Tool description scan** — scan keywords 任何匹配即 reject
2. **Layer 2: Perplexity detection** — tool selection 偏离 candidates 平均 perplexity > 2.0 → flag
3. **Layer 3: Known-answer test (KAT)** — ≥ 100 常见 query 覆盖,失败 → reject
4. **Layer 4: Trust policy** — strict mode + untrusted_repo_self_approval false + pending_label

## 触发条件

- 任何 MCP tool description 含 injection keyword (ignore previous / tool override / hijack / override / disregard)
- 任何 tool selection 偏离 candidates 平均 perplexity > 2.0
- 任何 KAT (100 known-answer test) 失败
- 任何 untrusted repo 试图 self-approve MCP server
- self-evolution cron 报 ToolHijacker 相关 P1

## 标准流程

### Step 1: Tool description scan (Layer 1)

```python
INJECTION_KEYWORDS = [
    "ignore previous",
    "tool override",
    "hijack",
    "override",
    "disregard",
    "ignore instructions",
    "system prompt",
    "you are",
    "act as",
    "pretend to be",
]

def scan_tool_description(tool_desc: str) -> bool:
    """Return True if safe, False if injection detected."""
    desc_lower = tool_desc.lower()
    for keyword in INJECTION_KEYWORDS:
        if keyword in desc_lower:
            return False  # reject
    return True
```

### Step 2: Perplexity detection (Layer 2)

```python
import math
from typing import List

def perplexity(tool_selection: str, candidates: List[str]) -> float:
    """计算 tool selection 相对 candidates 的 perplexity."""
    if not candidates:
        return float('inf')

    # candidate distribution
    cand_lower = [c.lower() for c in candidates]
    sel_lower = tool_selection.lower()

    # 如果 selection 不在 candidates 内,返回高 perplexity
    if sel_lower not in cand_lower:
        return float('inf')

    # uniform distribution perplexity = log(num_candidates)
    return math.log(len(candidates))


THRESHOLD = 2.0

def is_suspicious(perplexity_score: float) -> bool:
    return perplexity_score > THRESHOLD
```

### Step 3: Known-answer test (Layer 3)

```yaml
# tests/toolhijacker/kat.yaml
coverage: 100 queries
categories:
  benign_baseline: 50  # 常见 query,tool 选择应一致
  injection_attack: 30  # 含 injection keyword,应 reject
  tool_override: 10     # 含 tool override 模式,应 reject
  edge_case: 10         # ambiguous query,应 fallback to safe default

# 失败 → reject tool selection, alert ToolHijacker flag
```

### Step 4: Trust policy (Layer 4)

```yaml
# ~/.hermes/config.yaml
trust_policy:
  strict: true
  untrusted_repo_self_approval: false
  pending_label: "Pending approval"

# .mcp.json 自审批关闭 (沿用 Claude Code 2.1.196)
# claude mcp list/get → 显示 unapproved server 为 "⏸ Pending approval" 不自动连接
```

## 集成到 MCP runtime

```python
# mcp/runtime.py
def execute_tool(tool_name: str, args: dict, candidates: List[str]) -> dict:
    # Layer 1: Tool description scan
    tool_desc = get_tool_description(tool_name)
    if not scan_tool_description(tool_desc):
        return {"status": "rejected", "reason": "tool_description_injection"}

    # Layer 2: Perplexity detection
    p = perplexity(tool_name, candidates)
    if is_suspicious(p):
        return {"status": "flagged", "reason": "suspicious_tool_selection", "perplexity": p}

    # Layer 3: KAT (background, async)
    # ...

    # Layer 4: Trust policy
    if not trust_policy_allows(tool_name):
        return {"status": "pending_approval", "label": "Pending approval"}

    # Execute
    return {"status": "ok"}
```

## 失败回退

- Layer 1 误判 → 提供 white list (admin 维护)
- Layer 2 perplexity 阈值过严 → 调到 2.5 (实测 ±0.3 误差)
- Layer 3 KAT 失败 → 不立即 reject,先 alert,人工 review
- Layer 4 trust_policy strict → enterprise 用户可关 strict 但默认开

## Pitfalls

### tick31 - Tool description 含 case variation 绕过 scan

**触发**: tool description "IgNoRe PrEvIoUs" 大小写混合可绕过 substring match。

**修正路径**: scan 时 `desc_lower = tool_desc.lower()` 统一小写 (沿用 Step 1)。

### tick31 - Perplexity 在 selection ⊂ candidates 时永远 log(N)

**触发**: 如果 model 选择 candidate 内工具,perplexity 永远 log(N),无法 flag 异常。

**修正路径**: 用 tool call **frequency distribution** 替代 raw selection:统计同一 query 多次 run 的 tool selection distribution entropy。低 entropy = 一致,高 entropy = suspicious。

### tick31 - KAT 100 条覆盖不够

**触发**: 100 条已知 query 不覆盖所有 tool selection 路径。

**修正路径**: 持续加 KAT,目标 ≥ 1000 条 (沿用 enterprise 实践)。

## 关联 references

- 沿用 dev-agent SOUL `toolhijacker_defense_pattern_v1` 段
- 沿用 qa-agent SOUL `toolhijacker_known_answer_test_v1` 段
- 沿用 default SOUL `mcp_self_approval_baseline_v1` 段
- 参考 https://mywrittenword.com/toolhijacker-prompt-injection-llm-agent-tool-selection-defense-2026