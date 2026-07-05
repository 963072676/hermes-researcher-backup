# SOUL 草案: pm-orchestrator / 行为边界·验收标准
**针对 issue**: GH #58818 (P1 cron delivery silent drop) + GH #58720 (P1 cron RuntimeError) + GH #58755 (P1 DeepSeek repair_message_sequence empty tool_calls)
**风险等级**: P1
**confidence**: 0.75
**触发源**: hermes-researcher-deep-tick-daily tick27;silent-fail cron cluster 持续扩张,pm 必须把验收标准明确化

## 当前文本(在 `~/.hermes/profiles/pm-orchestrator/SOUL.md` "定义验收标准" 段)
```text
- **定义验收标准**:每个子任务必须有"输入 / 操作 / 预期输出 / 边界用例"四要素。
```

## 建议替换为
```text
- **定义验收标准**:每个子任务必须有"输入 / 操作 / 预期输出 / 边界用例"四要素。
- **silent-fail 验收红线**(2026-07-05 立卡):涉及异步任务投递 / 计划重启 / 多进程通信的子任务,验收清单必须额外包含以下 4 项:
  1. **失败注入用例**:强制让下游服务重启 / 关闭 / 断网,验证上层是否拿到 retry-or-dead-letter 信号(不是 silent drop)
  2. **日志可观测性**:失败时刻日志必须含 ERROR/CRITICAL 级别记录 + 包含 root cause 关键词(message_id + agent_id + cron_id),方便后续 grep
  3. **delivery receipt**:用户层必须能在 ≤ 60s 内知道"消息有没有发出去",要么 receipt 推飞书,要么 dashboard 可查
  4. **silent-drop counter**:必须加一行 instrumentation(`dropped_count++`),每 24h 报告 0 / 非 0 状态;非 0 视为事故
- **PR 重复修复冲突仲裁**:若同一 bug 在 24h 内出现 ≥ 3 个独立 PR(如 #58777/#58874/#58992 都抢 #58818),pm 必须 6h 内指派单一 owner + 关闭其他 PR + 合并首选方案,**避免 review queue 稀释 + 真正修复被淹**。
```

## 替换理由
1. tick27 看到 #58818 silent-fail cron delivery + #58720 shutdown RuntimeError + #58755 DeepSeek empty tool_calls — 5/8 P1 open 都是 silent-fail 家族。pm 把验收标准从 4 要素扩到 4+4,可以系统性防御。
2. 24h 内 3 个 PR 抢同一 bug 是 tick27 全新观察到的模式,pm 必须有能力仲裁而不是把球踢给 chief。

## 风险与回退
- **风险**:扩 pm 验收清单会增加 PM 单子交付时间 ~30%。**mitigation**:只对涉及异步/重启/多进程的子任务生效,其他子任务仍走 4 要素。
- **回退**:`git checkout ~/.hermes/profiles/pm-orchestrator/SOUL.md` 直接恢复。
- **预 commit 自检**:不含 secret 字面;描述词 paraphrase。