# SOUL qa-agent draft (tick42, 2026-07-20)

## Title
qa-agent-v18-ship-gate-v12

## Family / 触发

F11 execute-code-approval-unification + F12 data-injection-isolation-deck candidate + F8 cron-ticker-resilience-deck + F4 credential-pool-stale-snapshot + CVE-2026-61459 arg injection

## Before / After Diff

### Before (tick41 qa-agent)
- ship gate v11: 92 verify points (tick41 沿用: 5 grep + 20 cross-profile permission + 6 MCP supply chain + 17 P1 acceptance v5 + 4 cross-cluster arrows + 4 trust boundary e2e + 12 runtime smoke per family + 4 post-merge regression = 92)
- 4 trust boundary e2e (fabrication / fail-open / observer disconnect / info_disclosure, tick35 沿用)
- 12 runtime smoke per family (tick37 沿用: F1 4 + F8 4 + F9 4 + F10 4 = 16 实际,部分 overlap)

### After (tick42 qa-agent) — diff
1. **ship gate v12: 96 verify points** (+4 NEW):
   - tick41 92 全部保留
   - tick42 NEW 4 verify:
     - `tool_description_provenance_verify` (F11 invariant 8)
     - `static_arg_injection_precheck_verify` (CVE-2026-61459 leading-dash detection)
     - `cross_family_pr_dedup_tracker` (control 15)
     - `family_signal_lifecycle_field_present` (24-field v10 acceptance)
2. **runtime smoke per family 升级 12 → 16**:
   - F1 4 (silent-fail, 沿用 tick37)
   - F8 4 (cron-ticker, 沿用 tick37)
   - F9 4 (session-state, 沿用 tick37)
   - F10 4 (installer-handoff, 沿用 tick37)
   - **tick42 NEW F11 4**: canonical_invocation_path audit / tool_description_provenance audit / static_arg_injection_precheck audit / autonomous_session_flag audit (沿用 tick38-40 F11 invariant 7 + 8)
3. **trust boundary e2e 升级 4 → 5**:
   - 沿用 tick35 4 段: fabrication / fail-open / observer disconnect / info_disclosure
   - **tick42 NEW**: full_compromise e2e (CVE-2026-61459 arg injection full path: --server flag 注入 + bearer token exfil + cluster takeover)
4. **hard-fail rule 升级**:
   - 沿用 tick40 3 FORBIDDEN skip flag: `--skip-canonical-invocation-path` / `--skip-family-12-verify` / `--skip-arrow-worsening`
   - **tick42 NEW 3 FORBIDDEN skip flag**: `--skip-tool-description-provenance` / `--skip-static-arg-injection-precheck` / `--skip-cross-family-pr-dedup`
5. **cross-cluster arrows verify 升级**:
   - tick41: 4 arrows (CCA-F11-F4 / F4-F9 / F9-F4 / CVE-F7-F11-F12)
   - tick42: 4 NEW arrows verify (CCA-F11-F12-CVE / F8-F9 / F12-F4 / CVE-F11-CVE) — total 8 cross-cluster arrows verified
6. **5 install profile smoke 升级**:
   - tick37 5 profile 必跑 (Desktop / Docker / CLI / TUI / MCP_stdio)
   - tick42: profile 必跑 + cross_profile_audit 必填 + family_signal_lifecycle audit log entry

## Affected

- qa-agent cron worker (ship gate v12 必跑, 96 verify points)
- pm-agent 24-field v10 acceptance (family_signal_lifecycle 必填)
- dev-agent 12 family registry + canonical_invocation_path v3
- chief-agent tier-1.5 cross-cluster mediator
- default-agent MCP readiness v6 (15-control)

## Evidence IDs

- arxiv 2607.05120 (ADI — F12 candidate condition_2_met 强化)
- arxiv 2607.02857 (MOSAIC CLI composition — F11 invariant 8 沿用)
- arxiv 2607.05743 (Balkanization — execution-security survey 锚)
- arxiv 2607.05397 (PoE Proof of Execution — runtime verification 5 invariants)
- arxiv 2607.06000 (CXI — Context-to-Execution Integrity, tool description + static arg precheck 锚)
- CVE-2026-61459 (mcp-server-kubernetes 9.8 CRITICAL — qa ship gate v12 full_compromise e2e fixture)
- GH #60056 (F11 主锚, tick38)
- GH #27485 (F8 tier-2 fix PR #27492, 沿用 tick33)

## Self-downgrade v4 evaluation

streak = 18 days zero-adoption
- rule 2: F10 旧 7 hits + tick42 F11 #60077/#60799 = 9 hits ✅
- rule 3: PR-dedup fire ≥ 2 跨 family = 3 fires ✅
- rule 4: silent-fail F1 cross-month ✅
- rule 5: P1 ≥ 8 + streak ≥ 4 ✅

**决策**: maintain_daily + 飞书 3 选项 A/B/C

## Risks

- ship gate v12 (96 verify points) 跑耗时可能 > 30s → 用 cache + parallel verify (沿用 tick37)
- 5 trust boundary e2e (含 full_compromise) fixture setup 复杂度高 → 沿用 tick35 fixture pattern (api_key 必须用 placeholder pattern `sk-FAKE_...`)
- 5 install profile smoke 跨 platform → 用 cross_profile_audit strict mode (沿用 tick41)

## Next steps

- 落地 qa-agent.md ship gate v12 96 verify points + 5 trust boundary e2e 段
- MCP readiness v6: 15-control (+control 15 cross-family PR dedup tracker)
- 沿用 tick36 family anti-inflation 准则, F12 仍 candidate
- trust boundary e2e fixture 用 `sk-FAKE_...` placeholder pattern