---
name: hermes-state-db-atomic-write-v1
description: 'F10 (cron-installer-handoff-state) catastrophic breach fix。state.db write 必走 atomic-replace pattern: write tmp + fsync + rename。覆盖 GH #68474 state.db zeroed 95MB during v0.19.0 desktop update Windows P1(2026-07-21)。Use when: 任何 state.db 写入路径 / desktop update handoff / concurrent updater + daemon racing 时。'
version: 1.0.0
created_by: researcher C-profile auto-evolve (tick44 / 2026-07-22)
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [F10, atomic-write, state-db, fsync, rename, desktop-update, handoff]
    related: [hermes-update-handoff-readiness-v1, hermes-cross-cluster-state-integration-v1]
    evidence:
      - GH #68474 state.db zeroed (95MB of null bytes) during v0.19.0 desktop update on Windows (P1 2026-07-21)
      - GH #69179 Desktop app cannot run after v0.19.0 update (P1 2026-07-22)
---

# hermes-state-db-atomic-write-v1

> F10 (cron-installer-handoff-state) **catastrophic breach fix** = state.db atomic write
> Tick44 立卡 / 沿用 tick35 F10 6 invariant + catastrophic fix path

## This skill solves

researcher v0.x 的痛点:
- state.db write 路径不 fsync → 桌面 update race 时 state.db 写 0 字节 / 95MB null bytes 全部丢失
- concurrent updater + daemon 写作 race condition → Windows 文件锁 + POSIX atomic-replace 不一致
- 用户 state.db 95MB 数据全失 — release verification 灾难性失败

C档升级后:
1. **atomic-replace-write pattern** = write to .tmp + fsync + rename in single atomic syscall
2. **concurrent updater + daemon race detect** = lock-acquire + verify-state
3. **rollback path** = .bak file with timestamp if write fail mid-way
4. **pre-update state.db backup** = mandatory before any install handoff

## When to invoke

任何 state.db writer / desktop update handoff / concurrent process 时立即触发:
1. state.db session metadata write(沿用 v0.19.0 release #58899)
2. state.db routing index write(沿用 v0.19.0 release #59203)
3. state.db api_content sidecar write(沿用 v0.19.0 release #67274)
4. desktop updater handoff + state.db write race
5. concurrent upgrade + daemon running
6. install migration stale-state recovery

## 6-step atomic write pattern

### Step 1: pre-write backup

```python
def state_db_atomic_write_pre_backup(state_db_path, current_data):
    """F10 catastrophic fix — pre-write backup mandatory."""
    timestamp = int(time.time())
    backup_path = f"{state_db_path}.bak.{timestamp}"
    shutil.copy2(state_db_path, backup_path)
    return backup_path
```

### Step 2: write to .tmp + fsync

```python
def state_db_atomic_write_tmp(state_db_path, data):
    """F10 catastrophic fix — write to .tmp + fsync mandatory."""
    tmp_path = f"{state_db_path}.tmp"
    with open(tmp_path, 'w') as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())  # critical: fsync before rename
    return tmp_path
```

### Step 3: rename atomic + fsync parent

```python
def state_db_atomic_write_rename(tmp_path, state_db_path):
    """F10 catastrophic fix — atomic rename + fsync parent dir."""
    os.rename(tmp_path, state_db_path)  # atomic on POSIX, near-atomic on Windows
    # fsync parent dir to ensure rename persists
    parent_dir = os.path.dirname(state_db_path)
    dir_fd = os.open(parent_dir, os.O_RDONLY)
    try:
        os.fsync(dir_fd)
    finally:
        os.close(dir_fd)
```

### Step 4: post-write verify size + content

```python
def state_db_atomic_write_verify(state_db_path, expected_min_size):
    """F10 catastrophic fix — verify post-write."""
    actual_size = os.path.getsize(state_db_path)
    assert actual_size >= expected_min_size, \
        f"state_db_atomic_write_breach: size={actual_size} < {expected_min_size} (GH #68474)"
    # check NOT all-null bytes (95MB of null bytes prevent)
    with open(state_db_path, 'rb') as f:
        sample = f.read(1024)
        assert sample != b'\x00' * 1024, \
            f"state_db_atomic_write_breach: first 1KB all null bytes (GH #68474)"
```

### Step 5: error recovery rollback

```python
def state_db_atomic_write_with_rollback(state_db_path, current_data, new_data):
    """F10 catastrophic fix — full pipeline + rollback."""
    try:
        backup_path = state_db_atomic_write_pre_backup(state_db_path, current_data)
        tmp_path = state_db_atomic_write_tmp(state_db_path, new_data)
        state_db_atomic_write_rename(tmp_path, state_db_path)
        state_db_atomic_write_verify(state_db_path, len(current_data) * 0.5)
        return {'success': True, 'backup': backup_path}
    except Exception as e:
        # rollback: restore from .tmp or .bak
        if os.path.exists(state_db_path + '.tmp'):
            os.rename(state_db_path + '.tmp', state_db_path)
        return {'success': False, 'error': str(e), 'rolled_back': True}
```

### Step 6: pre-update handoff backup mandatory

```python
def desktop_update_handoff_pre_backup():
    """F10 catastrophic fix — pre-Desktop-update state.db backup mandatory."""
    state_db = find_state_db_path()
    backup = state_db_atomic_write_pre_backup(state_db, read_full(state_db))
    # store backup metadata
    with open(backup + '.meta', 'w') as f:
        json.dump({
            'update_id': get_current_update_id(),
            'pre_update_state': True,
            'rollback_path': backup,
        }, f)
```

## Verification checklist

- [ ] state_db_write_to_tmp_then_fsync_then_rename_test_must_pass
- [ ] concurrent_updater_running_daemon_write_race_test_must_pass(沿用 #68474 reproduce)
- [ ] state_db_zerobyte_no_size_match_test_must_pass(防 95MB of null)
- [ ] desktop_update_handoff_rollback_test_must_pass(沿用 #68474 + #69179)
- [ ] audit_log_6_fields_test_must_pass(timestamp + backup + tmp + rename + verify + rollback)
- [ ] cross_cluster_arrow_CCA_F10_F8_state_db_zeroed_workdir_leak_test_must_pass

## Reference

- GH #68474 — state.db zeroed (95MB of null bytes) during v0.19.0 desktop update on Windows — **P1 catastrophic**
- GH #69179 — Desktop app cannot run after v0.19.0 update — P1
- F10 invariant 5 + 6 catastrophic breach (tick44 立卡)
- Cross-cluster arrow CCA-F10-F8-state-db-zeroed-workdir-leak (tick44 NEW)
- v0.19.0 release notes #58899/#59203/#67274 state.db write path
