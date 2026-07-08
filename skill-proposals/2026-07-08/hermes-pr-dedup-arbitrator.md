---
name: hermes-pr-dedup-arbitrator
description: '当 GitHub issue 在 24h 内被 ≥ 3 PR 抢修时,自动评估各 PR 的 root cause 覆盖率 + 改动最小化 + cross-subsystem 影响,选 1 个 primary 并生成 closure template 给非 primary PR。Use when: chief 触发 6h SLA dedup 或 cron worker 自检 gh pr list --search linked:issue:#N --state open ≥ 3。配套 skill: hermes-researcher-self-evolution-v1 (tick27+ 立卡 PR-dedup rule)。'
version: 0.1.0
author: Hermes researcher (tick30)
license: MIT
created_by: agent
metadata:
  hermes:
    tags: [github, pr-dedup, arbitration, chief-sla, v0.18.1]
    related: [hermes-researcher-self-evolution-v1]
---

# hermes-pr-dedup-arbitrator

## 这个 skill 解决什么

tick27 立卡 PR-dedup rule 触发频率上升(v0.18.1 ship 后 555 PRs / 8 天 = 高 release velocity):
- #47828: 24h 内 3 PR (#60931 / #60970 / #60985)
- #60794: 24h 内 4 PR (#60810 / #60840 / #60919 / #60980)
- #60947: 24h 内 2 PR (#60956 / #60981)

chief 必须 6h 内 dedup,但目前**没有自动化工具**评估 PR 候选 — 全靠 chief 手动读 PR。

## 触发条件

- gh pr list --search linked:issue:#N --state open 计数 ≥ 3
- 或 chief-agent cron worker 接到 6h SLA 触发
- 或 self-evolution cron worker 自检时发现

## 标准流程

### Step 1: 收集候选 PR

```bash
gh pr list --search linked:issue:#N --state open --json number,title,author,additions,deletions,changedFiles,createdAt,mergeable
```

### Step 2: 评估每个 PR

对每个候选,跑 5 维评分(0-3 分):
1. **root cause 覆盖率**: 该 PR 修复 root cause 的百分比
2. **改动最小化**: +A/-D files=F,越小越好
3. **cross-subsystem 影响**: 是否触碰其他子系统
4. **测试覆盖**: 是否带 regression test
5. **作者活跃度**: 24h 内响应 comment 的概率

总分最高 = primary。

### Step 3: 生成 closure template

```bash
PR_NUMBER=$NON_PRIMARY
ISSUE_NUMBER=$1

gh pr close $PR_NUMBER --comment "$(cat <<EOF
Closing in favor of #${PRIMARY} (primary).
Root cause covered by #${PRIMARY} {specific lines}.

Thank you for the contribution — please re-target if #${PRIMARY} is reassigned in 3d.

cc @${PRIMARY_AUTHOR}
EOF
)"
```

### Step 4: 3 天 reassign 检查

```bash
# 3 天后检查 primary 合并状态
gh pr view $PRIMARY --json state,mergedAt
# 若仍未合并 → reassign 给次高分 PR
```

## 评分模板 (per PR)

```yaml
pr_candidate:
  number: #X
  author: @user
  delta: +A/-D files=F
  scores:
    root_cause_coverage: 0-3
    minimality: 0-3
    cross_subsystem_impact: 0-3  # 0=严重,3=无影响
    test_coverage: 0-3
    author_responsiveness: 0-3
  total: sum
  decision: primary | non_primary | reassign
  rationale: "reasoning"
```

## 失败回退

- gh CLI 不可用 → 飞书报错,chief 手动 dedup
- PR 数据缺失 → 用 best-effort 默认评分
- 评估结果并列 → chief 拍板

## Pitfalls

### tick30 - 评估时不要只看行数

**触发**: #60970 是 #60931 的 +353/-2 (4 files) 版本,行数看似大但根因覆盖广。

**修正**: root_cause_coverage 比 minimality 权重大 2x。覆盖广 ≠ 改动大。

### tick30 - salvage PR 不要直接关闭

**触发**: #60985 标题写 "salvage PR #60931",本质是 duplicate。

**修正**: 用 "Closing in favor of #N" 模板,不用 "duplicate"。

### tick30 - primary 关闭时 reassign 必查 3 天

**触发**: tick27 立卡 — primary 卡 3 天仍未合并 → reassign 给次高分。

**修正**: Step 4 必跑,不能跳过。

## 验证清单

- [ ] gh pr list --search 集成进 skill
- [ ] 5 维评分模板可手动填写
- [ ] closure template 自动生成
- [ ] 3 天 reassign cron 集成
- [ ] chief-agent 6h SLA 触发可走此 skill