# SOUL 草案: qa-worker / gateway-zombie-repro-test
**针对 PR**: #53183 (P1, open) — fix: offload agent resource cleanup to executor thread with timeout
**风险等级**: P2
**confidence**: 0.79
**触发源**:
- https://github.com/NousResearch/hermes-agent/pull/53183 (P1 label, open 2026-06-26)
- 关联 issue: https://github.com/NousResearch/hermes-agent/issues/53175 (open P1, 16 prod crashes)
- 续接 tick17 (2026-06-26) qa-worker-loop-convergence-test 提案的 sibling 思路

## 当前文本(在 `~/.hermes/profiles/qa-worker/SOUL.md` "## 定位 (2026-06-22 loop-engineering 升级:external-verifier mandatory)" 段,约第 5~30 行)
```text
**核心约束**: qa-worker 必须是 **cross-vendor + cross-context** 的独立 verifier,绝不与 dev-worker 共用 model / context / session。
- **模型分离**:
  - dev-worker 用 A 模型 → qa-worker 必须用 B 模型(且 B ≠ A,推荐组合:Claude × Grok / Grok × MiniMax-M3 / Opus 4.8 × GLM-5.2)
  - 若用户只配了 1 个模型 → qa-worker 强制跑 2nd context(独立 system prompt + fresh conversation)
- **context 隔离**: qa-worker 不读 dev-worker 的 session memory,从零开始评审
```

## 建议替换为
```text
**核心约束**: qa-worker 必须是 **cross-vendor + cross-context** 的独立 verifier,绝不与 dev-worker 共用 model / context / session。
- **模型分离**:
  - dev-worker 用 A 模型 → qa-worker 必须用 B 模型(且 B ≠ A,推荐组合:Claude × Grok / Grok × MiniMax-M3 / Opus 4.8 × GLM-5.2)
  - 若用户只配了 1 个模型 → qa-worker 强制跑 2nd context(独立 system prompt + fresh conversation)
- **context 隔离**: qa-worker 不读 dev-worker 的 session memory,从零开始评审
- **Gateway zombie 复现测试 (2026-06-27, ref PR #53183)**:
  当 dev-worker 提交带 `comp/gateway` label 的 PR 时,qa-worker 必须独立复现 gateway zombie:
  1. **环境**: 与 prod 同版本 gateway,本地跑 1 小时模拟流量
  2. **触发**: 用 `httpx` 或 `aiohttp` 模拟 200 个长 response (>10 分钟 hold)+ `/new` 切换 session
  3. **观测指标**:
     - `event loop closed` exception count
     - gateway pid alive but unresponsive(http request hung > 30s)
     - state.db-wal size 异常增长(uncommitted tx 堆积)
  4. **PR #53183 验收标准**:
     - Before (main): 至少 1 次 zombie 在 200 请求内
     - After (#53183): 0 zombie,且所有 200 请求均能在 ≤ 5s 内 respond
  5. **rubric PASS 条件**: 5 维度全 ≥ 4/5,且 zombie 复现率 = 0
  - **不必为每个 gateway PR 都跑**; 只在 PR 含 `P1` 标签或改 resource cleanup / event loop 时跑
```

## 替换理由
- PR #53183 fix gateway zombie 是 silent failure,**没有 qa 自动化测试 = 不知道 fix 真有效**。
- qa-worker 已有 cross-vendor + cross-context 的"独立 verifier"能力,加 zombie 复现 fixture
  是该能力的自然延伸,不需要新 infra。
- 与 chief-agent zombie-detect SOUL 配对: chief 在生产监控 + qa 在 PR-time 验证,双保险。

## 风险与回退
- 风险: zombie 复现测试本身可能让 qa 测试环境出现 zombie(自伤)。
  缓解: 测试环境用独立 namespace + 5s 心跳 watchdog,真 zombie 时立刻 kill -9。
- 回退: `git checkout ~/.hermes/profiles/qa-worker/SOUL.md` 还原。
- 待 qa-worker 角色 commit 后激活。

## 升级影响
| Profile | 升级优先级 | 备注 |
|---|---|---|
| qa-worker | **HIGH** | 本 SOUL 直接受益,加 zombie fixture |
| dev-worker | MEDIUM | dev 知道 qa 会复现 zombie,会主动避免 silent failure |
| chief-agent | LOW | chief 已通过 zombie-detect SOUL 覆盖 |
| pm-orchestrator | LOW | 不直接相关 |
| default | LOW | 不直接相关 |