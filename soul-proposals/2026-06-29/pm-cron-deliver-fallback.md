# SOUL 草案: pm / cron deliver=origin silent drop

**针对 issue**: GH #54329 (Issue open, P2) — deliver=origin cron reminders are silently dropped when the origin thread/channel is deleted or inaccessible
**风险等级**: P2 user-facing silent failure
**confidence**: 0.85
**触发源**: https://github.com/NousResearch/hermes-agent/issues/54329

## 当前文本(在 ~/.hermes/profiles/pm/SOUL.md — 假设在「cron deliver」段)

> cron deliver: 若 deliver target 不可达, 写本地 log + 标 status=failed; 不重试

## 建议替换为

> cron deliver fallback chain:
> 1. **try origin** (deliver=origin → 原始 thread/channel)
> 2. **on failure** (origin deleted/archived/permission-lost): 自动 fallback 到 `deliver=home` (用户的 home DM)
> 3. **on home failure**: 写本地 log + 标 status=critical (比 failed 高一档)
> 4. **每次 cron fire**: 包含「deliver path」 audit log, 用户能在 dashboard 看到「if origin lost, fallback to home」
>
> **用户感知**: 用户应明确知道 reminder 是否真的送达, 不接受 silent drop

## 替换理由

- #54329 是 "worst failure mode for a scheduled job" — 用户以为 reminder 设了, 实际从未送达
- 本环境 researcher cron deliver=feishu:oc_c653562b (home DM), **已是最稳 target**; 但 PM 用户实际用的是 deliver=origin (PM cron 在用户群里跑), **受此 bug 直接影响**
- 飞书 cron 是 09:00 UTC 17:00 北京日报, 若群临时不可达, 应 fallback 到 home DM 而非 silent drop

## 风险与回退

- **风险**: 自动 fallback 到 home DM 可能误报;用户期望收到 reminder in 群
- **回退**: 关闭 fallback, 仅标记 status=failed; `git revert` pm SOUL 段

## 实测锚点

本环境 PM profile cron:
```bash
hermes cron list --profile pm | grep deliver
# 若有 deliver=origin, 受 #54329 影响
```