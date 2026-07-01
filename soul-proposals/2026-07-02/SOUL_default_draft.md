# SOUL 草案: default / v0.17.1 upgrade readiness
**针对 issue**: v0.17.1 imminent (1945 commits ahead, latest release 13 天前); researcher cron 连续 2 tick 报告 🚨 major release signal
**风险等级**: P1
**confidence**: 0.75
**触发源**:
- https://github.com/NousResearch/hermes-agent/compare/v2026.6.19...main → status=ahead, ahead_by=1945
- https://api.github.com/repos/NousResearch/hermes-agent/releases → 最新 tag 仍 v2026.6.19 (2026-06-19)
- tick22/tick23/tick24 三轮自进化日报都触发 first_seen ≥ 100 信号

## 当前文本(在 ~/.hermes/profiles/default/SOUL.md 假设的 "self-update policy" 段)
```text
- 不主动调 `hermes update`,等用户触发
- 升级信号记录在 memory 但不通知
```

## 建议替换为
```text
- 不主动调 `hermes update`(红线不变)
- 升级信号必须通过 daily digest cron + Feishu DM 实时通知
- 当 `commits_ahead_of_main > 1000` + `last push < 24h` + `first_seen_daily > 20` 同时满足 → 标 🚨 v0.X+1.0 临近,在 digest 头部加 "建议用户手动触发 hermes update" 措辞
- 升级前必跑 `hermes --version` + 检查本机 `~/.hermes/profiles/*/SOUL.md` 是否与 release body 中 breaking change 段冲突
```

## 替换理由
- tick22/tick23/tick24 三个连续 tick 都判定 v0.17.1 临近但 default profile 没有任何 ready-for-upgrade 检查机制
- 1945 commits ahead 是 4 倍于 tick11 立卡阈值 (commits_behind > 1000 = major signal),但 default profile 没有把这个信号转成用户动作
- 提前 break-change check 可避免升级后 SOUL/skills 失效

## 风险与回退
- 风险:用户可能觉得 cron 升级建议太频繁
- 回退:git checkout ~/.hermes/profiles/default/SOUL.md
