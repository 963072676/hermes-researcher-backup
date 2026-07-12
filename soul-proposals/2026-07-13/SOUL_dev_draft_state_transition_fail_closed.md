# SOUL 草稿：dev — state transitions fail closed（tick34）

> Target: `dev` profile
> Risk: P1
> Sources: GH #63008 #63128 #63129 #63207 #63243 #63309
> Draft only。

## 建议卡片

今天的 P1 不是“多几个 try/except”问题，而是异常路径默认继续：lock error 后继续压缩、active-process check error 后继续 prune、observer disconnect 后继续 finalize、post-reconnect probe error 后继续启动另一条 recovery。统一原则就是 **state transition fail closed + idempotent recovery**。

## Before

```md
### State mutation
- 捕获异常并记录日志。
- 尽量继续提供服务。
```

## After（可粘贴）

```md
### State mutation — fail-closed and idempotent recovery

任何会改变 session / gateway / delivery 状态的操作必须满足：

1. **Guard result 三态化**：`ALLOW / DENY / UNKNOWN`。`UNKNOWN` 不得等价于 `ALLOW`。
2. **Lock acquisition**：只有显式 true 才可进入 critical section；异常一律跳过并记录 metric。
3. **Prune**：只有明确“无活跃任务”才可删除；检查异常必须保留。
4. **Ownership check**：observer surface 不能结束另一个 surface 的 routing target。
5. **Recovery dedup**：同一 adapter 同一时刻最多 1 个 recovery task；所有 probe 都走统一 scheduler。
6. **Timeout layering**：asyncio timeout 之外必须有底层 connect timeout / thread boundary，确保 blocking call 不让 watchdog 失效。
7. **State readback**：每次 mutation 后从 canonical store 回读，验证 session_id / ended_at / history count / owner 未漂移。

实现 PR 必须至少含：happy path、guard=UNKNOWN、concurrent caller、restart/reopen 四类测试。
```

## 直接适用

- #63129 / #63132：compression lock unknown → skip。
- #63128 / #63130 / #63172：active-process check unknown → keep。
- #63207 / #63219：WS observer close 不结束 live gateway session。
- #63243 / #63247：post-reconnect probe 统一走 `_polling_error_task` dedup。
- #63309：blocking initialize 增加低层 connect timeout 与 readiness probe。
