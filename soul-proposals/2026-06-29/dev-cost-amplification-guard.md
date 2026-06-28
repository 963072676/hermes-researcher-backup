# SOUL 草案: dev / Cost Amplification Guard

**针对 issue**: GH #54340 (PR open) + Issue #32827 — same-tool failure 反复 spawn, 无 auto-block, 默认 hard_stop_enabled=False, 直接烧 credits
**风险等级**: P2 cost / P1 silent cost explosion
**confidence**: 0.9 (生产事故已发生)
**触发源**: https://github.com/NousResearch/hermes-agent/pull/54340 + https://github.com/NousResearch/hermes-agent/issues/32827
**生产事故**:
- MCP transient failure → **42 wasted spawns**
- MCP deterministic 422 → **57-turn loop, ~$6 credits, 账户耗尽**

## 当前文本(在 ~/.hermes/profiles/dev/SOUL.md — 假设在「hard stop」段)

> Hard stop: 当同一 tool 连续失败 ≥ 10 次, 弹用户确认; < 10 次仅警告

## 建议替换为

> Hard stop 分层:
> - **L0** (3次连续失败): 自动 logger.warning, 不打扰用户
> - **L1** (5次连续失败): 自动 sleep 30s + 切换到 retry_with_backoff, 若仍失败进入 L2
> - **L2** (10次连续失败): 强制暂停 tool 调用, 弹用户确认 + 显示累计 estimated_cost (基于 model block 估算)
> - **L3** (15次连续失败): 自动硬停 + 立即推 chief-agent incident ticket
> - **Cost circuit breaker**: 累计 cost > $5 (per session) 自动 L3 等同, 即使 < 15 失败次数
>
> **配置位置**: `~/.hermes/config.yaml` 加 `guardrails.cost_breaker_usd: 5.0` + `guardrails.hard_stop_after: 10`

## 替换理由

- #32827 issue 已记录两个 production cost-amplification loop, 每个都是 ≥ $6 单次开销
- 本环境 researcher cron + dev session 都在 MiniMax-M3 via custom provider, **单次 cost 估算**: $0.30/M prompt token, 57 turn loop 平均 1k tokens ≈ $0.03/turn, 57 turn ≈ $1.7 (远低于 #54340 报告的 $6 但仍可观)
- 当前 hard_stop_enabled 默认 False, **等于无 guard**

## 风险与回退

- **风险**: L3 硬停可能误伤正常长循环(retry 不同 tool 同一目标)
- **回退**: 关闭 cost_breaker, 仅保留 fail_count 模式;或设高阈值到 $20

## 实测锚点

本环境 default profile `config.yaml` 应检查:
```yaml
guardrails:
  cost_breaker_usd: 5.0
  hard_stop_after: 10
  warn_after: 3
  sleep_after: 5
```