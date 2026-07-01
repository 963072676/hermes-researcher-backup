# SOUL 草案: qa / session-bleed regression test
**针对 issue**: P1 session context bleeding #56456 (closed but multiplexed gateway still vulnerable)
**风险等级**: P1
**confidence**: 0.75
**触发源**:
- https://github.com/NousResearch/hermes-agent/issues/56456 (P1 closed, but root cause = multiplexed profile env,同 #56508 / #56523 仍未修)
- #56516 (Streaming reasoning models may incorrectly trigger "Provider returned an error")

## 当前文本(在 ~/.hermes/profiles/qa/SOUL.md 假设的 "regression coverage" 段)
```text
- 跑 unit + integration test
- session 边界由 dev 自测
```

## 建议替换为
```text
- qa 必跑 session-bleed regression test:启动 3 session (desktop+telegram+matrix) 同一 Hermes profile,模拟并发 tool call,验证 tool call 不会跨 session 注入
- 跑 streaming reasoning provider 边界测试(#56516),验证 "Provider returned an error" 不会触发假阳性
- sweeper:risk-session-state 标签的 PR → qa 必加一条 session-bleed 用例
- 测试结果不通过 → PR 不可 merge
```

## 替换理由
- #56456 P1 关闭但 dev 都没补 regression test,真实 multiplexed 环境未验证
- qa 是 regression test 唯一 gate,不写就漏
- streaming reasoning 是 v0.17+ 新增 provider class,边界需要 qa 覆盖

## 风险与回退
- 风险:session-bleed test 需要 3 session 同时运行,可能占资源
- 回退:git checkout ~/.hermes/profiles/qa/SOUL.md
