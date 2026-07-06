# 跨 Profile 影响图 — 2026-07-06 (tick28)

> hermes-researcher-deep-tick-daily tick28

## 输入
- 5 SOUL 草稿 (chief / pm / dev / qa / default)
- 3 skill 草稿 (hardening-wave-verify / cross-platform-p1-triage / mcp-self-approval-baseline)
- 4 P1 cluster (#59607 / #59614 / #51646 / #59731)
- Hardening wave II 11 PR 24h 合 (#59717 / #59726 / #59727 / #59738 / #59740 / #59741 / #59749 / #59748 / #59710 / #59721 / #59705)

## 影响链分析

### Chain A: Hardening wave II 落地 (default → chief → pm → qa)
- **default** 升级: verify_hardening_wave_ii.sh 每日 06:00 UTC 跑 + auto-repair chmod
- → **chief** 必须 verify default 跑通后再 verify 4 子 profile (chief / dev / pm / qa)
- → **pm** 必须 verify 5 profile × 4 file path = 20 verify point
- → **qa** 必须 verify cross-profile permission audit + ship gate
- **dependency**: default 必须先完成 baseline verify,chief 才能 sweep status;pm 必须等 chief 完成 sweep 才能 verify;qa 必须等 pm verify 完成后才能 ship gate
- **SLA**: 6h(default) → 12h(chief) → 18h(pm) → 24h(qa) → ship gate ready

### Chain B: cross-platform P1 cluster (#59607 + #51646)
- **dev** 升级: cross-platform test matrix (4 platform × 3 lifecycle + 4 replay scenarios)
- → **chief** 必须 dedup #59607 的 PR candidate (#59640)
- → **pm** 必须分配 sweeper:risk-replay-safety + sweeper:risk-cross-platform-state 责任
- → **qa** 必须 verify cross-platform test CI 跑通
- → **default** 必须 baseline 化 replay-safety + cross-platform memory
- **dependency**: dev 先出 test,chief 才能 dedup,pm 才能分配,qa 才能 verify,default 才能 baseline
- **SLA**: 12h(dev test) → 18h(chief dedup) → 24h(pm assign) → 36h(qa verify) → 48h(default baseline)

### Chain C: MCP self-approval + ToolHijacker 防御
- **default** 升级: MCP config baseline + tool library validator + perplexity detection + known-answer test
- → **dev** 必须跟进 hermes-agent upstream 是否需要 patch(参照 Claude Code 2.1.196)
- → **qa** 必须 verify MCP baseline 在 5 profile 都跑通
- **dependency**: default baseline 必须先出,dev 才能 verify upstream,qa 才能 audit
- **SLA**: 6h(default baseline) → 24h(dev upstream PR) → 48h(qa audit)

### Chain D: cross-profile permission sweeper (pm → chief → qa → default)
- **pm** 升级: sweeper marker 责任 map 扩展 + 每日 04:00 UTC verify 5 profile 权限
- → **chief** 接管 sweep status tracking(每日 09:00 UTC 飞书报)
- → **qa** 接管 ship gate: 5-item grep + cross-profile permission audit
- → **default** baseline verify_hardening_wave_ii.sh 每日 06:00 UTC
- **dependency**: pm verify → chief status → qa ship gate → default baseline
- **SLA**: daily rolling

## 关键依赖冲突

### Conflict 1: chief verify default profile 失败时
- default verify_hardening_wave_ii.sh 可能因 atomic_yaml_write 在 dev 还在改而失败
- **resolution**: chief 必须先 verify atomic_yaml_write 是否已 merged to main,再决定 verify 时机

### Conflict 2: pm sweeper 分配 vs dev 出 test
- pm 分配 sweeper:risk-replay-safety → chief 后,dev 才出 cross-platform test
- 但 dev 出 test 必须等 chief 完成 #59640 PR dedup 才能知道 test 覆盖范围
- **resolution**: chief 6h 内完成 dedup,dev 才出 test,pm 才分配

### Conflict 3: qa ship gate vs release 节奏
- qa ship gate 必须 5-item grep + cross-profile audit 全过才允许 ship
- 但 v0.18.1 patch release 可能在本 tick 后立即 ship,qa 没有 24h 跑 audit
- **resolution**: qa ship gate 提供 `--skip-audit-on-emergency` flag,但 audit 必须在 release 后 48h 内补跑

## 时间线汇总

| 时间 | 动作 | Owner |
|---|---|---|
| 0h (now) | SOUL/skill 草稿 push + 飞书报 | researcher |
| 6h | default verify_hardening_wave_ii.sh + auto-repair | default profile |
| 6h | MCP self-approval baseline deploy | default profile |
| 12h | dev cross-platform test 矩阵 | dev profile |
| 18h | chief sweep status tracking | chief profile |
| 18h | chief dedup #59607 PR | chief profile |
| 24h | pm sweeper marker 责任分配 | pm profile |
| 24h | pm cross-profile permission audit | pm profile |
| 24h | 飞书 cluster status 报 oc_c653562b | researcher |
| 36h | qa cross-profile test CI verify | qa profile |
| 48h | qa ship gate ready | qa profile |
| 48h | default baseline 完整覆盖 | default profile |

## 跨 Profile 隐含要求

### chief 隐含要求
- chief 必须学会 `verify_hardening_wave_ii.sh` 调 default profile baseline
- chief 必须接管 daily sweep status tracking 飞书报
- chief 不直接 patch adapter,只 monitor + redirect + verify

### pm 隐含要求
- pm 必须学会 sweeper marker 责任 map(从 6 扩展到 8)
- pm 必须每日 verify 5 profile × 4 file path = 20 verify point
- pm 协调跨 profile credential lifecycle(沿用 tick27)

### dev 隐含要求
- dev 必须出 cross-platform test matrix (4 platform × 3 lifecycle + 4 replay scenarios)
- dev 必须跟进 hermes-agent upstream MCP PR(参照 Claude Code 2.1.196)
- dev 必须 verify Hardening wave II 11 PR 的 regression test

### qa 隐含要求
- qa 5-item grep 升级为 hard requirement
- qa cross-profile permission audit 必须每日 05:00 UTC 跑
- qa ship gate 默认开启(emergency flag 临时可关)

### default 隐含要求
- default verify_hardening_wave_ii.sh 每日 06:00 UTC 跑
- default MCP baseline (trust_policy strict + Remote Control bind + tool validator)
- default replay-safety + cross-platform memory baseline
