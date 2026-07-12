# MCP propose receipts — tick34 / 2026-07-13

Namespace / project context: `gc-hermes-researcher`
Mode: **propose only**；未调用 commit。
Endpoint probe: `http://127.0.0.1:18080`，OpenAPI 包含 `/memory/propose_write`。

## Probe

- Probe memory: `7a78a608-7b9d-46fd-b699-f123e9ef80b3`
- Propose result: `active`（session/debug trace）
- HTTP `/memory/delete` 返回 403，因为 context role 不是 privileged；改 privileged context 后 endpoint 对 Redis-backed item 返回 404（endpoint 只处理 DB memory）。
- 最终通过 Redis container 的 authenticated `HDEL` 清理并用 `HEXISTS=0` 回读确认。
- **Cleanup verified: deleted=1, exists_after=0**。

## P0/P1 proposals

| # | memory_id | status | confidence | 内容类型 |
|---|---|---|---|---|
| 1 | `02095e06-92ed-4ea5-8b2d-4f94187f2a84` | pending_review | 1.0 | F9 factual P1 cluster |
| 2 | `57d7ae84-54e5-4cc1-9d67-2268de752ff4` | pending_review | 0.75 | F9 six-invariant recommendation |
| 3 | `a583c22a-215b-407d-8066-ba086bd505a2` | pending_review | 1.0 | config migration + Desktop artifact facts |
| 4 | `970dcdf1-4a6c-4da2-8f87-d8dcd29e06c0` | pending_review | 0.75 | MCP 2026-07-28 readiness recommendation |

## Validation

- 4/4 HTTP 200。
- 4/4 `data.status=pending_review`，按 canonical private persistent path 视为 propose 成功。
- 未调用 `/memory/commit`。
- Full-content payload first try accepted；未触发 restricted-content rejection。
