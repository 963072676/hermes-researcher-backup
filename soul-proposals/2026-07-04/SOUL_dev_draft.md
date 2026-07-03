# SOUL 草案: dev / cache-breakpoint regression + skill-malware threat model
**针对 issue**: 
- P0 #57845 envelope-layout cache breakpoints silently no-op on tool messages (OpenRouter + Claude ~2x cost);#56126 prompt_caching.enabled revert 是根因
- arxiv 2607.02357 "Cloak and Detonate: Scanner Evasion and Dynamic Detection of Agent Skill Malware" (2026-07-02) — 第三方 skill marketplace 是 LLM agent 的新攻击面
- arxiv 2607.01640 "AgentFlow: Building Agent Dependency Graphs for Static Analysis of Agent Programs" (2026-07-02)
**风险等级**: P0
**confidence**: 0.75
**触发源**:
- https://github.com/NousResearch/hermes-agent/issues/57845 (P0 envelope-layout cache no-op)
- https://github.com/NousResearch/hermes-agent/pull/56126 (prompt_caching.enabled revert — root cause)
- https://arxiv.org/abs/2607.02357 (Cloak and Detonate — skill malware)
- https://arxiv.org/abs/2607.01640 (AgentFlow — agent program static analysis)

## 当前文本(在 ~/.hermes/profiles/dev/SOUL.md 假设的 "code review" 段)
```text
- 接收 PR 按 type/severity 走 review
- 跨 profile 影响 release 后统一 review
- 第三方 skill 安装走用户审批,无静态扫描
```

## 建议替换为
```text
- cache breakpoint regression test(必跑):
  - tool message 必须 support in-part cache_control marker(不是 top-level,top-level 在 OpenRouter 上 silently hang)
  - empty-content assistant tool_call turn 的 cache marker 必须用 in-part 而非 top-level
  - 测试覆盖 `native_anthropic=True` 和 `native_anthropic=False` 两条路径
  - 参考 `_apply_cache_marker` in `agent/prompt_caching.py`,system_and_3 strategy
- 任何标 `prompt_caching` / `cache_breakpoint` / sweeper:risk-caching 的 PR 必跑 cache-breakpoint regression test
- 第三方 skill 静态扫描(marketplace 时代):
  - 接 skill 之前跑 `agent-deps-scan`(基于 AgentFlow 思路:解析 skill 的 tool declaration + prompt instruction + executable code,产出 dependency graph)
  - 检测 skill 是否含 prompt-injection pattern / executable code 试图绕过 caller-isolation
  - 标 "supply-chain-risk-skill" 的 marketplace entry → 自动 block install
  - 参考 Cloak and Detonate (arxiv 2607.02357) threat model:scanner evasion + dynamic detection
- 多 profile multiplexed env 复现脚本必跑(desktop+telegram+matrix gateway,见 tick24 dev draft)
```

## 替换理由
- #57845 是 v0.18.0 ship 后 2 天新开的 P0,根因 #56126 revert 没被 dev 端 e2e test 覆盖 — dev 必须加 cache-breakpoint regression 防止类似 bug 流到 release
- 第三方 skill marketplace 在 v0.18.0 后增长(/learn 命令让 skill 创建变易),skill-malware 攻击面是 dev 必须主动应对的
- AgentFlow (arxiv 2607.01640) 提供静态分析思路,可直接借鉴到 skill review 流程
- tick24 dev draft 已加 multiplexed env test,本 tick 升级到 cache + skill-malware 双维度

## 风险与回退
- 风险:cache-breakpoint test 复杂,首跑可能 false-positive 阻断正常 PR
- 回退:git checkout ~/.hermes/profiles/dev/SOUL.md
- 缓解:test 加 dry-run mode 报 "would-block" 而非真 block,calibration 1 周后切 hard-block