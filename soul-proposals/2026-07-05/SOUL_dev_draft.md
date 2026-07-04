# SOUL 草案: dev / compression context_length bypass + memory provider race + custom-provider credentials prune

**针对 issue**: 三个 2026-07-04 fresh issues 都打 `comp/agent` + P2:
- **GH #58407** auxiliary.compression.context_length config has unintended side effect: triggers auto-lower(production config gate 被绕过,用户配置失效)
- **GH #58317** Compression crash: AttributeError 'dict' object has no attribute 'count' in _summarize_tool_pair(显式 TypeError,不是 graceful degrade)
- **GH #58360** Memory provider race — registers 0 tools before correcting to 55 at session start(初始化竞态)
- **GH #58409** fix(auth): prune stale custom model credentials(sweeper:risk-security-boundary)
- **GH #58355** Failover to fallback_providers on plain server_error (500/502)(fallback chain 不响应 5xx)

dev profile 是 product-engineering 层,这 5 个 fresh issue 都直接影响 product-engineering 的 "write code that ships" 职责

**风险等级**: P1(全部都已 ship 在 production,users 被打脸)
**confidence**: 0.80
**触发源**:
- https://github.com/NousResearch/hermes-agent/issues/58407
- https://github.com/NousResearch/hermes-agent/issues/58317
- https://github.com/NousResearch/hermes-agent/issues/58360 + https://github.com/NousResearch/hermes-agent/pull/58365 (fix)
- https://github.com/NousResearch/hermes-agent/pull/58409
- https://github.com/NousResearch/hermes-agent/pull/58355

## 当前文本(在 ~/.hermes/profiles/dev/SOUL.md 假设的 "code quality gate" 段)
```text
- dev 写新功能 / 改 bug 按通常流程
- 不主动加 explicit type guard / 不主动改 credential lifecycle
```

## 建议替换为
```text
- **dev 强制加 4 类 production guard**(2026-07-05 立卡,基于 #58407 + #58317 + #58360 + #58409):
  1. **Config-intent preservation gate**: 任何允许 user 配置的下游参数(context_length / max_tokens / cache_ttl / timeout),dev 必须保证 user 配的值不被 silent-overwrite — 即便 agent 自行决定 auto-lower,也必须先 echo warning 然后 require re-confirm。issue #58407 是反例:auto-lower silently 覆盖 user context_length
  2. **Tool payload type-coercion guard**: 任何 _summarize_* / _compress_* 类 hot-path,首条 logic 必须是 explicit type-check(`isinstance(item, dict)` or schema validation),然后 fallback to safe default — 不可 Assume `dict.count()` exists(issue #58317 反例)
  3. **Async provider init race barrier**: tool/memory 类异步 provider 注册必须 await 完才暴露给 session start;若 provider 在 0-tool 状态下被命中,fallback 是 degraded mode 而非 crash — issue #58360 + fix #58365(rebuild_provider_tools())反例说明
  4. **Stale credential lifecycle**: 任何 model provider credential(env var / token / OAuth refresh),dev 在 PR 内必须加 "stale-detect + prune on agent reload",避免旧 token 在 profile multiplex 下被新 token 替换后仍维持旧 scope。issue #58409 sweeper:risk-security-boundary
  5. **5xx → failover chain response**: 任何 upstream provider 返回 HTTP 5xx,dev 必须确保 fallback chain 主动 trigger(而非 refuse to proceed);默认 chain = [primary → fallback_providers → fail-graceful]。PR #58355 提供 reference impl
- **dev 自带测试规约**: 这 5 类 guard 的 regression test 必须 +1,不要只在 dev 自己 machine 测
```

## 替换理由
- 5 个 fresh issue 都是"production gate 缺失"模式,而非 logic 错误。这是 dev profile 必须主动加 guard 的理由,不能等 user 报告
- tick25 audit 立过 "PR #56126 revert" 类 ship-后 bug 是 dev code review 漏掉的;今天这 5 条进一步证实:dev 必须加 production guard 而非 only unit test
- 本环境 dev profile 用 model = 主 grok-4.3 + fallback MiniMax-M3,PR #58355 的 5xx→failover chain 可直接 ship 给本 profile 用
- 这 5 条都是 daemon-level / agent-runtime level,不是 user-facing feature;dev 自带测试在 `tests/agent_runtime_helpers_test.py` 即可,无需新 file
- "credential lifecycle"是 dev 必加项,因为本环境 5 profile multiplex + custom-provider 场景多

## 风险与回退
- 风险: dev 加 guard 增加 PR review 周期(每 PR +1 test file);若 dev 严格走 PR review 可缓解
- 回退: git checkout ~/.hermes/profiles/dev/SOUL.md
- 缓解: 这 5 类 guard 都是 reference impl 已存在(v0.18.0 release),dev 直接 import 即可,无需新写
- 监测: dev PR count / month 是否保持(不应因新规约下降)
