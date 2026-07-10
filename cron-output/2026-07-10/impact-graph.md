# Cross-profile 影响图 (2026-07-10 tick32)

> hermes-researcher-deep-tick-daily tick32
> 4 P1 cluster 跨 5 profile 影响图

## signal 来源

| source | cluster | PR | label | 影响 profile |
|---|---|---|---|---|
| GH #23810 | gateway outbound redact call-site 5+ token leak | #23821/#23822 open | P1 security | chief + qa + default + **all 4 platform profiles (telegram/discord/slack/feishu bots runtime)** |
| GH #24996 | fallback chain `_try_activate_fallback` host memory exhaustion | #24998/#25059/#53909 open | P1 | dev + all 5 profiles (provider chain) |
| GH #41935 + #12029 + #1416 | cron session leak (no_agent branch + cross-source) | #41969/#44087/#21031 open | P1 | pm + **all 5 profile cron workers** + dev (session DB) |

## 跨 profile 影响矩阵

```
                  chief  pm  dev  qa  default  cron_workers
#23810 redact       ●    -   -   ●     ●           ●  (gateway)
#24996 circuit      -    -   ●    -    -           ●  (provider chain)
#41935 session     ●    ●   ●    -    -           ●  (state.db)

                     ┃    ┃    ┃    ┃    ┃    ┃
                     ┃    ┃    ┃    ┃    ┃    ┃
                     ▼    ▼    ▼    ▼    ▼    ▼

PR dedup SLA     6h   -    -   -    -    6h  (cross-tick auto-trigger)
Invariant audit  -   6h   6h  ship    6h     -
Ship gate        -    -    -   0    -        -
```

## 跨 profile 依赖链

### Chain 1: #23810 outbound redact cluster

```
chief (6h dedup + cross-call-site audit order)
   ↓ delegates
default profile SOUL §3.5 update (5 platform baseline)
   ↓ requires
qa SOUL §5.3 update (release verification v2: add cross-platform-redact-audit.sh)
   ↓ requires
new skill: hermes-cross-platform-redact-call-site-audit
   ↓ produces
scripts/cross-platform-redact-audit.py — must exit 0 before v0.19.0 ship
```

**trigger order**:
1. Chief 6h SLA: select primary PR between `#23821` / `#23822` (both 60+ day open)
2. Default profile: `security.redact_outbound_chat: true` config baseline
3. QA: ship gate `cross-platform-redact-audit.sh` in 4-functional-test baseline
4. Skill `hermes-cross-platform-redact-call-site-audit` published

### Chain 2: #41935 cron session leak cluster

```
pm (new family 立卡 cron-session-leak-closed-state)
   ↓ requires
dev (centralize `_finalize_cron_session()` helper)
   ↓ requires
qa (release functional test `tests/cron/test_cron_no_agent_session_close.py`)
   ↓ requires
new skill: hermes-cron-session-leak-guard
   ↓ produces
all 5 profile cron workers must adopt invariant (沿用 tick28 cross-profile verify)
```

**trigger order**:
1. PM family 立卡 + silent-fail acceptance (extend 4 必填 fix 段)
2. Dev: PR #41969 (canonical earliest) + close #44087 / #21031 dedup
3. QA: ship gate add 4-functional-test baseline
4. Skill: `hermes-cron-session-leak-guard` published

### Chain 3: #24996 fallback circuit-breaker

```
dev (centralize `_fallback_circuit_breaker` helper)
   ↓ requires
qa (release functional test `tests/agent/test_fallback_circuit_breaker.py`)
   ↓ requires
new skill: hermes-fallback-circuit-breaker-invariants
   ↓ produces
all provider-using profiles (dev / qa / default — researcher + chief fall through)
```

**trigger order**:
1. Dev: PR dedup 6h SLA `#24998` / `#25059` / `#53909` (teknium1 自己 PR #53909 是
   canonical most-explicit)
2. QA: ship gate add circuit-breaker test
3. Skill: `hermes-fallback-circuit-breaker-invariants` published

## Family 立卡

**新立卡 (tick32)**:
- **`cron-session-leak-closed-state`** (#41935 + #12029 + #1416)
- sweeper marker: `sweeper:risk-cron-session-leak`

**升级 (tick32 立卡)**:
- **`gateway-outbound-redact-call-site`** (#23810) — new local family to
  extend existing silent-fail architecture escalation
- sweeper marker: `sweeper:risk-outbound-redact-call-site`

**Existing family confirm** (tick32):
- **MCP supply chain 5-control** — Microsoft + OWASP + TrueFoundry + Tencent
  converge. Extend tick28 `hermes-mcp-self-approval-baseline` skill.
- sweeper marker: `sweeper:risk-mcp-supply-chain-5-control`

## 跨 family 共同根因

3 family 共同点: **terminal-state cleanup 分散多处**,没有 centralized invariant。

回推根因: 历史上 Hermes 演化过程,不同 contributor 加 exit-path handling 时,
各自只管自己那个 case,没 funnel 设计。

**fix 范式**: 每 family fix 必加 centralized funnel helper + decorator / finally
block + 最终 single call (`_finalize_*()` / `redact_sensitive_text()` /
`_fallback_breaker.allow()`) 是 deterministic single-source-of-truth。

## 影响范围优先级

| priority | profile | action |
|---|---|---|
| P0 | (none — 0 P0) | - |
| P1 | chief | 2 PR dedup SLA (#23810 + secondary chains) |
| P1 | pm | family 立卡 + acceptance expansion (cron session leak) |
| P1 | dev | 2 dedup PR (circuit-breaker + cron session close) |
| P1 | qa | release verification v2 (4 functional test baseline) |
| P1 | default | MCP supply chain 5-control baseline upgrade |
| (impact) | all cron workers (5 profile) | adopt session close invariant post-ship |
| (impact) | all platform adapters (telegram/discord/slack/feishu/whatsapp) | adopt outbound redact call post-ship |

## 结论

- **chief 6h PR-dedup SLA 应用数量**: 2 (outbound redact + dev fallback dedup indirectly)
- **新立卡 family**: 2 (cron-session-leak + outbound-redact-extended)
- **新立卡 sweeper marker**: 3 (risk-cron-session-leak + risk-outbound-redact-call-site + risk-mcp-supply-chain-5-control)
- **新 SOUL 草稿**: 5 (1 chief + 1 pm + 1 dev + 1 qa + 1 default)
- **新 skill 草稿**: 3 (redact-audit + circuit-breaker + session-leak-guard)
- **跨 profile 依赖链**: 3 (redact / session-leak / circuit-breaker)
