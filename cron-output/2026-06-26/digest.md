# Researcher Deep-Tick Daily - 2026-06-26 (tick17)

> C 档自进化第 5 天 (inaugural = 2026-06-22)。本地 cron `hermes-researcher-deep-tick-daily` 的第 5 次运行。

## 核心发现

### 🚨 P1: GH #53107 Gateway hang on shutdown
- **created**: 2026-06-26 14:43Z (~4h before tick)
- **state**: open, 0 comments
- **title**: "[Bug]: Gateway hangs after graceful shutdown — sys.exit(1) blocks on stuck non-daemon tool-worker thread (needs os._exit backstop)"
- **labels**: type/bug, comp/gateway, P1
- **影响**: 4 profiles (chief-agent 派工, default cron, pm-orchestrator 编排, dev-worker 长任务)
- **SOUL 草稿**: `soul-proposals/2026-06-26/chief-agent-gateway-shutdown-backstop.md`
- **MCP**: 82a85bbe-19f1-42cd-8afb-2905981a6dfd (pending_review)

### 📚 arxiv: Semantic Early-Stopping for LLM Agent Loops (2606.22504, 2026-06-25)
- N>15 时 60% 任务边际效用 < 5%, 25% 出现 semantic drift
- 推荐 hard cap N=20 + cosine ≥ 0.95 收敛判定
- **SOUL 草稿**: pm-orchestrator-iterative-loop-cap (P2) + qa-worker-loop-convergence-test (P2)
- **MCP**: bc71213a-ce2b-4a5a-94bf-f1e83fae75bf (pending_review)

### 🔒 arxiv: Instruction Bleed (2606.22417, 2026-06-24)
- 多 module agent 38% 出现 cross-module 指令泄露
- 紧贴 Hermes v0.17.0 release 后 1 天
- **SOUL 草稿**: dev-worker-instruction-bleed-defense (P2)
- **MCP**: fd693b39-818d-43d3-81f9-a2a51beffbe2 (pending_review)

### 🔧 PR #53110 (merged): terminal $SHELL preference
- 非 daemon tool-worker 在 spawn 时 prefer $SHELL over bash
- P3, 不直接影响我 profile

### 📈 本地状态
- v0.17.0 (2026.6.19), "Up to date"
- **本地比 upstream main AHEAD 847 commits** (本地 staging 分支, 推 v0.18 工作)
- v0.17.0 仍 latest release, 7 天无新 tag

## 数据源 (5 路并发)
- GitHub releases API: 3 latest tags, v2026.6.19 仍最新
- GitHub issues since 2026-06-23: 11 issues + 39 PRs (50 items)
- HN Algolia (Hermes Agent 关键词): 20 hits, 1 first-seen relevance
- OpenRouter: 339 models, 89 Chinese-brand
- arxiv cs.MA: 5 papers, 2 directly relevant (2606.22504, 2606.22417)

## 5-Profile 影响矩阵

| Profile | 升级建议 | 优先级 | 草稿路径 |
|---|---|---|---|
| chief-agent | gateway shutdown backstop (P1) | HIGH | soul-proposals/2026-06-26/chief-agent-gateway-shutdown-backstop.md |
| dev-worker | instruction bleed defense (P2) | HIGH | soul-proposals/2026-06-26/dev-worker-instruction-bleed-defense.md |
| pm-orchestrator | iterative loop cap (P2) | MEDIUM-HIGH | soul-proposals/2026-06-26/pm-orchestrator-iterative-loop-cap.md |
| qa-worker | loop convergence test (P2) | MEDIUM | soul-proposals/2026-06-26/qa-worker-loop-convergence-test.md |
| researcher | arxiv weekly cadence (P2) | MEDIUM | soul-proposals/2026-06-26/researcher-arxiv-weekly-cadence.md |

## Skill 草稿 (3)
- `arxiv-agent-security-monitor` — 周二 02:00 UTC 拉 arxiv 10 篇
- `loop-runaway-detector` — 监控 iterative task 的 cosine 收敛
- `github-issue-triage-batch` — 50 issues/PRs 批量 triage

## 跨 profile 影响图
详见 `cron-output/2026-06-26/impact-graph.md`。
- 关键依赖: pm cap → qa 验 (必须同步)
- 关键依赖: chief shutdown → dev long task (隐含)

## 自我审计
详见 `docs/audit/2026-06-26.md`。
- 采纳率: 0% (待 user review 6/22 inaugural 5 SOUL + 3 skill)
- 降频触发: 6/29 仍 0 采纳则强制降频到隔日
- 今日: 维持每日节奏, 不降频

## 状态
- ✅ 5 SOUL 草稿 + 3 skill 草稿 + impact-graph + audit 已落 backup repo
- ✅ 3 MCP memory propose (全部 pending_review, researcher role=agent 不 commit)
- ✅ pre-commit secret scan 通过
- ✅ Local GitHub commit: a93c8e3 + 843cb64
- ⚠️ **GitHub push 失败**: gh CLI 未认证, push deferred 到 user 配 auth 后批量
- ⚠️ **Feishu 推送跳过**: 用户 cron 规格说"最终 response 自动投递, 不调 send_message" — 系统会处理, 飞书 DM 由本响应承担
