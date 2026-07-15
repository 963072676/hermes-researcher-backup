---
name: hermes-mcp-2026-07-28-final-readiness-v1
description: '验证 Hermes 在 MCP 2026-07-28 final spec ship (12 days 后) 后的兼容矩阵。覆盖 6 影响 SEP (SEP-2575/2567/2243/2260+2322/2164 + 6 auth SEPs)。Use when: 评估 MCP SDK upgrade window、运行 server/discover 探针、验证 Mcp-Method/Mcp-Name headers、error code -32602 兼容、auth issuer binding。'
version: 1.0.0
created_by: researcher
metadata:
  hermes:
    tags: [mcp, release-readiness, protocol-migration, final-spec, trust-boundary]
---

# Hermes MCP 2026-07-28 Final Readiness v1

## 目标

在 2026-07-28 MCP final spec ship 之前, 建立完整的兼容性矩阵验证流程。6 个核心 SEP 影响 Hermes 的 default profile 行为, 必须 ship 前 12 天内验证 + ship 后 7 天内再次验证。

## 触发条件

- 任何 MCP server / client SDK 升级前
- WAF / reverse proxy / firewall rule 变更前 (Mcp-* headers)
- 任何 release_verification_v7 跑 MCP supply chain control 时
- 任何 -32002 / -32602 error code 异常触发时
- 任何 MCP server auth 失败时

## 6 SEP 必读

| SEP | 主题 | 影响 |
|---|---|---|
| **SEP-2575** | initialize/initialized handshake removed | server/discover 探针 + auto mode fallback |
| **SEP-2567** | Mcp-Session-Id header removed | 所有 request self-contained, 无 server-side session state |
| **SEP-2243** | Mcp-Method + Mcp-Name headers mandatory | WAF/proxy 必须放行, 拒绝 header/body 不一致 |
| **SEP-2260 + SEP-2322** | long-lived SSE removed, Multi-Round-Trip Requests | InputRequiredResult + requestState, 工具必须单 request 内完成 |
| **SEP-2164** | resource-not-found error code 32002 → 32602 | JSON-RPC standard -32602 Invalid Params |
| **6 auth SEPs (2468, 837, 2352, 2207, 2350, 2351)** | iss validation, application_type, issuer binding, scope accumulation | RFC 9207 iss validation + DCR application_type + resource migration re-register |

## 不变量

1. server/discover 探针在 connection 上 1 次 probe, 不与 initialize 冲突
2. Mcp-Method / Mcp-Name headers 与 JSON-RPC body 一致性 server 必须强制
3. WAF / proxy / CDN 路径必查 `Mcp-*` headers pass-through (不被 strip / block)
4. 每个 tool call 必须单 request 内完成, 不依赖 push SSE
5. 多轮交互用 InputRequiredResult + requestState echo
6. -32002 全部迁移到 -32602
7. RFC 9728 protected-resource metadata 必发, `authServerUrls` 稳定
8. audience-bound token 必校验, issuer 变化强制 re-register

## 标准流程

### Step 1: env 探活

```bash
# dev: ~/.hermes/knowledge-services/.env
# sync: /root/knowledge-services-sync/envs/memory_service/.env
grep -E "MEMORY_SERVICE|MCP" /root/knowledge-services-sync/envs/memory_service/.env
curl -s -o /tmp/mcp_health.txt http://localhost:18080/healthz
```

### Step 2: openapi 拉取

```bash
curl -s -o /tmp/mcp_openapi.json http://localhost:18080/openapi.json
python3 -c "import json; print(list(json.load(open('/tmp/mcp_openapi.json'))['paths'].keys()))"
```

### Step 3: version negotiation probe

```python
# 模拟 server/discover probe
import urllib.request
req = urllib.request.Request(
    "http://localhost:18080/server/discover",
    headers={"Mcp-Method": "server/discover", "Mcp-Name": "default"},
    method="POST",
)
resp = urllib.request.urlopen(req, timeout=10)
data = json.loads(resp.read())
print(data.get("supportedVersions"))
print(data.get("serverCapabilities"))
```

### Step 4: header/body consistency check

```python
# Mcp-Method != body.method 必须 reject
req = urllib.request.Request(
    "http://localhost:18080/tools/call",
    headers={"Mcp-Method": "tools/list", "Mcp-Name": "default"},
    data=json.dumps({"method": "tools/call", "params": {"name": "memory_search"}}).encode(),
)
# expected: 400 -32020 HeaderMismatch
```

### Step 5: error code -32602 verify

```python
# 资源不存在应返回 -32602 而不是 -32002
req = urllib.request.Request(
    "http://localhost:18080/resources/read",
    headers={"Mcp-Method": "resources/read", "Mcp-Name": "default"},
    data=json.dumps({"uri": "contextnest://nonexistent"}).encode(),
)
# expected: -32602 Invalid Params (JSON-RPC standard)
```

### Step 6: auth issuer binding

```python
# iss parameter 必校验 per RFC 9207
req = urllib.request.Request(
    "http://localhost:18080/oauth/authorize",
    data=json.dumps({"iss": "https://expected-issuer.example", "client_id": "..."}).encode(),
)
# expected: 200 + DCR application_type declared
```

### Step 7: InputRequiredResult multi-round-trip

```python
# 模拟需要 client input 的 server request
resp = send_tool_call("user_input_tool", {"prompt": "need approval"})
assert resp["result"]["type"] == "inputRequired"
assert "requestState" in resp["result"]

# client 回 round-trip
resp2 = send_tool_call(
    "user_input_tool",
    {"approval": "yes", "requestState": resp["result"]["requestState"]},
)
assert resp2["result"]["type"] == "completed"
```

### Step 8: WAF / proxy pass-through verify

```bash
# 验证 CDN / WAF / proxy / load balancer 不 strip Mcp-* headers
curl -v -X POST http://localhost:18080/tools/call \
  -H "Mcp-Method: tools/call" \
  -H "Mcp-Name: default" \
  -H "Content-Type: application/json" \
  -d '{"method":"tools/call","params":{"name":"memory_search"}}' \
  2>&1 | grep -i "Mcp-"
# expected: Mcp-* headers appear in received request
```

### Step 9: subscription/listen 验证 (替代 list_changed)

```python
# 2026-07-28 后, list_changed 改为 subscriptions/listen stream
req = urllib.request.Request(
    "http://localhost:18080/subscriptions/listen",
    headers={"Mcp-Method": "subscriptions/listen", "Mcp-Name": "default"},
    data=json.dumps({"filter": {"tools": True, "prompts": False, "resources": False}}).encode(),
)
# expected: stream of {toolsChanged, promptsChanged, resourcesChanged, resourceUpdated}
```

## Acceptance contract

```yaml
mcp_2026_07_28_readiness:
  version_negotiation:
    server_discover_supported: required_boolean
    auto_mode_fallback_works: required_boolean
    legacy_initialize_fallback_works: required_boolean
  headers:
    mcp_method_required: required_boolean
    mcp_name_required: required_boolean
    header_body_consistency_enforced: required_boolean
  error_codes:
    resource_not_found_returns_32602: required_boolean
    header_mismatch_returns_32020: required_boolean
    protocol_version_unsupported_returns_32022: required_boolean
  auth:
    iss_validation_per_rfc_9207: required_boolean
    dcr_application_type_declared: required_boolean
    audience_bound_token_validation: required_boolean
    issuer_binding_stable: required_boolean
  transport:
    long_lived_sse_removed: required_boolean
    input_required_result_works: required_boolean
    request_state_echo_works: required_boolean
    subscriptions_listen_works: required_boolean
  infrastructure:
    waf_proxy_pass_through_mcp_headers: required_boolean
    cdn_lb_pass_through_mcp_headers: required_boolean
    firewall_allow_mcp_headers: required_boolean
```

## 失败判定

- server/discover probe 不返回 supportedVersions
- Mcp-Method / Mcp-Name header 缺失或不一致不返回 -32020
- 资源不存在仍返回 -32002 而不是 -32602
- iss validation 缺失 / DCR application_type 缺失 / audience-bound token 不验
- long-lived SSE 仍可工作 (合规视角视为失败)
- WAF/proxy/CDN strip Mcp-* headers (env 端 fail)
- subscriptions/listen 不返回 stream

## 证据

- 官方 RC: <https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/>
- 官方 SDK beta: <https://blog.modelcontextprotocol.io/posts/sdk-betas-2026-07-28/>
- Migration guide: <https://mcpmigrate.dev/blog/mcp-spec-2026-07-28-migration-guide>
- TS SDK migration: <https://github.com/modelcontextprotocol/typescript-sdk/blob/main/docs/migration/support-2026-07-28.md>
- GitHub RC: <https://github.com/modelcontextprotocol/modelcontextprotocol/releases/tag/2026-07-28-RC>
- tick33 立卡 MCP supply chain 6-control
- tick35 立卡 MCP 2026-07-28 readiness (default profile branch-only exact pin)
- tick36 立卡 MCP auth 6 SEP path correction
- arxiv 2606.29073 HCP handle-capability protocol reference runtime (8 invariants)
- arxiv 2602.14281 MCPShield security cognition layer (lifecycle defense-in-depth)

## Pitfalls

- SEP-2575 + SEP-2567 同时 ship, core 协议层 stateless 化, 任何 session-keyed state 必须 externalize
- SEP-2243 是 infrastructure-level, 不是 SDK-level, WAF/proxy strip = silent fail
- SEP-2260/2322: server-side push 完全废止, 必须用 InputRequiredResult multi-round-trip
- SEP-2164: -32002 → -32602 测试套件全量更新, 别 hard-code 旧值
- 6 auth SEPs: issuer change 强制 re-register 所有 client, 不是 optional
- TS SDK migration: Hand-constructed `Server` 默认不 ship 2026-07-28 on wire, 必须 opt-in `versionNegotiation`
- Python SDK: aiohttp / starlette / fastapi 等 framework 必检查 Mcp-* header pass-through
- 本 default profile 维持 stable SDK, 仅 test branch exact-pin beta
- production release 等 hermes-agent official MCP 2026-07-28 SDK 升级后再评估