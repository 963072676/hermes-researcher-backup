# 跨 profile 影响图 (2026-07-08 tick30)

> hermes-researcher-deep-tick-daily tick30
> 信号基础: 5 P1 cluster + PR dedup x3 + v0.18.1 release day

## P1 cluster 跨 profile 依赖链

### Chain 1: PR-dedup fire (5 PRs in 24h)

```
tick27 立卡 PR-dedup rule (24h ≥ 3 PR 抢同 root cause → chief 6h SLA)
        │
        ├──► chief-agent (SOUL: chief_dedup_protocol_v1 + chief_architecture_escalation_v1)
        │         │
        │         ├──► pm-agent (SOUL: pr_dedup_arbitration_template_v1 + installer_dual_track_verification_v1)
        │         │         │
        │         │         └──► qa-agent (SOUL: installer_post_install_smoke_v1 + pr_dedup_test_coverage_v1)
        │         │
        │         └──► dev-agent (SOUL: pr_dedup_acceptance_protocol_v1 + fallback_chain_index_reset_pattern_v1 + provider_base_url_symmetric_guard_v1)
        │
        └──► new skill: hermes-pr-dedup-arbitrator (5 维评分 + closure template + 3-day reassign)
                  │
                  └──► 触发源: gh pr list --search linked:issue:#N --state open ≥ 3
```

### Chain 2: install-recurrence 30d 第 2 hits

```
#59004 (2026-07-05) → #60384 (2026-07-07) = 30d 2 hits → 架构性问题立卡
        │
        ├──► chief-agent (chief_architecture_escalation_v1)
        │         │
        │         ├──► pm-agent (installer_dual_track_verification_v1: 5+5 项 checklist)
        │         │         │
        │         │         └──► qa-agent (installer_post_install_smoke_v1: track 1 + track 2)
        │         │
        │         └──► new skill: hermes-installer-post-install-smoke (5+5 项一键跑)
        │
        └──► 若 30d ≥ 3 hits → 冻结 Windows release channel
```

### Chain 3: MCP self-approval baseline 缺位

```
Claude Code 2.1.196 (2026-07-01) + ToolHijacker NDSS 2026 (96.7% ASR) + SHIELDMCP acl-industry 2026
        │
        ├──► default SOUL (mcp_self_approval_baseline_v1: trust_policy + pending_label)
        │         │
        │         └──► new skill: hermes-mcp-tool-library-validator (Stage 1+2+3 + KAT + Rule of Two)
        │
        └──► dev-agent (SOUL 增量: ToolHijacker 防御 pattern)
                  │
                  └──► qa-agent (KAT 100 条测试集准备)
```

### Chain 4: consent-gate family (#60379)

```
#60379 (zh) + #60382 (en) + #60319 (stdout auth material preview)
        │
        ├──► default SOUL (provider_pool_contamination_defense_v1)
        │
        └──► chief-agent (SOUL: chief_architecture_escalation_v1 包含 consent gate family)
                  │
                  └──► qa-agent (KAT 100 条覆盖 provider pool)
```

## P1 cluster ↔ profile 矩阵

| P1 issue | chief | pm | dev | qa | default | new skill |
|---|---|---|---|---|---|---|
| #47828 (provider base_url) | dedup SLA | arbitration_template | symmetric_guard | test_coverage | — | hermes-pr-dedup-arbitrator |
| #60384 (installer recurrence) | architecture_escalation | dual_track | — | post_install_smoke | — | hermes-installer-post-install-smoke |
| #60794 (Discord event-loop) | dedup SLA | arbitration_template | acceptance_protocol | test_coverage | — | hermes-pr-dedup-arbitrator |
| #60947 (Telegram hygiene) | dedup SLA | arbitration_template | acceptance_protocol | test_coverage | — | hermes-pr-dedup-arbitrator |
| #60955 (fallback chain) | dedup SLA | — | fallback_chain_index_reset_pattern | — | — | — |
| #60379 (consent-gate) | architecture_escalation | — | — | — | provider_pool_contamination_defense | — |
| MCP baseline (cross-cutting) | — | — | ToolHijacker defense pattern | KAT | mcp_self_approval_baseline | hermes-mcp-tool-library-validator |

## 新 skill 触发图

### hermes-pr-dedup-arbitrator
```
trigger: gh pr list --search linked:issue:#N --state open ≥ 3
   ↓
input: PR list (number, author, delta, files, mergeable)
   ↓
scoring: 5 维 (root_cause_coverage × 2 + minimality + cross_subsystem_impact + test_coverage + author_responsiveness)
   ↓
output: primary PR + closure template for non-primary
   ↓
3-day reassign cron check
```

### hermes-installer-post-install-smoke
```
trigger: release ship / hermes update / installer-related P1
   ↓
track 1 (release artifacts): 5 项 grep
   ↓
track 2 (fresh install): 5 项 smoke (需 clean VM)
   ↓
output: PASS/FAIL per track → release gate decision
   ↓
30d sliding window recurrence counter
```

### hermes-mcp-tool-library-validator
```
trigger: MCP tool call / .mcp.json load / ToolHijacker P1
   ↓
Stage 1 (Unicode / injection / instruction override)
   ↓
Stage 2 (semantic intent classifier, τ=0.72)
   ↓
Stage 3 (perplexity detection)
   ↓
KAT (100 common queries)
   ↓
Meta Rule of Two check
   ↓
output: ok / fail / quarantine / flag
```

## 受影响 profile 优先级

| Profile | 影响度 | SOUL 改 / 新 skill 优先级 |
|---|---|---|
| chief | HIGH (PR dedup + architecture escalation) | SOUL 改 — 必采纳 |
| pm | HIGH (arbitration template + dual_track verification) | SOUL 改 — 必采纳 |
| dev | MEDIUM (acceptance protocol + bug patterns) | SOUL 改 — 必采纳 |
| qa | MEDIUM (post-install smoke + test coverage) | SOUL 改 + new skill 集成 |
| default | MEDIUM (provider pool + MCP baseline + cron workaround) | SOUL 改 — 必采纳 |

## 验证清单

- [ ] 4 chain 跨 profile 集成一致
- [ ] P1 cluster ↔ profile 矩阵覆盖所有 5 P1
- [ ] 3 新 skill 触发路径清晰
- [ ] 影响度排序合理
- [ ] 没有 SOUL 改 / new skill 漏掉的关键路径