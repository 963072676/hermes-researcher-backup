---
name: hermes-cron-session-leak-guard
description: 'Tick32 立卡。Cron state.db session leak 防御 — no_agent branch + 全部 cron exit path 走 end_session() funnel invariant。沿用 GH #41935 + #12029 + #1416 cross-source 根因 + family 立卡 cron-session-leak-closed-state。当 cron session leak P1 触发或 release-time session-close invariant 缺位时使用。'
version: 0.1.0
created: 2026-07-10
category: devops
platforms: [linux, macos]
metadata:
  hermes:
    tags: [cron, state-db, session-leak, release-verification, invariant]
    related: [hermes-cross-platform-redact-call-site-audit, hermes-fallback-circuit-breaker-invariants, hermes-researcher-self-evolution-v1]
---

# hermes-cron-session-leak-guard

> Hermes cron state.db session leak defensive invariant + family guard
> 沿用 GH #41935 + #12029 + #1416 cross-source 根因 + tick32 SOUL_pm 草案
> 立卡 family `cron-session-leak-closed-state`

## 触发条件

- cron session leak P1 触发(GH #41935, #12029, #1416 三 cluster)
- v0.19.0 ship gate 需要 session-close invariant
- cron tick32+ researcher 监控发现相关 family 涌现

## family 立卡定义

**`cron-session-leak-closed-state`** family:
- root cause: cron / scheduler 路径下的 session finalization 不 invariant
  — 多个 exit path (no_agent, exception, compression, timeout, cancel,
  shutdown) 至少一个跳过 `end_session()` 调用
- 影响 source: `cron`, `cli`, `discord`, `telegram` (沿用 #12029 cross-source)
- sister family:
  - tick28 `cross-platform-state` (replay-safety gap)
  - tick31 `memory-injection-cross-platform` (Honcho memory leak)
  - tick27 `silent-fail` (send-and-forget path)
- sweeper marker: `sweeper:risk-cron-session-leak`

## 防御 invariant

**单一终极 invariant**: "if a session reaches any terminal state, `end_session()`
must run exactly once in a `finally`-style path"

强制手段:
1. **Centralize**: 全部 cron exit path funnel 通过一个 helper `_finalize_cron_session(...)`
2. **Decorator**: 用 `@functools.wraps` + decorator 强制 finally block 包含 end_session call
3. **finally-only mutation**: session row `ended_at` / `end_reason` 只在 finally block 写

## production patch template

```python
# cron/scheduler.py — centralize session finalization

def _finalize_cron_session(
    session_id: str | None,
    end_reason: str,
    exit_status: int = 0,
    output: str | None = None,
) -> None:
    """Single funnel for cron session end-of-life.

    Guarantees:
    - Session row always closed on any exit path (success, exception,
      no_agent, compression, timeout, cancel, shutdown)
    - All paths converge here — no exit_path bypass

    Idempotent: safe to call twice (e.g. outer finally + no_agent branch).
    """
    if not session_id:
        return
    try:
        session_db.end_session(
            session_id,
            end_reason=end_reason,
            exit_status=exit_status,
            output=output,
        )
    except Exception as exc:
        # never block exit on session DB error, just log
        logger.warning(f"session close failed for {session_id}: {exc}")


# In _run_job (~line 1921-1942), outer finally block:
def _run_job(self, job, ...):
    session_id = None
    try:
        session_id = self._open_job_session(job)
        # ... existing body ...
    finally:
        _finalize_cron_session(
            session_id=session_id,
            end_reason=self._determine_end_reason(),
            exit_status=self._last_exit_status,
            output=self._last_output,
        )


# In _run_job_impl (~line 1310), no_agent branch ALSO calls:
def _run_job_impl(self, job, no_agent: bool = False, ...):
    if no_agent:
        try:
            result = self._run_job_script(...)
        finally:
            _finalize_cron_session(
                session_id=self._current_session_id,  # null if no session opened
                end_reason="cron_no_agent_complete",
                exit_status=result.returncode,
                output=result.stdout,
            )
        return result
```

## test template

```python
# tests/cron/test_cron_no_agent_session_close.py
import pytest
import subprocess
import sqlite3
from pathlib import Path


def test_no_agent_cron_session_closed(tmp_path, hermes_test_env):
    """#41935 fix invariant: no_agent cron jobs MUST close session row."""
    # Setup: create test cron job with no_agent=True
    cron_yaml = tmp_path / "job.yaml"
    cron_yaml.write_text("""
name: test-no-agent
schedule: "* * * * *"
no_agent: true
script: /tmp/dummy.sh
""")

    # Run 3 ticks
    for _ in range(3):
        subprocess.run(["hermes", "cron", "run", str(cron_yaml)],
                       env=hermes_test_env, check=True)
        # Allow state.db flush

    # Query state.db
    state_db = Path(hermes_test_env["HERMES_STATE_DB"])
    con = sqlite3.connect(state_db)
    try:
        open_sessions = con.execute(
            "SELECT COUNT(*) FROM sessions WHERE source='cron' AND ended_at IS NULL"
        ).fetchone()[0]
        assert open_sessions == 0, f"Expected 0 open cron sessions, got {open_sessions}"
    finally:
        con.close()


def test_exception_path_closes_session(tmp_path, hermes_test_env):
    """exception during cron execution MUST close session."""
    cron_yaml = tmp_path / "job.yaml"
    cron_yaml.write_text("""
name: test-exception
schedule: "* * * * *"
script: /tmp/throw.sh
""")
    (tmp_path / "throw.sh").write_text("#!/bin/sh\nexit 99\n")
    (tmp_path / "throw.sh").chmod(0o755)

    subprocess.run(["hermes", "cron", "run", str(cron_yaml)],
                   env=hermes_test_env, check=False)

    state_db = Path(hermes_test_env["HERMES_STATE_DB"])
    con = sqlite3.connect(state_db)
    try:
        result = con.execute(
            "SELECT end_reason FROM sessions WHERE source='cron' AND ended_at IS NOT NULL ORDER BY ended_at DESC LIMIT 1"
        ).fetchone()
        assert result is not None, "session row must close even on exception"
        assert "error" in result[0].lower() or "exception" in result[0].lower() or \
               "exit_99" in result[0].lower(), \
               f"end_reason must reflect exception, got {result[0]}"
    finally:
        con.close()


def test_compression_handoff_closes_prior(tmp_path, hermes_test_env):
    """session split / compression handoff MUST finalize prior session."""
    # Setup cron job that triggers compression
    ...


def test_timeout_cancellation_cleanup(tmp_path, hermes_test_env):
    """timeout/cancel path MUST close session."""
    ...
```

## 推荐调用

```bash
# local dev: 前 commit 前跑
python3 -m pytest tests/cron/test_cron_no_agent_session_close.py -v || \
    { echo "BLOCK release"; exit 1; }

# CI: pre-merge 必须 exit 0
python3 scripts/cron-session-leak-guard.py

# release verification: v0.19.0 ship 前必须跑(沿用 tick32 SOUL_qa 草案)
scripts/release-verification-suite.sh
```

## Pitfalls

- 漏 no_agent branch:`@functools.wraps` decorator 强制 invariant 时,no_agent branch
  必须用 try/finally (沿用 PR #44087 approach)
- decorator 顺序:无 finally 概念的旧函数必须 manual wrapper,不要假设 cleanup 自动
- session DB error 不应阻塞 job execution:`_finalize_cron_session` 必须 catch
  + log,不让 cleanup 错误 mask 原 job error
- 旧 session row cleanup:已存在 zombie rows (历史 leak) 不应被新 fix 删除,
  应保留供分析(沿用 user workaround)

## v0.19.0 实装 schedule

1. **2026-07-12** (tick33): 立卡本 skill + PR #41969/#44087/`#21031` dedup 6h SLA 启动
2. **2026-07-14**: pm 接受 1 primary PR (优先 #41969 最早) + close 其他
3. **2026-07-16**: merged fix + 4 case test pass
4. **2026-07-18**: ship v0.19.0 含 invariant + cleanup script
5. **2026-07-20**: 全 5 profile (chief / pm / dev / qa / default) cross-profile verify

## verdict 倾向

**采纳:高** — 直接影响所有 cron worker (含本 researcher + chief / pm / dev / qa / default
5 profile 全部 cron-based skill)。family 立卡 + invariant 是 release verification v2 升级核心。
