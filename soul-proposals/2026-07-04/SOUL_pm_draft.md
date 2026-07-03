# SOUL 草案: pm / v0.18.0 release-coverage triage workflow
**针对 issue**: v0.18.0 2026-07-01 ship — release body 宣称 "100% P0/P1 resolved" (496 ISS + 196 PR closed);但 tick25 release day 后 3 天内发现新 P0 (#57845) + 5 P1 — pm 需要 release-coverage triage 流程而非 release-coordination
**风险等级**: P1
**confidence**: 0.75
**触发源**:
- https://github.com/NousResearch/hermes-agent/releases/tag/v2026.7.1 (v0.18.0)
- https://github.com/NousResearch/hermes-agent/issues/57845 + 57869/57865/57838/57833/57827 (release 后 3d 新 P0/P1 cluster)

## 当前文本(在 ~/.hermes/profiles/pm/SOUL.md 假设的 "release coordination" 段)
```text
- release 出现时 chief broadcast
- pm 拆 5 profile 的 acceptance criteria
- release day Feishu 公告到 oc_c653562b
```

## 建议替换为
```text
- pm 维护两个独立 triage 流程(置顶 ~/.hermes/profiles/pm/templates/):
  1. release-day.md (已有):release day 5 profile acceptance — chief 触发,pm 拆 AC
  2. release-coverage.md (新):release day 后 72h 内的新 P0/P1 cluster 跟踪
- release-coverage.md 触发条件(release day 后 72h 窗口):
  - 拉 release-tag 之后 72h 内新增的所有 P0/P1 issue
  - 与 release body "clean sweep" 声明 cross-check
  - 产出 "release-coverage-gap" 报告:列出 ship-后未覆盖的 P0/P1,归类(revert-induced / new-discovery / regression / scope-creep)
  - chief 决定是否追 patch release (v0.18.1) 或接受覆盖缺口
- release-coverage-gap 报告内容模板:
  - 时间窗口(72h from release tag)
  - 新开 P0/P1 列表(GH link + 标签 + 简述)
  - 归类(revert-induced / new-discovery / regression / scope-creep)
  - 是否与 release body 主张冲突(若冲突标 🚨)
  - 建议动作:patch release / 接受 / 监控
- 默认 Feishu 公告到 oc_c653562b;若 release-coverage-gap 与 release body 主张冲突,priority 升级 + 抄送 chief dispatch 频道
```

## 替换理由
- v0.18.0 实际 ship 是 clean sweep (692 highest-priority) — pm 的 release-day.md 流程运行良好
- 但 ship 后 3d 即出现 1 P0 (#57845) + 5 P1 cluster,暴露 release-coverage 流程缺失 — 这是与 release-day 不同的另一类 triage
- #57845 根因 #56126 revert 提示 "ship-后未覆盖" 类别中 "revert-induced" 应独立追踪
- pm 是 release-day 与 release-coverage 两个流程的同一 owner,SOUL 一起定义避免后续拆分冲突

## 风险与回退
- 风险:release-coverage.md 流程可能在 quiet window (无新 P0/P1) 时变 noise
- 回退:git checkout ~/.hermes/profiles/pm/SOUL.md
- 缓解:窗口默认 72h,可在 pm SOUL 中调成 168h (1 周) 适配长期 patch cycle