---
name: hermes-cache-breakpoint-audit
description: Hermes Agent v0.18.0 cache-breakpoint 端到端审计 skill。Use when: 验证 prompt cache marker 是否在 OpenRouter/Claude/Vertex AI 多 provider 路径上正确生效,或排查 "cache 命中率低 / input cost 翻倍" 类症状。覆盖 P0 #57845 (envelope-layout cache breakpoints silently no-op on tool messages) 的回归测试场景。
---

# hermes-cache-breakpoint-audit

> Hermes Agent v0.18.0 起的 cache-breakpoint 端到端审计 skill。
> 配套 SOUL v2 / cron: hermes-researcher-deep-tick-daily。
> 触发背景:2026-07-03 P0 #57845 报告 — OpenRouter + Claude 路径上,`role: tool` 消息和 empty-content assistant tool_call turn 的 `cache_control` marker 全部 silently no-op,导致 ~2x input cost。

## 何时调用

1. Hermes release 后 24h 内 ship-verification(见 qa SOUL draft)
2. 排查 "cache hit rate 突然下降" / "input cost 翻倍" 类症状
3. 验证 `prompt_caching.enabled` toggle 改动后实际行为
4. 用户报告 "agent 越来越贵" 且 provider 是 OpenRouter + Claude

## 标准流程

### Step 1: 准备

```bash
# 确认 hermes 版本支持 prompt caching 测试
hermes --version | head -1

# 准备 cache_breakpoint 测试脚本(伪代码示意)
mkdir -p /tmp/cache_audit
```

### Step 2: 三类 marker 路径验证

cache_control marker 三种放置位置:
- **A) top-level on `role: system`** — 标准路径,所有 provider 都支持
- **B) top-level on `role: tool`** — OpenRouter silently hang(已知,#57845 issue body 提到)
- **C) in-part in `content[]` block** — OpenRouter + Claude 都接受并 honor

必跑 assertion:
- 路径 A 在 `native_anthropic=True` 和 `native_anthropic=False` 都生效
- 路径 B 在 `native_anthropic=False` 必须 silently fallback 到路径 C(不是直接 hang)
- 路径 C 在两条路径都生效

### Step 3: tool-loop 真实场景

模拟 agentic tool call sequence:
```
system prompt (large, 5KB+)
user message
assistant tool_call turn (empty content, just tool_calls)
tool result message (large, 2KB+)
assistant text message
user follow-up
```

跑 5 轮,记录:
- 每轮的 cache_read_tokens / cache_creation_tokens
- 计算 cache hit rate
- 期望:cache hit rate ≥ 80% (前 3 轮 cache 暖起来后)

### Step 4: 多 provider 对照

分别跑 OpenRouter / Anthropic-native / Vertex AI:
- 同 conversation 序列,记录 cache hit rate
- 期望:三 provider 一致 ≥ 80%
- 若某 provider < 50% → 标 "provider-cache-anomaly",写入 MCP `bug_impact_matrix`

### Step 5: 输出 audit report

写到 `~/.hermes/cron/output/cache-audit/{date}-{provider}.md`,含:
- 三类 marker 路径 pass/fail
- tool-loop cache hit rate
- 多 provider 对照
- 异常定位(若 hit rate 低,标出哪类消息触发 no-op)

## 何时不该调用

- 不在 production session 跑 — 必须 test fixture 隔离,不要污染 user session
- 不在 cron worker 的 hermes-self-evolution-digest 内跑(避免 token 浪费)
- 不在 MoA preset 跑(MoA 多 reference model 走不同 routing,cache 行为不一致)

## 验证

- [ ] 三类 marker 路径都验证通过
- [ ] tool-loop 5 轮 cache hit rate ≥ 80%
- [ ] 三 provider hit rate 一致(±10%)
- [ ] audit report 写到正确路径
- [ ] 若异常,标 `provider-cache-anomaly` 并 propose_write 到 MCP

## 关联

- GH issue #57845 (P0 envelope-layout cache breakpoints silently no-op)
- GH PR #56126 (prompt_caching.enabled revert — 直接根因)
- v0.18.0 release body — 提及 prompt caching 重构 (引用 #56126 revert 段)
- arxiv 2607.01308 "Cache Merging as a Convergent Replicated State for Multi-Agent Latent Reasoning" — 多 agent cache 合并前沿