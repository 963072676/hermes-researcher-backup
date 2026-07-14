# SOUL pm 草稿 — P1 acceptance contract v4（15-field）

> 目标 profile: `pm-orchestrator`
> 来源: tick36 P1 cross-surface hot window
> 变更类型: append-only 草稿

## 升级建议卡

| 字段 | 内容 |
|---|---|
| 结论 | tick35 的 11-field v3 无法表达 #64484 ownership、#64435 boundedness、#64333 artifact coherence、#64482 dependency compatibility；升级到 15-field v4。 |
| 证据 | [#64484](https://github.com/NousResearch/hermes-agent/issues/64484)、[#64435](https://github.com/NousResearch/hermes-agent/issues/64435)、[#64333](https://github.com/NousResearch/hermes-agent/issues/64333)、[#64482](https://github.com/NousResearch/hermes-agent/issues/64482) |
| 影响 | PM 不再把“issue closed”当 acceptance；必须拿到 merged PR + surface verify 回执。 |

## Before / After diff

```diff
 pm:
   p1_acceptance_contract_v3:
     fields: 11
+  p1_acceptance_contract_v4:
+    fields: 15
+    extends: v3
+    new_fields:
+      - session_ownership_provenance
+      - runtime_boundedness
+      - artifact_source_coherence
+      - dependency_compatibility
```

## 可粘贴 SOUL 完整段落

```yaml
pm:
  p1_acceptance_contract_v4:
    extends: p1_acceptance_contract_v3
    total_fields: 15
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

    field_contracts:
      session_ownership_provenance:
        required_for: [async_delegation, background_process, restored_notification]
        schema:
          origin_session: required
          origin_lineage: required
          consumer_session: required
          ownership_match: required_boolean
          legacy_unfiltered_path: forbidden_for_restored_events
        acceptance: ownership_match=true 且 foreign/keyless restored event 不可消费

      runtime_boundedness:
        required_for: [terminal, execute_code, mcp_result, streaming]
        schema:
          capture_limit_bytes: required_integer
          bound_applied_stage: enum[capture, postprocess]
          memory_complexity: required
          timeout_under_continuous_output: required_boolean
        acceptance: bound_applied_stage=capture 且 memory_complexity=O(limit)

      artifact_source_coherence:
        required_for: [desktop, docker, installer, packaged_plugin]
        schema:
          source_commit: required
          artifact_manifest_commit: required
          import_smoke_on_artifact: required_boolean
          stale_bundle_detected: required_boolean
        acceptance: source_commit == artifact_manifest_commit 且 artifact smoke=true

      dependency_compatibility:
        required_for: [messaging_adapter, provider_stream, native_module]
        schema:
          dependency_name: required
          tested_versions: required_list
          connect_or_stream_smoke: required_boolean
          monkey_patch_strategy: enum[none, wrapper, subclass, instance_patch]
        acceptance: smoke=true 且 slotted/frozen object 禁止 instance_patch

    state_semantics:
      - issue_closed_pr_unmerged: verification_pending
      - issue_closed_pr_merged: release_verify_pending
      - issue_open_primary_pr_open: implementation_pending
      - only_after_all_surface_checks: accepted

    current_tick36_records:
      - family_name: session-state-integrity-deck
        evidence_ids: [64484, 63494, 63317, 63856]
        trust_boundary_impact: identity
        family_lifecycle: expansion
        session_ownership_provenance: required
      - family_name: cron-ticker-resilience-deck
        evidence_ids: [64435, 64448, 64524]
        trust_boundary_impact: info_disclosure
        family_lifecycle: expansion
        runtime_boundedness: required
      - family_name: cron-installer-handoff-state
        evidence_ids: [64333, 64359]
        family_lifecycle: expansion
        artifact_source_coherence: required
      - family_name: silent-fail
        evidence_ids: [64482, 64506, 64420]
        family_lifecycle: expansion
        dependency_compatibility: required

    final_acceptance_rules:
      - 15 字段缺一即 incomplete
      - closed-but-unmerged 不得标 fixed
      - cross_cluster_arrows 非空时等待 chief sign-off
      - trust_boundary_impact != none 时走 chief 6h SLA
      - memory_id 必须回填真实 propose receipt
```

## 15-field 模板

```yaml
family_name: F9-session-state-integrity-deck
evidence_ids: [64484, 63494, 63317, 63856]
reproduction_scope: [cli-new-session, durable-delegation-restore]
invariants: [positive-ownership, lineage-aware, restored-fail-closed]
primary_fix: TBD
ship_gate: release_verification_v6
memory_id: a6b1ca1a-b1fe-4f57-b76c-5ff449b28779
cross_cluster_arrows:
  - {target_family: F1, severity: severity-A, interaction_type: restored-completion-misroute}
trust_boundary_impact: identity
config_freshness_post_release: {requires_migrate: false, profiles_affected: [], raw_config_version_check: false}
family_lifecycle: expansion
session_ownership_provenance: {origin_session: required, origin_lineage: required, consumer_session: required, ownership_match: true, legacy_unfiltered_path: forbidden}
runtime_boundedness: {capture_limit_bytes: null, bound_applied_stage: null, memory_complexity: null, timeout_under_continuous_output: null}
artifact_source_coherence: {source_commit: null, artifact_manifest_commit: null, import_smoke_on_artifact: null, stale_bundle_detected: null}
dependency_compatibility: {dependency_name: null, tested_versions: [], connect_or_stream_smoke: null, monkey_patch_strategy: none}
```
