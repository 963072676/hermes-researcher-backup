---
name: hermes-post-merge-regression-window-guard-v1
description: '验证 Hermes v0.18.x 时代 merged P1 PR 在 14 天观察窗内的 regression 行为。覆盖 #64593/#64574/#64552/#64617 等 merged fix 的 regression smoke + cross-surface e2e + install profile 验证。Use when: P1 PR merged 后 14 天内、准备 release 时、回填 closed-but-merged 状态时。'
version: 1.0.0
created_by: researcher
metadata:
  hermes:
    tags: [release, regression, artifact-verify, post-merge, trust-boundary]
---

# Hermes Post-Merge Regression Window Guard v1

## 目标

在 P1 PR merged 但 release artifact 未发布 / 本机未升级的窗口期内, 保证 fix 路径的 regression 可被快速检测。把"merged = fixed"拆为多段状态机 (closed_only / closed_unmerged / closed_merged_no_artifact / closed_merged_artifact_verified / fixed_candidate / fixed)。

## 触发条件

- P1 PR `merged_at != null` 但最新 release tag 距 merge_at < 14 days
- 同一 root cause 跨 family cross-cluster arrow verify 时
- v0.18.x release verification gate (qa-worker release_verification_v7) 执行时
- closed-but-unmerged 状态机检测时 (PR merged_at=null)
- 用户 reproducible report 同 root cause 在 merged PR 之后仍出现

## 不变量

1. merged PR 的 commit SHA 必须进入 release artifact manifest (release_target=v0.18.3)
2. 5 install profile (Desktop/Docker/CLI/TUI/MCP stdio) 必跑 72-check ship gate
3. 14 天 regression 观察窗内任何同 root cause issue 触发 reopen
4. closed_unmerged_count 在 candidate_pr_dedup_state 中必须 ≤ total_candidate_prs - 1
5. cross_profile_audit_required=true 时 5 profile 全过才算 fixed_candidate
6. runtime smoke 12 项 per family 全过 (F1/F8/F9/F10 + 4 family)

## 状态机 (沿用 pm-orchestrator v5 contract)

```
issue_open + primary_pr_open → implementation_pending
issue_closed + primary_pr_unmerged → verification_pending (NOT fixed)
issue_closed + primary_pr_merged → release_verify_pending (NEEDS v0.18.3 + 72 checks)
artifact_verify_passed + cross_profile_verify_passed → fixed_candidate
ship_in_release + observed_in_production ≥ 14 days → fixed
```

## 标准流程

### Step 1: 列 merged P1 PR 状态

```bash
gh api 'search/issues?q=repo:NousResearch/hermes-agent+is:pr+is:merged+merged:>2026-07-13+label:P1' \
  --jq '.items[] | [.number, .title, .merged_at] | @tsv'
```

### Step 2: 列 closed_unmerged P1 PR 反例

```bash
gh api 'search/issues?q=repo:NousResearch/hermes-agent+is:pr+state:closed+is:unmerged+label:P1+created:>2026-07-13' \
  --jq '.items[] | [.number, .title, .state] | @tsv'
```

### Step 3: 对每个 merged PR 跑 4 项 invariant smoke

| Invariant | Tool | Output |
|---|---|---|
| foreign async completion cannot be consumed by new CLI | cli-new-session smoke + e2e | 0 foreign completion |
| owner session consumes exactly once | durability smoke | 1 owner resume |
| compression lineage owner consumes exactly once | compression e2e | 1 lineage consume |
| `/new`, `/clear`, process exit pending completion retained | session-key switch e2e | retained pending row |

### Step 4: 12 项 runtime smoke per family

```yaml
F1_silent_fail:
  - Telegram getUpdates connect on PTB 21.x / 22.x / 22.6
  - zero-chunk stream retry bound (max 3 attempts)
  - normal stream no retry overhead
  - Anthropic zero-event parity
F8_cron_ticker:
  - terminal capture bounded at configured max_bytes
  - head/tail preserved + omitted byte count
  - continuous producer timeout under wall clock
  - gateway RSS not coupled to output size
F9_session_state:
  - foreign async completion cannot be consumed by new CLI
  - concurrent turn detection blocks alternation wedge
  - supervisor ownership preserved under launchd/systemd
  - compression lineage owner consumes exactly once
F10_installer_handoff:
  - Desktop bundle smoke on macOS/Windows/Linux
  - install-tree AGENTS.md never loaded as project context
  - HERMES_HOME per profile strict
  - auxiliary_client process_bootstrap survives version-skewed
```

### Step 5: 5 install profile 全量 verify

```bash
for profile in Desktop Docker CLI TUI MCP_stdio; do
  qa_worker_run_ship_gate_v7 --profile $profile --total-checks 72
done
```

### Step 6: cross_profile_audit (chief/pm/dev/qa/default)

```bash
cross_profile_audit_run --profiles chief,pm,dev,qa,default \
  --checks permission,config,artifact_manifest,mcp_init,registry_skill
```

### Step 7: 14-day regression window observation

```bash
# 每日检查同 root cause 新 issue
gh api 'search/issues?q=repo:NousResearch/hermes-agent+is:issue+state:open+created:>merge_at+14d+label:P1' \
  --jq '.items[] | [.number, .title, .created_at] | @tsv'
```

### Step 8: 状态机推进

```yaml
release_verify_pending → fixed_candidate: "all 72 checks PASS + 5 profile cross-verify + 14-day no regression"
fixed_candidate → fixed: "observed_in_production ≥ 14 days + no user reproducible report"
```

## Acceptance contract

```yaml
post_merge_regression_window:
  merged_prs_tracked: required_list
  closed_unmerged_excluded: required_list
  install_profiles_verified: required_list  # 5 elements
  total_checks_passed: required_integer  # 72
  cross_profile_audit_passed: required_boolean
  regression_window_observed_days: required_integer  # 0-14
  state_machine_position: enum[implementation_pending, verification_pending, release_verify_pending, fixed_candidate, fixed]
```

## 失败判定

- 任何 closed_unmerged PR 计入 fixed → 立即 alert chief
- 任何 merged PR commit SHA 未在 release artifact manifest → 立即 reopen issue
- 任何 install profile 72-check ship gate fail → reject ship
- 任何 14-day window 内同 root cause 新 issue → reopen + new PR
- 任何 cross_cluster arrow verification fail → chief triage before ship

## 证据

- tick37 立卡 (2026-07-16): [merged P1 PR list](https://github.com/NousResearch/hermes-agent/pulls?q=is%3Apr+is%3Amerged+merged%3A%3E2026-07-13+label%3AP1)
- PR #64593 closes #64484
- PR #64574 closes #64482 + #64694 (duplicate)
- PR #64552 salvage #64420 + indirect fix #64435
- PR #64617 closes #64333
- pm SOUL v5 17-field acceptance contract
- qa SOUL v7 72-check ship gate

## Pitfalls

- "merged PR = fix" 是错的: 必须 artifact verify + cross_profile + 14-day window
- closed_unmerged PR 即使 commit 写得正确, 也不能当 fix evidence
- 本机 v0.18.0 + upstream v0.18.2 + main 1464 ahead → 任何 fix 路径在本机仍是老 code
- regression window 14 天是经验值, 不够覆盖 slow-burn bug (cross-month)
- cross_cluster arrow 在 fix 后必须 verify, 不能默认 fix 不引入联动 regression
- 本 default profile 受 fix 路径影响小, 但 regression window 任务不能省