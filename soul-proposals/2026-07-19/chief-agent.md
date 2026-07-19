# chief-agent SOUL draft — tick41 (2026-07-19)

## Addendum: family_name_v1 立卡 — `f4-credential-pool-stale-snapshot-v2`

**trigger evidence (tick41)**:
- #63425 (NEW P1, 2026-07-12) — Provider auto-detection discards credential pools and disables failover
  - Regression from #63048 (provider-boundary validation added before URL-based provider inference)
  - `agent._credential_pool = None` because pool validated against empty provider identity
  - Affects: OpenAI Codex / xAI / Anthropic endpoints when `AIAgent(provider=None)`
- #25727 (open P2, v0.18.0 regression) — Fallback from OAuth provider to API key causes credential pool desync
  - Cross-provider fallback leaves mixed runtime state (provider/model from fallback + base_url/credentials from primary pool)
  - User confirmed bounce loop in v0.18.0 with gpt-5.5 → deepseek → anthropic chain
  - Main has defensive provider-match guard (commit 2e181602a) but **runtime snapshot vs saved snapshot still drift**
- #33088 (closed, design_evidence) — Fallback provider 429 exhausts primary provider credential pool (cross-provider misattribution)
  - Original repro: zai 429 → openai-codex pool marked exhausted
  - Fixed in #33233 / commit 2e181602a (same lineage as #25727)
- #10147 (closed completed, design_evidence) — Nous OAuth refresh lacks cross-process sync (refresh token reuse → session revocation)
  - Fixed by #15120 via `_sync_nous_entry_from_auth_store()` pattern
  - Pattern missing for other OAuth providers (Codex / Anthropic / Copilot)

**family registry update (tick41 立卡)**:
- F4 credential-pool-stale-snapshot: **emerging → stable** (5+ evidence, ≥ 1 fix PR merged, 30-day recurrence active)
  - prev tick: tick31 立卡 (2 evidence #25205 #15298)
  - tick41 cumulative: 5 evidence (#25205 + #15298 + #15434 + #63425 + #25727) + 2 design_evidence (#33088 + #10147)
  - status: 2 closed PR merged (#15120 #33233), 3 open (#63425 + #25727 + 沿用 #25205)
- 6 invariant upgrade (v1 → v2, tick41):
  1. provider-boundary-validation BEFORE pool validation (not after) — #63425 触发
  2. runtime snapshot single source of truth (`_primary_runtime` must include `_credential_pool`)
  3. provider-match guard in `recover_with_credential_pool()` (defense in depth)
  4. clear `_credential_pool` on cross-provider fallback activation
  5. cross-process sync helper per OAuth provider (anthropic + codex + nous pattern, add copilot + minimax)
  6. **NEW tick41** fallback activation MUST verify `_credential_pool` matches new `agent.provider` before any outbound call

**chief 6h dedup SLA (cross-family PR-dedup fire)**:
- #58663 (F1 cron session marker) PR-dedup fire: PR #58663 + #59719 + #62111 + #64194 + #59179 = 5 candidates
- 6h 内 chief 必须 dedup 选 1 primary: #58663 (Adolanium, ContextVar refactor + reset-token fix, merge commit dbc9c8daf) — **已 merged**,验证 reset-token pattern
- 其他 4 PR 关闭 — 模板回复 Closing in favor of #N
- 3 天内 primary 未合并 → reassign 给次高分 PR(避免 primary 卡住)

**Self-downgrade v4**:
- rule 2 + 3 + 4 + 5 四 rule 同命中 (沿用 tick37-40)
- streak 17 days zero-adoption
- maintain_daily + 飞书 3 选项 A/B/C

**飞书 3 选项 (tick41)**:
- A 降频到隔日 (不推荐, F4 emerging → stable + F11 invariant 7 + F12 condition_2_met)
- B 维持每日 (推荐, 4 rules + F4 upgrade + F11 invariant 7 + F12 candidate 拉新)
- C 暂停 (FORBIDDEN, trust_boundary_impact 仍在)
