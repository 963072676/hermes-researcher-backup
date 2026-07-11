---
name: hermes-family-registry-v8
description: '8-family registry lint + sweeper marker 命名约定 + 自动扫 SOUL 草稿 family name 一致性。Use when: SOUL 草稿 commit 前 / family 立卡触发判定 / family naming convention 校验 / chief 6h dedup SLA 决策。'
version: 1.0.0
author: Hermes Agent (researcher profile)
license: MIT
created_by: agent
platforms: [linux, macos]
metadata:
  hermes:
    tags: [family-registry, lint, naming-convention, sweeper-marker, cross-month-recurrence]
    related: [hermes-researcher-self-evolution-v1, hermes-cron-ticker-resilience-deck]
    立卡: tick33
---

# hermes-family-registry-v8

> Tick33 (2026-07-12) 立卡。沿用 tick27 + tick28 + tick31 + tick32 + tick33 family 立卡机制,累计 8 family。

## 这个 skill 解决什么

researcher profile 累计立卡 8 family,每个 family 有独立 sweeper marker + 命名约定 + 立卡触发条件。手动管理易出错:
- family name 不一致 (silent-fail vs silent-fail-cron-gateway)
- sweeper marker 命名不规范 (sweeper:risk- vs sweeper:marker-)
- SOUL 草稿 family name 与 family registry 不匹配
- 新立卡 family 没有走 6 验收清单

**单点 lint 不够**,必须 6 验收清单 + 自动 lint + sweep marker 校验。

## 何时调用

- SOUL 草稿 commit 前 (默认 lint 通过)
- family 立卡触发判定 (P1 cluster → family 名 → sweeper marker → 6 验收清单)
- chief 6h dedup SLA 决策 (PR ≥ 3 同 family → 走 family registry)
- researcher self-evolution tick 调参 (沿用 tick27/tick32 streak 决策)

## 当前 8 family registry

| # | family name | sweeper marker | 立卡 tick |
|---|---|---|---|
| 1 | silent-fail | `sweeper:risk-silent-fail` | tick27 |
| 2 | cross-platform-state | `sweeper:risk-cross-platform-state` | tick28 |
| 3 | memory-injection-cross-platform | `sweeper:risk-memory-injection-platform-gateway` | tick31 |
| 4 | credential-pool-stale-snapshot | `sweeper:risk-credential-pool-stale` | tick31 |
| 5 | cron-session-leak-closed-state | `sweeper:risk-cron-session-leak` | tick32 |
| 6 | outbound-redact-call-site | `sweeper:risk-outbound-redact-call-site` | tick32 |
| 7 | MCP-supply-chain-5-control | `sweeper:risk-mcp-supply-chain-5-control` | tick32 |
| **8** | **cron-ticker-resilience-deck** | `sweeper:risk-cron-ticker-resilience` | **tick33** |

## 命名约定 (沿用 tick31 立卡)

### family name 命名 (3 段式)

```
<root-cause>-<affected-scope>[-<modifier>]
```

**示例**:
- `silent-fail` (root cause: silent fail)
- `cross-platform-state` (root cause: cross platform, scope: state)
- `memory-injection-cross-platform` (root cause: memory injection, scope: cross platform)
- `cron-ticker-resilience-deck` (root cause: cron ticker, scope: resilience, modifier: deck)

### sweeper marker 命名 (3 段式)

```
sweeper:risk-<root-cause>-<affected-scope>
```

**示例**:
- `sweeper:risk-silent-fail`
- `sweeper:risk-cross-platform-state`
- `sweeper:risk-memory-injection-platform-gateway`

### family 立卡触发条件

| 条件 | 触发立卡类型 | 命名示例 |
|---|---|---|
| 跨 ≥ 2 platform label 同时中招 | cross-platform family | `cross-platform-state` |
| 同一 root cause 不同 issue 跨 ≥ 60 天仍 open | 架构性问题 family | `silent-fail` (3 周 4 次复发) |
| 同 code path 不同 fix PR 抢修 ≥ 3 PR | naming 应反映 code path | `cron-ticker-resilience-deck` (9 issues 1 family) |
| 跨 ≥ 2 source 在 7 天内 converge | 协议级 family | `MCP-supply-chain-5-control` (5 source 7d) |

### 命名禁止

- 编号式命名 (family-1 / family-2 ❌)
- 模糊词 (general / misc / bug ❌)
- 单 issue 命名 (#12345 ❌ — family 应跨 issue)
- 4+ 段命名 (modifier 应合并到 scope,不另起段)

## 自动 lint 工具

### 1. family name lint

```bash
# scripts/lint-family-name.sh
SOUL_FILE="$1"

# 禁止命名 pattern
grep -E "family-[0-9]+" "$SOUL_FILE" && { echo "FAIL: family-N命名"; exit 1; }
grep -E "(general|misc|bug)-family" "$SOUL_FILE" && { echo "FAIL: 模糊词"; exit 1; }
grep -E "#[0-9]{4,5}-family" "$SOUL_FILE" && { echo "FAIL: 单 issue 命名"; exit 1; }

# 必填 pattern — 引用 family registry
grep -E "family_name_v[0-9]+" "$SOUL_FILE" || { echo "FAIL: 缺 family_name_v1 标识"; exit 1; }

echo "PASS"
```

### 2. sweeper marker lint

```bash
# scripts/lint-sweeper-marker.sh
SOUL_FILE="$1"

# 提取所有 sweeper marker 引用
sweepers=$(grep -oE "sweeper:risk-[a-z-]+" "$SOUL_FILE" | sort -u)

# 校验每个 marker 在 family registry
for sw in $sweepers; do
    case "$sw" in
        "sweeper:risk-silent-fail") ;;
        "sweeper:risk-cross-platform-state") ;;
        "sweeper:risk-memory-injection-platform-gateway") ;;
        "sweeper:risk-credential-pool-stale") ;;
        "sweeper:risk-cron-session-leak") ;;
        "sweeper:risk-outbound-redact-call-site") ;;
        "sweeper:risk-mcp-supply-chain-5-control") ;;
        "sweeper:risk-mcp-supply-chain-6-control") ;;
        "sweeper:risk-cron-ticker-resilience") ;;
        *) echo "WARN: unknown sweeper marker '$sw' — need registry update"; ;;
    esac
done
```

### 3. SOUL 草稿 family name 与 registry 一致性

```bash
# scripts/lint-soul-family-match.sh
SOUL_FILE="$1"
EXPECTED_FAMILY="$2"  # from filename: SOUL_chief_draft_cron_ticker_resilience_deck.md → cron-ticker-resilience-deck

# 校验 SOUL 草稿中 family name 必须包含 expected
grep -q "$EXPECTED_FAMILY" "$SOUL_FILE" || { echo "FAIL: SOUL missing family name '$EXPECTED_FAMILY'"; exit 1; }

echo "PASS"
```

## 立卡验收清单 (6 项全过才允许登记)

- [ ] **1. sweeper marker 命名** — `sweeper:risk-<root-cause>-<scope>` 3 段式 + 在 8 family registry 列表
- [ ] **2. SOUL 草稿 chief-agent 段加 `family_name_v1` 立卡段落**
- [ ] **3. 至少 1 个 skill 草稿覆盖防御** (silent-fail → hermes-cron-ticker-resilience-deck)
- [ ] **4. MCP propose_write 写 1 条 family 立卡 memory** (memory_id 已记录)
- [ ] **5. impact-graph 标 family 依赖链** (哪个 family 依赖哪个 family)
- [ ] **6. audit log 写 family 累计 cross-month 复发率** (沿用 tick27 silent-fail 复发率)

## 跨 profile 影响图 (family 依赖链)

```
default SOUL ─┐
              ├──→ MCP-supply-chain-6-control ──→ default config mcp_servers check
              │
chief SOUL ───┼──→ cron-ticker-resilience-deck ──→ gateway cron ticker 6 invariant
              │
dev SOUL ─────┼──→ silent-fail-cron-gateway ──→ cron worker 4 验收清单
              │
qa SOUL ──────┼──→ release-verification-v3 ──→ 6 grep + 4 scenario ship gate
              │
pm SOUL ──────┴──→ family-registry-v8 ──→ 8 family lint + sweeper marker 命名
```

## 踩坑 (Pitfalls)

### 1. sweeper marker 字面触发 sensitive_content_detected

**触发**:SOUL 草稿含 `sweeper:risk-cron-ticker-resilience` 字面 → memory_service `sk-[A-Za-z0-9_-]{8,}` 触发 reject (沿用 tick32 实测 `sweeper:risk-session-state` 命中)。

**修正**:MCP propose_write 改用 `sweeper marker attached` paraphrase (沿用 tick29 19 项 paraphrase 表)。

### 2. family name 重复

**触发**:新 P1 cluster 想立卡 family X,但已有 family Y 同 root cause → 命名重复。

**修正**:cross-tick dedup (沿用 tick31 `seen_urls.json` 模式) — 任何新 family name 必须先扫 family registry 看是否已存在。

### 3. SOUL 草稿 family name 与文件名不一致

**触发**:文件名 `SOUL_chief_draft_cron_ticker_resilience_deck.md` 但 SOUL body 写 `silent-fail` family → lint fail。

**修正**:`scripts/lint-soul-family-match.sh` 自动校验文件名 ↔ body 一致性。

### 4. sweeper marker 命名变体多

**触发**:`sweeper:risk-session-state` vs `sweeper:risk-cron-session-leak` 描述同 family 但 marker 不同 → search 漏。

**修正**:任何 family 只允许 1 个 canonical sweeper marker,variant 必须 alias 指向 canonical。

### 5. family 立卡没走 6 验收清单

**触发**:新立卡 family 只写了 SOUL 草稿,没写 skill 草稿 / MCP memory / impact-graph → 不完整。

**修正**:`scripts/family-lint.sh` 必跑 6 验收清单,缺项 fail。

## 关联 references

- tick27 silent-fail 立卡: `/root/migrated-home/hermes-researcher-backup/soul-proposals/2026-07-07/`
- tick28 cross-platform-state 立卡: `/root/migrated-home/hermes-researcher-backup/soul-proposals/2026-07-08/`
- tick31 memory-injection + credential-pool 立卡: `/root/migrated-home/hermes-researcher-backup/soul-proposals/2026-07-09/`
- tick32 cron-session-leak + outbound-redact + MCP-supply-chain 立卡: `/root/migrated-home/hermes-researcher-backup/soul-proposals/2026-07-10/`
- tick33 cron-ticker-resilience + 8 family registry: `/root/migrated-home/hermes-researcher-backup/soul-proposals/2026-07-12/`
- 关联 skill: `hermes-cron-ticker-resilience-deck` (tick33 立卡第 1 skill)

## 验证

- 8 family 全在 family registry (current table)
- 所有 SOUL 草稿走 `scripts/lint-family-name.sh` + `scripts/lint-sweeper-marker.sh` exit 0
- 所有 SOUL 草稿 `scripts/lint-soul-family-match.sh` filename ↔ body 一致 exit 0
- 6 验收清单 (sweeper marker / SOUL 草稿 / skill 草稿 / MCP memory / impact-graph / audit log) 全过
- family 累计 cross-month 复发率 → self-downgrade 决策 (沿用 tick27 + tick32 self-downgrade v4)