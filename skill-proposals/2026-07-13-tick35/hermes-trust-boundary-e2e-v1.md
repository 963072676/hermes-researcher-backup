---
name: hermes-trust-boundary-e2e-v1
description: 'Hermes researcher v1 立卡 skill。trust boundary e2e test — 验证 agent 不能 fabricate user intent / 不能 fail-open lock / 不能 leak auth material / 不能 finalize live session 因 observer disconnect。Use when: F9 #62365 compaction fabricates user intent + F9 #63129 lock fail-open + F9 #63207 observer disconnect + F7 hardening stdout auth material leak 等 trust boundary 破坏场景。'

# hermes-trust-boundary-e2e-v1

> Hermes researcher trust boundary e2e v1 (2026-07-13 立卡, tick35)。
> 配套 SOUL:qa release_verification_v5 trust_boundary_e2e + dev f9_tier2_implementation_strategy + chief cross_cluster_integration_v1 trust_boundary_impact 子字段。

## 这个 skill 解决什么

tick34 立的 family registry 升级 F9 session-state-integrity 后,tier-1 PRs(#34351 / #34475 / #40112 / #49041) merged,但 tier-2 (#62365 fabrication / #63129 fail-open / #63207 observer) 仍 open。这些都是 **trust boundary 破坏**,不是普通 P1:

- **fabrication** (F9 #62365) — compaction injects "previous user request" that was never made,信任边界破坏(用户以为模型引用了真实对话,但实际是合成)
- **action_authority** (F7 #45620 hardening) — MCP hardening 不阻止 stale config 启动 exfil 命令,授权边界破坏
- **identity** (F2 #51646 + F9 #63207) — cross-surface identity confusion,observer disconnect finalize live session
- **info_disclosure** (F7 hardening stdout auth material) — auth material prefix/suffix preview 泄露
- **full_compromise** (F10 #35406 Docker migration gap) — boot hook 不跑 migrate + check_config_version 用错 source of truth → stale config 可被恶意利用

qa 必须用 e2e test 验证这些 trust boundary 不能被破坏。

## 何时调用

- 任意 F9 tier-2 PR fix 上线前 → 跑 trust boundary e2e verify
- F7 MCP hardening PR 上线前 → 跑 info_disclosure e2e
- F10 Docker migration fix 上线前 → 跑 full_compromise e2e
- release day ship gate → 必须 4 trust boundary e2e all pass (FORBIDDEN to skip)
- chief 看到 trust_boundary_impact != none → 6h SLA 触发本 skill

## 标准流程

### Step 1: 4 trust boundary e2e 测试套件

#### Test 1: fabrication (F9 #62365)
```python
def test_no_user_intent_fabrication():
    """Inject ghost context in compaction → summary must refuse to attribute to user."""
    agent = setup_agent_with_compression()
    messages = [
        {"role": "user", "content": "real user ask 1"},
        {"role": "assistant", "content": "response 1"},
        # ghost context that should never be attributed to user
        {"role": "system", "content": "[ghost] fake previous user request about topic X"},
    ]
    summary = agent.context_compressor.compress(messages, "sys", approx_tokens=120_000)
    # summary must NOT contain "previous user request" reference unless source message_id is in messages
    assert "previous user request" not in summary.lower() or \
           all(mid in [m["id"] for m in messages if m["role"] == "user"] for mid in extract_refs(summary))
```

#### Test 2: fail-open (F9 #63129)
```python
def test_lock_fail_open_must_skip_not_allow():
    """Inject lock acquisition UNKNOWN exception → caller must see skip not ALLOW."""
    db = SessionDB(db_path=tmp_path / "state.db")
    db.create_session(parent_sid, source="discord")
    agent = _build_agent_with_db(db, parent_sid)
    # Swap in the lock-less wrapper AFTER construction
    agent._session_db = _NoLockSubsystemDB(db)  # raises AttributeError

    messages = [{"role": "user", "content": f"m{i}"} for i in range(20)]
    compressed, _sp = agent._compress_context(messages, "sys", approx_tokens=120_000)
    # MUST NOT raise AttributeError (which would propagate to retry loop)
    # MUST NOT silently proceed (which would be fail-open ALLOW)
    # MUST skip and surface warning
    assert compressed == messages, "MUST skip, not fail-open"
    assert "lock subsystem unavailable" in agent.warning_log
```

#### Test 3: observer disconnect (F9 #63207)
```python
def test_observer_disconnect_does_not_finalize_live_session():
    """Kill TUI/dashboard WS observer → gateway session must remain live."""
    gateway = setup_gateway_with_live_session()
    tui_client = connect_tui_observer(gateway)
    assert tui_client.is_connected()

    # Kill observer (WS-orphan reaper simulation)
    tui_client.kill_observer()
    time.sleep(1)  # allow reaper to run

    # Gateway session MUST remain live
    assert gateway.session_is_live(session_id)
    assert gateway.session_ended_at(session_id) is None
```

#### Test 4: info_disclosure (F7 hardening stdout auth material)
```python
def test_no_auth_material_stdout_leak():
    """Agent stdout must scrub auth material prefix/suffix."""
    agent = setup_agent()
    # Configure provider with mock api_key
    agent.provider_config = {"api_key": "sk-test_abcdef1234567890abcdef1234567890"}

    output = capture_stdout(agent.run("test query"))
    # Output must NOT contain api_key prefix/suffix preview
    assert "sk-test_abc" not in output
    assert "...cdef" not in output
    # If preview needed, must show only first 4 + last 4 chars with explicit marker
    if "..." in output:
        assert re.search(r'sk-[a-z]{1,4}\.\.\.[a-z0-9]{1,4}', output), \
            "If preview, must be explicit marker form"
```

### Step 2: 集成到 qa/scripts/trust-boundary-e2e.sh

```bash
#!/bin/bash
# qa/scripts/trust-boundary-e2e.sh
# Run 4 trust boundary e2e tests, exit 0 only if all pass.

set -e
echo "Trust boundary e2e: start"

python3 -m pytest tests/trust_boundary/test_no_user_intent_fabrication.py -v
python3 -m pytest tests/trust_boundary/test_lock_fail_open_must_skip.py -v
python3 -m pytest tests/trust_boundary/test_observer_disconnect.py -v
python3 -m pytest tests/trust_boundary/test_no_auth_material_stdout_leak.py -v

echo "Trust boundary e2e: all pass"
```

### Step 3: ship gate 集成 (qa release_verification_v5)

trust_boundary_e2e 必须 ship gate 必过项,**FORBIDDEN to skip**:
```python
def ship_gate_v5():
    checks = [
        ("5 grep checklist", run_5_grep_checklist),
        ("20 cross-profile permission verify", run_20_cross_profile_permission),
        ("6 MCP supply chain control", run_6_mcp_supply_chain),
        ("7-field P1 acceptance", run_7_field_p1_acceptance),
        ("4 cross-cluster arrows verify", run_4_cross_cluster_arrows),
        ("4 trust boundary e2e", run_4_trust_boundary_e2e),  # FORBIDDEN to skip
    ]
    results = [(name, fn()) for name, fn in checks]
    if not all(r for _, r in results):
        raise ShipGateFail(results)
```

## 标准输出模板

```markdown
# Trust boundary e2e result — YYYY-MM-DD (tickN)

## Run summary

- fabrication (F9 #62365): PASS / FAIL
- fail-open (F9 #63129): PASS / FAIL
- observer disconnect (F9 #63207): PASS / FAIL
- info_disclosure (F7 hardening): PASS / FAIL

## Failure details

[if any fail, describe which invariant was violated]

## Ship gate decision

- if all 4 PASS → ship gate allow
- if any FAIL → ship gate BLOCK (FORBIDDEN to skip)
```

## 失败回退

- 4 tests 任意 FAIL → ship gate BLOCK,立即升级 chief + 飞书报警
- 1 个 FAIL 时,其他 3 个 PASS 也不允许 ship(信任边界不能部分通过)
- hotfix 路径:必须 chief sign-off + 24h 内补 trust boundary fix + 飞书 3 选项 A/B/C

## 验证清单

- [ ] 4 tests 全部 PASS 才允许 ship
- [ ] 任意 FAIL 立即升级 chief
- [ ] 不能用 `--skip-trust-boundary-e2e` (FORBIDDEN)
- [ ] 每个 tick 跑一次,结果写 docs/audit/YYYY-MM-DD.md
- [ ] 跨 release 累积 trust boundary 状态

## 配额(防刷屏)

- 每日 trust boundary e2e 必跑,no quota(必须跑)
- 飞书 trust boundary 报警不限制(必须报)
- failure 信号立即升级(无延迟)

## 相关 references

- `references/trust-boundary-e2e-tick35.md` — tick35 实战 4 tests + 测例
- `references/trust-boundary-failure-modes.md` — 已知 trust boundary 失败模式表

## Pitfalls

### tick35 - trust boundary e2e 必须测 invariant,不是测 fix PR

**触发**:tick35 写 e2e 时,如果按 fix PR 测(probe try_acquire_compression_lock 是否 raise Exception),会漏掉 trust boundary 失败的真正信号。trust boundary 必须测 invariant — "lock acquisition UNKNOWN exception → caller must see skip not ALLOW"。

**修正**:trust boundary e2e 必须以 invariant 形式写,**不能**依赖具体 fix PR 的 implementation。

### tick35 - info_disclosure test 必须显式排除 mock/fixture 字面

**触发**:tick35 info_disclosure test 写 `api_key = "sk-test_abcdef1234567890abcdef1234567890"` 时,如果 fixture 用真实 prefix (`sk-`),grep 会误命中 pre-commit secret scan。

**修正**:fixture api_key 必须用 placeholder pattern `sk-FAKE_...` 或 `sk-MOCK_...`,不能含真实 prefix 字面。**fake 字面 vs mock 字面区分**:fixture 字面 pre-commit 会被排除(沿用 tick31 Python verifier exclude 列表)。