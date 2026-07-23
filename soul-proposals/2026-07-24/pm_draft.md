# SOUL Draft — pm-agent (2026-07-24, tick45)

> Target: `pm-agent` SOUL `acceptance_contract_v13`，仅草稿。

## 升级建议卡

【结论】P1 acceptance contract 从 27-field v12 升为 29-field v13，新增两个字段：
1. `approval_view_fidelity`
2. `runtime_update_coherence`

## 建议追加段落

```yaml
pm:
  acceptance_contract_v13:
    extends: tick44_v12_27_field
    fields_total: 29
    new_fields:
      approval_view_fidelity:
        required: true
        sub_fields:
          rendered_metadata_digest: str
          model_context_metadata_digest: str
          byte_faithful: bool
          unicode_tag_block_rejected: bool
          schema_default_risk_checked: bool
          namespace_collision_checked: bool
          error_channel_checked: bool
          definition_change_reconsent: bool
        hard_fail: rendered_metadata_digest != model_context_metadata_digest
      runtime_update_coherence:
        required: true
        sub_fields:
          dirty_tree_detected: bool
          update_mode: enum[refuse, isolated_staged]
          live_runtime_holders: list
          cross_platform_holder_guard_passed: bool
          dependency_generation_id_before: str
          dependency_generation_id_after: str
          all_consumers_restarted: bool
          rollback_artifact_verified: bool
        hard_fail: dirty_tree_detected and update_mode not in [refuse, isolated_staged]
    status_machine_binding:
      GH_70218_PR_62811: implementation_pending
      GH_70211: verification_pending
      GH_70201: verification_pending
      GH_70206: reproduction_pending
      GH_70185: reproduction_pending
      arxiv_2607_05744: external_design_evidence
    family_signal_lifecycle:
      family_count_total: 11
      candidate_count: 1
      cross_cluster_arrows_active: 25
      cross_family_dedup_active_count: 3
      cross_family_dedup_window_hours: 24
```

## PM 验收规则

- P0 成本事件 #70216 与 trust-boundary 事件分开计分，不能把 cost severity 伪装成 security severity。
- `approval_view_fidelity.byte_faithful=false`：直接拒绝 ship。
- `runtime_update_coherence.cross_platform_holder_guard_passed=false`：直接拒绝 update release。
- Desktop session-state cluster 统一归 F9 expansion，不拉新 family。
- F12 仍 candidate；外部论文只补 defense taxonomy，不改 family 数。
