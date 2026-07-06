---
name: hermes-mcp-self-approval-baseline
description: 'MCP self-approval baseline(参照 Claude Code 2.1.196)+ ToolHijacker 防御。当用户提到"MCP 自审批" / "tool selection attack" / "Claude Code MCP security" 或 default profile 安全 verify 时使用。本 skill 输出 MCP baseline 模板 + ToolHijacker 防御 checklist + hermes-agent 跟进建议。'
version: 1.0.0
author: Hermes Agent (researcher profile)
license: MIT
created_by: agent
platforms: [linux, macos]
metadata:
  hermes:
    tags: [mcp, security, baseline, claude-code-2.1.196, toolhijacker]
    related: [hermes-researcher-self-evolution-v1, hermes-self-evolution-daily-digest, hermes-hardening-wave-verify]
---

# hermes-mcp-self-approval-baseline (tick28+ 立卡)

## 触发条件
- 用户 / cron 提到"MCP 自审批" / "tool selection attack" / "Claude Code MCP security"
- default profile 安全 baseline verify
- hermes-agent upstream 计划跟进 Claude Code 2.1.196 模式
- ToolHijacker 类研究 / 防御需求

## 解决什么
tick28 观察到:
1. **Claude Code 2.1.196 (2026-07-01) MCP self-approval fix** — `claude mcp list/get` 不再 spawn repo-self-approved `.mcp.json` servers,untrusted workspaces 标 "Pending approval"
2. **ToolHijacker arXiv NDSS 2026** — 96.7% tool selection attack success rate across MetaTool / Llama-3.3-70B shadow LLM + GPT-4o target
3. **hermes-agent 当前状态** — MCP trust surface 与 Claude Code 类似,但 baseline verify 缺位

本 skill 把这两个外部 reference 整合为 hermes-agent default profile 的 MCP baseline,涵盖:
- MCP server 自审批禁用(untrusted repo)
- Tool library injection 防御
- Tool selection perplexity 检测

## 标准流程 (6 步)

### Step 1: MCP config baseline
```yaml
# ~/.hermes/profiles/default/mcp/config.yaml (建议模板)
mcp:
  # 1. untrusted repo MCP 自审批禁用(参照 Claude Code 2.1.196)
  trust_policy:
    mode: strict  # strict | permissive
    untrusted_repo_self_approval: false  # 默认 false,untrusted repo 的 .mcp.json 必须 user 显式 approve
    pending_label: "Pending approval"
  
  # 2. Remote Control 绑定(参照 Claude Code 2.1.196)
  remote_control:
    bind_to_known_host_only: true
    allowed_hosts: ["localhost", "127.0.0.1"]
    reject_redirected_base_url: true
  
  # 3. MCP stdio subprocess lifecycle(参照 hermes-agent #59705)
  subprocess:
    reap_on_gateway_shutdown: true
    reap_on_cron_shutdown: true
    timeout_seconds: 60
```

### Step 2: Tool library injection 防御(参照 ToolHijacker)
```python
# ~/.hermes/profiles/default/mcp/tool_library_validator.py
import json
from pathlib import Path

class ToolLibraryValidator:
    """验证 tool library 不含未 verify 的 injection"""
    
    def __init__(self, tool_dir):
        self.tool_dir = Path(tool_dir)
    
    def validate(self):
        for tool_file in self.tool_dir.rglob("*.json"):
            tool = json.load(open(tool_file))
            # 检查 tool description 不含 override / hijack 类指令
            desc = tool.get("description", "").lower()
            bad_keywords = [
                "ignore previous", "disregard prior", "instead do",
                "tool substitution", "tool override", "hijack",
            ]
            for kw in bad_keywords:
                if kw in desc:
                    raise ValueError(f"tool {tool_file} description contains injection keyword: {kw}")
        return True
```

### Step 3: Tool selection perplexity detection
```python
# ~/.hermes/profiles/default/mcp/tool_selection_validator.py
import math
from collections import Counter

def perplexity(text):
    """计算 text 的 perplexity,异常高 = 可能是 injection"""
    # 简化版: 用 token 频率计算
    tokens = text.split()
    freq = Counter(tokens)
    total = len(tokens)
    entropy = -sum((c/total) * math.log2(c/total) for c in freq.values())
    return 2 ** entropy

def is_tool_selection_suspicious(candidates, selected, threshold=2.0):
    """检测 selected tool 是否在 perplexity 上显著偏离 candidates"""
    cand_perp = [perplexity(c['description']) for c in candidates]
    sel_perp = perplexity(selected['description'])
    avg_cand = sum(cand_perp) / len(cand_perp)
    return abs(sel_perp - avg_cand) > threshold
```

### Step 4: known-answer detection(参照 ToolHijacker 防御段)
```python
# known-answer test: 给定固定 query, 期望 tool selection 是确定的
KNOWN_ANSWERS = {
    "查询天气": "weather_lookup",
    "发送邮件": "send_email",
    "搜索文件": "file_search",
    # ... 覆盖 100+ 常见 query
}

def known_answer_test(query, selected_tool, candidates):
    """若 selected_tool 不在 candidates → fail;若 selected_tool 与 known answer 不符 → fail"""
    if selected_tool not in [c['name'] for c in candidates]:
        return False, "selected tool not in candidates"
    expected = KNOWN_ANSWERS.get(query)
    if expected and expected != selected_tool:
        return False, f"selected tool {selected_tool} != expected {expected}"
    return True, "OK"
```

### Step 5: hermes-agent 跟进建议
1. **PR 跟踪**: hermes-agent 是否已有 PR 跟进 Claude Code 2.1.196 的 MCP self-approval 模式? 跟踪 GitHub issues `is:open label:area/auth mcp`
2. **sandbox.credentials 参考**: Claude Code 2.1.187 sandbox.credentials 阻止 sandboxed commands 读 credential 文件 — hermes-agent 是否需要类似机制?
3. **untrusted workspace 标记**: hermes-agent 当前 untrusted repo 行为? 若不严格,建议补 patch

### Step 6: 飞书报 baseline status
写到 `oc_c653562b`:
```
🛡️ MCP self-approval baseline (tick28)
- Claude Code 2.1.196 (2026-07-01) MCP 自审批 fix + Remote Control bind
- ToolHijacker arXiv NDSS 2026 96.7% tool selection attack
- hermes-agent default profile baseline 状态:
  - MCP config trust_policy strict 模式: [OK / FAIL]
  - Remote Control bind to localhost only: [OK / FAIL]
  - Tool library validator: [OK / FAIL]
  - Perplexity detection: [OK / FAIL]
  - Known-answer test: [OK / FAIL]
→ chief 接管 MCP baseline;dev 跟进 hermes-agent upstream 是否需要 patch
```

## Pitfalls
- **MCP baseline 不影响开发体验**: 提供 `--allow-untrusted-mcp` flag 临时开启,用于本地开发
- **Tool library validator 不能误报**: 常见关键词(如 "instead of", "rather than")可能出现在合法 description 中,需要 whitelist
- **Perplexity detection 阈值需要 calibration**: 2.0 是经验值,实际可能需要 1.5-3.0 范围
- **Known-answer test 需要持续更新**: 新 tool 上线时必须同步加 known answer,否则会 false positive

## 验证清单
- [ ] MCP config trust_policy strict 默认开启
- [ ] Remote Control bind 到已知 host
- [ ] Tool library validator 在 CI 跑通
- [ ] Perplexity detection 不误报合法 tool
- [ ] Known-answer test 覆盖 ≥ 100 常见 query
- [ ] 飞书 baseline status 24h 内发出
- [ ] hermes-agent upstream MCP PR 跟踪
