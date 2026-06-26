---
name: loop-runaway-detector
description: 任何 iterative LLM agent task 跑 N 轮后, 检测是否 semantic drift (cosine of consecutive outputs < 0.5) 或 收敛但被忽略 (cosine ≥ 0.95 还继续)。命中后报警给 chief-agent, 触发 early-stop。Use when: pm-orchestrator / dev-worker / qa-worker 跑 refinement loop, 或 researcher 跑 multi-round self-review。
---

# Loop Runaway Detector

## 何时调用
- 任何 agent 跑 "until X" / "iterate" / "再来一次" 路径
- 任何 tool call 出现循环 pattern (e.g. 同一函数被连续 call 5+ 次)
- cosine 监控: 每 N 轮后, 把当前 output embedding vs 上轮做 cosine
  - cosine ≥ 0.95 → 收敛, 早停
  - cosine < 0.5 → drift, 报警 (任务在乱跑)

## 标准流程
1. **监控点**
   - pm-orchestrator 编排时: 派工后每轮 collect output, cosine vs prev
   - dev-worker 单 task: 内部 tool loop 每 5 轮 check 一次
   - qa-worker 验收: 跑 task N=1, 5, 10, 20, 30 (5 anchor)
2. **判定**
   ```python
   import numpy as np
   cos = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
   if cos >= 0.95:
       action = "early_stop_converged"
   elif cos < 0.5:
       action = "alarm_drift"
   else:
       action = "continue"
   ```
3. **处置**
   - early_stop_converged → 报 caller "converged at iter N", 停止派新工
   - alarm_drift → 报 chief-agent "drift detected", 默认停 + 等 user 决定
   - continue → 走下一轮
4. **持久化** — 每次判定写一行 JSONL, 路径 `~/.hermes/state/loop-runaway/<date>.jsonl`

## 何时不该调用
- 单次 query (没循环)
- 任务明确说 "跑 100 轮" (用户显式声明)
- 嵌入计算失败 (e.g. 纯文本无 embedder)

## 验证
- 测试 fixture: 5 个 anchor cosine 输出符合论文 arxiv 2606.22504 分布
- 5 个 anchor 跑 N>20 后 cosine 显著上升 (验证 convergence signal)
- drift 报警的 false positive 率 < 10% (在 dev set 上)
