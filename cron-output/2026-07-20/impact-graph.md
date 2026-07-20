# tick42 impact-graph (2026-07-20)

> 12 family registry (F11 + F12 candidate condition_2_met_strong) + 14 cross-cluster arrows (8 沿用 + 6 NEW tick42) + CVE-2026-61459 cross-cluster anchor

## tick42 family state 累计

| # | family | lifecycle | tick 立卡 | tick42 status |
|---|---|---|---|---|
| 1 | silent-fail | maintenance | tick27 | 沿用, fix PR merged #59524 |
| 2 | cross-platform-state | stable | tick28 | 沿用 |
| 3 | memory-injection-cross-platform | stable | tick31 | 沿用 |
| 4 | credential-pool-stale-snapshot | stable | tick31 → tick41 upgrade | 沿用 (v2 invariant 7) |
| 5 | cron-session-leak-closed-state | maintenance | tick32 | 沿用 |
| 6 | outbound-redact-call-site | maintenance | tick32 | 沿用 |
| 7 | MCP-supply-chain-protocol-migration | expansion | tick32/33 | 沿用 + tick42 +1 CVE |
| 8 | cron-ticker-resilience-deck | expansion | tick33 | 沿用 + tick42 sibling fix PR #27492 |
| 9 | session-state-integrity-deck | expansion | tick34 | 沿用 + tick42 tier-2 #62665 |
| 10 | cron-installer-handoff-state | stable | tick35 | 沿用 |
| 11 | execute-code-approval-unification-deck | emerging | tick38 | **tick42 + invariant 8 + CVE anchor** |
| **12 candidate** | **data-injection-isolation-deck** | **emerging** | **tick40-41** | **tick42 condition_2_met_strong + CVE-2026-61459 cross-cluster anchor** |

## tick42 NEW cross-cluster arrows (4)

| arrow_id | from | to | severity | interaction |
|---|---|---|---|---|
| CCA-F11-F12-CVE | F11 execute-code-approval | F12 candidate + CVE-2026-61459 | **severity-A** | 5 family + 1 CVE 三联 anchor: F11 invariant 8 tool_description_provenance + static_arg_injection_precheck 防御 CVE-2026-61459 leading-dash arg injection;F12 B2_origin_trust 防御 origin tag integrity 攻击;CVE-2026-61459 跨 F11+F7+F12 三 family 触发 |
| CCA-F8-F9 | F8 cron-ticker-resilience | F9 session-state-integrity | severity-B | F8 cron ticker BaseException + F9 session state mutation 异常路径 fail-open 联动:cron ticker die 时 session state 也 fail-open,双盲区 |
| CCA-F12-F4 | F12 candidate data-injection-isolation | F4 credential-pool-stale-snapshot | severity-C | F12 ADI attack 通过 tool description poisoning 触发 F4 credential pool misattribution (沿用 tick41 F4 v2 invariant 7 pool mutation provider-match audit) |
| CCA-CVE-F11-CVE | CVE-2026-61459 → F11 invariant 8 | F11 invariant 8 precheck dependency | severity-A | CVE-2026-61459 mcp-server-kubernetes < 3.9.0 直接 dependency:F11 invariant 8 static_arg_injection_precheck 必须升级到 leading-dash detection 必填 |

## 沿用 cross-cluster arrows (8 沿用 tick39-41)

| arrow_id | from | to | severity | 来源 |
|---|---|---|---|---|
| CCA-F11-F4 | F11 execute-code-approval | F4 credential-pool-stale | sev-B | tick41 |
| CCA-F4-F9 | F4 credential-pool-stale | F9 session-state-integrity | sev-B | tick41 |
| CCA-F9-F4 | F9 session-state-integrity | F4 credential-pool-stale | sev-C | tick41 |
| CCA-CVE-F7 | CVE-2026-61459 | F7 MCP supply chain | sev-A | tick41 |
| CCA-CVE-F11 | CVE-2026-61459 | F11 execute-code-approval | sev-A | tick41 |
| CCA-CVE-F12 | CVE-2026-61459 | F12 candidate | sev-A | tick41 |
| CCA-F11-F10 | F11 execute-code-approval | F10 cron-installer-handoff | sev-B | tick40 |
| CCA-F12-F7 | F12 candidate | F7 MCP supply chain | sev-B | tick40 |

## total = 8 沿用 + 4 NEW tick42 = 12 cross-cluster arrows (注:与 tick41 总数 14 不同,tick42 重新评估为 12 arrows with stricter severity-eval)

## cross-family PR dedup fires (tick42 实测)

| fire_id | family | pr_candidates | dedup_window_hours | status |
|---|---|---|---|---|
| fire-2026-07-20-F11 | F11 | #60077, #60799 | 6h | chief must decide |
| fire-2026-07-20-F8 | F8 | #61674, #39782, #27492 (merged) | 6h | chief must decide |
| fire-2026-07-20-F12-CVE | F12 candidate + CVE-2026-61459 | (no PR yet, CVE pending fix) | 6h | chief must triage |

**cross-family fires ≥ 2 → rule 3 命中 → maintain_daily** (沿用 tick30 v4 决策树)
**cross-family fires = 3 → chief must personally triage (tick42 NEW)**

## trust boundary impact (tick42)

| category | severity | tick42 触发 |
|---|---|---|
| fabrication | tier-1 | 沿用 tick35 F9 #62365 |
| action_authority | tier-2 | F11 #60056 + CVE-2026-61459 mcp-server-kubernetes arg injection |
| identity | tier-3 | 沿用 tick35 CCA-F2-F11 |
| info_disclosure | tier-1 | CVE-2026-61459 bearer token exfil (operator → attacker-controlled API server) |
| full_compromise | tier-1 | CVE-2026-61459 9.8 CRITICAL cluster takeover |

**3 tier-1 category 触发**: fabrication (F9) + info_disclosure (CVE) + full_compromise (CVE) → 必须 chief sign-off before ANY follow-up

## severity-eval prefilter (tick42 chief-agent 沿用)

```python
def severity_eval(arrow):
    if arrow.from_family_fix_side_effect_directly_worsens(arrow.to_family_bug):
        return "severity-A"  # chief 6h triage 必须 sign-off
    if arrow.from_family_fix_requires_to_family_fix_to_complete():
        return "severity-B"  # chief 24h joint review
    return "severity-C"  # 进 daily report
```

## tick42 12 family + 12 cross-cluster arrows 影响链

```
F11 (canonical_invocation_path v3) ← CVE-2026-61459 (leading-dash arg injection)
    ↓ tool_description_provenance + static_arg_injection_precheck
F12 candidate (data-injection-isolation v2) ← arxiv 2607.05120 ADI + CVE-2026-61459 cross-cluster
    ↓ 5 boundaries + probabilistic delimiter + origin tag + PoE + CXI
F8 cron-ticker (BaseException + lock granularity) ← tick33 fix PR #27492 merged
    ↓ canonical ticker invariant 6
F9 session-state-integrity ← tier-2 #62665 parent session model contamination
    ↓ session state mutation fail-open defense
F4 credential-pool-stale (v2 invariant 7) ← pool mutation provider-match audit
    ↓ ADI attack path blocked
F7 MCP-supply-chain (control 8 + 9 + 14 + 15) ← CVE-2026-61459 + tick42 control 15 NEW
    ↓ mcp server version pin + tool spawn static analyzer + provenance + cross-family dedup
```

## Self-downgrade v4 evaluation (tick42)

streak = 18 days zero-adoption (tick41 +1)
- rule 2 (installer-recurrence 30d ≥ 2): F10 旧 7 hits + tick42 F11 #60077/#60799 = 9 hits ✅
- rule 3 (PR-dedup fire ≥ 2 跨 family): tick42 3 fires ✅
- rule 4 (silent-fail cross-month): F1 沿用 tick27-41 ✅
- rule 5 (P1 ≥ 8 + streak ≥ 4): tick42 P1-effective ≥ 8 + streak 18 ✅
- rule 6 (streak ≥ 5 + rule 1-5 任一): streak 18 + rules 2/3/4/5 命中 ✅
- rule 7 (streak ≥ 5 + 无 rule 1-5): rule 2/3/4/5 命中 → 被推翻 ❌
- rule 8 (streak ≥ 4 normal): P1 = 8 → rule 5 优先 ❌

**决策**: maintain_daily + 飞书 3 选项 A/B/C (4 rules 同命中 + F12 candidate condition_2_met_strong + CVE-2026-61459 cross-cluster anchor + 12 cross-cluster arrows)

## 飞书 3 选项 (tick42)

- **A 降频到隔日** (不推荐, CVE-2026-61459 tier-1 + F12 condition_2_met_strong + 12 cross-cluster arrows)
- **B 维持每日** (推荐, 4 rules + F11 invariant 8 + F12 v2 + CVE-2026-61459 + control 15 + 12 arrows)
- **C 暂停** (FORBIDDEN, trust_boundary_impact=fabrication+info_disclosure+full_compromise 仍在)