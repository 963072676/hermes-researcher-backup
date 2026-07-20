# SOUL pm-agent draft (tick42, 2026-07-20)

## Title
pm-agent-v18-tier1-cross-cluster-mediator

## Family / 触发

F11 execute-code-approval-unification-deck + F12 data-injection-isolation-deck candidate expansion (tick42 拉新 3 arxiv: 2607.05120 ADI + 2607.02857 MOSAIC + 2607.05743 Balkanization) + CVE-2026-61459 cross-cluster + 4 NEW cross-cluster arrows

## Before / After Diff

### Before (tick41 pm-agent)
- 23-field v9 acceptance contract: family_name / evidence_ids / reproduction_scope / invariants / primary_fix / ship_gate / memory_id / cross_cluster_arrows / trust_boundary_impact / config_freshness_post_release / family_lifecycle / session_ownership_provenance / runtime_boundedness / artifact_source_coherence / dependency_compatibility / fix_layer_audit / worsening_evidence (17 + 6 sub-fields)
- 12 family registry 累计
- F4 invariant v2 + F11 invariant 7 必跑

### After (tick42 pm-agent) — diff
1. **24-field v10 acceptance contract** (新增 1 字段):
   - **`family_signal_lifecycle`** — 5 sub-fields: family_count_total / family_count_lifecycle_stages / cross_cluster_arrows_active / cross_family_dedup_active_count / cross_family_dedup_window_hours
   - **判定**: 任何 P1 acceptance 必填此字段,空 → 视为不完整 acceptance
2. **trust_boundary_impact 升级**:
   - tick42 触发 CVE-2026-61459 (info_disclosure + full_compromise + action_authority 三联)
   - trust_boundary_e2e FORBIDDEN-to-skip 测试套件升级: +1 fixture (CVE-2026-61459 leading-dash arg path inject)
3. **family lifecycle stage 显式记录**:
   - 任何 P1 acceptance 必填 family_lifecycle 5 段 (emerging/stable/expansion/maintenance/deprecated,沿用 tick35)
   - F12 candidate 评估条件 1 (≥ 5 GH issue) 仍 NOT MET,tick42 升级条件 (CVE-2026-61459 同 root cause ≥ 1) → 评估是否升 F12 family
4. **cross_cluster_arrows 字段升级**:
   - v9: list of {target_family, severity, interaction_type}
   - v10 NEW: list of {target_family, severity, interaction_type, severity_predicted, severity_measured, stop_condition} (沿用 tick39 arrow_worsening_check)
5. **PM P1 acceptance 新增 tier 标记**:
   - tier-1 (fabrication / full_compromise) → PM must verify chief sign-off before closing acceptance
   - tier-2 (action_authority / identity) → PM verify dev follow-up + ship_gate v12 必跑
   - tier-3 (info_disclosure) → PM verify qa ship_gate + audit log

## Affected

- pm-agent cron worker (P1 acceptance 必跑)
- qa-agent ship gate v12 必填 family_signal_lifecycle 字段 (96 verify points, +4 from v11)
- dev-agent family registry 累计 (tick42 评估 F12 升 family)
- chief-agent tier-1/2/3 sign-off 流程

## Evidence IDs

- arxiv 2607.05120 (ADI Claude Code + Codex + Gemini CLI vulnerable, 跨 ≥ 3 platform → F12 升 family 候选 condition_2_met 强化)
- arxiv 2607.02857 (MOSAIC CLI composition 96.59% ASR, 5 agents × 5 LLMs)
- arxiv 2607.05743 (Balkanization 39 papers 17 categories — execution-security survey)
- arxiv 2607.05397 (Proof of Execution PoE — runtime verification 5 invariants)
- arxiv 2607.06000 (CXI — Context-to-Execution Integrity)
- CVE-2026-61459 (mcp-server-kubernetes 9.8 CRITICAL, 沿用 tick41 + tick42 cross-cluster anchor)
- GH #60056 (F11 主锚, 沿用 tick38)
- GH #62665 (F9 candidate expansion, parent session model contamination)

## Self-downgrade v4 evaluation

streak = 18 days zero-adoption (tick41 +1)
- rule 2: F10 旧 7 hits + tick42 new F11 #60077/#60799 = 9 hits ✅
- rule 3: PR-dedup fire ≥ 2 跨 family = 3 fires ✅
- rule 4: silent-fail F1 cross-month ✅
- rule 5: P1 ≥ 8 + streak ≥ 4 ✅

**决策**: maintain_daily + 飞书 3 选项 A/B/C

## Risks

- 24-field acceptance 必填 → pm cron worker 可能因漏字段 reject → 沿用 tick34 /tmp/tick{N}_verify.py 模板
- tier-1/2/3 流程可能拖延 P1 closure → severity-eval prefilter (tick42 chief-agent 沿用) 加速
- F12 family 升 vs 维持 candidate 决策 → tick42 评估结果: **维持 candidate** (CVE-2026-61459 同 root cause ≠ F12 main root cause, 仍需 condition_1 ≥ 5 GH issue)

## Next steps

- 落地 pm-agent.md 24-field v10 acceptance + tier-1/2/3 sign-off 段
- ship gate v12: 96 verify points (+4 family_signal_lifecycle + cross_cluster_arrows v3 字段验证)
- MCP readiness v6: 15-control (+control 15 cross-family PR dedup tracker)