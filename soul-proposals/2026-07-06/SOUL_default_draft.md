# SOUL 草案: default / cross-platform Hardening wave II + MCP self-approval 防御

**针对 issue**: Hardening wave II 11 PR 24h 合 + 4 P1 cluster(#59607/#59614/#51646/#59731→59730)+ Claude Code 2.1.196 MCP self-approval fix + ToolHijacker 96.7% attack success rate
本环境 default profile 是所有其他 profile 的 baseline,所有 cron worker / SOUL 草稿 / skill 草稿都默认走 default 的 dispatcher — Hardening wave II 11 PR 直接影响 default 的 atomic_yaml_write / state.db / backup zip / dangerous-commands + MCP trust surface

**风险等级**: P1(default profile 是 baseline,任何 default permission drift 会级联到所有子 profile)
**confidence**: 0.75
**触发源**:
- Hardening wave II merged: #59717/#59726/#59727/#59738/#59740/#59741/#59749/#59748/#59710/#59721/#59705
- P1 cluster: #59607/#59614/#51646
- MCP self-approval fix 参考: Claude Code 2.1.196 (.mcp.json 自审批关闭 + Remote Control bind Anthropic host)
- ToolHijacker arXiv NDSS 2026 (96.7% tool selection attack success)

## 当前文本(在 ~/.hermes/profiles/default/SOUL.md 假设的 "baseline security" 段)
```text
- default profile 是 baseline,不做特殊 verify
- file permission 卫生归 qa,default 信任 upstream
- MCP trust 是 dev 范畴
```

## 建议替换为
```text
- **default 接管 cross-platform Hardening wave II + MCP trust baseline**(2026-07-06 立卡):
  1. **cross-platform Hardening wave II verify**(本 tick 升级):
     - default profile 每日 06:00 UTC 跑 `verify_hardening_wave_ii.sh`:
       - `~/.hermes/config.yaml` 权限 = 0600
       - `~/.hermes/state.db` / `state.db-wal` / `state.db-shm` 权限 = 0600
       - `~/hermes-backups/*.zip` 权限 = 0600
       - `atomic_yaml_write` 路径(grep verify "0o600")已应用
     - 任何 verify 失败 → 立即触发 `hermes config repair-permissions` 自动 chmod,不阻塞 cron
     - 自动 chmod 失败 → 飞书报 🚨 "permission drift"
  2. **MCP self-approval baseline**(参照 Claude Code 2.1.196):
     - default profile 的 MCP 配置 `~/.hermes/mcp/config.yaml`:
       - 任何 untrusted repo 的 `.mcp.json` 自审批 → **默认拒绝**,必须 user 显式 approve 才生效(参照 Claude Code 2.1.196)
       - 任何 MCP server 的 stdio subprocess 在 gateway 重启 / cron shutdown 时必须 reap(参照 #59705 修)
       - Remote Control 类插件必须 bind 到已知 host(localhost / 已知 IP),不接受 ANTHROPIC_BASE_URL 重定向
  3. **ToolHijacker 防御 baseline**(arXiv NDSS 2026 96.7%):
     - default profile 禁用未 verify 的 tool library 注入(任何 user 提供的 tool library 必须经 dev + qa 双重 review)
     - Tool selection 必须有 known-answer detection(per ToolHijacker paper 防御段)
     - perplexity detection 用于 flag unusual tool selection
  4. **replay-safety baseline**(针对 #59607):
     - default profile 的 destructive-confirmation 历史(任何 user 确认过 destructive action)在 session restart / host reboot 后必须 **invalidate**,不 re-execute
     - 任何 dangling `assistant(tool_calls)` tail 在 new session 必须 cleanup(沿用 75ed07ace fix)
  5. **cross-platform memory baseline**(针对 #51646):
     - default profile 的 hermes_state.py `append_message` INSERT 必须显式 `active=1`,不允许依赖 SQLite DEFAULT(防止 schema drift)
     - 任何 platform gateway(Discord / Feishu / Dashboard)的 memory load 都走相同 active=1 过滤
```

## 替换理由
- default profile 是 baseline,任何权限 drift 会级联到所有子 profile 的 cron / dispatcher
- Hardening wave II 11 PR 是 v0.18.0 后立即跟进的权限 hardening,default 必须 verify 完整落地
- MCP self-approval 是 2026-07-01 Claude Code 2.1.196 的关键 fix,hermes-agent 跟进参考 — default 必须 baseline 化
- ToolHijacker 96.7% attack success rate 证明 tool selection 攻击面大,default 必须 baseline 防御
- #59607 + #51646 是 cross-platform P1,default profile 是唯一能跨 platform baseline 化的层

## 风险与回退
- 风险: 每日 verify + auto-repair 增加 default 的 cron latency(~5s overhead);MCP self-approval baseline 可能影响开发体验
- 回退: verify + auto-repair 走 `delegate_task` 异步,default 主 cycle 不阻塞;MCP self-approval baseline 提供 `--allow-untrusted-mcp` flag 用于开发场景
- 升级触发: 跨 7 天出现 ≥ 2 个 permission drift P1 或 ≥ 1 个 MCP 攻击成功 → 强制要求 chief + qa 出 architectural hardening 而非 patch PR

## Action item for tick29
- 跟踪 verify_hardening_wave_ii.sh 是否在 CI 默认跑
- 跟踪 MCP self-approval baseline 是否被 user 接受(可能影响开发体验)
- 跟踪 ToolHijacker 防御是否纳入 hermes-agent upstream
- 跟踪 cross-platform memory + replay-safety baseline 是否覆盖完整 5 profile
