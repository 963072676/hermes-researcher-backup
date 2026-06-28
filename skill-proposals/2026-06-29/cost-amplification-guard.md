---
name: cost-amplification-guard
description: 监控 same-tool 重复失败 + 累计 cost, 自动 L0→L3 分层响应。Use when: agent session 出现 ≥ 3 次连续同 tool 失败, 或累计 cost 接近 budget 上限, 防止 cost-amplification loop (#32827 / #54340 模式)。
---

# cost-amplification-guard

> Hermes session 内 same-tool failure + cost circuit breaker, 防 42 spawns / 57 turn / $6 cost 单次事故。

## 何时调用

- `session.trace` 中同 tool_name 连续失败 ≥ 3 次
- 单 session 累计 estimated_cost > $5
- 用户主动 `/cost-armor` 开启硬停
- chief-agent / pm 自动跑 daily 审计

## 标准流程

### Step 1: 状态探针

```python
# 在 session 内
import json, time
trace = session.get_trace()
fails = [t for t in trace if t["status"] == "failed"]
last_tool = fails[-1]["tool"] if fails else None
fail_count = sum(1 for t in reversed(fails) if t["tool"] == last_tool)
est_cost = session.estimated_cost_usd

print(f"tool={last_tool} fail_count={fail_count} est_cost=${est_cost:.2f}")
```

### Step 2: 分层响应

| 等级 | 条件 | 响应 |
|---|---|---|
| L0 | fail_count=3 | `logger.warning` + 不打扰用户 |
| L1 | fail_count=5 | `time.sleep(30)` + retry_with_backoff |
| L2 | fail_count=10 | **暂停 tool call**, 弹用户确认 + 显示 est_cost |
| L3 | fail_count=15 OR est_cost > $5 | **硬停** + 推 chief-agent incident ticket |

### Step 3: 用户感知

- L2: 弹 modal "Same tool failed 10x, est cost $3.20. Continue? [Y/n]"
- L3: 硬停后自动 `send_message(to=chief, severity=P1, content="cost loop detected: tool=X, count=N, cost=$X.XX")`

### Step 4: 关闭 / 降级

- 临时关闭: `hermes guardrails disable cost_breaker`
- 永久关闭: `config.yaml` 设 `guardrails.cost_breaker_usd: 999`
- 仅 fail_count 模式: `config.yaml` 设 `cost_breaker_usd: null`

## 配置参考

```yaml
# ~/.hermes/config.yaml
guardrails:
  warn_after: 3
  sleep_after: 5
  hard_stop_after: 10
  cost_breaker_usd: 5.0
  circuit_breaker_enabled: true
```

## 何时不该调用

- 不同 tool 失败(retry 不同 tool 同一目标是合法)
- 用户明确说 "不要 stop, 一直 retry"
- cost < $0.10 (小额试探, 不应硬停)

## Pitfalls

- **L1 sleep 30s 可能 block 用户**: 若是 interactive session, sleep 期间用户看不到进度;建议 sleep 期间显示 "auto-retry in 30s..."
- **cost 估算精度**: 当前 `session.estimated_cost_usd` 用 model block pricing, 实际 cost 可能 ±20%, **保守设阈值 $5 而非 $3**
- **MCP tool 失败 vs 普通 tool 失败**: #54340 报告两个 MCP 失败 → 42/57 turn loop;若 tool type=mcp, fail_count 阈值降为 5 即应进 L2

## 关联监控

- GH #54340 (PR open) — fix(guardrails) 提案
- GH #32827 (Issue open) — 原始 cost loop 报告
- Linear COD-XXX — chief ticket 跟踪

## 验证

```bash
# mock 测试
python3 -c "
from agent.guardrails import CostAmplificationGuard
g = CostAmplificationGuard(cost_breaker_usd=5.0, hard_stop_after=10)
for i in range(12):
    action = g.on_failure(tool='web_search', cost=0.5)
    print(f'fail #{i+1} → action={action}')
# 期望: warn(3) → sleep(5) → sleep_more(10) → HARD_STOP(11,12)
"
```