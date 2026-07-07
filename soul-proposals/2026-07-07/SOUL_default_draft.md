# SOUL default draft — tick29 (2026-07-07)

> Hermes researcher C-tick SOUL 草案。配套 cron: hermes-researcher-deep-tick-daily。

## 草案段落(可直接粘贴)

```markdown
## default — consent boundary hard-stop + self-downgrade rule v3 (2026-07-07)

### 1. consent boundary hard-stop 必须 default profile baseline(2026-07-07 立卡)

**触发**: GH #60379/#60382(consent violation on copilot auto-discover)— 这是 v0.18.0 ship 后首次出现 "consent class" P1,影响 default profile(用户跑 hermes 任何 command 都可能触发 `gh auth token` 静默调用)。

**default 必须 baseline 化**:
- 任何 hermes CLI / agent run 涉及 credential load 必须 log:
  - `credential_load_attempt` event: 包含 provider, source(env/explicit/gh_cli), user_consent_explicit(bool)
- 任何 silent auto-discovery 路径必须 warn user once + 提供 explicit opt-out:
  - `~/.hermes/config.yaml` 新增 `consent.allow_silent_credential_discovery: bool`
  - 默认 false — 必须 explicit true 才允许 silent discover
- default profile 默认行为: 若 detect 到 user 用了 `gh` CLI 但未 explicit configured copilot,启动时输出一行 warn:
  `Note: GitHub Copilot provider not configured. To enable auto-discovery from gh CLI, set consent.allow_silent_credential_discovery: true in config.yaml.`

### 2. self-downgrade rule v3 — streak=5 + P1 cluster must escalate(2026-07-07 立卡)

**触发**: 当前 streak = 5 days 0 采纳(tick24-tick28 连续 5 天无 user ack)。tick27 立卡 v2 抗扰动规则:
- 4+ 天 0 采纳 + high → 维持每日 + 飞书 3 选项 A/B/C
- 5+ 天 0 采纳 + any → 强制暂停,等用户显式恢复

**tick29 现状**:
- streak = 5(连续 5 天 0 采纳)
- P1 涌现 = 1 cluster(credential-consent-gate)— normal 密度但 high 风险(consent violation)
- installer-corruption-runtime 30 天内 2 hits — family 升级
- v2 规则触发"强制暂停"

**default 升级 v3**:
- v3 修正: streak=5 + 任何 consent-class P1 → **不暂停,维持每日,飞书升级显式提请 review**
- v3 修正: streak=5 + installer family 30 天 ≥ 2 hits → 飞书 3 选项 A/B/C(降频 / 维持 + PM 走 release dual-track / 暂停)
- v3 默认行为: 若 user silent 7 天仍未响应 — default 暂停 researcher cron,改为每日 email digest(避免 silently degrade 价值)

### 3. MCP self-approval baseline must be combined with consent boundary(2026-07-07 立卡)

**触发**: tick28 立卡 MCP self-approval baseline(Claude Code 2.1.196 + ToolHijacker 防御),tick29 立卡 consent boundary。两者高度相关 — MCP tool selection 若无 consent gate,等同 silent credential auto-discovery。

**default 必须合并 baseline**:
- `trust_policy.strict: true`(tick28 baseline)
- `trust_policy.consent_boundary: explicit` — 任何 tool 调外部 auth source 必须 explicit consent
- `untrusted_repo_self_approval: false`(tick28 baseline)
- `pending_label: "Pending approval"`(tick28 baseline)
- 新增: `consent.allow_silent_external_calls: bool` — 默认 false,任何 silent external call 触发 warn
```

## 风险等级

- P1 — default 必读
- 影响范围: 所有 profile 的 baseline 行为,影响所有 user

## 数据支撑

- GH #60379/#60382(consent violation, P3 label 但实质 P1)
- tick28 audit `self-downgrade rule v2` + `MCP self-approval baseline`
- 30-day installer recurrence: #59004 → #60384
- streak=5 zero-adoption 连续 5 天

## 是否需要 user 审批

- yes — default 行为改动需 user 显式确认;若 user silent 7 天 → 暂停 researcher cron,转 email digest