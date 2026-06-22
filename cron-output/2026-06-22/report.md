# researcher-tick: 2026-06-22-tick1 (inaugural)
扫描窗口: 2026-06-19 ~ 2026-06-22 北京时间(过去 3 天)
profile 数: 5
新增信号: 30+ 命中 across 8 路
新增 memory 提议: 5 (pending_review: 5,等 chief/user commit)
新增 SOUL 草稿: 5 → github.com/963072676/hermes-researcher-backup/tree/main/soul-proposals/2026-06-22
新增 skill 草稿: 3 → github.com/963072676/hermes-researcher-backup/tree/main/skill-proposals/2026-06-22
采纳率(过去 7 天): N/A (inaugural)

## 1. Hermes 官方
**v0.17.0 (v2026.6.19) "Reach Release" — 1,475 commits / 800 PRs / 300 issues closed**
- 本地版本: `Hermes Agent v0.17.0 (2026.6.19) · upstream 2b3a4f0a`,Update available: 261 commits behind
- 关键 surface: iMessage via Photon Spectrum / Raft agent network / async subagents / image editing / Cursor Composer via xAI Grok / profile builder + secure login / Skills Hub 重写 / memory tool atomic batch operations / disk-cleanup + security-guidance plugins
- Researcher 自身影响: profile builder 让 dashboard 视图成为可能;async subagents 可重构成 "scout × 5 + synthesizer × 1" 模式;disk-cleanup 默认行为迫使 in-tick backup 到 backup 仓库
- Memory: `61475b95`

## 2. Claude Code 生态
- Anthropic Sonnet 4.6 (Feb 17 2026) / Opus 4.5 (Nov 24 2025) / Opus 4.6 (Feb 5 2026) / Opus 4.8 (May 28 2026, 1M context, $5/$25) / Sonnet 4 + Opus 4 retired June 15
- Claude Code: Plan Mode 更精准、Workflows research preview、v2.1.158+ Auto mode on Bedrock/Vertex/Foundry、managed deployments 版本范围强制
- 影响: dev-worker 的 fallback 链需要更新 Sonnet 4.6 / Opus 4.8 选型
- (注:web_search query 误把 Opus 4.5 当 2026-06,实际是 2025-11 的旧 model,已校正时间线)

## 3. Loop Engineering / 多 Agent
- **LangChain 官方 4 圈框架**: agent loop / verification loop / event-driven loop / hill-climbing loop
- **swyx / i-scoop Loop Engineering**: "builder ≠ judge" 硬规则
- **RALPH Loop**: Generate → Critique → Judge → Improve,Critic 引导修复,Judge 强制 stop
- **architect-loop**: 跨厂商 builder × judge (Claude Fable 5 × GPT-5.5)
- arxiv 2606.13707 Orchestra-o1 omnimodal orchestration / 2606.11440 INFRAMIND infra-aware / 2606.13598 OrchRM / 2605.25746 structure-guided / 2606.14790 XFlow protocol programming
- Memory: `d72fc9b1`

## 4. MCP / Memory
- **2026-07-28 RC**: stateless core / Tasks extension (`tasks/list` removed) / MCP Apps SEP-1865 / EMA 2026-06-18 stable (Okta + Claude/VS Code, Asana/Atlassian/Canva/Figma/Linear/Supabase launch) / well-known server discovery / formal deprecation
- python-sdk v2.0.0a2 ship 2026-06-16, three type modules (monolith / v2025_11_25 / v2026_07_28)
- Memory: `19c6c152`

## 5. AI Agent 安全
- **arxiv 2606.14517** "From Shield to Target" — guardrail DoS via beam-search payload
- **arxiv 2605.17986** LivePI — 7 input surfaces / 12 attack families
- **arxiv 2606.10525** AgentDojo — GCG/TAP automated PI; black-box > gradient-based
- **arxiv 2603.19423** "Autonomy Tax" — defense training breaks agents (capability-alignment paradox)
- **arxiv 2602.14211** SkillJect — automated skill-based PI
- Memory: `cadbfcf1`
- Hermes #50452 (smart approval hardening) closed 2026-06-21; #50414 IPv6 scope ID URL safety; #50423/#50514 redaction ongoing

## 6. arxiv / 社区新动态
- GLM-5.2 (2026-06-16 ship) — 753B params, 1M context, MIT license, IndexShare 架构 2.9× FLOPs reduction, $1.4/M input $4.4/M output; API + 20+ coding environments + HuggingFace weights
- OpenRouter snapshot 2026-06-22: 340 models, 64 Chinese-brand; 本 profile 用的 minimax/minimax-m3 = $0.30/M input
- HN: "Migrate from OpenClaw" 120↑/101c on 6/18 = v0.17.0 引发的迁移潮
- Memory: `0221670e`

## 7. 每 profile 升级建议清单

### 7.1 chief-agent
- **P1**: 加 "loop-engineering-mandate" — 强制 builder ≠ judge,跨 profile verification loop
- 草稿: `soul-proposals/2026-06-22/chief-agent-loop-engineering-mandate.md`

### 7.2 pm-orchestrator
- **P1**: 加 "mcp-ema-adoption" — MCP 授权走 EMA 优先 / well-known server discovery / Tasks extension handle 模式
- 草稿: `soul-proposals/2026-06-22/pm-orchestrator-mcp-ema-adoption.md`

### 7.3 dev-worker
- **P2**: 加 "glm-5.2-fallback" — 三轴 cost-arbitrage fallback 链 (主 / grok / GLM-5.2 / DeepSeek V4 Pro)
- 草稿: `soul-proposals/2026-06-22/dev-worker-glm-5.2-fallback.md`

### 7.4 qa-worker
- **P1**: 加 "external-verifier-mandate" — cross-vendor + cross-context 强制,5 维度 rubric,reward hacking 自检
- 草稿: `soul-proposals/2026-06-22/qa-worker-external-verifier-mandate.md`

### 7.5 default
- **P0**: 加 "redact-followup" — 数据流净化层(rephrasing layer / pre-commit secret 自检 / `#50514` JSON secret 折叠盲点)
- 草稿: `soul-proposals/2026-06-22/default-redact-followup.md`

## 8. SOUL 草稿(链接到 GitHub repo)
1. chief-agent / loop-engineering-mandate (P1, 0.82)
2. pm-orchestrator / mcp-ema-adoption (P1, 0.78)
3. dev-worker / glm-5.2-fallback (P2, 0.71)
4. qa-worker / external-verifier-mandate (P1, 0.79)
5. default / redact-followup (P0, 0.86)

## 9. 跨 profile 影响图
→ `cron-output/2026-06-22/impact-graph.md` (8 行依赖链 + 3 关键冲突点 + 4 待用户裁决)

## 10. 自我审计结果
→ `docs/audit/2026-06-22.md` (inaugural baseline,signal density 高,8 路共 30+ 命中)

## 11. 立即处置项(P0/P1 影响我环境)
- **#50514** (redaction JSON secret 折叠盲点, open 2026-06-22): researcher profile web scraping 路径必踩,默认 profile SOUL redact 章节紧迫
- **MCP 2026-07-28 final 7/28 ship**: 距今 5 周,所有 MCP 长跑 polling task 必须迁 Tasks extension
- **EMA IDP second wave 未到**: 当前只 Okta,企业部署等 IDP 扩

## 12. 下一步建议
- 用户 review 8 个 SOUL/skill 草稿 → ✅/❌/✏️
- chief/user 决定是否 commit 5 条 MCP memory (pending_review)
- 用户 IT 团队拍 EMA 时间窗
- 明日 tick2 起进入正常 7 日累计采纳率观测模式

## 三通道交付清单
- [x] **GitHub push**: commit `d0b0ea9`,main branch 已同步 5 SOUL + 3 skill + impact-graph + audit
- [x] **MCP memory propose**: 5 条 pending_review (memory_id 见 §1-§6)
- [x] **飞书卡片**: 实时 P0 卡片即将送 oc_c653562b (researcher v2 流程)

---