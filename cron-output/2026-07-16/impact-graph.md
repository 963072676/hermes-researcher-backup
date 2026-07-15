# 跨 Profile 影响图 — 2026-07-16 (tick37)

> hermes-researcher-deep-tick-daily
> 北京时间 2026-07-16 02:02 启动; UTC 2026-07-15 18:02
> latest release: v0.18.2 (2026-07-08T03:11:22Z), release day +7
> local: v0.18.0, local commit 4d5d9fff +1 carried commit
> upstream main: da4a28ec (2026-07-15T17:55:41Z)
> compare local...main: upstream ahead_by 1464, behind_by 0
> 当前阶段: **post-rediscovery verification window v1** (tick36 hot window 之后 36h)

## 结论

tick36 立的 5 个 P1 cluster 中, 4 个进入 release_verify_pending 阶段 (primary PR 已 merged), 1 个 (#64435) 通过不同路径 (#64552 zero-chunk retry) 部分修复。新增 4 个 open P1 (#64934 alternation wedge + #64778 launchd orphan + #64590 install-tree AGENTS.md + #63978 -p regression)。family registry 维持 10 family, 不立 F11。total cross-cluster arrows = 4。

| 信号 | 来源 | 状态 | family | 4-state |
|---|---|---|---|---|
| #64593 | PR merged #64484 | 2026-07-15T05:14Z | F9 | release_verify_pending |
| #64574 | PR merged #64482+#64694 | 2026-07-15T04:25Z | F1+F10 | release_verify_pending |
| #64552 | PR merged #64420+#64435 via streaming | 2026-07-15T05:28Z | F1+F8 | release_verify_pending |
| #64617 | PR merged #64333 | 2026-07-15T14:47Z | F10 | release_verify_pending |
| #64934 | issue open, 2 PR open | 2026-07-15T11:27Z | F9 | implementation_pending |
| #64778 | issue open, PR #65105 open | 2026-07-15T05:33Z | F9 candidate F11 | implementation_pending |
| #64590 | issue open, 2 PR open | 2026-07-14T20:41Z | F10 candidate F11 | implementation_pending |
| #63978 | issue open, #64006 closed unmerged | 2026-07-13T20:57Z | F9 | implementation_pending (no live fix) |

## P1 证据表 (closed-but-not-fixed cluster)

| Evidence | State | Family | Path-to-fixed |
|---|---|---|---|
| #64593 | merged | F9 | v0.18.3 artifact verify + 14d regression window |
| #64574 | merged | F1+F10 | v0.18.3 artifact verify + Telegram connect smoke |
| #64552 | merged | F1+F8 | v0.18.3 artifact verify + zero-chunk stream smoke |
| #64617 | merged | F10 | v0.18.3 artifact verify + Desktop bundle smoke |
| #63219 | merged | F9 | v0.18.2+ verify + ws_orphan_reap recover smoke |
| #63422 | merged | F9 | v0.18.2+ verify + compression state probe fail-closed |
| #63533 | merged | F4 | v0.18.2+ verify + credential pool validate smoke |
| #64365 | merged | F8 | v0.18.2+ verify + cron long-running one-shot smoke |
| #64362 | merged | F9 | v0.18.2+ verify + active-process check fail-closed |
| #64381 / #64370 / #64368 / #64361 / #64355 / #64348 | merged | F1+F9 | v0.18.2+ verify + Telegram + state cluster smoke |
| #64004 | merged | F9 | v0.18.2+ verify + CLI close transcript |
| #63402 | merged | F8 | v0.18.2+ verify + cron live one-shot |
| #64006 | closed unmerged | F9 | REJECTED — reopen + new PR needed for #63978 |
| #64524 / #64448 | closed unmerged | F8 | REJECTED — alternative fix path #64552 only |
| #64506 | closed unmerged | F1+F10 | REJECTED — alternative fix #64574 wins |
| #64359 | closed unmerged | F10 | REJECTED — alternative fix #64617 wins |
| #64420 | closed unmerged | F1+F8 | REJECTED — salvage fix #64552 wins |

## Open P1 cluster (未修)

| Issue | Title | State | Family | Fix candidate | Dedup |
|---|---|---|---|---|---|
| #64934 | Two turns concurrently on one gateway session, alternation wedge | open | F9 | #64935 + #64936 | dual-candidate, chief 6h dedup |
| #64778 | Gateway self-detaches from launchd (setsid → PPID 1) | open | F9 candidate F11 | #65105 open | single-candidate, no fire |
| #64590 | Context-file discovery falls back to Hermes install tree | open | F10 candidate F11 | #64603 + #64611 | dual-candidate, chief 6h dedup |
| #63978 | -p <profile> chat runs default profile (regression v2026.7.7.x) | open | F9 | #64006 closed unmerged, NO live fix | reopen + new PR |
| #64694 | Telegram adapter crashes on startup (PTB 22.6 conflict) | open (duplicate) | F1+F10 | #64574 merged → expected to close | trust fix |

## Cross-cluster arrows (4 total)

### severity-A — chief 6h triage

```text
F9-F1-concurrent-turn-alternation
  from: F9 session-state-integrity (#64934)
  to:   F1 message-delivery/silent-fail
  interaction: concurrent turn 让 durable transcript 错位, repair_message_sequence 每请求都跑,
               全量 history 被多次复制到 repair log
  trust_boundary_impact: info_disclosure (history 复制) + identity (lineage 错位)
  required_fix: positive ownership + persist-before-dispatch invariant
  primary_candidates: #64935 (heal at restore) + #64936 (turn-overlap tripwire)
```

### severity-B — chief 24h joint review

```text
F9-F1-launchd-supervisor-misroute
  from: F9 session-state-integrity (#64778)
  to:   F1 message-delivery/silent-fail
  interaction: gateway self-detach 让 launchd KeepAlive 误以为进程独立,
               config 变更不再触发 reload, 后续 launchctl 操作可能误判
  trust_boundary_impact: identity (process identity confusion)
  required_fix: external-supervisor flag + supervisor ownership preservation
  primary_candidate: #65105 (open)
  family_decision: maintain F9 expansion; promote to F11 only after #65105 merged

F10-F1-install-tree-context-poisoning
  from: F10 installer-handoff (#64590)
  to:   F1 message-delivery (agent_init 把 contributor guide 内容当 prompt)
  interaction: agent_init 把 install-tree AGENTS.md 当 project context,
               contributor guide 内容被当 prompt, 跨 session lineage 错位
  trust_boundary_impact: identity (lineage confusion) + action_authority (untrusted guidance)
  required_fix: deny-by-default + explicit allow flag + path whitelist
  primary_candidates: #64603 (guard) + #64611 (don't load), must merge as 1 PR
```

### severity-C — 进 daily report

```text
F9-F1-durable-restoration-after-merge
  from: F9 (merged fix #64593)
  to:   F1
  interaction: #64593 修复路径已 in main, 但本机仍 v0.18.0,
               用户的 durable restore 路径未切到新 code, 仍可能跨 CLI session
  trust_boundary_impact: identity
  required_fix: 本机升级到 v0.18.3 + cross_profile_audit
  observation_window: 14 days since 2026-07-15T05:14Z
```

## Family lifecycle (10 family, no new F11)

| # | Family | tick37 lifecycle | 变化 |
|---|---|---|---|
| 1 | silent-fail | expansion | #64574+#64552 merged; #64694 trust close pending |
| 2 | cross-platform-state | stable | 无新 P1 |
| 3 | memory-injection-cross-platform | stable | 无新 P1 |
| 4 | credential-pool-stale-snapshot | expansion | #63533 merged (validation); need artifact verify |
| 5 | cron-session-leak-closed-state | maintenance | 无新 P1 |
| 6 | outbound-redact-call-site | maintenance | 无新 P1 |
| 7 | MCP-supply-chain-protocol-migration | expansion | MCP 2026-07-28 final 12d countdown |
| 8 | cron-ticker-resilience-deck | expansion | #64552 merged (zero-chunk fix); #64435 closed-via-#64552 path |
| 9 | session-state-integrity-deck | expansion | #64593+#64934+#64778 active; #63978 no live fix |
| 10 | cron-installer-handoff-state | expansion | #64617 merged; #64590 active |

F11 候选评估:
- `gateway-supervisor-ownership` (#64778 + #65105): 1 issue, 1 PR open — 不达 tick36 立卡阈值
- `install-tree-context-poisoning` (#64590 + #64603/#64611): 1 issue, 2 PR open — 不达阈值
- `concurrent-turn-alternation` (#64934 + #64935/#64936): 1 issue, 2 PR open — 不达阈值

判定: **维持 10 family**, tick38+ 若任一 cluster 拉新 issue ≥ 5 或跨三平台同根, 才立 F11。

## 5 profile 依赖链 (v0.18.3 readiness)

```text
External evidence
  ├─ #64593 async ownership fix (merged)
  ├─ #64574 Telegram PTB 22.6 fix (merged)
  ├─ #64552 zero-chunk stream retry (merged)
  ├─ #64617 auxiliary_client process_bootstrap (merged)
  ├─ #64934 alternation wedge (2 PR open, chief 6h dedup)
  ├─ #64778 launchd orphan (PR #65105 open)
  ├─ #64590 install-tree AGENTS.md (2 PR open)
  ├─ #63978 -p regression (NO live fix)
  └─ MCP 2026-07-28 final 12d countdown
        ↓
chief-agent
  - p1_post_rediscovery_verification_window_v1
  - 4-state machine: closed_only / closed_unmerged / closed_merged_no_artifact / closed_merged_artifact_verified
  - 6h dedup SLA for #64934 + #64590 dual-candidate
  - 24h sign-off for #65105 supervisor ownership
        ↓
pm-orchestrator
  - acceptance v4 15-field → v5 17-field (candidate_pr_dedup_state + artifact_verify_required_for_release)
  - new state machine extension
  - 5 tick37 records updated
        ↓
dev-worker
  - post_merge_invariant_verification_v1 (4 merged P1 PR 14d window)
  - 4 open P1 implementation plans
  - regression_window_until = merge_at + 14d
        ↓
qa-worker
  - release_verification_v6 68 → v7 72 (4 post-merge checks)
  - 12 runtime smoke per family (F1+F8+F9+F10 + 4 family)
  - 5 install profile全过 verify
        ↓
default
  - post_rediscovery_safe_defaults_v1
  - profile_switching: HERMES_HOME 显式
  - telegram: disable until v0.18.3
  - zero_chunk_stream: 显式 timeout + bounded retry
  - MCP 2026-07-28 countdown 12d
  - regression window 14d 观察 4 merged PR
```

## Skill 映射

| Skill draft | Covers |
|---|---|
| `hermes-post-merge-regression-window-guard-v1` | #64593 / #64574 / #64552 / #64617 + 14d regression window |
| `hermes-mcp-2026-07-28-final-readiness-v1` | MCP 2026-07-28 final 6 SEP + auth + transport + infrastructure |
| `hermes-launchd-supervisor-ownership-preserver-v1` | #64778 + #65105 external-supervisor + macOS launchd / Linux systemd |

## 15-field v4 → 17-field v5 升级

新增 2 字段:
1. `candidate_pr_dedup_state` (5 sub-fields)
2. `artifact_verify_required_for_release` (6 sub-fields)

ship gate 50 + 4 acceptance-field delta + 14 runtime = 68 (tick36 v6)
升 v7: 68 + 4 post-merge regression window = **72**

```text
5 grep + 20 cross-profile permission + 6 MCP supply chain + 17 P1 acceptance v5
+ 4 cross-cluster arrows + 4 trust boundary e2e + 12 runtime smoke per family
+ 4 post-merge regression window = 72
```

## MCP 2026-07-28 readiness (12 天倒计时)

6 SEPs 影响 default profile:
- SEP-2575 (initialize handshake removed)
- SEP-2567 (Mcp-Session-Id removed)
- SEP-2243 (Mcp-Method + Mcp-Name headers mandatory)
- SEP-2260 + SEP-2322 (long-lived SSE removed, multi-round-trip)
- SEP-2164 (-32002 → -32602 error code)
- 6 auth SEPs (iss validation + application_type + issuer binding)

本 default profile 保持 stable SDK, branch-only exact-pin beta SDK 仅 dev profile。
production release 等 hermes-agent official MCP 2026-07-28 SDK 升级后再评估。

## arxiv 方向加证 (不单独升 P1)

- [arXiv:2607.07405](https://arxiv.org/abs/2607.07405): Reason Less, Verify More — deterministic pre-execution gates 在 policy-permissive tools 上 recover silent policy-violation writes 78% → 42.0% success (gpt-4o-mini), +12.4pp P=0.0012。映射 trust boundary `action_authority`。
- [arXiv:2606.29073](https://arxiv.org/html/2606.29073): From Tool Connection to Execution Control — HCP handle-capability protocol reference runtime, 8 invariants: metadata non-authority, grant-backed approval, canonical resources, principal binding, scoped capability invocation, source-and-target data-flow authorization, deny-path audit, explicit protocol state。HCP 阻断全部 10 modeled attack, MCP-like baselines 漏 6。
- [arXiv:2602.14281](https://arxiv.org/abs/2602.14281): MCPShield — security cognition layer (pre-invocation probing + isolated projection + periodic reasoning), 6 attack scenarios 跨 6 LLM backbone, in-domain GuardedJoint 84.2, balanced OOD 56.9。
- [arXiv:2605.24069](https://arxiv.org/abs/2605.24069): When the Manual Lies — MCP-TDP Security Benchmark, tool description poisoning 95.2% ASR (Supply Chain attack) > 82.8% (Trojan Horse), leading models GPT-4o nearly 100% in 6 scenarios。
- [arXiv:2607.02116](https://arxiv.org/html/2607.02116): ContextNest — verifiable context governance, governed selection Pareto-dominates BM25 (97% vs 93-90%) at ~1/3 token cost。

## Watch signals

1. CLI boot 5s 内 foreign completion count > 0 → P1 alert (沿用 tick36)
2. foreground terminal RSS delta > 4 × max_bytes → fail
3. artifact manifest source commit != bundled commit → ship block
4. messaging platform configured > 0 且 connected = 0 → gateway health fail
5. zero-chunk stream retries > configured bound → visible error
6. issue closed but linked primary PR mergedAt=null → state=verification_pending (沿用 tick36)
7. PPID=1 + LaunchAgent plist 存在 → launchd orphan
8. -p <profile> falls back to default → fail closed (沿用 #63978)
9. closed_unmerged PR counted as fix → reject ship
10. MCP 2026-07-28 final 倒计时 12d → final 7d 内必跑 readiness