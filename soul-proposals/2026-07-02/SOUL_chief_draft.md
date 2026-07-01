# SOUL 草案: chief / risk-aware dispatch section
**针对 issue**: v0.17.1 imminent (1945 commits ahead of v0.17.0); P1 session context bleeding (#56456 closed) still affects cross-profile coordination
**风险等级**: P1
**confidence**: 0.75
**触发源**:
- https://github.com/NousResearch/hermes-agent/issues/56456 (P1 session context bleeding, closed-but-not-merged-on-affected-branches)
- https://github.com/NousResearch/hermes-agent/issues/56508 (P2 sweeper:risk-security-boundary — multiplexed profile env)
- https://github.com/NousResearch/hermes-agent/issues/56523 (P2 sweeper:risk-session-state — same root cause)

## 当前文本(在 ~/.hermes/profiles/chief/SOUL.md 假设的 "dispatch" 段)
```text
- 派工前不强制做 cross-profile isolation check
- 接受同 gateway 多 session 并行(默认 desktop + telegram 一起跑)
```

## 建议替换为
```text
- 派工前必须核验 target session 与当前 session 来自不同 Hermes profile;同 profile 跨 session 并行前先跑 `security_context_isolation_check`
- 收到 sweeper:risk-session-state / sweeper:risk-message-delivery 标签的 issue 立即升 P1,触发 chief → dev → qa 三方 review
- 多平台 gateway (desktop+telegram+matrix) 共存时,默认开启 session_fence=true
```

## 替换理由
- #56456 已证实在 desktop+TUI+Telegram 多 session 并发时会出现"另一个 session 的 tool call 注入到当前 session",且 fix 处于 P1 closed-but-multiplexed-gateway-still-vulnerable 状态
- chief 是派工中枢,出问题最先体现在 chief 派工的 session 里
- 默认开启 session_fence 避免 dev/qa 各自再手动加 fence,降低出错面

## 风险与回退
- 风险:session_fence 可能让 dev/qa 的快速切换变慢(额外一次 isolation check)
- 回退:git checkout ~/.hermes/profiles/chief/SOUL.md
