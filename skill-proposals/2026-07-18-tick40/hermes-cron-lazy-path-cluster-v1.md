---
name: hermes-cron-lazy-path-cluster-v1
description: 'F8 cron-ticker-resilience-deck 拉新 evidence (#61674 lazy jobs.json path + #39782 cron inactivity timeout containment + #32612 ticker BaseException + #27485 lock held + #32666). 升级 dev-agent weekly sibling sweep 输出 5 issue 收敛 1 root cause 的 family 12 verify 模板。Use when: 任意 cron jobs.json / JOBS_FILE / cron/scheduler.py lazy resolution 相关 issue 或 PR acceptance 必跑。'
version: 1.0.0
author: hermes-researcher (auto-generated tick40)
license: MIT
created_by: agent
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [cron, F8, cron-ticker-resilience, lazy-path, jobs-json, cron-inactivity-timeout]
    family: F8
    tick: 40
    related: [hermes-researcher-self-evolution-v1, hermes-canonical-invocation-path-v1, hermes-family-sibling-sweep-v2]
---

# hermes-cron-lazy-path-cluster-v1

## 触发

F8 cron-ticker-resilience-deck tick40 拉新 evidence:
- #61674 (open, lazy jobs.json path, P1) — `cron/jobs.py` import-time-frozen `JOBS_FILE` 暴露测试 fixture 误写实文件
- #39782 (open, cron inactivity timeout containment, P1) — timeout 返回 failure 但 worker 仍 running
- #32612 (closed, ticker dies silently 15.5h, 已 merged fix)
- #27485 (open, tick lock held for full job duration, 已 fix PR #27492)
- #32666 (merged, ticker keep alive)

## 5 issue 收敛到 1 root cause cluster

| issue | layer | root cause |
|---|---|---|
| #61674 | 1: import-time-frozen constants | `cron/jobs.py:64-66` `_current_cron_store()` 不解析 late HERMES_HOME |
| #39782 | 2: timeout non-cooperative | worker thread 不响应 `agent.interrupt()` → 同样 job 重入 race |
| #32612 | 3: ticker silent death | `cron_tick()` raise BaseException (SystemExit) → thread dies silently |
| #27485 | 4: lock held too long | `tick()` 持 fcntl.LOCK_EX 整个 job execution → 其他 tick starve |
| #32666 | 5: ticker keep alive | surface level — 沿用 BaseException catch fix |

## 流程

```python
def cron_lazy_path_cluster_verify(pr_id):
    """F8 cron-ticker-resilience-deck sibling cluster verify."""
    verify = {
        "pr_id": pr_id,
        "verify_timestamp": now_utc(),
        "layers": {},
        "sibling_prs": [],
        "cross_cluster_arrows": [],
    }
    # Layer 1: lazy jobs.json path
    verify["layers"]["L1_lazy_jobs_path"] = {
        "test_id": "test_public_io_after_late_env_repoint_leaves_old_file_untouched",
        "verify": run_test("tests/cron/test_jobs.py::test_public_io_after_late_env_repoint_leaves_old_file_untouched"),
        "evidence_required": "import-time jobs.json byte-identical to sentinel after late HERMES_HOME repoint",
    }
    # Layer 2: timeout containment
    verify["layers"]["L2_timeout_containment"] = {
        "test_id": "test_run_job_does_not_hang_when_timeout_interrupt_is_ignored",
        "verify": run_test("tests/cron/test_scheduler.py::TestRunJobSessionPersistence::test_run_job_does_not_hang_when_timeout_interrupt_is_ignored"),
        "evidence_required": "non-cooperative agent interrupt → _TIMED_OUT_RUNS skip later runs",
    }
    # Layer 3: ticker BaseException
    verify["layers"]["L3_ticker_baseexception"] = {
        "test_id": "test_cron_ticker_keeps_running_after_systemexit",
        "verify": run_test("tests/cron/test_scheduler_provider.py::test_cron_ticker_keeps_running_after_systemexit"),
        "evidence_required": "cron.tick raises SystemExit → ticker keeps running",
    }
    # Layer 4: lock held too long
    verify["layers"]["L4_lock_held_too_long"] = {
        "test_id": "test_tick_lock_released_before_job_execution",
        "verify": run_test("tests/cron/test_scheduler.py::test_tick_lock_released_before_job_execution"),
        "evidence_required": "fcntl.LOCK_EX released after get_due_jobs + advance_next_run, NOT after ThreadPoolExecutor",
    }
    # Layer 5: ticker keep alive (already merged baseline)
    verify["layers"]["L5_ticker_keep_alive"] = {
        "merged": True,
        "commit_sha": "07424da76f60ce1efee5239e9d324a3069873494",
        "evidence_required": "Already merged in v0.18.x",
    }
    # sibling PRs (PR-dedup fire)
    verify["sibling_prs"] = [
        {"pr": 61674, "state": "open", "title": "lazy jobs.json path"},
        {"pr": 39782, "state": "open", "title": "timeout containment"},
        {"pr": 27492, "state": "merged", "title": "release tick file lock before executing due jobs"},
        {"pr": 50016, "state": "merged", "title": "ticker keep alive on BaseException"},
    ]
    # cross-cluster arrows
    verify["cross_cluster_arrows"] = [
        {"from": "F8", "to": "F9", "severity": "B", "interaction": "lock fail-open + session state integrity"},
        {"from": "F8", "to": "F11", "severity": "C", "interaction": "kanban_worker auto-approve + ticker keep alive"},
    ]
    return verify
```

## 输出

```json
{
  "pr_id": 61674,
  "verify_timestamp": "2026-07-18T18:35:00Z",
  "layers": {
    "L1_lazy_jobs_path": {
      "test_id": "test_public_io_after_late_env_repoint_leaves_old_file_untouched",
      "verify": "pass",
      "evidence": "import-time jobs.json byte-identical to sentinel"
    },
    "L2_timeout_containment": {
      "test_id": "test_run_job_does_not_hang_when_timeout_interrupt_is_ignored",
      "verify": "pass",
      "evidence": "_TIMED_OUT_RUNS skip later runs"
    },
    "L3_ticker_baseexception": {
      "test_id": "test_cron_ticker_keeps_running_after_systemexit",
      "verify": "pass",
      "evidence": "SystemExit does not kill ticker"
    },
    "L4_lock_held_too_long": {
      "test_id": "test_tick_lock_released_before_job_execution",
      "verify": "pass",
      "evidence": "fcntl.LOCK_EX released at correct moment"
    },
    "L5_ticker_keep_alive": {
      "merged": true,
      "commit_sha": "07424da76f60ce1efee5239e9d324a3069873494"
    }
  },
  "sibling_prs": [
    {"pr": 61674, "state": "open", "title": "lazy jobs.json path"},
    {"pr": 39782, "state": "open", "title": "timeout containment"},
    {"pr": 27492, "state": "merged", "title": "release tick file lock"},
    {"pr": 50016, "state": "merged", "title": "ticker keep alive"}
  ],
  "cross_cluster_arrows": [
    {"from": "F8", "to": "F9", "severity": "B"},
    {"from": "F8", "to": "F11", "severity": "C"}
  ],
  "action": "WAIT_L1_L2_MERGE_THEN_VERIFY"
}
```

## 判定

- 5/5 layer verify pass → SHIP with audit log
- L1 / L2 layer verify fail (open PR) → WAIT_L1_L2_MERGE_THEN_VERIFY
- L3 / L4 / L5 已 merged baseline, 任何 regression 立即 ABORT_SHIP
- cross_cluster_arrows severity-B → chief 6h SLA triage

## sibling PR dedup SLA (沿用 tick27 + tick34 PR-dedup 跨 family 累积)

- tick40 F8 sibling PRs: #61674 + #39782 = 2 open + #27492 + #50016 = 2 merged
- chief 6h 内 dedup 2 open PRs → primary PR 必含 L1 + L2 双重 fix
- 其他 PR 关闭 (模板: Closing in favor of #N)

## 1-line rationale

把 F8 cron-ticker-resilience-deck 5 issue 5 layer root cause cluster (#61674 + #39782 + #32612 + #27485 + #32666) 整合到一个可执行 skill, cron worker sibling sweep 必跑。

## pitfalls

- L1 lazy jobs.json path 必须用 sentinel test (沿用 #61674 PR #61674 实战)
- L2 timeout containment 必须 verify _TIMED_OUT_RUNS skip (沿用 #39782 PR)
- L3 BaseException catch 必须用 test_cron_ticker_keeps_running_after_systemexit (沿用 #32612 fix commit 07424da)
- L4 lock granularity 必须 verify LOCK_EX release after get_due_jobs + advance_next_run (沿用 #27492)
- 任一 layer regression → ABORT_SHIP

## 相关 references

- `references/cron-tick-mcp-writer.md` — tick32 canonical writer
- `references/tick33-deliverables.md` — F8 立卡 baseline
- `references/tick37-deliverables.md` — F11 + F8 5 install profile verify
- `references/tick39-deliverables.md` — tick39 invariant 7