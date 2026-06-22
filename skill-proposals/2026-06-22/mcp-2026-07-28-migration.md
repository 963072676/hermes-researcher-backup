---
name: mcp-2026-07-28-migration
description: Hermes 环境迁移到 MCP 2026-07-28 spec 的清单 + 探针 + 兼容层。重点: stateless core / MCP Apps / Tasks extension / EMA / well-known server discovery。Use when: 任何 MCP server upgrade 决策 / 配置 cross-app access / 评估现有 MCP server 是否兼容新 spec。
---

# MCP 2026-07-28 Migration(2026-06-22)

> MCP 2026-07-28 RC 是"自发布以来最大 revision"(官方)。stateless core + extensions framework + formal deprecation policy。最终 spec 2026-07-28 ship,SDK maintainers 10 周窗口验证。Tier 1 SDKs 在窗口内 ship 支持。

## 何时调用

1. **判定条件**
   - 用户要求升级 MCP server / client
   - 配置 cross-app access(EMA via Okta XAA)
   - 长跑 MCP 调用准备迁移到 Tasks extension
   - 评估当前 MCP server 是否受 `tasks/list` 移除影响
   - 想用 MCP Apps(server-rendered UI)

2. **不调用场景**
   - 纯 read-only use existing MCP server
   - 个人 toy project, 不在乎 deprecation

## 关键 breaking changes(必须知道)

### 1. Stateless Core
- **不再需要**: sticky sessions / shared session store / 深度包检
- **可以**: 部署在 round-robin load balancer 后面
- **路由**: 基于 `Mcp-Method` header
- **缓存**: `tools/list` 响应可缓存 `ttlMs` 时长

### 2. Tasks Extension(SEP-1865 类似但独立)
- **新模式**: server 回答 `tools/call` 用 task handle,client 用 `tasks/get` / `tasks/update` / `tasks/cancel`
- **关键变化**: `tasks/list` 被**移除**(无法安全 scope)
- **影响**: 长跑 polling 全部要改 handle 模式

### 3. MCP Apps(SEP-1865)
- server-rendered UI:servers ship HTML, hosts 在 sandboxed iframe render
- tools 预先 declare UI templates,hosts 可 prefetch/cache/security-review
- rendered UI → host 通信走同一 JSON-RPC,所有 UI 触发的 action 走同一 audit/consent 路径

### 4. EMA (Enterprise-Managed Authorization)
- 2026-06-18 stable
- 客户端: Anthropic Claude/Claude Code/Cowork + Microsoft VS Code
- IDP: Okta(首个,XAA / ID-JAG)
- Server 端 launch: Asana/Atlassian/Canva/Figma/Granola/Linear/Supabase;Slack 滚动支持
- **效果**: IT admin 一次配置 → 全 team MCP server access,无需每个员工单独授权

### 5. Well-Known Server Discovery
- 通过 `/.well-known/mcp-server` URL 自动发现 MCP server
- 配合 server discovery, crawler / browser / agent 可自动加 MCP endpoint

### 6. Formal Deprecation Policy
- 协议演进不再"破存量",明确 deprecation timeline
- 实施者可基于 `2026-07-28` build 知道所 ship 会持续工作

## 标准流程(6 步)

### Step 1: Inventory Current MCP Servers
```bash
# 列当前 MCP server
cat ~/.hermes/config.yaml | grep -A5 mcp_servers
mcp_project_memory_memory_list_documents
```
评估每条:用 sticky session?有 polling?走 individual auth?

### Step 2: Compatibility Probe
- 每个 server 跑 `mcp_research_inspect_paper` 风格 probe
- 查 release notes / changelog 是否声明 `2026-07-28` support
- 标 tier1/tier2/tier3 (Tier 1 = 主要 maintainer 已 ship SDK support)

### Step 3: Migration Priority Matrix
| 场景 | 优先级 | 行动 |
|---|---|---|
| 长跑 polling task | P0 | 立即迁 Tasks extension |
| 个人多 server OAuth | P1 | 6-9 月内迁 EMA |
| 部署 stateless infra | P1 | 7/28 后切换 LB + cache |
| 用 well-known discovery | P2 | browser 集成时启用 |
| 用 MCP Apps | P3 | 内部 admin tool 优先 |

### Step 4: Backward Compat Layer
- `tasks/list` 移除后,旧 client 用 `tasks/get` 逐个查 — 注意 rate limit
- `tools/list` 缓存前必须 verify ttlMs 字段
- 跨 IDP EMA 暂只 Okta,其他 IDP 等 second wave

### Step 5: Validation Tests
```yaml
test_scenarios:
  - load_balancer_round_robin:
      expect: stateless server 通过 plain LB, sticky session 移除后仍 work
  - tasks_extension_handle:
      expect: server 返回 task handle,client GET /tasks/{id} 拿到结果
  - ema_sso_flow:
      expect: 用户登录一次 IdP,所有 EMA-enabled server 无需再授权
  - well_known_discovery:
      expect: curl https://example.com/.well-known/mcp-server 返回 manifest
  - mcp_apps_iframe:
      expect: host 渲染 server-supplied HTML sandbox,UI 触发 action 走 audit
```

### Step 6: Rollout
- 7/28 final spec → sandbox first → 1 周后 production
- 准备 rollback 到 pre-2026-07-28 (semver pin `<2026.7.28`)

## 反模式
- ❌ 等到 7/28 最后一刻才迁(10 周窗口是给 SDK implementer 的,production 部署需要更多)
- ❌ 用 `tasks/list` polling (已移除)
- ❌ 假设所有 server 立即支持 EMA(只有 launch list 7 家)
- ❌ 忽略 `ttlMs` 缓存策略(stale `tools/list` 后果严重)

## 验证清单
- [ ] Inventory 完整 (所有 current MCP servers 列清)
- [ ] Compatibility probe 每个 server 都跑过
- [ ] Priority matrix 用户已确认
- [ ] Backward compat layer ready
- [ ] Validation tests pass 5/5
- [ ] Rollout + rollback plan 都有

## 参考
- https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/
- https://www.techtimes.com/articles/318708/20260619/mcp-enterprise-authorization-goes-stable-zero-touch-sso-okta-anthropic-vs-code.htm
- https://github.com/modelcontextprotocol/python-sdk/releases/tag/v2.0.0a2