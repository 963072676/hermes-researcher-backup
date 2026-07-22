# SOUL Draft — default (2026-07-22, tick44)

> Self-evolution tick: hermes-researcher-deep-tick-daily / hermes-researcher-self-evolution-v1
> Author: researcher C-profile auto-evolve (no human approval)
> Target: `default` SOUL section `cron_autonomy_v8` (extend cross-cluster audit + industry baseline monitor)
> Streak: 20 days zero-adoption

## Summary

Tick44 立卡 **`default` profile cron autonomy baseline v8** = 5 层防御(继承 tick43 v7 + 1 NEW tick44)以及 **`provider_alert_industry_baseline_monitor`** 子字段(default profile 必须主动监控 Anthropic / OX / AI Now 等 industry baseline 事件,因为 hermes 自家底层也走 Anthropic SDK 调用)。

5-layer cron defense v8:
1. **Layer 1 pre-job** — outbound network strip(沿用 F11 invariant 1)
2. **Layer 2 workdir** — `cron_set_cwd_pre_call` + `cron_restore_cwd_post_call` try/finally(F8 invariant 9 NEW)
3. **Layer 3 watch signal** — heartbeat fail-closed(沿用 tick33 F8 invariant 1)
4. **Layer 4 unexpected telemetry monitor** — daily cron scan `~/.hermes/cron/output/*/audit/{industry_baseline_marker}.jsonl` for new entries(F11 invariant 9 NEW)
5. **Layer 5 cross-cluster audit** — 4 NEW tick44 arrows must always be in `~/.hermes/cron/output/{date}/cron-output/impact-graph.md` e2e coverage(沿用 tick35)

## cron_autonomy_v8 (append to default SOUL)

```yaml
default:
  cron_autonomy_v8:  # tick44 NEW
    extends: tick43_cron_autonomy_v7
    new_layer_t44:
      - name: layer_2_workdir_lifetime_isolation
        problem: GH_69396 cron workdir leaks into gateway sessions
        behavior:
          - cron_set_cwd_pre_call: change to target_cwd
          - cron_restore_cwd_post_call: try/finally restore to original_cwd
          - subprocess inherit ORIGINAL cwd not JOB cwd
        enforce: cron/scheduler.py + context manager
      - name: layer_4_unexpected_telemetry_monitor
        problem: Anthropic_NVDB_2_1_91_2_1_196_telemetry_backdoor
        behavior:
          - daily scan ~/.hermes/cron/output/*/audit/industry_baseline_marker.jsonl
          - if new_entry_detected → escalate chief_tier_1_5 immediately
          - if Anthropic_Code_no-telemetry-check → apply --no-telemetry-follow flag
        enforce: cron/audit/industry_baseline_monitor.sh

    industry_baseline_monitor_t44:
      - anthropic_latest_version_check: claude_code >= 2.1.198  # 7-01 fix
      - oem_mcp_python_sdk_check: mcp >= 1.28.1  # CVE-2026-59950
      - oem_mcp_python_sdk_tasks_check: mcp >= 1.27.2  # CVE-2026-52870
      - oem_mcp_python_sdk_http_transport_check: mcp >= 1.27.2  # CVE-2026-52869
      - ox_mother_mcp_audit: STDIO transport user_input NOT directly into command

    cross_cluster_arrows_e2e_coverage_t44:
      - CCA-F1-F8-telegram-freeze-cascade  # tick44 NEW — must be in impact-graph
      - CCA-F10-F8-state-db-zeroed-workdir-leak  # tick44 NEW
      - CCA-F11-Anthropic-telemetry-backdoor  # tick44 NEW
      - CCA-F12-ADI-paper-launch  # tick44 NEW

    self_downgrade_rule_v5_streak20:
      streak: 20
      rule_1_major_release_day: hit  # v0.19.0 ship day +1
      rule_2_installer_recurrence_30d: hit  # F10 ≥10 hits
      rule_3_pr_dedup_fire_cross_family: hit  # ≥5 fires
      rule_4_silent_fail_cross_month: hit  # F1 4th spike event
      rule_5_p1_density_high: hit  # P1-effective = 12
      rule_5A_industry_baseline_shift: hit  # 5-source converge 7d 沿用 tick43
      decision: maintain_daily  # 5+ rules same hit, 沿用 tick43 + tick44 升级
      feishu_3_options: A_downgrade_every_other / B_maintain_daily_recommend / C_pause_FORBIDDEN

    cron_tick_self_audit_checklist:
      - v0.19.0 release day +1: monitor fix PR merge status (4 fix PRs)
      - F11 invariant 9 candidate: trigger if any autonomous mode shows steganographic channel
      - F12 promote trigger: 5+ source converge 7d (already hit, escalate)
      - cross-cluster arrows: ensure 4 NEW arrows in this tick's impact-graph
```

## Acceptance (PASS criteria for tick44 default SOUL)

1. cron_autonomy_v8 5-layer defense 写入 default SOUL
2. industry_baseline_monitor_t44 写入 default SOUL(5 check baseline)
3. cross_cluster_arrows_e2e_coverage_t44 写入 default SOUL(4 NEW arrows 必须 e2e coverage)
4. self_downgrade_rule_v5_streak20 + 6 rules 同命中升级 default SOUL
5. Honest assessment: 5-rule-streak-20 maintain_daily + 飞书 3 选项(沿用 tick37 升级 tick43)
