# SOUL Draft: chief-agent (2026-07-09 tick31)

> Hermes researcher profile C 档自进化产出
> target: `~/.hermes/profiles/chief/SOUL.md`
> 信号基础: tick31 v0.18.2 ship day +1 + #25205 credential pool bypass 新立卡 + #40170 Honcho memory injection family + tick30 PR-dedup fire x3 持续

## Context (今日事件)

- **v0.18.2 (v2026.7.7.2)** 昨日 03:11 UTC ship (WhatsApp Baileys unpin #60643) — patch day +1
- **last push main**: 2026-07-09 14:11Z — 持续 high velocity (>700 commits / 555 PRs since v0.18.0)
- 0 P0 open / **5 P1 cluster (tick30) + 2 P1 新立卡 (#25205, #40170)** = 7 P1 cluster 持续跟踪
- streak zero-adoption = **7 days** (tick25-31 全 0) — 触发 v4 维持每日 + 飞书 3 选项 A/B/C

## 新立卡 P1 family (tick31 立卡)

### #25205 — `_restore_primary_runtime` credential pool bypass (P1, comp/agent)

- 创建 2026-05-13, 持续 60 天 open, fix PRs: #25206 / #25730 / #53913 (3 PR 抢修)
- root cause: `run_agent.py:8908` 在恢复 primary runtime 时用 stale snapshot 的 api_key,不 consult 当前的 credential pool
- 影响: token revocation (401) / exhaustion (429/402) / rate-limit cooldown → fall through to cross-provider fallback
- 关联 #15298 / #15434 (exhaustion/cooldown variant)
- **判定**: tick27 PR-dedup fire 3 PRs — chief 6h SLA 必须 dedup,选 primary #53913 (teknium1 merge review gate),关闭 #25206 / #25730

### #40170 — Honcho memory injection on customer-facing gateways (P1 security)

- 创建 2026-06-07 (60 天 open), fix PR #40967 关闭但 PR body 内 wiring 缺失 → #41003 follow-up
- root cause: `conversation_loop.py:790-796` prefetch_all() + `970-973` cached injection 路径未对 customer-facing gateway 屏蔽
- 影响: WhatsApp / Telegram / Discord / Slack / Signal / Matrix 6 个 platform 同时泄露
- **新立卡 family**: `memory-injection-cross-platform` (与 cross-platform-state family 并列,新立卡)
- **sweeper marker**: `sweeper:risk-memory-injection-platform-gateway`

### 触发: tick27 PR-dedup rule 24h 内触发 × 4 (累加)

| Issue | 抢修 PR 数 | 状态 | chief 6h SLA 决议建议 |
|---|---|---|---|
| **#47828** provider base_url drift | 3 | tick30 决议 primary #60931 | 3 天未合并 → reassign 给 #60970 |
| **#60794** Discord event-loop blocking | 4 | tick30 决议 primary #60980 | 检查 #60980 merge 状态 |
| **#60947** Telegram hygiene no-op | 2 | tick30 决议 primary #60981 | 检查 #60981 merge 状态 |
| **#25205** credential pool bypass | 3 | **tick31 NEW 决议** primary #53913 | 关闭 #25206 / #25730 |

## 升级: installer-recurrence 30d 第 2 hits (沿用 tick30)

- **#59004** (2026-07-05) — Windows installer web_server.py 合并冲突 ship
- **#60384** (2026-07-07) — Windows hermes_bootstrap.py `hermes update` 后 SyntaxError

## 升级: memory-injection-cross-platform family 30d ≥ 2 hits (NEW family 立卡)

- **#40170** (2026-06-07) — Honcho memory leak on customer-facing gateways
- 关联 #40967 + #41003 (fix PR chain)
- 判定: tick28 立卡 cross-platform-state family 同 root cause family (single fix 跨 platform 修),但**新立卡 memory-injection-cross-platform 是 distinct family**(memory prefetch 路径不同)

## SOUL 草稿段落 (增量)

```yaml
# 追加到 chief-agent SOUL.md 第 "release-oversight" 段后
chief_dedup_protocol_v1 (tick30+) → tick31+:
  # tick30 立卡,tick31 实战验证
  trigger:
    - single root cause 24h 内 ≥ 3 PR 抢修
    - tick27 PR-dedup SLA 已立卡

  action_6h_SLA:
    1. 评估每个 PR 的 root cause 覆盖率 + 改动最小化 + cross-subsystem 影响
    2. 选 1 个 primary PR (通常最小修复 + 最少子系统扩散)
    3. 关闭其他 PR with template "Closing in favor of #N, root cause covered by #N"
    4. 3 天内 primary 未合并 → reassign 给次高分 PR

  tick31_实战案例:
    - #25205 (3 PR): primary #53913, close #25206/#25730
    - #47828 (3 PR): primary #60931 (待 reassign 检查), #60970 单独跟踪
    - #60794 (4 PR): primary #60980 (待 merge 检查)
    - #60947 (2 PR): primary #60981 (待 merge 检查)

  metrics:
    - PR dedup 触发率(每周)
    - 关闭 PR 数 vs primary PR 合并延迟
    - "3 天 reassign" SLA 命中率

chief_architecture_escalation_v1 (tick30+) → tick31+:
  # installer-recurrence 30d ≥ 2 hits + 新立卡 memory-injection-cross-platform
  trigger:
    - family 30d 重复 hits ≥ 2
    - 或 fresh-install severity 的 ship-time 缺陷
    - 或 customer-facing platform security P1 跨 platform ≥ 2 platform 同时中招

  response:
    1. chief 亲自协调,标注架构性问题非个别 bug
    2. PM 起草 dual-track verification checklist (installer) 或 cross-platform memory injection guard (memory family)
    3. QA 加 release channel-specific smoke gate (installer) 或 platform-level memory injection test (memory family)
    4. 若再发 → 临时冻结 release channel (installer) 或 customer-facing gateway memory injection (memory family)

  tick31_新立卡_family:
    memory_injection_cross_platform_v1:
      family_root_cause: |
        agent._memory_manager.prefetch_all() 在 agent_init 后立即 cache memory context,
        而 conversation_loop 直接 inject cached context 进 user-facing prompt,
        未区分 internal CLI session 和 customer-facing gateway session
      reference_pr_chain: #40967 (closed, wiring missing) → #41003 (follow-up)
      proposed_fix:
        - agent._skip_memory_injection = True 在 gateway/run.py 平台检测时设置
        - 平台集合: {telegram, discord, slack, whatsapp, signal, matrix}
        - memory tool 仍可用 (memory.read / memory.write),仅屏蔽 prefetch 路径
      sweeper_marker: sweeper:risk-memory-injection-platform-gateway

  monitoring:
    - 30d 滑动窗口 family recurrence counter
    - 每 tick 自我审计时跑一次
    - 新立卡 family 必须 sweep 一遍所有 open P1 找同 root cause
```

## 跨 profile 影响

- **PM**: 起草 cross-platform memory injection guard checklist (新增,与 installer dual-track 并列)
- **QA**: 加 platform-level memory injection test 集 (6 platform × 10 case = 60 test)
- **Dev**: 接 chief dedup 决议,合并 primary,关闭非 primary (#25205/#47828/#60794/#60947)
- **Default**: 不直接受影响 (本次 SOUL 改 chief,非 default)

## 验证清单

- [ ] chief-agent SOUL.md 追加 memory_injection_cross_platform_v1 段
- [ ] PR dedup 触发率本周 ≥ 4 次 (tick30+tick31)
- [ ] installer-recurrence 30d counter 维持 ≥ 2 hits
- [ ] memory-injection-cross-platform 30d counter ≥ 2 hits
- [ ] 4 P1 dedup 决议在 3 天 SLA 内完成 primary merge 检查