# Cross-Profile Impact Graph — tick29 (2026-07-07)

> Hermes researcher C-tick cross-profile impact analysis。
> 基于今日 5 SOUL + 3 skill 草案,识别 profile 间隐含依赖链。

## 主信号

| Issue | Cluster | Severity |
|---|---|---|
| GH #60379 / #60382 + PR #60404 | credential-consent-gate (new family) | P1 |
| GH #60384 | installer-corruption-runtime (recurrence 30d 2 hits) | P1 |
| GH #60350 (corroborating #56771/#57736/#58662) | session-state env var leak (4 issues now) | P1 |

## Impact Graph (依赖链)

```
default profile
  │
  ├── consent.allow_silent_credential_discovery: false  (default 配置)
  │   └── 隐含要求: 所有 hermes CLI / agent run 在调外部 auth tool 前必须显式 consent
  │       └── 迫使 chief-agent 升级 release verification checklist:
  │           ├── qa-worker 跑 consent-default test suite (全 provider)
  │           └── pm-orchestrator 跑 consent audit (新 feature 默认行为)
  │
  ├── trust_policy.consent_boundary: explicit  (default 配置)
  │   └── 隐含要求: MCP tool 调外部 auth source 必须 explicit consent
  │       └── 沿用 tick28 hermes-mcp-self-approval-baseline,扩展 consent_boundary 维度
  │
  ├── self-downgrade rule v3 (streak=5 + critical density)
  │   └── 隐含要求: 即使 streak=5,consent-class P1 不降频
  │       └── 迫使 cron `hermes-researcher-deep-tick-daily` 维持每日,user silent 7 天才暂停
  │           └── 飞书 3 选项必须含 "维持每日 + 显式提请 review" 选项
  │
  └── cross-platform-state baseline (tick28 立卡)
      └── 与 consent-gate 合并:MCP tool selection + credential load 都必须 explicit gate

chief-agent profile
  │
  ├── 24h 内 review PR #60404
  │   └── 验证 fix 是否完整(覆盖 `agent/credential_pool.py:1923-1950` + `hermes_cli/copilot_auth.py:93-101` 两处)
  │       └── merge 后立即派 qa-worker audit 其他 provider(anthropic/openai/google/deepseek/moonshot)
  │           └── audit 报告 → docs/audit/credential-auto-discovery-2026-07.md
  │
  └── installer-corruption-runtime 升级为架构性问题
      └── 30 天 2 hits (#59004 + #60384) → 升级判定条件
          └── 若 30 天 ≥ 3 hits → chief 必须冻结 Windows release channel
              └── 迫使 pm-orchestrator 协调 release dual-track 流程

pm-orchestrator profile
  │
  ├── 72h coverage 矩阵加 consent-gate family
  │   └── sweeper marker `sweeper:risk-consent-gate` 必须注册到 GitHub
  │       └── 迫使 qa-worker 配置 sweep-bot 自动加 label
  │
  ├── release dual-track 流程文档
  │   └── fresh install + in-place update + hot-fix 三 channel
  │       └── 迫使 qa-worker 扩展 release-grep-checks.sh 到 6-item dual-track
  │
  └── weekly 5-day ship-time audit 报告
      └── 每周一发布 `docs/audit/ship-time-weekly-YYYY-MM-DD.md`
          └── 迫使 qa-worker 每日 09:00 UTC 跑 dual-track verify

dev-worker profile
  │
  ├── credential_consent explicit gate (PR #60404 模板)
  │   └── agent/credential_pool.py + hermes_cli/copilot_auth.py 两处都加 gate
  │       └── 迫使 qa-worker 写 test_provider_explicit_gate.py 全 provider 覆盖
  │
  ├── update-channel corruption 修复 (Windows)
  │   └── hermes update 走 atomic rename + py_compile 校验 + rollback to backup
  │       └── 迫使 qa-worker 跑 in-place update channel 的 6-item grep checklist
  │
  └── credential auto-discovery audit (其他 provider)
      └── grep `auth.token` 全扫,找出所有 silent-seed 路径
          └── 输出 docs/audit/credential-auto-discovery-2026-07.md

qa-worker profile
  │
  ├── release-grep-checks.sh dual-track 扩展
  │   └── 5-item → 6-item(加 Windows-specific py_compile)
  │       └── fresh install + in-place update + hot-fix 三 channel 都跑
  │
  ├── consent-default test suite
  │   └── tests/consent/test_provider_explicit_gate.py 全 provider 覆盖
  │       └── 集成 pytest 每日跑,失败立即 issue + 飞书报错
  │
  ├── sweeper marker risk-consent-gate 注册
  │   └── GitHub label 创建 + sweep-bot 配置
  │       └── 每日 sweep 报告含 consent-gate family hit 数
  │
  └── weekly ship-time audit
      └── docs/audit/ship-time-weekly-YYYY-MM-DD.md 每周一发布

## 跨 profile 强制依赖总结

1. **default → chief → dev → qa**: consent-gate 必须 dev 实现 → qa test suite → chief review merge → default config baseline
2. **chief → pm → qa**: installer family 升级 → pm dual-track 流程 → qa dual-track verify
3. **default → cron**: self-downgrade rule v3 影响 researcher cron cadence,user silent 7 天触发暂停
4. **pm → qa**: sweeper marker `risk-consent-gate` 必须 pm 注册 → qa 配置 sweep-bot

## 风险升级条件(若未满足)

- 若 chief 7 天内未 review PR #60404 → P1 持续 open,user 风险面扩大
- 若 qa 7 天内未扩展 dual-track verify → #60384 类 issue 再发概率 > 60%
- 若 pm 14 天内未注册 `risk-consent-gate` marker → 后续 consent-gate P1 漏检
- 若 default 7 天内未 baseline consent boundary → silent-seed 行为在新 provider 中重发

## 关联

- SOUL 草案: `soul-proposals/2026-07-07/SOUL_*_draft.md` (5 个 profile)
- Skill 草案: `skill-proposals/2026-07-07/SKILL_*.md` (3 个 skill)
- 历史 impact graph: `cron-output/2026-07-06/impact-graph.md` (tick28)