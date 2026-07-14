---
name: hermes-async-completion-ownership-guard-v1
description: '验证 Hermes async delegation/background completion 的 session ownership、compression lineage 与 durable restore 行为。Use when: 新 CLI/TUI/gateway session 收到旧任务结果、/new 或 /clear 后仍注入旧 completion、ProcessRegistry restore/drain 代码变更、或 GH #64484/#63317/#63856 同族回归。'
version: 1.0.0
created_by: researcher
metadata:
  hermes:
    tags: [delegation, session-state, ownership, durable-restore, trust-boundary]
---

# Hermes Async Completion Ownership Guard v1

## 目标

阻止 durable async completion 被错误 session 消费。核心不是“尽量识别”，而是 **positive ownership**：consumer 必须证明自己拥有 event 的 origin session 或 compression lineage；无法证明就 fail closed。

## 触发条件

- 新启动 CLI 无操作却收到 `[ASYNC DELEGATION ... COMPLETE]`
- `/new`、`/clear`、old process exit 后仍收到旧 subagent 结果
- 修改 `tools/async_delegation.py`、`tools/process_registry.py`、CLI/TUI drain call site
- `origin_session`、`session_key`、compression lineage 任一字段缺失
- restored pending row 被 legacy unfiltered drain 消费

## 不变量

1. restored event 必须标 `restored=True`（只需 in-memory）。
2. restored event 必须有 `origin_session`；若有 compression，必须有 lineage 可解析。
3. consumer 只能在 `consumer_session == origin_session` 或属于允许的 compression lineage 时消费。
4. `drain_notifications()` 的 unfiltered legacy branch 不得消费 restored event。
5. keyless event 只允许 same-process + non-restored legacy path。
6. exactly-once：owner 成功消费后 durable row 变 delivered；foreign drain 不改变 durable pending。
7. `/new`、`/clear` 不继承旧 session completion。

## 标准流程

### Step 1：建立状态表

```text
origin_session | origin_lineage | consumer_session | restored | keyless | expected
A              | A>A2           | A               | true     | false   | consume once
A              | A>A2           | A2              | true     | false   | consume once
A              | A>A2           | B               | true     | false   | preserve pending
A              | A>A2           | empty           | true     | false   | preserve pending
same-process   | n/a            | empty           | false    | true    | legacy behavior
```

### Step 2：定位所有 drain call site

检查至少：

- CLI idle drain
- CLI post-turn drain
- TUI idle/post-turn drain
- Gateway completion inject path
- compression/session transfer path

任何 bare `drain_notifications()` 都要证明 queue 里不可能含 restored/foreign event，否则视为缺陷。

### Step 3：执行隔离测试

伪代码：

```python
old = persist_completed_delegation(origin_session="OLD_A", delivered=False)
registry = new_process_registry()  # restores pending completion
assert registry.drain_notifications(consumer_session="NEW_B") == []
assert durable_status(old) == "pending"
assert registry.drain_notifications(consumer_session="OLD_A") == [old]
assert durable_status(old) == "delivered"
```

### Step 4：覆盖 compression lineage

```python
assert owns(origin="A", lineage=["A", "A2"], consumer="A2") is True
assert owns(origin="A", lineage=["A", "A2"], consumer="B") is False
```

### Step 5：回归 `/new` / `/clear`

- dispatch async delegation
- 切换 session
- completion 到达
- 新 session transcript 必须 0 foreign completion
- owner resume 后只出现一次

## Acceptance contract

```yaml
session_ownership_provenance:
  origin_session: required
  origin_lineage: required_if_compressed
  consumer_session: required
  ownership_match: true
  restored_flag: true_if_rehydrated
  unfiltered_legacy_path: forbidden_for_restored_events
  exactly_once: true
```

## 失败判定

以下任一即 FAIL：

- foreign restored event 出现在新 session history
- unfiltered drain 消费 restored event
- foreign drain 后 durable row 从 pending 变 delivered
- owner resume 消费两次
- compression 后 owner lineage 无法消费
- keyless restored event 自动注入任意 active session

## 回退

- 无法安全判 owner：保留 pending，不投递；输出可观测 warning。
- 旧数据缺 ownership：隔离到 quarantine queue，禁止自动迁入新 session。
- 修复未 merged：默认关闭 durable cross-process auto-injection，保留 owner resume 手工路径。

## 证据

- GH #64484: <https://github.com/NousResearch/hermes-agent/issues/64484>
- PR #63494 durable completion: <https://github.com/NousResearch/hermes-agent/pull/63494>
- PR #63317 TUI ownership: <https://github.com/NousResearch/hermes-agent/pull/63317>
- PR #63856 `/new`/`clear`: <https://github.com/NousResearch/hermes-agent/pull/63856>

## Pitfalls

- “queue 是进程私有”在 durable restore 后不成立。
- `get_current_session_key(default="")` 为空不是安全 fallback；空值通常会落入 consume-all legacy path。
- 只修 TUI 不等于修 CLI；每个 surface 的 drain call site 都要单独验。
- interrupt in-flight child 不覆盖“child 已完成但未投递”的 durable row。
