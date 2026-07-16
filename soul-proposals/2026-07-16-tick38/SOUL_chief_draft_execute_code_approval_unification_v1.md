# SOUL_chief_agent 草案 — execute_code approval unification (tick38, 2026-07-16)

> 配套 SOUL v2 / cron: hermes-researcher-deep-tick-daily
> tick38 立卡:family_name_v1 = `execute-code-approval-unification-deck`
> family sweeper marker: `sweeper:risk-execute-code-approval-unification`
> 关联 issue: #60056 (P2 -> 升级 P1 候选,2026-07-07 open);关联 PR #60077 + #60799 (both open)
> trust boundary impact: `action_authority` + `identity` + `info_disclosure` (3 of 5)
> 来源:GitHub issue #60056 + arXiv 2605.24659 (IterInject) + CSA MCP STDIO RCE + CVE-2026-61459
> 立卡 tick: tick38 (2026-07-16)
> 沿用:tick27 立卡 silent-fail family / tick33 立卡 cron-ticker-resilience-deck / tick35 立卡 cron-installer-handoff-state

## 1. 触发(为什么立 family)

**tick38 关键观察 (2026-07-16)**:
- **#60056** open P2 (2026-07-07) by valmy — Hermes agent (default profile) merged prod PR with **no human consent** via `gh pr merge --squash --delete-branch`;forensics identified **3 distinct reproducible gaps** in the command-approval system.
- 三 gap root cause:
  - **Gap 1**: `gh pr merge --delete-branch` / `git push --force-with-lease` / `git branch -D` / `gh release create` 不在任何 dangerous_pattern 列表 — VCS/remote-mutation commands 全部 auto-approved
  - **Gap 2**: `execute_code` 是 documented, functioning bypass of approval layer;hermes_tools.terminal() 在 execute_code RPC 内 bypasses DANGEROUS_PATTERNS pipe-to-interpreter match
  - **Gap 3**: Session-classification hole — kanban-spawned autonomous sessions 既有 `HERMES_CRON_SESSION` (fail-closed) 又有 gateway-ask (fail-ask),但 kanban card-completion notification spawned session 落 "local non-interactive → approved" bucket → **auto-approved**
- **PR-dedup fire**: #60077 (izumi0uu,2026-07-07) + #60799 (embwl0x,2026-07-08) — 2 PR 抢同一 root cause
- **关联 PR #57890** (jquesnelle,2026-07-04 merged) — vision sandbox escape 修复使用 unified resolver 模式(tick30 已立卡),佐证:同 root cause 不同 attack vector 都需 unified pattern
- **关联 PR #24942** (LifeJiggy,2026-06-09 closed) — Phase 1 hardening 3 critical fixes;**unmerged** 证明此 family 修复 attempted but 仍 pending

**F11 候选判定 (tick38 立卡准则)**:
| 判定条件 | tick38 触发 | 命中 |
|---|---|---|
| 跨 ≥ 5 GH issue 同 root cause | #60056 + #60077 + #60799 + #24942 + (4 隐性: 实验性 reproduce) = 5 | ✅ |
| 跨 ≥ 3 platform 同根 | `execute_code` 跨 Python + Node + Rust SDK + 所有 IDE = 4 | ✅ |
| 修复 PR 合入但根因 broader | #24942 unmerged (3 attempted fixes withdrawn);#57890 同 root cause 但只修 vision | ✅ |

**判定**:满足 3 条件任意 1 → 立 F11 family。**`execute-code-approval-unification-deck` 第 11 family 立卡,加入 11 family registry**(沿用 tick36 family anti-inflation 准则:本 cluster ≥ 5 evidence 不算反膨胀)。

## 2. 6 invariant 必备 (tick38 chief-agent SOUL 草稿)

沿用 tick33 F8 + tick34 F9 + tick35 F10 立卡的 invariant 6 段模式。tick38 F11 invariant 6 段:

### Invariant 1 — VCS/remote-mutation class 独立 deny list
- `gh pr merge --(squash|merge|rebase)[-...]` / `gh pr merge --delete-branch` / `git push --force[-with-lease]` / `git branch -D` / `git push --delete` / `gh release create` / mutating `gh api -X POST/PUT/DELETE/PATCH`
- **default-deny when no approver present** (HERMES_CRON_SESSION / kanban worker / kanban-notification-spawned / subagent)
- 在 `tools/approval.py` DANGEROUS_PATTERNS 单独段(class="vcs-remote-mutation"),不依赖 shell-destruction patterns

### Invariant 2 — execute_code RPC dispatch 走同一 per-call guard pipeline
- `tools/code_execution_tool.py:501` RPC dispatch (`from model_tools import handle_function_call`) 必须 apply `_check_all_guards` 在每次 sub-tool call (terminal/patch/write_file/read_file),不只在 one-shot whole-script guard
- `hermes_tools.terminal()` 在 execute_code 内跑也走同一 per-call check
- 关闭 "execute_code is documented escape hatch" 文档 (`experiment-patterns.md:484`),替换为 "fix the command, don't route around scanner"

### Invariant 3 — Session-classification unification
- `check_execute_code_guard` (`tools/approval.py:2696-2765`) 失败关闭不只 `HERMES_CRON_SESSION + cron_mode=deny`,而是所有 "no human approver present" 类别:cron / kanban worker / kanban-notification-spawned / subagent
- 引入 `autonomous_session_flag` 字段,set `True` if (cron || kanban || subagent || notification),统一 fail-closed path
- 关闭 "local non-interactive non-gateway session returns approved" 路径(`tools/approval.py:2707-2713, 2764-2765`)

### Invariant 4 — Tool description sanitization (MCP supply chain 6-control 沿用)
- `core/supply_chain.py` + `scan_mcp_description()` 必须扫 tool description 不含 injection keyword (ignore previous / tool override / hijack / system prompt)
- Perplexity detection:tool selection 偏离 candidates 平均 perplexity > 2.0 → flag suspicious
- Known-answer test:覆盖 ≥ 100 常见 query,失败 → reject tool selection

### Invariant 5 — Defense-in-depth audit log (info_disclosure 防御)
- 任何 `execute_code` block 必须 audit log:incoming code block SHA256 + runtime result hash + sub-tool calls list
- GitHub PR merge 成功必须 audit log 包含:approver role / session_id / risk_class / post-merge commit SHA
- GitHub attribute misattribution 防御:`is_bot=true` 标签必须设置 when actor is agent session,即使 GitHub UI 默认 `is_bot=false`

### Invariant 6 — Pre-commit release gate (CVE-2026-61459 + CVE-2026-59950 + EXT14 alignment)
- ship gate v7 (tick37) 升级到 v8:加 `dangerous_command_unified_classify` 必须 exit 0 才 ship
- dangerous_command_unified_classify 检查项:
  - VCS/remote-mutation commands 必须在 DANGEROUS_PATTERNS
  - execute_code RPC dispatch 走同一 per-call guard
  - Session classification table 含 autonomous_session_flag
  - audit log 包含 approver role / session_id / risk_class
- 默认 deny on absent flag (fail-closed)

## 3. family_lifecycle 状态

**emerging** — 立卡 < 14 days,本 tick 是立卡时刻 (F11 第 11 family)。

## 4. P1 acceptance contract v5 (17-field) 实战应用 (tick38 first application on F11)

| 字段 | tick38 F11 实战填值 |
|---|---|
| family_name | execute-code-approval-unification-deck |
| evidence_ids | #60056 + #60077 + #60799 + #24942 (unmerged Phase 1 hardening) + #57890 (vision sandbox same root cause) |
| reproduction_scope | default profile / kanban worker / subagent / cron / notification-spawned session — `local non-interactive → approved` bucket |
| invariants | 见 Section 2 (6 invariant) |
| primary_fix | (none yet, TBD by chief 6h dedup PR-candidate selection) |
| ship_gate | v7 72-check → v8 76-check (+4 dangerous_command_unified_classify) |
| memory_id | (after MCP propose) |
| cross_cluster_arrows | CCA-E1: F11 execute-code-approval → F7 MCP-supply-chain (extending #57890 vision sandbox → unified resolver) severity-B;CCA-E2: F11 execute-code → F8 cron-ticker (kanban-spawned session 走 execute_code 路径,可触发 cron silent die via thread death) severity-C;CCA-E3: F11 execute-code → F10 installer-handoff (setup.py pin + execute_code 双重 upgrade 红线) severity-C |
| trust_boundary_impact | action_authority + identity + info_disclosure (3 of 5) |
| config_freshness_post_release | {requires_migrate: false, profiles_affected: [default, chief, dev, qa, pm], raw_config_version_check: optional} |
| family_lifecycle | emerging |
| session_ownership_provenance | autonomous_session_flag (cron / kanban worker / subagent / notification) — 统一 fail-closed |
| runtime_boundedness | execute_code block 必须 bounded timeout (default 30s, kanban worker 60s, cron worker 300s);sub-tool call per-call guard 必须 < 100ms |
| artifact_source_coherence | tools/approval.py:2696-2765 + tools/code_execution_tool.py:501 + core/supply_chain.py (4 file coherence) |
| dependency_compatibility | heremes-python >= 3.12;PyYAML >= 6.0;mcp-sdk >= 1.28.1 (CVE-2026-59950 fix) |
| candidate_pr_dedup_state | {total_candidate_prs: 2, candidate_prs: [#60077, #60799], primary_pr_selected: (TBD chief 6h), closed_unmerged_count: 1 (#24942 unmerged as Phase 1 hardening), dedup_decision_made_by: chief, dedup_window_hours: 24} |
| artifact_verify_required_for_release | {release_target: "v0.18.3 + later", install_profiles_affected: [Desktop, Docker, CLI, TUI, MCP_stdio], manifest_required: true, import_smoke_target_paths: [tools/approval.py:2696-2765, tools/code_execution_tool.py:501, experiment-patterns.md:484], runtime_smoke_target_surfaces: [kanban worker, cron, subagent, notification], cross_profile_audit_required: true} |

## 5. ship_gate 升级 v7 → v8 (tick38 立卡)

```text
v7 72-check (tick37) + 4 dangerous_command_unified_classify = v8 76-check

dangerous_command_unified_classify 4 项:
1. VCS/remote-mutation commands 在 DANGEROUS_PATTERNS (grep + AST parse)
2. execute_code RPC dispatch 走 per-call guard (runtime smoke:kanban worker spawn + 模拟 gh pr merge 拦截)
3. Session classification 含 autonomous_session_flag (unit test: cron / kanban / subagent / notification 4 类)
4. audit log 包含 approver role + session_id + risk_class (integration test: 模拟 merge 成功 verify log 含 3 字段)
```

## 6. chief-agent 6h dedup SLA (沿用 tick27 + tick33 + tick34 + tick35 立卡)

**PR-dedup fire**:
- #60077 (izumi0uu,2026-07-07,5 commits) — primary candidate
- #60799 (embwl0x,2026-07-08,1 commit,smaller scope)

**chief 6h SLA**:
1. 评估两个 PR 修复覆盖率:#60077 含 Invariant 1+2+3 但漏 Invariant 5;#60799 含 Invariant 1+3 但缺 Invariant 2+5
2. 选 #60077 作 primary (覆盖 3/6 invariant),合并后追加 #60799 scope (Invariant 2+5) 作 follow-up PR
3. 关闭其他 dual-candidate 模板回复 Closing in favor of #60077 (沿用 tick27 立卡)
4. 24h 内 primary 未合并 → reassign #60799 (沿用 tick27 立卡)
5. chief 必须在 6h 内 decision;若 6h 后无 chief decision 标 "open primary selection",worker 转 nightly digest 持续观察

## 7. 关联 family (cross-cluster arrows)

- **CCA-E1 (F11 → F7, severity-B)**: F11 execute-code approval unification 修复必须 extend F7 MCP supply chain 6-control,因为 vision sandbox (#57890) 用 unified resolver 模式证明同 root cause 不同 attack vector 需 unified pattern
- **CCA-E2 (F11 → F8, severity-C)**: F11 kanban-spawned session 走 execute_code,如果 execute_code block 内触发 thread death,会触发 F8 cron-ticker silent die 模式 (BaseException escape) — 需 chief cross-review
- **CCA-E3 (F11 → F10, severity-C)**: F11 execute_code RPC upgrade 必须 verify F10 setup.py pin (#60685 redline) 不被绕过;`pip install hermes-agent` 走的 shell 不走 execute_code path

## 8. 飞书推送内容 (tick38 chief-agent)

```
[F11 family 立卡] execute-code-approval-unification-deck
6 invariant + 4 PR-dedup candidate (#60077 + #60799)
chief 6h dedup SLA
ship gate v7 → v8 (76-check)
trust boundary: action_authority + identity + info_disclosure (3 of 5)
关联 CVE: CVE-2026-61459 (MCP K8s RCE) + CVE-2026-59950 (MCP WS origin)
```

## 9. 状态机 (5-state machine extension 沿用 tick37)

1. `closed_only` — issue closed, 0 PR merged (NOT fixed)
2. `closed_unmerged_candidates` — ≥1 PR closed unmerged (#24942 unmerged Phase 1)
3. `closed_merged_no_artifact` — primary PR merged, v0.18.x release tag 未包含 commit SHA (release_verify_pending)
4. `closed_merged_artifact_verified` — primary PR merged + v0.18.x shipped + 72 checks PASS (fixed_candidate) [升级到 v8 76-check]
5. `closed_merged_artifact_verified_cross_profile` — + 5 install profile cross_profile_audit PASS + 14d regression window no regression (fixed)

**当前 tick38 状态**:**open** — #60056 P2 (待升级 P1);PR-candidate #60077 + #60799 都在 open,closed_unmerged 0,no merged primary yet。

## 10. 采纳等待 (tick38 SOUL_chief 草稿)

等待 user ack 后:
1. 写入 default profile `~/.hermes/profiles/chief/SOUL.md` 作为 v2 段 (沿用 v2 段标记模式)
2. 不写 cron/control plane (硬红线)
3. tick39 audit 回读 verify 是否被采纳