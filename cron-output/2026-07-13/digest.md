# Researcher Deep Tick 34 — 2026-07-13

## 摘要

- P0: 0
- Consolidated P1: 5
- NEW family: `session-state-integrity-deck`（registry 8 → 9）
- Hermes release: latest v0.18.2，local v0.18.0，main ahead 1094 commits
- Adoption: 0/8 yesterday，10-day zero-adoption streak
- Decision: self-downgrade v4 rule 2+3+4 hit → maintain daily

## Top signals

1. Session integrity P1 chain: #62365 #63008 #63128 #63129 #63207，fix PRs open。
2. Multi-profile config migration data loss: #62723。
3. Telegram reconnect/startup readiness gaps: #63243/#63247 + #63309。
4. npm 12 Desktop native artifact gap: #62171/#61798，canonical fix still open。
5. MCP 2026-07-28 final approaches in 15 days；read-only dual-era readiness required。

## Status corrections

- #62151/#62198 are closed; move from open risk to release verification.
- #60683 MiniMax stream, #60350 env spill, #62212 MCP keepalive, #60685 update downgrade remain open P2.

## Deliverables

- `soul-proposals/2026-07-13/` — 5
- `skill-proposals/2026-07-13/` — 3
- `cron-output/2026-07-13/impact-graph.md`
- `docs/audit/2026-07-13.md`

## Source links

- https://github.com/NousResearch/hermes-agent/issues/62365
- https://github.com/NousResearch/hermes-agent/issues/63008
- https://github.com/NousResearch/hermes-agent/issues/63128
- https://github.com/NousResearch/hermes-agent/issues/63129
- https://github.com/NousResearch/hermes-agent/issues/63207
- https://github.com/NousResearch/hermes-agent/issues/62723
- https://github.com/NousResearch/hermes-agent/issues/63243
- https://github.com/NousResearch/hermes-agent/issues/63309
- https://github.com/NousResearch/hermes-agent/pull/61798
- https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/
- https://modelcontextprotocol.io/specification/draft/changelog
