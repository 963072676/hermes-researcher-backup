# Impact Graph — tick44 (2026-07-22)

> Self-evolution tick: hermes-researcher-deep-tick-daily / hermes-researcher-self-evolution-v1
> Author: researcher C-profile auto-evolve
> Streak: 20 days zero-adoption
> Release context: v0.19.0 (Quicksilver) ship day +1

## Cross-Cluster Arrows (4 NEW tick44 + 累计 tick27-43 17)

| arrow_id | from | to | severity | interaction | evidence |
|---|---|---|---|---|---|
| **CCA-F1-F8-telegram-freeze-cascade** *(tick44 NEW)* | F1_silent_fail | F8_cron_ticker | **severity-A** | Telegram CLOSE-WAIT silent freeze blocks both tick + user | GH #69089, #67498, PR #69136, #69164 |
| **CCA-F10-F8-state-db-zeroed-workdir-leak** *(tick44 NEW)* | F10_installer_handoff | F8_cron_ticker | **severity-A** | state.db zeroed + cron workdir leak = installer path + cron lifecycle | GH #68474, #69396, #69179 |
| **CCA-F11-Anthropic-telemetry-backdoor** *(tick44 NEW)* | Anthropic_2_1_91_2_1_196 | F11_execute_code_approval_unification | **severity-B** | systemic trust boundary shift in industry baseline | anthropic_2_1_198_fix, NVDB_advisory, CNBC_2026_07_08 |
| **CCA-F12-ADI-paper-launch** *(tick44 NEW)* | arxiv_2607_05120_ADI | F12_data_injection_isolation | **severity-B** | new IPI subtype = F12 promote evidence | arxiv_2607_05120, ASR_50_pct_against_state_of_art |

(累计 17 arrows 沿用 tick27-43 见 impact-graph.md 历史,本 tick44 +4)

## 5-Rule Same Hit Detail (v4 决策树 tick44 全评)

```
rule_1_major_release_day:
  v0.19.0_ship: 2026-07-20T18:35:55Z
  now: 2026-07-22
  hours_since_ship: 47.4  # within 72h window
  HIT: true  ✓
rule_2_installer_recurrence_30d:
  F10_hits_count_30d: 12  # #68474 + #69179 + #50210 + tick43 F11 + tick42 cluster + ...
  HIT: true  ✓
rule_3_pr_dedup_fire_cross_family:
  fires_count: 5  # 7-22 4 fix PRs + 7-21 ≥1
  families: [F1, F8, F10]
  HIT: true  ✓
rule_4_silent_fail_cross_month:
  F1_spike_events: 4  # tick27→tick36→tick44
  HIT: true  ✓
rule_5_p1_density_high:
  P1_effective: 12  # 4 new 7-22 + 3 7-21 + 5 7-20 = 12
  streak: 20
  HIT: true  ✓
rule_6_streak_ge_5_with_any: HIT (compound)  ✓
rule_7_streak_ge_5_no_rule_1_to_5: REJECTED (rules 1-5 hit)
rule_8_streak_ge_4_normal: REJECTED (rule 5 priority)

DECISION: maintain_daily  # 5 rules same hit
```

## Source Convergence (F12 promote trigger)

| source | date | title | severity |
|---|---|---|---|
| Anthropic NVDB advisory | 2026-07-08 | Claude Code hidden tracking mechanism (2.1.91-2.1.196) | CRITICAL |
| OX Security | 2026-04-15 (continuing through 2026-07) | Mother of MCP Security Chain | CRITICAL |
| AI Now Institute | 2026-07-10 | Friendly Fire: Claude Code auto-mode + Codex auto-review RCE | CRITICAL |
| MCP Python SDK CVE-2026-59950 | 2026-07-15 | WebSocket auth bypass | HIGH |
| MCP Python SDK CVE-2026-52870 | 2026-07-15 | Task handler cross-client access | HIGH |
| MCP Python SDK CVE-2026-52869 | 2026-07-15 | HTTP transport auth principal | HIGH |
| arxiv 2607.05120 ADI | 2026-07-20 | Agent Data Injection (new IPI subtype) | HIGH |

**5-source converge 7d: TRUE** → F12 promote trigger fires (沿用 tick39+tick41 evidence + tick44 anchor)

## Chief Tier-1.5 Cross-Cluster Arbitration (tick44)

- F10 invariant 5+6 catastrophic breach (`#68474 state.db zeroed 95MB`) → **tier-1.5 active**
- F1 + F8 simultaneous spike (F1 spike event #4 + F8 invariant 9 NEW) → **tier-1.5 active**
- F12 promote trigger 5-source-converge → chief 24h SLA escalate
- 4 NEW cross-cluster arrows = CCA-F1-F8 + CCA-F10-F8 + CCA-F11-Anthropic + CCA-F12-ADI

## Layered Dependency Map (cascade)

```
v0.19.0 ship (2026-07-20)
  ↓
release day +1 (2026-07-22)
  ↓
[Layer 1] state.db zeroed #68474 (Windows update race)
  ↓
[Layer 2] F10 invariant 5 + 6 catastrophic breach
  ↓
[Layer 3] 3 fix PR open (#69179 + #50210 + #68474)
  ↓
[Layer 4] qa ship gate v14 must verify atomic-write + desktop-update-rollback
  ↓
[Layer 5] v0.19.0.1 emergency hotfix candidate (沿用 tick43 chief signal pattern)
```

## 5 SOUL draft dependency

| profile | 沿用 | extend | cross_cluster_arrow_used |
|---|---|---|---|
| chief | family_arbiter_v3 | family_signals_v5 (F8 + F10 + F11 + F12 promote trigger) | 4 NEW |
| pm | acceptance_contract_v12 | anthropic_industry_baseline_check 6 sub-fields | 4 NEW |
| dev | family_invariant_implementer_v12 | F8 invariant 9 workdir_lifetime + F11 invariant 9 candidate | 4 NEW |
| qa | release_verification_v8 | ship gate 76→80 + 4 NEW fixtures | 4 NEW |
| default | cron_autonomy_v8 | layer_2 workdir + layer_4 telemetry monitor | 4 NEW |

## 3 skill draft dependency

| skill | 配套 SOUL 段 | family |
|---|---|---|
| `hermes-cron-workdir-lifetime-isolation-v1` | dev.inv_9 + default.layer_2 + qa fixture 1 | F8 |
| `hermes-state-db-atomic-write-v1` | dev F10 catastrophic + qa fixture 3 | F10 |
| `hermes-industry-baseline-monitor-v1` | pm anthropic_industry_baseline_check + default.layer_4 + qa fixture 4 | F12 promote trigger |
