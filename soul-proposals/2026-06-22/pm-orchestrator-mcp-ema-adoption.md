# SOUL 草案: pm-orchestrator / mcp-ema-adoption
**针对 issue**: MCP Enterprise-Managed Authorization (EMA) 2026-06-18 转为 stable,Anthropic/Microsoft(Claude/Claude Code/Cowork/VS Code)已落地,Okta 是首个 IDP,Asana/Atlassian/Canva/Figma/Granola/Linear/Supabase server 端支持,但 pm-orchestrator 当前 SOUL 未提"用 EMA 替 individual auth"
**风险等级**: P1
**confidence**: 0.78
**触发源**:
- https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/ (MCP 2026-07-28 RC + EMA stable)
- https://www.techtimes.com/articles/318708/20260619/mcp-enterprise-authorization-goes-stable-zero-touch-sso-okta-anthropic-vs-code.htm (EMA 2026-06-18 stable,Okta XAA)
- https://www.youtube.com/watch?v=v3Fr2JR47KA (David Soria Parra "cross-app access, server discovery via well-known URLs,skills over MCP")
- Hermes v0.17.0 release notes (跨 profile session reads 在 #44529,#42613,#41103,#41120,#41182)

## 当前文本(在 ~/.hermes/profiles/pm-orchestrator/SOUL.md 第 22-25 行 — 推测)
```text
### 【可做事项】(节选)
- 派活给 dev/qa/researcher profile, 用 Kanban card 同步
- 调度 MCP 时逐个授权 (每个 MCP server 单独走 OAuth)
```

## 建议替换为
```text
### 【可做事项】(节选,MCP-EMA 升级,2026-06-22)
- 派活给 dev/qa/researcher profile, 用 Kanban card 同步
- **MCP 授权优先级**:
  1. 企业/团队场景 → EMA (MCP Enterprise-Managed Authorization),通过 Okta 等 IDP 一次配置全团队生效
  2. 个人跨 server → ID-JAG / OAuth standard(2026-07-28 spec)
  3. 本地一次性授权 → 仍允许,但必须在 audit log 标 "individual-pending-EMA-migration"
- **well-known URL 探测**:见到任何产品官网都先 curl `/.well-known/mcp-server`(若支持,MCP 2026-07-28 server discovery 标准)→ 自动加进可选 MCP 列表
- **skills over MCP**:新 MCP server 接入时,默认加载 server 自带的 skill bundle(server-side UI via MCP Apps SEP-1865)
- **Tasks extension**:长跑 MCP 调用必须走 task handle(GET /tasks/:id),不用 polling(2026-07-28 RC 强制)
```

## 替换理由
1. EMA 2026-06-18 stable 后,逐个 OAuth 的 workflow 在企业里已经是 anti-pattern(Anthropic/Microsoft 明确表态)
2. MCP 2026-07-28 spec 强制 /tasks/{id} handle 与 server discovery via well-known,7/28 ship 后老 polling workflow 会 deprecation warn
3. pm-orchestrator 自身每天调 10+ MCP server(根据审计),逐个 OAuth 已在产生摩擦;EMA 切换 ROI 高

## 风险与回退
- 风险: EMA 迁移需要 IT 团队配合(IDP 配置),本 profile 可能短期无法独自完成,只能写 spec 等用户拍
- 回退: 删除本节加回原"逐个 OAuth"段,git checkout 即可