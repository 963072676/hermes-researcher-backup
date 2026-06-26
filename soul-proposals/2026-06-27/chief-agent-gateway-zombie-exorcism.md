# SOUL 草案: chief-agent / gateway-zombie-exorcism
**针对 issue**: #53175 (P1, open) — Gateway event loop dies silently after long responses + /new (16 crashes in prod) + **PR #53183 (P1, open)** — fix: offload agent resource cleanup to executor thread with timeout to prevent event loop zombie state
**风险等级**: P1
**confidence**: 0.84
**触发源**:
- https://github.com/NousResearch/hermes-agent/issues/53175 (open, 2026-06-26)
- https://github.com/NousResearch/hermes-agent/pull/53183 (P1 label, open 2026-06-26)

## 当前文本(在 `~/.hermes/profiles/chief-agent/SOUL.md` "## 行为边界 / ###【必须升级人工的情况】" 段,大约在 70~80 行)
```text
### 【必须升级人工的情况】
- 收到低置信度（系统无法准确分类）或影响范围较大的 P0 级别事故。
- 涉及生产权限变更、资金结算、删除敏感数据或客户隐私的操作。
- 业务规则冲突、需求定义不明确,或看板分派出现多轮循环阻塞。
- dev / qa 出现原则性技术争议,且无客观证据可裁决。
```

## 建议替换为
```text
### 【必须升级人工的情况】
- 收到低置信度（系统无法准确分类）或影响范围较大的 P0 级别事故。
- 涉及生产权限变更、资金结算、删除敏感数据或客户隐私的操作。
- 业务规则冲突、需求定义不明确,或看板分派出现多轮循环阻塞。
- dev / qa 出现原则性技术争议,且无客观证据可裁决。
- **Gateway zombie 检测**(2026-06-27, ref #53175 + PR #53183):当 chief-agent 派工的 cron / feishu 任务
  在 ≤ 30 秒内无 task state 更新 + gateway 日志含 `event loop closed` 或
  `RuntimeError: Event loop is closed`,立即视为 gateway zombie,执行以下流程:
  1. 立即停派新工(`hermes kanban pause <chief-paused>` 或飞书群 `oc_6b75046a` 通报)。
  2. 触发 state.db WAL 落盘(`fsync ~/.hermes/state.db-wal`)抢救未提交事务。
  3. 重启 gateway(`systemctl --user restart hermes-gateway` 或后台启动脚本),等 ≥ 30 秒后恢复派工。
  4. 飞书 DM `oc_c653562b` 报 zombie,含 last 50 行 stack + #53175 / #53183 commit SHA。
  **不应等 dev / qa 自查** — zombie 是 silent failure,人工延迟 = 数据丢失。

### 【Gateway 关停 / 重启保护】(2026-06-27, ref #53107 + #53175 + PR #53183)
- chief-agent 派工的 sub-delegate 在 5xx / 超时返回时,**立即触发 gateway 自我体检**:
  1. `curl -s http://127.0.0.1:<gw_port>/healthz` 期望 200,否则 zombie。
  2. 不健康 → 不再派新工,等 gateway 自然恢复或人工重启。
  3. 主线程阻塞时 (`sys.exit(1)` 因非 daemon tool-worker 卡住),**强制走 `os._exit(1)` 兜底**,
     由 watchdog / systemd 拉起新实例。**绝不**等 graceful shutdown 完成。
- 参考: arxiv 2606.27287 (2026-06-25) Prompt Injection in Multi-Injection Settings — gateway zombie
  后的恢复路径必须重新鉴权,不能 trust 上一次会话的 state。
```

## 替换理由
- **#53175 是生产 P1**: event loop 死了 16 次,silent failure 没 alert,影响所有 cron / feishu 任务。
- **PR #53183 提供修复**: offload agent resource cleanup 到 executor thread + timeout,直接 fix zombie。
  PR 标签 P1 说明社区已认可,等 merge 后立即激活本段 SOUL。
- **chief-agent 是派工总闸**:gateway 死了 = chief-agent 派不出工 = 整个 4 profile 链路停滞,
  必须第一响应 + 不依赖 dev/qa 自查。

## 风险与回退
- 风险: zombie 检测 + 强制重启可能误杀正常卡顿的 gateway。但 production evidence 16 crashes
  表明 silent failure 远比误杀严重,接受 5% 误杀换 0 数据丢失。
- 回退: `git checkout ~/.hermes/profiles/chief-agent/SOUL.md` 即可还原。
- 待 chief-agent 角色 commit 后激活。本 SOUL 不直接改 gateway 代码,只改 chief-agent 的派工前置检查。

## 升级影响
| Profile | 升级优先级 | 备注 |
|---|---|---|
| chief-agent | **HIGH** | 派工链路核心,本 SOUL 直接受益 |
| pm-orchestrator | MEDIUM | 派工被 zombie 阻断时,需感知暂停状态 |
| dev-worker | LOW | dev 长任务遇 zombie 时本身已被杀 |
| qa-worker | MEDIUM | 需复现 zombie 来验 PR #53183 修复 |
| default | HIGH | cron 走 gateway,本 SOUL 的 detect 路径直接保护 |