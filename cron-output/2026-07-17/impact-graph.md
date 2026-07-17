# tick39 (2026-07-17) 跨 profile 影响图

## 影响图依赖链

| SOUL 草稿 | 隐含 SOUL | 必须跟进 | 紧迫度 |
|---|---|---|---|
| chief SOUL: arrow_worsening_v1 | pm SOUL v7 + dev SOUL sibling sweep + qa SOUL v9 | pm SOUL 必跑 20-field (F11 fixing 必须 verify arrow) | 6h |
| pm SOUL: acceptance v7 | chief 6h dedup SLA 必须 verify arrow_worsening_check 不空 | chief exec 强制 | 24h |
| dev SOUL: sibling sweep | F11 fix 时 sibling scan F1 silent-fail + F2 cross-platform | weekly Sunday 06:00 UTC | 1 week |
| qa SOUL: ship gate v9 | v8 -> v9 80 checks, --skip-arrow-worsening FORBIDDEN | release time | 立即 |
| default SOUL: mcp readiness v3 | API session identity early-bind (#65102 review) | all profile | 24h |

## cross-cluster arrows

| arrow_id | from_family | to_family | severity | tick39 trigger |
|---|---|---|---|---|
| CCA-F11-F1 | execute-code-approval-unification | silent-fail | B | #60056 + #60897 (Telegram approval swallow) |
| CCA-F11-F10 | execute-code-approval-unification | cron-installer-handoff-state | B | #57563 BWS multiplexing stale |
| CCA-F2-F11 | cross-platform-state | execute-code-approval-unification | C | Slack/Discord/Feishu approval parity (#59163 followup) |
| CCA-F9-F11 (NEW) | session-state-integrity | execute-code-approval-unification | B | #65102 session identity alias + execute_code dispatch |
| CCA-F12 candidate | data-injection-isolation-deck | F1-F11 | tbd | arxiv 2607.05120 ADI |

## family 立卡情况 (tick39)

- 现有 11 family registry (沿用 tick38)
- F12 candidate: data-injection-isolation-deck — pending evidence (tick39 评估: arxiv + Claude Code + Codex + Gemini CLI + Antigravity + Nanobrowser + Claude in Chrome = 7 entities affected, but only 1 paper 1 root cause family)
- family anti-inflation (tick36) 准则: tick39 必须先 verify 是否有 >= 5 GH issue 1 root cause, arxiv paper 不算 (沿用 tick37 single-issue 准则)
- **决议**: F12 立卡 pending — 等 >= 5 GH issue 同 root cause 才立, 本周先 skill draft + awareness only

## timeline

| 时间 (UTC) | 事件 |
|---|---|
| 02:00 | cron tick39 启动 (本日) |
| 02:15 | web search 信号拉回 (~5 calls) |
| 02:20 | GitHub API probe (~5 calls) |
| 02:30 | SOUL 草稿生成 (5) |
| 02:40 | skill 草稿生成 (3) |
| 02:50 | impact graph + audit log 生成 |
| 03:00 | MCP propose_write 4 条 |
| 03:15 | git commit + push |
| 03:30 | 飞书 deliver (auto) |
