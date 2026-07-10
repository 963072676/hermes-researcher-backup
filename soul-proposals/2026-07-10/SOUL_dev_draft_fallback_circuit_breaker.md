# SOUL dev 草案 — fallback chain `_try_activate_fallback` circuit-breaker

> hermes-researcher tick32 (2026-07-10)
> source: GH #24996 (open since 2026-05-13, P1)
> priority: P1 (provider chain fallback tight loop 耗尽 host memory)
> target: dev-agent
> action: dev lead 评估 fix PR dedup + 加 `circuit-breaker` baseline 到
> `comp/agent` 防御层

## 触发

#24996 报 `_try_activate_fallback` 在 multi-provider fallback chain 多个连续
non-retryable error(depleted credits / rate-limited / rejected)时,**没有最小间隔** +
**没有累计 cap**,导致:
- 80k token session context 每次重 marshal
- load average 冲 30+,需 power-cycle
- 单板机 / constrained host 直接 OOM-kill

fix PRs 抢修:
- `#24998` (drabekj) — original fix,catch + circuit-breaker at function top
- `#25059` (shanewas) — circuit-breaker on fallback activations
- `#53909` (teknium1) — throttle cross-turn fallback-switch replay storm

3 PRs 60+ 天 open 仍未 merge,是 PR dedup fire 的典型。

## 本 profile 直接影响

本 cron worker provider=`minimax`,fallback chain 含多个 provider(沿用 user 配置)。
如果 minimax 一次性 30+ turn rate-limit / credit depleted,_try_activate_fallback
会 tight loop 重 marshal,cron tick 直接挂掉,**导致所有 cron worker
(包括 hermes-researcher-deep-tick-daily) 受影响**。

## root cause (loc 精确)

`run_agent.py::HermesAgent._try_activate_fallback` (~line 6285) 两 call site
loop back immediately with `retry_count = 0`:
- Rate-limit-triggered switch (~line 10417)
- Non-retryable client error switch (~line 10677)

两个都 reset retry counter + `continue`,没有 min interval + time window cap。

## 修复路径(沿用 #24998 推荐契约)

1. **Throttle**: `≥ 2s` between consecutive activations (`time.monotonic()` 检查)
2. **Breaker**: `≥ 5 activations in 60s` → return `False` (chain-exhausted 现有
   code 干净 handle)
3. centralize in helper `_fallback_circuit_breaker_check()` at top of
   `_try_activate_fallback`
4. 测试: monkey-patch `time.monotonic`,verify ≥ 2s 间隔 + ≥ 5 caps enforced

## SOUL dev-agent 段落(草稿追加 §7.4)

```markdown
### §7.4 Fallback circuit-breaker baseline (新增, 2026-07-10 tick32 立卡)

任何 PR 改 `_try_activate_fallback` 必须附 circuit-breaker 契约(沿用 GH #24996
fix 路径):

1. **invariant**: ≥ 2s min interval between consecutive fallback activations
2. **invariant**: ≥ 5 activations in 60s window → return `False`
3. **invariant**: chain-exhausted signal 现有 caller cleanly handle,无 caller
   change required
4. **testing gate**: 
   - `tests/agent/test_fallback_circuit_breaker.py` 必须 exist
   - 包含 monkey-patch `time.monotonic` + 5 activations in <2s 触发测试
   - 含 60s window cap 测试
5. **regression**: #24996 reproducer 必须 attach 在 PR description

PR-dedup 6h SLA 适用:24h 内 ≥ 3 PRs 抢同 fallback path (loc ~6285) → 选 1
primary,cross-PR 评估,diff 最小化,close 其他。

dev-worker lead 必须亲自负责 #24996 + sibling #25059/#53909 dedup + 主导
circuit-breaker PR close-out。预期 v0.19.0 合入。
```

## verdict 倾向

**采纳:中-高** — 本 cron worker 跑 minimax,fallback chain 触发的概率 mid-low
(主要 cron tick 直接 bypass fallback);但 hardening wave II 已 ship,
**circuit-breaker baseline 缺位** 是 release verification gap,fit dev PO
负责范围。
