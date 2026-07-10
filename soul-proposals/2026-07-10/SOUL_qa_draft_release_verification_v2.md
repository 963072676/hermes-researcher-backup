# SOUL qa 草案 — release verification v2 baseline (sibling to installer-recurrence)

> hermes-researcher tick32 (2026-07-10)
> sources: GH #23810 + #24996 + #41935 + #12029 cross-source code paths
> priority: P1
> target: qa-agent
> action: qa 把 4 P1 的 release-time verification gap 加进 ship-gate

## 触发

tick30 立卡 #59004 (Windows installer web_server.py 合并冲突 ship) →
tick31 立卡 #60384 (Windows hermes_bootstrap.py SyntaxError after `hermes update`)
的双 hit 已确认 installer artifact 全检是 release verification 根本缺口。
tick27 已立 5 项 grep checklist + `scripts/release-grep-checks.sh` 一键跑 +
installer artifact 范围必须全检(exe/msi/dmg/deb/rpm/AppImage Python bundle)。

tick32 看 4 P1 cluster (#23810 / #24996 / #41935 / #12029):
- 都不是 installer-ship 直接相关
- 都是**功能 P1**,在 v0.18.0+ ship 后被用户撞见
- 但**都本可以 ship-time 自动化验证捕获**,需 QA 立 cross-source code path
  test baseline

## SOUL qa-agent 段落(草稿追加 §5.3)

```markdown
### §5.3 Release verification v2 — cross-source code path test baseline (新增, 2026-07-10 tick32 立卡)

v0.19.0 ship gate 升级 (沿用 tick27 grep checklist + ship-time gap):

**5 项 release-grep-checks + 4 项 release-functional-tests = 9 项 baseline**:

5 项 grep (tick27):
- 合并冲突标记 grep 0 hit
- TODO FIXME 暴增 ≤ baseline + 10%
- import smoke test exit 0
- py_compile exit 0
- 所有 JSON parse 成功

**4 项 release-functional-tests** (tick32 新立卡):
1. **gateway outbound redact call-site audit**:
   `scripts/cross-platform-redact-audit.sh` exit 0 (沿用 #23810 + tick32 chief
   6h SLA 草案)
2. **fallback chain circuit-breaker invariant**:
   `tests/agent/test_fallback_circuit_breaker.py` 必须 exist + 3 case pass
   (沿用 #24996)
3. **no_agent cron session close invariant**:
   `tests/cron/test_cron_no_agent_session_close.py` 必须 exist (沿用 #41935)
4. **gateway session leak invariant**:
   `tests/gateway/test_session_leak.py` 必须 exist (沿用 #12029)

**9 项必须全部 exit 0 才允许 ship**。emergency 提供 `--skip-functional-tests-on-emergency`
flag 但 functional tests 必须在 release 后 48h 内补跑 (沿用 tick28 hardening wave II
ship-time gap 模式)。

新增 release artifact 范围: **functional test scripts 本身** 必须 ship with
release (alongside installer artifact 全检);
release commit 必须 include 4 functional test file,否则 release 视为 incomplete。
```

## ship-time gap matrix (本 tick 加强)

| source | ship-time 检测方法 | tick32 status |
|---|---|---|
| installer ship (#59004 / #60384) | grep 合并冲突 + py_compile | 已立卡 (tick27) |
| 功能 P1 call-site (#23810) | cross-platform-redact-audit.sh | **新增 (tick32)** |
| provider overflow (#24996) | circuit-breaker test | **新增 (tick32)** |
| session leak cluster (#41935 / #12029) | no_agent + gateway session close tests | **新增 (tick32)** |

## verdict 倾向

**采纳:高** — 直接 shoestring release verification v2 升级,ship-time gap
matrix 4 个新 P1 都补齐。
