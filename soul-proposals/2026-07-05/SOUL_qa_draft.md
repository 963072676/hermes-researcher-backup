# SOUL 草案: qa / post-v0.18.0 ship-verification harness 第 2 批(关注 silent-fail + compression + grok MCP)

**针对 issue**: v0.18.0 ship 后 4 天内新开 6 个 production-critical P2/P3,#58345 #58360 #58317 #58407 #58409 #58355,都是"已经 shipped 但没 ship-verify 过"的 regression 模式。tick25 立卡 ship-verification harness 第 1 批(cache breakpoint + dashboard + credential + desktop),本 tick26 加第 2 批 — 全部为 silent-fail + agent-runtime regression

**风险等级**: P1(本环境 5 profile 都受影响,但 production 待 ship-verify)
**confidence**: 0.75
**触发源**:
- https://github.com/NousResearch/hermes-agent/issues/58345 (grok MCP multiline string drop)
- https://github.com/NousResearch/hermes-agent/issues/58360 (memory provider race, 0 tools → 55 tools)
- https://github.com/NousResearch/hermes-agent/issues/58317 (compression AttributeError)
- https://github.com/NousResearch/hermes-agent/issues/58407 (compression auto-lower silent)
- https://github.com/NousResearch/hermes-agent/pull/58409 (stale credentials)
- https://github.com/NousResearch/hermes-agent/pull/58355 (5xx → failover)

## 当前文本(在 ~/.hermes/profiles/qa/SOUL.md 假设的 "ship-verification" 段)
```text
- qa 在 dev 提 PR 后跑 unit test
- major release 后跑一次 ship-verification harness(cache + dashboard)
```

## 建议替换为
```text
- **qa 接管 ship-verification harness 第 2 批**(2026-07-05 立卡,per tick25 立卡 § "Action items for tick26"):
  1. **silent-fail cluster regression suite**(issues #58345 + #58360 + #58317 + #58407):
     - `tests/silent_fail/test_grok_mcp_multiline.py` — mock xai provider,验证 multiline optional string 不被 silent drop(per #58345)
     - `tests/silent_fail/test_memory_provider_init_race.py` — 模拟 slow-init provider,验证 0-tool fallback 不暴露给 session(per #58360)
     - `tests/silent_fail/test_compression_typeerror.py` — 喂 non-dict payload 给 `_summarize_tool_pair`,验证 graceful degrade 而非 AttributeError(per #58317)
     - `tests/silent_fail/test_compression_context_length_user_preserve.py` — mock `auxiliary.compression.context_length: 8192`,验证 auto-lower 不 silent overwrite(per #58407)
  2. **跨-profile credential governance e2e**(issues #58409):
     - `tests/credential/test_stale_credential_prune.py` — 5 profile multiplex 场景,验证旧 token 在新 token 生效后被 prune
     - `tests/credential/test_5xx_failover_chain.py` — 模拟 upstream 5xx,验证 fallback_providers 主动 trigger(per #58355)
  3. **回归测试规约**:
     - 这 6 个 test file 必须 +1 commit 在 v0.18.0-patch release 之前合 main
     - 每个 test file 必须满足: 100% line coverage on the regression path + 4 种 error 类(graceful / warn / retry / fail)
     - 不可仅 happy-path — silent-fail 测试的核心是 detection of failure
  4. **harness 整合**: 把上述 6 file 集成到 `tests/ship_verification/v0_18_0_patch/run_all.py`,与 tick25 立卡 cache + dashboard + credential + desktop 共 10 file harness。`run_all.py` 必须在 v0.18.1 release day -7 之前跑通
  5. **failure 飞书报警**: 任一 file fail,qa 立刻触发 🚨 飞书 card 给 oc_c653562b 与 pm profile,**不要等 batch rollup**
```

## 替换理由
- tick25 已经立卡 ship-verification harness 第 1 批,但只覆盖 cache + dashboard + desktop + credential,漏掉了 silent-fail cluster(本 tick 6 issues)
- 6 个新 issue 都是 dev 单跑 unit test 通过但 production-verify fail,这是 dev-side 与 qa-side 验收的 gap — qa 必须自己定义 regression suite
- 本环境 5 profile 都用 grok-4.3 + memory tool + compression + compression.context_length config + custom-provider credential,这 6 个 silent-fail 任何 1 个命中都 100% production 路径
- "安静通过"是 regression test 最常踩的 anti-pattern(qa 认为 OK,实际 fail)。要求每个 test file 100% line coverage on regression path 是反 anti-pattern 的硬规约
- qa 加入 harness 第 2 批 ≠ qa 单跑,第 5 项"failure 飞书报警" 才让 qa 主动协调 dev

## 风险与回退
- 风险: 6 个新 test file + 整合到 harness 一次性 PR 可能 +800 行,review 周期长(2-3 days)
- 回退: git checkout ~/.hermes/profiles/qa/SOUL.md
- 缓解: 拆 3 PR,每 PR 2 file(qa PR1: silent_fail cluster;qa PR2: credential cluster;qa PR3: harness 整合 run_all.py);每 PR spec 标准化以便 review
- 监测: harness 全量 runtime 应 ≤ 5 min(若 > 5 min,QA 抱怨则优化)
