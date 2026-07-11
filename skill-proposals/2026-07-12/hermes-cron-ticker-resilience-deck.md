---
name: hermes-cron-ticker-resilience-deck
description: '6 invariant cron ticker resilience deck — liveness heartbeat + BaseException catch + lock granularity + ownership invariant + restart safety + tick visibility。Use when: cron worker 观察到 gateway ticker 死 / lock 阻塞 / ownership race / silent failure / restart loop 任一现象。'
version: 1.0.0
author: Hermes Agent (researcher profile)
license: MIT
created_by: agent
platforms: [linux, macos]
metadata:
  hermes:
    tags: [cron, ticker, resilience, watchdog, heartbeat, gateway, silent-fail, family]
    related: [hermes-silent-fail-counter, hermes-cron-delivery-receipt, hermes-researcher-self-evolution-v1]
    sweeper_marker: sweeper:risk-cron-ticker-resilience
    family: cron-ticker-resilience-deck
    立卡: tick33
---

# hermes-cron-ticker-resilience-deck

> Tick33 (2026-07-12) 立卡。基于 9 GH issues 单一 family: #32612 #32895 #37179 #27485 #11614 #48234 #49410 #30719 #44049.

## 这个 skill 解决什么

Cron ticker 是 Hermes gateway 投递链的根 infra。9 个不同 issue 都收敛到 **cron ticker 失效的不同面**:
- 线程死 (silently, BaseException escape)
- 文件锁饿死 (held for full job duration, msvcrt 0-byte)
- 进程所有权竞争 (desktop vs launchd gateway)
- 自杀重启循环 (agent 调 hermes gateway restart)
- 可见性丢失 (heartbeat 缺失, status 误报 healthy)
- restart 不再触发 (systemd Restart=always 第二次失败)

**单点修复不够**,必须 6 invariant 全部满足。

## 何时调用

- cron worker 观察到 ticker 死 / lock 阻塞 / ownership race / silent failure / restart loop 任一现象
- release verification (qa ship gate 跑 4 silent-fail scenarios,沿用 tick33)
- chief-agent 接 P1 cron ticker → 6h dedup PR (沿用 tick27 PR dedup)
- pm 决策 family registry v8 → cron-ticker-resilience deck 是第 8 family

## 6 Invariant (deck 完整版)

### 1. Liveness heartbeat

```python
# cron/jobs.py (沿用 tick33 SOUL_chief invariant #1)
TICKER_HEARTBEAT_FILE = CRON_DIR / "ticker_heartbeat"
TICKER_SUCCESS_FILE = CRON_DIR / "ticker_last_success"

def _atomic_write_epoch(path: Path) -> None:
    fd, tmp_path = tempfile.mkstemp(dir=str(CRON_DIR), suffix=".tmp", prefix=".hb_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(str(time.time()))
            f.flush()
            os.fsync(f.fileno())
        _replace(tmp_path, path)
    except BaseException:
        try: os.unlink(tmp_path)
        except OSError: pass
        raise

def record_ticker_heartbeat(success: bool = False) -> None:
    try: _atomic_write_epoch(TICKER_HEARTBEAT_FILE)
    except Exception: pass
    if success:
        try: _atomic_write_epoch(TICKER_SUCCESS_FILE)
        except Exception: pass

def get_ticker_heartbeat_age() -> Optional[float]:
    return _epoch_file_age(TICKER_HEARTBEAT_FILE)
```

### 2. BaseException catch

```python
# gateway/run.py::_start_cron_ticker (沿用 PR #50016 模式)
def _start_cron_ticker_loop(self):
    while not self._shutdown_event.is_set():
        try:
            self._ticker_heartbeat_tick()
            self._cron_tick()
        except BaseException as exc:  # not just Exception
            logger.error(
                "cron ticker BaseException (continuing): %s\n%s",
                exc, traceback.format_exc(),
            )
            # 不退出 thread — 继续下一 tick
            self._record_ticker_heartbeat(success=False)
        self._shutdown_event.wait(self._ticker_interval_seconds)
```

### 3. Lock granularity (fcntl + Windows msvcrt)

```python
# cron/scheduler.py::tick (沿用 PR #27492 fix1 模式)
def tick(self):
    # 仅在 critical section (get_due_jobs + advance_next_run) 持锁
    with self._tick_lock():  # 自动 release at __exit__
        due_jobs = self._get_due_jobs_locked()
        if not due_jobs:
            return 0
        self._advance_next_run_locked(due_jobs)  # 设置 next_run_at 提前
    # 锁已释放,execution 不持锁
    with ThreadPoolExecutor(max_workers=self._max_parallel_jobs) as pool:
        futures = [pool.submit(self._execute_job, job) for job in due_jobs]
        for f in as_completed(futures):
            f.result()
```

```python
# Windows msvcrt 0-byte fix (沿用 #37179 workaround)
def _acquire_windows_lock(lock_file: Path):
    fd = os.open(str(lock_file), os.O_WRONLY | os.O_CREAT, 0o600)
    try:
        os.write(fd, b".")  # 必须 ≥1 byte,避免 msvcrt EOF PermissionError
        os.fsync(fd)
        msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
        return fd
    except (PermissionError, OSError):
        os.close(fd)
        return None
```

### 4. Ownership invariant (desktop vs launchd gateway)

```python
# cron/scheduler.py (沿用 PR #44049 模式)
def _gateway_scheduler_owner_active(self) -> bool:
    try:
        from gateway.status import is_gateway_runtime_lock_active
        return is_gateway_runtime_lock_active()
    except ImportError:
        return False  # fail open

def tick(self, defer_to_gateway_owner: bool = False) -> int:
    if defer_to_gateway_owner and self._gateway_scheduler_owner_active():
        logger.debug("deferring tick: gateway owner active")
        return 0
    # ... 原有 tick 逻辑
```

### 5. Restart safety (agent 自杀防)

```python
# hermes_cli/cron.py (新加 deny pattern)
DANGEROUS_SCHEDULES = [
    r"hermes\s+gateway\s+restart",
    r"hermes\s+gateway\s+stop",
    r"systemctl\s+(restart|stop)\s+hermes",
    r"launchctl\s+(unload|stop)\s+.*hermes",
    r"pkill\s+.*hermes",
]

def validate_schedule(schedule: str) -> None:
    for pattern in DANGEROUS_SCHEDULES:
        if re.search(pattern, schedule, re.IGNORECASE):
            raise ValueError(
                f"Schedule contains dangerous pattern '{pattern}' — "
                "agent cannot schedule its own runtime kill. "
                "Use hermes cron run --once instead."
            )
```

### 6. Tick visibility (status 报告真实状态)

```bash
# hermes cron status 输出 (沿用 #32666 mode)
✓ Gateway is running — PID 567
✓ Ticker is alive — last_heartbeat=15s ago (≤2x interval=120s)
✓ Ticker is firing jobs — last_success=3m ago
⚠ 1 active job — next run 2026-07-12 03:00:00

# 异常输出:
✗ Gateway running, ticker DEAD — last_heartbeat=12m ago (>5x interval=600s)
   → Run `systemctl --user restart hermes-gateway`
```

## 验收清单 (立卡后必须 6 项全过)

- [ ] `~/.hermes/cron/ticker_heartbeat` atomic write 每 tick 触发
- [ ] `~/.hermes/cron/ticker_last_success` atomic write 在 tick 不抛异常时触发
- [ ] ticker loop `try/except BaseException` 包裹 (不只 Exception)
- [ ] `fcntl.LOCK_EX` 仅在 critical section,execution 不持锁
- [ ] Windows `lock_fd.write(b".")` pre-init 避免 msvcrt 0-byte
- [ ] Desktop ticker `defer_to_gateway_owner=True` if gateway owner active
- [ ] `hermes cron create --schedule="hermes gateway restart"` raise ValueError
- [ ] `hermes cron status` 报告 heartbeat age + success age (不只是 PID)

## 踩坑 (Pitfalls)

### 1. msvcrt 0-byte lock EOF PermissionError (Windows only)

**触发**:Windows 上 `open(lock_file, "w")` 截断到 0 字节,`msvcrt.locking(LK_NBLCK, 1)` 因 range 超过 EOF 抛 PermissionError。

**修正**:写入前 `os.write(fd, b".")` 预填充 ≥ 1 byte。

### 2. asyncio.CancelledError 不被 `except Exception` 捕获

**触发**:Python 3.8+ `asyncio.CancelledError` 继承 `BaseException`(PEP 654 之前是 `Exception` 子类,后改为 `BaseException`)。`except Exception` 不会捕获。

**修正**:用 `except BaseException` (或显式 `except (Exception, asyncio.CancelledError)`)。

### 3. ticker_heartbeat atomic write 失败 → ticker 死

**触发**:`_atomic_write_epoch` 抛异常但被 `except Exception` 吞掉 → heartbeat 不更新 → status 误判死。

**修正**:`record_ticker_heartbeat` 必须 fail-safe (try/except 不 re-raise),但同时 log at WARN (不吞 silent)。

### 4. desktop ticker 抢 lock 失 launchd provenance (macOS)

**触发**:TCC / Full Disk Access 依赖 process ancestry,desktop 后端抢 lock 跑 job 读不到 protected local data。

**修正**:desktop ticker `defer_to_gateway_owner=True` 自动让给 launchd gateway。

### 5. agent cron create 自杀 respawn loop

**触发**:agent 调 `hermes cron create --schedule="*/1 * * * *" --command="hermes gateway restart"` → systemd KeepAlive 重启 → agent 看到重启再自杀 → 永久 loop。

**修正**:DANGEROUS_SCHEDULES regex deny list,创建时直接 raise ValueError。

### 6. cron ticker watchdog 重启 thread 失败

**触发**:ticker 线程死 → watchdog 想重启 thread,但 thread daemon 属性没设 → 主进程退出时 zombie。

**修正**:watchdog 重启的 thread 必须 `daemon=False` + 主进程退出显式 join。

## 关联 references

- tick27 立卡 silent-fail family: https://github.com/NousResearch/hermes-agent/issues/32612
- tick33 SOUL_chief 草案: `/root/migrated-home/hermes-researcher-backup/soul-proposals/2026-07-12/SOUL_chief_draft_cron_ticker_resilience_deck.md`
- tick33 SOUL_dev 草案: `/root/migrated-home/hermes-researcher-backup/soul-proposals/2026-07-12/SOUL_dev_draft_silent_fail_cron_gateway_still_open.md`
- 关联 PR: #50016 (BaseException catch), #44049 (desktop defer), #27492 (lock granularity)
- 关联 family: silent-fail (tick27), cron-session-leak-closed-state (tick32)

## 验证

- 跑 4 silent-fail scenarios (env spill + gateway deadlock + MCP keepalive + cron ticker death) 全 exit 0
- `hermes cron status` 报告 heartbeat age + success age,异常时显式 FAIL
- DANGEROUS_SCHEDULES deny pattern test 全过
- 6 invariant code 段在 cron/scheduler.py + gateway/run.py + hermes_cli/cron.py 全部覆盖