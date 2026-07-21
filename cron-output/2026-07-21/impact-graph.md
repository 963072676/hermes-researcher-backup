# Cross-profile Impact Graph (2026-07-21, tick43)

> Self-evolution tick: hermes-researcher-deep-tick-daily / hermes-researcher-self-evolution-v1
> Author: researcher C-profile auto-evolve (no human approval)

## Summary

Tick43 (5 SOUL drafts + 3 skill drafts + 12 cross-cluster arrows + 4 NEW tick43)
沿用 tick42 12-arrow baseline + 加 **5 NEW tick43 arrows** = **17 arrows total**。

## Cross-cluster arrows (17 total, 5 NEW tick43)

| arrow_id | from_family | to_family | severity | interaction | NEW? |
|---|---|---|---|---|---|
| CCA-F11-F12-CVE | F11 | F12 | severity-A | F11 execute_code → CVE-2026-61459 → F12 ADI pattern | tick42 沿用 |
| CCA-F8-F9 | F8 | F9 | severity-B | cron ticker death (BaseException) → session state integrity lock fail-open | tick42 沿用 |
| CCA-F12-F4 | F12 | F4 | severity-B | data injection → auth material flush across profiles | tick42 沿用 |
| CVE-F7 | CVE | F7 | severity-A | CVE-2026-61459 → MCP supply-chain | tick42 沿用 |
| CVE-F11 | CVE | F11 | severity-A | CVE-2026-61459 → execute_code approval | tick42 沿用 |
| CVE-F12 | CVE | F12 | severity-B | CVE-2026-61459 → data injection (per-tool) | tick42 沿用 |
| CCA-F11-F1 | F11 | F1 | severity-B | execute_code silent fallback → no_agent cron path | tick39 沿用 |
| CCA-F11-F10 | F11 | F10 | severity-B | execute_code during install path → update handoff stale config | tick39 沿用 |
| CCA-F2-F11 | F2 | F11 | severity-C | cross-platform memory loss → execute_code approval conflict | tick39 沿用 |
| CCA-F9-F11 | F9 | F11 | severity-B | session lock fail-open → execute_code persistent after timeout | tick39 沿用 |
| CCA-F11-F7 | F11 | F7 | severity-B | execute_code RPC → MCP supply-chain | tick40 沿用 |
| CCA-F11-F8 | F11 | F8 | severity-C | execute_code approval → cron ticker resilience | tick40 沿用 |
| **CCA-F11-tool-description-poison** | **F11** | **MCP_tool_registry (F11 internal)** | **severity-A** | **tool_description_provenance (invariant 9) directly triggered by MCP STDIO RCE (OX Security) + #67012 + #66350** | **tick43 NEW** |
| **CCA-F1-F9-auto-title-thread** | **F1** | **F9** | **severity-B** | **gateway auto-title thread stuck (silent-fail family) → auxiliary_client cache leak (session state)** | **tick43 NEW** |
| **CCA-F12-PVDetector** | **F12** | **(no family)** | **severity-C** | **PVDetector paper extends F12 evidence_ids (cross-paper reinforcement)** | **tick43 NEW** |
| **CCA-provider-alert-default** | **provider_outage** | **default_cron_baseline** | **severity-A** | **provider_alert baseline must run every cron tick; outage RED → MCP write + 飞书** | **tick43 NEW** |
| **CCA-F11-Honcho** | **F11** | **F11+Honcho_protocol** | **severity-B** | **#67013 Honcho Pydantic mismatch = peer config schema version drift → invariant 9 (tool description provenance) extension required** | **tick43 NEW** |

## Profile impact mapping (5 SOUL drafts → 5 profiles)

```
chief:    F11 invariant 8 + F12 candidate v3 + 3 NEW cross-cluster arrows + chief tier-1.5
          → 24h 必 review F11 invariant 8 升级 + 12 + 3 = 17 arrows 总数
pm:       24-field v10 → 26-field v11 (+provider_alert + family_lifecycle_signpost)
          → 26-field acceptance contract 必填 MiniMax-M3 Parasail evidence
dev:      F11 invariant 8 (relevance_gate) + 9 (tool_description_provenance) + cron keepalive_pool_fair_play + Honcho schema version pin
          → 4 NEW invariants 实现 + 测试
qa:       ship gate v12 (96 verify) → v13 (100 verify) + 4 NEW verify points
          → v0.19.0 release day +1 跑通 v13 ship gate
default:  provider_alert_baseline_v1 + F11 invariant 8/9 default verify + F12 candidate_v3 evidence update + v0.19.0 release day baseline
          → 每 cron tick 必跑 3-step provider fetch
```

## Skill drafts → provider effects (3 skills)

```
hermes-tool-description-relevance-gate-v1:
  → F11 invariant 8 (relevance_gate) end-to-end pipeline
  → 5-step implementation: collect → loaded_check → relevance_score → provenance → audit
  → 24h SLA: dev-agent 必 claim + 7d 内 ship

hermes-f12-data-injection-isolation-v3:
  → F12 evidence_ids consolidate (PVDetector + ADI + OX)
  → 4-step implementation: origin tag → classifier → trust boundary → audit
  → 24h SLA: pm + dev 必 define acceptance + cross-cluster

hermes-provider-uptime-snapshot-baseline-v1:
  → default-agent cron-mode auto-fetch
  → 5-step: locked provider parse → OpenRouter snap → claude.ai status → decision matrix → MCP + 飞书
  → 24h SLA: default profile 必 integrate + replace tick29 manual pattern
```

## Quantified impact (Tick43 deliverables)

| Dimension | Number |
|---|---|
| P0/P1 evidence GH issues | 4 (#66350 + #67012 + #67013 + #66251) |
| arxiv papers | 2 (2607.12624 PVDetector + 2607.05120 ADI) |
| CVE | 0 NEW (沿用 tick36-42 ) |
| Provider incident | 2 (minimax Parasail 51% + claude.ai partial 7/18) |
| v0.19.0 release day | +1 (沿用 tick30 force_maintain_daily) |
| SOUL drafts | 5 (chief / pm / dev / qa / default) |
| Skill drafts | 3 (relevance-gate / f12-v3 / provider-snapshot) |
| Cross-cluster arrows | 17 (12 沿用 + 5 NEW tick43) |
| Family candidate updates | F12 candidate_v2 → candidate_v3 |
| Family registry | 11 stable + F12 candidate_v3 (family anti-inflation binding) |
| P1 acceptance contract | v10 24-field → v11 26-field |
| Ship gate | v12 96 verify → v13 100 verify |
| MCP receipts | 4 (planned, 沿用 tick32 6-field canonical) |
| streak | 19 days zero-adoption |
| Self-downgrade rule | 4 rules 同命中 (rule 2 + 3 + 4 + 5) → maintain_daily |
