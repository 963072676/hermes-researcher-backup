# 跨 profile 影响图 (2026-07-09 tick31)

> hermes-researcher-deep-tick-daily tick31
> 信号基础: 7 P1 cluster (tick30 5 + tick31 NEW 2) + PR dedup fire x4 (累加) + v0.18.2 ship day +1 + memory-injection-cross-platform family NEW 立卡

## P1 cluster 跨 profile 依赖链

### Chain 1: PR-dedup fire (4 P1, 12 PR total in 24h 累加)

```
tick27 立卡 PR-dedup rule (24h ≥ 3 PR 抢同 root cause → chief 6h SLA)
        │
        ├──► chief-agent (chief_dedup_protocol_v1: tick31 实战 +4 P1)
        │         │
        │         ├──► pm-agent (pr_dedup_arbitration_template_v1: closure template + 3-day reassign)
        │         │         │
        │         │         └──► qa-agent (pr_dedup_test_coverage_v1: regression test 必跑)
        │         │
        │         └──► dev-agent (pr_dedup_acceptance_protocol_v1: merge primary, close non-primary)
        │
        └──► new skill: hermes-pr-dedup-arbitrator (tick30 已立卡,tick31 复用)
                  │
                  └──► 触发源: gh pr list --search linked:issue:#N --state open ≥ 3
```

### Chain 2: install-recurrence 30d 第 2 hits (沿用 tick30)

```
#59004 (2026-07-05) → #60384 (2026-07-07) = 30d 2 hits → 架构性问题立卡
        │
        ├──► chief-agent (chief_architecture_escalation_v1)
        │         │
        │         ├──► pm-agent (installer_dual_track_verification_v1: 5+5 项 checklist)
        │         │         │
        │         │         └──► qa-agent (installer_post_install_smoke_v1: track 1 + track 2)
        │         │
        │         └──► new skill: hermes-installer-post-install-smoke (tick30 已立卡)
        │
        └──► 若 30d ≥ 3 hits → 冻结 Windows release channel
```

### Chain 3: NEW — memory-injection-cross-platform family (tick31 立卡)

```
#40170 (2026-06-07) + #40967 (wiring missing) + #41003 (follow-up) = NEW family
        │
        ├──► chief-agent (memory_injection_cross_platform_v1: family 立卡 + 触发器)
        │         │
        │         ├──► pm-agent (cross_platform_memory_injection_guard_v1: 60 test 框架)
        │         │         │
        │         │         └──► qa-agent (cross_platform_memory_injection_test_v1: 6 platform × 10 case)
        │         │
        │         └──► dev-agent (cross_platform_memory_injection_guard_v1: wiring 实施)
        │
        └──► new skill: hermes-cross-platform-memory-injection-guard (tick31 NEW)
                  │
                  └──► 触发源: PR 含 _skip_memory_injection 但 wiring 缺失 / chief 触发 / qa 60 test 失败
```

### Chain 4: credential-pool-stale-snapshot family (tick31 立卡)

```
#25205 (2026-05-13) + #15298 + #15434 = 60 天 open + 3 PR 抢修
        │
        ├──► chief-agent (chief_dedup_protocol_v1: primary #53913)
        │         │
        │         └──► dev-agent (fallback_chain_index_reset_pattern_v1: pool.select() + index reset)
        │                   │
        │                   └──► qa-agent (pr_dedup_test_coverage_v1: 5 regression test)
        │
        └──► new skill: hermes-credential-pool-stale-snapshot-fix (tick31 NEW)
                  │
                  └──► 触发源: PR 含 _restore_primary_runtime 但 diff 不含 pool.select() / chief 触发
```

### Chain 5: MCP self-approval baseline (沿用 tick30)

```
Claude Code 2.1.196 (2026-07-01) + ToolHijacker NDSS 2026 (96.7% ASR) + SHIELDMCP acl-industry 2026
        │
        ├──► default SOUL (mcp_self_approval_baseline_v1: trust_policy + pending_label)
        │         │
        │         └──► new skill: hermes-mcp-tool-library-validator (tick30 已立卡)
        │
        └──► dev-agent (toolhijacker_defense_pattern_v1: 4 层防御)
                  │
                  └──► qa-agent (toolhijacker_known_answer_test_v1: KAT 100 条)
                            │
                            └──► new skill: hermes-toolhijacker-defense (tick31 NEW)
```

### Chain 6: consent-gate family (沿用 tick30)

```
#60379 (zh) + #60382 (en) + #60319 (stdout auth material preview)
        │
        ├──► default SOUL (provider_pool_contamination_defense_v1)
        │
        └──► chief-agent (chief_architecture_escalation_v1 包含 consent gate family)
                  │
                  └──► qa-agent (KAT 100 条覆盖 provider pool)
```

## P1 cluster ↔ profile 矩阵 (tick31)

| P1 issue | chief | pm | dev | qa | default | new skill |
|---|---|---|---|---|---|---|
| #47828 (provider base_url) | dedup SLA | arbitration_template | symmetric_guard | test_coverage | — | hermes-pr-dedup-arbitrator |
| #60384 (installer recurrence) | architecture_escalation | dual_track | — | post_install_smoke | — | hermes-installer-post-install-smoke |
| #60794 (Discord event-loop) | dedup SLA | arbitration_template | acceptance_protocol | test_coverage | — | hermes-pr-dedup-arbitrator |
| #60947 (Telegram hygiene) | dedup SLA | arbitration_template | acceptance_protocol | test_coverage | — | hermes-pr-dedup-arbitrator |
| #60955 (fallback chain) | dedup SLA | — | fallback_chain_index_reset | — | — | hermes-credential-pool-stale-snapshot-fix |
| #25205 (credential pool bypass) | dedup SLA | — | pool_select_after_restore | test_coverage | — | hermes-credential-pool-stale-snapshot-fix |
| #40170 (memory injection cross-platform) | memory_injection_cross_platform_v1 | cross_platform_memory_injection_guard_v1 | cross_platform_memory_injection_guard_v1 | cross_platform_memory_injection_test_v1 | awareness | hermes-cross-platform-memory-injection-guard |
| #60379 (consent-gate) | architecture_escalation | — | — | — | provider_pool_contamination_defense | — |
| MCP baseline (cross-cutting) | — | — | ToolHijacker defense 4 层 | KAT 100 | mcp_self_approval_baseline | hermes-mcp-tool-library-validator + hermes-toolhijacker-defense |

## 新 skill 触发图 (tick31 NEW 2 + 沿用 tick30 1)

```
Tick31 NEW:
- hermes-cross-platform-memory-injection-guard (memory-injection-cross-platform family)
- hermes-toolhijacker-defense (ToolHijacker 4 层防御 pattern)
- hermes-credential-pool-stale-snapshot-fix (#25205 family)

Tick30 沿用:
- hermes-pr-dedup-arbitrator (PR dedup 评分)
- hermes-installer-post-install-smoke (5+5 项 grep checklist)
- hermes-mcp-tool-library-validator (MCP baseline)
```

## 累计 stats (tick27-31)

- PR dedup fire: tick27 3 + tick30 3 + tick31 1 = 7 P1 (4 个 new in tick31)
- installer-recurrence: tick30 立卡 (#59004/#60384)
- cross-platform family: tick28 立卡 (cross-platform-state) + tick31 NEW (memory-injection-cross-platform) = 2 family
- MCP baseline: tick28 立卡,持续跟踪
- memory injection: tick31 NEW 立卡
- credential pool family: tick31 NEW 立卡

## 依赖关系总结

```
chief-agent
  ├─► pm-agent (template + checklist)
  │     └─► qa-agent (test framework + smoke runner)
  └─► dev-agent (implementation + acceptance)

default-agent
  └─► (standalone baseline, 适用于所有 profile)

new skills (3 NEW tick31):
  ├─► hermes-cross-platform-memory-injection-guard (依赖 chief + pm + dev + qa)
  ├─► hermes-toolhijacker-defense (依赖 dev + qa + default)
  └─► hermes-credential-pool-stale-snapshot-fix (依赖 chief + dev + qa)
```