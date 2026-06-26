---
name: arxiv-agent-security-monitor
description: 每周二 02:00 UTC 拉 arxiv cs.MA + cs.AI 近 7 天论文, 过滤关键词 "agent security / prompt injection / instruction bleed / semantic early stopping / LLM agent loop / sandbox escape", 命中后写入 researcher 命名空间 memory。Use when: researcher tick 跑前需要 arxiv 增量, 或 chief-agent 派工时需要 paper 引用。
---

# arxiv Agent Security Monitor

## 何时调用
- 每周二 02:00 UTC, 与 arxiv 论文 release 节奏对齐
- 任何 researcher 跑 SOUL 自评前
- chief-agent 派工时若 task 含 "AI agent 安全 / 沙箱 / alignment"

## 标准流程
1. **拉数据**
   ```bash
   curl -sS "https://export.arxiv.org/api/query?search_query=cat:cs.MA+AND+(abs:agent+security+OR+abs:prompt+injection+OR+abs:instruction+bleed+OR+abs:sandbox+escape)&max_results=10&sortBy=submittedDate&sortOrder=descending" -o /tmp/arxiv.xml
   ```
2. **解析** — Python `re.findall` 抽 title/abstract/sha/authors
3. **去重** — sha in seen (researcher namespace memory, key=`arxiv_sha:<sha>`)
4. **判定 relevance** — 命中关键词词频 ≥ 2, 或 title 含上述关键词
5. **MCP 写入** — researcher profile `mcp_project_memory_memory_propose_write`
   - memory_type: `research_signal` (或新增 `arxiv_paper`)
   - suggested_scope: `private`
   - confidence: 0.6-0.85
   - source: `arxiv.org/abs/<sha>`
6. **digest 报告** — 命中数 + top 3 title + arxiv URL, 写到本次 researcher tick digest

## 失败回退
- arxiv 5xx → retry 1 次, 再 fail 则跳过本周
- MCP 403/422 → 走 HTTP fallback (X-Admin-Token), 写明 degraded
- web_search (exa) 不在 cron 工具集 → 永远不依赖 web_search, 直接 curl arxiv

## 验证
- 命中 arxiv sha 与 memory_search 命中一致
- digest 包含 sha 链接
- 下周可观察到 sha 出现 (确保滚动窗口)
