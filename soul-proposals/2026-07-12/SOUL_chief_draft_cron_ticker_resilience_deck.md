# SOUL 草案 — chief-agent — cron-ticker-resilience-deck v1 (tick33)

> Tick33 2026-07-12 | Author: researcher profile | Streak=9 zero-adoption | v0.18.0 local + v0.18.2 upstream
> Memory ID: 77fe080a-2250-43dc-822b-8a195cc56fac (MCP pending_review)
> Family: cron-ticker-resilience-deck (NEW 8th family)

## 触发 evidence (9 GH issues 单一 family)

| GH # | 创建 | 主题 | 关键 root cause 段 |
|---|---|---|---|
| #32612 | 2026-05-26 | Cron ticker dies silently 15.5h, no error log, no watchdog | DEBUG-level swallowed error + `except Exception` miss BaseException + no ticker liveness monitor |
| #32895 | 2026-05-27 | ticker thread stops silently, jobs never fire (dup of #32612) | 同 root cause |
| #37179 | 2026-06-02 | ticker thread dies after long-running sequential job + Windows msvcrt 0-byte lock + `mark_job_run` fast-forward | 3 failure mode: (a) BaseException escape (b) Windows lock PermissionError on 0-byte file (c) `next_run_at` 永久丢失 |
| #27485 | 2026-05-17 | tick lock held for full job duration causes scheduler starvation | `fcntl.LOCK_EX` 持有至 ThreadPoolExecutor.__exit__, 长任务冻整个 ticker |
| #11614 | 2026-04-17 | Gateway exits when Telegram disconnects, killing embedded cron ticker | platform retryable error → `await self.stop()` → cron 死 |
| #48234 | 2026-06-18 | Gateway exits 1 on cron-triggered LLM IndexError; second crash leaves it down indefinitely (Feishu websocket dies) | `IndexError` from malformed provider response → systemd 重启一次后 second crash 不再 Restart=always 触发 |
| #49410 | 2026-06-20 | Gateway crashes on startup with `ModuleNotFoundError: No module named 'cron.scheduler_provider'` | `plugins/cron/` namespace 被 `sys.path.insert(0, plugins/)` 抢先解析 |
| #30719 | 2026-05-? | Agent schedule gateway-restart cron job that kills its own runtime | agent 自启 cron 调 `hermes gateway restart` 创 respawn loop with launchctl/systemd KeepAlive |
| #44049 | 2026-06-11 | Desktop dashboard cron ticker can execute jobs instead of launchd gateway (macOS TCC/FDA provenance) | dashboard 后端 `HERMES_DESKTOP=1` 抢 `.tick.lock` 失 launchd provenance |

**判定**:9 issues 1 family = 架构性问题,不是个别 bug 累计。**与 silent-fail (tick27) 同级,但 root cause 不同**:
- silent-fail = send-and-forget 投递缺失
- cron-ticker-resilience = **cron thread death + lock starvation + ownership race + restart loop + ticker visibility** 4-轴失效

## 草案 (chief-agent SOUL v2 第 12 段追加)

```diff
+ ## Cron Ticker Resilience Deck v1 (tick33 立卡)
+
+ **原则**:任何 cron ticker 失败模式必须 6 invariant 全部满足,缺一即视为架构问题。
+
+ 6 Invariant:
+ 1. **Liveness heartbeat** — ticker thread 每 tick 必须 atomic write `~/.hermes/cron/ticker_heartbeat` epoch;`hermes cron status` 必须读 heartbeat age 判活,不再只看 gateway PID
+ 2. **BaseException catch** — ticker loop body 必须 wrap `try/except BaseException`,log + heartbeat advance,continue next tick (不退出 thread)
+ 3. **Lock granularity** — `fcntl.LOCK_EX` 仅在 `get_due_jobs()` + `advance_next_run()` critical section,不在 job execution 持锁。Windows: `lock_fd.write(b".")` pre-init 避免 msvcrt 0-byte EOF PermissionError
+ 4. **Ownership invariant** — gateway 模式下,desktop ticker (`HERMES_DESKTOP=1`) 必须 defer 到 gateway owner;launchd/systemd owner is the canonical ticker;Windows 没有 launchd,默认 gateway owner
+ 5. **Restart safety** — `agent cron create --schedule="*/1 * * * *" --command="hermes gateway restart"` 必须 deny with reason (防止 agent 自杀 respawn loop)
+ 6. **Tick visibility** — `hermes cron status` 必须显示 `(ticker alive, last_success=3m ago, last_heartbeat=15s ago)`,heartbeat stale > 2x interval = WARN,> 5x = FAIL with explicit "ticker thread dead" message
+
+ **chief 6h SLA**:任何 cron ticker P1 → chief 必须在 6h 内 dedup PR,选 primary,关重复 (沿用 tick27 PR dedup 模式)。PR ≥ 3 同 root cause 即触发。
+
+ **family 标识**: `sweeper:risk-cron-ticker-resilience`
```

## 配套 SOUL chief 段修订建议

- 现行 chief SOUL 没有 ticker resilience deck → 建议在 chief SOUL v2 加 1 段 (上面 6 invariant)
- 触发立卡条件 = 同 family 30d ≥ 3 issues / cross-platform cross-team ≥ 2 hits / 投递可靠性 < 99% 触发 1 次即升级
- chief 必须主动监控 `ticker_heartbeat` file 在 cron-output 每日报告里 (researcher cron worker 顺手收)
- 5 SOUL 配额本次 chief 占 1 配额,保留 4 配额给 default / dev / qa / pm

## 优先级

P1: cron-ticker-resilience deck 是 **本 cron worker 直接高优级**,因为 gateway ticker 是 cron worker 投递的根 infra。ticker 死 = 我们日终汇总 0 投递。

## 关联 references

- 草稿落地: `/root/migrated-home/hermes-researcher-backup/soul-proposals/2026-07-12/SOUL_chief_draft_cron_ticker_resilience_deck.md`
- MCP memory_id: 77fe080a-2250-43dc-822b-8a195cc56fac (pending_review)
- 备份 commit: 待 tick33 push (cba4ac7 之上)
- 关联 issue/PRs: #32612 #32895 #37179 #27485 #11614 #48234 #49410 #30719 #44049

## 下一步

1. user review → SOUL v2 第 12 段合并
2. chief-agent 接到 SOUL 后 6h 内 dedup 3+ PR family (沿用 tick27 #58777/#58874/#58992 PR dedup 模式)
3. 配套 skill `hermes-cron-ticker-resilience-deck` 草稿(已生成,见 skill-proposals/2026-07-12/)