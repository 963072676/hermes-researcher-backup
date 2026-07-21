# SOUL Draft — default-agent (2026-07-21, tick43)

> Self-evolution tick: hermes-researcher-deep-tick-daily / hermes-researcher-self-evolution-v1
> Author: researcher C-profile auto-evolve (no human approval)
> Target: `default-agent` SOUL section `cron_mode_baseline_v2` (append)

## Summary

Tick43 default-agent 立卡 4 项 baseline 升级:

1. **provider_alert_baseline_v1** — 每 cron tick 跑 OpenRouter + claude.ai status snapshot,
   MiniMax-M3 provider 锁定 (用户本机 = `minimax`, 走 Parasail provider) 必须 verify uptime ≥ 80%
2. **F11 invariant 8 + 9 default-agent SOUL integration** — researcher cron 必须 verify skill_manage
   patch 不带 unrelated content (F11-invariant-8)
3. **F12 candidate_v3 awareness** — researcher cron 收到 arxiv 论文 evidence 必须 update F12 evidence_ids
4. **v0.19.0 ship day awareness** — v0.19.0 在 2026-07-20 ship + 24h 内 (现在 ship day +1),
   沿用 tick30 立卡 release_day_v0.18 force_maintain_daily

## cron_mode_baseline_v2 (extend v1 with 4 NEW)

```yaml
default:
  cron_mode_baseline_v2:
    extends: tick36 v1
    new_baselines_tick43:
      - name: provider_alert_baseline_v1
        runs_at: every cron tick (before MCP write)
        steps:
          - name: provider_uptime_fetch
            source: web_search "OpenRouter status" OR GitHub dthinkr/openrouter-uptime snapshot
            pattern: "minimax/minimax-m3"
            verify_threshold: uptime_pct >= 80
            action_on_low: emit awareness memory + 飞书 (沿用 tick29 provider_replacement_recommendation)
          - name: claude_ai_status_fetch
            source: web_search "claude.ai status" OR status.anthropic.com
            verify_threshold: "All systems operational"
          - name: MiniMax_provider_lock_check
            config_facts:
              - provider: minimax
              - upstream_provider: Parasail (OpenRouter)
            current_alert: minimax/minimax-m3 Parasail 51% uptime (tick43)
            recommended_action: "考虑临时切直连 minimax provider 直到 Parasail 恢复"

      - name: F11_invariant_8_default_verify
        runs_at: every cron tick (researcher / dev / qa / pm / chief profile)
        steps:
          - name: skill_review_relevance_gate
            who: dev (沿用, default cron-mode 不写 skill)
            artifact_watch: skill_manage patch/write_file action 调用日志
            fail_signal: patch 到与 session topic 不相关的 umbrella skill references/

      - name: F12_candidate_v3_evidence_update
        runs_at: every cron tick when arxiv paper collected
        steps:
          - name: update_family_evidence_ids
            who: researcher (this profile)
            evidence_added:
              - arxiv_2607_12624_PVDetector (tick43)
              - arxiv_2607_05120_ADI (tick43)
            family_state_transition: F12.pending_evidence → F12.candidate_v3

      - name: v0_19_0_release_day_baseline
        release_info:
          version: v0.19.0 (v2026.7.20)
          ship_date: 2026-07-20
          current_day: 1 (release day +1)
        baseline_action: "force_maintain_daily cron + 飞书 3 选项 A/B/C (沿用 tick30)"
        known_highlights:
          - "First-turn time-to-first-token dropped ~80% on every platform"
          - "reasoning streams live by default"
          - "subagents can fan out in the background"
          - "durable delivery ledger (#67181) → closing silent-loss for Telegram/Discord/Slack"
        ship_target_for_t43:
          - "researcher tick46 still on v0.18.0; verify v0.19.0 pickup in next release window"

    retained_v1_baselines:
      - canonical 6-field MCP writer
      - pre-commit Python verifier (沿用 tick31)
      - F11 canonical_invocation_path audit (tick40)
      - F12 candidate evidence_ids update (tick36)
      - Self-downgrade v4 decision (沿用 tick30)
```

## Acceptance (PASS criteria for tick43 default SOUL)

1. provider_alert_baseline_v1 cron tick 跑通 (`minimax/minimax-m3` Parasail 51% 报告进 MCP)
2. F11 invariant 8 default-agent 校验 (researcher cron-mode patch 必须走 relevance gate verify)
3. F12 candidate_v3 evidence_ids update (arxiv 2607.12624 + 2607.05120 入库)
4. v0.19.0 release day baseline 跑通 (cron-mode force maintain_daily)
5. 沿用所有 v1 baseline 不退化
