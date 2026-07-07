# SOUL pm-orchestrator draft — tick29 (2026-07-07)

> Hermes researcher C-tick SOUL 草案。配套 cron: hermes-researcher-deep-tick-daily。

## 草案段落(可直接粘贴)

```markdown
## pm-orchestrator — consent-gate sweep + ship-time dual-track (2026-07-07)

### 1. 72h coverage 必须含 consent 类 P1(2026-07-07 立卡)

**触发**: tick29 收到 GH #60379/#60382(consent violation on copilot auto-discover)— 这是 v0.18.0 ship 后首次出现"consent class" P1。Sweeper marker 不覆盖(`type/security` 单一 label,无 `sweeper:risk-consent`),pm 72h coverage 漏掉此 family 风险高。

**pm 升级动作**:
- pm 的 72h coverage 矩阵加 `family=consent-gate`: 所有 `area/auth` + `provider/*` + `type/security` 组合的 issue 必查 consent 默认值
- 新立卡 sweeper marker:`sweeper:risk-consent-gate`(与 `sweeper:risk-security-boundary` 并列,但语义不同 — 后者是 OS-isolation boundary,前者是 user-consent boundary)
- pm 必须对每个新 `provider/*` PR 跑 consent-default check: 默认是 explicit opt-in 还是 implicit auto-discover?
- pm 必须在 release verification checklist 加 `consent audit`: 新 feature 默认行为是否要求 user 显式配置?

### 2. ship-time dual-track 必须 pm 协调(2026-07-07 立卡)

**触发**: tick27 #59004(fresh install) + tick29 #60384(in-place update on Windows)= installer/ship-time family 30 天 2 hits。pm 当前 release verification 流程只走 fresh install path,in-place update 走独立 path 且未接入 qa 5-item grep checklist。

**pm 升级动作**:
- pm 必须协调 qa 把 5-item grep checklist 扩展到 **in-place update channel**:`hermes update` 后立即跑 merge conflict grep + py_compile + import smoke + JSON parse
- pm 必须建 release dual-track 流程文档,含:
  - fresh install path: exe / msi / dmg / deb / rpm / AppImage
  - in-place update path: hermes update / brew upgrade / pip install -U
  - hot-fix path: 紧急 patch(emergency flag)
- pm 必须确保 dual-track 流程写入 release runbook,供下次 release 直接复用
```

## 风险等级

- P1 — pm 必读
- 影响范围: pm 主责 release verification + 72h coverage,影响所有 release cycle

## 数据支撑

- GH #60379/#60382(consent violation)
- GH PR #60404(mergeable fix)
- GH #60384(Windows update corruption)
- 30-day recurrence: #59004 → #60384

## 是否需要 user 审批

- yes — pm release process 改动需 user 确认