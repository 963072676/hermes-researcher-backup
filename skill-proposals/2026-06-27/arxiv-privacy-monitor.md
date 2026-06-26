---
name: arxiv-privacy-monitor
description: 周二 02:00 UTC 自动扫 arxiv cs.CR + cs.MA 关于 LLM agent privacy / data leakage / memorization 的新论文。Use when: researcher 需要每周跟踪 agent privacy 趋势,而不依赖人工刷 arxiv。
---

# arxiv-privacy-monitor

## 何时调用
- 每周二 02:00 UTC 自动触发(researcher cron 调度)
- 当 user 提到 "agent privacy" / "PII in LLM" / "memorization attack" / "training data extraction" 时手工调用
- 当其他 skill (如 `ai-agent-security-defense`) 命中 privacy topic 时联动调用

## 标准流程

### Step 1: arxiv 扫描
```bash
# 5 个独立 query (防止漏检)
curl -sL 'https://export.arxiv.org/api/query?search_query=abs:%22LLM+agent+privacy%22&start=0&max_results=15&sortBy=submittedDate&sortOrder=descending' -o /tmp/arxiv_p1.xml
curl -sL 'https://export.arxiv.org/api/query?search_query=abs:%22training+data+extraction%22+OR+abs:%22memorization+attack%22&start=0&max_results=10' -o /tmp/arxiv_p2.xml
curl -sL 'https://export.arxiv.org/api/query?search_query=abs:%22agent+data+leakage%22+OR+abs:%22PII+LLM%22&start=0&max_results=10' -o /tmp/arxiv_p3.xml
curl -sL 'https://export.arxiv.org/api/query?search_query=abs:%22memory+poisoning+agent%22+OR+abs:%22agent+side+channel%22&start=0&max_results=10' -o /tmp/arxiv_p4.xml
curl -sL 'https://export.arxiv.org/api/query?cat:cs.CR&start=0&max_results=20&sortBy=submittedDate' -o /tmp/arxiv_p5.xml
```

### Step 2: 去重 + 优先级分类
```python
# Per skill tick-execution-recipe.md §3 — 朴素直查 3-tier dedup
# Classify each hit:
#   - new_attack_vector → P1 propose (must write SOUL draft)
#   - defense_mechanism → P2 propose (配 SOUL upgrade for dev-worker)
#   - survey → P3 (internalize in researcher's own cadence)
#   - unrelated → skip
```

### Step 3: 产出 3 件套
1. **memory propose**: 1 条 `memory_type=platform_api` 或 `system_design`,
   `confidence=1.0`(paper 是事实)/ 0.75(影响判断)
2. **SOUL 草案**: 跨 profile 影响最大者写 1 段 draft (e.g. dev-worker-memory-privacy-redact)
3. **飞书 DM 摘要**: ≤ 100 字,送 `oc_c653562b`

### Step 4: 联动
- 联动 skill: `ai-agent-security-defense` (命中 defense paper 时)
- 不联动 skill: `arxiv-agent-security-monitor` (太宽泛,避免重复扫描)

## 何时不该调用
- 非周二 + user 未明确要求 → 不要手工触发 (会撞 researcher cron weekly cadence)
- arxiv API 5xx → 跳过本周,下次 cron 自动 retry
- 已存在的 baseline paper (dedup 命中) → 跳过

## 验证
- [ ] 周二 02:00 UTC cron 自动触发,产出 1 memory + 1 SOUL draft + 1 飞书 DM
- [ ] 5 路 arxiv query 全部返回 200
- [ ] dedup 命中 baseline 的 paper 不进 propose
- [ ] P1 attack vector 走强信号, P3 survey 走弱信号
- [ ] 飞书 DM 摘要字数 ≤ 100

## 关联
- 上游 skill: `self-driven-cron-execution` (umbrella)
- 平行 skill: `arxiv-agent-security-monitor` (cs.MA 通用,本 skill 是 privacy-focused 子集)
- 下游 skill: `ai-agent-security-defense` (联动消费 P2 defense)
- 主 SOUL: `researcher-privacy-survey-weekly-cadence`