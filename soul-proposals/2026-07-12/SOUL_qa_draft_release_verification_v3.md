# SOUL 草案 — qa — release verification v3 (tick33)

> Tick33 2026-07-12 | Author: researcher profile | Streak=9 zero-adoption
> Memory ID: b868be0c-772e-4031-9bc1-733c24801e19 (MCP pending_review) — family registry v8
> Family: 5 grep checklist (tick27) → 6 release verification gate (tick33)

## 触发 evidence (release verification 5 → 6 项升级)

| tick | 阶段 | checklist 项数 | 触发事件 |
|---|---|---|---|
| tick27 (2026-07-07) | v0.18.0 ship day +5 | **5** | #59004 installer artifact ship 合并冲突 (SyntaxError fresh install) |
| tick28 (2026-07-08) | v0.18.0 ship day +6 | 5 (沿用) | hardening wave II 11 PR 24h 集中合, cross-profile verify 缺位 |
| tick29 (2026-07-09) | v0.18.0 day-7 rediscovery | 5 (沿用) | --yolo broken + max_tokens silent drop + stdout auth material preview |
| tick30 (2026-07-09) | v0.18.1+v0.18.2 ship | 5 (沿用) | PR-dedup fires x3 |
| tick31 (2026-07-10) | v0.18.2 day +1 | 5 (沿用) | credential-pool-stale-snapshot family |
| tick32 (2026-07-10) | v0.18.2 day +2 | 5 (沿用) | MCP supply chain 5-control 立卡 |
| **tick33 (2026-07-12)** | v0.18.2 day +4 | **6** | silent-fail cron gateway still open + cron-ticker-resilience deck + MCP 6-control + family registry v8 |

## 草案 (qa SOUL v3 第 7 段追加)

```diff
+ ## Release Verification v3 (tick33 立卡)
+
+ **原则**:任何 v{x}.{y}.z release ship 前必须 6 grep checklist + 4 silent-fail scenario 全部 exit 0 才允许 ship。
+
+ 6 Grep Checklist (5 → 6 升级):
+ 1. 合并冲突标记 grep (`<<<<<<<` / `=======` / `>>>>>>>`) 必须 0 命中 (沿用 tick27)
+ 2. TODO FIXME 暴增必须 ≤ baseline + 10% (沿用 tick27)
+ 3. import smoke test 必须成功 — `python3 -c "import hermes_agent"` exit 0 (沿用 tick27)
+ 4. py_compile 必须 exit 0 — `python3 -m py_compile $(find . -name "*.py")` (沿用 tick27)
+ 5. 所有 JSON 必须 parse 成功 — `find . -name "*.json" -exec python3 -c "import json; json.load(open('{}'))" \;` exit 0 (沿用 tick27)
+ 6. **新增 (tick33)**: MCP supply chain 6-control scan — `_convert_mcp_schema()` 调用 `scan_mcp_description()` 必须存在 + `core/supply_chain.py` 已合 + `tirith` pipe-scan 必须 reject `curl|sh` / `npx|bash` / `wget|bash` 模式
+
+ 4 Silent-Fail Scenario (tick33 新增,沿用 tick33 SOUL_dev 4 验收清单):
+ A. **失败注入 — env spill**: 模拟 `HERMES_CRON_SESSION` 不清,验证 job 后 env 是否残留
+ B. **失败注入 — gateway deadlock**: 模拟 tool-call 第 2+ 次 API 永久挂死,验证 inactivity watchdog 是否触发
+ C. **失败注入 — MCP keepalive hang**: 模拟 MCP stdio 异常空响应,验证是否无限重连
+ D. **失败注入 — cron ticker death**: 模拟 BaseException escape,验证 ticker 是否 liveness heartbeat 触发重启
+
+ 验收标准: 6 grep + 4 scenario = 10 项 exit 0 才允许 ship;任意 1 项 fail → ship 阻断。
+
+ **family 标识**: `sweeper:risk-release-verification-v3`
```

## 配套 skill 升级

- `scripts/release-grep-checks.sh` 升级 — 加第 6 项 (MCP supply chain 6-control scan)
- `scripts/release-silent-fail-scenarios.sh` 新增 — 4 scenario 自动化跑
- 关联 tick27 `hermes-cross-platform-redact-call-site-audit` skill 沿用

## 优先级

P1: ship gate 是 release verification 根本缺口 (沿用 tick27 #59004 教训)

## 关联 references

- 草稿落地: 本文件
- MCP memory_id: b868be0c-772e-4031-9bc1-733c24801e19 (pending_review) — family registry v8 共用
- 关联 PR/issue: #59004 (installer 合并冲突), #62151 (gateway deadlock), #62212 (MCP keepalive), #32612 (cron ticker death), #45886 (MCP egress reject), #6336ad7 (supply chain scan)

## 下一步

1. user review → qa SOUL v3 第 7 段合并
2. `scripts/release-grep-checks.sh` 升级 — 加入第 6 项
3. `scripts/release-silent-fail-scenarios.sh` 落地 — 4 scenario 自动化
4. 任何 v{x}.{y}.z release ship 前必跑 — exit 0 才 ship