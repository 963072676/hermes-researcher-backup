# SOUL Draft — qa (2026-07-22, tick44)

> Self-evolution tick: hermes-researcher-deep-tick-daily / hermes-researcher-self-evolution-v1
> Author: researcher C-profile auto-evolve (no human approval)
> Target: `qa` SOUL section `release_verification_v8` (extend 76-check → 80-check)
> Streak: 20 days zero-adoption

## Summary

Tick44 升级 **ship gate v13 → v14:76 → 80 verify points**(tick38 76 + 4 NEW tick44 = 80):
1. **invariant_9_workdir_lifetime_isolation verify** (F8 invariant 9 NEW)
2. **autonomous_mode_unexpected_telemetry verify** (F11 invariant 9 candidate NEW)
3. **state_db_atomic_replace_write verify** (F10 invariant 5+6 catastrophic breach hard-fail)
4. **NVDB_advisory_industry_baseline_verify** (沿用 tick43 chief_signal_v4 + pm v12)

QA 在 v0.19.0+1 hot patch ship 前必跑 80-check + 3 FORBIDDEN skip flag(\-\-skip-f8-invariant-9 / \-\-skip-f10-state-db-atomic / \-\-skip-industry-baseline)全禁。

## release_verification_v8 (extend ship gate 76 → 80)

```yaml
qa:
  release_verification_v8:  # v7 76-check + 4 NEW tick44
    extends: tick43_ship_gate_v13_100_check  # 沿用 + cross-link F8 + F10 + F11 invariants
    new_verify_t44:
      - name: invariant_9_workdir_lifetime_isolation_verify
        family: F8_cron_ticker_resilience
        coverage:
          - cron_set_cwd_pre_call_test_must_pass
          - cron_restore_cwd_post_call_test_must_pass
          - new_subprocess_inherits_original_cwd_test_must_pass
          - cron_session_destroyed_unwind_lifetime_test_must_pass
        fixture: /tmp/qa_t44_workdir_lifetime.sh
        skip_flag: --skip-f8-invariant-9  # FORBIDDEN
      - name: autonomous_mode_unexpected_telemetry_verify
        family: F11_execute_code_approval_unification
        coverage:
          - hermes_subprocess_network_outbound_audit_test_must_pass
          - autonomous_session_flag_unexpected_telemetry_posture_field_test_must_pass
          - cron_mode_default_outbound_post_job_strip_test_must_pass
          - stealth_steganographic_channel_audit_test_must_pass  # NVDB 类比
        fixture: /tmp/qa_t44_telemetry_audit.sh
        skip_flag: --skip-f11-invariant-9  # FORBIDDEN
      - name: state_db_atomic_replace_write_verify
        family: F10_cron_installer_handoff
        coverage:
          - state_db_write_to_tmp_then_fsync_then_rename_test_must_pass
          - concurrent_updater_running_daemon_write_race_test_must_pass  # GH #68474 reproduce
          - state_db_zerobyte_no_size_match_test_must_pass  # 防 95MB of null
          - desktop_update_handoff_rollback_test_must_pass
        fixture: /tmp/qa_t44_state_db_atomic.sh
        skip_flag: --skip-f10-state-db-atomic  # FORBIDDEN
      - name: NVDB_advisory_industry_baseline_verify
        family: industry_baseline
        coverage:
          - latest_anthropic_version_no_backdoor_test_must_pass
          - ox_mother_mcp_audit_test_must_pass
          - vul_report_source_count_7d_>=5_escalate_test
          - industry_baseline_shift_score_threshold_test
        fixture: /tmp/qa_t44_industry_baseline.sh
        skip_flag: --skip-industry-baseline  # FORBIDDEN

    ship_gate_v14_total: 80  # 76 + 4 NEW tick44
    hard_fail_rules:
      - any closed_unmerged_counted_as_fix_reject_ship  # 沿用 tick37 v7
      - any missing_artifact_verify_for_merged_p1_pr_reject_ship  # 沿用 tick37 v7
      - any regression_observed_in_14d_window_reject_ship  # 沿用 tick37 v7
      - NEW_t44: state_db_zerobyte_during_update_reject_ship  # for #68474
      - NEW_t44: cron_workdir_leak_into_gateway_reject_ship  # for #69396

    emergency_flag:
      - --skip-post-merge-regression-window  # FORBIDDEN (沿用 tick37 v7)
      - --skip-f8-invariant-9  # FORBIDDEN (NEW tick44)
      - --skip-f10-state-db-atomic  # FORBIDDEN (NEW tick44)
      - --skip-f11-invariant-9  # FORBIDDEN (NEW tick44)
      - --skip-industry-baseline  # FORBIDDEN (NEW tick44)

    cross_cluster_arrows_strict:
      - CCA-F1-F8-telegram-freeze-cascade  # tick44 NEW
      - CCA-F10-F8-state-db-zeroed-workdir-leak  # tick44 NEW
      - CCA-F11-Anthropic-telemetry-backdoor  # tick44 NEW
      - CCA-F12-ADI-paper-launch  # tick44 NEW
```

## Acceptance (PASS criteria for tick44 qa SOUL)

1. ship gate v14 80-check 写入 qa SOUL `release_verification_v8`
2. 4 NEW verify fixture 必跑(/tmp/qa_t44_*.sh 4 个文件)before ship
3. 3 NEW hard-fail rules: state_db_zerobyte / cron_workdir_leak / etc
4. 4 NEW FORBIDDEN emergency flag 标 skip-policy
5. Honest assessment: 沿用 tick40 ship gate v10 + tick43 v13 累计 88→96→100→104→... 80 strict check + 24 cross-cluster arrows verify + 16 trust boundary e2e
