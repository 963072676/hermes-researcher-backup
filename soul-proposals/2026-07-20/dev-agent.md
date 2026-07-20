# SOUL dev-agent draft (tick42, 2026-07-20)

## Title
dev-agent-v18-canonical-invocation-path-v3

## Family / 触发

F11 execute-code-approval-unification + F12 data-injection-isolation-deck candidate + F8 cron-ticker-resilience-deck sibling + F9 session-state-integrity-deck tier-2 + F4 credential-pool-stale-snapshot stable

## Before / After Diff

### Before (tick41 dev-agent)
- 12 family registry 累计
- F4 v2 invariant 7 (pool mutation provider-match audit)
- F11 canonical_invocation_path (tick40 invariant 7 沿用)
- 6 NEW cross-cluster arrows (tick41)

### After (tick42 dev-agent) — diff
1. **canonical_invocation_path v3 升级**:
   - v2 (tick40): 6 audit_log 必填字段 (dispatch_origin / per_call_guard_status / risk_class / outcome / is_bot_tag / arrow_worsening_check)
   - v3 (tick42) NEW 2 字段:
     - **`tool_description_provenance`** — 必填 tool name + description hash + 来源 (built-in / approved / runtime-add) + risk_score
     - **`static_arg_injection_precheck`** — 必填 leading-dash detection / kwarg allowlist / type validation, 沿用 CVE-2026-61459 防御
2. **F11 invariant 8 (NEW)**:
   - 沿用 tick40 invariant 7 canonical_invocation_path + tick41 CVE-2026-61459 防御 + tick42 arxiv 2607.05120 ADI defense
   - **Invariant 8**: 任何 MCP tool call 必走 tool_description_provenance + static_arg_injection_precheck 两层预检,缺一 → block
3. **F12 candidate 评估 (tick42)**:
   - 沿用 tick36 family anti-inflation 准则 (binding)
   - condition 1 (≥ 5 GH issue): NOT MET (沿用 tick40-41)
   - condition 2 (≥ 3 platform 同根): MET 强化 (Claude Code + Codex + Gemini CLI 沿用 tick41 + tick42 CVE-2026-61459 mcp-server-kubernetes 跨 platform)
   - condition 3 (修复 PR 合入但根因 broader): tick42 沿用 #60056 + #21563 + #63183 (F11 沿用) + CVE-2026-61459 F12 同 root cause 候选
   - **决议**: **维持 candidate, F12 升 family 条件未达 (condition_1 仍未 met)**, 但 audit log 必标 `condition_2_met_strong + CVE-2026-61459 cross-cluster anchor`
4. **F8 sibling cluster 拉新**:
   - tick41 拉新 5 issue (#61674 + #39782 + #32612 + #27485 + #32666)
   - tick42 NEW pull: #27485 tier-2 sibling cluster fix PR #27492 沿用 tick33 (lock release before job execution)
   - fix PR #27492 merged status 沿用 tick33 6h dedup SLA
5. **F9 tier-2 evidence 拉新**:
   - #62665 (parent session model contaminated by delegation, 沿用 tick40-41 拉新)
   - tick42: 评估为 F9 tier-2 expansion (session state mutation 异常路径统一 fail-open 缺陷), 沿用 tick34 F9 invariant 6
6. **cross-cluster arrows 8 → 12 (tick42 NEW 4)**:
   - CCA-F12-F11 (F12 candidate → F11 execute-code-approval, sev-C) 沿用 tick40
   - CCA-F12-F7 (F12 → F7 MCP supply chain, sev-B) 沿用 tick40
   - **NEW tick42**:
     - CCA-F11-F12-CVE (F11+F12 联动 + CVE-2026-61459 arg injection, sev-A) — 5 family + 1 CVE 三联 anchor
     - CCA-F8-F9 (cron ticker resilience ↔ session state integrity, sev-B) — 沿用 tick35 CCA-3 强化
     - CCA-F12-F4 (F12 candidate → F4 credential-pool-stale, sev-C) — 跨 family data-injection + credential-pool-stale
     - CCA-CVE-F11-CVE (CVE-2026-61459 → F11 invariant 8 precheck dependency, sev-A)

## Affected

- dev-agent cron worker (12 family registry + 6 invariant 必跑 + canonical_invocation_path v3)
- qa-agent ship gate v12 必跑 tool_description_provenance + static_arg_injection_precheck
- pm-agent 24-field v10 acceptance (family_signal_lifecycle + tier-1/2/3)
- default-agent MCP readiness v6 (15-control, +control 15 cross-family PR dedup tracker)
- chief-agent tier-1.5 cross-cluster mediator (4 NEW arrows 必评 severity)

## Evidence IDs

- arxiv 2607.05120 (ADI Claude Code + Codex + Gemini CLI — F12 condition_2_met 强化)
- arxiv 2607.02857 (MOSAIC CLI composition 96.59% ASR — F11 invariant 8 沿用)
- arxiv 2607.05743 (Balkanization 39 papers 17 categories — execution-security survey 锚)
- arxiv 2607.05397 (PoE Proof of Execution 5 invariants)
- arxiv 2607.06000 (CXI — tool description provenance + static arg precheck 锚)
- CVE-2026-61459 (mcp-server-kubernetes 9.8 CRITICAL, F11 invariant 8 + F12 candidate cross-cluster anchor)
- GH #60056 (F11 主锚, tick38)
- GH #27485 (F8 tier-2 fix PR #27492, 沿用 tick33)
- GH #62665 (F9 tier-2 expansion)

## Self-downgrade v4 evaluation

streak = 18 days zero-adoption
- rule 2: F10 旧 7 hits + tick42 F11 #60077/#60799 = 9 hits ✅
- rule 3: PR-dedup fire ≥ 2 跨 family = 3 fires ✅
- rule 4: silent-fail F1 cross-month ✅
- rule 5: P1 ≥ 8 + streak ≥ 4 ✅

**决策**: maintain_daily + 飞书 3 选项 A/B/C

## Risks

- F11 invariant 8 + canonical_invocation_path v3 升级可能 block 合法 tool call → 用 prefilter mode (沿用 tick35 severity-eval) 区分 legitimate vs attack
- F12 维持 candidate 但 evidence 拉新 → family 反膨胀 (tick36 binding) 守约
- cross-cluster arrows 12 评估时延 → tier-1.5 chief 必须 6h 内完成 severity-A 评估

## Next steps

- 落地 dev-agent.md 12 family registry + canonical_invocation_path v3 段
- ship gate v12: 96 verify points (+4 tool_description_provenance + static_arg_injection_precheck verify)
- MCP readiness v6: 15-control (+control 15 cross-family PR dedup tracker)
- 沿用 tick36 family anti-inflation 准则,F12 仍 candidate