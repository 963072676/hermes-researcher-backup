# 跨 Profile 影响图 + Cross-cluster arrows — 2026-07-13（tick35）

## 结论

本 tick 归一化为 **5 P1 cluster + 5 cross-cluster arrows**(沿用 tick34 立的 9 family registry,本 tick 立卡第 10 family `cron-installer-handoff-state`)。
新立卡:1 family + 5 cross-cluster arrows + 1 trust boundary 升级(fabrication)。
影响面从 session state 向 update handoff + cross-cluster acceptance 扩散,所有生产写入仍禁止;本仓库只保存草稿。

## 节点

- **F1** silent-fail
- **F2** cross-platform-state
- **F5** cron-session-leak-closed-state
- **F7** MCP-supply-chain
- **F8** cron-ticker-resilience
- **F9** session-state-integrity-deck
- **F10 NEW** cron-installer-handoff-state
- **TB1** trust-boundary (cross-cutting)

## Cross-cluster arrows (NEW skill: hermes-cross-cluster-state-integration-v1)

### severity-A (chief 6h triage)

```
CCA-1: F9-F5-prune-zombie-mis-kill
   from_family: F9 #63128 prune live session
   to_family:   F5 #41935 zombie cron session
   severity: severity-A
   interaction: F9 fix 上线后 prune 默认 skip liveness check → 误杀 F5 zombie → 双重漏算
   default_impact: cron worker 跑时,僵尸 cron session 被 F9 prune 当作 live 误杀
   watch_signal: zombie cron session count (sessions.source=cron AND ended_at IS NULL) > 5 AND age > 7 day
```

### severity-B (chief 24h joint review)

```
CCA-2: F7-F10-hardening-stale-config
   from_family: F7 MCP hardening
   to_family:   F10 #35406 Docker migration gap
   severity: severity-B
   interaction: F7 hardening PR 合入,但 F10 Docker boot hook 不跑 migrate → hardening control 在 stale config 下不生效
   default_impact: Docker 安装 default profile 跑 v0.19.0 后 MCP hardening control 失效
   watch_signal: raw config.yaml _config_version != effective version

CCA-3: F9-F8-lock-ticker-silent
   from_family: F9 #63129 lock fail-open
   to_family:   F8 #32612 ticker silent die
   severity: severity-B
   interaction: F9 lock fail-open (unknown exception → ALLOW) + F8 ticker silent die → lock subsystem error + ticker heartbeat 缺失
   default_impact: cron worker 在 lock 异常时 ticker 死亡,session 不能 end_session
   watch_signal: lock subsystem error count + ticker heartbeat 缺失
```

### severity-C (进 daily report)

```
CCA-4: F1-F5-no-agent-silent-fallback
   from_family: F1 silent-fail
   to_family:   F5 no_agent cron path
   severity: severity-C
   interaction: F1 silent_fallback 是否覆盖 F5 cron_mode=deny?no_agent 路径未明确
   default_impact: cron worker silent fallback 在 no_agent 模式未定义
   watch_signal: cron_mode=deny + no_agent=True 组合的 audit log

CCA-5: F2-F9-observer-memory-confusion
   from_family: F2 #51646 cross-platform memory loss
   to_family:   F9 #63207 observer disconnect
   severity: severity-C
   interaction: F2 cross-surface identity confusion + F9 observer disconnect finalize live session → cross-surface identity + state inconsistency
   default_impact: TUI/dashboard 关闭后 messaging session 状态不一致
   watch_signal: live session count 跨 surface 不一致
```

## Chain 1 — F9 session state integrity tier-2 (5 issue)

```text
GH #62365 (fabricated user intent, trust_boundary_impact=fabrication)
 + #63008/#63018 (compaction-runaway, fallback degradation R1-R6)
 + #63129 (lock acquisition UNKNOWN fail-open)
 + #63128 (prune live session → CCA-1 severity-A with F5)
 + #63207 (observer disconnect finalize messaging)
        ↓
chief SOUL: trust_boundary_impact != none → 6h SLA (pm acceptance contract v3)
        ↓
dev SOUL: 5 tier-2 implementation_strategy 各 1 个 fix PR
        ↓
qa SOUL: trust boundary e2e 4 tests (hermes-trust-boundary-e2e-v1) all PASS
        ↓
pm SOUL: 11-field P1 acceptance contract v3 with cross_cluster_arrows + trust_boundary_impact
        ↓
default: cross_cluster_watch_list CCA-1 ~ CCA-5 watch signals 监控
        ↓
MCP propose M1 + skill hermes-cross-cluster-state-integration-v1 + hermes-trust-boundary-e2e-v1
```

Marker: `sweeper marker attached` (沿用 tick32 paraphrase 表)。

## Chain 2 — F10 NEW cron-installer-handoff-state (3 issue)

```text
GH #61093 (open, Desktop update handoff home resolution — profile-scoped home + base home)
 + #35406 (closed but root cause broader, Docker image update no migrate_config)
 + #35458/#35508/#36627 (closed PRs, only fixed Docker boot hook, not dev layer)
        ↓
chief SOUL: F10 立卡 + cross-cluster integration arrow CCA-2 severity-B
        ↓
dev SOUL: _read_raw_config_version + check_config_version 双读
        ↓
qa SOUL: release_verification_v5 f10_docker_migration_check 4 测例
        ↓
default: update_handoff_readiness_v1 5 steps (HERMES_HOME / raw_config_version / cron_worker / marker dual / trust boundary)
        ↓
MCP propose M2 + skill hermes-update-handoff-readiness-v1
```

Marker: `sweeper marker attached` (F10 family)。

## Chain 3 — F7 MCP supply chain hardening closed + open

```text
GH #45620 (closed, Hermes 官方 attribution 不成立但开 5 hardening PR)
 + #38017 (open, catalog install.ref pinning → bootstrap 可执行 attacker code)
 + #45886 (mentioned, fix config reject MCP shell egress)
        ↓
chief SOUL: F7 已合并但需 verify cross-cluster (CCA-2)
        ↓
default: cross_cluster_watch_list CCA-2 watch
        ↓
MCP propose M3
```

## Cross-cluster acceptance plan

| arrow | severity | sign-off | 时间线 |
|---|---|---|---|
| CCA-1 F9↔F5 | severity-A | chief sign-off required | 6h triage |
| CCA-2 F7↔F10 | severity-B | chief joint review | 24h joint |
| CCA-3 F9↔F8 | severity-B | chief joint review | 24h joint |
| CCA-4 F1↔F5 | severity-C | daily report | 不阻塞 |
| CCA-5 F2↔F9 | severity-C | daily report | 不阻塞 |

## Watch signals (default profile cron 监控)

```bash
# zombie cron session 监控 (CCA-1)
sqlite3 ~/.hermes/state.db "SELECT COUNT(*) FROM sessions WHERE source='cron' AND ended_at IS NULL AND started_at < datetime('now', '-7 day');"

# raw vs effective config_version (CCA-2)
python3 -c "from hermes_cli.config import read_raw_config_version, load_config; raw=read_raw_config_version(Path.home()/'.hermes/config.yaml'); eff=load_config().get('_config_version'); print(f'raw={raw} eff={eff} stale={raw!=eff}')"

# lock subsystem error count (CCA-3)
grep -c "lock subsystem unavailable" ~/.hermes/logs/cron.log

# cron_mode=deny + no_agent audit (CCA-4)
grep -c "cron_mode=deny" ~/.hermes/logs/cron.log | head -100

# live session cross-surface (CCA-5)
sqlite3 ~/.hermes/state.db "SELECT source, COUNT(*) FROM sessions WHERE ended_at IS NULL GROUP BY source;"
```

## 5 profile 联动

| Profile | 影响 | 草稿 |
|---|---|---|
| chief | cross_cluster_integration_v1 + F10 立卡 | SOUL_chief |
| pm | p1_acceptance_contract_v3 (11-field) | SOUL_pm |
| dev | f9_tier2_implementation_strategy + f10_docker_migration_dev_fix | SOUL_dev |
| qa | release_verification_v5 (42 verify points) | SOUL_qa |
| default | update_handoff_readiness_v1 + cross_cluster_watch_list | SOUL_default |

## 引用

- tick34 立卡:9 family registry + F9 session-state-integrity-deck
- tick33 立卡:cron-ticker-resilience-deck + 6-control MCP supply chain
- tick32 立卡:cron-session-leak-closed-state + outbound-redact-call-site + 6-field MCP canonical
- tick31 立卡:Python verifier secret scan v4 + memory-injection-cross-platform + credential-pool-stale-snapshot