# Cross-profile impact graph — tick41 (2026-07-19)

## P1 cluster (8 effective signals)

### F4 credential-pool-stale-snapshot v2 (升级 emerging → stable)

| evidence | state | fix PR | fix_layer |
|---|---|---|---|
| #63425 | open P1 (2026-07-12) | TBD | layer_runtime (agent_init.py) |
| #25727 | open P2 (v0.18.0 regression) | partial #33233 merged | layer_runtime (recovery paths) |
| #33088 | closed (design_evidence) | #33233 merged (2e181602a) | layer_runtime (pool match guard) |
| #10147 | closed (completed) | #15120 merged | layer_data (auth.json sync) |
| #25205 + #15298 + #15434 | tick31 立卡证据 | — | — |

**cross-profile impact**:
- chief-agent: 必须 6h 内 dedup #63425 fix PR 候选 (沿用 tick27 PR dedup SLA)
- dev-agent: 实现 invariant 6 (pool mutation provider-match audit)
- qa-agent: ship gate v11 加 4 verify (fix_layer_audit + worsening_evidence)
- pm-agent: 23-field v9 acceptance contract (含 `fix_layer_audit` + `worsening_evidence`)
- default-agent: control 14 NEW (MCP server config mutation provenance audit)

### F9 session-state-integrity-deck (扩展)

| evidence | state | cross-cluster arrow |
|---|---|---|
| #66251 (NEW P2, 2026-07-17) | open | CCA-F9-F4 (auxiliary_client stale pool reuse) |
| #62665 (NEW P2, 2026-07-11) | open | CCA-F4-F9 (parent model contamination) |
| #62365 + #63008 + #63128 + #63129 + #63207 | tick34 立卡证据 | — |

**cross-profile impact**:
- chief-agent: 6h dedup #66251 fix PR 候选 (预计 PR 数 ≥ 2)
- dev-agent: F9 invariant 6 (surface ownership) 升级 — 集成 cross-cluster arrow 表
- default-agent: control 13 family_12_verify_runtime 加 F9 cross-cluster arrow verify

### F1 silent-fail (PR-dedup fire 5)

| PR | title | status |
|---|---|---|
| #58663 | fix(security): scope the cron-session approval marker to the job context | **merged** (commit dbc9c8daf + reset-token fix) |
| #59719 | fix(cron): scope approval marker to cron execution context | open candidate |
| #62111 | fix(approvals): make cron-session classification task-local, not process-global | open candidate |
| #64194 | fix(cron): keep approval context task-local | open candidate |
| #59179 | fix(approval): deny unattended gateway jobs via cron mode | open candidate |

**chief dedup (6h SLA)**:
- primary 已 merged: #58663
- 其他 4 PR 关闭 (模板回复 Closing in favor of #58663)
- 3 天内 primary 未合并 → reassign 给次高分 PR

### F11 execute-code-approval-unification-deck (沿用 tick40)

| evidence | state | cross-cluster arrow |
|---|---|---|
| #60056 + #60077 + #60799 + #24942 + #57890 | tick38 立卡证据 | CCA-F11-F4 NEW tick41 |

### F12 candidate (condition_2_met=true)

| evidence | state | condition met |
|---|---|---|
| arxiv 2607.12406 isolation survey | published | condition 2 (≥ 3 platform) ✓ |
| arxiv 2604.10134 PlanGuard | published | condition 2 ✓ |
| arxiv 2607.12624 PVDetector | published | condition 2 ✓ |
| arxiv 2607.05120 ADI | tick40 拉新 | condition 2 ✓ |
| #60056 + #21563 + #63183 | tick40 拉新 | condition 1 NOT MET |

### CVE-2026-61459 (CRITICAL 9.8)

| field | value |
|---|---|
| CVSS | 9.8 CRITICAL |
| CWE | CWE-88 Argument Injection |
| Affected | mcp-server-kubernetes < 3.9.0 |
| Patched | 3.9.0+ |
| fix_layer | layer_runtime (kubectl tool) |

**cross-profile impact**:
- chief-agent: 6h dedup MCP server version pin PR candidate
- dev-agent: control 8 (MCP server version pin) MUST 加 mcp-server-kubernetes ≥ 3.9.0
- qa-agent: ship gate v11 加 CVE version pin verify
- pm-agent: 23-field v9 acceptance contract `fix_layer_audit.layer_runtime` 必填
- default-agent: control 14 NEW (MCP server config mutation provenance)

## Cross-cluster arrows (tick41 NEW)

| arrow_id | from | to | severity | interaction | worsening check |
|---|---|---|---|---|---|
| CCA-F11-F4 | F11 execute-code-approval | F4 credential-pool-stale | sev-B | execute_code RPC dispatch may invoke with stale pool | predicted sev-B, measure after F11 fix lands |
| CCA-F4-F9 | F4 credential-pool-stale | F9 session-state-integrity | sev-B | #62665 parent model contamination may bypass pool isolation | predicted sev-B, measure after F4 v2 fix lands |
| CCA-F9-F4 | F9 session-state-integrity | F4 credential-pool-stale | sev-C | #66251 auxiliary_client stale pool reuse | predicted sev-C, measure 14 days |
| CCA-CVE-F7 | CVE-2026-61459 | F7 MCP supply chain | sev-A | control 8 version pin required | predicted sev-A, mandatory |
| CCA-CVE-F11 | CVE-2026-61459 | F11 execute-code-approval | sev-A | kubectl tool arg injection | predicted sev-A, mandatory |
| CCA-CVE-F12 | CVE-2026-61459 | F12 candidate | sev-A | F12 defense layer 2 (tool result provenance) | predicted sev-A, monitor |

**Total cross-cluster arrows**:
- tick40 沿用: 8 arrows (4 tick39 + 4 tick40)
- tick41 NEW: 6 arrows
- **Total**: 14 arrows (8 + 6)

## Family registry cumulative (tick41)

| # | family | lifecycle | evidence | sweeper marker |
|---|---|---|---|---|
| 1 | silent-fail | stable → expansion | 6+ | `sweeper:risk-silent-fail` |
| 2 | cross-platform-state | stable | 3 | `sweeper:risk-cross-platform-state` |
| 3 | memory-injection-cross-platform | stable | 3 | `sweeper:risk-memory-injection-platform-gateway` |
| 4 | credential-pool-stale-snapshot | **emerging → stable** | **5+2** | `sweeper:risk-credential-pool-stale` |
| 5 | cron-session-leak-closed-state | maintenance | 3 | `sweeper:risk-cron-session-leak` |
| 6 | outbound-redact-call-site | maintenance | 2 | `sweeper:risk-outbound-redact-call-site` |
| 7 | MCP-supply-chain-protocol-migration | stable → expansion | 8+ CVE | `sweeper:risk-mcp-supply-chain-6-control` |
| 8 | cron-ticker-resilience-deck | stable | 9 | `sweeper:risk-cron-ticker-resilience` |
| 9 | session-state-integrity-deck | stable → expansion | 7 (2 NEW) | `sweeper:risk-session-state-integrity` |
| 10 | cron-installer-handoff-state | stable | 5 | `sweeper:risk-installer-handoff-state` |
| 11 | execute-code-approval-unification-deck | emerging | 5+ | `sweeper:risk-execute-code-approval-unification` |
| **12** | **data-injection-isolation-deck (candidate)** | **emerging (condition_2_met)** | **5+ arxiv** | `sweeper:risk-data-injection-isolation` |

## Profile cross-dependency chain

```
chief-agent ──6h dedup SLA──> dev-agent (invariant enforce)
    │                            │
    │                            ├──> qa-agent (ship gate verify)
    │                            │
    │                            └──> default-agent (control upgrade)
    │
    └──> pm-agent (23-field v9 acceptance)

F4 upgrade ─> F11 CCA ─> F9 CCA (worsening_evidence 14-day window)
CVE-2026-61459 ─> F7 + F11 + F12 (control 8 + 9 + 14)
F12 candidate ─> arxiv 2607.12406 5 boundaries taxonomy
```

## Self-downgrade v4 (tick41)

- rule 1: major release day — latest v0.18.2 ship day +12 ❌
- rule 2: installer-recurrence 30d ≥ 2 — F10 沿用 5+ hits + tick36-40 = 7+ ✓
- rule 3: PR-dedup fire ≥ 2 cross-family — 5 fires tick41 ✓
- rule 4: silent-fail cross-month recurrence — F1 沿用 tick27-40 ✓
- rule 5: P1 ≥ 8 + streak ≥ 4 — P1-effective = 8 + streak 17 ✓
- rule 6: streak ≥ 5 + rule 1-5 any — yes
- rule 7: streak ≥ 5 + 无 rule 1-5 — 被推翻
- rule 8: streak ≥ 4 + normal — rule 5 优先

**决策**: maintain_daily + 飞书 3 选项 A/B/C (4 rule 同命中 + F4 emerging → stable + F11 + F12 condition_2_met)
