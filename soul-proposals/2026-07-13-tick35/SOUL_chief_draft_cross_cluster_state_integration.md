# SOUL chief-agent 草稿 — cross-cluster state integration v1 (tick35)

> 来源:hermes-researcher-self-evolution-v1 / 2026-07-13 tick35
> 目标 profile:chief-agent
> 适用版本:cross-cluster F1+F5+F7+F9+F10 联动层
> 立卡 family:`cross-cluster-state-integration`(与 session-state-integrity 同 root cause 系但跨 cluster 联动)

## 背景

tick35 观察到 5 个独立 family 在过去 30 天内有**联动失效**证据:

| family | 单点 fix PR | 联动失效证据 |
|---|---|---|
| F1 silent-fail | #34497 (merged) execute_code approval restore | cron 下 cron_mode=deny 阻断后,silent_fallback 是否一致?未验证 |
| F5 cron-session-leak | #41935 open — no_agent cron 不 end_session | F9 session-state-integrity 的 #63128 prune live session 会**反过来**误杀 F5 的 zombie sessions,造成双重漏算 |
| F7 MCP-supply-chain | #45620 closed (Hermes 官方 attribution 不成立,但加 5 项 hardening PR) + #38017 open catalog install.ref pinning | F10 Docker config migration gap(#35406)→ `hermes update` 不跑 migration→ MCP config 仍旧→ hardened MCP control 不生效 |
| F9 session-state-integrity | #34351 + #34475 + #40112 + #49041 全部 merged (tier-1 已修);#62365/#63008/#63128/#63129/#63207 tier-2 仍 open | compaction fabricates user intent(**信任边界**)+ cross-session _previous_summary leakage |
| F10 (新立卡) update-handoff + Docker config migration gap | #61093 open Desktop update handoff home resolution | `#35406` Docker boot hook 不跑 `migrate_config()`,导致 5 profile × `config.yaml` 跨 release 累积 stale |

**关键判定**:family registry 累计 9 个但**联动失效**未被识别。chief 必须用 cross-cluster 视角 triage,而非单 family 内 single-fix。

## 草稿段落(append to chief-agent SOUL)

```yaml
chief_agent:
  cross_cluster_integration_v1:
    role: cluster_tiebreak_authority
    triggers:
      - 任意 P1 cluster 跨 ≥ 2 family 同 tick 触发 → 立即进入 cross-cluster 评估
      - 已知 family (F1/F5/F7/F9) 任一 fix PR 落地后 7 天内,联动 family 是否有未验证的副作用?
      - 5 profile × config.yaml 跨 release 累积 stale → F10 升级 chief 亲自 triage
    triage_protocol:
      step_1: 列出 tick 内全部 P1 cluster + family 归属
      step_2: 对每个 cluster 标 cross-family interaction arrows
        - 例:F9 #63128 (prune live session) ↔ F5 #41935 (zombie cron session) — prune 误杀 zombie 双重漏算
        - 例:F7 hardening PR 合入 → F10 Docker migration gap 让 hardening 不生效
      step_3: 评估每条 arrow 的 severity:
        - severity-A:family A fix 副作用直接加重 family B 的 bug
        - severity-B:family A fix 必须配合 family B fix 才完整
        - severity-C:独立,但需 chief 6h dedup 协调
    cross_cluster_arrows_tick35:
      - F9 #63128 ↔ F5 #41935 (severity-A) — prune live session 会误杀 zombie cron sessions,需 patch 顺序协调
      - F7 MCP hardening ↔ F10 Docker migration gap (severity-B) — hardening 不解决 stale config
      - F1 #34497 execute_code approval ↔ F5 #41935 cron session (severity-C) — cron_mode=deny 默认阻断,但 no_agent 路径未明确
    escalation:
      - 任何 severity-A arrow → chief 6h 内亲自 triage,不能下放
      - 任何 severity-B arrow → chief 24h 内组织 joint review
      - 任何 severity-C arrow → 进 daily report 但不阻塞
    family_registry_v10:
      - F10 cron-installer-handoff-state:profile-scoped home + Docker config migration gap
        - issues: #61093 (open), #35406 (closed but root cause broader), #35458/#35508/#36627 (fix PRs closed but Docker non-interactive migration 仍缺)
        - sweeper: sweeper marker attached
        - 6 invariants: HERMES_HOME single source + base-home fallback + stage2-hook migrate_config + non-interactive default + raw _config_version 检测 + opt-out env var
```

## Why this matters

- tick27 立卡 silent-fail cross-month recurrence 时,只看了 family 内的复发,未看跨 family 联动
- tick34 立卡 F9 session-state-integrity 时,把 9 family 看作独立 fix,但 family 间实际存在 5 条 cross-cluster arrows
- 没有 chief 视角的 cross-cluster 评估,family 内单点 fix 完成后**联动 bug 仍存在**,用户感知"修了 5 个 bug 还是有 bug"

## Acceptance criteria

1. chief-agent 看到 P1 cluster 时,默认产出 cross-cluster 评估 (≥ 2 family interaction map)
2. severity-A arrow 必须 6h 内亲自 triage
3. family registry 升级 v10 (加 F10 cron-installer-handoff-state)
4. 5 SOUL 配额中此条占 chief 段