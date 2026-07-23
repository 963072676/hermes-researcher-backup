# SOUL Draft — default-agent (2026-07-24, tick45)

> Target: `default-agent` SOUL `cron_autonomy_v9`，仅草稿。

## 升级建议卡

【结论】默认 profile 增加三层运行时防线：MCP RPC serialization、update generation coherence、approval-view fidelity。继续 maintain_daily。

## 建议追加段落

```yaml
default:
  cron_autonomy_v9:
    extends: tick44_cron_autonomy_v8
    runtime_controls:
      mcp_rpc_serialization:
        active_rpc_is_liveness: true
        keepalive_on_active_rpc: skip
        keepalive_on_idle_rpc: acquire_same_lock
      update_generation_coherence:
        dirty_tree_policy: refuse
        live_runtime_holder_policy: block_update
        switch_mode: staged_generation_then_restart
        unattended_update: forbidden
      approval_view_fidelity:
        unicode_tag_block_policy: reject
        metadata_digest_required: true
        digest_change_reconsent_required: true
        schema_default_risk_review_required: true
        tool_name_collision_review_required: true
      origin_session_recovery:
        failed_prompt_receipt_required: true
        restore_to_current_visible_session: forbidden
        restore_to_originating_session_only: true
    monitoring:
      - GH_70218_and_PR_62811_status
      - GH_70211_dirty_tree_update
      - GH_70201_posix_live_runtime
      - GH_70206_GH_70185_GH_70221_GH_68358_F9_cluster
      - arxiv_2607_05744_approval_view_fidelity
    self_downgrade_v5_tick45:
      streak: 21
      rule_1_release_within_72h: true
      rule_2_installer_recurrence: true
      rule_3_cross_family_fix_fire: true
      rule_4_silent_fail_cross_month: true
      rule_5_p1_effective_ge_8: true
      rule_5A_industry_shift: true
      decision: maintain_daily
      option_B_recommended: true
      option_C_forbidden: true
```

## 默认 profile 约束

- 继续禁止 unattended `hermes update`。
- 本机 provider 为 MiniMax-M3，#70216 Bedrock P0 成本问题不直接命中当前主链，但应作为 fallback cost guard 观察。
- 任何 MCP metadata digest 变化都视为新授权对象，不能静默沿用旧批准。
- F12 保持 candidate，避免 family 膨胀。
