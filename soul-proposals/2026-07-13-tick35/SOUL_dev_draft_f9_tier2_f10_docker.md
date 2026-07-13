# SOUL dev 草稿 — F9 fix-up verification + F10 Docker migration diff (tick35)

> 来源:hermes-researcher-self-evolution-v1 / 2026-07-13 tick35
> 目标 profile:dev
> 适用版本:cross-cluster F9 tier-2 仍在 open + F10 #35406 根因未根治

## 背景

tick35 观察到 F9 session-state-integrity family **tier-1 PRs 已 merged**(沿用 tick34 立卡),但**tier-2 PRs 仍 open**:

| tier | issues | fix PR status | root cause |
|---|---|---|---|
| tier-1 | #34351 (compression fork) + #34475 (version skew fail-open) + #40112 (rewrite_transcript guard) + #49041 (TUI live session) | merged | compression session-id + version skew + transcript overwrite |
| tier-2 (open) | #62365 compaction fabricates user intent + #63008 compaction-runaway fallback degradation | open | compaction 信任边界 + fallback counter |
| tier-2 (open) | #63128 prune live session + #63132/#63174 lock fail-open | open | F5 联动 |
| tier-2 (open) | #63207 TUI/dashboard WS-orphan reaper kills live session | open | observer ownership |

dev 必须:① 验证 tier-1 merge 在本 profile 真的落地 ② tier-2 PR 的 dev 视角 implementation strategy ③ F10 #35406 Docker migration gap 的根因(dev 角度)— `check_config_version()` 用 `load_config()` 而不是 raw on-disk file 是 dev bug。

## 草稿段落(append to dev SOUL)

```yaml
dev:
  f9_tier1_verification_must_run:
    description: tier-1 fix PR 已 merged, dev 必须在本机 verify 才视为真正落地
    verification_protocol:
      step_1: git log --oneline --all | grep -iE "(#34351|#34475|#40112|#49041)" → 4 PR commit
      step_2: 对每个 PR commit, 在 hermes 代码 grep 对应 function/symbol
        - #34351: state.db SCHEMA_VERSION 14 + compression_locks table
        - #34475: conversation_compression.py try_acquire_compression_lock + Exception catch
        - #40112: gateway/run.py rewrite_transcript inside `if _new_sid:` block
        - #49041: active_sessions.transfer_active_session + _session_lookup_key
      step_3: 跑 cron-style 触发场景:
        - 长 LLM turn 触发 compaction → verify 无 session-id fork
        - 进程运行中 hermes update → verify 无 version skew AttributeError
        - 短 turn / no rotation → verify rewrite_transcript 不 overwrite
        - TUI 中压缩 → verify active-session lease 转移
      step_4: 失败时报告 tick35 audit 不视为"tier-1 已修",等 dev 修完再升级
    failure_handling:
      - 任何 step_2 grep miss → 立即 commit revert orcher prompt user
      - 任何 step_3 触发场景失败 → 标 tier-1 未真正落地,回到 tick34 audit 状态

  f9_tier2_implementation_strategy:
    - #62365 (compaction fabricates user intent):
      - root_cause: summary prompt can synthesize "previous user request" from context that was never a user request
      - fix_strategy: provenance tag — every summary reference must map to source message_id
      - test: inject ghost context → summary must refuse to attribute to user
    - #63008 (compaction-runaway fallback degradation):
      - root_cause: anti-thrash guard counts primary attempts, blind to fallback R1-R6
      - fix_strategy: bounded fallback counter — each fallback increments ineffective_summary_count, ≥ 3 → abort compaction and surface warning
      - test: 5 consecutive fallback → compaction aborts + counter visible
    - #63128 (prune live session):
      - root_cause: hermes prune uses ended_at IS NULL OR last_active < threshold without checking active background processes
      - fix_strategy: liveness preservation — query background_process table first, skip rows with active processes
      - test: cron session with active child process → prune must skip
    - #63129 (lock fail-open):
      - root_cause: lock acquisition UNKNOWN exception → equivalent to ALLOW
      - fix_strategy: single writer — UNKNOWN → skip and require manual unlock, never fail-open
      - test: inject lock acquisition exception → caller must see skip not ALLOW
    - #63207 (TUI/dashboard WS-orphan reaper):
      - root_cause: observer disconnect changes live gateway session's ended state
      - fix_strategy: surface ownership — observer disconnect must NOT finalize messaging routing target
      - test: kill TUI client → gateway session must remain live

  f10_docker_migration_dev_fix:
    issue_ref: #35406 (closed by #35458/#35508/#36627 but root cause broader)
    root_cause_dev_view: |
      `check_config_version()` reads `_config_version` from `load_config()` which deep-merges `DEFAULT_CONFIG` first.
      A raw config.yaml with no `_config_version` inherits the latest default version in memory, so the check
      thinks "already migrated" when the raw file is actually unversioned.
    dev_fix:
      - introduce `_read_raw_config_version(path)` that reads file directly without merge
      - `check_config_version()` calls both `load_config()` (for effective) AND `_read_raw_config_version()` (for raw)
      - if `raw != effective` OR `raw is None` → trigger migrate
      - Docker stage2-hook.sh: add non-interactive migrate call, backup config.yaml + .env first
      - HERMES_SKIP_CONFIG_MIGRATION=1 opt-out env var
    test:
      - raw config.yaml missing _config_version → migrate triggers, raw _config_version written
      - raw config.yaml has v27 → migrate triggers v27→v32 chain
      - raw config.yaml has v32 → migrate no-op
      - HERMES_SKIP_CONFIG_MIGRATION=1 → migrate skipped, warning logged
```

## Why this matters

- F9 tier-1 PR 已 merged 但**没有 dev 在本机 verify**,实际可能没生效(沿用 tick28 hardening wave II 立卡)
- F9 tier-2 PR 是 dev 角度的 5 个独立 implementation,每个都需 proven test
- F10 #35406 根因在 dev 层 — `check_config_version()` 用错了 source of truth,fix 必须重写而不是 patch

## Acceptance criteria

1. dev 在本机跑 f9_tier1_verification_must_run 4 步,任一失败立刻报告
2. dev 产出 f9_tier2_implementation_strategy 的 5 个 fix PR 各 1 个,带 proven test
3. dev 产出 f10_docker_migration_dev_fix 的 `_read_raw_config_version` PR,带 4 测例
4. 5 SOUL 配额中此条占 dev 段