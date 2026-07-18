# tick40 (2026-07-18) 跨 profile 影响图

## 影响图依赖链

| SOUL 草稿 | 隐含 SOUL | 必须跟进 | 紧迫度 |
|---|---|---|---|
| chief SOUL: execute_code_dispatch_unification_v1 | pm SOUL v8 + dev SOUL sibling sweep v2 + qa SOUL v10 + default SOUL v4 | chief 6h SLA 内 dedup #60077+#60799 (F11) + verify arrow_worsening_check 不空 | 6h |
| pm SOUL: canonical_invocation_path_v1 | chief 6h dedup SLA 必 verify 21-field v8 acceptance (含 canonical_invocation_path_audit 5 sub-fields) | PM 跑 acceptance 默认 21-field, 缺 canonical_invocation_path_audit 视为 incomplete | 24h |
| dev SOUL: family_sibling_sweep_v2 | F1+F2+F7+F8+F9+F10+F11+F12 candidate 11 family 全 sweep + evidence freshness 评分 | weekly Sunday 06:00 UTC 必跑 | 1 week |
| qa SOUL: ship gate v10 | v9 → v10 80→88 verify, 4 canonical invocation path + 4 family 12 verify | release time + 4 FORBIDDEN skip flag | 立即 |
| default SOUL: mcp readiness v4 | v3 → v4 10→13-control, canonical_invocation_path + audit_log_field_strict + family_12_verify_runtime | all profile + 5 install profile verify | 24h |

## cross-cluster arrows (tick40 评估)

| arrow_id | from_family | to_family | severity | tick40 trigger |
|---|---|---|---|---|
| CCA-F11-F1 (tick39 → tick40 强化) | execute-code-approval-unification | silent-fail | B | #60056 silent drop + #60897 Telegram approval swallow |
| CCA-F11-F10 (tick39) | execute-code-approval-unification | cron-installer-handoff-state | B | #57563 BWS multiplexing stale |
| CCA-F2-F11 (tick39) | cross-platform-state | execute-code-approval-unification | C | cross-platform approval rule_key parity |
| CCA-F9-F11 (tick39) | session-state-integrity | execute-code-approval-unification | B | #65102 session identity alias + execute_code dispatch |
| **CCA-F11-F7 (tick40 NEW)** | execute-code-approval-unification | MCP-supply-chain-protocol-migration | B | execute_code RPC 用 MCP tool wrapper (#34497 dispatch) 必过 MCP 6-control |
| **CCA-F11-F8 (tick40 NEW)** | execute-code-approval-unification | cron-ticker-resilience-deck | C | kanban_worker auto-approve (cron-derived) + #63183 |
| **CCA-F12-F7 (tick40 NEW)** | data-injection-isolation-deck (candidate) | MCP-supply-chain-protocol-migration | B | tool poisoning + MCP supply chain (arxiv 2604.17125 CASCADE) |
| **CCA-F12-F11 (tick40 NEW)** | data-injection-isolation-deck (candidate) | execute-code-approval-unification | C | execute_code + tool description poisoning |

## family 立卡情况 (tick40)

- 现有 11 family registry (沿用 tick38)
- F12 candidate: data-injection-isolation-deck — pending evidence (tick39 + tick40 评估: arxiv 2607.05120 ADI + 2601.17549 ProtoAmp + 2604.17125 CASCADE, 7 entities affected Claude Code / Codex / Gemini CLI / Antigravity / Nanobrowser / Claude in Chrome / Cursor)
- family anti-inflation (tick36 + tick37) 准则: tick40 评估 condition 2 (≥ 3 platform 同根) 满足, 但 condition 1 (≥ 5 GH issue 同根) 未满足
- **决议**: 维持 F12 candidate, tick41+ 拉新 GH issue 时重评估立 family 阈值

## F11 evidence 拉新 (tick40)

- #60056 (P2 → P1 候选, autonomous VCS mutation) - valmy 报 execute_code 绕过 DANGEROUS_PATTERNS pipe-to-interpreter 块 → gh pr merge --squash --delete-branch 成功
- #21563 (P2, MCP bridge approval tools no-ops)
- #63183 (P2, Kanban worker approval context drop)
- #34497 (merged, execute_code RPC context restore baseline)
- #30882 (merged, gateway manual approval bypass)
- #32776 + #27492 (cron lifecycle guard, 沿用)
- 5+ evidence 满足 tick38 立卡阈值

## F8 evidence 拉新 (tick40)

- #61674 (P1 open, lazy jobs.json path)
- #39782 (P1 open, cron inactivity timeout containment)
- #32612 (closed, ticker dies silently 15.5h, 已 merged fix)
- #27485 (open, tick lock held for full job duration, 已 fix PR #27492)
- #32666 (merged, ticker keep alive)
- 5 evidence 同 root cause cluster

## timeline

| 时间 (UTC) | 事件 |
|---|---|
| 18:01 | cron tick40 启动 |
| 18:05 | backup repo + gh auth + 路径验证 (OK) |
| 18:10 | 5 路数据源 web_search 并发 (hermes / Anthropic / MCP / AI 安全 / arxiv) |
| 18:15 | MCP URL probe (localhost:18080 OK) + schema probe (6 字段 active) |
| 18:18 | 4 条 MCP propose_write (c42cae0d + 4b0d001e + 780b3a5e + 05fed071) 全部 pending_review |
| 18:20 | SOUL 草稿 5 条 (chief / pm / dev / qa / default) |
| 18:25 | skill 草稿 3 条 (canonical-invocation-path + cron-lazy-path + agent-data-injection) |
| 18:28 | impact graph + audit log 生成 |
| 18:30 | pre-commit Python secret verifier (PASS) |
| 18:32 | git commit + push |
| 18:35 | 飞书 deliver (auto) |