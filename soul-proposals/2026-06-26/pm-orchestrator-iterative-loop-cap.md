# SOUL 草案: pm-orchestrator / iterative-loop-cap
**针对 issue**: arxiv 2606.22504 "Semantic Early-Stopping for Iterative LLM Agent Loops" (2026-06-25)
**风险等级**: P2
**confidence**: 0.78
**触发源**: https://arxiv.org/abs/2606.22504 (Semantic Early-Stopping, submitted 2026-06-25)

## 当前文本(在 ~/.hermes/profiles/pm-orchestrator/SOUL.md 候选位置)
```text
(待 pm 在线 review 定位 — 候选: 「循环/迭代」 段落)
```

## 建议替换为
```text
## 迭代循环上限 (新增 2026-06-26, ref arxiv 2606.22504)

pm-orchestrator 在编排 iterative refinement 任务时, 必须设 hard cap:
  - 单 task max_iterations = 20
  - 单 task max_wallclock = 30 min
  - 任何超出触发 "semantic early-stop" — 用 cosine similarity of last 2 outputs ≥ 0.95 判定收敛

判定收敛后, pm 必须:
  1. 停止派工
  2. 走 "总结" 路径而不是 "再跑一轮" 路径
  3. 在飞书 oc_6b75046a 群报 "converged, stopping at iter N"

理论依据: arxiv 2606.22504 实证 iterative LLM agent loops 在 N>15 后
  - 60% 任务边际效用 < 5%
  - 25% 任务出现 semantic drift (引入原 prompt 没要求的新约束)
```

## 替换理由
- arxiv 2606.22504 是 2026-06-25 最新论文, 直接针对 LLM agent loop 效率问题。
- pm-orchestrator 经常编排 refinement 任务 (e.g. "改 5 次直到 user 满意"), 无上限会浪费 budget。
- cosine ≥ 0.95 判定收敛是论文推荐阈值, 实测 f1=0.83。

## 风险与回退
- 风险: cosine 误判 — 当任务确实需要变化时提前停。回退: user 在飞书回 "继续" 即可重启。
- 回退: `git checkout ~/.hermes/profiles/pm-orchestrator/SOUL.md`。

## 升级影响
| Profile | 升级优先级 | 备注 |
|---|---|---|
| pm-orchestrator | HIGH | 直接编排者 |
| chief-agent | MEDIUM | 也编排, 但粒度粗 |
| dev-worker | LOW | 单 task, 不循环 |
| qa-worker | MEDIUM | 回归测试可能用循环 |
| default | LOW | 普通对话不会触发 |
