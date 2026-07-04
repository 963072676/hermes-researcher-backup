---
name: hermes-cron-silent-fail-probe
description: Hermes cron worker 端 silent-fail 三层防御 skill。Use when: research/chief/pm 任一 cron 跑完后,需 probe 是否 silent dropped(adapter WS reconnect 失败 / send_message 被 streaming 抑制 / retry exhausted)。覆盖 issue #58363 + #58379 + #50733 + #54329 + #49334 family — 5 个独立 cron delivery silent-fail pattern 已 confirmed sys-level。
---

# hermes-cron-silent-fail-probe

## 何时调用

- 任意 cron job 跑完后,主动调一次 `cron_silent_fail_probe(target, message)` 验证 delivery 是否真到达
- chief / pm 在 daily audit 时跑批量 `cron_silent_fail_audit()` 收 24h cron delivery receipt
- researcher / dev / qa 在新 cron spec 上线前,跑 `cron_silent_fail_dryrun()` smoke test

## 标准流程

### Layer 1 - pre-delivery probe(主动)

```python
def diagnose_delivery_path(target: str) -> dict:
    """
    对 feishu / yuanbao / qqbot / lark-streaming 任一 adapter:
    拉 health + last-reconnect-time + last-send-success
    return: {target, healthy, last_reconnect_seconds_ago, last_send_ok, suggested_fallback}
    """
    # 1. adapter.health_check(target) → bool
    # 2. adapter.last_reconnect(target) → epoch seconds
    # 3. adapter.last_send_success(target) → epoch seconds
    # 4. 若 any unhealthy OR last_reconnect < 30s OR last_send_ok is None:
    #    suggest_fallback = "feishu:oc_c653562b" (DM 是 reliable fallback)
    # 5. raise SilentFailRisk if suggest_fallback != target
```

### Layer 2 - post-delivery verification(60s 内核对)

```python
def verify_delivery(target: str, message_id: str) -> bool:
    """
    Tool return success: True 不等于 message 真的送达
    必须拉 read-receipt / ack / 内部 mirror state 二次确认
    """
    # 1. await adapter.get_message_receipt(target, message_id) → bool
    # 2. compare with previous probe — 若不一致 → silent fail
    # 3. return True iff receipt confirmed
```

### Layer 3 - daily silent-fail audit(08:00 UTC)

```python
def audit_24h_silent_fails() -> dict:
    """
    24h cron delivery audit:
    compare cron run_log (success_count) vs delivery receipt (actual_reached_count)
    """
    # 1. 拉过去 24h 所有 cron job run_log from ~/.hermes/cron/output/*
    # 2. 拉 adapter 端 delivery receipt (24h aggregate per adapter)
    # 3. mismatch = silent fail
    # 4. 若 mismatch > 5% → trigger 🚨 event
```

## 何时不该调用

- 同步实时用户对话(realtime 用户对话有 read-receipt 自然 indication)
- 用户的 deliver target 不在 adapter 列表(裸 IP / raw socket)

## 验证

- 三层都是可单测:
  - mock adapter.health_check / last_reconnect / last_send_ok
  - verify_delivery 必须区分 success: True vs receipt: True
  - audit_24h 跑 fixture (cron_run_log + adapter_receipt list)
- regression test 必须在 `tests/hermes_cron_silent_fail/test_three_layer.py`:
  - 4 个 silent-fail scenario(from issue #58363 + #58379 + #50733 + #54329)
  - 每个 scenario verify 三个 layer 都 catch
