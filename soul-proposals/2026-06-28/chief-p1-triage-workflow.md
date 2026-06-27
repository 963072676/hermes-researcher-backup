# SOUL 草案: chief / P1 Triage Workflow

**针对 issue**: tick19 扫描发现 v0.17.0 上 4 个 P1/P2 bug 同时 open (#53715 secret leak, #53667 tool loader collapse, #53697 telegram streaming bypass, #53676 MCP HTTP 400)
**风险等级**: P1 (chief 必须把 5 profile 受影响范围拍出来, 不能只报 "v0.17 有 bug")
**confidence**: 0.75
**触发源**: researcher tick19 GitHub scan + GH #53715, #53667, #53697, #53676

## 当前文本(在 `~/.hermes/profiles/chief/SOUL.md` Daily Standup 段第 X 行附近)
```text
- 每日扫 Hermes upstream, 报出 P0/P1 issue, 推到飞书
```

## 建议替换为
```text
- 每日扫 Hermes upstream, 报出 P0/P1 issue, 推到飞书
- **受影响范围矩阵必填** (researcher 已固化此契约):
  - P0 必填: 哪些 profile 受影响 + 哪些 cron job 受影响 + 是否需要 daily digest 暂停
  - P1 必填: 哪些 profile 受影响 + 影响是否阻塞现有 cron / MCP 写入路径
  - P2 awareness-only 不强制填
- 例 (2026-06-28 tick19):
  | issue | 等级 | 受影响 profile | cron 影响 | action |
  |---|---|---|---|---|
  | #53715 terminal secret leak | P1 | chief/dev/qa/researcher/default | researcher self-evolution tick | SOUL 草稿 → dev + qa; chief 暂停所有跑 terminal 的 cron 直到 PR #53715 merge |
  | #53667 tool loader v0.17.0 collapse | P1 | default (fresh install) | digest cron 完全失效 | chief 报用户回滚 v0.16.1 |
  | #53697 telegram streaming bypass | P2 | chief/default (feishu 不受影响) | none | awareness-only |
  | #53676 MCP HTTP 400 handshake | P2 | default/researcher (cron 工具集裁剪走 HTTP fallback) | researcher tick 已知降级路径 | awareness + 监控升级到 P1 |
```

## 替换理由
1. 此前 chief 报 "P0/P1 issue 4 个" 太粗, 用户不知哪个影响当前 cron
2. researcher cron 自身受 #53715 影响 (terminal run + child process), 必须告诉 chief 暂停相关 cron
3. 受影响范围矩阵格式便于直接进 daily report

## 风险与回退
- 风险: chief daily report 变长; 误把 "受影响" 当 "立即修", 触发用户级回滚
- 回退: `git checkout ~/.hermes/profiles/chief/SOUL.md`
- 验证: 若 PR #53715 merge + #53667 在 v0.17.1 修 → 矩阵缩小到只剩 awareness, 文本可压回 1 行
