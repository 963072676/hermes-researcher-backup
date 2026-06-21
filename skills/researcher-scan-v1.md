---
name: researcher-scan
description: |
  researcher profile 专属。跨 5 类互联网信号扫描(Hermes 官方 / Claude Code 生态 / Loop Engineering / MCP / AI agent 安全),
  基于现有 hermes-self-evolution-digest 的扫描流水线,扩展"对每个 profile 的影响分析"。
  ONLY for researcher profile;其他 profile 不会加载。
trigger: |
  - 用户说"扫互联网信号"/"调研 Hermes 最新进展"/"查 Claude Code 更新"
  - cron hermes-self-evolution-digest tick 触发后,researcher 接手拆 profile
  - chief 派"调研 X 主题"任务
---

# Researcher · 跨 Profile 信号扫描

## 目标
把 hermes-self-evolution-digest 的"单条信号摘要"升级为"对每个 profile 的能力影响矩阵"。

## 输入
- `~/.hermes/cron/output/hermes-self-evolution-digest/digest/<date>.md` — 今日 digest
- `~/.hermes/cron/output/hermes-self-evolution-digest/hits/<date>.jsonl` — 今日 hits(含 URL + title + summary)
- `~/.hermes/cron/output/hermes-self-evolution-digest/dedup/seen_urls.json` — 历史 baseline

## 5 类扫描域
1. **Hermes 官方**:`github.com/NousResearch/hermes-agent` releases + PRs + issues
2. **Claude Code 生态**:`code.claude.com/docs` + `claude.com/blog` + `/goal` `/loop` hooks 进展
3. **Loop Engineering / 多 Agent**:Addy Osmani + Boris Cherny + Peter Steinberger
4. **MCP 协议**:`modelcontextprotocol.io` + `github.com/modelcontextprotocol`
5. **AI Agent 安全**:Hermes docs security + 上游 P0/P1 issues + tirith 类审批器

## 输出格式
对每个命中,产出:
```yaml
- url: <hit URL>
  hit_time: <首次发现时间>
  domain: hermes|claude_code|loop_engineering|mcp|ai_safety
  severity: P0|P1|P2|info
  affected_profiles: [chief-agent, dev-worker, ...]
  impact_summary: 一句话影响
  propose_memory: true|false
  confidence: 0.0-1.0
```

## 复用现有 pipeline
不要重新发明扫描器。直接读 hermes-self-evolution-digest 今日产物:
```bash
DIGEST=$(ls -t ~/.hermes/cron/output/hermes-self-evolution-digest/digest/ | head -1)
cat ~/.hermes/cron/output/hermes-self-evolution-digest/digest/"$DIGEST"
```
然后用 LLM 把每条命中分类到 5 个 profile 的影响矩阵。

## Pitfall
- **去重**:每条 URL 已在 seen_urls.json baseline 中,先 grep 判 first_seen 才算新信号
- **profile 影响**:不是所有信号都影响所有 profile
- **confidence 校准**:已合并 PR ≥ 0.85;博客文章 ≤ 0.6;X/Twitter ≤ 0.4
- **P0 信号必须 escalate**:即使 confidence 不到 0.85,P0 安全问题也必须 propose + 飞书紧急卡片