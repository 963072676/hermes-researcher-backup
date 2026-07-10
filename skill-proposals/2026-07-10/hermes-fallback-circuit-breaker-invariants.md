---
name: hermes-fallback-circuit-breaker-invariants
description: 'Tick32 立卡。Fallback chain `_try_activate_fallback` 调合 circuit-breaker + 全局 patch。沿用 GH #24996 + 3 PR (#24998/#25059/#53909) dedup。提供 test template + production-ready patch。当 provider chain fallback 耗 host memory P1 触发或 researcher 监控 dev acceptance 缺位时使用。'
version: 0.1.0
created: 2026-07-10
category: mlops/inference
platforms: [linux, macos]
metadata:
  hermes:
    tags: [provider, fallback, circuit-breaker, dev-acceptance, release-verification]
    related: [hermes-cross-platform-redact-call-site-audit, hermes-researcher-self-evolution-v1]
---

# hermes-fallback-circuit-breaker-invariants

> Hermes fallback chain circuit-breaker baseline + test template
> 沿用 GH #24996 (open since 2026-05-13) + tick32 SOUL_dev 草案

## 触发条件

- provider chain fallback P1 触发 (GH #24996)
- v0.19.0 ship gate 需要 circuit-breaker invariant
- cron tick32+ researcher 监控 dev acceptance 缺位 (PRs open > 60 天)

## 修复路径契约(沿用 #24998 recommended)

`run_agent.py::HermesAgent._try_activate_fallback` (~line 6285) 必须加:

1. **Throttle**: `≥ 2s` min interval between consecutive activations
2. **Breaker**: `≥ 5 activations in 60s` → return `False` (chain-exhausted
   现有 caller cleanly handle)
3. centralize in helper `_fallback_circuit_breaker_check()` at top of
   `_try_activate_fallback`
4. tester: `tests/agent/test_fallback_circuit_breaker.py` (≥ 5 case)

## production patch template

```python
# run_agent.py — at top of _try_activate_fallback (~line 6285)

from collections import deque
import time


class _FallbackCircuitBreaker:
    """Per-instance fallback activation circuit breaker.

    Invariants:
    - ≥ 2s between consecutive activations (throttle)
    - ≥ 5 activations in 60s → return False (breaker)

    Replaces tight retry loops in rate-limit-triggered switch
    (~line 10417) and non-retryable client error switch (~line 10677).
    """

    THROTTLE_SECONDS = 2.0
    WINDOW_SECONDS = 60.0
    MAX_ACTIVATIONS_IN_WINDOW = 5

    def __init__(self):
        self._last_activation: float = 0.0
        self._window: deque[float] = deque()

    def allow(self) -> bool:
        """Return True if next fallback activation is allowed."""
        now = time.monotonic()
        # Throttle
        if (now - self._last_activation) < self.THROTTLE_SECONDS:
            return False
        # Window breaker
        cutoff = now - self.WINDOW_SECONDS
        while self._window and self._window[0] < cutoff:
            self._window.popleft()
        if len(self._window) >= self.MAX_ACTIVATIONS_IN_WINDOW:
            return False
        self._window.append(now)
        self._last_activation = now
        return True


# In HermesAgent.__init__:
self._fallback_breaker = _FallbackCircuitBreaker()


# In _try_activate_fallback (~line 6285), gate every activation:
def _try_activate_fallback(self, ...):
    if not self._fallback_breaker.allow():
        return False  # chain-exhausted signal, existing callers handle cleanly
    # ... existing body ...
```

## test template

```python
# tests/agent/test_fallback_circuit_breaker.py
import pytest
import time
from unittest.mock import patch


class TestFallbackCircuitBreaker:
    def test_throttle_2s_min_interval(self):
        """Two activations within 2s → second returns False."""
        from run_agent import _FallbackCircuitBreaker
        cb = _FallbackCircuitBreaker()
        assert cb.allow() is True
        assert cb.allow() is False  # immediately after

    def test_breaker_5_in_60s_returns_false(self):
        """5 activations in <60s → 6th returns False."""
        from run_agent import _FallbackCircuitBreaker
        cb = _FallbackCircuitBreaker()
        # 5 activations, time-travel between each
        with patch("time.monotonic") as mono:
            mono.return_value = 100.0
            for i in range(5):
                mono.return_value = 100.0 + i * 12  # 12s apart, all in window
                assert cb.allow() is True
            mono.return_value = 161.0  # 61s after start
            assert cb.allow() is False  # 6th in window

    def test_window_expiration_clears(self):
        """After WINDOW_SECONDS, activations expire and counter resets."""
        from run_agent import _FallbackCircuitBreaker
        cb = _FallbackCircuitBreaker()
        with patch("time.monotonic") as mono:
            mono.return_value = 100.0
            for _ in range(5):
                cb.allow()
            mono.return_value = 200.0  # 100s later, all expired
            assert cb.allow() is True  # window cleared

    def test_throttle_recovery_after_2s(self):
        """Activations after throttle window allowed."""
        from run_agent import _FallbackCircuitBreaker
        cb = _FallbackCircuitBreaker()
        with patch("time.monotonic") as mono:
            mono.return_value = 100.0
            assert cb.allow() is True
            mono.return_value = 101.0
            assert cb.allow() is False
            mono.return_value = 102.5
            assert cb.allow() is True

    def test_per_instance_isolation(self):
        """Two agents have independent breaker states."""
        from run_agent import _FallbackCircuitBreaker
        cb1 = _FallbackCircuitBreaker()
        cb2 = _FallbackCircuitBreaker()
        cb1.allow()
        assert cb2.allow() is True  # independent of cb1
```

## Pitfalls

- 漏 helper wrapper:某些 provider 调自己 `_switch_provider_safely` 而不是直接
  `_try_activate_fallback`,必须 audit 全 provider wrapper chain
- 时间源:`time.monotonic()` vs `time.time()` — monotonic 必须用 (避免 DST
  jump / system clock skew)
- per-instance vs global state:helper 是 per-HermesAgent-instance,不是
  class-level (避免 multi-agent interference)
- caller contract 改变:return False 现在可能是 chain-exhausted (旧 caller
  会再 retry),所以 caller logic 必须更新成 "Non-retryable, dont fall back again"

## v0.19.0 实装 schedule

1. **2026-07-13** (tick34): 立卡本 skill + patch 写 ready
2. **2026-07-15**: PR dedup 6h SLA 启动(dev lead 选 1 primary from
   #24998/#25059/#53909)
3. **2026-07-17**: merged fix + 5 case test pass
4. **2026-07-21**: ship v0.19.0

## verdict 倾向

**采纳:中-高** — 直接 harden provider chain robustness,本 cron worker
provider=minimax 受影响概率 mid-low。但 hardening wave II 已 ship,
circuit-breaker baseline 缺位是 release verification gap,fit dev PO 范围。
