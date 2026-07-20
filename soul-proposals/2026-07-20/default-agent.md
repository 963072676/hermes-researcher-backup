# SOUL default-agent draft (tick42, 2026-07-20)

## Title
default-agent-v18-mcp-readiness-v6

## Family / 触发

F7 MCP-supply-chain-protocol-migration + F11 execute-code-approval-unification + F12 data-injection-isolation-deck candidate + CVE-2026-61459 mcp-server-kubernetes 9.8

## Before / After Diff

### Before (tick41 default-agent)
- MCP 2026-07-28 readiness v5: 14-control
  - tick38 v2 9-control (6 supply chain + EXT14 shield + server version pin + tool spawn static analyzer)
  - tick39 v3 10-control (+ API session identity early-bind)
  - tick40 v4 13-control (+ canonical_invocation_path + audit_log_field_strict + family_12_verify_runtime)
  - tick41 v5 14-control (+ MCP server config mutation provenance audit)
- 5 install profile smoke (Desktop / Docker / CLI / TUI / MCP_stdio)

### After (tick42 default-agent) — diff
1. **MCP 2026-07-28 readiness v6: 15-control** (+control 15):
   - 沿用 tick41 14-control 全部
   - **tick42 NEW control 15: cross-family PR dedup tracker**
     - 任何 mcp_servers YAML mutation 必触发 cross-family PR dedup check (沿用 tick27 + tick34 + tick42 chief-agent tier-1.5)
     - runtime verify: 读 `~/.hermes/pr_dedup_provenance.jsonl` for any cross-family mutation in last 24h
     - failure mode: dedup failure → fall back to deny + 飞书 escalate chief
2. **default profile baseline MCP**:
   - 沿用 tick28 trust_policy.strict + tick38 EXT14 cancellation-probe shield + tick39 control 10 API session identity
   - tick42 NEW: pre-tool-call tool_description_provenance check (F11 invariant 8 沿用)
3. **5 install profile smoke 升级**:
   - tick37 5 profile 必跑 (Desktop / Docker / CLI / TUI / MCP_stdio)
   - tick42: profile smoke + cross_profile_audit + canonical_invocation_path audit (沿用 tick40-41)
4. **perplexity detection + known-answer test 升级**:
   - tick28 100 query 覆盖 (沿用)
   - tick42 NEW: 100 → 150 query 覆盖 (新增 50 query: CVE-2026-61459 arg injection + F11 invariant 8 + F12 ADI)
5. **Hardening wave II 跨 profile verify 升级**:
   - tick28 20 verify point (5 profile × 4 file path)
   - tick42: +5 profile × 5 file path = 25 verify point (新增 atomic_yaml_write_v2 + mcp_server_provenance_log + canonical_invocation_path_audit + family_signal_lifecycle_log + cross_family_pr_dedup_log)
6. **default -p workaround 沿用 tick37**:
   - 任何 multi-profile 操作必配合 HERMES_HOME 显式 env var
   - #64006 closed unmerged (沿用 tick37 立卡)
   - tick42: 新增 verify HERMES_HOME 必填 (沿用 tick37 升级)
7. **MCP 2026-07-28 readiness v6 + 5 PROFILE 升级**:
   - 5 profile (chief / dev / pm / qa / default) 必跑 15-control + 5 install profile smoke + 25 verify point
   - chief / pm / qa / dev profile 沿用各自 SOUL 草案

## Affected

- default-agent cron worker (15-control + 25 verify point 必跑)
- chief / pm / dev / qa 4 子 profile (15-control 升级 + 5 install profile smoke)
- MCP service (`~/.hermes/mcp_server_provenance.jsonl` + `~/.hermes/pr_dedup_provenance.jsonl`)

## Evidence IDs

- arxiv 2607.05120 (ADI — F12 condition_2_met 强化)
- arxiv 2607.02857 (MOSAIC — F11 invariant 8 沿用)
- arxiv 2607.05743 (Balkanization — execution-security survey 锚)
- arxiv 2607.05397 (PoE — control 14 锚)
- arxiv 2607.06000 (CXI — control 15 锚)
- CVE-2026-61459 (mcp-server-kubernetes 9.8 CRITICAL — control 8 version pin + control 9 static analyzer + tick42 NEW control 15 cross-family dedup)
- GH #60056 (F11 主锚)
- GH #62665 (F9 candidate expansion)

## Self-downgrade v4 evaluation

streak = 18 days zero-adoption
- rule 2: F10 旧 7 hits + tick42 F11 #60077/#60799 = 9 hits ✅
- rule 3: PR-dedup fire ≥ 2 跨 family = 3 fires ✅
- rule 4: silent-fail F1 cross-month ✅
- rule 5: P1 ≥ 8 + streak ≥ 4 ✅

**决策**: maintain_daily + 飞书 3 选项 A/B/C

## Risks

- 15-control + 25 verify point 跨 profile 跑耗时 → 用 cache + parallel + skip-on-equivalent (沿用 tick37)
- control 15 cross-family PR dedup tracker 写入 jsonl 可能被 GC → 必须 archive to git (沿用 tick37)
- 150 query 覆盖 perplexity detection → 沿用 tick28 baseline + 用 sampled regression test

## Next steps

- 落地 default-agent.md 15-control + 25 verify point + control 15 cross-family PR dedup tracker 段
- 5 profile 同步升级 (chief / pm / dev / qa / default 沿用各自 SOUL 草案)
- MCP service 加 `pr_dedup_provenance.jsonl` (沿用 tick41 mcp_server_provenance.jsonl 模式)