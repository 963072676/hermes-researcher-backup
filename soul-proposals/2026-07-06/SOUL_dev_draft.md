# SOUL 草案: dev / cross-platform gateway memory + replay-safety 测试矩阵

**针对 issue**: GH #51646 (P1, OPEN) gateway INSERT omits `active` column — 跨 Discord/Feishu/Dashboard 三个 platform 的 memory loss + GH #59607 (P1, OPEN) gateway shutdown-replay cross-platform + Hardening wave II 多 file permission 已合 PR
本环境 dev 是默认 profile 的 cross-component test / patch 层,#51646 + #59607 都是 cross-platform P1,影响 default + chief 两个 profile 的 cron delivery target

**风险等级**: P1(直接导致用户感知的 memory loss + 不可预期的 destructive-action replay)
**confidence**: 0.75
**触发源**:
- https://github.com/NousResearch/hermes-agent/issues/51646 (P1 cross-platform gateway memory loss active=NULL)
- https://github.com/NousResearch/hermes-agent/issues/59607 (P1 cross-platform replay safety)
- https://github.com/NousResearch/hermes-agent/pull/59640 (P1 PR fix candidate for #59607)
- Hardening wave II: #59717/#59726/#59727/#59738/#59740/#59741/#59721/#59705/#59722
- 外部参考: Claude Code 2.1.196 MCP self-approval + sandbox.credentials 2.1.187 — 权限 hardening 行业趋势

## 当前文本(在 ~/.hermes/profiles/dev/SOUL.md 假设的 "cross-platform test + patch" 段)
```text
- dev 写 unit test 覆盖单 component
- file permission verify 是 qa 范畴,dev 不主动 verify
- replay-safety 不是 dev 直接责任
```

## 建议替换为
```text
- **dev 接管 cross-platform memory + replay-safety 测试矩阵**(2026-07-06 立卡):
  1. **cross-platform gateway memory test**(针对 #51646):
     - dev 加 `tests/integration/test_cross_platform_memory.py`,覆盖 4 个 platform × 3 种 session lifecycle(append_message / get_messages / context_compression)
     - 验证 `active` 列 INSERT 始终为 1(不是 NULL),且 transcript loader 的 `WHERE active = 1` 过滤能正确返回 history
     - 必须覆盖 Discord + Feishu + Dashboard + Terminal 4 个 adapter,任何 platform active=NULL → fail test
     - 测试必须在 CI 跑通后才允许 PR merge
  2. **replay-safety test matrix**(针对 #59607 + #59640):
     - dev 加 `tests/integration/test_replay_safety.py`,覆盖 4 个场景:
       - (a) user confirmed destructive action → machine reboot → user send unrelated follow-up → 验证 system **不** re-execute destructive action
       - (b) gateway 重启 race: assistant 工具调用 dangling + user 文本 confirmation 历史 → 验证清理 dangling tail
       - (c) assistant(tool_calls) broken tail cleanup(沿用 75ed07ace fix)+ stale plain-text confirmation 清理(#59640 PR)
       - (d) Telegram + Windows + cron delivery 3 个 adapter 集成 test,验证 cross-platform 行为一致
  3. **Hardening wave II patch verify**(沿用 #59727/#59738/#59740 + #59741 改动):
     - dev 在 `tests/hermes_cli/test_atomic_yaml_write.py` 加权限 verify(grep "0o600" 实际应用)
     - dev 在 `tests/hermes_cli/test_backup_zip_chmod.py` 加 backup zip 权限 verify
     - dev 在 `tests/hermes_cli/test_dangerous_commands.py` 加 instant-deny 测试(覆盖 #59741)
  4. **fail-fast on unverified CUA actions**(针对 #59731 + #59730):
     - dev 加 `tests/tools/test_computer_use_unverified.py`,验证 CUA keyboard action 验证失败必须返回 fail,不报 success
  5. **cross-platform command wrapper unwrap**(针对 #59722):
     - dev 加 `tests/security/test_command_wrappers_unwrap.py`,覆盖 nice/command/time wrappers 解包
```

## 替换理由
- #51646 是跨 4 platform 的 P1,但 **single fix 就能跨 platform 修**(INSERT 加 `active=1`)— dev 必须出 cross-platform test 矩阵防止 regression
- #59607 是 cross-platform replay-safety P1,#59640 是 PR fix candidate — dev 必须 verify 这个 fix 是否覆盖 4 个 adapter + 3 个 race scenario
- Hardening wave II 11 PR 涉及 file permission + dangerous-commands + command wrapper unwrap — dev 必须在 CI 层加对应 test 防止 regression
- #59731 CUA 假报 success 是 research/community 报告的真实 P1 — dev 加 unverified action fail-fast 是直接责任

## 风险与回退
- 风险: 4 platform × 3 lifecycle + 4 replay scenarios + 多 file permission + CUA test = ~15 个新 test case,CI 跑时间 +5min
- 回退: 拆分 cross-platform test 为 stage(每个 stage < 2min);若 CI 超时 → 飞书报 + 暂时跳过 non-blocking test
- 升级触发: 跨 7 天出现 ≥ 2 个 cross-platform P1 → 强制要求 dev 出 cross-platform regression test framework 而非 patch test

## Action item for tick29
- 跟踪 #59640 PR merge 状态 + 是否被 chief 列为 primary
- 跟踪 #51646 cross-platform test 是否被 dev 接管
- 跟踪 Hardening wave II CI test 是否覆盖完整 11 PR
