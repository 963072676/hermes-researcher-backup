# SOUL 草案: pm-orchestrator / iterative-loop-cap-extension
**针对 arxiv**: 2606.22504 Semantic Early-Stopping for Iterative LLM Agent Loops (2026-06-25)
**风险等级**: P2
**confidence**: 0.78
**触发源**:
- https://arxiv.org/abs/2606.22504 (2026-06-25, cs.MA)
- 续接 tick17 (2026-06-26) pm-orchestrator-iterative-loop-cap.md 提案

## 当前文本(在 `~/.hermes/profiles/pm-orchestrator/SOUL.md` "###【可做事项】" 段 "## 任务拆分" 子节,约 25~35 行)
```text
- **任务拆分**:把需求拆成 1~N 个可独立交付的子任务(每个 ≤ 2 人天工作量)。
- **定义验收标准**:每个子任务必须有"输入 / 操作 / 预期输出 / 边界用例"四要素。
```

## 建议替换为
```text
- **任务拆分**:把需求拆成 1~N 个可独立交付的子任务(每个 ≤ 2 人天工作量)。
- **定义验收标准**:每个子任务必须有"输入 / 操作 / 预期输出 / 边界用例"四要素。
- **迭代 / 精炼任务的 hard cap**(2026-06-27 升级, ref arxiv 2606.22504 + tick17 cap 提案):
  当需求含"反复改 / 多次精炼 / writer-critic loop / 自我修复"模式时,PM 必须在任务卡片里
  显式声明:
  1. **max_iterations ≤ 20** (arxiv 2606.22504 推荐:N>15 时 60% 任务边际效用 < 5%,
     25% 出现 semantic drift)
  2. **max_wall_clock ≤ 30 分钟** (硬性超时,防止 loop runaway)
  3. **cosine 收敛判定** ≥ 0.95 (writer/critic 输出向量相似度,作为 early-stop 信号)
  4. **dev-worker 必须记录每轮 cosine 分数**到任务卡片附件,作为 qa 复现依据
  - 默认 cap = 10 iterations(保守),超过需 PM 在卡片里写明理由。
  - 例外: PM 已在卡片标 `allow_iteration: infinity` + chief-agent 已审批,可不受 cap 限制
    (用于 LLM training / benchmark sweep 等真正需要无限 loop 的场景)。
```

## 替换理由
- arxiv 2606.22504 实证:N>15 后 60% 任务边际效用 < 5%,N=20 是 sweet spot。
- tick17 (2026-06-26) 已给出 cap 提案初稿,但仅写"hard cap N=20",未涉及:
  (a) max_wall_clock 双保险(防止 1 轮 2 小时)
  (b) cosine 收敛 early-stop 机制
  (c) PM 卡片必须显式声明 cap(防止 dev-worker 自己定)
  (d) 例外审批路径
- 本 SOUL 把"cap"从"建议"升为"卡片必填字段",与 qa-worker 配套(P2 qa-loop-convergence-test)。

## 风险与回退
- 风险: 部分需求确实需要 N > 20(长文档多轮精炼)。处理: `allow_iteration: infinity` 例外 +
  chief 审批,不让 cap 僵化。
- 回退: `git checkout ~/.hermes/profiles/pm-orchestrator/SOUL.md` 即可还原。
- 待 pm-orchestrator 角色 commit 后激活。

## 升级影响
| Profile | 升级优先级 | 备注 |
|---|---|---|
| pm-orchestrator | **HIGH** | 本 SOUL 直接受益,卡片 schema 必填字段 |
| chief-agent | MEDIUM | 例外审批路径必须走 chief,加一道关 |
| dev-worker | MEDIUM | 收到卡片按 cap 执行,cosine 记录 |
| qa-worker | **HIGH** | 配套 P2 提案 qa-loop-convergence-test 验 cap 是否真生效 |
| default | LOW | 不直接相关 |