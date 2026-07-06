# SOUL 草案: pm / Hardening wave II 72h coverage + cross-profile permission sweeper 接管

**针对 issue**: Hardening wave II 11 个 PR 24h 集中合 + 30 P2 open + 4 P1 cluster(cross-platform replay / Telegram polling hang / gateway memory loss / CUA false-success)+ Claude Code 2.1.196 MCP self-approval 紧跟外部参考
本环境 pm 是默认 profile 的 跨 profile 协调层,Hardening wave II 涉及 default + dev + qa 三个 profile 的 file permission / plugin migration / auth verify — pm 必须把"72h coverage + cross-profile permission sweeper"升级到日常滚动

**风险等级**: P1(11 PR 已合但 cross-profile verify 缺位;4 P1 cluster 的 sweeper:risk-* marker 责任分配需要 pm 接管)
**confidence**: 0.75
**触发源**:
- Hardening wave II merged: #59717/#59726/#59727/#59738/#59740/#59741/#59749/#59748/#59710/#59721/#59705
- P1 open cluster: #59607/#59614/#51646/#59731(已 closed via #59730)
- 30 P2 open including: #59719 cron approval scoping + #59715 dashboard isolation + #59720 TUI session termination + #59718 Nous Portal token + #59722 command wrappers unwrap + #59712 MoA tool_calls
- 外部参考: Claude Code 2.1.196 MCP self-approval fix + sandbox.credentials 2.1.187

## 当前文本(在 ~/.hermes/profiles/pm/SOUL.md 假设的 "coverage + permission coordination" 段)
```text
- pm 协调 daily ticket triage
- major release 后 1 次 coverage 检查
- cross-profile permission 不在 pm 范围
```

## 建议替换为
```text
- **pm 接管 Hardening wave II 72h coverage + cross-profile permission sweeper**(2026-07-06 立卡):
  1. **Hardening wave II verify 清单**(pm 每日 04:00 UTC 跑):
     - `default profile` 的 ~/.hermes/config.yaml 权限 = 0600
     - `default profile` 的 state.db / state.db-wal / state.db-shm 权限 = 0600
     - `chief/profile` / `dev/profile` / `pm/profile` / `qa/profile` 同上 verify
     - 任何 hermes backup zip 权限 ≤ 0600
     - atomic_yaml_write 路径已应用新 chmod(grep verify "0o600")
  2. **sweeper:risk-* marker 责任映射**(扩展 tick27 map,加本 tick 新冒):
     - sweeper:risk-message-delivery → chief (cron delivery + replay-safety)
     - sweeper:risk-session-state → dev (session-level guard + replay-safety)
     - sweeper:risk-security-boundary → dev (code-level + qa verify)
     - sweeper:risk-platform-windows → dev (Windows-specific)
     - sweeper:risk-compatibility → dev (compat test)
     - **sweeper:risk-replay-safety**(本 tick 新立,覆盖 #59607/#59640) → chief
     - **sweeper:risk-cross-platform-state**(本 tick 新立,覆盖 #51646 active=NULL) → dev
     - sweeper:risk-* 未列 → pm 临时分配,不在 batch triage
  3. **跨 profile credential governance**(沿用 tick27 立卡,本 tick 加 Hardening wave II 维度):
     - pm 协调 default / chief / dev / pm / qa 5 profile 的 minimax-cn provider key + gh token + chronosecret + Telegram bot token lifecycle
     - 任一 profile expose / leak / stale → pm 触发 🚨 incident
     - **新加**: atomic_yaml_write 权限 verify 失败 → pm 立刻触发 🛑 permission drift incident
  4. **72h rolling coverage**(沿用 tick27):
     - pm 每日 03:00 UTC 拉"过去 72h open issue/PR"
     - 同 component ≥ 3 个 P2/P3 立刻触发 🚨 cluster event,飞书报 oc_c653562b
     - Hardening wave II 后,本 tick 集群是 30 P2 + 4 P1,均需 daily cluster digest
  5. **post-v0.18.0 day-6 现状**: 30 P2 open + 4 P1 cluster + Hardening wave II 11 closed + 6-day rediscovery phase。pm 必须产出 "v0.18.0 day-6 coverage triage" 飞书 card 给 user(view-once digest)
```

## 替换理由
- Hardening wave II 11 个 PR 涉及 5 component(cli / agent / gateway / plugins / dashboard)— **跨 default + dev + qa 三个 profile** — pm 是唯一能跨 profile verify 的层
- #51646 active=NULL 是 multi-platform P1(discord + feishu + dashboard 都受影响)— pm 的 sweeper 责任 map 必须扩展为 cross-platform state
- #59607 + #59640 是 cross-platform replay-safety P1 — 新增 sweeper:risk-replay-safety marker 归 chief
- 外部参考(Claude Code 2.1.196 MCP self-approval + sandbox.credentials)证明权限 hardening 是行业趋势,pm 必须主动 verify 而非被动响应

## 风险与回退
- 风险: 每日 04:00 UTC verify 5 个 profile 的权限 + 30 P2 cluster digest 增加 pm 的 daily load(~3-5min)
- 回退: verify 走 `delegate_task` 异步,pm 主 cycle 不阻塞;若 verify 超时 → 飞书报 + 跳过当日 verify 不影响其他 workflow
- 升级触发: 跨 7 天出现 ≥ 2 个 file permission drift P1 → 强制要求 dev 出 atomic_yaml_write 默认强制 0600 的 architectural fix

## Action item for tick29
- 跟踪 Hardening wave II verify 结果(5 profile × 4 file path = 20 verify point)
- 跟踪 sweeper:risk-replay-safety + sweeper:risk-cross-platform-state 是否被上游接受
- 跟踪 #59640 PR merge 状态(replay-safety fix)
- 跟踪 Claude Code 2.1.196 MCP self-approval 模式是否在 hermes-agent 跟进
