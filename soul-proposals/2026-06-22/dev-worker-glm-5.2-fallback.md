# SOUL 草案: dev-worker / glm-5.2-fallback
**针对 issue**: 2026-06-16 GLM-5.2 发布,753B params、1M context、MIT license、$1.4/M input $4.4/M output(OpenRouter 上 $1.0/M) — 比当前 dev-worker 用的 fallback 便宜 5-10× 且长程任务更强;但 dev-worker SOUL 仍把 Anthropic Sonnet 当 fallback,没考虑中国开源模型作为 cost-arbitrage 第二轴
**风险等级**: P2(不影响马上生产,但错过 5× cost saving 窗口)
**confidence**: 0.71
**触发源**:
- https://z.ai/blog/glm-5.2 (官方, IndexShare 架构,2.9× per-token FLOPs reduction at 1M)
- https://venturebeat.com/technology/z-ais-open-weights-glm-5-2-beats-gpt-5-5-on-multiple-long-horizon-coding-benchmarks-for-1-6th-the-cost
- https://simonwillison.net/2026/May/28/claude-opus-4-8/ (Opus 4.8 是 modest improvement,价格仍 $5/$25)
- OpenRouter 价格快照 2026-06-22:GLM-5.2 $1.0/M,Opus 4.8 $5/M,DeepSeek-V4-Pro $0.435/M

## 当前文本(在 ~/.hermes/profiles/dev-worker/SOUL.md 第 8-12 行 — 推测)
```text
## 模型
- 主: minimax-cn/MiniMax-M3
- fallback: xai-oauth/grok-4.3
- 二级 fallback: (未配置)
```

## 建议替换为
```text
## 模型(2026-06-22 三轴 cost-arbitrage 升级)
- 主: minimax-cn/MiniMax-M3 (中文 + 长 context 稳)
- fallback 1: xai-oauth/grok-4.3 (英文 + reasoning)
- **fallback 2 (新增): zai-org/GLM-5.2 via z-ai API 或 OpenRouter**
  - 触发条件: 单次请求 > 100K tokens 或 长程 loop > 10 turns
  - 理由: 1M solid context,MIT license 可下载微调,$1.4/M input 是 Opus 4.8 的 28%
  - **慎用**: 不用于 security-critical 代码生成(GLM-5.2 自评有偏差,参考 Autonomy Tax 论文)
- **fallback 3 (新增): deepseek-ai/DeepSeek-V4-Pro**
  - 触发条件: cost-critical 长程批量任务(参数 1.6T 但 $0.435/M)
  - 理由: 性价比 axis 极致,中文/英文均可
```

## 替换理由
1. 当前 fallback 在 cost 长程任务上 Opus 4.8 / Sonnet 4.6 仍是 >$3/M,GLM-5.2 $1.0/M + 1M context 让 dev-worker 能用同 budget 跑 3-5 倍 session
2. MIT license + IndexShare 2.9× FLOPs reduction 暗示自部署 ROI 高(若 user 有 GPU cluster)
3. 风险提示清楚(security-critical 不走 GLM-5.2),不是盲目切换

## 风险与回退
- 风险: GLM-5.2 是 6/16 新发,benchmark 数据仍不全面,踩坑概率 > 30%
- 回退: 删除 fallback 2/3,保留原 fallback 1; git checkout