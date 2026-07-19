# pm-agent SOUL draft — tick41 (2026-07-19)

## P1 acceptance contract v8 → v9 升级 (tick41 立卡)

**trigger**: tick41 跑 P1 acceptance 时,21-field v8 (tick40 立卡) 暴露 2 个新缺口:
1. **trust_boundary_impact** 字段没有 sub-field 区分 architectural_fix vs runtime_mitigation (F4 #25727 v0.18.0 重新打开就是 architectural_fix 与 #33233 runtime fix 分不清的典型)
2. **cross_cluster_arrows** 没有 `worsening_evidence` 子字段,F11 invariant 7 修复后是否会 worsen CCA-F11-F4 需要明示 (tick41 rule 3 PR-dedup fire 5 次的 family 联动)

**完整 v9 contract (tick41+)**:
- v8 21-field 全部保留
- tick41 NEW 2 字段:
  1. `fix_layer_audit` — 5 sub-fields: layer_design / layer_runtime / layer_config / layer_data / layer_release
  2. `worsening_evidence` — 5 sub-fields: from_family / to_family / predicted_severity / measured_severity / stop_condition

**P1 acceptance workflow (tick41)**:
- 19-field v6 → 21-field v8 → **23-field v9** (累计)
- 任何 v8 acceptance 必须补 2 NEW 字段,不接受 fallback
- `fix_layer_audit` 五层明确:design (架构层) / runtime (代码层) / config (配置层) / data (数据层) / release (release tag)
- `worsening_evidence` 用于 cross-cluster arrow 修复后 14 天内观察副作用

**P1 cluster 评估 (tick41)**:
| # | family | issue | severity | fix_layer_audit | worsening_evidence |
|---|---|---|---|---|---|
| 1 | F4 | #63425 | P1 | layer_runtime (agent_init.py) | potential CCA-F4-F11 (credential pool validation may break execute_code path) |
| 2 | F4 | #25727 | P2 | layer_runtime (recovery paths) | confirmed CCA-F4-F1 (silent failure path) |
| 3 | F9 | #66251 | P2 | layer_runtime (auxiliary_client.call_llm) | potential CCA-F9-F8 (gateway client pool reuse) |
| 4 | F9 | #62665 | P2 | layer_data (state.db metadata) | confirmed CCA-F9-F11 (parent model contamination via tool/delegate) |
| 5 | F1 | #58663 fix | P1 | layer_design (ContextVar refactor) | potential CCA-F1-F9 (reset value bug was session-state) |
| 6 | F11 | 沿用 tick38-40 | P1 | layer_runtime | confirmed CCA-F11-F7 |
| 7 | F12 | candidate + 3 arxiv | P2 | layer_design | potential CCA-F12-F11 |
| 8 | CVE | CVE-2026-61459 | CRITICAL | layer_runtime (kubectl) | potential CCA-CVE-F7 (mcp-server-k8s version pin) |

**pm 必跑 7-field P1 acceptance (沿用 tick34-40)**:
1. family_name (3 段式)
2. evidence_ids (issue / PR / commit SHA)
3. reproduction_scope (5 install profile affected)
4. invariants (≥ 6 + family-specific)
5. primary_fix (PR / commit)
6. ship_gate (90-check v11 tick41)
7. memory_id (propose receipt)
- **tick41 NEW** 8. fix_layer_audit (5 layer classification)
- **tick41 NEW** 9. worsening_evidence (cross-cluster arrow 14-day window)

**ship gate v11 升级 88→92 verify points**:
- v10 88-check 全部保留 (tick40)
- tick41 NEW 4 verify:
  1. `fix_layer_audit` 必填 5 sub-fields (PM 跑 acceptance 时)
  2. `worsening_evidence` 14-day window 监控启用
  3. F4 credential-pool-stale-snapshot v2 invariant 6 必跑
  4. CVE-2026-61459 + CVE-2026-59950 已知 MCP server version pin 检查 (control 8 沿用 tick38)

**Self-downgrade v4**:
- 沿用 chief-agent 4 rule 同命中 (rule 2 + 3 + 4 + 5)
- 23-field v9 acceptance contract binding (取代 v8)
