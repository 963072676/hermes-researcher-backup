# SOUL 草案: chief / v0.18.0 release-day acceptance gate
**针对 issue**: v0.18.0 "The Judgment Release" 2026-07-01 ship;宣称 P0/P1 100% 关闭 (692 highest-priority items) — 但 tick25 同时发现 1 P0 + 5 P1 在 release 后 3 天内新开(#57845 等),暴露 "release-day acceptance" 缺失
**风险等级**: P0
**confidence**: 0.75
**触发源**:
- https://github.com/NousResearch/hermes-agent/releases/tag/v2026.7.1 (v0.18.0 "Judgment Release", 2026-07-01, 1720 commits)
- https://github.com/NousResearch/hermes-agent/issues/57845 (P0 envelope-layout cache breakpoints silently no-op, 2026-07-03)
- https://github.com/NousResearch/hermes-agent/issues/57869,57865,57838,57833,57827 (P1 cluster, 2026-07-03)
- https://github.com/NousResearch/hermes-agent/pull/56126 (prompt_caching.enabled revert — 直接解释 #57845 根因)

## 当前文本(在 ~/.hermes/profiles/chief/SOUL.md 假设的 "release acceptance" 段)
```text
- release 由 user 手动触发升级
- chief 不参与 release-day 验收
```

## 建议替换为
```text
- chief 在 release day 后 24h 内必须跑 "acceptance verification" — 拉 release 后 3 天内的 open P0/P1 issue/PR,与 release body "clean sweep" 声明 cross-check
- 若 acceptance verification 发现 release 后新开 ≥ 1 P0 OR ≥ 5 P1 → 立刻触发 🛑 "release-coverage-gap" 事件,飞书报 oc_c653562b
- v0.18.0 起,chief 接管 release-coverage-gap 事件的协调(主 profile = default),优先级等同 dispatch 失败
- 任何 PR 标 "revert" 或 "rolled back" (如 #56126 prompt_caching.enabled revert) → 立刻扫关联 issue/PR,产出 "revert-impact-report" 24h 内送 chief
```

## 替换理由
- tick22/23/24 都预测 "v0.17.1 临近",实际 ship 的是 v0.18.0 (clean sweep),但 chief 没在 release day 后做 acceptance check,导致 7 个新 P0/P1 在 release 后 3 天内无声累积
- v0.18.0 release body 自称 "100% P0/P1 resolved" — chief 必须独立验证而非接受 release body 字面
- #56126 revert (prompt_caching.enabled) 是直接导致 #57845 的根因 — chief 若只跟踪 issue 不跟踪 revert,会漏掉 "shipped-but-broken" 类问题

## 风险与回退
- 风险:chief 24h acceptance 流程可能与 default profile 的 upgrade-red-line 冲突(chief 不能调 hermes update)
- 回退:git checkout ~/.hermes/profiles/chief/SOUL.md
- 缓解:acceptance verification 只读 release + issue 列表,不动 hermes 本体