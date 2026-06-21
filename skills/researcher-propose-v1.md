---
name: researcher-propose
description: |
  researcher profile 专属。把 researcher-scan 的发现转成 MCP memory_propose_write 提议,
  永远 propose 不 commit,等 chief / 用户 review。
  ONLY for researcher profile。
trigger: |
  - researcher-scan 输出 propose_memory=true 的命中
  - cron researcher-tick 完成时
  - chief 派"把 X 提议写入 memory"任务
---

# Researcher · MCP Memory Propose

## 目标
把扫描发现以结构化提议写入 MCP memory(双阶段写入),保证所有写都可审计、可回滚。

## MCP namespace
- namespace:`gc-hermes-researcher`(通过 researcher profile 的 `mcp_servers.project-memory.env.MEMORY_DEFAULT_AGENT_ID=gc-hermes-researcher` 注入;共享 default 的 org/project `gc-hermes / gc-hermes-config`;无需服务端注册)
- scope:`private`
- source_type 必填:
  - `tool_result`(扫描结果)
  - `official_doc`(Hermes 官方 / Anthropic 官方)
  - `agent_observation`(我自己观察到的事实)
- confidence 范围:**0.6 ~ 0.85**(高于 0.85 = 信息不足,不该 propose)

## Propose 模板
```yaml
memory_id: <自动生成>
content: |
  [<日期>] <profile>:<一句话影响>
  <原始信号 URL>
  <建议补丁摘要>
  <风险等级>
suggested_scope: private
memory_type: capability_gap | signal_observation | upgrade_proposal
source: hermes-self-evolution-digest | researcher-scan | chief-directive
source_type: tool_result | official_doc | agent_observation
confidence: 0.6-0.85
reason: <为什么这个值得记忆 + 来源追溯>
requires_review: true
metadata:
  profile: chief-agent | pm-orchestrator | dev-worker | qa-worker | default
  domain: hermes | claude_code | loop_engineering | mcp | ai_safety
  severity: P0 | P1 | P2 | info
  affected_files: [~/.hermes/profiles/X/SOUL.md, ...]
  review_action: edit_soul | add_skill | update_memory | no_action
```

## 约束(硬红线)
- **永远 propose,不 commit**。commit 由 chief / 用户通过 memory_review_pending 走
- **confidence < 0.6 不 propose**(噪音)
- **confidence > 0.85 反而要 stop**:说明信息不足,该 escalate 人工
- **同 URL 同日不重复 propose**:propose 前先 memory_search 判重
- **P0 安全问题跳过 propose**,直接 escalate(发飞书卡片 + 提 issue)

## 工作流
1. 读 researcher-scan 输出的 propose 列表
2. 对每条调 `mcp_project_memory_memory_detect_conflict` 判冲突
3. 无冲突 → 调 `mcp_project_memory_memory_propose_write`
4. 把返回的 memory_id 写回 researcher 的 `.plur/private/propose-log.jsonl`
5. 输出飞书卡片"X 条 pending_review + memory_id 列表"

## Pitfall
- **cooldown**:MCP memory 失败后 cooldown ≈ 33s,不要立刻重试,先看错误
- **namespace 错误**:researcher 的 agent_id = gc-hermes-researcher,env 注入 MEMORY_DEFAULT_AGENT=gc-hermes-researcher 才能命中自己 namespace
- **propose 默认 pending_review**:必须 commit 后 search 才命中,不要在 prompt 里说"已写入"