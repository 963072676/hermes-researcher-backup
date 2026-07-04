# SOUL 草案: chief / cron delivery 三层 silent-fail 防御

**针对 issue**: GH #58363 (P2, OPEN 2026-07-04) Yuanbao cron delivery silently fails after WS reconnect (three causes) — 同 family #58379 + #58378 + 类似 #54329 feishu deliver=origin silent drop + #50733 QQBot `_listen_loop` silently hangs after single transport-level reconnect failure
4 条 issue 共享同一 root pattern: **adapter WS reconnect 失败时,cron delivery 在 cron worker 那端静默丢失**(no alarm / no retry / no fallback)
本环境 chief 是 default profile 的 cron 调度协调层,**所有 cron 最终 delivery 都走这一层**(feishu DM / oc_c653562b 是默认 target)

**风险等级**: P0(cron 是 production-critical;silent fail 比 loud fail 危险 10 倍)
**confidence**: 0.75
**触发源**:
- https://github.com/NousResearch/hermes-agent/issues/58363 (Yuanbao cron delivery silently fails after WS reconnect, three causes)
- https://github.com/NousResearch/hermes-agent/pull/58379 (fix(yuanbao): restore adapter singleton after WS reconnect + retry delivery)
- https://github.com/NousResearch/hermes-agent/issues/50733 (QQBot _listen_loop silently hangs)
- https://github.com/NousResearch/hermes-agent/issues/54329 (feishu deliver=origin silent drop)
- tick11 立卡 #49334 (hermes-lark-streaming 抑制 send_message 工具输出)

## 当前文本(在 ~/.hermes/profiles/chief/SOUL.md 假设的 "cron delivery 监控" 段)
```text
- chief 不主动 monitor cron delivery
- failure 由 cron worker 自己 retry / report
```

## 建议替换为
```text
- **cron delivery 三层 silent-fail 防御**(2026-07-05 立卡,issue #58363 + family):
  1. **layer 1 - pre-delivery probe**: chief 在每个 cron job 启动时(0s / 5s / 30s 三次)调 `diagnose_delivery_path(target)` probe — 拉 feishu / yuanbao / qqbot / lark-streaming 任一 adapter 的 health + last-reconnect-time + last-send-success,若任一 fail → 立刻 redirect cron 到 fallback target(飞书 oc_c653562b)
  2. **layer 2 - post-delivery verification**: 每条 cron 发出后 60s 内主动 ack — 若 tool return `success: True` 但 `mirrored: False` 或 no read-receipt → 标 silent fail,飞书报 oc_c653562b + 把 cron 标 retry-pending
  3. **layer 3 - daily silent-fail audit**: chief 每日 08:00 UTC 跑 "cron delivery silent-fail audit" — 对比 cron job.run_log vs final delivery receipt,任何 mismatch > 5% → 触发 🛑 "cron delivery silent fail rate" 事件
- **规范**: chief 接管所有 cron delivery 通道(feishu / yuanbao / qqbot / 飞书 streaming)健康监控,优先级等同 dispatch 失败
- **red-line 保留**: chief 不调 hermes update,不直接 patch adapter — 只 monitor + redirect
- **trigger words**(命中即升级 🚨):"silent fail" / "stuck reconnect" / "no retry" / "delivery lost" / "WS 重连后无消息"
```

## 替换理由
- tick11 立卡 #49334(hermes-lark-streaming 抑制 send_message)已经写过此问题,但当时不知道是 family pattern;今天 #58363 + #58378 + #58379 + #50733 + #54329 五连发证实是 **系统级 silent-fail 模式**而非个别 bug
- chief 是默认 profile 的 cron 协调层,默认 profile 装了多个 cron(hermes-self-evolution-digest + hermes-researcher-deep-tick-daily + kanban),每个 cron 的 delivery failure 都会影响用户对系统的信任
- "silent fail 监控"是 chief 的天然职责,因为它跨越所有 cron / profile / adapter,而单个 profile 看不到全局 picture
- 三层防御的设计:probe(提前拦截)+ verify(事后核对)+ audit(每日总结)覆盖 silent-fail 的 4 种 entry point(adapter hung / reconnect lost / send_message swallow / retry exhaustion)

## 风险与回退
- 风险: probe + verify 每天调用 + 给所有 cron 增加 ~3~5% 延迟(每个 cron 多 ~6s overhead);若 chief 自 cycle 进入 busy-loop 反而拖慢 cron
- 回退: git checkout ~/.hermes/profiles/chief/SOUL.md
- 缓解: probe 用 asyncio.gather 并行跑(2s 内完成);verify 用 background task 不阻塞主 cron;audit 只在 08:00 UTC 跑,其他时间不动
- 监测: chief 自 cycle 24h 平均 runtime 是否 > 120% baseline(原 6s → > 7.2s 即报警)
