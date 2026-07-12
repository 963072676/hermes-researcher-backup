# SOUL 草稿：default — upgrade freeze + MCP 2026-07-28 readiness（tick34）

> Target: `default` profile
> Risk: P1
> Sources: GH #62723 #61798 #62171 #60685；MCP draft changelog / release candidate
> Draft only；不改生产 config/cron。

## 建议卡片

**本机状态**：Hermes v0.18.0 local，latest tag v0.18.2，main ahead 1094 commits。当前升级面新增三条红线：v30→v32 multi-profile migration 可删除平台配置（#62723）、npm 12 可留下不完整 Desktop artifact（#61798/#62171）、exact pin downgrade 仍 open（#60685）。因此继续禁止 unattended update。

同时 MCP 2026-07-28 final 还有 15 天：协议删除 handshake/session header，新增 `server/discover`、标准 headers、cache hints、issuer/resource binding，并弃用旧 HTTP+SSE。default 应进入 read-only readiness 阶段，不做生产切换。

## Before

```md
### Upgrade redline
- 不自动运行 hermes update。
- 等关键 P1 修复。
```

## After（可粘贴）

```md
### Upgrade redline v5 — snapshot, migrate, verify, then switch

以下任一条件存在时，禁止 unattended `hermes update`：
- multi-profile config migration 尚未通过 platforms roundtrip；
- package manager lifecycle policy 可能跳过 native build；
- exact dependency pin 可能回退已修版本；
- gateway readiness 只验证 PID，不验证 adapter/API/heartbeat。

允许升级必须按四阶段：
1. **Snapshot**：default + 所有 profile 的 config / platform key manifest / gateway readiness baseline；
2. **Offline migrate**：在临时副本跑 config migration 与 desktop package build；
3. **Runtime verify**：QA v4 18 gate 全过；
4. **Switch + rollback**：切换后回读所有 profile platform 数量与 gateway readiness，失败立即回滚。

### MCP 2026-07-28 readiness（read-only）

在 final 前只做 probe / conformance，不切生产：
- 双时代协商：legacy 默认，modern 显式 opt-in；
- 支持 `server/discover`；
- 校验标准 header 与 body 一致；
- list/read cache 默认 `private`，未知 policy 不共享；
- OAuth response issuer 与 recorded issuer 精确匹配；
- resource audience binding；
- HTTP+SSE 标记 deprecated，迁移 Streamable HTTP；
- tool schema depth / validation time 有界。
```

## 影响

- default/chief/dev/pm/qa 均受 upgrade gate 约束。
- 只写草稿，不执行 update、不改生产 config、不切 MCP protocol。
