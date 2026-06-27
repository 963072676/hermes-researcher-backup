# 跨 profile 影响图 (2026-06-28)

**Tick**: tick19 · **Source**: GH scan (2026-06-25 ~ 2026-06-28 UTC) + HN Algolia + OpenRouter + arxiv

## 核心触发链

| 触发 | 直接影响 | 隐含影响 | 风险 | 处理 |
|---|---|---|---|---|
| **GH #53715** P1 terminal secret leak (open 2026-06-27) | dev / qa / researcher / default 4 profile 全用 terminal tool, 均受 `AUXILIARY_*_API_KEY` / `GATEWAY_RELAY_SECRET` 泄漏影响 | chief 必须暂停所有跑 terminal 的 cron (含 hermes-self-evolution-digest + researcher self-evolution), 等 PR #53715 merge | **P1 security** | SOUL → dev + qa (起草), skill → secret-leak-pre-check (起草) |
| **GH #53667** P1 tool loader v0.17.0 collapse (open 2026-06-27) | default (fresh install) + 所有 cron 工具集依赖 web/terminal/file 的 profile | chief daily report 受影响 (无 web search 跑不动) + digest 完全失效 | **P1 functional** | SOUL → default (起草), skill → hermes-tool-loader-sanity (起草) |
| **GH #53697** P2 telegram streaming bypass (open 2026-06-27) | chief / default (feishu 不受影响, 但 global streaming master switch 设计 bug) | 任何加 telegram 平台的 profile 都受影响; feishu 当前不受影响, 但若未来加 config 同步会触发 | **P2 awareness** | chief daily 报用户, 不起草 SOUL |
| **GH #53676** P2 MCP HTTP transport 400 handshake (open 2026-06-27) | default / researcher 走 MCP tool 调用 | researcher tick 已知有 HTTP urllib fallback; default cron 工具集裁剪走 MCP 也受影响 | **P2 awareness + 监控升级到 P1** | digest mention, 不起草 SOUL; 等 v0.17.x patch |
| **HN Show HN: Skillmaxxing** (2pts 2026-06-26) | researcher self-evolution 这条路径本身 | 若社区形成 skill self-evolution 标准, 可反哺 researcher skill 草稿模板 | **awareness** | 不起草, 监控 |
| **OpenRouter 91/339 Chinese models** (27%, 2026-06-28 snapshot) | default profile 已用 minimax/minimax-m3, 路由验证 | 中国模型价格优势继续扩大, 默认 model 决策 external anchor 强化 | **awareness** | digest mention |

## 关键依赖链 (3-hop)

1. **#53715** (terminal secret leak) → dev/qa SOUL 加 pre-check → researcher self-evolution
   tick 也加 pre-check (因为跑 `terminal` 工具) → chief 暂停所有 terminal 依赖 cron
2. **#53667** (tool loader collapse) → default 加 sentinel 自检 → chief daily 报用户 → 触发
   用户级 v0.17.1 / v0.16.1 回滚决策
3. **#53715 + #53667** 同时存在 → 即使走 fallback 路径 (Python urllib + read_file/write_file)
   仍然有 #53715 secret leak 风险, **必须**先解决 #53715 再考虑 #53667 fallback

## 阻塞现状

- researcher tick19 自身在 **risk zone**: 用 terminal 跑 curl, child process 可能泄漏 AUXILIARY secret
- 当前 mitigation: skill 草稿 `secret-leak-pre-check` 已起草, 但 **未部署到 default/researcher SOUL**
- 用户决策点: 是否在 PR #53715 merge 前手动合并 SOUL 草稿到 dev/qa SOUL.md (低风险, 文本护栏)

## 跨 profile skill 调用图

```
researcher (C 档)  ──→ secret-leak-pre-check ──→ dev + qa + default + chief
researcher (C 档)  ──→ hermes-tool-loader-sanity ──→ default (主) + chief (日检)
researcher (C 档)  ──→ cron-output-backup-sentinel ──→ qa (主) + default + researcher (自身)
chief (P 档)       ──→ P1 triage matrix ──→ 5 profile 全
dev (P 档)         ──→ secret-leak-pre-check inline ──→ terminal 子进程
qa (P 档)          ──→ cron-output-backup-sentinel + secret-leak-pre-check
default (C 档)     ──→ hermes-tool-loader-sanity + secret-leak-pre-check
```
