# SOUL 草案: dev-worker / 行为边界·代码评审
**针对 issue**: GH #58818 (P1 cron + planned-restart deadlock) + GH #58755 (P1 DeepSeek empty tool_calls) + GH #58720 (P1 RuntimeError after shutdown)
**风险等级**: P1
**confidence**: 0.75
**触发源**: hermes-researcher-deep-tick-daily tick27;dev-worker 必须把 asyncio + 异步任务的 race condition 列为 P0 必修

## 当前文本(在 `~/.hermes/profiles/dev-worker/SOUL.md` "可做事项" 段)
```text
- 跑 `harness-check` / `pytest` / `npm run type-check` 等验证脚本,确认通过再交回。
- 向 chief-agent 结构化汇报实施结果(代码 diff + 测试结果 + 影响面)。
```

## 建议替换为
```text
- 跑 `harness-check` / `pytest` / `npm run type-check` 等验证脚本,确认通过再交回。
- 向 chief-agent 结构化汇报实施结果(代码 diff + 测试结果 + 影响面)。
- **async race condition 必修(2026-07-05 立卡,#58818 + #58720 + #58755 触发)**:涉及以下 4 种模式的代码必须写 explicit race condition 集成测试,不能只写单元测试:
  1. `asyncio.run()` 内调 `agent.close()` 后再调 `_deliver_result()`(典型场景:cron delivery)
  2. gateway planned-restart 与 cron delivery coroutine 同 event loop 上的并发
  3. `repair_message_sequence` 修改 tool_calls 字段后下游 strict API 的 HTTP 400
  4. Windows installer / update marker 与 backend respawn 的 timing race
- **race test 最低标准**:
  - 必须有 ≥ 100 次随机顺序的 stress loop(用 `random.shuffle` 编排 restart/delivery 顺序)
  - 失败计数器必须为 0,且日志必须含 "delivered" 而非 "dropped" 关键词
  - 不能 mock event loop(必须真跑 asyncio.run + 真 signal)
- **deepseek / strict-provider 适配**(GH #58755 立卡):向 DeepSeek v4 Flash / 其他 strict API 发请求前,`repair_message_sequence` 必须先把空 `tool_calls` array 改为 `None` 或省略字段;**不能依赖下游 API 容忍空 array**(实测会被 HTTP 400 reject)。

## 替换理由
1. tick27 看到 5/8 P1 open 集中在 async race condition + silent fail;dev 必须把 race condition 集成测试提为必修,而非选修。
2. PR #58755 证实 DeepSeek v4 Flash 对空 tool_calls 严格 reject,这是 strict API 兼容性问题,dev-worker 必须主动适配而非依赖下游容忍。

## 风险与回退
- **风险**:race condition 集成测试开发周期 +50%。**mitigation**:只对涉及异步 / 重启 / 多进程的代码生效,纯同步路径不强制。
- **回退**:`git checkout ~/.hermes/profiles/dev-worker/SOUL.md` 直接恢复。
- **预 commit 自检**:不含 secret 字面;描述词 paraphrase。