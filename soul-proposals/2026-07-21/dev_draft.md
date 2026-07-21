# SOUL Draft — dev-agent (2026-07-21, tick43)

> Self-evolution tick: hermes-researcher-deep-tick-daily / hermes-researcher-self-evolution-v1
> Author: researcher C-profile auto-evolve (no human approval)
> Target: `dev-agent` SOUL section `code_path_security_v3` (append)

## Summary

Tick43 立卡 **F11 invariant 8 = relevance gate**(沿用 tick36-42 的 7 invariant),
把 dev-agent 的 SOUL 升级纳入必须校验:

1. **tool description = 不可信指令载体** (沿用 MCP STDIO RCE, OX Mother + #67012)
2. **background_review relevance check** (沿用 #66350)
3. **keepalive expiry = real bug for proxy paths** (沿用 #67012 实证: 20s cloudflare GRU conflict)
4. **Honcho protocol guard** (沿用 #67013 = peer config schema version mismatch)

## code_path_security_v3 (extend v2 with 4 NEW invariants)

```yaml
dev:
  code_path_security_v3:
    extends: tick38 v2 (F11 6 invariant)
    new_invariants_tick43:
      - id: F11-invariant-8-relevance-gate
        name: tool_description_relevance_gate
        description: |
          任何 write_file / patch / skill_manage(patch|write_file) / cron create
          在 plan / prompt 上下文里必须含 relevance gate:
          (a) 目标 topic 与 session 实际 conversation topic 必须有 semantic match
          (b) 合规对话 → skill_review 必须 verify skill_loaded_this_session=True
          (c) 不相关 conversation content 不得写入任何 umbrella skill 任何 references/
          reference: GH #66350 (background_review unrelated write)
        verify_examples:
          - agent/background_review.py::_SKILL_REVIEW_PROMPT
          - turn_finalizer.py::_should_review_skills (新增 _skills_loaded_this_session 字段)

      - id: F11-invariant-9-tool-description-provenance
        name: tool_description_provenance
        description: |
          任何 MCP server tool description 写入 agent context 之前必须验:
          (a) tool description 不含 instruction-like content (regex whitelist)
          (b) tool description 来源 provenance 必须 traceable (server hash pin)
          (c) 连接后第一次 tool call 必须走 danger_classify pipeline
          reference: OX Security MCP STDIO RCE 2026-04-16; MCP supply-chain 6-control (tick33)

      - id: cron-invariant-keepalive-pool-fair-play
        name: keepalive_pool_fair_play
        description: |
          任何 HTTP client keepalive_expiry 设定必须 verify 与 reverse proxy 的兼容:
          (a) 已知 cloud 边缘有长 timeout (Cloudflare GRU 100-600s) 必须 keepalive > 120s
          (b) 直连 provider 短期 connections 可 keepalive 20s (沿用 #54049 / #12952 修复)
          (c) shared=True HTTP client + 多 platform 跨接 → 必须为 per-provider 单独 pool
          reference: GH #67012 (229 stream timeouts, all cf-ray=-GRU)

      - id: integration-invariant-honcho-schema-version
        name: honcho_schema_version_pin
        description: |
          任何第三方 SDK plugin (Honcho / OpenMemory / LiteLLM) 必须:
          (a) server version + client SDK version 在 startup 时 assert
          (b) 已知 schema change (`observe_others` 字段) 必须 monkeypatch 兼容或升级 SDK
          (c) 必须 fail-closed on schema mismatch
          reference: GH #67013 (Honcho PeerResponse validate error)

    retained_v2_invariants:
      - F11-invariant-1: VCS class deny list
      - F11-invariant-2: execute_code RPC per-call guard
      - F11-invariant-3: autonomous_session_flag unification
      - F11-invariant-4: tool description sanitization (extends MCP supply-chain)
      - F11-invariant-5: defense_in_depth audit_log fields
      - F11-invariant-6: pre-commit release gate
      - F11-invariant-7: canonical_invocation_path  (tick40)
```

## Acceptance (PASS criteria for tick43 dev SOUL)

1. F11 invariant 8 (relevance_gate) 实现 + write 测试
2. F11 invariant 9 (tool_description_provenance) MCP server validate pipeline 跑通
3. cron keepalive_pool_fair_play 在 #67012 路径上修 (~15 LOC httpx.Limits override)
4. Honcho schema version pin in startup
5. 所有现有 v2 6 invariant 测试仍 pass
