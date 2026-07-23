# SOUL Draft — qa-agent (2026-07-24, tick45)

> Target: `qa-agent` SOUL `release_verification_v9`，仅草稿。

## 升级建议卡

【结论】沿用 tick44 80-check strict baseline，追加 8 项，形成 **ship gate v15 = 88 checks**。本次只追加，不重写旧门数。

## 建议追加段落

```yaml
qa:
  release_verification_v9:
    extends: tick44_ship_gate_v14_80_check_strict
    ship_gate_v15_total: 88
    new_checks:
      - mcp_keepalive_skips_when_rpc_lock_active
      - mcp_keepalive_acquires_rpc_lock_when_idle
      - unicode_tag_block_metadata_rejected
      - metadata_digest_change_requires_reconsent
      - dirty_tree_update_refuses_or_isolated_staged
      - posix_live_venv_holder_blocks_mutation
      - failed_prompt_restores_to_origin_session_only
      - desktop_archive_cascade_has_preview_audit_undo
    hard_fail_rules:
      - approval_view_digest_mismatch_reject_ship
      - tool_definition_changed_without_reconsent_reject_ship
      - live_runtime_dependency_hot_mutation_reject_ship
      - dirty_tree_workspace_manifest_loss_reject_ship
      - retry_restored_to_non_origin_session_reject_ship
    forbidden_skip_flags:
      - --skip-approval-view-fidelity
      - --skip-mcp-rpc-serialization
      - --skip-runtime-update-coherence
      - --skip-origin-session-recovery
```

## 必测 fixtures

1. Metadata 五 surface：description、input schema、tool name、error result、post-approval mutation。
2. Unicode TAG block：审批 UI 不得吞字符后继续给模型；必须拒绝或显示显式 escaped code points。
3. MCP long-running call：probe 到点时不能交错；active call 本身算 liveness。
4. Dirty tree：连续三次 update attempt 不得删除 workspace manifest 或重写 lockfile 为不一致状态。
5. POSIX live runtime：加载 old interface 后不得从 new generation lazy import implementation。
6. Desktop：provider timeout 后 composer 恢复必须带 origin session receipt；切换可见 session 不得改变 receipt。
7. Archive：compression lineage cascade 必须预览受影响 session 数，有 audit 和 undo。
8. 大 session renderer：重复 toolCallId 不得造成 root error-boundary render loop。
