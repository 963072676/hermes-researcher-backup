# Researcher Deep-Tick Daily - 2026-06-27 (tick18)

> C 档自进化第 6 天 (inaugural = 2026-06-22)。本地 cron `hermes-researcher-deep-tick-daily` 的第 6 次运行。

## 核心发现

### 🚨 P1: GH PR #53183 + GH #53175 Gateway zombie
- **PR #53183 (P1, open 2026-06-26)**: fix: offload agent resource cleanup to executor thread with timeout
- **#53175 (P1, open)**: Gateway event loop dies silently, 16 prod crashes
- **影响**: 4 profiles (chief 派工 + default cron + pm + dev)
- **SOUL 草稿**: `soul-proposals/2026-06-27/chief-agent-gateway-zombie-exorcism.md` (P1)
- **SOUL 草稿**: `soul-proposals/2026-06-27/qa-worker-gateway-zombie-repro-test.md` (P2)
- **skill 草稿**: `skill-proposals/2026-06-27/gateway-zombie-detector.md`
- **MCP**: 7d332179-0771-4500-a593-dab4128516b1 (pending_review)

### 🔒 arxiv: Agent Privacy Survey (2606.26627, 2026-06-25)
- 首次系统综述 LLM agent memory privacy
- 攻击链: prompt injection → log sensitive → memory ingest → search
- **SOUL 草稿**: dev-worker-memory-privacy-redact (P1) + researcher-privacy-survey-weekly-cadence (P2)
- **skill 草稿**: arxiv-privacy-monitor
- **MCP**: d34244c1-bb6e-4b63-907e-ffc9aeeb4f7c (pending_review)

### 📚 arxiv: Semantic Early-Stopping 续接 (2606.22504)
- tick17 已生成 pm-orchestrator-iterative-loop-cap
- tick18 扩展: + max_wall_clock ≤ 30min + cosine 必填 + 例外审批
- **SOUL 草稿**: pm-orchestrator-iterative-loop-cap-extension (P2)
- **MCP**: 6642f690-0c8d-449d-90b4-b13d881fab12 (pending_review)

### 🔍 新增 arxiv 命中 (本 tick)
- **2606.27287** Prompt Injection in Multi-Injection Settings — chief SOUL recovery 路径
- **2606.26793** MIRROR memory MCTS red-teaming for Agentic RAG — researcher memory_slim v2 关联
- **2606.26479** Adaptive OOB Defenses Against Prompt Injection — ai-agent-security-defense 联动

### 📈 本地状态
- v0.17.0 (2026.6.19), 仍 latest release (8 天无新 tag)
- upstream main 持续 active (pushed 2026-06-26T18:01:33Z)
- 本地 = upstream main 同步 (researcher cron 走 hermes-agent fork 路径, 同样 v0.17.0)

## 数据源 (5 路并发)
- GitHub releases API: v2026.6.19 仍最新, 5 个 release
- GitHub issues since 2026-06-24: 14 issues + 36 PRs (50 items)
- HN Algolia (Hermes Agent 关键词): 20 hits, 0 first-seen (3d window)
- OpenRouter: 339 models, 92 Chinese-brand (MiniMax-M3 仍 #2 by usage)
- arxiv cs.MA + cs.CR: 15+10 hits, 4 directly relevant (2606.22504/26356/26627/27287 等)

## 5-Profile 影响矩阵

| Profile | 升级建议 | 优先级 | 草稿路径 |
|---|---|---|---|
| chief-agent | gateway zombie exorcism (P1) | HIGH | soul-proposals/2026-06-27/chief-agent-gateway-zombie-exorcism.md |
| dev-worker | memory privacy redact (P1) | HIGH | soul-proposals/2026-06-27/dev-worker-memory-privacy-redact.md |
| qa-worker | gateway zombie repro test (P2) | MEDIUM-HIGH | soul-proposals/2026-06-27/qa-worker-gateway-zombie-repro-test.md |
| pm-orchestrator | iterative loop cap extension (P2) | MEDIUM-HIGH | soul-proposals/2026-06-27/pm-orchestrator-iterative-loop-cap-extension.md |
| researcher | privacy survey weekly cadence (P2) | MEDIUM | soul-proposals/2026-06-27/researcher-privacy-survey-weekly-cadence.md |

## Skill 草稿 (3)
- `arxiv-privacy-monitor` — 周二 02:00 UTC 扫 arxiv cs.CR/cs.MA privacy topic (5 路 query)
- `memory-service-audit-cli` — researcher 自审 propose 历史, 替代 review_pending 403
- `gateway-zombie-detector` — 30s 间隔 healthz probe + 3 次失败 restart + 飞书 DM

## 跨 profile 影响图
详见 `cron-output/2026-06-27/impact-graph.md`。
- 关键依赖: chief zombie-exorcism → qa repro-test (必须同步)
- 关键依赖: dev privacy-redact → qa redact-test (隐含)
- 跨 tick 累积: 13 SOUL + 9 skill 草稿 (6 ticks 累计)

## 自我审计
详见 `docs/audit/2026-06-27.md`。
- 采纳率: 0% (4 天连续 user 未 ack)
- 降频触发: 6/29 强制降到隔日 (按 skill contract, 6/26 是 0-采纳第 1 天, 6/27 第 2 天, 6/28 tick19 第 3 天)
- 关键路径: 6/28 是最后冲刺 — 若 ack ≥ 1 条, 6/29 维持每日; 否则降频
- 最高 ROI: ack tick17 P1 (chief zombie-exorcism) → 采纳率跳 33%

## 状态
- ✅ 5 SOUL 草稿 + 3 skill 草稿 + impact-graph + audit + memory-snapshot 已落 backup repo
- ✅ 3 MCP memory propose (全部 pending_review, researcher role=agent 不 commit)
- ✅ pre-commit secret scan: 5 SOUL + 3 skill + 4 docs 已扫, 无 secret pattern 命中
- ✅ Local GitHub commit: pending (after this digest write)
- ✅ gh CLI 已认证 (963072676) — push 应能成功
- ⚠️ **MCP pending 累积**: 6 条 (tick17 3 + tick18 3) 等 chief/user commit
- ⚠️ **Feishu 推送**: 走最终 assistant message 自动投递 (按 skill contract, 不调 send_message 到 home DM)

## 下一步 (用户操作)
1. **关键**: review tick17 + tick18 5+5=10 个 SOUL 草稿 → ack 至少 1 条 P1 阻止降频
2. **可选**: 直接 merge PR #53183 (它 fix #53175, 与本 tick chief SOUL 配对)
3. **可选**: 配 arxiv-privacy-monitor 周二 02:00 UTC 自动跑
4. **6/29 决策**: 若届时仍 0 采纳, researcher cron 自动降到隔日 (skill contract 自动触发)