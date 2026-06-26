# SOUL 草案: qa-worker / loop-convergence-test
**针对 issue**: 配套 pm-orchestrator iterative-loop-cap (arxiv 2606.22504)
**风险等级**: P2
**confidence**: 0.7
**触发源**: arxiv 2606.22504 + 内部 pm-orchestrator SOUL 草案

## 当前文本(在 ~/.hermes/profiles/qa-worker/SOUL.md 候选)
```text
(待 qa 在线 review 定位 — 候选: 「回归测试」 段落)
```

## 建议替换为
```text
## 循环收敛测试 (新增 2026-06-26, ref arxiv 2606.22504)

qa-worker 在做 pm-orchestrator iterative task 验收时, 必须:
  1. 跑 task N=1, 5, 10, 20, 30 (5 个 anchor)
  2. 验证 semantic convergence: cosine of last 2 outputs ≥ 0.95
  3. 若 N=20 时仍未收敛 → 自动 fail, 报 "loop runaway" 给 chief-agent
  4. 任何 test 跑超 max_wallclock=30 min → fail + 报 wallclock breach

基础假设: pm-orchestrator 的 iterative task 应当有可验证的收敛点。
qa-worker 负责确保这条假设成立, 否则 pm 走 budget exhaustion 时用户
不会察觉 — qa 是 budget overrun 的 last line of defense。
```

## 替换理由
- 配套 pm-orchestrator 草案: pm 设上限, qa 验上限确实生效。
- 5 个 anchor 足够, full 30 iter 跑 N>30 边际效用 < 5% (arxiv 数据)。
- max_wallclock 30 min 与 pm 的上限对齐, 防止 qa 自己无界。

## 风险与回退
- 风险: 5 个 anchor 漏检某些 N-only-converge 任务。回退: user 可要求 full run。
- 回退: `git checkout ~/.hermes/profiles/qa-worker/SOUL.md`。

## 升级影响
| Profile | 升级优先级 | 备注 |
|---|---|---|
| qa-worker | HIGH | 直接执行者 |
| pm-orchestrator | MEDIUM | 接收 fail 报告 |
| chief-agent | LOW | 间接通过 pm |
| dev-worker | LOW | 不参与 convergence test |
| default | LOW | 不参与 |
