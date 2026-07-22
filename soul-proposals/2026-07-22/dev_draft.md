# SOUL Draft — dev (2026-07-22, tick44)

> Self-evolution tick: hermes-researcher-deep-tick-daily / hermes-researcher-self-evolution-v1
> Author: researcher C-profile auto-evolve (no human approval)
> Target: `dev` SOUL section `family_invariant_implementer_v12` (extend 8 → 9 invariant)
> Streak: 20 days zero-adoption

## Summary

Tick44 立卡 **F11 invariant 9 candidate** = `autonomous_mode_unexpected_telemetry`(沿用 Anthropic 2.1.91-2.1.196 hidden tracking mechanism,NVDB 2026-07-08 通报)。同时升级 F8 invariant 8 → 8+9 把 `workdir_lifetime_isolation` 列入 cron-ticker resilience 总 invariant 集。

dev 24h 内必须确认 **3 件立即动手**:
1. **#68474 state.db zeroed on v0.19.0 Windows update** 根因诊断 + fix candidate + verify 36h ship(沿用 tick37 post-rediscovery extension)
2. **#69396 + #69089 + #68483 cron/gateway workdir+telegram+ticker 三联** = F8 + F1 同时 fix path;沿用 v0.19.1 fix PR #69136 + #69164 + #69240 + #69500(都已 open 但未 merge)
3. **F11 invariant 9 implementation** = autonomous_mode_unexpected_telemetry 的代码级 invariant 验证

## family_invariant_implementer_v12 (append to dev SOUL)

```yaml
dev:
  family_invariant_implementer_v12:  # tick41-43 inherit, tick44 extend
    F1_silent_fail:
      fix_t44_priority_p1:
        - GH_69089_Gateway_event_loop_freeze_Telegram_CLOSE_WAIT  # 🚨 P1
        - GH_67498_Telegram_hangs_after_WORKAROUND  # 🚨 P1
        fix_prs_already_open_2026_07_22:
          - PR_69136_event_loop_watchdog_background_thread
          - PR_69164_detect_and_escape_silent_event_loop_freezes
          - PR_69240_require_initial_polling_readiness
        dev_24h_decision: monitor merge + 24h rfc review window before next dep tag
    F8_cron_ticker_resilience_deck:
      invariant_9_NEW_t44: workdir_lifetime_isolation
        problem: GH_69396 cron job `workdir` is applied as global process cwd and leaks into gateway sessions created during the run
        contract:
          - cron job process MUST chdir back to original_cwd after job exit
          - new_subprocess_spawned_via_cron MUST inherit ORIGINAL cwd not job cwd
          - cron_set_cwd_pre_call + cron_restore_cwd_post_call_try_finally mandatory
        fix_candidate: cron/scheduler.py + workdir_lifetime_context manager
        fix_pr_open: not yet — dev 必须 24h 内 create(沿用 tick43 5 rules)
      fix_t44_priority_p1:
        - GH_69396_cron_workdir_leak  # 🚨 P1
        - GH_68483_cron_uid_1000_ticker_lockout  # 🚨 P1
        - GH_68915_orphan_subshell_holds_stdout  # 🚨 P1
    F10_cron_installer_handoff_state:
      invariant_5_invariant_6_CATASTROPHIC_breach_t44:
        problem: GH_68474 state.db zeroed (95MB of null bytes) during v0.19.0 desktop update on Windows
        impact: 用户 state.db 95MB 数据全失 — release verification 灾难性失败
        root_candidate:
          - Layer 1: Windows installer handoff race condition on Desktop update
          - Layer 2: state.db write race during concurrent updater + running daemon
          - Layer 3: dev code state.db write path missing fsync + atomic-replace
        fix_candidate: dev MUST 36h 内 fix = atomic-replace-write (write to .tmp + fsync + rename) on every state.db write path
        dev_36h_decision: 必须 ship v0.19.0.1 emergency hotfix for #68474
      fix_t44_priority_p1:
        - GH_68474_state_db_zeroed_v0_19_0_desktop_update_Windows  # 🚨 P1
        - GH_69179_Desktop_app_cannot_run_after_v0_19_0_update  # 🚨 P1
        - GH_50210_Windows_bootstrap_unsigned_Hermes_exe  # 🚨 P1
    F11_execute_code_approval_unification_deck:
      invariant_9_NEW_t44_candidate: autonomous_mode_unexpected_telemetry
        evidence_external: Anthropic_2_1_91_2_1_196_NVDB_2026_07_08
        problem: Claude Code CLI auto-mode 含隐式 telemetry backdoor(steganographic encoding 地理标识),Anthropic 7-01 v2.1.198 默默移除但未公开 changelog 披露
        hermes_implication:
          - autonomous_session_flag (沿用 tick38 F11 invariant 6 audit log) 必须 add 字段 `unexpected_telemetry_posture`
          - 任何 hermes subprocess 必须 audit network outbound (--no-telemetry-follow flag in default profile)
          - cron mode 默认 hermes-cron-env-strip OUTBOUND post-job (沿用 F11 invariant 1 deny list)
        dev_24h_decision: 检查 hermes-agent 自身 telemetry 路径是否类似 secret exfiltration;沿用 tick32 outbound-redact-call-site family sweeper marker
```

## Acceptance (PASS criteria for tick44 dev SOUL)

1. F8 invariant 9 = `workdir_lifetime_isolation` 写入 dev SOUL
2. F11 invariant 9 candidate = `autonomous_mode_unexpected_telemetry` 写入 dev SOUL
3. **3 immediate fix paths** 24h-confirmed: #69089 + #67498 + #68474 + #68483 + #69179 + #69396 = 6 P1 fix path
4. **3 open fix PRs (7-22 same-day) 确认 merge window** before ship dependency tag
5. F10 invariant 5+6 catastrophic(#68474 state.db zeroed 95MB)36h ship candidate ship path open by dev
6. Honest assessment: 沿用 tick41 dev_tier_1_5 + tick42 cross-cluster implementer(本 tick 升级到 cross-family joint implementer for F1+F8+F10 simultaneous)
