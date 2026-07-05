---
name: cron-silent-fail-probe
description: 针对 cron delivery silent-fail cluster (#58818/#58720/#58755 等)的探针工具。Use when: 用户报告"cron 任务没执行"或"消息没收到"时,或 chief-agent 收到 silent-fail 升级,或 researcher tick 报 silent-fail P1 涌现。本 skill 跑一次 fail-injection 探针,定位是 gateway restart / interpreter shutdown / strict API reject 三类中的哪一种。
---

# cron-silent-fail-probe

## 何时调用

- 用户 / chief / dev 报 "cron 任务没执行"或"消息没收到"或"cron 跑了但 receipt 没看到"
- researcher tick 报 silent-fail cron cluster P1 涌现
- 升级人工条件触发:same root cause 24h 内 ≥ 3 PR

## 标准流程

1. **收集 baseline**:
   ```bash
   # 跑前先列 active cron jobs
   hermes cron list --json | jq '.[] | {id, schedule, last_run, last_status}'
   ```

2. **3 类 fail-injection probe** (按顺序跑,失败即停):
   - **Probe A — gateway planned-restart race**:
     ```bash
     # 在 cron 触发后 100ms 内 SIGTERM gateway
     # 验证 receipt 是否出现
     ```
   - **Probe B — interpreter shutdown race**:
     ```bash
     # 让 agent.close() 与 _deliver_result() 并发
     # 验证 RuntimeError 是否进 dead-letter
     ```
   - **Probe C — strict API reject**:
     ```bash
     # 构造空 tool_calls array, 验证 DeepSeek / strict API 是否 400
     # 验证 repair_message_sequence 是否提前过滤
     ```

3. **输出诊断**:
   - 三类 probe 全部 exit 0 → silent-fail 不是这 3 类,转 general async race 排查
   - Probe A fail → 推荐 PR #58874 / #58992 任一
   - Probe B fail → 推荐 PR #58777
   - Probe C fail → 推荐 dev-worker 加 deepseek adapter(per SOUL tick27 draft)

## 何时不该调用

- 用户报 "cron 完全没触发"(schedule 解析问题)— 用 `hermes cron list` 看 last_run,不需 silent-fail probe
- silent-fail 不是用户报,只是 researcher tick 观察 — 直接报 chief-agent,不调 probe

## 验证

- Probe 三类都要 exit 0 才算 skill 跑通
- 失败时必须输出 silent_fail_class 字段(A / B / C / unknown),便于 SOUL draft 跟进