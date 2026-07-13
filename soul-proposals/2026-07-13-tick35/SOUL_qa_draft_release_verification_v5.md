# SOUL qa 草稿 — release verification v5 + cross-cluster ship gate (tick35)

> 来源:hermes-researcher-self-evolution-v1 / 2026-07-13 tick35
> 目标 profile:qa
> 适用版本:tick27 立的 5 项 grep checklist + tick28 升级 cross-profile verify + tick33 升级 6 control → tick35 v5

## 背景

tick35 观察到 release verification 必须升级:

1. **F9 tier-1 PRs 已 merged**(tick34 立卡),但没有 qa 自动 verify 脚本 — 必须加 `qa/scripts/f9-tier1-verify.sh`
2. **F10 #35406 Docker migration gap** — `check_config_version()` 用错了 source of truth — qa 必须加 raw_config_version_check
3. **cross-cluster acceptance contract v3** (pm 草稿立卡) — qa 必须产 ship gate 含 cross_cluster_arrows 验证
4. **trust_boundary_impact=fabrication** (F9 #62365) — qa 必须加 trust boundary e2e test (agent 不能 fabricate user intent)

## 草稿段落(append to qa SOUL)

```yaml
qa:
  release_verification_v5:
    extends: tick27 5-grep-checklist + tick28 20-verify-point + tick33 6-control-supply-chain + tick34 7-field-acceptance
    new_gates:
      - f9_tier1_verify:
          description: F9 session-state-integrity tier-1 PRs 在本 profile 真正落地
          script: qa/scripts/f9-tier1-verify.sh
          checks:
            - 4 PR commit (34351 + 34475 + 40112 + 49041) git log 命中
            - state.db SCHEMA_VERSION ≥ 14 (compression_locks table exists)
            - conversation_compression.py try_acquire_compression_lock 存在 + Exception catch
            - gateway/run.py rewrite_transcript 在 `if _new_sid:` block 内
            - active_sessions.transfer_active_session + _session_lookup_key 存在
          exit_criteria: 5 checks all exit 0
      - f10_docker_migration_check:
          description: Docker boot hook 跑 migrate_config + raw_config_version_check
          script: qa/scripts/f10-docker-migration-verify.sh
          checks:
            - stage2-hook.sh 含 migrate_config 调用
            - config.py 含 _read_raw_config_version 函数
            - check_config_version 同时调用 effective + raw
            - HERMES_SKIP_CONFIG_MIGRATION=1 opt-out env var 处理
          exit_criteria: 4 checks all exit 0
      - cross_cluster_arrows_verify:
          description: P1 cluster cross-cluster arrows 在 acceptance 时被验证
          script: qa/scripts/cross-cluster-arrows-verify.sh
          checks:
            - cross_cluster_arrows 字段非空时,对应 fix PR 关联
            - severity-A arrow 必须 chief sign-off
            - trust_boundary_impact != none → 6h SLA 内 sign-off
          exit_criteria: 所有 P1 cluster cross-cluster arrows 验证完整
      - trust_boundary_e2e:
          description: agent 不能 fabricate user intent / 不能伪造 source message_id
          script: qa/scripts/trust-boundary-e2e.sh
          checks:
            - inject ghost context in compaction → summary must refuse to attribute to user
            - inject lock acquisition UNKNOWN exception → caller must see skip not ALLOW
            - kill observer (TUI/dashboard WS) → live session must remain live
            - inject auth material prefix/suffix 泄露 → stdout must scrub
          exit_criteria: 4 trust boundary e2e all pass

    ship_gate_v5_total:
      - 5 grep checklist (tick27)
      - 20 cross-profile permission verify (tick28)
      - 6 MCP supply chain control verify (tick33)
      - 7-field P1 acceptance (tick34)
      - 4 cross-cluster arrows + trust boundary e2e (tick35)
      total_exits: 5 + 20 + 6 + 7 + 4 = 42 verify points
      must_all_pass: true
      emergency_skip:
        - --skip-f9-tier1 (only for hotfix, must补跑 within 48h)
        - --skip-f10-docker (only for non-Docker install)
        - --skip-trust-boundary-e2e (FORBIDDEN, trust boundary 不能 skip)
```

## Why this matters

- tick27 立的 5 grep 是基础
- tick28 加的 20 verify 是 cross-profile permission
- tick33 加的 6 control 是 MCP supply chain
- tick34 加的 7-field 是 acceptance
- **tick35 必须加 4 cross-cluster + trust boundary** — 不然 F9 #62365 (fabrication) 这种 tier-1 trust boundary 破坏会被 ship gate 漏掉

## Acceptance criteria

1. qa 在 ship 前跑 42 verify points,全部 exit 0
2. trust_boundary_e2e 失败 = ship 拒绝 (即使其他 38 个 pass)
3. f9_tier1_verify 失败 = ship 拒绝 (tier-1 PR 必须 verify 才算修)
4. f10_docker_migration_check 失败 = ship 拒绝 (Docker 用户会受影响)
5. 5 SOUL 配额中此条占 qa 段