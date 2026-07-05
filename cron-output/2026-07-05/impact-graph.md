# 跨 profile 影响图 (2026-07-05)

> hermes-researcher-deep-tick-daily tick27 产出
> 扫描窗口:近 3 天(2026-07-02 ~ 2026-07-05)
> 触发信号:8 P1 open(全 silent-fail family) + 6 P1 closed-merged(config / telegram / compressor)

## 5-profile 影响图

| Profile | 直接影响 | 隐含影响 | 风险 | 处理 |
|---|---|---|---|---|
| **chief-agent** | 同 root cause 24h 内 ≥ 3 PR 抢同一 bug(#58777/#58874/#58992 都抢 #58818)→ review queue 稀释 | 跨月 silent-fail 复发(#49334→#54329→#58818→#58720)→ 架构问题,非个别 bug | P1 | SOUL draft `chief-agent-silent-fail-triage-2026-07.md` 立升级人工条件 |
| **pm-orchestrator** | silent-fail 验收清单必须包含 4 项 fail-injection(retry / log / receipt / dropped counter) | PR 重复修复冲突仲裁(24h 内 ≥ 3 PR 抢同一 bug 必须 dedup) | P1 | SOUL draft `pm-orchestrator-silent-fail-acceptance-2026-07.md` |
| **dev-worker** | async race condition 必修(asyncio.run + close + deliver / planned-restart / strict API) | integration test 强制 ≥ 100 次 stress loop,不能只 unit test | P1 | SOUL draft `dev-worker-async-race-test-2026-07.md` |
| **qa-worker** | Windows installer ship merge conflict markers(#59004)→ release verification 缺口 | 5 项 grep checklist 必须 ship 前 exit 0 | P1 | SOUL draft `qa-worker-release-grep-checks-2026-07.md` |
| **default** | 5/8 P1 直接命中 default profile 用法(cron / gateway / desktop / DeepSeek) | send-and-forget 路径必须 receipt + retry + dead-letter + drain | P1 | SOUL draft `default-silent-fail-defense-2026-07.md` |

## 跨 profile 依赖链详解

### 链 1: silent-fail cron delivery 复发链

```
PR #58777 (cron delivery before teardown)
  ↓ 触发 chief 升级
chief 升级 → 必须 dedup 同 root cause 抢的 PR (#58874 #58992)
  ↓ chief 仲裁 6h
单一 owner + 冻结其他 PR
  ↓ pm 拿到合并的 root cause fix
pm 把 silent-fail 验收 4 要素写进子任务 AC
  ↓ dev 拿新 AC 写 race condition 集成测试
dev 跑 ≥ 100 次 stress loop
  ↓ qa 验收
qa 跑 5 项 grep + 真复现 + 验收报告
  ↓ chief 关闭卡片
默认 agent 下次 silent-fail 不会复发
```

### 链 2: Windows installer ship 不安全代码链

```
PR #59004 (Windows installer ship merge conflict markers)
  ↓ 触发 qa 立即升级
qa 加 5 项 grep 到 release checklist
  ↓ qa 跑 scripts/release-grep-checks.sh
失败 → block ship + dev 重 build installer
  ↓ 通过 → ship
默认 agent 用户 fresh install 不再 SyntaxError
```

### 链 3: DeepSeek strict API 拒绝空 tool_calls

```
PR #58755 (DeepSeek v4 Flash HTTP 400 on empty tool_calls)
  ↓ dev 加 deepseek adapter 过滤空 array
dev-worker SOUL 加 "strict API 适配"红线
  ↓ pm 验证
pm 把 "strict API compatibility" 加进 AC 4 要素
  ↓ chief 升级 default SOUL
default agent 在向 strict API 发请求前主动 sanitize
```

## 触发条件摘要

本 tick 命中以下 3 条(详见 self-evolution skill Pitfalls "5-profile impact-graph 触发条件表"):

- [x] **单 issue P0 → 必画** (本期 0 P0 open,但 8 P1 都画了)
- [x] **单 P1 + 5 profile 都涉及** (#58818 集群 4/5 profile + #59004 3/5 profile 涉及 default)
- [x] **3+ P0 cluster 同 family** (本次为 8 P1 cluster,远超 3 阈值)

## 风险等级

- 全表 P1(8 P1 open + silent-fail 跨月复发) — 影响范围广,但 root cause 已有 3 PR 待选,**24h 内 chief 必须 dedup**
- 若 1 周内不解决 → 升级到 chief-agent 走 release-blocked 路径

## 处理建议

1. **chief 立即**:6h 内 dedup #58777/#58874/#58992,选 primary,关闭其他
2. **pm 立即**:把 silent-fail 验收 4 要素写进新派单 AC
3. **dev 立即**:给 primary PR 加 race condition 集成测试(≥ 100 次 stress loop)
4. **qa 立即**:跑 scripts/release-grep-checks.sh 给所有 artifact,确认无 #59004 复发
5. **default 立即**:把"send-and-forget 路径 receipt 必现"写进性格红线