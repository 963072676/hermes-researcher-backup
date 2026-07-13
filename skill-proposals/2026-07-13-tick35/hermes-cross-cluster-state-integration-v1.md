---
name: hermes-cross-cluster-state-integration-v1
description: 'Hermes researcher v1 立卡 skill。cross-cluster state integration 评估 — 任意 P1 cluster 跨 ≥ 2 family 时立即触发,产出 severity-A/B/C arrows + chief triage map + 联动 fix 优先级。Use when: researcher tick 看到 P1 cluster 触发 ≥ 2 family 联动,或 F9↔F5/F7↔F10 等已知 cross-cluster arrow 活跃。'

# hermes-cross-cluster-state-integration-v1

> Hermes researcher cross-cluster state integration v1 (2026-07-13 立卡, tick35)。
> 配套 SOUL:chief-agent cross_cluster_integration_v1 + pm p1_acceptance_contract_v3 + dev f9_tier2_implementation_strategy + qa release_verification_v5 + default update_handoff_readiness_v1。

## 这个 skill 解决什么

tick34 立的 9 family registry 把 family 看作独立 fix 单元。但 tick35 观察到 5 条 cross-cluster arrows:

| arrow | from | to | severity |
|---|---|---|---|
| CCA-1 | F9 #63128 prune live session | F5 #41935 zombie cron session | severity-A |
| CCA-2 | F7 MCP hardening | F10 Docker migration gap | severity-B |
| CCA-3 | F9 #63129 lock fail-open | F8 #32612 ticker silent die | severity-B |
| CCA-4 | F1 silent-fail | F5 no_agent cron path | severity-C |
| CCA-5 | F2 #51646 cross-platform memory | F9 #63207 observer disconnect | severity-C |

family 内 single-fix 完成后**联动 bug 仍存在**,用户感知"修了 5 个 bug 还是有 bug"。本 skill 提供 cross-cluster 评估 protocol,让 chief 在 6h 内做 severity-A triage,24h 内组织 severity-B joint review。

## 何时调用

- 任意 researcher tick 看到 P1 cluster 跨 ≥ 2 family 联动 → 立即触发
- 已知 family F1/F5/F7/F8/F9/F10 任一 fix PR 落地后 7 天内 → 验证联动 family 是否有未验证的副作用
- 5 profile × config.yaml 跨 release 累积 stale → F10 升级 chief 亲自 triage
- cron worker silent fallback + no_agent 路径不明确 → CCA-4 触发
- TUI/dashboard 关闭后 messaging session 状态不一致 → CCA-5 触发

## 标准流程

### Step 1: 列出 tick 内全部 P1 cluster + family 归属

```bash
# 从 researcher-tick 输出拉 P1 cluster + family
P1_CLUSTERS=$(gh issue list --state all --label "P1" --json number,title,labels --limit 50 | jq -r '.[] | "\(.number)|\(.title)|\(.labels[].name | select(. != "P1"))"')
```

### Step 2: 标 cross-family interaction arrows

对每个 cluster,搜索关联 family:
```bash
# 用 gh issue view 看 linked issues + linked PRs + 关联 label
gh issue view <N> --json body,title | grep -iE "#[0-9]+|sweeper:"
```

画出 arrow map:
```markdown
## Cross-cluster arrows tick35

- F9 #63128 ↔ F5 #41935 (severity-A) — prune 误杀 zombie cron sessions
- F7 MCP hardening ↔ F10 #35406 (severity-B) — hardening 不解决 stale config
- F9 #63129 ↔ F8 #32612 (severity-B) — lock fail-open + ticker silent die
- F1 silent-fail ↔ F5 no_agent cron (severity-C) — cron_mode=deny 路径未明确
- F2 #51646 ↔ F9 #63207 (severity-C) — cross-platform memory + observer disconnect
```

### Step 3: 评估每条 arrow 的 severity

```python
def severity_eval(arrow):
    if arrow.from_family_fix_side_effect_directly_worsens(arrow.to_family_bug):
        return "severity-A"  # chief 6h triage
    if arrow.from_family_fix_requires_to_family_fix_to_complete():
        return "severity-B"  # chief 24h joint review
    return "severity-C"  # 进 daily report
```

### Step 4: severity-A arrow chief 6h triage

对每条 severity-A arrow,chief 必须:
1. 列出 family A fix 的副作用范围
2. 评估 family B 当前状态(是否已修 / 仍 open / 复发)
3. 决定:
   - family A fix revert(如果副作用太重)
   - family A fix 加 conditional(只在 family B 已修时启用)
   - family A fix 加速 family B 修复(joint fix PR)

### Step 5: severity-B arrow chief 24h joint review

对每条 severity-B arrow,chief 必须:
1. 联系 family A + family B 的 primary owner
2. 评估 joint fix 时间线
3. 决定 ship 顺序(family A 先 / family B 先 / 同步)

### Step 6: 写 impact-graph 输出

写到 `~/hermes-researcher-backup/cron-output/YYYY-MM-DD/impact-graph.md` 的 cross-cluster arrows 段。

## 标准输出模板

```markdown
# 跨 Profile 影响图 + Cross-cluster arrows — YYYY-MM-DD (tickN)

## Cross-cluster arrows

### severity-A (chief 6h triage)

- [arrow_id, from_family, to_family, severity, interaction, fix_priority]

### severity-B (chief 24h joint review)

- [arrow_id, from_family, to_family, severity, interaction, fix_priority]

### severity-C (进 daily report)

- [arrow_id, from_family, to_family, severity, interaction, fix_priority]

## Cross-cluster acceptance plan

- 每条 severity-A arrow 必须有 chief sign-off 才允许 tick 完成
- 每条 severity-B arrow 必须有 joint review 时间线
- severity-C 进 daily report 不阻塞

## Watch signals

- [arrow_id, signal_name, threshold, alert_channel]
```

## 失败回退

- chief 6h 内未 triage severity-A → 飞书报警 + cross-cluster arrow 升级为 escalation
- severity-A arrow 修复无时间线 → 进 PM 11-field acceptance contract 阻塞 acceptance

## 验证清单

- [ ] 每个 tick 跑 Step 1 + Step 2,产出 cross-cluster arrows map
- [ ] severity-A arrow 必须 chief 6h triage 文档化
- [ ] severity-B arrow 必须 joint review 时间线
- [ ] impact-graph.md 含 cross-cluster arrows 段
- [ ] watch signals 在 default profile cron 监控

## 配额(防刷屏)

- 每个 tick cross-cluster arrows ≤ 8 (防止过载)
- severity-A 必须 ≤ 2 (再多就升级 chief escalation)
- severity-B 必须 ≤ 3
- severity-C 任意
- 飞书 cross-cluster summary 每日 ≤ 1 条 (与日报合并)

## 相关 references

- `references/cross-cluster-arrows-tick35.md` — tick35 实战 5 arrows + severity 评估
- `references/cross-cluster-acceptance-template.md` — 11-field acceptance contract v3 template (pm 草稿立卡)
- `references/cross-cluster-watch-signals.md` — 5 cross-cluster arrows 的 default profile watch signal 列表

## Pitfalls

### tick35 - severity 评估不可只看字面,必须看 fix 副作用

**触发**:tick35 评估 CCA-1 (F9 #63128 ↔ F5 #41935) 时,如果只看"prune live session" + "zombie cron session" 字面,容易判 severity-C(看起来独立)。但实际 F9 #63128 fix 上线后,prune 默认 skip liveness check → 误杀 F5 zombie session → 双重漏算。

**修正**:severity 评估必须问"family A fix 副作用是否**加重** family B 的 bug"。加重 = severity-A;依赖 = severity-B;独立 = severity-C。

### tick35 - cross-cluster arrow 命名必须 ≥ 2 段式

**触发**:cross-cluster arrow 命名若只编号"arrow-1" / "arrow-2",后续引用不明确。

**修正**:3 段式命名 `<from_family_initials>-<to_family_initials>-<interaction>`:
- `F9-F5-prune-zombie-mis-kill` (CCA-1)
- `F7-F10-hardening-stale-config` (CCA-2)
- `F9-F8-lock-ticker-silent` (CCA-3)
- `F1-F5-no-agent-silent-fallback` (CCA-4)
- `F2-F9-observer-memory-confusion` (CCA-5)