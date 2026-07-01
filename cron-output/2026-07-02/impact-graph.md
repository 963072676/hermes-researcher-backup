# 跨 profile 影响图 (2026-07-02)

Tick 24 (researcher cron) — 113 first-seen signals, 5 P0/P1 cluster triggers cross-profile dependency chain.

| 触发 | 直接影响 | 隐含影响 | 风险 | 处理 |
|---|---|---|---|---|
| **GH #56456** session context bleeding (P1, closed but multiplexed path vulnerable) | chief 必须加 session_fence=true; dev 必须补 multiplexed env test | qa 必跑 session-bleed regression;default 必须升级 v0.17.1+ | **P1** | SOUL_chief + SOUL_dev + SOUL_qa drafts |
| **GH #56508** multiplexed HOOKS_DIR resolve (P2 security) | dev 必须改成 per-request resolve | chief 派工时若仍走 import-time → bleed | **P1** | SOUL_dev draft |
| **GH #56523** multiplexed SKILLS_DIR resolve (P2 sweeper:risk-session-state) | dev 同上,skills_sync 也要 per-request | qa 必跑 skills_dir cross-session 测试 | **P1** | SOUL_dev + SOUL_qa drafts |
| **v0.17.1 imminent** (1945 commits ahead) | pm 必排 release-day triage;default 必跑 pre-upgrade check | chief 必须先做 isolation check 才能让 default 升级 | **P1** | SOUL_pm + SOUL_default drafts |
| **GH #56540** Telephony API JSONDecodeError leak (P3) | dev 必修 _json_request 异常路径 | qa 加 malformed-body 用例 | **P3** | awareness only |
| **GH #56558** clarify.respond 4009 leak (no label) | dev 必加 expired-prompt path graceful return | chief 派工 clarify 类任务时若 expired 不能 hard-fail | **P2** | awareness,待 PR 标 P |
| **HN 52pt** "Hermes Agent – Open-source AI agent with persistent memory" | pm 收集社区解读;default 关注 brand reputation | dev 不动;qa 不动 | awareness | HN digest only |
| **MiniMax-M3 OR pricing stable** (0.30/1.20 USD per M) | default profile 走 custom:minimax-cn 不直接受影响 | awareness | awareness | OpenRouter 监控持续 |

## 跨 profile 依赖链详解

### 链 1: 升级 v0.17.1 前的 isolation check
```
default (升级触发) → chief (security_context_isolation_check)
                  → dev (verify_session_fence)
                  → qa (regression suite)
                  → pm (acceptance criteria digest)
                  → default (post-upgrade health check)
```

### 链 2: session-bleed fix 落地
```
dev (multiplexed per-request resolve) → qa (regression test 必含 session-bleed)
                                     → chief (派工时强制 session_fence=true)
                                     → default (升级到含 fix 的 v0.17.1)
```

## 用户 review 行动项

1. **回 ✅ 采纳 SOUL 5 草稿** → 落到 default profile 后 cron 自动覆盖
2. **回 ✏️ 改写** → 标注哪条要改,researcher 下个 tick 改
3. **回 🔇 静音** → 当日 proposals 不再推送
4. **3 skill 草稿** → 决定是否注册到 `~/.hermes/skills/` 还是 `~/.hermes/profiles/researcher/skills/`
