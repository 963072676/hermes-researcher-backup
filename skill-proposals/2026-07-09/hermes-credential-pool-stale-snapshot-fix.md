---
name: hermes-credential-pool-stale-snapshot-fix
description: 'Hermes Agent `_restore_primary_runtime` credential pool bypass 修复 skill。用于 #25205 + #15298 + #15434 family 立卡 (60 天 open,3 PR 抢修)。Use when: 任何 _restore_primary_runtime / pool.select() / cross-provider fallback 路径相关的 P1,或 cron worker 自检时发现 api_key 用 stale snapshot 而非 pool current best。'
version: 0.1.0
author: Hermes researcher (tick31)
license: MIT
created_by: agent
metadata:
  hermes:
    tags: [credential-pool, fallback, restore-runtime, dev-pattern]
    related: [hermes-pr-dedup-arbitrator, hermes-installer-post-install-smoke]
---

# hermes-credential-pool-stale-snapshot-fix

## 这个 skill 解决什么

#25205 (2026-05-13) `_restore_primary_runtime bypasses credential pool`:
- **root cause**: `run_agent.py:8908` 在恢复 primary runtime 时用 stale snapshot 的 `api_key`,不 consult 当前的 credential pool (`self._credential_pool`)
- **影响**: token revocation (401) / exhaustion (429/402) / rate-limit cooldown → fall through to cross-provider fallback
- **60 天 open** (2026-05-13 → 2026-07-09),fix PRs:
  - #25206 (jmmaloney4) — primary candidate
  - #25730 (dusterbloom) — overlapping
  - #53913 (teknium1) — merge review gate

**关联**:
- #15298 / #15434 — same `_restore_primary_runtime()` credential pool bypass,但 focus on exhaustion/cooldown
- #60955 — `_fallback_index` 不回滚(family cluster)

## 触发条件

- 任何 PR 含 `_restore_primary_runtime` 但 diff 不含 `pool.select()`
- chief 触发 PR dedup (#25205 触发条件)
- cron worker 报 fallback chain issue + API key rotation 失败
- 任何 cross-provider fallback 触发的 P1

## 标准流程

### Step 1: 验证 PR 是否含 pool.select()

```bash
PR_NUMBER=$1
gh pr view $PR_NUMBER --json files

# 必查 3 处
gh pr diff $PR_NUMBER -- run_agent.py          # _restore_primary_runtime 路径
gh pr diff $PR_NUMBER -- pool/__init__.py      # pool.select() 实现
gh pr diff $PR_NUMBER -- tests/pool/test_stale_snapshot.py  # regression test
```

### Step 2: 实施完整修复

```python
# run_agent.py L8908 (_restore_primary_runtime)
def _restore_primary_runtime(self):
    # OLD (stale snapshot):
    # self.api_key = rt["api_key"]

    # NEW (consult pool):
    self.api_key = rt["api_key"]  # restore from snapshot first
    self.base_url = rt["base_url"]
    self.client = rt["client"]

    # NEW: consult credential pool for current best entry
    if hasattr(self, "_credential_pool") and self._credential_pool:
        best_entry = self._credential_pool.select()
        if best_entry:
            self.api_key = best_entry.api_key
            self.base_url = best_entry.base_url
            # NEW: rebuild client with new credentials
            self.client = build_client(self.api_key, self.base_url)

    # NEW: reset fallback index (沿用 #60955 fix)
    self._fallback_index = 0
```

### Step 3: pool.select() 实现参考

```python
# pool/__init__.py
class CredentialPool:
    def __init__(self, entries: List[CredentialEntry]):
        self.entries = entries
        self.exhausted = set()  # entries that hit 429/402

    def select(self) -> Optional[CredentialEntry]:
        """Return current best entry, skipping exhausted/revoked."""
        available = [e for e in self.entries if e.id not in self.exhausted]
        if not available:
            return None
        # Round-robin or weighted (by health score)
        return available[0]
```

### Step 4: regression test (5 case)

```python
# tests/pool/test_stale_snapshot.py
def test_restore_with_pool_consults_pool():
    """#25205 核心 case: _restore_primary_runtime must call pool.select()."""
    agent = AIAgent(...)
    agent._credential_pool = mock_pool(
        entries=[
            CredentialEntry(api_key="stale_key", exhausted=True),
            CredentialEntry(api_key="fresh_key", exhausted=False),
        ]
    )
    agent._restore_primary_runtime()
    assert agent.api_key == "fresh_key"  # NOT "stale_key"

def test_restore_without_pool_uses_snapshot():
    """Backwards compat: pool absent → snapshot still works."""
    agent = AIAgent(api_key="snapshot_key")
    agent._restore_primary_runtime()
    assert agent.api_key == "snapshot_key"

def test_restore_with_empty_pool_uses_snapshot():
    """Pool empty → snapshot fallback."""
    agent = AIAgent(api_key="snapshot_key")
    agent._credential_pool = mock_pool(entries=[])
    agent._restore_primary_runtime()
    assert agent.api_key == "snapshot_key"

def test_restore_resets_fallback_index():
    """#60955 cross-link: _fallback_index must reset."""
    agent = AIAgent(_fallback_index=5)
    agent._restore_primary_runtime()
    assert agent._fallback_index == 0

def test_pool_skips_revoked_entries():
    """Token revocation (401) → entry marked exhausted."""
    pool = CredentialPool(entries=[
        CredentialEntry(api_key="k1", exhausted=True),  # revoked
        CredentialEntry(api_key="k2", exhausted=False),
    ])
    assert pool.select().api_key == "k2"
```

## 评分模板 (per PR candidate #25205)

```yaml
pr_candidate:
  number: #X
  files_modified:
    - run_agent.py: yes/no  # _restore_primary_runtime 路径 (REQUIRED)
    - pool/__init__.py: yes/no  # pool.select() 实现
    - tests/pool/test_stale_snapshot.py: yes/no  # regression test (REQUIRED)
  scores:
    pool_consults: 0-3  # 0=无 pool.select, 3=完整
    fallback_index_reset: 0-3  # 沿用 #60955
    test_coverage: 0-3  # 5 regression test
    backwards_compat: 0-3  # pool absent/empty 仍 work
  decision: primary | non_primary | reject
  rationale: "reasoning"

tick31_实战:
  primary_candidate: #53913 (teknium1, merge review gate)
  close:
    - #25206 (jmmaloney4) — closing in favor of #53913
    - #25730 (dusterbloom) — closing in favor of #53913
```

## 失败回退

- pool absent → snapshot fallback (backwards compat)
- pool empty → snapshot fallback (graceful degradation)
- pool.select() 抛异常 → 捕获 + log warning + fallback to snapshot
- PR 缺 regression test → reject (要求补 5 case)

## Pitfalls

### tick31 - _restore_primary_runtime 路径上有多处相似实现

**触发**: hermes-agent 历史代码可能有多处 `_restore_*` 函数,都需要 pool consultation。

**修正路径**: grep 找所有 `_restore_` 函数,逐一 patch,共享 helper 函数 `_restore_with_pool_consult()`。

### tick31 - pool.select() 实现差异大

**触发**: 不同 pool 实现 (round-robin / weighted / LRU),PR candidate 可能依赖特定实现。

**修正路径**: 在 PR review 时 explicit 标注 pool.select() 实现 strategy,避免 #25206 vs #25730 vs #53913 三 PR strategy 不一致。

### tick31 - fallback index reset 与 pool select 顺序

**触发**: pool select 后必须 reset fallback index,否则 stale state。

**修正路径**: 顺序固定 — pool.select() → fallback_index reset → done。

## 关联 references

- 沿用 dev-agent SOUL `fallback_chain_index_reset_pattern_v1` 段
- 沿用 chief-agent SOUL `chief_dedup_protocol_v1` 段 (PR dedup)
- 沿用 qa-agent SOUL `pr_dedup_test_coverage_v1` 段