# Impact Graph — tick45 (2026-07-24)

> Release: v0.19.0, 71.4h after publish，仍在 72h window。
> Family registry: 11 families + F12 candidate；无新 family。
> Cross-cluster arrows: tick44 累计 21 + tick45 NEW 4 = 25。

## NEW arrows

| arrow_id | from | to | severity | 交互 | 证据 |
|---|---|---|---|---|---|
| CCA-F7-F11-approval-view-byte-mismatch | F7 MCP supply chain | F11 approval unification | A | 审批视图 bytes 与模型输入 bytes 不同，旧 approval 无法约束实际 action authority | arXiv 2607.05744 |
| CCA-F7-F9-keepalive-rpc-session-corruption | F7 MCP protocol | F9 session integrity | B | keepalive 与 active RPC 交错，可能造成 timeout / response ordering 失真 | GH #70218, PR #62811 |
| CCA-F10-F9-live-update-session-corruption | F10 installer handoff | F9 session integrity | A | dirty-tree / live-venv 热更新可让运行时和 session store 进入不一致 generation | GH #70211, #70201, #70185 |
| CCA-F9-F1-desktop-failure-retry-misdelivery | F9 session integrity | F1 silent fail | A | provider failure后 prompt 恢复到 stale session，原 session 无响应、错误 surface 收到回复 | GH #68358, #70221 |

## Dependency chain

```text
External MCP metadata
  -> canonical bytes + digest
  -> approval render (same bytes)
  -> consent receipt
  -> model context
  -> digest mutation check
  -> re-consent before dispatch

Updater
  -> install-kind detection
  -> dirty-tree gate
  -> live-holder gate (all OS)
  -> isolated staged generation
  -> verification
  -> atomic switch + restart
  -> rollback pointer

Provider failure
  -> origin session receipt
  -> retry exhausted
  -> origin-bound composer recovery
  -> explicit fallback choice
  -> no stale-session delivery
```

## 5 profile impact

| profile | 必须升级 |
|---|---|
| chief | tier-1.5 arbitration for F7/F11 and F10/F9 |
| pm | 29-field acceptance v13，增加 approval_view_fidelity + runtime_update_coherence |
| dev | invariant implementations：metadata digest、RPC lock、staged runtime、origin receipt |
| qa | ship gate 80 + 8 = 88 checks，4 个 forbidden skip |
| default | 禁 unattended update；MCP digest change re-consent；origin-bound recovery |

## Family anti-inflation

- F9 Desktop 四症状属于既有 session-state-integrity expansion。
- F10 update coherence 属于 installer-handoff expansion。
- arXiv 2607.05744 加强 F7/F11/F12 candidate，但未验证 F12 condition_1，因此不升 family。
