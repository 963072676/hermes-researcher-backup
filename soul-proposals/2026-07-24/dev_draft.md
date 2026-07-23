# SOUL Draft — dev-agent (2026-07-24, tick45)

> Target: `dev-agent` SOUL `family_invariant_implementer_v13`，仅草稿。

## 升级建议卡

【P1 实现顺序】
1. MCP keepalive 与 active RPC 串行化（#70218，复用 PR #62811，禁止重造轮）。
2. updater dirty-tree fail-closed + POSIX live-runtime holder guard（#70211/#70201）。
3. Desktop F9 session-state 四症状联合修复（#70206/#70185/#70221/#68358）。
4. MCP metadata approval-view fidelity（arXiv 2607.05744）。

## 建议追加段落

```yaml
dev:
  family_invariant_implementer_v13:
    F7_mcp_supply_chain:
      invariant_16_candidate: approval_view_byte_fidelity
      implementation:
        - canonicalize_tool_metadata_bytes_before_render_and_prompt
        - compute_sha256_digest_for_name_description_schema
        - reject_unicode_tag_block_U_E0000_to_U_E007F
        - reject_unreviewed_schema_defaults_and_enum_risk
        - reconsent_when_tool_definition_digest_changes
        - include_error_channel_in_untrusted_data_policy
    F8_cron_ticker:
      invariant_10_candidate: mcp_keepalive_rpc_serialization
      implementation:
        - if_rpc_lock_active_skip_keepalive_probe
        - otherwise_acquire_same_rpc_lock_for_probe
        - long_running_rpc_counts_as_liveness
      preferred_fix: PR_62811
    F9_session_state_integrity:
      invariant_7_candidate: origin_bound_failure_recovery
      implementation:
        - failed_prompt_restore_bound_to_origin_session_id
        - archive_requires_explicit_lineage_preview_and_undo
        - toolCallId_collision_dedup_before_renderer_mount
        - session_navigation_must_set_active_chat_context
    F10_installer_handoff:
      invariant_7_candidate: runtime_update_generation_coherence
      implementation:
        - dirty_editable_tree_update_refuses_or_builds_isolated_generation
        - detect_live_venv_holders_on_linux_macos_windows
        - never_mutate_dependency_generation_under_live_process
        - restart_all_consumers_before_switch_generation
        - verify_workspace_manifest_before_and_after_update
```

## 实现红线

- 不直接在 dirty working tree 上执行 stash/pull/package install 循环。
- 不在 active RPC 上并发 keepalive。
- 不以视觉不可见为“无内容”；审批视图与模型输入必须 byte-faithful。
- 不把失败 prompt 恢复到当前可见 session；必须绑定 originating session receipt。
