---
name: hermes-cron-workdir-lifetime-isolation-v1
description: 'F8 (cron-ticker-resilience-deck) invariant 9 = workdir_lifetime_isolation。当 cron job 设置 cwd 后,该 cwd 必须隔离到 job lifetime 内,不能 leak 到 gateway session 或后续 subprocess。沿用 tick33 F8 8 invariant + 1 NEW tick44。Use when: 看到 cron job spawn subprocess / gateway turn 创建于 cron 工作期间 / cross-profile.cron.workdir.leak 触发任意 P1 信号时。'
version: 1.0.0
created_by: researcher C-profile auto-evolve (tick44 / 2026-07-22)
platforms: [linux, macos]
metadata:
  hermes:
    tags: [F8, invariant-9, cron-workdir, lifetime-isolation, leak-fix]
    related: [hermes-cron-ticker-resilience-deck-v1, hermes-cross-cluster-state-integration-v1]
    evidence:
      - GH #69396 (cron job workdir leaks into gateway sessions, P1 2026-07-22)
      - GH #68483 (cron CLI root locks uid-1000 ticker, P1 2026-07-21)
      - GH #68915 (orphan subshell holds stdout pipe, P1 2026-07-22)
---

# hermes-cron-workdir-lifetime-isolation-v1

> F8 (cron-ticker-resilience-deck) **invariant 9** = workdir lifetime isolation
> Tick44 立卡 / 沿用 tick33+tick40+tick43 立卡的 9 invariant 累计(2026-07-22)

## This skill solves

researcher v0.x 的痛点:
- cron job 设置 target_cwd 后,**进程级 cwd 被全局污染**,后续 spawn 的 subprocess / 在 cron 工作期内的 gateway session 都继承这个 cwd
- 工作结束 → cwd 仍停留在 target_cwd,后续的交互式 gateway turn 也继承
- 沿用 #68483 模式:CLI run as root silently locks uid-1000 ticker → cwd 泄露到 daemon 流程
- 沿用 #68915 模式:agent background server via shell `&`,subprocess 继承 cwd,**且 stdout pipe 不释放**

C档升级后(F8 invariant 9):
1. **workdir lifetime context manager** = try/finally restore original_cwd
2. **subprocess inherit ORIGINAL cwd, not JOB cwd**(SPAWN env override)
3. **gateway session during cron run** = workdir-aware, 不被 cron cwd 影响
4. **audit log 强制记录** job_cwd / original_cwd / subprocess_inherited_cwd

## When to invoke

任何 cron worker / agent 见到以下条件立即触发:
1. cron job 启动前(`pre_job_hook`)
2. cron job 结束前(`post_job_hook`)
3. cron job spawn 任意 subprocess 时
4. cron job working period 内 gateway session 创建
5. CLI run as root(沿用 #68483)
6. shell `&` background(沿用 #68915)

## 6-step workdir lifetime isolation

### Step 1: pre_job_hook save original_cwd

```python
import os
from contextlib import contextmanager

JOB_CWD_STACK = []

@contextmanager
def cron_workdir_lifetime(target_cwd):
    """F8 invariant 9 — workdir isolated to job lifetime."""
    saved_cwd = os.getcwd()
    JOB_CWD_STACK.append({
        'job_id': current_job_id(),
        'saved_cwd': saved_cwd,
        'target_cwd': target_cwd,
    })
    try:
        os.chdir(target_cwd)
        yield
    finally:
        os.chdir(saved_cwd)
        JOB_CWD_STACK.pop()
```

### Step 2: subprocess spawn — force inherit ORIGINAL cwd

```python
def safe_subprocess_spawn(cmd, **kwargs):
    """F8 invariant 9 — subprocess inherits ORIGINAL not JOB cwd."""
    original_cwd = JOB_CWD_STACK[-1]['saved_cwd'] if JOB_CWD_STACK else os.getcwd()
    kwargs['cwd'] = original_cwd
    return subprocess.run(cmd, **kwargs)
```

### Step 3: gateway session during cron — workdir-aware

```python
def create_gateway_session_during_cron():
    """F8 invariant 9 — gateway session NOT inherit cron job cwd."""
    original_cwd = JOB_CWD_STACK[-1]['saved_cwd'] if JOB_CWD_STACK else os.getcwd()
    return GatewaySession(cwd=original_cwd)
```

### Step 4: post_job_hook verify cwd restored

```python
def post_job_hook():
    """F8 invariant 9 — assert cwd restored to original."""
    assert len(JOB_CWD_STACK) == 0, \
        f"workdir_lifetime_isolation_breach: {JOB_CWD_STACK} not popped"
    assert os.getcwd() == ORIGINAL_PROCESS_CWD, \
        f"workdir_lifetime_isolation_breach: cwd={os.getcwd()} != {ORIGINAL_PROCESS_CWD}"
```

### Step 5: audit log 6 必填字段

```python
audit_log = {
    'job_id': current_job_id(),
    'job_cwd': JOB_CWD_STACK[-1]['target_cwd'] if JOB_CWD_STACK else None,
    'original_cwd': JOB_CWD_STACK[-1]['saved_cwd'] if JOB_CWD_STACK else os.getcwd(),
    'subprocess_inherited_cwd': safe_subprocess_spawn.last_kwargs['cwd'] if safe_subprocess_spawn.last else None,
    'lifetime_restored': JOB_CWD_STACK == [],
    'invariant_9_violation': len(JOB_CWD_STACK) != 0 or os.getcwd() != ORIGINAL_PROCESS_CWD,
}
write_audit_log(audit_log)  # write to ~/.hermes/cron/output/{date}/audit/cron-workdir-lifetime.jsonl
```

### Step 6: cross-cluster hook (CCA-F10-F8-state-db-zeroed-workdir-leak)

```python
def check_cross_cluster_arrow_cca_f10_f8():
    """F10 + F8 cross-cluster evidence — #68474 + #69396 reproduce check."""
    if get_state_db_size() == 0 and install_state_db_updated_recently():
        fire_CCA_F10_F8_state_db_zeroed_workdir_leak_arbitration()  # chief tier-1.5
    if JOB_CWD_STACK != [] and any(gateway_session_created_in_last_n_seconds(n=60)):
        fire_CCA_F10_F8_state_db_zeroed_workdir_leak_arbitration()
```

## Verification checklist

- [ ] cron_set_cwd_pre_call_test_must_pass
- [ ] cron_restore_cwd_post_call_test_must_pass
- [ ] new_subprocess_inherits_original_cwd_test_must_pass
- [ ] cron_session_destroyed_unwind_lifetime_test_must_pass
- [ ] audit_log_6_fields_test_must_pass(沿用 tick36 F11 invariant 5)
- [ ] cross_cluster_arrow_CCA_F10_F8_test_must_pass

## Reference

- GH #69396 — cron job workdir leaks into gateway sessions
- GH #68483 — cron CLI run as root silently locks uid-1000 ticker
- GH #68915 — Worker deadlocks when shell `&` orphan subshell holds stdout
- F8 invariant 9 立卡 tick44
- Cross-cluster arrow CCA-F10-F8-state-db-zeroed-workdir-leak (tick44 NEW)
