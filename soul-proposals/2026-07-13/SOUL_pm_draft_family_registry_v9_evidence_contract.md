# SOUL 草稿：pm — family registry v9 + evidence contract（tick34）

> Target: `pm` profile
> Risk: P1
> Draft only。

## 建议卡片

**结论**：family registry 从 8 升到 9；新增 `session-state-integrity-deck`。今天另有 3 个独立高风险 cluster：config migration data loss、Telegram reconnect/startup hangs、Linux Desktop artifact incomplete。PM 必须强制每张 P1 卡带“可复现事实 / fix PR / acceptance gate / family mapping”，避免只按 issue 数量排序。

## Before

```md
### P1 family acceptance
- family name 使用三段式。
- 关联 sweeper marker、skill、impact graph、memory。
```

## After（可粘贴）

```md
### P1 family acceptance v9

每条 P1 proposal 必须包含 7 字段：
1. `family_name`：`<root-cause>-<affected-scope>[-modifier]`；
2. `evidence_ids`：issue / PR / official spec URL；
3. `reproduction_scope`：受影响 profile / platform / release；
4. `invariants`：至少 3 条可机器验证的不变量；
5. `primary_fix`：主 PR；若候选 ≥3，标记 chief 6h dedup；
6. `ship_gate`：失败注入 + artifact/readback 验证；
7. `memory_id`：researcher propose 回执。

family registry v9 新增：
- `session-state-integrity-deck`
- marker: `sweeper:risk-session-state-integrity`
- evidence: GH #62365 #63008 #63128 #63129 #63207

单个 issue 不新建 family；但同一 session state 链跨 compaction / lock / prune / surface ownership ≥3 层时立即立卡。
```

## 本 tick proposal routing

| Proposal | Family | Owner | Acceptance |
|---|---|---|---|
| Session state integrity | F9 NEW | chief + dev + qa | 6 invariant |
| Config migration preserves platforms | F2 cross-platform-state extension | default + qa | 10/10 profile roundtrip |
| Telegram reconnect finite-state | F1 silent-fail extension | dev + qa | bounded connect/reconnect |
| Desktop artifact completeness | installer-recurrence extension | qa | runtime binary readback |
| MCP 2026-07-28 readiness | F7 protocol migration | default + qa | dual-era conformance |
