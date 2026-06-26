# SOUL 草案: chief-agent / gateway-shutdown-backstop
**针对 issue**: #53107 — [P1] Gateway hangs after graceful shutdown — sys.exit(1) blocks on stuck non-daemon tool-worker thread
**风险等级**: P1
**confidence**: 0.82
**触发源**: https://github.com/NousResearch/hermes-agent/issues/53107 (created 2026-06-26 14:43Z, open, 0 comments)

## 当前文本(在 ~/.hermes/profiles/chief-agent/SOUL.md 第 N 行,需在 chief-agent 实际运行时核对)
```text
(待 chief-agent 在线 review 时定位确切行号 — 候选: 「健康检查」 段落)
```

## 建议替换为
```text
## Gateway 关停保护 (新增 2026-06-26, ref #53107)

任何 cron/feishu 任务完成后, gateway 进程必须能在 ≤ 5 秒内退出。
若 sys.exit() 因非 daemon tool-worker 线程被 block, 必须走 os._exit(1) 兜底。
在派工给 sub-delegate 时, 若返回 5xx 或超时, chief-agent 必须:
  1. 立即停派新工
  2. 触发 gateway state.db 落盘
  3. 通过 feishu DM (oc_c653562b) 报错, 含 last 50 行 stack
```

## 替换理由
- #53107 是 2026-06-26 14:43Z 新开的 P1, 症状是 gateway 在 graceful shutdown 时被非 daemon 工具线程 block。
- 兜底 os._exit(1) 解决 main thread 阻塞, 但会绕过 atexit handler — 可接受, 因为我们已有 state.db WAL 落盘保护。
- chief-agent 通过 cron 调度 sub-delegate, 是直接受影响方。

## 风险与回退
- 风险: os._exit 跳过 Python 析构, 可能丢 in-flight 写。但本 profile 关键数据已 WAL 化(state.db, memory_service), 风险可控。
- 回退: `git checkout ~/.hermes/profiles/chief-agent/SOUL.md` 即可还原。
- 待 chief-agent 角色 commit 后激活。

## 升级影响
| Profile | 升级优先级 | 备注 |
|---|---|---|
| chief-agent | HIGH | 派工链路核心 |
| pm-orchestrator | MEDIUM | 间接通过 cron |
| dev-worker | MEDIUM | 长期任务遇 shutdown 风险 |
| qa-worker | LOW | 不直接调度 gateway |
| default | HIGH | profile 自身 cron 走 gateway |
