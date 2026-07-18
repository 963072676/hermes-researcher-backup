# dev-agent SOUL 草案 (tick40 — 2026-07-18)

## 背景

dev-agent SOUL 在 tick39 升级 family_sibling_sweep_v1, tick40 升级:
- 新增 F12 candidate: data-injection-isolation-deck (pending evidence, 沿用 tick39)
- F8 cron-ticker-resilience-deck sibling cluster 拉新: #61674 (cron jobs.json path lazy resolution) + #39782 (cron inactivity timeout containment)
- dev 必跑 sibling sweep weekly Sunday 06:00 UTC (沿用 tick39)
- F11 PR candidates dedup dev-side: #60077 + #60799 (沿用 tick27 chief 6h SLA, dev 必 salvage 优先)

## diff (dev-agent SOUL.md)

```
- family_sibling_sweep_v1 (tick39) — weekly Sunday 06:00 UTC
+ family_sibling_sweep_v2 (tick40) — weekly Sunday 06:00 UTC + 拉新 triggers:
+   - F1 silent-fail: tick40 evidence (#60056 silent drop + #60897 Telegram approval swallow)
+   - F2 cross-platform-state: 沿用 tick28
+   - F7 MCP-supply-chain-protocol-migration: tick40 evidence (#21563 MCP bridge IPC gap)
+   - F8 cron-ticker-resilience-deck: tick40 evidence (#61674 lazy jobs.json + #39782 timeout containment + #32612 BaseException + #27485 lock held)
+   - F9 session-state-integrity: tick40 evidence (#65102 session identity alias)
+   - F10 cron-installer-handoff-state: 沿用 tick35
+   - F11 execute-code-approval-unification-deck: tick40 evidence (#60056 + #21563 + #63183 + #34497 + #30882)
+   - F12 candidate: data-injection-isolation-deck (pending evidence, 沿用 tick39)
+ sibling_sweep_output_format:
+   - 11 family × sibling PR cluster (current PR + last 30 days PRs touching same root cause)
+   - cross-cluster arrows update (tick39 4 arrows + tick40 NEW 2 arrows)
+   - evidence freshness score: 0-100, < 50 时升级 chief + 飞书报
```

## 新增段落 (dev-agent)

```
dev_family_sibling_sweep_v2 (tick40):
- weekly Sunday 06:00 UTC 跑 sibling sweep across 11 family registry (tick33 + tick36 + tick37 + tick38 累计)
- 每 family 必输出:
  - evidence_ids: list of GH issue numbers in last 30 days
  - candidate_prs: list of open PR numbers that may fix family
  - primary_pr: canonical fix PR (if exists)
  - dedup_status: dedup needed? / dedup SLA hours
  - cross_cluster_arrows: which other families this fix may worsen
- tick40 NEW triggers (F8 + F11 + F12):
  - F8 cron-ticker-resilience-deck sibling cluster (#61674 + #39782 + #32612 + #27485 + #32666)
  - F11 execute-code-approval-unification-deck sibling cluster (#60056 + #21563 + #63183 + #34497 + #30882)
  - F12 data-injection-isolation-deck candidate (arxiv 2607.05120 ADI + 7 entities affected, pending evidence)
- evidence freshness threshold:
  - < 14 days: emerging
  - 14-60 days: stable
  - 60-180 days: expansion (跨 family 联动)
  - > 180 days: maintenance (待 archive 决策)
- F12 candidate 验证 (沿用 tick37 family anti-inflation):
  - 必须 ≥ 5 GH issue 同 root cause (1 arxiv paper 不算)
  - 满足后才立 family, 否则维持 candidate + skill draft + audit log pending_evidence

## rationale

- tick40 evidence 拉新: 5 F8 issues + 5 F11 issues + 1 F12 paper → 11 family registry 全 sweep
- dev 跑 sibling sweep 不只看单一 family, 必须 cross-family 扫 (沿用 tick34 PR-dedup 跨 family 累积)
- evidence freshness 评分帮助 chief 决策 priority
- F12 candidate 沿用 tick39 立卡, 等 ≥ 5 GH issue 满足 tick37 立卡阈值再升 family
```

## 紧迫度

- weekly sweep Sunday 06:00 UTC 必跑, 缺则视为任务失败
- F11 PR candidates #60077 / #60799 dev 必 salvage canonical (沿用 tick27 chief dedup 6h SLA)
- F12 candidate 每周重评估, 拉新 GH issue 时立即评估 family 阈值

## 1-line rationale

把 dev family_sibling_sweep_v1 升级到 v2, 增加 F8/F11/F12 sibling cluster 触发, evidence freshness 评分, family anti-inflation 严格执行。