---
name: hermes-release-coverage-gap
description: Hermes Agent release 后 72h 内 "ship-后未覆盖" P0/P1 cluster 跟踪 skill。Use when: major release tag 切后,需 cross-check release body 主张与新开 issue/PR 的 gap。配合 chief (acceptance verification) 和 pm (release-coverage.md) workflow。
---

# hermes-release-coverage-gap

> Hermes Agent release-coverage-gap 跟踪 skill。
> 触发背景:2026-07-03 v0.18.0 ship 后 72h 内,1 P0 (#57845) + 5 P1 cluster 涌现,与 release body "100% P0/P1 resolved" 主张冲突 — chief 24h acceptance verification 与 pm release-coverage.md 流程的实际执行 skill。

## 何时调用

1. release tag 切后 24h-72h 窗口(chief 触发)
2. 用户报告 "新 release 后立即遇到 bug"
3. tick25 类 researcher cron 在 release day 后 3d 跑 deep tick 时
4. 周期性(每日 cron,检查 release day 是否在 72h 内)

## 标准流程

### Step 1: 探针 release tag 时间窗口

```bash
RELEASE_TAG=v2026.7.1  # 或 latest
RELEASE_DATE=$(curl -s --noproxy '*' "https://api.github.com/repos/NousResearch/hermes-agent/releases/latest" | python3 -c "import json,sys; print(json.load(sys.stdin)['published_at'][:10])")
NOW=$(date -u +%Y-%m-%d)
DAYS_SINCE_RELEASE=$(( ($(date -d "$NOW" +%s) - $(date -d "$RELEASE_DATE" +%s)) / 86400 ))
if [ $DAYS_SINCE_RELEASE -gt 3 ]; then echo "OUT_OF_WINDOW"; exit 0; fi
```

### Step 2: 拉 release day 后所有 open P0/P1

```bash
curl -s --noproxy '*' "https://api.github.com/repos/NousResearch/hermes-agent/issues?state=open&since=${RELEASE_DATE}T00:00:00Z&per_page=100" -o /tmp/release_gap_issues.json
python3 -c "
import json
issues = json.load(open('/tmp/release_gap_issues.json'))
for it in issues:
    labels = [l['name'].lower() for l in it.get('labels', [])]
    if any(l in labels for l in ['p0','p1','priority/p0','priority/p1']):
        print(f\"#{it['number']} {','.join(labels)} {it['title'][:80]}\")
"
```

### Step 3: 抓 release body "clean sweep" 声明

```bash
curl -s --noproxy '*' "https://api.github.com/repos/NousResearch/hermes-agent/releases/latest" | python3 -c "
import json, sys
body = json.load(sys.stdin)['body']
# 找 'clean sweep' / '0 open P0' / 'priority backlog' 等主张
import re
for line in body.split('\n'):
    if re.search(r'(clean sweep|priority backlog|0 open P0|0 open P1|highest-priority)', line, re.I):
        print('CLAIM:', line.strip()[:200])
"
```

### Step 4: cross-check + 归类

对每个新开 P0/P1 issue:
- 创建时间是否在 release tag 之后
- 关联 revert PR 标签(如 sweeper:risk-revert-induced / 引用具体 revert PR)
- 是否为 new-discovery / regression / revert-induced / scope-creep

归类映射:
- **revert-induced**:issue 引用具体 revert PR(如 #57845 ↔ #56126)
- **new-discovery**:在 release 前已存在但 P0/P1 label 是 release 后加
- **regression**:issue body 明确说 "v0.X.0 之前 OK,v0.X.0 之后 fail"
- **scope-creep**:新 surface 不在 release body 范畴(如 desktop credential guard 是新加但与现有 component 相关)

### Step 5: 输出 gap report

写到 `~/.hermes/cron/output/release-coverage/{RELEASE_TAG}-{date}.md`:
```markdown
# Release Coverage Gap Report — {RELEASE_TAG} ({date})

## Release body 主张
- "100% P0/P1 resolved" (literal)
- "496 issues + 196 PRs closed"
- "P0 = 3 closed ISS + 8 PR merged"
- "P1 = 493 closed ISS + 188 PR merged"

## Release day 后 72h 新开 P0/P1
| # | 标签 | 简述 | 归类 |
|---|---|---|---|
| #57845 | P0 | envelope-layout cache no-op | revert-induced (root: #56126) |

## Gap 判定

| 维度 | 数量 | 与 release body 主张冲突? |
|---|---|---|
| 新开 P0 | 1 | 🚨 冲突 (声称 0 open P0) |
| 新开 P1 | 5 | 🚨 冲突 (声称 0 open P1) |
| revert-induced | 1 | 内含 — release 内 #56126 revert |
| regression | 0 | — |

## 建议动作

1. **patch release v0.18.1** — 至少 cache + credential cluster 6 项
2. **release-coverage note** — 在 v0.18.1 release body 引用本报告
3. **user 通知** — 若 default profile 已在 v0.18.0,飞书报 oc_c653562b "已知 issue,等 patch"
4. **chief acceptance verification 升级** — release-coverage 流程标准化

## Acceptance 状态

❌ FAIL — release body 主张与 release day 后实际状态冲突
```

### Step 6: 触发后续动作

- 若 gap report 标 🚨 冲突 → 飞书送 oc_c653562b(用户 home)
- 若 chief 已 enabled acceptance verification → 触发 chief 派 dev/qa 走 fix
- 若 pm 已 enabled release-coverage.md → 升级 pm 的 release-coverage 报告

## 何时不该调用

- 不在 release tag 切后 72h 窗口外跑(失效)
- 不在 patch release (v0.X.Y) ship 后跑 — patch release 本身是 coverage gap 的 fix,无需再 coverage check
- 不在 quiet window (新开 P0/P1 = 0) 跑 — 跑也是 "no gap" 报告,加 noise

## 验证

- [ ] 时间窗口判定正确(DAYS_SINCE_RELEASE ≤ 3)
- [ ] 新开 P0/P1 列表完整
- [ ] release body 主张抓到(cross-check)
- [ ] 归类映射(revert-induced / new-discovery / regression / scope-creop)清晰
- [ ] gap report 写到正确路径
- [ ] 冲突时飞书触发

## 关联

- GH #57845 (P0 envelope-layout cache no-op, 2026-07-03, ship 后 2d)
- GH #57869/#57865/#57838/#57833/#57827 (P1 cluster, dashboard credential + desktop windows)
- v0.18.0 release body (claims "100% P0/P1 resolved")
- PR #56126 (prompt_caching.enabled revert — 直接导致 #57845 根因)
- tick22/23/24 researcher cron — 连续 3 tick 预测 "v0.17.1 imminent" 实际 ship v0.18.0,提示 release 预测模型需校准
- skill `hermes-researcher-self-evolution-v1` — researcher cron 母 skill