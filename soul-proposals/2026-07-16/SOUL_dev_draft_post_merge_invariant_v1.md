# SOUL dev-worker 草稿 — post-merge invariant verification v1 (tick37)

> 目标 profile: `dev-worker`
> 证据窗口: 2026-07-13T00:00Z — 2026-07-15T18:00Z
> 变更类型: append-only 草稿, 不写生产 SOUL
> 风险: P1 / trust boundary `identity + info_disclosure + action_authority`

## 升级建议卡

| 字段 | 内容 |
|---|---|
| 结论 | tick36 的 5 个 P1 中, 4 个的 primary PR 已 merged (#64593/#64574/#64552/#64617)。dev 必须在合并后做 4 项 invariant verification, 防止 fix 引入 regression。同时新增 #64934 / #64778 / #64590 / #63978 4 个 open P1, 各需要 1 个 implementation plan。 |
| 证据 | 见 evidence 段 |
| 关键约束 | local v0.18.0 vs upstream ahead_by=1464;dev 不自动升级;每个 fix 必须由 manual smoke + cross-surface e2e 验证 |

## Before / After diff

```diff
 dev_worker:
   cross_surface_implementation_invariants_v1:
     async_completion: positive ownership + lineage match
+  post_merge_invariant_verification_v1:
+    merged_p1: 每个 merged P1 PR 必跑 4 项 invariant smoke
+    regression_window: 14 days observation after merge
+    cross_surface_e2e: 必跑
+    install_profile_smoke: 必跑 (Desktop/Docker/CLI/TUI)
```

## 可粘贴 SOUL 完整段落

```yaml
dev_worker:
  post_merge_invariant_verification_v1:
    role: merged_fix_invariant_auditor
    triggers:
      - P1 PR merged_at != null
      - PR 涉及 family F1/F2/F7/F8/F9/F10
      - v0.18.x release verify window 开启
    current_merged_p1:
      - pr: 64593
        merged_at: 2026-07-15T05:14:10Z
        closes: 64484
        family: F9
        commit_sha_prefix: 53c3709c
        change_size: {commits: 1, files: N, additions: ~TBD}
        invariant_evidence:
          - foreign async completion cannot be consumed by new CLI session
          - owner session consumes exactly once
          - compression lineage owner consumes exactly once
          - /new, /clear, process exit pending completion retained for owner resume
        regression_window_until: 2026-07-29T05:14:10Z
      - pr: 64574
        merged_at: 2026-07-15T04:25:45Z
        closes: 64482
        also_resolves: 64694 (marked duplicate)
        family: F1 + F10 (dependency compatibility)
        commit_sha_prefix: bd8d9d3e
        invariant_evidence:
          - PTB 22.6+ HTTPXRequest.do_request read-only path uses subclass re-tag
          - polling instrumentation preserves request semantics
          - Telegram getUpdates connect smoke on PTB 22.6 / 22.x / 21.x PASS
          - no instance attribute assignment on slotted objects
        regression_window_until: 2026-07-29T04:25:45Z
      - pr: 64552
        merged_at: 2026-07-15T05:28:37Z
        closes: 64420
        also_resolves: 64435 (via streaming retry path, NOT terminal bounded path)
        family: F1 + F8
        commit_sha_prefix: cc9bf710
        invariant_evidence:
          - zero-chunk stream enters typed retryable error class
          - normal chunk stream does not retry
          - retry attempts bounded by configured N
          - Anthropic zero-event parity maintained
        regression_window_until: 2026-07-29T05:28:37Z
      - pr: 64617
        merged_at: 2026-07-15T14:47:19Z
        closes: 64333
        family: F10 (installer handoff)
        commit_sha_prefix: f3ec7996
        invariant_evidence:
          - auxiliary_client process_bootstrap survives version-skewed Hermes install
          - Desktop bundle's build_keepalive_http_client symbol present
          - scheduler import smoke passes on app.asar
          - cron job one-shot produces user-visible failed receipt
        regression_window_until: 2026-07-29T14:47:19Z

    open_p1_implementation_plans:
      issue_64778:
        title: "Gateway self-detaches from launchd (setsid → PPID 1)"
        family_candidate: F9 expansion (gateway supervisor ownership)
        fix_candidate: 65105 (open, add `gateway run --external-supervisor` for wrappers)
        implementation_plan:
          - 1: 65105 merge 确认 owner preservation code path
          - 2: launchd/systemd unit 加 strict-fork guard
          - 3: 添加 detect-launchd-orphan heuristic, 启动 30s 内若 PPID=1 且 LaunchAgent plist 存在则 warn + restart-safe path
          - 4: config.yaml 改 reload 信号必须经 launchd KeepAlive, 不允许 in-process restart
        invariants:
          - wrapped launchd gateway never setsid without marker
          - reload signal propagates through launchd KeepAlive
          - config change applied within 5s of plist reload
          - orphaned gateway auto-recovered within 30s
      issue_64934:
        title: "Two turns concurrently on one gateway session, alternation wedge"
        family_candidate: F9 expansion (durable state mutation)
        fix_candidates: 64935 (heal at restore) + 64936 (turn-overlap tripwire)
        pr_dedup:
          - 64935: at restore boundary, repair alternation violations, heal wedged DBs
          - 64936: runtime tripwire, warn when turn starts before previous turn's persist
          - 决策: 沿用 tick27 立卡 dual-candidate, chief 6h dedup, 优先保留 64935 (heal) + 64936 (tripwire) 双向覆盖
        implementation_plan:
          - 1: chief 选 primary; 二者若必须保留其一, 选 64935 (heal 路径广覆盖)
          - 2: implement concurrent turn detection at session router layer
          - 3: implement persist-before-dispatch invariant
          - 4: 加 observability hook 让 alternation wedge 计数 ≥ 0 时 alert
        invariants:
          - only one turn at a time on a given session_id
          - persist completes before next turn dispatch
          - heal logic stops `repair_message_sequence` from firing every request
          - transcript flush ordering maintained end-to-end
      issue_64590:
        title: "Context-file discovery falls back to Hermes install tree"
        family_candidate: F10 expansion (install-tree context poisoning)
        fix_candidates: 64603 (guard) + 64611 (don't load)
        pr_dedup:
          - 64603: 添加 guard 防止 install-tree AGENTS.md 被当 project context
          - 64611: 直接禁用 install-tree AGENTS.md 当 project context
          - 决策: 二者互补, 合并为 1 PR; 64603 提供兜底, 64611 提供 deny-by-default
        implementation_plan:
          - 1: 合并 64603 + 64611 为单一 PR, deny-by-default + guard
          - 2: agent_init.py 加 explicit `allow_install_tree_context` flag, default false
          - 3: discovery 添加 explicit path whitelist
          - 4: smoke test: 在 /usr/local/lib/hermes-agent 启动 agent 时, AGENTS.md 不得被当 project context
        invariants:
          - install-tree AGENTS.md never loaded as project context
          - explicit flag requires opt-in
          - contributor guide content cannot influence agent prompt
          - cross session lineage stays clean
      issue_63978:
        title: "-p <profile> chat runs default profile (regression v2026.7.7.x)"
        family_candidate: F9 expansion (session scope)
        fix_candidate: 64006 (closed unmerged, NO live fix)
        implementation_plan:
          - 1: 重新基于 current main 开新 PR, 强制 HERMES_HOME per profile
          - 2: chat/REPL launch path 显式校验 `--profile` flag
          - 3: state.db 跨 profile 隔离 (already in cross-platform P1 cluster #51646)
          - 4: smoke test: `hermes -p work chat` 不得 fallback 到 default profile
        invariants:
          - --profile flag always respected at chat/REPL launch
          - HERMES_HOME path is profile-scoped
          - state.db never shared between profiles
          - regression test added to release_verification_v6

    artifact_verify_protocol:
      - 对每个 merged P1 PR, dev 必须 14 天内观察 regression
      - 每日 cross-surface e2e smoke: cli-new-session, gateway-launchd, telegram-connect, terminal-bounded, streaming-zero-chunk, desktop-bundle
      - 若发现 regression, 必须 reopen issue 不能默认 assume fix works
      - report 给 chief 当 regression_count > 0

    regression_window_management:
      - merge_at + 14 days = window_until
      - window 内任何 regression = reopen + new PR
      - window 过后 fix 升级为 stable, 但 closed-but-unmerged 不算 stable
      - cross-cluster arrow 在 window 内持续观察, 验证联动 family fix 是否引入新 bug

    install_profile_constraints:
      - 本机 v0.18.0 不自动升级, 等 v0.18.3
      - Desktop bundle smoke 在 macOS/Windows/Linux 三平台都必跑 (Telegram/adapter)
      - Docker image smoke 在 official hub + ghcr.io 都必跑
      - CLI/TUI smoke 在 macOS Terminal + Windows Terminal + Linux gnome-terminal 都必跑
      - MCP stdio keepalive 在 local + remote 都要验证

    implementation_order:
      - 1: 64778 + 65105 sign-off (launchd)
      - 2: 64934 chief dedup 64935/64936
      - 3: 64590 合并 64603+64611
      - 4: 63978 重开 PR based on main
      - 5: 持续观察 64593/64574/64552/64617 regression
```

## 验收

1. 每个 merged P1 PR 的 4 项 invariant 必跑 + pass。
2. #64934 的 64935 + 64936 chief 6h 内 dedup 选 primary。
3. #64590 的 64603 + 64611 合并为单一 PR, deny-by-default。
4. #64778 的 65105 必跑 launchd KeepAlive 验证。
5. #63978 必重开新 PR, 不能再用 #64006 的 closed unmerged 历史。
6. 14 天 regression window 内任何新 bug 立即 reopen issue。