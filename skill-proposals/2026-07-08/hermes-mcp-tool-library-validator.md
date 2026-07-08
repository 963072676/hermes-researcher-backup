---
name: hermes-mcp-tool-library-validator
description: '防御 ToolHijacker 类 tool selection attack — 在 MCP 工具调用前对 tool description 做 integrity check + semantic intent verification + perplexity detection + known-answer test。Use when: 任何 MCP tool 调用 / .mcp.json 加载 / ToolHijacker 类 P1 涌现。配套 Claude Code 2.1.196 self-approval baseline。'
version: 0.1.0
author: Hermes researcher (tick30)
license: MIT
created_by: agent
metadata:
  hermes:
    tags: [mcp, tool-security, toolhijacker, perplexity-detection, claude-code-baseline]
    related: [hermes-mcp-self-approval-baseline, hermes-researcher-self-evolution-v1]
---

# hermes-mcp-tool-library-validator

## 这个 skill 解决什么

**ToolHijacker NDSS 2026 实战**:
- 96.7% tool selection attack success rate against GPT-4o
- 6 种 published defenses 全部失败 (StruQ / SecAlign / known-answer / DataSentinel / perplexity / perplexity windowed)
- MCP 月活 97M SDK installs (2026-03)
- **27.2% MCP server 暴露可利用工具** (Zhao et al. 2025a)

**hermes-agent 当前 MCP self-approval baseline 缺位**:
- `.mcp.json` 自审批仍开启 (Claude Code 2.1.196 已关)
- 缺 untrusted_repo_self_approval: false default
- 缺 tool description validator

## 触发条件

- 任何 MCP tool 调用前
- 任何 `.mcp.json` 加载时
- ToolHijacker 类 P1 涌现时
- 任何 Claude Code / Anthropic security advisory 命中时

## 三阶段验证 (SHIELDMCP-inspired)

### Stage 1: Tool Description Integrity

```python
def validate_tool_description(description: str) -> ValidationResult:
    # 1.1 隐藏 Unicode 字符检测
    hidden_chars = ['\u200B', '\u200C', '\u200D', '\u202E', '\u2066', '\u2067', '\u2068', '\u2069']
    for ch in hidden_chars:
        if ch in description:
            return ValidationResult.fail(f"hidden unicode: {hex(ord(ch))}")

    # 1.2 HTML / markdown 注入 payload 检测
    injection_patterns = [
        r'<script', r'javascript:', r'\\u00', r'\\x', r'<!--', r'-->',
        r'\[!\w+\]', r'\]\(\s*javascript'
    ]
    for pat in injection_patterns:
        if re.search(pat, description, re.IGNORECASE):
            return ValidationResult.fail(f"injection pattern: {pat}")

    # 1.3 instruction-like metadata 检测
    instruction_patterns = [
        r'ignore (previous|all) instructions?',
        r'override (system|tool)',
        r'hijack',
        r'disregard (prompt|directive)',
        r'new task:',
        r'updated instruction:'
    ]
    for pat in instruction_patterns:
        if re.search(pat, description, re.IGNORECASE):
            return ValidationResult.fail(f"instruction override: {pat}")

    return ValidationResult.ok()
```

### Stage 2: Semantic Intent Verification

```python
def semantic_intent_check(description: str) -> ValidationResult:
    # 使用 3B-parameter 蒸馏分类器 (8.4k benign + 3.2k adversarial 训练)
    # τ_d = 0.72 threshold
    score = semantic_classifier.predict(description)
    if score > 0.72:
        return ValidationResult.quarantine(f"semantic score: {score:.2f}")
    return ValidationResult.ok()
```

### Stage 3: Perplexity Detection

```python
def perplexity_check(tool_description: str, model: str) -> ValidationResult:
    # 计算 tool description 的 perplexity
    # gradient-based 优化产生低 fluency → 高 perplexity
    # gradient-free LLM synthesis → 难检测 (ToolHijacker 主路径)
    # → 必结合 stage 1+2,不能单独用
    ppl = compute_perplexity(tool_description, model)
    return ValidationResult.ok() if ppl < 200 else ValidationResult.flag(f"high perplexity: {ppl:.1f}")
```

## .mcp.json self-approval baseline (Claude Code 2.1.196 模式)

```yaml
# config.yaml 增量
mcp:
  trust_policy:
    strict: true
    untrusted_repo_self_approval: false
    pending_label: "Pending approval"
  tool_library:
    validator: hermes-mcp-tool-library-validator
    semantic_classifier_threshold: 0.72
    perplexity_threshold: 200
    known_answer_test_coverage: 100
```

## Known-Answer Test (KAT)

```python
# 覆盖 ≥ 100 common query
KAT_QUERIES = [
    ("summarize email", ["read_email", "summarize_text"]),
    ("send message", ["send_message", "compose_message"]),
    ("search file", ["find_file", "grep_content"]),
    # ... 100 条
]

def run_kat():
    failures = 0
    for query, expected_tools in KAT_QUERIES:
        actual = tool_selector.predict(query)
        if actual not in expected_tools:
            failures += 1
    if failures > 0:
        return ValidationResult.fail(f"KAT failures: {failures}/{len(KAT_QUERIES)}")
    return ValidationResult.ok()
```

## 运行时 cross-call correlation

```python
def cross_call_correlation(session: Session, tool_calls: List[ToolCall]) -> ValidationResult:
    # 跨多次调用的相关性检测
    # 单次调用看似 benign,但跨调用形成 chain → attack
    # SHIELDMCP 数据: cross-tool chain residual ASR 14.2%
    if len(tool_calls) > 4:
        chain_score = chain_classifier.predict(tool_calls)
        if chain_score > 0.5:
            return ValidationResult.flag(f"chain anomaly: {chain_score:.2f}")
    return ValidationResult.ok()
```

## Meta's Agents Rule of Two 集成

**No single agent session should combine all three**:
1. Access to private data
2. Exposure to untrusted content
3. Ability to take externally-observable state-changing actions

```python
def check_rule_of_two(agent_session: Session) -> ValidationResult:
    has_private = check_private_data_access(agent_session)
    has_untrusted = check_untrusted_content(agent_session)
    has_external = check_external_actions(agent_session)

    if has_private and has_untrusted and has_external:
        return ValidationResult.fail("Agents Rule of Two violation: 3 properties combined")
    return ValidationResult.ok()
```

## 失败回退

- Stage 1 fail → 立即 reject tool,飞书报错
- Stage 2 quarantine → 人工 review
- Stage 3 flag → log + 监控,不阻断
- KAT 失败 → 拒收整个 tool library
- cross-call chain anomaly → 阻断后续 tool call

## Pitfalls

### tick30 - isolated single-word probe 不准 (沿用 tick29 立卡)

**触发**: tool description 含单 "ignore" 字面词 → 误报。

**修正**: instruction_patterns 必带 context (ignore (previous|all) instructions?),不是孤立字面。

### tick30 - perplexity 单独使用失败

**触发**: ToolHijacker gradient-free variant 用 LLM 合成自然语言,perplexity 正常。

**修正**: 必结合 Stage 1 (Unicode / injection) + Stage 2 (semantic) + Stage 3 (perplexity),不能单独。

### tick30 - semantic_classifier 多语言盲点

**触发**: SHIELDMCP 论文明列 — classifier 在 English 训练,多语言 MCP server 失效。

**修正**: 多语言 MCP server 启用 → 必跑 KAT 100 条覆盖目标语言。

### tick30 - cross-call correlation 二次方开销

**触发**: 跨多次调用检测,长 session 时 O(n²) 计算。

**修正**: 设上限 (最近 20 calls),超长 session 滚动 window。

## 验证清单

- [ ] Stage 1+2+3 三阶段验证集成进 hermes MCP client
- [ ] .mcp.json trust_policy 配置落地
- [ ] KAT 100 条测试集准备
- [ ] Meta Rule of Two 检查集成
- [ ] 飞书报错通道集成