# dev-agent SOUL draft — tick41 (2026-07-19)

## Addendum: family_sibling_sweep_v3 — 11 family + F12 candidate 全 sweep (tick41 升级)

**trigger**: tick41 跨 family PR-dedup fire 5 次 + F4 credential-pool-stale-snapshot 新 evidence + arxiv 2607.12406 isolation survey 与 F12 完美对齐

**11 family registry (tick41 cumulative)**:
| # | family | sweeper marker | evidence count (tick41) | lifecycle (tick41) |
|---|---|---|---|---|
| 1 | silent-fail | `sweeper:risk-silent-fail` | 6+ | stable → expansion (PR-dedup fire #58663 触发) |
| 2 | cross-platform-state | `sweeper:risk-cross-platform-state` | 3 | stable |
| 3 | memory-injection-cross-platform | `sweeper:risk-memory-injection-platform-gateway` | 3 | stable |
| 4 | credential-pool-stale-snapshot | `sweeper:risk-credential-pool-stale` | **5+2 (升级 emerging → stable)** | stable (tick41 升级) |
| 5 | cron-session-leak-closed-state | `sweeper:risk-cron-session-leak` | 3 | maintenance (closed PRs) |
| 6 | outbound-redact-call-site | `sweeper:risk-outbound-redact-call-site` | 2 | maintenance |
| 7 | MCP-supply-chain-protocol-migration | `sweeper:risk-mcp-supply-chain-6-control` | 8+ CVE | stable → expansion (CVE-2026-61459 加证) |
| 8 | cron-ticker-resilience-deck | `sweeper:risk-cron-ticker-resilience` | 9 | stable |
| 9 | session-state-integrity-deck | `sweeper:risk-session-state-integrity` | 7 (新增 #66251 #62665) | stable → expansion |
| 10 | cron-installer-handoff-state | `sweeper:risk-installer-handoff-state` | 5 | stable |
| 11 | execute-code-approval-unification-deck | `sweeper:risk-execute-code-approval-unification` | 5+ | emerging |
| **12** | **data-injection-isolation-deck (candidate)** | `sweeper:risk-data-injection-isolation` | **5+ arxiv (condition 2 met)** | **emerging (condition 2 met)** |

**F12 立卡判定 (tick41)**:
- condition 1 (≥ 5 GH issue 同 root cause): NOT MET (沿用 tick40 candidate)
- condition 2 (≥ 3 platform 同根): **MET** (Claude Code + Codex + Gemini CLI + OpenClaw per arxiv 2607.12406)
- condition 3 (修复 PR 合入但根因 broader): tick40 沿用 #60056 + #21563 + #63183
- **结论**: condition 2 met → F12 evidence threshold tick36 立卡 → 维持 candidate 但记 `condition_2_met=true`;anti-inflation (tick36) binding — F12 仍 candidate,直到 condition 1 met

**F4 invariant v2 (升级)**:
- 6 invariant (tick31) → 7 invariant (tick41 升级)
- 新增: `credential_pool_provider_match_audit` — any pool mutation MUST verify `pool.provider == agent.provider` before persist
- apply to: `recover_with_credential_pool()`, `mark_exhausted_and_rotate()`, `_refresh_entry()`, `try_activate_fallback()`

**arxiv 2607.12406 isolation survey 5 boundaries taxonomy**:
- 与 F12 data-injection-isolation-deck 完美对应:
  - user-agent boundary → ADI 防御层 1 (instruction-data decoupling)
  - agent-tool boundary → ADI 防御层 2 (tool result provenance)
  - agent-execution boundary → ADI 防御层 3 (code action containment)
  - agent-agent boundary → ADI 防御层 4 (cross-agent isolation)
  - system-environment boundary → ADI 防御层 5 (RAG / retrieval isolation)
- PlanGuard (arxiv 2604.10134) Hierarchical Verifier 模式可作 F12 defense layer 3

**F11 invariant 7 canonical_invocation_path 沿用 tick40**:
- 5 origin 必跑 dangerous_command_unified_classify (沿用 tick40)
- CVE-2026-61459 MCP Server Kubernetes 加证 — kubectl 工具 arg injection 必须由 control 9 (tool spawn static analyzer) 拦截
- control 8 (MCP server version pin) 必填 minimum version: mcp-server-kubernetes ≥ 3.9.0

**Self-downgrade v4**:
- 沿用 chief-agent 4 rule 同命中 (rule 2 + 3 + 4 + 5)
- streak 17 days
- 12 family registry binding (含 F12 candidate)

**dev 必须验证的 cross-cluster arrows (tick41)**:
| arrow | from_family | to_family | severity | tick41 evidence |
|---|---|---|---|---|
| CCA-F11-F4 (NEW) | F11 execute-code-approval | F4 credential-pool-stale | sev-B | #63425 + #25727 + F11 invariant 7 → execute_code RPC may invoke with stale pool |
| CCA-F4-F9 (NEW) | F4 credential-pool-stale | F9 session-state-integrity | sev-B | #62665 parent session model contamination may bypass pool isolation |
| CCA-F9-F4 (NEW) | F9 session-state-integrity | F4 credential-pool-stale | sev-C | #66251 auxiliary_client stale pool reuse |
| CCA-F12-F11 (沿用 tick40) | F12 candidate | F11 | sev-C | arxiv 2607.12406 isolation 5 boundaries 与 F11 invariant 7 联动 |
| CCA-CVE-F7 (NEW) | CVE-2026-61459 | F7 MCP supply chain | sev-A | control 8 version pin 必须加 mcp-server-kubernetes ≥ 3.9.0 |
