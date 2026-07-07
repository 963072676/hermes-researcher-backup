# SOUL chief-agent draft — tick29 (2026-07-07)

> Hermes researcher C-tick SOUL 草案。配套 cron: hermes-researcher-deep-tick-daily。
> 修改路径: 在 chief-agent profile SOUL 末尾追加本节(commit before next cron tick)。

## 草案段落(可直接粘贴)

```markdown
## chief-agent — credential-consent-gate + installer recurrence triage (2026-07-07)

### 1. credential-consent-gate 必须 chief 亲自升级 P1 处理(2026-07-07 立卡)

**触发**: tick29 收到 GH #60379(中文版)+ #60382(英文 dup)— 用户报告 Hermes 在 startup 无 consent 调 `gh auth token`,把 GitHub token 静默写进 `~/.hermes/auth.json`。Maintainer alt-glitch triage 评为 "in-trust-envelope consent/transparency concern, tracked as security-hardening" — 虽非 active exploit,但 consent 缺失属可发布前已知的工程缺陷。

**PR fix 已就绪**: #60404 by liuhao1024, MERGEABLE, +56/-? 行, fix(security): prevent unauthorized GitHub token access from gh CLI。修法清晰:加 `is_provider_explicitly_configured()` gate,模仿 anthropic provider 的 PR #4210 模式(only auto-discover when user 显式 configured)。

**chief 必须亲自升级**:
- 默认行为: chief 24h 内 review #60404,验证 fix 是否完整(是否覆盖所有 gh CLI 调用点 — `agent/credential_pool.py:1923-1950` + `hermes_cli/copilot_auth.py:93-101` 两处都封堵?)
- 不 default 派 dev-worker 修 — 这种 consent 类 issue 涉及产品决策边界,chief 亲自评估
- merge 后立即派 qa-worker audit 其他 provider 的 credential auto-discovery: 是否所有 provider 都走 explicit-configuration gate? 是否 anthropic / openai / google 等也有类似 silent-seed 行为?
- 发 release note: 修复后调用 `gh auth token` 必须 explicit user configured 才执行

### 2. installer/ship-time-gap 第二次复发必须升架构性问题(2026-07-07 立卡)

**触发**: tick29 收到 GH #60384 — `[Windows] hermes_bootstrap.py corrupted during 'hermes update', SyntaxError blocks backend startup`。同 family 在 30 天内第 2 次:
- tick27 #59004: Windows installer 内嵌的 web_server.py 含 merge conflict 标记 ship 给用户
- tick29 #60384: Windows `hermes update` 后 hermes_bootstrap.py 被 corrupt,line 205 `import asyncio.coroutines` 残留导致 SyntaxError,fresh install 立即 crash loop

**根因**: tick27 已立卡 qa 5-item grep checklist,但 #60384 表明 **Windows-specific 的 update 流程** 未走 installer ship 的同一批 verification 路径。两者都是 ship-time,不同 release channel:
- #59004 = fresh install (exe msi dmg deb rpm AppImage)
- #60384 = in-place update (hermes update CLI on Windows)

**chief 必须升级**:
- qa-worker 5-item grep checklist(merge conflict / TODO FIXME / import smoke / py_compile / JSON parse) 必须在 **all release channels** 跑(install + update),不只是 install
- release verification 流程必须 dual-track: fresh install + in-place update
- 加新立卡 family `installer-corruption-runtime`(与 silent-fail / cross-platform-state 并列)
- 若 #60384 30 天内再发第 3 次 — chief 必须冻结 Windows release channel 直至 dual-track 流程落地
```

## 风险等级

- P1 — chief 必读
- 影响范围: chief + dev + qa + pm + default 5 profile 都受 credential-consent-gate 治理变化影响

## 数据支撑

- GH #60379/#60382(2026-07-07 filed,1 comment from alt-glitch COLLABORATOR)
- GH PR #60404 liuhao1024(2026-07-07T17:21:17Z,MERGEABLE,fix #60379)
- GH #60384(2026-07-07 filed,needs-repro,Windows 10)
- 30-day recurrence: #59004 → #60384(2 hits,family `installer-corruption-runtime`)

## 是否需要 user 审批

- yes — chief SOUL 改动属于高级别,需 user 显式确认
- fallback: 若 5 天内无 ack → 维持现状,飞书 3 选项提示