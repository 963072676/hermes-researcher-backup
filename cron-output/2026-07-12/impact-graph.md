# 跨 profile 影响图 — 2026-07-12 (tick33)

> Tick33 cron-output/2026-07-12/impact-graph.md
> Author: researcher profile
> 5 SOUL 草稿 + 3 skill 草稿 跨 profile 依赖链

## 节点 (8 family registry + 5 SOUL + 3 skill + 4 MCP memory)

```
8 families (ticker=本 tick 立卡 cron-ticker-resilience-deck):
  F1= silent-fail                  [tick27]
  F2= cross-platform-state         [tick28]
  F3= memory-injection-cross-platform [tick31]
  F4= credential-pool-stale-snapshot [tick31]
  F5= cron-session-leak-closed-state [tick32]
  F6= outbound-redact-call-site    [tick32]
  F7= MCP-supply-chain-5-control   [tick32]
  F8= cron-ticker-resilience-deck  [tick33 NEW]

5 profiles:
  P_chief   = chief-agent (cross-team dedup + escalate)
  P_pm      = product-manager (family registry + acceptance)
  P_dev     = dev (PR dedup + 4 验收清单)
  P_qa      = qa (release gate + ship verification)
  P_default = default (config baseline + cross-profile verify)

3 skill drafts:
  S1= hermes-cron-ticker-resilience-deck  [tick33]
  S2= hermes-mcp-supply-chain-6-control  [tick33]
  S3= hermes-family-registry-v8          [tick33]

4 MCP memories:
  M1= 77fe080a (cron-ticker-resilience-deck 立卡)
  M2= 5f36d52b (MCP supply chain 6-control)
  M3= af81023e (silent-fail cron gateway still open)
  M4= b868be0c (family registry v8)
```

## 依赖链 (5 chain)

### Chain 1: cron-ticker-resilience-deck 跨 profile 链

```
F8 (cron-ticker-resilience-deck)
  ↓ triggers
P_chief SOUL (新增 6 invariant 段)
  ↓ requires
S1 (hermes-cron-ticker-resilience-deck) 提供 6 invariant 实现细节
  ↓ enforces
P_qa SOUL (新增 release verification v3 第 6 项: cron ticker 6 invariant 在 ship 前跑)
  ↓ enforces
P_default SOUL (新增 ticker_heartbeat atomic write baseline)
  ↓ outputs
M1 (77fe080a 立卡 memory) — 进入 review queue
```

**关键依赖**:P_chief → S1 → P_qa + P_default。**任一段缺失,family 立卡不完整**。

### Chain 2: MCP supply chain 6-control 跨 profile 链

```
F7 (MCP-supply-chain-5-control) → 升级
F7+1 (MCP-supply-chain-6-control)
  ↓ requires
S2 (hermes-mcp-supply-chain-6-control) — 新增 tirith pipe scan (5th→6th control)
  ↓ enforces
P_default SOUL (新增 6-control baseline 段) — config write + runtime startup 双重 check
  ↓ enforces
P_qa SOUL (新增 release verification v3 第 6 项) — 6-control scan 在 ship 前跑
  ↓ outputs
M2 (5f36d52b 立卡 memory) — 进入 review queue
```

**关键依赖**:F7 → F7+1 (升级路径)。**升级路径必须明确,避免 family 名漂移**。

### Chain 3: silent-fail cron gateway still open 跨 profile 链

```
F1 (silent-fail) 持续 open (v0.18.2 patch wave 仍未根治)
  ↓ requires
P_dev SOUL (新增 silent-fail cron gateway v2 段) — 4 验收清单
  ↓ enforces
P_qa SOUL (新增 release verification v3 第 4 silent-fail scenarios)
  ↓ requires
P_default SOUL (silent_drop_total counter baseline)
  ↓ outputs
M3 (af81023e 立卡 memory) — 进入 review queue
```

**关键依赖**:F1 复发 → P_dev → P_qa + P_default。**v0.18.2 ship 后 4 天仍未根治,family 立卡升级**。

### Chain 4: family registry v8 跨 profile 链

```
F1-F8 (8 family registry)
  ↓ requires
S3 (hermes-family-registry-v8) — 6 验收清单 + 自动 lint
  ↓ enforces
P_pm SOUL (新增 family registry v8 段) — 8 family 命名 + sweeper marker
  ↓ enforces
P_chief SOUL (6h dedup SLA 走 family registry 决策)
  ↓ outputs
M4 (b868be0c 立卡 memory) — 进入 review queue
```

**关键依赖**:F1-F8 → S3 → P_pm + P_chief。**family naming 漂移必须经 S3 lint 拦住**。

### Chain 5: release verification v3 跨 profile 链 (聚合 chain 1-3)

```
P_qa SOUL (新增 release verification v3 段)
  ↓ enforces
6 grep checklist (5 → 6 升级) + 4 silent-fail scenarios
  ↓ requires
P_default SOUL (cross-profile verify baseline 沿用 tick28)
  ↓ requires
P_dev SOUL (4 验收清单 silent-fail scenarios 实现)
  ↓ requires
P_chief SOUL (chief 6h dedup SLA for PR dedup)
  ↓ requires
P_pm SOUL (family registry v8 决策)
```

**关键依赖**:P_qa 是聚合点。**任一段缺失,ship gate 不完整**。

## 跨 profile 决策树

```
新 P1 cluster 出现
  ↓
判断 family (沿用 S3 hermes-family-registry-v8)
  ├─ 已存在 family → 走现有 family 处理 (PR dedup / 立卡升级)
  │   ├─ chief 6h dedup SLA (PR ≥ 3 同 root cause → 走 tick27 PR dedup)
  │   ├─ dev 4 验收清单 (silent-fail scenarios)
  │   └─ qa release verification v3 (6 grep + 4 scenario)
  │
  └─ 新 family → 立卡
      ├─ 命名 3 段式 (<root-cause>-<scope>[-<modifier>])
      ├─ sweeper marker (sweeper:risk-<root-cause>-<scope>)
      ├─ 6 验收清单 (sweeper marker + SOUL + skill + MCP memory + impact-graph + audit)
      └─ pm + chief 共同 review
```

## 优先级汇总

| Priority | family | 触发 | 影响范围 |
|---|---|---|---|
| P1 | cron-ticker-resilience-deck (F8) | 9 GH issues 1 family | 本 cron worker 直接高优级 |
| P1 | MCP-supply-chain-6-control (F7+1) | 6 source converge | 所有 Hermes 用户 |
| P1 | silent-fail cron gateway still open (F1 升级) | v0.18.2 patch wave 仍未根治 | 本 cron worker 日终汇总可靠性 |
| P1 | release verification v3 | 5 → 6 grep + 4 silent-fail scenario | release ship gate |
| P2 | family registry v8 (F1-F8) | 8 family 累计 + 立卡机制 | research foundation |

## 配套 audit

- 5 SOUL 草稿: `soul-proposals/2026-07-12/SOUL_*.md`
- 3 skill 草稿: `skill-proposals/2026-07-12/hermes-*.md`
- 4 MCP memory_ids: 77fe080a / 5f36d52b / af81023e / b868be0c
- audit log: `docs/audit/2026-07-12.md`
- 备份 commit: 待 tick33 push (cba4ac7 之上)