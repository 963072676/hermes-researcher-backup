# 跨 Profile 影响图 — 2026-07-13（tick34）

## 结论

本 tick 归一化为 5 个 P1 cluster，新增第 9 family：`session-state-integrity-deck`。影响面从 session state 向 config migration、gateway readiness、artifact completeness 与 MCP protocol migration 扩散，但所有生产写入仍禁止；本仓库只保存草稿。

## 节点

- **F1** silent-fail
- **F2** cross-platform-state
- **F7** MCP-supply-chain / protocol migration
- **F9 NEW** session-state-integrity-deck
- **I1** installer-recurrence / artifact completeness
- **C1** config migration preservation
- **G1** gateway connect/reconnect readiness

## Chain 1 — F9 session state integrity

```text
GH #62365 (fabricated user intent)
 + #63008/#63018 (compaction runaway)
 + #63129/#63132/#63174 (lock fail-open)
 + #63128/#63130/#63172 (prune live work)
 + #63207/#63219 (cross-surface session finalization)
        ↓
chief SOUL: family_name_v1 + 6 invariant
        ↓
dev SOUL: state transitions fail closed
        ↓
qa SOUL: provenance/concurrency/recovery runtime gates
        ↓
pm SOUL: family registry v9 evidence contract
        ↓
default: upgrade blocked until runtime readback passes
        ↓
MCP propose M1 + skill hermes-session-state-integrity-deck
```

Marker: `sweeper:risk-session-state-integrity`。

## Chain 2 — C1 config migration preservation

```text
GH #62723 (v30→v32 drops platforms in 9/10 profiles)
        ↓
default SOUL: snapshot → offline migrate → verify → switch
        ↓
qa SOUL: all-profile key-manifest roundtrip + restore drill
        ↓
pm: acceptance requires profile/platform scope
        ↓
chief: blocks unattended upgrade
        ↓
skill hermes-config-migration-preservation-gate + MCP M2
```

Family mapping: extend F2 cross-platform-state；不另立第 10 family，因为目前是单 issue，但 blast radius 是 multi-profile。

## Chain 3 — G1 Telegram recovery finite-state

```text
GH #62047/#62098 (heartbeat reconnect prior fix)
 + #63243/#63247 (post-reconnect probe classification/dedup gap)
 + #63309 (connect attempt hangs while process looks healthy)
        ↓
dev SOUL: one recovery task + low-level connect timeout
        ↓
qa SOUL: concurrent probe failure injection + readiness triplet
        ↓
chief: silent-fail cross-month recurrence remains maintain signal
        ↓
default: PID green ≠ adapter ready
        ↓
MCP M3
```

Family mapping: extend F1 silent-fail；不新立 family。

## Chain 4 — I1 npm 12 / Desktop artifact completeness

```text
npm 12 lifecycle policy change
 + GH #62171/#62462
 + PR #61798 open (canonical production fix)
 + PR #62564 closed (artifact validation variant)
        ↓
qa SOUL: executable + stamp + native payload + Electron smoke
        ↓
default SOUL: offline package build before upgrade
        ↓
chief: canonical PR dedup / mechanism selection
        ↓
MCP M4
```

Family mapping: installer-recurrence extension；v4 self-downgrade rule 2 继续命中。

## Chain 5 — F7 MCP 2026-07-28 readiness

```text
MCP RC: final scheduled 2026-07-28
 + stateless core
 + server/discover
 + required standard headers
 + cache scope/TTL
 + issuer/resource binding
 + deprecated HTTP+SSE/roots/sampling/logging
        ↓
default SOUL: read-only dual-era readiness, no production switch
        ↓
qa SOUL: dual-era conformance matrix
        ↓
dev: bounded schema validation + header/body reject
        ↓
pm: release date + migration acceptance
        ↓
skill hermes-mcp-2026-07-28-readiness
```

Family mapping: F7 protocol-migration extension。当前不是新 P1 issue，但 final 前 15 天是高价值 readiness signal。

## 9 family registry

| # | family | marker | tick |
|---|---|---|---|
| 1 | silent-fail | `sweeper:risk-silent-fail` | 27 |
| 2 | cross-platform-state | `sweeper:risk-cross-platform-state` | 28 |
| 3 | memory-injection-cross-platform | `sweeper:risk-memory-injection-platform-gateway` | 31 |
| 4 | credential-pool-stale-snapshot | `sweeper:risk-credential-pool-stale` | 31 |
| 5 | cron-session-leak-closed-state | `sweeper:risk-cron-session-leak` | 32 |
| 6 | outbound-redact-call-site | `sweeper:risk-outbound-redact-call-site` | 32 |
| 7 | MCP-supply-chain/protocol | `sweeper:risk-mcp-supply-chain-6-control` | 32/33 |
| 8 | cron-ticker-resilience-deck | `sweeper:risk-cron-ticker-resilience` | 33 |
| **9** | **session-state-integrity-deck** | `sweeper:risk-session-state-integrity` | **34** |

## 强制依赖

1. chief 不能只选 PR，必须要求 QA runtime readback。
2. PM 的 P1 卡缺 family/evidence/invariant/ship gate/memory ID 任一项即退回。
3. Dev 的 state mutation 不能把 UNKNOWN 当 ALLOW。
4. QA 不能以 parse/build/process success 代替 config/artifact/adapter/session readback。
5. Default 保持 unattended update 红线，不改生产 config，不切 MCP modern era。
