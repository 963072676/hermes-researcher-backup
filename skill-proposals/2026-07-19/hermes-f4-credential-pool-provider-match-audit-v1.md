---
name: hermes-f4-credential-pool-provider-match-audit-v1
description: F4 credential-pool-stale-snapshot family v2 invariant 6 enforce — provider-match guard in any pool mutation path. Use when: any code path that mutates credential pool MUST verify pool.provider == agent.provider before persist. Trigger evidence: #63425 (NEW P1, 2026-07-12) + #25727 (open P2, v0.18.0 regression) + #33088 (closed, design_evidence, zai 429 → openai-codex pool misattribution).
---

# hermes-f4-credential-pool-provider-match-audit-v1

> F4 family v2 invariant 6 (tick41 立卡)
> Trigger: tick41 P1 cluster #63425 + #25727

## Family registry

| 字段 | 值 |
|---|---|
| family_id | F4 |
| family_name | credential-pool-stale-snapshot |
| sweeper_marker | `sweeper:risk-credential-pool-stale` |
| lifecycle (tick41) | emerging → stable (升级) |
| evidence_count | 5 + 2 design_evidence |
| 立卡 tick | tick31 (v1), tick41 (v2) |

## Evidence chain (tick41 cumulative)

1. **#63425** (NEW P1, 2026-07-12) — Provider auto-detection discards credential pools
   - regression from #63048, `AIAgent(provider=None)` 时 pool validation 失败
   - 影响: OpenAI Codex / xAI / Anthropic endpoints
2. **#25727** (open P2, 2026-07-02 confirm) — Fallback OAuth → API key causes credential pool desync
   - v0.18.0 regression, 主要 fix 已在 main 但 runtime snapshot vs saved snapshot drift
3. **#33088** (closed, design_evidence) — Fallback provider 429 exhausts primary provider credential pool
   - zai 429 → openai-codex pool marked exhausted (cross-provider misattribution)
   - Fixed in #33233 / commit 2e181602a
4. **#10147** (closed completed, design_evidence) — Nous OAuth refresh lacks cross-process sync
   - Fixed by #15120 `_sync_nous_entry_from_auth_store()` pattern
5. **#25205 + #15298 + #15434** (tick31 立卡证据)

## Invariant 6 (v2, tick41)

| # | invariant | code path | failure mode |
|---|---|---|---|
| 1 | provider-boundary-validation BEFORE pool validation | `agent/agent_init.py` | pool 验证时 provider 仍为 None → pool 误拒 |
| 2 | runtime snapshot single source of truth (`_primary_runtime`) | `_primary_runtime` snapshot | 缺 credential_pool 字段导致恢复时 mismatch |
| 3 | provider-match guard in `recover_with_credential_pool()` | `recover_with_credential_pool()` | 跨 provider 误标记 exhausted |
| 4 | clear `_credential_pool` on cross-provider fallback activation | `try_activate_fallback()` | fallback 后保留 stale primary pool |
| 5 | cross-process sync helper per OAuth provider | `_refresh_entry()` | 跨进程 race → refresh token reuse |
| 6 | **NEW tick41** any pool mutation MUST verify `pool.provider == agent.provider` before persist | `mark_exhausted_and_rotate()` / `_refresh_entry()` / `try_activate_fallback()` / `recover_with_credential_pool()` | pool 与 provider 不一致时仍写入 |

## Verification script (tick41 template)

```python
def verify_f4_v2():
    """F4 credential-pool-stale-snapshot v2 invariant 6 verify"""
    checks = [
        ("provider-boundary-validation order", verify_provider_boundary_order),  # invariant 1
        ("runtime snapshot single source", verify_primary_runtime_includes_pool),  # invariant 2
        ("recover_with_credential_pool guard", verify_pool_match_guard),  # invariant 3
        ("fallback clear pool", verify_fallback_clear_pool),  # invariant 4
        ("cross-process sync helpers", verify_oauth_sync_helpers),  # invariant 5
        ("pool mutation provider-match audit", verify_pool_mutation_match),  # invariant 6 NEW
    ]
    results = [(name, fn()) for name, fn in checks]
    if not all(r for _, r in results):
        raise F4V2VerifyFail(results)
```

## Cross-cluster arrows (tick41 NEW)

| arrow | from | to | severity | evidence |
|---|---|---|---|---|
| CCA-F11-F4 | F11 execute-code-approval | F4 | sev-B | execute_code RPC dispatch may invoke with stale pool |
| CCA-F4-F9 | F4 | F9 session-state | sev-B | #62665 parent session contamination may bypass pool isolation |
| CCA-F4-F1 | F4 | F1 silent-fail | sev-B | #25727 silent fallback desync |
| CCA-CVE-F7 | CVE-2026-61459 | F7 MCP supply chain | sev-A | mcp-server-kubernetes version pin required |

## Self-downgrade v4 (tick41)

- streak 17 days zero-adoption
- rule 2 + 3 + 4 + 5 四 rule 同命中
- maintain_daily + 飞书 3 选项 A/B/C
