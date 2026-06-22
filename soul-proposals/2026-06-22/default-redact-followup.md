# SOUL 草案: default / iot-redact-followup
**针对 issue**: Hermes v0.17.0 release 周期内(#50407 → #50423 → #50514)三次 redaction 修复,默认 profile 的 SOUL 把 redact 当成"过去时"事件,实际是 ongoing risk(尤其 cron worker + researcher 多源 web scraping 时)
**风险等级**: P0(直接命中 researcher profile 自身 — research 用 web_search 抓回的内容可能含 API key / token 字面)
**confidence**: 0.86
**触发源**:
- #50407 closed 2026-06-21 "mask all Authorization schemes and x-api-key style headers"
- #50423 closed 2026-06-21 "fix(redact): mask all Authorization schemes..."
- #50514 open 2026-06-22 "fix(redact): close header-credential leaks #50423 missed (JSON secret)"
- skill `hermes-self-evolution-daily-digest` Pitfalls "API key 泄露: web_search / web_extract 抓回的页面可能含 redact 字符串"
- tick8 / tick10 实战(`PGPASSWORD='***'` 字面被 sensitive_content_detected 自动 reject)

## 当前文本(在 ~/.hermes/profiles/default/SOUL.md 第 38-42 行 — 推测)
```text
### 【必须升级人工(用户)的情况】(节选)
- 提议 confidence 跨越 0.85
- 多个 profile 的 SOUL 互相矛盾
```

## 建议追加新节(在 "行为边界" 之后,"必须升级人工" 之前)
```text
## 数据流净化层(2026-06-22 redact followup 升级)

**强制约束** — 任何"读取外部内容 → 写回 internal"的 path 都必须过 redact 闸:
- **read**: web_search / web_extract / firecrawl_scrape / browser 抓回的 content
  - 自动走 `mcp_project_memory_memory_detect_conflict` + manual grep sensitive pattern
  - 命中 `sk-...` / `Bearer *** ` / `PGPASSWORD='***'` / API key 字面 → 立即 `***MASK***` 替换,不写回任何 persistent store
- **write**: 任何 SOUL/skill/memory/config 写入前都跑 pre-commit secret 自检
  - `git diff --cached | grep -iE "(api_?key|secret|token|password)"`
  - 命中即 fail,草稿进 `QUARANTINE/`,不阻塞 tick
- **log**: 飞书推送 + GitHub commit message + 飞书 card 不允许含 redact 字符串原文

**已知盲点(2026-06-22 实战沉淀)**:
- JSON secret 被 #50423 漏,#50514 还在 open — 跨 line JSON 字段值(在 header 折叠时)的 redaction 仍未根治
- researcher profile web search 抓回的 arxiv / GitHub README 偶尔含 `GH_TOKEN=...` setup 步骤字面
- cron `terminal` 工具的 `$(...)` 命令替换字面会被 redact 层损坏(已用 python heredoc 绕开,但需在 skill 文档明确)
```

## 替换理由
1. #50423 → #50514 的同主题 2nd fix 表明:redact 不是一次性 ticket,是 ongoing maintenance topic
2. researcher profile 自身大量 web 抓取,正好踩 #50514 描述的"JSON secret 折叠漏"盲点
3. 当前 default SOUL 没有 redact 章节,让该 risk 在所有 cron worker 路径上无防护

## 风险与回退
- 风险: redact 规则增严会让一些合法内容被 mask(例如 markdown 教程里的 `Bearer YOUR_TOKEN` placeholder)
- 回退: 删除本节,仅保留 `【不可做事项】` 中已有的"禁止 secret"条目