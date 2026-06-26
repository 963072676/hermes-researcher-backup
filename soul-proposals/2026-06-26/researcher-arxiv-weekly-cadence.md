# SOUL 草案: researcher / arxiv-weekly-cadence
**针对 issue**: 当前 researcher 每日 tick 走 web_search (exa) + GitHub API, **没在跑 arxiv 轮询** — 跨周会漏掉新论文
**风险等级**: P2
**confidence**: 0.7
**触发源**: SOUL v2 自评 — 当前 tick 漏掉 2 篇直接相关论文 (2606.22504 + 2606.22417), 是因为 web_search 覆盖了 arxiv 但没 query 词

## 当前文本(在 ~/.hermes/profiles/researcher/SOUL.md 第 36 行附近 — 「扫互联网信号 (扩展)」)
```text
  - **arxiv cs.MA / cs.AI 新论文(每周二)**(v2 新增)
```

## 建议替换为
```text
  - **arxiv cs.MA / cs.AI 新论文(每周二 02:00 UTC)**(v2 新增)
    - query 词: agent security, prompt injection, instruction bleed,
               semantic early stopping, LLM agent loop, sandbox escape,
               autonomous agent alignment
    - 命中阈值: abs 含上述任意关键词 AND submittedDate 在过去 7 天
    - 必读: max_results=10, 不分批
    - 失败回退: arxiv API 5xx → 走 export.arxiv.org 重试 1 次 → 再 fail 则跳过本周
```

## 替换理由
- 本 tick (2026-06-26) 才发现 arxiv 2606.22504 (Semantic Early-Stopping, 2026-06-25) 和 2606.22417 (Instruction Bleed, 2026-06-24) — 都是直接相关论文, 漏了整整 1-2 天。
- 根因: web_search 没专门 query arxiv; 即使走 GitHub API 也只看 NousResearch。
- 修正: 加 arxiv cs.MA/cs.AI 专门 cron, 固定 query 词, 周二跑 (与论文 release 节奏对齐 — arxiv 周一-周二上线最多)。

## 风险与回退
- 风险: arxiv 偶发 5xx, 走 retry 后会延后本周论文采集。回退: 下周补跑即可 (arxiv 论文 7 天内不会变)。
- 回退: `git checkout ~/.hermes/profiles/researcher/SOUL.md`。

## 升级影响
| Profile | 升级优先级 | 备注 |
|---|---|---|
| researcher | HIGH | 自身节奏修补 |
| chief-agent | MEDIUM | 派工时论文 review 需进 ticket |
| pm-orchestrator | MEDIUM | 编排时引用论文结论 |
| dev-worker | LOW | 不直接消费 arxiv |
| qa-worker | LOW | 同上 |
| default | LOW | 不直接消费 |
