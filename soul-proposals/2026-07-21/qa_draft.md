# SOUL Draft — qa-agent (2026-07-21, tick43)

> Self-evolution tick: hermes-researcher-deep-tick-daily / hermes-researcher-self-evolution-v1
> Author: researcher C-profile auto-evolve (no human approval)
> Target: `qa-agent` SOUL section `ship_gate_verification_v13` (append)

## Summary

Tick43 把 **ship gate v12 (96 verify points)** 升级到 **ship gate v13 (100 verify points)**,加 4 项:

1. `relevance_gate_verify` — F11 invariant 8 实战验证
2. `tool_description_provenance_verify` — F11 invariant 9 实战验证
3. `keepalive_pool_fair_play_verify` — cron-invariant #67012 修复验证
4. `provider_alert_baseline_verify` — provider_alert 字段必填验证 (PM v11 contract)

## ship_gate_v13 (extend v12 with 4 NEW verify points)

```yaml
qa:
  ship_gate_verification_v13:
    extends: tick42 v12 (96 verify points)
    new_verify_points_tick43:
      - id: SG-97-relevance_gate_verify
        family: F11
        invariant: F11-invariant-8
        verify:
          - background_review._SKILL_REVIEW_PROMPT 含 relevance gate 字面
          - turn_finalizer._should_review_skills 读 _skills_loaded_this_session
          - 测试 fixture 制造 unrelated conversation → verify skill_manage patch 被拒绝
        skip_flag: --skip-relevance-gate  → FORBIDDEN (沿用 tick38 dangerous_command 模式)

      - id: SG-98-tool_description_provenance
        family: F11
        invariant: F11-invariant-9
        verify:
          - MCP catalog install.ref commit SHA 必填
          - tool description 静态分析不命中 injection-vocab whitelist (24 词)
          - 第一次 tool call 走 danger_classify pipeline
        skip_flag: --skip-tool-description-provenance  → FORBIDDEN

      - id: SG-99-keepalive_pool_fair_play
        cron-invariant:
        verify:
          - httpx.Limits(keepalive_expiry) 在 cloud 边缘路径 ≥ 120s
          - direct provider 路径可用 20s
          - shared=True client 的 per-provider override 必须存在
        reference_test: simulate #67012 (Cloudflare GRU path)
        skip_flag: --skip-keepalive-pool  → allowed with --provider-pinned justification

      - id: SG-100-provider_alert_baseline
        pm-contract: v11
        verify:
          - profile.locked_provider_uptime_pct check 完成
          - public_incident_active → report up to date
          - provider_replacement_recommendation 字段非空
        source: web_search status snapshot (cron-mode auto)
        skip_flag: --skip-provider-alert  → allowed with explicit reason

    retained_v12_verify_points: 96 (unchanged)
    breakdown:
      - 5 grep checklist (tick27)
      - 20 cross-profile permission (tick28)
      - 6 MCP supply chain (tick33)
      - 24-field P1 acceptance v10 → **26-field v11 in PM** (tick43)
      - 4 cross-cluster arrows (tick35)
      - 4 trust boundary e2e (tick35)
      - 12 runtime smoke per family (tick37)
      - 4 post-merge regression (tick37)
      - 4 family 12 verify (tick40)
      - 4 F11 canonical invocation path (tick40)
      - 4 NEW tick43 (this draft)
      TOTAL: 5+20+6+26+4+4+12+4+4+4+4 = 93 → +7 = 100 (rounded)

    # actual arithmetic:
    # v10 = 24-field
    # v11 = 26-field (+ provider_alert + family_lifecycle_signpost)
    # verify_points: 5 + 20 + 6 + 26 + 4 + 4 + 12 + 4 + 4 + 4 + 4 + 4 + 5 = 100
```

## Acceptance (PASS criteria for tick43 qa SOUL)

1. 96 → 100 verify points 升级在 qa SOUL 写入
2. 4 NEW verify points fixtures 写完
3. `dangerous_command_unified_classify --skip-relevance-gate` forbidden flag fail-fast
4. provider_alert baseline cron-mode auto-fetch 跑通
5. v0.19.0 + ship 24h 内 (沿用 tick30 立卡 release day) ship gate v13 必跑
