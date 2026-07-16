# Cross-Profile Impact Graph + Cross-Cluster Arrows (tick38, 2026-07-16)

> 配套 cron: hermes-researcher-deep-tick-daily
> tick38 立卡时间: 2026-07-16 18:00 UTC
> 沿用:tick35 cross-cluster arrows protocol + tick37 4 arrows + tick38 F11 NEW family 立卡
> 来源:tick38 chief + pm + dev + qa + default 5 SOUL 草稿 + 11 family registry

## 1. 11 family registry (tick38 立卡 + 沿用)

| # | family | sweeper marker | 立卡 tick | 状态 |
|---|---|---|---|---|
| 1 | silent-fail | `sweeper:risk-silent-fail` | tick27 | expansion (#64574+#64552 merged tick37) |
| 2 | cross-platform-state | `sweeper:risk-cross-platform-state` | tick28 | stable |
| 3 | memory-injection-cross-platform | `sweeper:risk-memory-injection-platform-gateway` | tick31 | stable |
| 4 | credential-pool-stale-snapshot | `sweeper:risk-credential-pool-stale` | tick31 | expansion |
| 5 | cron-session-leak-closed-state | `sweeper:risk-cron-session-leak` | tick32 | maintenance |
| 6 | outbound-redact-call-site | `sweeper:risk-outbound-redact-call-site` | tick32 | maintenance |
| 7 | MCP-supply-chain-protocol-migration | `sweeper:risk-mcp-supply-chain-6-control` → v2 9-control | tick32/33 | expansion (readiness v2 立卡 tick38) |
| 8 | cron-ticker-resilience-deck | `sweeper:risk-cron-ticker-resilience` | tick33 | expansion |
| 9 | session-state-integrity-deck | `sweeper:risk-session-state-integrity` | tick34 | expansion |
| 10 | cron-installer-handoff-state | `sweeper:risk-installer-handoff-state` | tick35 | expansion |
| **11** | **execute-code-approval-unification-deck** | **`sweeper:risk-execute-code-approval-unification`** | **tick38** | **emerging** (NEW F11) |

## 2. tick38 cross-cluster arrows (5 NEW + 4 沿用 = 9 total)

### 2.1 NEW arrows (tick38 立卡, F11-driven)

| arrow_id | from_family | to_family | severity | interaction |
|---|---|---|---|---|
| **CCA-E1** | **F11** execute-code-approval-unification | F7 MCP-supply-chain-protocol-migration | **severity-B** | F11 Invariant 4 (tool description sanitization) 共享 F7 control 4 + control 6;F11 instantiate MCP server 须过 F7 readiness v2 9-control (沿用) |
| **CCA-E2** | **F11** execute-code-approval-unification | F8 cron-ticker-resilience-deck | **severity-C** | F11 kanban-spawned session 走 execute_code 路径可触发 EXT14 crash → STDIO transport 异常 → BaseException escape → F8 ticker silent die 模式 |
| **CCA-E3** | **F11** execute-code-approval-unification | F10 cron-installer-handoff-state | **severity-C** | F11 execute_code RPC upgrade 必须 verify F10 setup.py pin (#60685 redline) 不被 execute_code 绕过;`pip install hermes-agent` 走的 shell 不走 execute_code path |
| **CCA-E4** | **F11** execute-code-approval-unification | F9 session-state-integrity-deck | **severity-C** | F11 autonomous_session_flag 与 F9 session ownership provenance 共享"no-human-approver"概念;F9 supervisor ownership invariant 应 extend 含 autonomous flag |
| **CCA-E5** | **F7** MCP-supply-chain-protocol-migration (readiness v2) | **F11** execute-code-approval-unification | **severity-B** | F7 readiness v2 9-control 中 control 8+9 (version pin + tool spawn analyzer) 是 F11 Invariant 6 pre-commit release gate 的子集;F7 readiness v2 必须升级含 F11 9-control preflight |

### 2.2 沿用 arrows (tick37 → tick38)

| arrow_id | from_family | to_family | severity | interaction | 沿用 |
|---|---|---|---|---|---|
| CCA-1 | F9 #64934 concurrent turn | F1 silent-fail | severity-A | durable transcript 错位 + repair_message_sequence | tick35 |
| CCA-2 | F9 #64778 launchd orphan | F1 silent-fail | severity-B | config 变更不再触发 reload | tick35 |
| CCA-3 | F10 #64590 install-tree | F1 silent-fail | severity-B | agent_init 把 contributor guide 当 prompt | tick35 |
| CCA-4 | F9 #64593 merged fix | F1 silent-fail | severity-C | 本机 v0.18.0 未升级 | tick35 |

## 3. 跨 profile 影响链 (tick38)

### 3.1 F11 execute-code-approval 跨 profile 影响

| Profile | F11 影响 | 必须 verify |
|---|---|---|
| **chief** | 6 invariant + PR-dedup 6h SLA | chief 决策 primary PR (#60077 vs #60799) |
| **pm** | 17-field v5 → 19-field v6 acceptance contract | 升级 f11_invariants_verify + autonomous_session_flag_audit |
| **dev** | tools/approval.py + tools/code_execution_tool.py + core/audit.py + core/supply_chain.py 4 file 修改 | per-call guard + VCS deny + autonomous flag + audit log |
| **qa** | ship gate v7 → v8 (76-check) + dangerous_command_unified_classify 4 项 | 5 install profile verify + 9-control preflight |
| **default** | MCP 2026-07-28 readiness v1 → v2 (9-control) + EXT14 shield + CVE-2026-61459/59950 | countdown 12d tracking |

### 3.2 跨 profile dependency chain

```
F11 chief 立卡 (6 invariant + PR-dedup 6h SLA)
    ↓
F11 pm 升级 19-field v6 acceptance
    ↓
F11 dev 4 file 修改 (approval.py + code_execution_tool.py + audit.py + supply_chain.py)
    ↓
F11 qa ship gate v8 76-check + dangerous_command_unified_classify
    ↓
F11 default MCP readiness v2 9-control
    ↓
2026-07-28 final spec release readiness
```

## 4. severity 评估 (tick38 立卡)

### 4.1 CCA-E1 severity-B 评估
- **from_family_fix_side_effect_directly_worsens**: NO (F11 fix 不会加重 F7)
- **from_family_fix_requires_to_family_fix_to_complete**: YES (F11 Invariant 4 依赖 F7 control 4+6;F11 readiness v2 control 8+9 是 F7 readiness v2 子集)
- **结论**: severity-B — chief 24h joint review

### 4.2 CCA-E2 severity-C 评估
- **from_family_fix_side_effect_directly_worsens**: NO (F11 fix 不会直接触发 F8 silent die)
- **from_family_fix_requires_to_family_fix_to_complete**: NO (F11 + F8 是独立 fix,但协同防御)
- **结论**: severity-C — 进 daily report

### 4.3 CCA-E3 severity-C 评估
- **from_family_fix_side_effect_directly_worsens**: NO
- **from_family_fix_requires_to_family_fix_to_complete**: NO
- **结论**: severity-C — 进 daily report

### 4.4 CCA-E4 severity-C 评估
- **from_family_fix_side_effect_directly_worsens**: NO
- **from_family_fix_requires_to_family_fix_to_complete**: NO (F9 supervisor ownership 与 F11 autonomous flag 概念共享但实现独立)
- **结论**: severity-C — 进 daily report

### 4.5 CCA-E5 severity-B 评估
- **from_family_fix_side_effect_directly_worsens**: NO
- **from_family_fix_requires_to_family_fix_to_complete**: YES (F7 readiness v2 必须 extend 含 F11 9-control)
- **结论**: severity-B — chief 24h joint review

## 5. severity-A 检查 (tick38)

**当前 tick38 severity-A arrows**: 0
- tick35 有 CCA-1 (severity-A F9→F5) — 沿用,无新增
- tick38 F11 立卡本身 severity=emerging (family_lifecycle 5 段),但 cross-cluster arrows 全部 ≤ severity-B

**判定**:tick38 无新 severity-A 升级,**chief 6h SLA 不强制要求 F11**。但 F11 PR-dedup fire (#60077 + #60799) 仍触发 chief 6h dedup SLA(沿用 tick27 立卡)。

## 6. family_lifecycle 状态 (tick38)

| Family | lifecycle | tick38 变化 |
|---|---|---|
| F1 silent-fail | expansion | 无变化(沿用 tick37 #64574+#64552 merged) |
| F2 cross-platform-state | stable | 无变化 |
| F3 memory-injection-cross-platform | stable | 无变化 |
| F4 credential-pool-stale-snapshot | expansion | 无变化 |
| F5 cron-session-leak-closed-state | maintenance | 无变化 |
| F6 outbound-redact-call-site | maintenance | 无变化 |
| F7 MCP-supply-chain-protocol-migration | expansion → **expansion (readiness v2)** | **tick38 立卡 9-control (6 + EXT14 + version pin + tool spawn analyzer)** |
| F8 cron-ticker-resilience-deck | expansion | 无变化 |
| F9 session-state-integrity-deck | expansion | 无变化 |
| F10 cron-installer-handoff-state | expansion | 无变化 |
| **F11 execute-code-approval-unification-deck** | **emerging (NEW)** | **tick38 立卡 (#60056 + #60077 + #60799 + #24942 + #57890)** |

## 7. family 命名 3 段式 (沿用 tick34 立卡)

| # | family name | 3 段式解析 | sweeper marker 3 段式 |
|---|---|---|---|
| 11 | execute-code-approval-unification-deck | `execute-code` (root cause) + `approval` (affected scope) + `unification-deck` (modifier: 6 invariant + cross-cluster) | `sweeper:risk-execute-code-approval-unification` |

**family 命名禁词检查**:
- ❌ `family-11` (编号)
- ❌ `execute-code-bug` (模糊)
- ❌ `#60056-family` (单 issue)
- ✅ `execute-code-approval-unification-deck` (3 段式 + 反映 root cause + scope + modifier)

## 8. cross-cluster arrow 命名 3 段式 (沿用 tick35)

| arrow_id | 3 段式解析 |
|---|---|
| CCA-E1 | `F11` (from) + `F7` (to) + `tool-desc-sanitize-share` (interaction) |
| CCA-E2 | `F11` + `F8` + `execute-code-ticker-die` (interaction) |
| CCA-E3 | `F11` + `F10` + `setup-pin-bypass-verify` (interaction) |
| CCA-E4 | `F11` + `F9` + `autonomous-flag-share` (interaction) |
| CCA-E5 | `F7` + `F11` + `readiness-v2-preflight-extend` (interaction) |

**arrow 命名禁词检查**:
- ❌ `arrow-1` / `arrow-2` (编号)
- ✅ `F11-F7-tool-desc-sanitize-share` (3 段式 + from + to + interaction)

## 9. 飞书推送 (tick38 impact-graph)

```
[Cross-Profile Impact Graph tick38]
F11 execute-code-approval-unification-deck 立卡 (emerging)
5 cross-cluster arrows: CCA-E1/E2/E3/E4/E5 (2 severity-B + 3 severity-C)
CCA-E1 (F11→F7 severity-B): tool description sanitization 共享
CCA-E2 (F11→F8 severity-C): execute-code 触发 EXT14 → ticker die
CCA-E3 (F11→F10 severity-C): setup.py pin 不被 execute_code 绕过
CCA-E4 (F11→F9 severity-C): autonomous_session_flag 共享 ownership
CCA-E5 (F7→F11 severity-B): readiness v2 9-control extend F11
severity-A: 0 (F11 自身 PR-dedup 仍触发 chief 6h dedup)
5 profile dependency chain: chief → pm → dev → qa → default
```

## 10. 关联 reference

- `tick35 SOUL_chief_draft_cross_cluster_arrows_v1.md` (沿用)
- `tick35 SOUL_default_draft_trust_boundary_5_categories_v1.md` (沿用)
- `tick36 F11 anti-inflation criteria` (沿用)
- `tick37 4 cross-cluster arrows baseline` (沿用)
- `tick38 SOUL_chief_draft_execute_code_approval_unification_v1.md` (NEW)
- `tick38 SOUL_default_draft_mcp_readiness_v2_ext14_cve_2026.md` (NEW)