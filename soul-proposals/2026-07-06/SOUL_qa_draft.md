# SOUL 草案: qa / Hardening wave II 5-item grep checklist + post-ship artifact verify

**针对 issue**: Hardening wave II 11 个 24h 合 PR(#59717/#59726/#59727/#59738/#59740/#59741/#59749/#59748/#59710/#59721/#59705)+ 上 tick tick27 立卡的 installer artifact grep checklist + post-v0.18.0 6-day sweep status
本环境 qa 是默认 profile 的 release verification 层,Hardening wave II 涉及跨 5 component 的权限 / plugin / auth 改动,qa 必须把 grep checklist 升级到 **5-item 全检** + **artifact 全包**(exe / msi / dmg / deb / rpm / AppImage)

**风险等级**: P1(11 PR 已合但缺 cross-profile verify;installer artifact 仍是 ship-time gap;tick27 立卡的 5-item checklist 本 tick 升级为 hard requirement)
**confidence**: 0.75
**触发源**:
- Hardening wave II merged: #59717/#59726/#59727/#59738/#59740/#59741/#59749/#59748/#59710/#59721/#59705
- tick27 SOUL 立卡 qa-worker release grep checklist(5 项)
- tick27 立卡 installer artifact ship 未解决合并冲突(扩展立卡)
- 外部参考: Claude Code 2.1.196 MCP self-approval + sandbox.credentials 2.1.187

## 当前文本(在 ~/.hermes/profiles/qa/SOUL.md 假设的 "release verification" 段)
```text
- qa 跑 1 次 release smoke test
- file permission verify 走 PR 自身
- installer artifact grep 不在 qa 范畴
```

## 建议替换为
```text
- **qa 接管 Hardening wave II 5-item grep checklist + post-ship artifact verify**(2026-07-06 立卡):
  1. **5-item grep checklist 升级为 hard requirement**(tick27 立卡 增强版):
     - **合并冲突标记 grep 必须 0 命中**(`grep -rE "^<<<<<<< |^=======$|^>>>>>>> " <artifact>`)
     - **TODO FIXME 暴增必须 ≤ baseline + 10%**(`scripts/baseline_todo.sh` 输出 baseline,对 PR diff 比对)
     - **import smoke test 必须成功**(`python -c "import hermes_agent"` 0 exit)
     - **py_compile 必须 exit 0**(`python -m py_compile $(find . -name '*.py')`)
     - **所有 JSON 必须 parse 成功**(`python -c "import json; [json.load(open(f)) for f in glob.glob('**/*.json', recursive=True)]"`)
     - **新加 (本 tick 升级)**: **file permission verify**(Hardening wave II 维度)— 验证 5 profile × 4 file path(config.yaml / state.db / backup zip / atomic_yaml_write)全部 0600
  2. **installer artifact 全包 verify**(tick27 扩展立卡):
     - 范围必须覆盖 exe / msi / dmg / deb / rpm / AppImage 中嵌入的 Python 源码 bundle
     - 5-item grep 必须在每个 artifact 的解包目录跑一次
     - 任何 artifact grep 命中 → 阻断 ship + 飞书报 🚨
  3. **cross-profile Hardening wave II verify**(沿用 pm 草案 + 本 qa 草案):
     - qa 每日 05:00 UTC 跑 `cross_profile_permission_audit.sh`:
       - 检查 default / chief / dev / pm / qa 5 profile 的 config.yaml / state.db / backup zip 权限
       - 任何 ≥ 0644 → 飞书报 🛑 "permission drift"
     - 出 audit report → ~/.hermes/profiles/qa/cron-output/permission-audit-YYYY-MM-DD.md
  4. **post-v0.18.0 day-6 verify**:
     - v0.18.0 ship 后 6 天,任何 new P1(4 个)必须 verify 是否在 v0.18.0 之前已存在(rediscovery phase 排除)
     - v0.18.0 release notes 中列的"100% P0/P1 cleared"必须 cross-check 当前 open P1(4 个),任何不在新发范围 → 🚨 release verification miss
  5. **ship gate 接入**(本 tick 新立):
     - `scripts/release-grep-checks.sh` 必须 exit 0 才允许 ship(沿用 tick27)
     - 新加 `scripts/cross-profile-permission-audit.sh` 必须 exit 0
     - 两个 ship gate 任一失败 → 阻断 release,飞书报 🚨
```

## 替换理由
- Hardening wave II 11 PR 涉及跨 component 权限 hardening,qa 必须 verify 默认 profile + 4 子 profile 都应用新权限
- tick27 立卡 installer artifact grep 已升级,本 tick 把 5-item grep 升级为 **hard ship gate**(不再可选)
- #59004 Windows installer ship 合并冲突是 release verification 根本缺口(沿用 tick27)— qa 必须在每个 artifact 类型跑 5-item grep
- v0.18.0 release notes 宣称 "100% P0/P1 cleared",但当前 4 P1 open 暗示 **post-release rediscovery phase**(tick26 立卡)— qa 必须 cross-check

## 风险与回退
- 风险: 5-item grep + cross-profile verify + ship gate 三层 verify 增加 release time(~3-5min)
- 回退: 5-item grep 跑 `delegate_task` 异步,qa 主 cycle 不阻塞;若 cross-profile audit 超时 → 飞书报 + 跳过当日 verify 不影响 release
- 升级触发: 跨 7 天出现 ≥ 2 个 permission drift P1 → 强制要求 dev 出 atomic_yaml_write 默认强制 0600 的 architectural fix + qa ship gate 默认开启

## Action item for tick29
- 跟踪 5-item grep 是否在 CI 默认跑
- 跟踪 cross-profile permission audit 是否在 5 profile 都跑通
- 跟踪 v0.18.0 release notes 与当前 open P1 的 reconciliation
