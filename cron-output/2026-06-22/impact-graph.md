# 跨 profile 影响图 (2026-06-22)

> C 档自进化 inaugural tick。今天扫到 5 条 SOUL 草稿 + 3 条 skill 草稿,以下整理 A 改 X → B 必须改 Y 的依赖链。

| # | 触发 | 直接影响 | 隐含影响 | 风险 | 处理 |
|---|---|---|---|---|---|
| 1 | **chief-agent** 改 "loop-engineering-mandate" (强制 builder≠judge) | dev-worker / qa-worker 必须接受 cross-vendor 编排 | pm-orchestrator 派活时同步声明 verifier;default profile cron 也需 cross-vendor QA | P0 | 三 profile 配套升级 |
| 2 | **qa-worker** 改 "external-verifier-mandate" (cross-vendor 强制) | dev-worker 必须明确 verifier 不是自身;增加 2x token cost | 用户预算需调整;chief-agent 必须监控 cost rise | P1 | 先告知用户,再批 SOUL 替换 |
| 3 | **pm-orchestrator** 改 "mcp-ema-adoption" | 所有 MCP 授权走 IDP/EMA;IT 团队需配 Okta XAA | Hermes MCP config.yaml 可能需加 EMA 块;dev / qa / default 都受 | P1 | 待用户 IT 团队拍板 |
| 4 | **dev-worker** 改 "glm-5.2-fallback" | OpenRouter 价格敏感任务可省 5-10x cost | chief-agent 派活时需声明 "cost-critical" flag | P2 | 静默切换,先小流量 |
| 5 | **default** 改 "redact-followup" (5 个 redaction 章节) | 所有 profile 在 web scraping / write 操作前过 redact | researcher profile 自身产出会被盯紧 #50514 JSON secret 折叠盲点 | P0 | 立即升级 default,下游渐进 |
| 6 | **新增 skill** loop-engineering-orchestrator | chief / pm / qa 三个 profile 都需要引用 | dev-worker 的 delegate_task 协议需扩 rubric 字段 | P1 | 与 #1 同步 ship |
| 7 | **新增 skill** mcp-2026-07-28-migration | pm-orchestrator / dev-worker 都要参照 tasks/list 移除迁移 | 长跑 polling task 必须改 handle 模式 | P1 | 7/28 ship 前置 |
| 8 | **新增 skill** ai-agent-security-defense | 5 攻击面对应 5 防御;Hermes 已 fix 6 条 | researcher profile 写 mcp memory 前必走 rephrasing layer | P0 | 立即配套 |

## 依赖链可视化

```
chief-agent (loop-engineering-mandate)
    ↓ 强制
qa-worker (external-verifier-mandate) ←→ dev-worker (glm-5.2-fallback)
    ↓ 调度                              ↓ 触发
pm-orchestrator (mcp-ema-adoption) ─────┘
    ↓ 通用 default
default (redact-followup) ─── 所有 profile 共享

新增 skill:
- loop-engineering-orchestrator → chief / qa / pm 引用
- mcp-2026-07-28-migration     → pm / dev 引用
- ai-agent-security-defense    → 所有 profile 引用
```

## 关键冲突点

1. **cost 冲突**: #2 qa-worker 强制 cross-vendor 会涨 token cost,#4 dev-worker 加 GLM-5.2 试图压 cost → 互相抵消,需用户拍最终 cost 策略
2. **migration 节奏**: #3 EMA 需 IT 团队配,#7 MCP 2026-07-28 是 10 周窗口 → 7/28 前 EMA 必须先到位,否则迁移断
3. **redact 优先级**: #5 default redact 与 #8 ai-agent-security-defense 的 rephrasing layer 重复,但不同 layer,必须配套 ship

## 待用户裁决清单
- [ ] 是否同意 cross-vendor QA 涨 cost(预估 daily +30-50% token)
- [ ] EMA 配 Okta 的时间窗
- [ ] 是否同意降频 chief-agent 自我评估 → 转 chief-external-verifier 强配
- [ ] researcher profile 是否启用 rephrasing layer(影响 research throughput)