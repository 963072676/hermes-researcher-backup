# SOUL 草案 — pm — family registry v8 (8 total 立卡) (tick33)

> Tick33 2026-07-12 | Author: researcher profile | Streak=9 zero-adoption
> Memory ID: b868be0c-772e-4031-9bc1-733c24801e19 (MCP pending_review) — 共用 family registry
> Family: 8-family registry (沿用 tick27 命名约定 + tick33 立卡 cron-ticker-resilience-deck)

## 8 family registry (tick33 累计)

| # | family name | sweeper marker | 立卡 tick | 立卡触发 |
|---|---|---|---|---|
| 1 | silent-fail | `sweeper:risk-silent-fail` | tick27 (2026-07-07) | 3 个月内 silent-fail bug family 4 次复发 |
| 2 | cross-platform-state | `sweeper:risk-cross-platform-state` | tick28 (2026-07-08) | 跨 ≥ 2 platform label P1 cluster (#59607+#51646) |
| 3 | memory-injection-cross-platform | `sweeper:risk-memory-injection-platform-gateway` | tick31 (2026-07-10) | #40170+#40967+#41003 cross-platform |
| 4 | credential-pool-stale-snapshot | `sweeper:risk-credential-pool-stale` | tick31 (2026-07-10) | #25205+#15298+#15434 同 code path |
| 5 | cron-session-leak-closed-state | `sweeper:risk-cron-session-leak` | tick32 (2026-07-10) | #41935+#12029+#1416 同一 family |
| 6 | outbound-redact-call-site | `sweeper:risk-outbound-redact-call-site` | tick32 (2026-07-10) | #23810 60 天 open + 5 token shapes |
| 7 | MCP-supply-chain-5-control | `sweeper:risk-mcp-supply-chain-5-control` | tick32 (2026-07-10) | Microsoft+OWASP+Tencent+Koi+MCPTox 5-control converge |
| **8** | **cron-ticker-resilience-deck** | `sweeper:risk-cron-ticker-resilience` | **tick33 (2026-07-12)** | **9 GH issues 1 family (#32612+#32895+#37179+#27485+#11614+#48234+#49410+#30719+#44049)** |

## 草案 (pm SOUL v2 第 6 段追加)

```diff
+ ## Family Registry v8 (tick33 立卡)
+
+ **原则**:任何 P1 cluster 必须先归类到 family registry,family name 必须反映 root cause + scope。family 命名约定 = `<root-cause>-<affected-scope>` (沿用 tick31 立卡机制)。
+
+ 当前 8 family (沿用 tick27 + tick28 + tick31 + tick32 立卡):
+ - silent-fail / cross-platform-state / memory-injection-cross-platform / credential-pool-stale-snapshot
+ - cron-session-leak-closed-state / outbound-redact-call-site / MCP-supply-chain-5-control
+ - **cron-ticker-resilience-deck** (tick33 NEW 第 8)
+
+ **family 命名禁止**:
+ - 编号式命名 (family-1 / family-2 ❌)
+ - 模糊词 (general / misc / bug ❌)
+ - 单 issue 命名 (#12345 ❌ — family 应跨 issue)
+
+ **family 触发立卡条件** (沿用 tick31):
+ - 跨 ≥ 2 platform label 同时中招 → cross-platform family
+ - 同一 root cause 不同 issue 跨 ≥ 60 天仍 open → 架构性问题 family
+ - 同 code path 不同 fix PR 抢修 ≥ 3 PR → naming 应反映 code path (`-pool-` / `-state-` / `-injection-`)
+
+ **family 必跑验收清单** (立卡后必须):
+ 1. sweeper marker 命名 — `sweeper:risk-<root-cause>-<scope>`
+ 2. SOUL 草稿 chief-agent 段加 `family_name_v1` 立卡段落
+ 3. 至少 1 个 skill 草稿覆盖防御 (沿用 tick27 hermes-cron-session-leak-guard)
+ 4. MCP propose_write 写 1 条 family 立卡 memory (沿用 tick28 实战)
+ 5. impact-graph 标 family 依赖链
+ 6. audit log 写 family 累计 cross-month 复发率
+
+ **family 优先级**: silent-fail ≥ MCP-supply-chain-5-control ≥ cron-ticker-resilience-deck ≥ 其他 5 family
```

## 配套 skill 升级

- `hermes-family-registry-v8` (新立) — 8 family sweeper marker 汇总 + 自动 lint SOUL 草稿 family name 命名

## 优先级

P2: 但 family registry 是 research foundation (本 cron worker 决策树根)

## 关联 references

- 草稿落地: 本文件
- MCP memory_id: b868be0c-772e-4031-9bc1-733c24801e19 (pending_review)
- 关联 family: 7 prior families (见上表)
- 关联 tick: tick27, tick28, tick31, tick32, tick33

## 下一步

1. user review → pm SOUL v2 第 6 段合并
2. `hermes-family-registry-v8` skill 草稿 (本 tick 3 skill 配额之一)
3. family name lint 自动扫 — `grep -rE "family-[0-9]+" ~/.hermes/profiles/` 必须 0 命中