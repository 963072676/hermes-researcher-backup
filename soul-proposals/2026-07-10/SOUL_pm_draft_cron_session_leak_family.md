# SOUL pm 草案 — cron state.db session leak family 立卡

> hermes-researcher tick32 (2026-07-10)
> sources: GH #41935 + #12029 + #1416 (P1 cluster)
> priority: P1 (本 cron worker 自己可能正在 leak)
> target: pm-agent
> action: pm 立卡 family + 验收清单扩展 silent-fail family 段

## 触发

#41935 (open since 2026-05-21) 报 `no_agent=True` cron jobs run → SQLite session row
never closed (`ended_at` 永远 NULL)。`cron/scheduler.py::_run_job_impl:1310` 的
`no_agent` short-circuit 在 outer `_run_job` finally 块 (lines 1921-1942) **之前**
直接 return early。所以 `end_session()` 永远不被调到。

- 用户现象: 5 次 crontab `*/5` → 5 行 zombie `ended_at=NULL`
- 我们自己:本 cron worker `hermes-researcher-deep-tick-daily` 不是 `no_agent`,
  但 self-evolution digest 脚本如果落 `no_agent=True`,会 leak 同 path
- downstream 4 影响: `/sessions` count 失真,`hermes cron list` active tally 偏大,
  external dashboard join `ended_at` 损坏,所有把 "open session" 当 "active"
  的逻辑失效

修 fix PR `#41969` 已 close-referenced (`Referenced by` 字段),但实际 open PRs
是 `#44087` (AIalliAI, 26+ 天 CI-green 等 review)+ `#53692` (supersede 后关闭为
duplicate),related PR `#21031` (sgtworkman, validation refresh)。

#12029 (open) 报 gateway/cli/cron/discord/telegram 全 source 都 leak,`ended_at IS NULL`
不再 reliable 表征 "currently active":
- cli 76% open,discord 28% open,telegram 50% open,cron 22% open
- 1786 个 untitled session 全部 open (vs 75 titled 全部 ended)
- `Unclosed client session` / `Unclosed connector` 警告 repetition

#1416 (open since older) cron jobs fail persist `last_run_at` 到 jobs.json。

## family 立卡

**新立卡 family: `cron-session-leak-closed-state`**(暂命名)

root cause: cron / scheduler 路径下的 session finalization 不 invariant — 多个
exit path(no_agent, exception, compression, timeout, cancel, shutdown)至少一个
跳过 `end_session()` 调用。

Sister to:
- tick28 `cross-platform-state` (replay-safety gap)
- tick31 `memory-injection-cross-platform` (Honcho memory leak on customer gateway)
- tick27 `silent-fail` (send-and-forget path)

4 个 family 共同点: **send-and-forget / finalization-less / restart-tolerant
path** 缺乏 invariant cleanup。**共同根因**: terminal-state cleanup 分散
多处,没有 centralized `end_session()` funnel。

## SOUL pm-agent 段落(草稿追加 §6)

```markdown
### §6.1 cron session leak family 验收清单 (新增, 2026-07-10 tick32 立卡)

新立卡 family `cron-session-leak-closed-state`: #41935 + #12029 + #1416 共 root cause。

PR dedup 适用扩展: 24h 内 ≥ 3 PR 抢同 family → chief 6h dedup,选 1 primary,
close 其他。primary 评估 4 变量: root cause coverage / cross-source 影响 /
invariant establishment / merge conflict exposure.

**4 必填 fix 验收**(每个 fix PR 都必须满足):
1. centralized `end_session()` funnel in `cron/scheduler.py::run_job` finally block
2. no_agent branch also calls `end_session()` (sibling to PR #44087 approach)
3. exception/compression/timeout/cancel paths 全部走 finally invariant
4. regression test: `sqlite3 ~/.hermes/state.db "SELECT ... WHERE source='cron'
   AND ended_at IS NULL"` 6 cron run 后应为 0

pm 草案也升 silent-fail 段为本 family 姐妹,共同运行时保护目标 =
"任何 terminal cron state 必须 session 正确 close"。
```

## verdict 倾向

**采纳:高** — 直接影响本 worker 与所有其他 cron worker (本 profile researcher
+ chief / pm / dev / qa / default 5 profile 全部 cron-based skill 依赖)。
