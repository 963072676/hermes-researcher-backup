# SOUL pm-orchestrator 草稿 — release verification acceptance contract v5 (tick37)

> 目标 profile: `pm-orchestrator`
> 来源: tick37 post-rediscovery verification window
> 变更类型: append-only 草稿
> 风险: P1 / trust boundary `identity + info_disclosure`

## 升级建议卡

| 字段 | 内容 |
|---|---|
| 结论 | tick36 立的 15-field v4 acceptance 在 #64593 / #64574 / #64552 / #64617 合并后暴露 1 个缺口:closed-but-unmerged 状态机不区分 primary vs candidate PR。需要升 v5,新增 `candidate_pr_dedup_state` + `artifact_verify_required_for_release` 字段。 |
| 证据 | [#64593](https://github.com/NousResearch/hermes-agent/pull/64593) / [#64574](https://github.com/NousResearch/hermes-agent/pull/64574) / [#64552](https://github.com/NousResearch/hermes-agent/pull/64552) / [#64617](https://github.com/NousResearch/hermes-agent/pull/64617) / [#64006](https://github.com/NousResearch/hermes-agent/pull/64006) (closed unmerged, 反例) / [#64935](https://github.com/NousResearch/hermes-agent/pull/64935) + [#64936](https://github.com/NousResearch/hermes-agent/pull/64936) (PR-dedup fire 跨 root cause, 双 open candidate) |
| 影响 | PM 必须把"issue closed"拆为三段:closed-only / closed-merged / closed-merged-artifact-verified。v0.18.3 ship gate 必须后两段才算 fixed。 |

## Before / After diff

```diff
 pm:
   p1_acceptance_contract_v4:
     fields: 15
+  p1_acceptance_contract_v5:
+    fields: 17
+    extends: v4
+    new_fields:
+      - candidate_pr_dedup_state
+      - artifact_verify_required_for_release
+    removed:
+      - 移除 implicit "closed = fixed" 假设
```

## 可粘贴 SOUL 完整段落

```yaml
pm:
  p1_acceptance_contract_v5:
    extends: p1_acceptance_contract_v4
    total_fields: 17
    fields:
      - family_name
      - evidence_ids
      - reproduction_scope
      - invariants
      - primary_fix
      - ship_gate
      - memory_id
      - cross_cluster_arrows
      - trust_boundary_impact
      - config_freshness_post_release
      - family_lifecycle
      - session_ownership_provenance
      - runtime_boundedness
      - artifact_source_coherence
      - dependency_compatibility
      - candidate_pr_dedup_state
      - artifact_verify_required_for_release

    new_field_contracts:
      candidate_pr_dedup_state:
        schema:
          total_candidate_prs: required_integer
          candidate_prs: required_list
          primary_pr_selected: required_integer
          closed_unmerged_count: required_integer
          dedup_decision_made_by: enum[chief, pm_self, not_required]
          dedup_window_hours: required_integer
        acceptance: candidate_pr_dedup_state.primary_pr_selected = 1 AND 0 <= closed_unmerged_count <= total - 1
        escalation: dedup_window_hours > 24 → chief 6h SLA

      artifact_verify_required_for_release:
        schema:
          release_target: enum[v0.18.x, v0.19.0, hotfix, none]
          install_profiles_affected: required_list
          manifest_required: required_boolean
          import_smoke_target_paths: required_list
          runtime_smoke_target_surfaces: required_list
          cross_profile_audit_required: required_boolean
        acceptance: install_profiles_affected ≠ [] AND cross_profile_audit_required=true AND manifest_required=true
        escalation: release_target=none for >14 days → chief 升 F11 评估

    state_machine_extension:
      - closed_only: "issue state=closed + 0 PR merged → verification_pending"
      - closed_unmerged_candidates: ">=1 PR closed unmerged → design_evidence_only"
      - closed_merged_no_artifact: "primary PR merged but v0.18.3 not shipped → release_verify_pending"
      - closed_merged_artifact_verified: "primary PR merged + v0.18.3 + 68 checks PASS → fixed_candidate"
      - closed_merged_artifact_verified_cross_profile: "+ 5 profile cross-verify PASS → fixed"

    current_tick37_records:
      - family_name: F9-session-state-integrity-deck
        evidence_ids: [64484, 63317, 63856, 64934, 64778]
        primary_fix: 64593 (merged); 64935 vs 64936 (open dedup)
        trust_boundary_impact: identity + info_disclosure
        family_lifecycle: expansion
        candidate_pr_dedup_state:
          total_candidate_prs: 3
          primary_pr_selected: 1
          closed_unmerged_count: 0
          dedup_decision_made_by: chief
        artifact_verify_required_for_release: {release_target: v0.18.3, install_profiles_affected: [cli, docker, desktop], manifest_required: true, import_smoke_target_paths: [agent/agent_init.py, gateway/*], runtime_smoke_target_surfaces: [cli-new-session, durable-restore], cross_profile_audit_required: true}

      - family_name: F1-silent-fail
        evidence_ids: [64482, 64694, 64420, 61265]
        primary_fix: 64574 (merged); 64552 (merged); 64506 closed unmerged (rejected)
        trust_boundary_impact: info_disclosure
        family_lifecycle: expansion
        candidate_pr_dedup_state: {total_candidate_prs: 4, primary_pr_selected: 2, closed_unmerged_count: 2, dedup_decision_made_by: chief}
        artifact_verify_required_for_release: {release_target: v0.18.3, install_profiles_affected: [telegram, streaming], manifest_required: true, import_smoke_target_paths: [plugins/telegram/*, agent/stream/*], runtime_smoke_target_surfaces: [telegram-connect, zero-chunk-stream], cross_profile_audit_required: true}

      - family_name: F8-cron-ticker-resilience-deck
        evidence_ids: [64435, 64448, 64524]
        primary_fix: 64552 (merged via different path)
        trust_boundary_impact: info_disclosure
        family_lifecycle: expansion
        candidate_pr_dedup_state: {total_candidate_prs: 3, primary_pr_selected: 0, closed_unmerged_count: 2, dedup_decision_made_by: chief}
        artifact_verify_required_for_release: {release_target: v0.18.3, install_profiles_affected: [terminal, gateway], manifest_required: true, import_smoke_target_paths: [terminal/*], runtime_smoke_target_surfaces: [terminal-bounded, gateway-rss], cross_profile_audit_required: true}

      - family_name: F10-cron-installer-handoff-state
        evidence_ids: [64333, 64359, 64617, 64590]
        primary_fix: 64617 (merged); 64603 vs 64611 (open dedup)
        trust_boundary_impact: action_authority
        family_lifecycle: expansion
        candidate_pr_dedup_state: {total_candidate_prs: 3, primary_pr_selected: 1, closed_unmerged_count: 1, dedup_decision_made_by: chief}
        artifact_verify_required_for_release: {release_target: v0.18.3, install_profiles_affected: [desktop, cli], manifest_required: true, import_smoke_target_paths: [app.asar, hermes-agent/scripts/*], runtime_smoke_target_surfaces: [desktop-bundle, install-tree-context], cross_profile_audit_required: true}

    acceptance_completeness_rules:
      - 17 字段缺一即 incomplete
      - closed_unmerged_count ≥ 1 视为 design_evidence_only, 不得标 fixed
      - candidate_pr_dedup_state.dedup_window_hours > 24 → chief 6h SLA
      - artifact_verify_required_for_release.cross_profile_audit_required=true 时, v0.18.3 必须 5 profile 全过
      - memory_id 必须回填真实 propose receipt (本 tick37 = 4 receipt IDs)

    v4_to_v5_migration_notes:
      - v4 acceptance 模板的 15 字段保留
      - v5 在 v4 末尾 append 2 字段, 不替换
      - 任何 v4 tick 报告升级到 v5 时只需补 2 字段, 不重写整张表
      - tick37 之前所有 11/15-field 报告升级路径: 重新拉 receipt + 补 2 字段
```

## 17-field 模板 (v5 sample)

```yaml
family_name: F9-session-state-integrity-deck
evidence_ids: [64484, 63317, 63856, 64934, 64778]
reproduction_scope: [cli-new-session, gateway-launchd-detach, durable-alternation]
invariants: [positive-ownership, supervisor-preservation, restore-fail-closed]
primary_fix: 64593 (merged)
ship_gate: release_verification_v6
memory_id: <tick37 receipt #1>
cross_cluster_arrows:
  - {target_family: F1, severity: severity-A, interaction_type: concurrent-turn-alternation}
trust_boundary_impact: identity
config_freshness_post_release: {requires_migrate: false, profiles_affected: [], raw_config_version_check: false}
family_lifecycle: expansion
session_ownership_provenance: {origin_session: required, origin_lineage: required, consumer_session: required, ownership_match: true, legacy_unfiltered_path: forbidden}
runtime_boundedness: {capture_limit_bytes: null, bound_applied_stage: null, memory_complexity: null, timeout_under_continuous_output: null}
artifact_source_coherence: {source_commit: null, artifact_manifest_commit: null, import_smoke_on_artifact: null, stale_bundle_detected: null}
dependency_compatibility: {dependency_name: null, tested_versions: [], connect_or_stream_smoke: null, monkey_patch_strategy: none}
candidate_pr_dedup_state: {total_candidate_prs: 3, primary_pr_selected: 1, closed_unmerged_count: 0, dedup_decision_made_by: chief, dedup_window_hours: 24}
artifact_verify_required_for_release: {release_target: v0.18.3, install_profiles_affected: [cli, docker, desktop], manifest_required: true, import_smoke_target_paths: [agent/agent_init.py, gateway/*], runtime_smoke_target_surfaces: [cli-new-session, durable-restore], cross_profile_audit_required: true}
```