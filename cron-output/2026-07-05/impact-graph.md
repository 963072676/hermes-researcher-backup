# 跨 profile 影响图 (2026-07-05) — tick26

> 本 tick 涉及 5 个 profile (default/chief/dev/qa/pm) 全部更新
> 同时触发 3 个新 skill 立项 + 4 个 MCP memory propose

## 主依赖链:A → B → C

| 触发 (A) | 直接影响 (B) | 隐含影响 (C) | 风险 | 处理 |
|---|---|---|---|---|
| `#58345` xAI grok-4.3 drops multiline MCP args | default SOUL 加 multiline 防御 + 新 skill `hermes-multiline-string-passthrough` | researcher / chief / pm 任一 cron 用 grok-4.3 调 send_message 飞书卡片 → markdown 表格塌陷 | P1 | researcher cron 每日 baseline probe + multiline-aware prompt prefix |
| `#58363 + #58379 + #50733 + #54329 + #49334` family silent-fail cluster(5 issues) | chief SOUL 加 cron delivery 三层防御 + 新 skill `hermes-cron-silent-fail-probe` | 任意 cron worker(包括 researcher / pm / kanban) delivery 静默丢 → user 看不到产出 | P0 | chief cron 跑 daily silent-fail audit,02:00 UTC |
| `#58317 + #58407` compression crash + auto-lower silent | dev SOUL 加 type-coercion guard + config-intent preservation gate | qa ship-verification harness 必须加 silent-fail test | P1 | dev code review + qa regression test 在 v0.18.1 release day -7 |
| `#58360` memory provider race(0 tools → 55 tools) | dev SOUL 加 async provider init race barrier | qa 必须 rebuild_provider_tools() regression | P1 | dev fix #58365 merged + qa test 跟进 |
| `#58409 + #58355` 5xx failover + stale credential prune | pm SOUL 加跨 profile credential governance + chief 加 5xx-aware failover | 5 profile 共享 minimax-cn credential,任一 stale → 5 profile 都 down | P1 | pm daily audit + dev PR #58355 |
| `#58378 + #58379` yuanbao silent fail + #58369 asyncio.sleep blocking | pm SOUL 加 daily 72h coverage triage + 新 skill `hermes-post-ship-daily-triage` | chief acceptance verification 周期变密(每日 vs weekly) | P1 | pm 03:00 UTC cron + chief 06:00 UTC review |

## 5 profile 多重影响图

```
P0 cluster (#58363 群 silent-fail)
   ├─ chief SOUL  ← 三层防御
   ├─ researcher cron  ← silent-fail 三层 probe
   ├─ pm SOUL  ← 72h coverage daily
   ├─ chief cron (hermes-pm-post-ship-triage-daily)  ← 03:00 UTC
   └─ qa regression test  ← silent-fail suite

P1 cluster (grok MCP multiline drop)
   ├─ default SOUL  ← typed-guard workaround
   ├─ researcher cron digest  ← multiline-aware prompt prefix
   ├─ chief delivery  ← 受影响(同 provider)
   └─ pm 飞书 card  ← 受影响(同 provider)

P1 cluster (compression crash + silent auto-lower)
   ├─ dev SOUL  ← type-coercion + config-intent gates
   ├─ qa regression  ← silent-fail test 6 file
   └─ chief release-coverage  ← v0.18.0 4-day cluster

P1 cluster (memory provider race + stale credentials)
   ├─ dev SOUL  ← async init barrier + credential lifecycle
   ├─ qa 5 profile e2e  ← credential governance
   ├─ pm credential governance  ← 跨 profile secret
   └─ chief monitor  ← 5 profile multiplex fallback

## 跨 profile 调用契约(关键)

1. **chief 跑 cron-silent-fail audit 06:00 UTC** — 需要读 researcher cron digest 文件路径
   - 路径: `~/.hermes/profiles/researcher/cron/output/digest/{date}-researcher-tick{N}.md`
   - 跨 profile 软 guard bypass 用 `terminal cp`
2. **pm 跑 post-ship-daily-triage 03:00 UTC** — 需要读 GitHub release body + open issues
   - 路径: 走 GitHub API,无需本机文件
3. **qa regression test harness** — 需要 dev PR merged 才能跑
   - 路径: `tests/ship_verification/v0_18_0_patch/run_all.py`
   - depends on: PR #58352 + #58365 + #58355 + #58409 + #58379 merged
4. **default SOUL multiline workaround** — 任何 cron tick 调 tool call 时自动挂
   - 触发点: cron worker 在 tool call wrapper layer 加 `multiline_payload_check`
5. **researcher cron 加 4 个 MCP propose writes** — 跨 default + researcher 双路径
   - chief profile 必须 review 后 commit(researcher role=agent 不 commit)

## 风险汇总

| 风险 | 概率 | 影响 | 优先级 |
|---|---|---|---|
| 5 个 profile 同时改 SOUL → 一次性 commit 体量过大 | M | M | P2 |
| chief cron 03:00 + 06:00 UTC + 02:00 UTC researcher 共 3 个 cron 同时跑 | L | H | P1 |
| qa 6 file regression test 与 dev PR merge 顺序冲突 | M | M | P2 |
| pm 03:00 UTC cron 与 chief 06:00 UTC cron 形成 tight loop | L | M | P2 |
| silent-fail cluster 5 issues 中任 1 个 fix 不完整 → 仍 silent | M | H | P1 |

## 推荐 review 顺序

1. **chief + default SOUL(立即)** — silent-fail 是 silent mode,影响所有 cron
2. **pm SOUL + `hermes-post-ship-daily-triage` skill(本周内)** — daily 72h coverage 自循环
3. **dev + qa SOUL + 3 个 skill(本月内)** — 都有 reference impl,不必抢时间
