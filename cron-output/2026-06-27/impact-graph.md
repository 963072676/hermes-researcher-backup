# 跨 profile 影响图 (2026-06-27)

> tick18 researcher。触发源 = GH PR #53183 (gateway zombie fix) + arxiv 2606.26627 (agent privacy survey) + 续接 tick17 (2606.22504 iterative cap)。

| 触发 | 直接影响 | 隐含影响 | 风险 | 处理 |
|---|---|---|---|---|
| chief-agent 接受 SOUL `gateway-zombie-exorcism` (P1) | chief 派工前置 healthz check, zombie 时立即停派 + restart | dev 长任务遇 zombie 时被 kill, pm 派工不会因 zombie 而 fail | P1 | 待 chief role commit |
| chief 接受 zombie-exorcism → qa 必须能验 PR #53183 | qa-worker 加 `gateway-zombie-repro-test` 配套 (P2) | 200 长 response 模拟 + /new 切换, 验 zombie 复现率 = 0 | P2 | 待 qa role commit |
| pm-orchestrator 接受 SOUL `iterative-loop-cap-extension` (P2) | 卡片必填 cap + wall_clock + cosine, 默认 N≤10 | dev 收到 cap 后跑 loop, qa 配套验收敛 | P2 | 待 pm role commit |
| pm 接受 cap extension → qa 必须能验 cosine | qa-worker 加 `loop-convergence-test` (sibling of tick17) | 5 anchor 跑 N=1,5,10,20,30, cosine ≥ 0.95 验收敛 | P2 | 待 qa role commit |
| dev-worker 接受 SOUL `memory-privacy-redact` (P1) | pre-commit hook 扫 secret 字面 + 自动替换 | sandbox 越权路径被堵, qa 测 redact 是否生效 | P1 | 待 dev role commit |
| researcher 加 `privacy-survey-weekly-cadence` | 每周二扫 arxiv cs.CR/cs.MA privacy topic | chief 派工时论文引用不缺; dev 接受 dev SOUL 升级 | P2 | 待 researcher role commit |
| researcher 接受 cadence → dev 配套 redact | researcher 出的 attack → dev SOUL 自动升级 (中长期) | qa 复现 attack vector 验证 defense | P3 | 中长期, 无需本次 commit |
| **跨 5-profile 关联**: zombie detect + cap + privacy = 3 SOUL 互相依赖 | **3 profile 联动**, 单独改任一会导致不一致 | 全 5 profile 同时更新可避免"半套" | P1 风险: 错位 | **推荐同步 commit** |

## 依赖链图

```
GH PR #53183 (Gateway zombie fix)
   ↓
chief-agent SOUL zombie-exorcism
   ↓ (依赖)
qa-worker SOUL zombie-repro-test (本次新增)

arxiv 2606.22504 (Semantic Early-Stopping)
   ↓
pm-orchestrator SOUL iterative-loop-cap-extension (本次扩展)
   ↓ (依赖)
qa-worker SOUL loop-convergence-test (tick17 已生成)

arxiv 2606.26627 (Agent Privacy Survey)
   ↓
researcher SOUL privacy-survey-weekly-cadence
   ↓ (依赖)
dev-worker SOUL memory-privacy-redact

#53107 (Gateway shutdown hang, tick17)
   ↓
chief-agent SOUL shutdown-backstop (tick17 已生成)
```

## 推荐 commit 顺序

1. **chief-agent zombie-exorcism** (P1, 最紧急, 5 profile 中最强的 P1 信号)
2. **dev-worker memory-privacy-redact** (P1, secret leak 直接危害生产)
3. **qa-worker gateway-zombie-repro-test** (P2, 验证 PR #53183)
4. **pm-orchestrator iterative-loop-cap-extension** (P2, 续接 tick17)
5. **researcher privacy-survey-weekly-cadence** (P2, 续接 tick17)

不要先 commit qa, 因为依赖 chief zombie 和 pm cap。

## 本 tick 相比 tick17 的增量

| 维度 | tick17 (2026-06-26) | tick18 (2026-06-27) |
|---|---|---|
| 触发源数 | 3 (1 GH issue + 2 arxiv) | 4 (1 PR + 1 issue + 2 arxiv) |
| SOUL 草案数 | 5 | 5 (续接 + 新增) |
| 新增 P1 SOUL | chief-agent shutdown-backstop | chief-agent zombie-exorcism + dev-worker privacy-redact |
| Skill 草案 | 3 (arxiv monitor + loop detector + issue triage) | 3 (arxiv-privacy + audit-cli + zombie-detector) |
| MCP propose | 3 (pending) | 3 (新增, pending) |
| GH push | OK (a93c8e3 + 843cb64 + fda2fe0) | 本 tick 尝试 push |
| 采纳率 | 0% (user 仍未 ack tick17) | 待 user ack tick17+tick18 |

## 跨 tick 累积影响

researcher 累积 13 SOUL 草稿 (5+5+3 from tick22/26/27), 9 skill 草稿 (3+3+3).
**采纳率 0% (4 天连续)** — 6/29 强制降频触发 (按 skill contract).