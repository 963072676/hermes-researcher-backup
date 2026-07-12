# SOUL 草稿：qa — release verification v4（tick34）

> Target: `qa` profile
> Risk: P1
> Sources: GH #62723 #61798/#62171/#62462/#62564 #63309 #63243 #62365/#63008/#63128/#63129/#63207；MCP draft 2026-07-28
> Draft only。

## 建议卡片

v3 的 10 项 ship gate 仍不足：它能抓 merge marker、import、JSON 和 silent delivery，却抓不到“迁移后 config 少一段”“artifact 有 stamp 但 native payload 缺失”“gateway process 绿但 adapter 未 ready”“摘要产生无来源用户请求”。升级为 v4：**静态检查 + runtime readback + state invariant + protocol conformance**。

## Before

```md
### release verification v3
- 6 grep checks
- 4 silent-fail scenarios
- 10 项全过才 ship
```

## After（可粘贴）

```md
### release verification v4

保留 v3 10 项，并新增 8 个 runtime gate：

1. **Config migration roundtrip**：default + 9 profiles，migration 前后 `platforms` key set 与非空字段计数一致。
2. **Backup restore drill**：每个 profile 的 config 迁移失败可从 snapshot 恢复，并回读 hash。
3. **Desktop artifact completeness**：packaged executable + content stamp + required native payload 三者同时成立；payload 非 0 byte 且 Electron smoke test 可 load。
4. **Gateway readiness**：process spawned 不算 ready；adapter connected + API listener + heartbeat 三信号齐全才通过。
5. **Session provenance**：compaction summary 的 pending/user asks 必须映射原 message_id。
6. **Session concurrency**：lock error、prune check error、WS observer disconnect 三种失败注入不改变 canonical live session。
7. **Recovery dedup**：Telegram post-reconnect probe 与 heartbeat 同时失败时，最多一个 recovery task。
8. **MCP dual-era conformance**：legacy 2025 + opt-in 2026-07-28；验证 `server/discover`、header/body mismatch reject、cacheScope private、auth issuer/resource binding。

任一 runtime gate 失败：禁止 tag；若 emergency skip，必须 24h 内补跑并把结果附到 release notes。
```

## 判定

- #62723 证明 schema parse 成功不等于 config data preserved。
- #61798/#62564 证明 build success + matching stamp 不等于 artifact complete。
- #63309 证明 systemd running 不等于 Telegram ready。
- F9 证明 session row 存在不等于历史可恢复且无 fork。
