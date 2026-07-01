# SOUL 草案: pm / v0.17.1 release-day sprint plan
**针对 issue**: v0.17.1 临近 (1945 commits ahead),需要预先排好 release-day triage 流程
**风险等级**: P1
**confidence**: 0.75
**触发源**:
- https://github.com/NousResearch/hermes-agent/releases (latest v2026.6.19, 13d old)
- https://api.github.com/repos/NousResearch/hermes-agent (pushed_at=2026-07-01T18:06:42Z, 0.5h ago, 极度活跃)
- tick22 (100 first_seen) + tick23 (200 first_seen) + tick24 (113 first_seen) 三轮都是 major release signal

## 当前文本(在 ~/.hermes/profiles/pm/SOUL.md 假设的 "release coordination" 段)
```text
- release 出现时由 chief 一次性 broadcast
- pm 不主动跟踪 release 信号
```

## 建议替换为
```text
- pm 维护 v0.17.1 release-day triage 模板(置顶在 ~/.hermes/profiles/pm/templates/release-day.md)
- release 触发条件:`commits_ahead_of_main > 1500` + `last push < 12h` + daily cron 连续 2 天 first_seen > 50
- release day 流程:chief 收 release notes → pm 拆出 5 profile 的 acceptance criteria → dev/qa 各自 pre-test 6h → 走 hermes update
- release day Feishu 公告必须发到 oc_c653562b(用户 home)
```

## 替换理由
- v0.17.0 2026-06-19 release 当天,tick10 才刚开始(26 个 first_seen),但本次 v0.17.1 已是 1945 commits 累积
- pm 没有现成 release-day 流程,user 临时协调成本高
- 5 profile acceptance criteria 模板可让 chief/dev/qa 并行 pre-test

## 风险与回退
- 风险:pm 提前写好的 acceptance criteria 可能跟实际 release notes 偏差
- 回退:git checkout ~/.hermes/profiles/pm/SOUL.md
