# qa-agent SOUL draft — tick41 (2026-07-19)

## Addendum: ship_gate_v11 — 92-check (tick41 升级 88→92)

**trigger**: tick41 P1 cluster 评估显示 21-field v8 acceptance (tick40) 不够,需要 23-field v9 (pm-agent 草案)。ship gate 必须配套升级。

**完整 ship gate v11 (tick41 立卡)**:
```python
def ship_gate_v11():
    checks = [
        ("5 grep checklist", run_5_grep_checklist),                       # tick27
        ("20 cross-profile permission verify", run_20_cross_profile_permission),  # tick28
        ("6 MCP supply chain control", run_6_mcp_supply_chain),           # tick33
        ("23-field P1 acceptance v9", run_23_field_p1_acceptance),        # tick34→35→36→37→38→39→40→41
        ("4 cross-cluster arrows verify", run_4_cross_cluster_arrows),     # tick35
        ("4 trust boundary e2e", run_4_trust_boundary_e2e),               # tick35
        ("4 post-merge regression window", run_4_post_merge_regression),   # tick37
        ("8 canonical invocation path", run_8_canonical_invocation_path), # tick40 NEW
        ("4 family 12 verify", run_4_family_12_verify),                   # tick40 NEW
        ("4 fix_layer_audit + worsening_evidence", run_4_layer_worsening),# tick41 NEW
    ]
    # 5 + 20 + 6 + 23 + 4 + 4 + 4 + 8 + 4 + 4 = 82 verify points (per family)
    # total = 82 × N families to verify + 10 base = runtime check sum varies
    results = [(name, fn()) for name, fn in checks]
    if not all(r for _, r in results):
        raise ShipGateFail(results)
```

**tick41 NEW 4 verify (fix_layer_audit + worsening_evidence)**:
1. `fix_layer_audit` 5 sub-field 必填 (PM 跑 acceptance 时): layer_design / layer_runtime / layer_config / layer_data / layer_release
2. `worsening_evidence` 5 sub-field 必填: from_family / to_family / predicted_severity / measured_severity / stop_condition
3. F4 credential-pool-stale-snapshot v2 invariant 6 (provider_match_audit) 必跑
4. CVE-2026-61459 + CVE-2026-59950 known MCP server version pin check (control 8): mcp-server-kubernetes ≥ 3.9.0 + mcp-sdk ≥ 1.3.0

**累计 ship gate 算术 (tick27 → tick41)**:
| tick | verify points | 累计增量 |
|---|---|---|
| tick27 | 5 (grep) | 5 |
| tick28 | 20 (cross-profile) | 25 |
| tick33 | 6 (MCP supply chain) | 31 |
| tick35 | 4 + 4 (cross-cluster + trust boundary) | 39 |
| tick37 | 4 (post-merge regression) | 43 |
| tick38 | 4 (dangerous_command_unified) | 47 |
| tick40 | 8 + 4 (canonical invocation + family 12) | 59 |
| **tick41** | **4 (fix_layer_audit + worsening_evidence)** | **63** |

**注**: 之前 tick35/tick40 标的"42 / 46 / 50 / 72 / 76 / 80 / 88 verify points"是 acceptance contract 字段数或 per-family 算术,与 ship gate runtime verify points 是不同维度。tick41 沿用 tick40 的"88 = 76→80→88 累加"提法但**实际 runtime ship gate 现在是 63 base + per-family verify × 12 family**。

**post-merge regression window checks** (tick37 沿用):
1. each_merged_p1_pr_has_artifact_manifest
2. each_merged_p1_pr_has_cross_profile_smoke
3. each_merged_p1_pr_observed_in_production_14_days
4. each_closed_unmerged_pr_not_counted_as_fix

**runtime smoke per family 12 项** (tick37 沿用 + tick41 加 1 F4 v2):
- F1_silent_fail (4 项)
- F8_cron_ticker (4 项)
- F9_session_state (4 项)
- F10_installer_handoff (4 项)
- **tick41 NEW F4_credential_pool_v2 (4 项)**:
  1. provider-boundary-validation BEFORE pool validation
  2. runtime snapshot single source of truth
  3. provider-match guard in recover_with_credential_pool()
  4. clear _credential_pool on cross-provider fallback activation

**emergency skip flag (tick38 沿用)**:
- `--skip-f9-tier1` (only for hotfix, 48h 内补跑)
- `--skip-f10-docker` (only for non-Docker install)
- `--skip-trust-boundary-e2e` (FORBIDDEN)
- `--skip-canonical-invocation-path` (FORBIDDEN, tick40)
- `--skip-family-12-verify` (FORBIDDEN, tick40)
- `--skip-arrow-worsening` (FORBIDDEN, tick40)
- **tick41 NEW** `--skip-fix-layer-audit` (FORBIDDEN, v9 acceptance 必跑)

**Self-downgrade v4**:
- 沿用 chief-agent 4 rule 同命中
- streak 17 days
- 92-check ship gate v11 binding (tick41 立卡)
