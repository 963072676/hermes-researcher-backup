# SOUL qa-worker draft — tick29 (2026-07-07)

> Hermes researcher C-tick SOUL 草案。配套 cron: hermes-researcher-deep-tick-daily。

## 草案段落(可直接粘贴)

```markdown
## qa-worker — release-grep-checks dual-track + Windows update verify (2026-07-07)

### 1. release-grep-checks.sh 必须扩展到 in-place update channel(2026-07-07 立卡)

**触发**: tick27 #59004(fresh install) + tick29 #60384(in-place update on Windows)= installer family 30 天 2 hits。tick27 已立卡 5-item grep checklist:
1. merge conflict markers grep 必须 0 命中
2. TODO FIXME 暴增 ≤ baseline + 10%
3. import smoke test 必须成功
4. py_compile 必须 exit 0
5. 所有 JSON 必须 parse 成功

**但 #60384 表明**: 5-item checklist 只在 fresh install path 跑,in-place update path 未覆盖。

**qa 必须扩展**:
- 把 `scripts/release-grep-checks.sh` 改为 dual-track:
  - track 1 — fresh install: 对 exe / msi / dmg / deb / rpm / AppImage 内嵌 bundle 跑 5-item
  - track 2 — in-place update: 对 `hermes update` 后的 install root 跑 5-item
- Windows-specific 加 6-item(第 6 项):
  - `.py` 文件 in `hermes_bootstrap.py` / `web_server.py` 等关键 module 跑 `py_compile` 必须 exit 0
- qa 必须建 release verification dual-track runbook 文档,标 release-time SLA: dual-track 全 exit 0 才允许 ship

### 2. install/update ship-time gap must be reported in 5d audit(2026-07-07 立卡)

**触发**: v0.18.0 ship 后 7-day window 进入第 6-7 天,tick27 #59004 + tick29 #60384 显示 ship-time gap 仍在持续 — 必须建立 5-day ship-time audit 报告。

**qa 必须执行**:
- 每日 09:00 UTC 跑 `release-grep-checks.sh --dual-track` — 任何 track 失败立即飞书报错 + GitHub issue
- 5-day ship-time audit 每周一发布到 `docs/audit/ship-time-weekly-YYYY-MM-DD.md`,含:
  - fresh install 5-item 通过率(过去 7 天 release)
  - in-place update 5-item 通过率(过去 7 天 release)
  - installer-corruption-runtime family recurrence count(过去 30 天)
  - ship-time gap 趋势(↑ ↓ =)
- 若 30 天内 installer-corruption-runtime family ≥ 3 hits → 冻结对应 release channel,直至 dual-track 落地

### 3. consent-default test suite 必须 qa 编写(2026-07-07 立卡)

**触发**: PR #60404 修复 copilot auto-discover 默认行为,但其他 provider 的 consent 默认值未测。

**qa 必须编写**:
- `tests/consent/test_provider_explicit_gate.py` 覆盖:
  - 每个 provider 在未 configured 时,credential load 不调外部 auth tool
  - 每个 provider 在 configured 时,credential load 正常调外部 auth tool
  - telemetry `auth_blocked_no_consent` event 在 gate 拒绝时记录
- 集成到 `pytest tests/consent/` 每日跑
- 失败立即 issue + 飞书报错

### 4. sweeper marker risk-consent-gate 必须 qa 注册(2026-07-07 立卡)

**触发**: tick29 pm-orchestrator 立卡 `sweeper:risk-consent-gate` marker,但 qa 也必须注册到 GitHub label + sweep 自动化。

**qa 必须执行**:
- 创建 GitHub label `sweeper:risk-consent-gate`(description: consent boundary violations; color: red)
- sweeper-bot 配置: 任何新 issue 含 `type/security` + `area/auth` + provider/* 自动加此 label
- 每日 sweep 报告含 consent-gate family hit 数
```

## 风险等级

- P1 — qa 必读
- 影响范围: 所有 release cycle + consent-gate sweep

## 数据支撑

- tick27 SOUL_qa_draft(5-item grep checklist 立卡)
- GH #60384(in-place update channel 未覆盖)
- GH PR #60404(consent fix 模板,需 qa test suite 配套)
- 30-day recurrence: #59004 → #60384

## 是否需要 user 审批

- yes — qa release process 改动需 user 确认