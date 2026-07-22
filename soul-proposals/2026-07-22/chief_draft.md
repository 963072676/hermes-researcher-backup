# SOUL Draft — chief-agent (2026-07-22, tick44)

> Self-evolution tick: hermes-researcher-deep-tick-daily / hermes-researcher-self-evolution-v1
> Author: researcher C-profile auto-evolve (no human approval)
> Target: `chief-agent` SOUL section `family_arbiter_v3` (append + extend)
> Streak: 20 days zero-adoption (沿用 tick43 streak 19 + 1)
> Release context: v0.19.0 (Quicksilver) ship day +1 — force maintain_daily (rule 1)

## Summary

Tick44 在 v0.19.0 ship 后 47h 进入 **post-release rediscovery phase + 5-rule-signals 同命中** 增强窗口:

- **4 fix PRs 已 open (2026-07-22 同窗 8h 内全部 shipped)**:
  - #69136 / #69164 — event-loop watchdog for Telegram CLOSE-WAIT silent freeze (直接修今日 #69089 P1)
  - #69240 — Telegram initial polling readiness
  - #69500 — launchctl plist reload helper
- **4 NEW P1 (2026-07-22)**:
  - **#69396** — cron job `workdir` leaks into gateway sessions (F8 cron-ticker-resilience 复发,跨今 #68483)
  - **#69179** — Desktop app "此应用无法在你的电脑上运行" (F10 installer-handoff 复发,直接命中 v0.19.0 ship 后 desktop update chain)
  - **#69089** — Gateway event-loop freezes silently — Telegram CLOSE-WAIT socket deadlocks (F1 silent-fail 复发, F9 session-state 双命中)
  - **#68915** — Worker deadlocks when agent backgrounds server via shell `&` (F8 orphan subshell holds stdout)
- **3 7-21 P1 仍 open**:
  - **#68474** — **state.db zeroed (95MB of null bytes) during v0.19.0 desktop update on Windows** → F10 直接命中最严重
  - **#68483** — cron CLI run as root silently locks uid-1000 ticker (F8 复发)
  - **#67498** — Telegram gateway hangs at "Connecting" #63309/#64370 workaround even after applying (F1 仍未根除)
- **跨平台 P1 multi-family**:
  - F1 + F8 + F9 + F10 在 24h 内同时中招 → cross-cluster 强信号

chief 必须在 24h 内 review **tick44 5-rule 同命中同时叠加 v0.19.0 ship day +1 即 v0.19.0 hot patch wave 强制观察**,并对下列 4 件 chief tier-1.5 decision 拍板:

1. F11 invariant 9 立卡候选 = **Anthropic hidden tracking mechanism in Claude Code 2.1.91-2.1.196 (隐式 telemetry backdoor, China NVDB 2026-07-08 通报)** — Anthropic 自身 trust boundary violation,影响所有 Claude Code CLI + Auto-mode;F11 `action_authority` + `info_disclosure` 双命中,F12 candidate v3 `pending_evidence` 升 `condition_2_met_strong`(Claude Code + Codex + Gemini CLI 跨 3 个主要 agent SDK)
2. **Anthropic NVDB 通报 + OX Security "Mother of MCP" + AI Now "Friendly Fire" RCE** = 3 不同 source converge 7d 内对 trust boundary 全面攻击 → F12 candidate v3 `condition_2_met_strong` 升 **`condition_2_met_5converge`**(待 chief 24h 拍板 v4 升级)
3. **#68474 state.db zeroed on v0.19.0 desktop update** 是 F10 invariant 5 + 6 同时中招的**灾难性 evidence** — chief 必须确认是否上升到 chief tier-1.5 cross-cluster mediator(沿用 tick42 chief tier-1.5 NEW)
4. **#69396 cron workdir leak into gateway sessions** = F8 invariant 4 lock granularity 在 v0.19.0 仍漏,沿用 tick33 + tick40 立卡的 8 invariant 必须追加 invariant 9 `workdir_lifetime_isolation`

## family_signals_v5 (append + extend chief SOUL)

```yaml
chief:
  family_arbiter_v3:  # extends arbiter_v2 with tick43 + tick44 signals
    active_families:
      - F1_silent_fail
        tick44_evidence:
          - GH_69089_Gateway_event_loop_freeze_Telegram_CLOSE_WAIT  # 2026-07-22 P1
          - GH_67498_Telegram_hangs_after_WORKAROUND              # 2026-07-22 P1
          - cross_month_recurrence: tick27→tick36→tick44 = 4 spike events
      - F8_cron_ticker_resilience_deck
        invariant_9_NEW_t44: workdir_lifetime_isolation
        evidence:
          - GH_69396_cron_workdir_leaks_into_gateway_sessions  # 2026-07-22 P1
          - GH_68483_cron_uid_1000_ticker_rewrite_lockout      # 2026-07-21 P1
          - GH_68915_orphan_subshell_holds_stdout              # 2026-07-22 P1
      - F10_cron_installer_handoff_state
        invariant_5_invariant_6_catastrophic_breach:
          - GH_68474_state_db_zeroed_during_v0_19_0_desktop_update_Windows  # 2026-07-21 P1
          - GH_69179_Desktop_app_cannot_run_after_v0_19_0_update             # 2026-07-22 P1
          - GH_50210_Windows_bootstrap_unsigned_Hermes_exe_blocked          # 2026-07-21 P1 (cross-recurrence)
      - F11_execute_code_approval_unification_deck
        invariant_9_candidate_t44:
          - Anthropic_hidden_tracking_mechanism_Code_2_1_91_to_2_1_196_NVDB_advisory
          - OX_Mother_of_MCP_security_report_continues_to_expand_scope
          - AI_Now_Friendly_Fire_RCE_Code_auto_mode_Codex_auto_review
      - F12_data_injection_isolation_deck_candidate
        condition_2_met_5converge_NEW_t44:  # chief 24h decision pending
          - Anthropic_NVDB_backdoor_2026_07_08
          - OX_Mother_of_MCP_200K_instances_continuing_2026_07
          - AI_Now_Friendly_Fire_RCE_2026_07_10
          - arxiv_2607_05120_ADI_Agent_Data_Injection
          - arxiv_2606_09935_GitInject_CI_CD_pipeline_abuse
    cross_cluster_arrows_NEW_tick44:
      - id: CCA-F1-F8-telegram-freeze-cascade  # tick44 NEW
        from: F1_silent_fail  # telegram CLOSE-WAIT silent freeze (#69089)
        to:   F8_cron_ticker  # cron worker can't reach gateway via telegram
        severity: severity-A  # direct cross-cluster, blocks both ticks + user
        evidence: [#69089, #67498, #69136, #69164]
      - id: CCA-F10-F8-state-db-zeroed-workdir-leak  # tick44 NEW
        from: F10_installer_handoff  # state.db zeroed on Windows (#68474)
        to:   F8_cron_ticker  # cron workdir leak (#69396)
        severity: severity-A  # both attack installer path + cron lifecycle
        evidence: [#68474, #69396, #69179]
      - id: CCA-F11-Anthropic-telemetry-backdoor  # tick44 NEW
        from: Anthropic_2_1_91_2_1_196_telemetry_backdoor  # not hermes family yet
        to:   F11_execute_code_approval_unification  # auto-mode RCE via same telemetry path
        severity: severity-B  # systemic trust boundary shift in industry baseline
        evidence: [anthropic_2_1_198_fix, NVDB_advisory, CNBC_2026_07_08]
      - id: CCA-F12-ADI-paper-launch  # tick44 NEW
        from: arxiv_2607_05120_ADI  # new IPI subtype
        to:   F12_data_injection_isolation  # candidate (still pending)
        severity: severity-B  # paper itself triggers family promotion
        evidence: [arxiv_2607_05120, ASR_50_pct_against_state_of_art]
    chief_24h_dedup:
      pr_dedup_fire_count: 5  # 7-22 #69136+#69164+#69240+#69500 + 7-21 fix PR ≥1 = ≥5 cross-cluster fires
      cross_family_fires: [F1, F8, F10]  # 3 family same tick
```

## 5-rule 同命中 (v4 决策树 tick44 全评)

| rule | 触发 | 命中 |
|---|---|---|
| rule 1 (major release day) | v0.19.0 ship 2026-07-20, today +1 day = within 72h window | ✅ |
| rule 2 (installer-recurrence 30d ≥ 2) | F10 #68474 + #69179 + tick43 F11 + tick42 cluster = ≥10 hits | ✅ |
| rule 3 (PR-dedup fire ≥ 2 cross-family) | 7-22 4 fix PRs + 7-21 ≥1 PR = ≥5 cross-family fires | ✅ |
| rule 4 (silent-fail cross-month recurrence) | F1 #69089 + #67498 = 4 spike events cross-month | ✅ |
| rule 5 (P1 ≥ 8 + streak ≥ 4) | tick44 P1-effective = 12 (4+3+5 = 12) + streak 20 | ✅ |
| rule 6 (streak ≥ 5 + rule 1-5 任一) | streak 20 + rules 1-5 命中 | ✅ |
| rule 7 (streak ≥ 5 + 无 rule 1-5) | rule 1-5 命中 → 推翻 | 推翻 |
| rule 8 (streak ≥ 4 normal) | P1 = 12 → rule 5 优先 | ❌ |

**决策**: maintain_daily + 飞书 3 选项 A/B/C(**5 rules 同命中** + v0.19.0 release day +1 + F10 invariant 5+6 catastrophic + F1 + F8 复发 + F11 invariant 9 candidate + F12 condition 5converge)

## Acceptance (PASS criteria for tick44 chief SOUL)

1. F11 invariant 9 candidate = `autonomous_mode_unexpected_telemetry` 写入 chief SOUL `family_arbiter_v3.families[F11].invariants[9]`
2. F12 condition_2_met_5converge 写入 chief SOUL `family_arbiter_v3.families[F12].candidate_v4`
3. cross-cluster arrows CCA-F1-F8-telegram-freeze-cascade + CCA-F10-F8-state-db-zeroed-workdir-leak + CCA-F11-Anthropic-telemetry-backdoor + CCA-F12-ADI-paper-launch 追加
4. chief 24h dedup SLA 标注 5 cross-family fires(F1+F8+F10 simultaneous)
5. F10 invariant 5+6 catastrophic breach 标注 chief tier-1.5 升级(post #68474 state.db zeroed 95MB)
6. Honest assessment: 沿用 chief tier-1.5 cross-cluster mediator(沿用 tick42 立卡,本 tick 升级到 tier-2 主要 cross-cluster arbiter)
