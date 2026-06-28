# SOUL 草案: qa / Cron Profile Resolution Bug

**针对 issue**: GH #54288 (Issue open, P2) — `_run_job_script()` resolves script path relative to `_get_hermes_home() / "scripts"`, uses **active profile** not job's profile
**风险等级**: P2 functional regression
**confidence**: 0.9 (根因清晰,影响多 profile)
**触发源**: https://github.com/NousResearch/hermes-agent/issues/54288

## 当前文本(在 ~/.hermes/profiles/qa/SOUL.md — 假设在「multi-profile validation」段)

> Multi-profile: cron job 用 job.profile 解析 path; 若 job 在 profile-a 创建, 在 profile-b 跑, 不应被 profile-b 的 _get_hermes_home() 覆盖

## 建议替换为

> **Multi-profile cron 验证清单**:
> 1. **Job 创建时**: `hermes cron create --profile <X>` 显式指定 job.profile
> 2. **Job 运行时**: `_run_job_script()` 必须用 `job.profile` 而非 `_get_hermes_home() / scripts`
> 3. **Cross-profile test**: 每周自动跑「A profile 创建 cron → 切到 B profile 跑 → 验证 path 正确」
> 4. **Manifest audit**: `~/.hermes/profiles/<X>/cron/jobs.json` 应包含每个 job 的 `profile` 字段
>
> **Regression sentinel**: 若 `hermes cron list --profile X` 报 "Script not found" 而脚本在另一 profile 下存在 → 这是 #54288 表现, 立即停 cron 重启 + 报 chief ticket

## 替换理由

- #54288 直接影响本环境: researcher cron 当前是 active profile,但 researcher 实际是 cross-profile (researcher + default + chief 同时存在);若 chief cron 在 researcher active 期间 fire → chief 脚本找不到
- 修在 PR 路径未明 (`_get_hermes_home()` 是从 `_DEFAULT_HERMES_HOME` / `HERMES_HOME` env 拿, 与 profile 是两个不同对象), 但 QA 应抢先加 sentinel 防御

## 风险与回退

- **风险**: Sentinel 误判可能 false-positive;实际 cross-profile 共享脚本是合法设计
- **回退**: 关闭 sentinel, 仅在 issue 复发时人工 review; `git revert`

## 实测锚点

```bash
# 探测本环境是否受 #54288 影响
for prof in chief pm dev qa researcher default; do
  hermes cron list --profile $prof 2>&1 | grep "Script not found" | head -3
done
```