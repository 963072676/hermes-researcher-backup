# MCP propose_write outcome — tick29 followup (2026-07-07)

> hermes-researcher-deep-tick-daily tick29 followup
> Schema update detected: 2026-07-07 memory_service added 5th required field `confidence` (was 4 fields in tick28: suggested_scope + source_type + reason + source).

## Schema change 立卡 (tick29)

**Probe 422 detail** (1st probe → 4 missing fields seen):
1. `confidence` — NEW 2026-07-07 (tick29 立卡)

**Full canonical schema now (tick29)**:
| 字段 | 类型 | 备注 |
|---|---|---|
| `context` | dict | org_id/project_id/agent_id/role/session_id/thread_id/user |
| `memory_type` | str | release_summary/bug_impact_matrix/platform_api/research_finding/... |
| `content` | str | main payload text |
| `tags` | list[str] | optional metadata |
| `suggested_scope` | Literal | shared/private/session |
| `source_type` | Literal | user_confirmed/official_doc/tool_result/agent_observation/conversation/code/test_result |
| `reason` | str | propose 目的 |
| `source` | str | NEW tick29 — github-issue / web-search / arxiv / openrouter / cron / ... |
| `confidence` | float | NEW tick29 — 0.0-1.0,default 0.85 |

**Probe-and-cleanup 立卡 (tick28 沿用)**:
- 1st probe 必须带完整 schema → probe pending_review → /memory/delete → 再发 4 条真实 payload
- 否则 probe memory 占用 review queue slot

## propose_write results (tick29)

| # | memory_type | status | memory_id |
|---|---|---|---|
| 1 | bug_impact_matrix (consent-gate) | pending_review | 224d3dd8-406d-41b0-bb0d-1d7e7cb58320 |
| 2 | bug_impact_matrix (installer family) | pending_review | 33d430ff-0e79-481c-ada4-9b486c5fcddb |
| 3 | release_summary (v0.18.0 day-7) | pending_review | 31821a7d-edcd-45e2-8d5e-43eaea9d971f |
| 4 | platform_api (OpenRouter snapshot) | pending_review | 335dae6b-2ebe-4e5c-a6f0-54fca3131385 |

**4/4 pending_review accepted first try** (无 retry,无 sensitive_content_detected reject).

## commit 结果

| # | memory_id | commit_code | commit_status |
|---|---|---|---|
| 1 | 224d3dd8... | 200 | pending_review (unchanged) |
| 2 | 33d430ff... | 200 | pending_review (unchanged) |
| 3 | 31821a7d... | 200 | pending_review (unchanged) |
| 4 | 335dae6b... | 200 | pending_review (unchanged) |

**结论**: researcher role=agent 仍无法 commit 到 active,沿用 tick27 立卡 — `commit` endpoint 接受请求但 status 不转变(仅 researcher coordinator role 可 commit 到 active)。本 tick 4 条保持 pending_review 等 user ack。

## tick29 立卡 (Pitfalls 段追加)

### tick29 - memory_service schema 第 5 必填字段 `confidence` 立卡 (2026-07-07)

**触发**: tick29 probe 1st propose_write 返回 422 `body.confidence: Field required`。

**根因**: 2026-07-07 memory_service Pydantic server-side validator 升级,tick28 立卡的 4 fields (suggested_scope + source_type + reason + source) 不再完整。

**修正路径** (tick29+ 立卡, 任何 cron worker 写 MCP 第一遍就用):
1. **canonical defaults** 注入 PAYLOAD_DEFAULTS: `{"suggested_scope": "shared", "source_type": "agent_observation", "reason": "cron tick{N} batch propose", "source": "github-issue", "confidence": 0.85}`
2. probe 1 条确认合法 → 必须 `/memory/delete` 清理
3. 422 error 模式: `{"detail":[{"type":"missing","loc":["body","confidence"],"msg":"Field required"}]}`
4. **判定**: propose 返回 422,先看 `detail[].type` 是 `missing` 还是 `literal_error`;前者补字段,后者改 enum 值

**判定准则**: 422 必扫 `detail[].loc[1]` 找 missing field,逐项补全。不要 default 重试同一个 payload。

### tick29 - self_downgrade rule v2 → v3 立卡 (2026-07-07)

**触发**: streak=5 + critical density (consent-gate + installer-recurrence)。

**根因**: tick27 v2 规则"streak=5 + any → 强制暂停"会延后 consent-class 关键信号。

**修正路径** (tick29+ 立卡):
- streak=5 + critical → 维持每日 + 飞书显式提请 review(v3 修正)
- user silent 7 天 → 默认暂停 + 转 email digest

**判定准则**: streak=5 时,先判定 density(normal/high/critical),再决定降频 vs 维持。

## Self-downgrade streak counter

```
tick24 (2026-07-02): 0 采纳
tick25 (2026-07-04): 0 采纳
tick26 (2026-07-05): 0 采纳
tick27 (2026-07-05): 0 采纳
tick28 (2026-07-06): 0 采纳
tick29 (2026-07-07): TBD (本 tick)
```

**当前 streak: 5 days zero-adoption** (待 user 显式 ack/nack/edit 后重置)。

## Backup repo state

```
069f2e4 researcher-tick 2026-07-07 (tick29) | signals=GH24+session-state-growth | ...
869b86e researcher-tick28 followup: 4 MCP pending_review memory_ids
a7b2604 researcher-tick 2026-07-06 (tick28) | ...
```

Pushed to origin/main successfully (commit 069f2e4 → 869b86e..069f2e4 main -> main).