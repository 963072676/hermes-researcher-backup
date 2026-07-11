# SOUL 草案 — dev — silent-fail cron gateway still open after v0.18.2 (tick33)

> Tick33 2026-07-12 | Author: researcher profile | Streak=9 zero-adoption
> Memory ID: af81023e-2f64-4600-8a24-d38330670134 (MCP pending_review)
> Family: silent-fail cron gateway (沿用 tick27 立卡, v0.18.2 验证未根治)

## 触发 evidence (v0.18.2 patch wave 仍未根治 silent-fail)

| 路径 | 状态 | 备注 |
|---|---|---|
| #62151 (gateway deadlock cron tool-call) | open | inactivity watchdog 被 `_touch_activity("waiting…")` 心跳致盲 |
| #62198 (fix PR for #62151) | open | 拆 `seconds_since_progress` vs `seconds_since_activity` |
| #60350 (HERMES_CRON_SESSION spill) | open | env spill cleanup in job finally — 5 PRs 抢修 |
| #57124 / #60386 / #56796 / #56784 (fix PRs) | open | 4 PR 抢同一 root cause |
| #56771 (sister) | open | env spill cross-cron |
| #61581 / #61525 / #61382 (freeze triad) | **closed 2026-07-10** | tick32 立的 P1 cluster 已 closed (merged_at=null — 记 closed 不宣称 confirmed merge) |
| #60683 (MiniMax stream AttributeError) | open | fix PRs #60695/#60700 open; teknium1 review 要求 `chat_completion_helpers` 主路径 fallback |
| #60685 (hermes update setup.py pin downgrade) | open | **升级红线加证** — 仍禁止 unattended `hermes update` |
| #62212 + #62220 (MCP stdio keepalive 空异常无限重连) | open | MCP keepalive 无限重连 — knowledge MCP 风险 |

**判定**:v0.18.1 + v0.18.2 patch wave (2026-07-07/08) ship 后 4 天,核心 silent-fail cluster **仍未根治**。**fix PR 抢修 ≥ 4 个同 root cause**(沿用 tick27 PR dedup 模式)但根因仍 open。

## 草案 (dev SOUL v2 第 9 段追加)

```diff
+ ## Silent-Fail Cron Gateway v2 (tick33 立卡)
+
+ **原则**:任何 silent-fail P1 必须 4 验收清单全部满足,缺一即视为未根治。
+
+ 4 验收清单 (tick27 + tick33 合并):
+ 1. **失败注入用例** — 必跑模拟 env spill / gateway deadlock / MCP keepalive hang 三类 scenario,每个 scenario ≥ 3 case
+ 2. **日志可观测性** — failure mode 必须 log at ERROR level(沿用 tick27 #32666 logging escalation) + atomic write ticker_heartbeat (沿用 tick33 cron-ticker-resilience deck invariant #1)
+ 3. **Delivery receipt** — 每个 cron job 投递路径必须 emit delivery receipt (success / failure / timeout / skipped 四态),feishu DM 必须可见
+ 4. **Silent-drop counter** — gateway 必须 maintain counter for `silent_drop_total` (gateway.log INFO metric),counter increase ≥ 1 → WARN, ≥ 10 → page chief
+
+ **Dev 必跑 PR dedup 6h SLA**: silent-fail family PR ≥ 3 同 root cause → dev 6h 内 dedup,选 1 primary(沿用 tick27 #58777/#58874/#58992 模式)。
+
+ **PR-dedup 当前 tick33**:
+ - HERMES_CRON_SESSION spill: #57124 / #60386 / #56796 / #56784 (4 PRs 抢修)
+ - gateway deadlock #62151: #62198 (1 PR 但属同一 family)
+ - MiniMax stream #60683: #60695 / #60700 (2 PRs)
+
+ 4 验收清单必填入 PR template(`hermes_agent/.github/PULL_REQUEST_TEMPLATE.md`)。
+
+ **family 标识**: `sweeper:risk-silent-fail-cron-gateway`(沿用 tick27 sweeper:risk-cron-session-leak + 新增 silent-fail-cron-gateway)
```

## 配套 skill 升级

- `hermes-silent-fail-counter` (新立) — `silent_drop_total` counter + feishu DM 通知脚本
- `hermes-cron-delivery-receipt` (新立) — 4 态 receipt emitter

## 优先级

P1: 本 cron worker 直接高优级 (silent-fail 影响日终汇总可靠性)

## 关联 references

- 草稿落地: 本文件
- MCP memory_id: af81023e-2f64-4600-8a24-d38330670134 (pending_review)
- 关联 issue/PR: #62151, #62198, #60350, #57124, #60386, #56796, #56784, #56771, #60683, #60685, #61581, #61525, #61382, #62212, #62220
- 关联 family: silent-fail (tick27), cross-platform-state (tick28), cron-session-leak-closed-state (tick32)

## 下一步

1. user review → dev SOUL v2 第 9 段合并
2. `scripts/release-verification.sh` 升级 — 跑 4 验收清单 silent-fail scenario
3. cross-profile verify 必跑 (沿用 tick28 hardening wave II verify 模式)