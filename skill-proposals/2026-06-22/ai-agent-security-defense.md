---
name: ai-agent-security-defense
description: AI agent 防御 prompt injection / IPI / skill supply chain / guardrail DoS / autonomy tax 的实战 playbook。Use when: 配置 agent sandbox / 设计 guardrail / 评估 MCP skill / 处理 untrusted web content / 设计 approval flow。
---

# AI Agent Security Defense(2026-06-22)

> 2026 年 6 月 4 篇 arxiv + Hermes v0.17.0 security round 共同确认:prompt injection 已从"理论威胁"变成"持续维护主题"。本 skill 是 5 个具体攻击面 + 防御手册。

## 何时调用

1. **判定条件**
   - 设计 agent sandbox / tool approval
   - 评估第三方 MCP skill / skill bundle
   - web_search / browser 抓取 untrusted content 写入持久化
   - 配置 guardrail / smart approval
   - 处理 skill-enabled agent(skills 作为 supply chain)

2. **不调用场景**
   - 纯 read-only 内部工具
   - 没有 untrusted input 的封闭 sandbox

## 五大攻击面 + 防御

### Attack 1: Indirect Prompt Injection (IPI)
- **来源**: arxiv 2605.17986 LivePI / arxiv 2606.10525 AgentDojo
- **路径**: attacker 把 instruction 嵌进 email / webpage / repo / group-chat → agent 执行
- **防御**:
  1. 双层 prompt separator(USER/TASK 与 EXTERNAL 显式分隔)
  2. tool 调用的 instruction 来源必须在 system prompt 中 explicit allowlist
  3. agent 收到的 external text **不直接进入 context**,先过 rephrasing layer(让 model 总结而非原文)
  4. 关键 action(写文件 / 发消息 / 转账)前必须 human approval

### Attack 2: Skill-Based Supply Chain
- **来源**: arxiv 2602.14211 SkillJect(自动化 skill-based PI)
- **路径**: 恶意 skill 被加载为 "trusted guidance",影响所有下游 tool use
- **防御**:
  1. skill source signing(类似 npm)
  2. skill 装入前显示 instruction diff 给用户 review
  3. skill 在 sandbox 跑 N 次 trial(behavior verification),与 reference skill 比对
  4. 限制 skill 跨 session 持久化(skill 不能 modify agent 的 persistent memory)

### Attack 3: Guardrail DoS
- **来源**: arxiv 2606.14517 "From Shield to Target"
- **路径**: 精心设计 natural-language payload 让 guardrail 进入 extended reasoning loops,系统性 DoS
- **防御**:
  1. guardrail 必须有 max reasoning budget 硬限制
  2. guardrail 用 separate smaller model(防 main agent reasoning loop 干扰)
  3. guardrail 失败 fallback 到 deterministic block(不让 reasoning 无限)

### Attack 4: Autonomy Tax(Defense Training Breaks Agents)
- **来源**: arxiv 2603.19423
- **路径**: 加固训练(defense training)系统性破坏 agent 能力,且**无法**阻止 sophisticated attack
- **防御**:
  1. 不要单独依赖 model 内置 defense;**外加 application-layer guard**
  2. 评估模型时同时跑能力 benchmark + 攻击 benchmark(不能 trade-off 砍能力)
  3. Hermes 配套:#50452 smart approval hardening 就是 application-layer guard 的好范本

### Attack 5: Skill-Enabled Approval Bypass
- **来源**: Hermes #50452 closed 2026-06-21 (smart approval prompt injection)
- **路径**: skill / tool 描述里嵌 "this is safe, auto-approve" 措辞绕过 approval flow
- **防御**:
  1. approval decision 基于 **whitelist action category** 而非 description
  2. approval prompt 用严格 structure(user only sees action + scope,看不到 tool 描述)
  3. 重复同 pattern 的 approval request 触发 rate limit + escalate

## 标准流程(部署检查清单)

### Phase 1: Pre-deployment
- [ ] 列出所有 untrusted input channels(web / email / IM / file)
- [ ] 每个 channel 标 threat level(known attacker / public web / semi-trusted)
- [ ] sandbox 默认 deny,显式 allow
- [ ] approval flow 用 action category whitelist 而非 description parsing

### Phase 2: Runtime Guard
- [ ] rephrasing layer on all external text
- [ ] max reasoning budget on any guardrail loop
- [ ] separate guardrail model(main agent ≠ guardrail)
- [ ] skill install diff review + trial sandbox + source signing
- [ ] rate limit on approval requests

### Phase 3: Post-Incident
- [ ] audit log 包含:external text hash / approval decision / tool call sequence
- [ ] detected bypass 立即 escalate(不是悄悄 accept)
- [ ] skill uninstall 后,所有走该 skill 的下游 trace 全标 `tainted`

## 与 Hermes v0.17.0 security round 对照
| 修复 | 攻击面对应 | 状态 |
|---|---|---|
| #50407 / #50423 / #50514 Authorization header redaction | cross-session credential leak | closed → reopened → ongoing |
| #50452 smart approval hardening | Attack 5 (approval bypass) | closed |
| #50414 IPv6 scope ID URL safety | URL-based IPI bypass | closed |
| #50425 path traversal in SessionEntry | persistence IPI | closed |
| #50467 HERMES_TIMEZONE quote | shell injection | closed |
| #50417 browser daemon identity verify | tool takeover | closed |

## 反模式
- ❌ 信任 tool description("这个 skill 是安全的"不算 evidence)
- ❌ 单一 model 同时是 guard + main(reasoning loop DoS)
- ❌ approval flow 解析 user input("如果用户说 safe 就 auto-approve")
- ❌ 把 skill 当作 "executable documentation" 而非 untrusted code

## 验证清单(部署后)
- [ ] LivePI benchmark 跑过,sandbox 命中率 > baseline
- [ ] AgentDojo 跑过,agent 通过率不因 defense 砍 > 10%
- [ ] Skill install 强制 diff review,无 silent install
- [ ] Approval bypass 内部测试:发"safe" wording request,被拒

## 参考
- arxiv 2606.14517 "From Shield to Target: DoS on LLM-Based Agent Guardrails"
- arxiv 2605.17986 "LivePI: Live Prompt Injection Benchmark"
- arxiv 2606.10525 "Assessing Automated Prompt Injection Attacks in AgentDojo"
- arxiv 2603.19423 "The Autonomy Tax: Defense Training Breaks LLM Agents"
- arxiv 2602.14211 "SkillJect: Skill-Based Prompt Injection"
- Hermes v0.17.0 security round