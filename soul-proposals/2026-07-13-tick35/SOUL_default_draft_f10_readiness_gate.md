# SOUL default 草稿 — F10 update handoff + cross-cluster readiness gate (tick35)

> 来源:hermes-researcher-self-evolution-v1 / 2026-07-13 tick35
> 目标 profile:default
> 适用版本:F10 #35406 + #61093 update handoff home resolution + cross-cluster F9↔F5 readiness

## 背景

tick35 观察到 default profile 在 F10 update-handoff + F9↔F5 cross-cluster 场景下的具体 readiness gap:

1. **#61093 (open)** — Desktop update handoff home resolution — profile-scoped home + base home fallback for staged updater。default profile 用 `~/.hermes/` 而非 profile-scoped,所以本机**不受此 bug 直接影响**,但 5 profile 都用 default home 的话,任何 profile 启动的 desktop 都受影响。

2. **#35406 (closed but root cause broader)** — Docker boot hook 不跑 migrate_config + `check_config_version()` 用错了 source of truth。default profile 如果跑 Docker 镜像更新,**所有 5 profile × config.yaml 跨 release 累积 stale**。本机是 Linux (6.8.0-63-generic) 不是 Docker,但 readiness 必须覆盖此路径。

3. **F9↔F5 cross-cluster** — F9 #63128 prune live session 误杀 F5 #41935 zombie cron session。default profile 跑 cron worker,本 tick 直接受影响(沿用 tick34 立卡)。

## 草稿段落(append to default SOUL)

```yaml
default:
  update_handoff_readiness_v1:
    description: F10 update handoff + Docker migration gap readiness 在 default profile 验证
    applicable_when: default profile 启动 + update / boot / cron worker 启动
    pre_update_checklist:
      - [ ] HERMES_HOME 单一 source:env $HERMES_HOME + active home 优先, base home fallback
      - [ ] profile-scoped home 时:base home 包含 staged updater, marker 必须两 home 都写
      - [ ] staged updater resolved from candidate ladder (active → base)
      - [ ] cwd / child HERMES_HOME / PATH 都从 selected home 派生,not mixed
      - [ ] pre-written update markers cover both homes for relaunch inspection
    boot_checklist:
      - [ ] Docker stage2-hook.sh 含 migrate_config 调用 (non-interactive)
      - [ ] config.yaml + .env backup 写在 migrate 前
      - [ ] _read_raw_config_version 与 effective version 同时检测
      - [ ] raw missing _config_version → trigger migrate (不依赖 DEFAULT_CONFIG 继承)
      - [ ] HERMES_SKIP_CONFIG_MIGRATION=1 opt-out 走 warning path,not silent skip
    cron_worker_checklist:
      - [ ] F9 #63128 prune 不误杀 cron session (liveness preservation)
      - [ ] F5 #41935 no_agent cron 必须 end_session
      - [ ] F5 zombie session 不能被 F9 prune 双重漏算 (cross-cluster arrow severity-A)
      - [ ] 跑 cron worker 前先检查 raw config_version != effective → trigger migrate 后再启
    readiness_gate:
      description: default profile 启动前必须过 readiness gate,失败立即停
      steps:
        - step_1: env HERMES_HOME + active home + base home 验证
        - step_2: config.yaml raw _config_version 与 effective version 比较
        - step_3: cron worker no_agent end_session 验证 (5 sample 抽样)
        - step_4: update marker 双 home 写验证
        - step_5: trust boundary e2e (no fabrication / no fail-open / no auth material leak)
      exit_0_required: true
      emergency_skip:
        - HERMES_READINESS_SKIP=update_handoff (only for hotfix)
        - HERMES_READINESS_SKIP=docker_migration (only for non-Docker install)
        - HERMES_READINESS_SKIP=trust_boundary (FORBIDDEN)

  cross_cluster_watch_list:
    description: 5 cross-cluster arrows 当前活跃,default profile 跟踪
    arrows:
      - arrow_id: CCA-1
        from_family: F9 session-state-integrity
        to_family: F5 cron-session-leak-closed-state
        severity: severity-A
        interaction: F9 #63128 prune live session 会误杀 F5 #41935 zombie cron session
        default_impact: cron worker 跑时,F9 fix 上线后 F5 双重漏算
        watch_signal: zombie cron session count (sessions.source=cron AND ended_at IS NULL) > 7 days
      - arrow_id: CCA-2
        from_family: F7 MCP-supply-chain
        to_family: F10 cron-installer-handoff-state (NEW)
        severity: severity-B
        interaction: F7 hardening 不解决 stale config,F10 Docker migration gap 让 hardening 不生效
        default_impact: Docker 安装 default profile 跑 v0.19.0 后 MCP hardening control 失效
        watch_signal: raw config.yaml _config_version != effective version
      - arrow_id: CCA-3
        from_family: F9 session-state-integrity
        to_family: F8 cron-ticker-resilience
        severity: severity-B
        interaction: F9 #63129 lock fail-open 配合 F8 #32612 ticker silent die → cron session lock leak + ticker die
        default_impact: cron worker 在 lock 异常时 ticker 死亡
        watch_signal: lock subsystem error count + ticker heartbeat 缺失
      - arrow_id: CCA-4
        from_family: F1 silent-fail
        to_family: F5 cron-session-leak
        severity: severity-C
        interaction: F1 silent_fallback 是否覆盖 F5 cron_mode=deny? no_agent 路径未明确
        default_impact: cron worker silent fallback 在 no_agent 模式未定义
        watch_signal: cron_mode=deny + no_agent=True 组合的 audit log
      - arrow_id: CCA-5
        from_family: F2 cross-platform-state
        to_family: F9 session-state-integrity
        severity: severity-C
        interaction: F2 #51646 cross-platform memory loss + F9 #63207 observer disconnect → cross-surface identity confusion
        default_impact: TUI/dashboard 关闭后 messaging session 状态不一致
        watch_signal: live session count 跨 surface 不一致

  upgrade_blocked_until:
    description: default profile 升级被阻塞直到 readiness_gate 全过
    conditions:
      - raw_config_version != effective_config_version → block + require migrate
      - cron_worker_no_agent_audit_fail → block + require dev fix
      - update_marker_single_home → block + require dual-home write
      - trust_boundary_e2e_fail → block (FORBIDDEN to skip)
```

## Why this matters

- default profile 是所有 profile 的 baseline,如果 default 升级 readiness 失败,所有 sub-profile 也失败
- F10 #35406 Docker 根因在 default 视角的 config_version check,必须 readiness 验证
- 5 cross-cluster arrows 中 CCA-1 (F9↔F5) 直接影响 cron worker,必须 watch signal 监控

## Acceptance criteria

1. default profile 启动前跑 readiness_gate 5 步,失败立即停 + 飞书报错
2. cron worker 跑时 watch 5 cross-cluster arrows 的 signal
3. 升级前必须过 raw_config_version_check + cron_worker_no_agent_audit
4. trust_boundary_e2e 不能 skip
5. 5 SOUL 配额中此条占 default 段