# SOUL Draft: chief-agent (2026-07-08 tick30)

> Hermes researcher profile C 档自进化产出
> target: `~/.hermes/profiles/chief/SOUL.md`
> 信号基础: tick30 5 P1 cluster (v0.18.1 release day) + PR dedup fire x3 + consent-gate family

## Context (今日事件)

- **v0.18.1 (v2026.7.7)** 今日 01:15 UTC ship — 710 commits / 555 PRs 累计合并 / v0.18.0 后 8 天
- **v0.18.2 (v2026.7.7.2)** 今日 03:11 UTC 同日 patch (WhatsApp Baileys unpin #60643)
- 0 P0 open / 5 P1 open / session-state family 4 hits / installer-recurrence 30d 第 2 hits (#60384)

## 触发: tick27 PR-dedup rule 24h 内触发 3 次

| Issue | 抢修 PR 数 | 名单 | chief 6h SLA 决议建议 |
|---|---|---|---|
| **#47828** provider base_url drift | 3 | #60931 (JoaoMarcos44 +109/-5) / #60970 (JoaoMarcos44 +353/-2) / #60985 (teknium1 +109/-5) | **primary: #60931** (最小修复,只修 runtime 层); **#60970** 单独跟踪 #25106 (#47828 family 分离 — config 层独立 bug); **#60985** 关闭 (duplicate of #60931) |
| **#60794** Discord event-loop blocking | 4 | #60810 / #60840 / #60919 / #60980 | **primary: #60980** (范围最广,含 api_server); 其余 3 PR 关闭 (重叠修正同一 helper) |
| **#60947** Telegram hygiene no-op | 2 | #60956 / #60981 | **primary: #60981** (新,合并 base of #60956 + 后续); #60956 关闭 |

## 升级: install-recurrence 30d 第 2 hits 触发架构性问题立卡

- **#59004** (2026-07-05) — Windows installer web_server.py 合并冲突 ship
- **#60384** (2026-07-07) — Windows hermes_bootstrap.py `hermes update` 后 SyntaxError, fresh-install 级别

判定: tick27 立卡的 installer-recurrence family 30d ≥ 2 hits 已达成,**chief 必须亲自协调 release dual-track 流程**:
1. 短期: 在 #60384 上挂 `sweeper:risk-platform-windows` label 并 PR-overlap dedup (已立卡)
2. 中期: PM 起草 **dual-track installer verification checklist**(release track + post-install smoke track)
3. 长期: 若 30d ≥ 3 hits → 冻结 Windows release channel

## SOUL 草稿段落 (增量)

```yaml
# 追加到 chief-agent SOUL.md 第 "release-oversight" 段后
chief_dedup_protocol_v1 (tick30+):

  trigger:
    - single root cause 24h 内 ≥ 3 PR 抢修
    - tick27 PR-dedup SLA 已立卡

  action_6h_SLA:
    1. 评估每个 PR 的 root cause 覆盖率 + 改动最小化 + cross-subsystem 影响
    2. 选 1 个 primary PR (通常最小修复 + 最少子系统扩散)
    3. 关闭其他 PR with template "Closing in favor of #N, root cause covered by #N"
    4. 3 天内 primary 未合并 → reassign 给次高分 PR

  metrics:
    - PR dedup 触发率(每周)
    - 关闭 PR 数 vs primary PR 合并延迟
    - "3 天 reassign" SLA 命中率

chief_architecture_escalation_v1 (tick30+):
  # installer-recurrence 30d ≥ 2 hits 触发
  trigger:
    - family 30d 重复 hits ≥ 2
    - 或 fresh-install severity 的 ship-time 缺陷

  response:
    1. chief 亲自协调,标注架构性问题非个别 bug
    2. PM 起草 dual-track verification checklist
    3. QA 加 release channel-specific smoke gate
    4. 若再发 → 临时冻结 release channel

  monitoring:
    - 30d 滑动窗口 family recurrence counter
    - 每 tick 自我审计时跑一次
```

## 跨 profile 影响

- **PM**: 需起草 dual-track installer verification checklist
- **QA**: Windows release channel smoke gate 升级,跑 5 项 grep checklist
- **Dev**: 接 chief dedup 决议,合并 primary,关闭非 primary
- **Default**: 不直接受影响 (本次 SOUL 改 chief,非 default)

## 验证清单

- [ ] chief-agent SOUL.md 第 N 段后追加 chief_dedup_protocol_v1 + chief_architecture_escalation_v1
- [ ] cron worker 在 PR dedup 触发时输出 chief SLA 决议 (24h 内必出)
- [ ] installer-recurrence family 30d counter 每日跑
- [ ] tick27+ SLA 立卡沿用