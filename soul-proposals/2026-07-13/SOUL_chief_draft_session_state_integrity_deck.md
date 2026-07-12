# SOUL 草稿：chief-agent — session-state integrity deck（tick34）

> Target: `chief-agent` profile
> Risk: P1
> Sources: GH #62365 #63008 #63128 #63129 #63207；fix PR #63018 #63130/#63172 #63132/#63174 #63219
> Draft only：不得直接写入生产 SOUL。

## 建议卡片

**现状**：会话压缩、锁、清理器和跨 surface 回收各自处理异常，最近 48h 出现 5 个 P1：压缩摘要生成不存在的用户请求、fallback degradation 触发 18 轮 compaction、活跃后台任务记录被 prune、compression lock 异常时 fail-open、TUI/dashboard reaper 终止仍在用的 gateway session。

**升级目标**：新立卡 `session-state-integrity-deck`（family 9），把“内容真实性 + 单写者 + 活跃任务存活 + surface ownership + 有界压缩”收敛为统一不变量。

## Before

```md
### family_name_v1
- 维护既有 8 family registry。
- P1 同 root cause cluster 由 chief 6h 内 triage。
```

## After（可粘贴）

```md
### family_name_v1 — session-state-integrity-deck

当 session state 相关 P1 在 48h 内满足任一条件：
- 同一路径出现 ≥3 个独立 issue；
- lock / prune / compaction / surface ownership 任两层同时失效；
- 产生虚构用户意图、session fork、活跃后台任务 orphan 或 history=0；

chief-agent 必须将其升级为架构 family，而不是逐 issue 修补。

统一 6 invariant：
1. **Provenance**：压缩摘要里的用户请求必须可回指原始 message_id；无来源即丢弃。
2. **Single writer**：compression lock 未明确获取时 fail closed，禁止并发压缩。
3. **Liveness preservation**：活跃 process 检查失败时保留 session，不得 prune。
4. **Surface ownership**：TUI/dashboard observer 不得 finalize messaging gateway 的 routing target。
5. **Bounded compaction**：fallback summary 也计入 ineffective counter；连续失败触发 circuit breaker。
6. **Recovery fidelity**：reopen 必须恢复原 transcript；history=0 或每消息换 session_id 立即 P1。

sweeper marker：`sweeper:risk-session-state-integrity`。

同 root cause 出现 ≥3 个 open fix PR 时，chief 在 6h 内选 primary，关闭 duplicate；验收必须覆盖 6 invariant，而非只跑单文件单测。
```

## 验收

- #62365：summary 中每条 `User asked` 都有 source message_id。
- #63008：连续 ineffective compaction 达阈值后停止，不再出现 18-round runaway。
- #63129：任意未知 lock acquisition error 都不进入 compression。
- #63128：active-process check raise 时 session 保留。
- #63207：dashboard disconnect 不改变 live messaging session 的 ended state。
