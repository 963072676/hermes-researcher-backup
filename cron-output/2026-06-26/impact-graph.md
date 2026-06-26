# 跨 profile 影响图 (2026-06-26)

> tick17 researcher。触发源 = arxiv 2606.22504 (Semantic Early-Stopping) + arxiv 2606.22417 (Instruction Bleed) + GH #53107 (Gateway shutdown hang)。

| 触发 | 直接影响 | 隐含影响 | 风险 | 处理 |
|---|---|---|---|---|
| chief-agent 接受 SOUL `gateway-shutdown-backstop` (P1) | cron 派工链路 gateway 在 ≤ 5s 内 exit | dev-worker 长任务遇 graceful shutdown 时不再 hang, pm 派工不再因 gateway hang 而 fail | P1 | 待 chief role commit |
| pm-orchestrator 接受 SOUL `iterative-loop-cap` (P2) | 编排 refinement 时设 hard cap N=20, max_wall=30min | dev-worker 收到 "改 5 次" 任务时不再无限跑, budget 守恒 | P2 | 待 pm role commit |
| pm 接受 iterative cap → qa 必须能验 | qa-worker 加 `loop-convergence-test` 配套 (P2) | 5 anchor 跑 N=1,5,10,20,30, cosine ≥ 0.95 验收敛 | P2 | 待 qa role commit |
| dev-worker 接受 SOUL `instruction-bleed-defense` (P2) | 子进程工具调用前检查 cross-module 关键词 | sandbox 越权路径被堵, qa 需复现 attack vector 验证 | P2 | 待 dev role commit |
| researcher 加 arxiv weekly cadence | 每周二 02:00 UTC 拉 arxiv 10 篇 | chief-agent 派工时论文引用不再缺; pm 编排时引用 "收敛" 论文 | P2 | 待 researcher role commit |
| **跨 5-profile 关联**: pm cap → qa 验 → dev 配合 (defense) | **3 profile 联动**, 单独改任一会导致不一致 | 全 5 profile 同时更新可避免"半套" | P1 风险: 错位 | 推荐同步 commit |

## 依赖链图

```
arxiv 2606.22504 (Semantic Early-Stopping)
   ↓
pm-orchestrator SOUL cap
   ↓ (依赖)
qa-worker SOUL convergence test
   
arxiv 2606.22417 (Instruction Bleed)
   ↓
dev-worker SOUL defense
   ↓ (依赖)
qa-worker SOUL attack reproduction test (本次未生成, 优先级 P3)

GH #53107 (Gateway hang)
   ↓
chief-agent SOUL shutdown backstop
   ↓ (依赖)
pm + dev + default 隐含, 因为他们 cron 走 gateway
```

## 推荐 commit 顺序

1. chief-agent shutdown backstop (P1, 最紧急)
2. dev-worker instruction bleed defense (P2, 安全)
3. pm-orchestrator iterative cap (P2, 行为)
4. qa-worker convergence test (P2, 配套 pm)
5. researcher arxiv cadence (P2, 自身)

不要先 commit qa, 因为依赖 pm。
