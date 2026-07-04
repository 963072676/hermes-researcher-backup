# SOUL 草案: default / xAI grok-4.3 MCP 工具调用降级策略

**针对 issue**: GH #58345 (P2, OPEN 2026-07-04) xAI grok-4.3 drops optional multiline string args from MCP tool calls — AgentMail + 其他 multiline-string optional args 静默截断。本环境 default profile 主模型 = `xai-oauth/grok-4.3`(researcher / chief / pm-orchestrator 都用同 provider),任何 call `tool(...)\n  ` 任意 multi-line optional string 都受影响

**风险等级**: P1(实时生效,每天 cron tick 都在用)
**confidence**: 0.75
**触发源**:
- https://github.com/NousResearch/hermes-agent/issues/58345 (xAI grok-4.3 drops optional multiline string args from MCP tool calls — AgentMail scenario)
- https://github.com/NousResearch/hermes-agent/pull/58351 (docs warn grok-4.3 drops optional multiline string args)
- https://github.com/NousResearch/hermes-agent/pull/58352 (fix(schema): promote optional string params to required — workaround)

## 当前文本(在 ~/.hermes/profiles/default/SOUL.md 假设的 "model routing" 段)
```text
- 主模型: xai-oauth/grok-4.3
- fallback: minimax-cn/MiniMax-M3
- 选 grok 原因: 中文 + 长上下文
```

## 建议替换为
```text
- 主模型: xai-oauth/grok-4.3(默认)
- fallback: minimax-cn/MiniMax-M3
- 选 grok 原因: 中文 + 长上下文
- **grok MCP 工具调用降级策略**(2026-07-05 立卡,issue #58345 + fix #58352):
  - 凡是发给 grok-4.3 的 tool call,如果参数包含 multi-line optional string(例如 body / content / body_markdown / description),agent 必须先在调用前补 "将 optional 改写为 required 用空字符串填充" 的 prompt 前缀,避免 Anthropic schema 严格化之前被 grok 静默丢弃
  - 触发条件: tool call parameter 含 default=null OR type=string 但实际有 multiline payload
  - 绕过: 若 critical path 严格要求 multiline payload,临时切到 MiniMax-M3 fallback provider(本环境已在 config)
  - 监测: 任一 grok-4.3 MCP tool call 返回值与送入 payload 不一致(例如 email body 含 `\n\n` 但收件人看到无换行),立刻上报 researcher profile + 飞书 oc_c653562b
  - 不要尝试在 grok 端修 schema-level "promote optional→required"(那是 PR #58352 已经在做的);default profile 自己的 prompt-level workaround 才稳
```

## 替换理由
- 本环境 default profile 日常 90% tool call 走 grok-4.3,任何 multiline payload(instruction / prompt / email body)都属于受影响面
- PR #58351 (docs) + PR #58352 (schema fix) 还在 open,即使 shipped 也是 schema-level,long-tail multiline edge case 仍未根治
- 默认 profile SOUL 必须显式列 workaround,因为 chief / pm / dev 全用同 provider
- 影响本环境的具体场景:
  1. 飞书 send_message 长 markdown 表格正文(本 cron digest)
  2. delegate_task 跨 profile 调度时,parent profile 给 child profile 的 system-prompt nudge
  3. memory_propose_write 时 content 多行(markdown)
- 这 4 类场景天天跑,默认 SOUL 显式 workaround 是唯一预防措施

## 风险与回退
- 风险: prompt 前缀占用 token(每次 tool call +50 tokens 左右);若 token 预算紧可降级 MiniMax-M3 反而更省钱
- 回退: git checkout ~/.hermes/profiles/default/SOUL.md
- 监测触发: researcher cron 每日 baseline probe 时,额外 probe 一次 grok-4.3 MCP tool call 是否返回 multiline 一致性(新 skill `hermes-grok-multiline-probe` 立卡)
