---
name: github-issue-triage-batch
description: 一次拉 GitHub 50 issues/PRs, 区分 issues vs PRs, 判定 P0/P1/security 标签, 输出 triage table 含 affects_my_env 判定。Use when: researcher tick / cron-self-evolution-daily-digest / chief-agent 派工 "扫 Hermes 仓"。
---

# GitHub Issue Triage Batch

## 何时调用
- researcher tick (本 skill 设计目标场景)
- cron-self-evolution-daily-digest Step 3
- chief-agent 派 "扫 Hermes 仓 3 天" 类任务

## 标准流程
1. **拉数据**
   ```bash
   curl -sS "https://api.github.com/repos/NousResearch/hermes-agent/issues?state=all&since=<3_days_ago>&per_page=50" -o /tmp/issues.json
   ```
2. **分类** — `'pull_request' in item` 区分
3. **PR 状态** — PR 没有 `merged` 字段, 需单独 `/pulls/{n}` 查
4. **判定 relevance**
   - 标签含 `P0` / `P1` / `P2` / `security` / `comp/gateway` / `comp/cli` / `comp/agent`
   - 影响: matches profile 的 component
5. **去重** — `seen_urls.json` 三轮降级 (url 直查 → 去 trailing `/` → https↔http)
6. **输出 table**
   ```
   | # | type | state | labels | affects_my_env | first_seen | url |
   |---|------|-------|--------|----------------|------------|-----|
   ```

## 常见坑
- `/issues` 端点同时返回 PRs (需 `pull_request` 字段区分)
- `since` 按 `updated_at` 过滤, 客户端再按 `created_at` filter
- GitHub 限速 60/h unauthenticated — 攒请求, 别密集打
- 大小写变体 URL (capital H+A) 算 first_seen, 需 structural-mirror 过滤

## 何时不该调用
- 任务明确 "只看 1 个 issue" (直接 `/issues/{n}`)
- GitHub 限速已耗尽 (403 rate limit)
- 任务明确 "只看 PR" (`/pulls?state=all`)

## 验证
- 50 items 拉回, issues + PRs 比例符合仓现状 (~ 15/35)
- triage table 中 affects_my_env 准确率 > 90% (manual spot check)
- first_seen URL 数与 baseline 漂移 < 5 (避免假 first_seen)
