# SOUL 草案: dev / multiplexed-gateway test gate
**针对 issue**: P2 sweeper:risk-security-boundary on multiplexed profile env (#56508 hooks_dir, #56523 skills_sync_dir)
**风险等级**: P1
**confidence**: 0.75
**触发源**:
- https://github.com/NousResearch/hermes-agent/issues/56508 (P2 sweeper:risk-security-boundary)
- https://github.com/NousResearch/hermes-agent/issues/56523 (P2 sweeper:risk-session-state)
- 同根因:gateway 启动时把 `HOOKS_DIR` / `HERMES_HOME` / `SKILLS_DIR` 解析为 import-time 常量,在多 profile multiplexed 场景下被错路由

## 当前文本(在 ~/.hermes/profiles/dev/SOUL.md 假设的 "code review gate" 段)
```text
- 接收 PR 时按 type/severity 走 review
- 跨 profile 影响只在 release 后统一 review
```

## 建议替换为
```text
- 接收 PR 时若 issue 标签含 sweeper:risk-session-state 或 sweeper:risk-security-boundary,强制在 dev 复现多 profile multiplexed 环境
- multiplexed env 复现脚本必跑:启动 desktop tui_gateway + telegram gateway + matrix gateway,验证同一进程内不同 ContextVar 隔离
- 复现失败 → 自动 block PR
```

## 替换理由
- #56508 / #56523 是同根因(import-time resolve vs request-time ContextVar),dev 复现一次可同时验证两个 fix
- multiplexed gateway 是 desktop app 的默认拓扑,但 dev 单跑 unit test 抓不到 — 必须在 dev 流程加 e2e gate
- 阻止 P2 security bug 流入 release → 升级 v0.17.1 时不必再追 P0

## 风险与回退
- 风险:multiplexed e2e 跑 5-10min 拖慢 dev 节奏
- 回退:git checkout ~/.hermes/profiles/dev/SOUL.md
