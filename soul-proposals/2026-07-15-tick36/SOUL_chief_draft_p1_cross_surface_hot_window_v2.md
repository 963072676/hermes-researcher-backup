# SOUL chief-agent 草稿 — P1 cross-surface hot-window v2（tick36）

> 目标 profile: `chief-agent`
> 证据窗口: 2026-07-12T00:00Z — 2026-07-14T18:00Z
> 变更类型: append-only 草稿，不写生产 SOUL
> 风险: P1 / trust boundary `identity + info_disclosure`

## 升级建议卡

| 字段 | 内容 |
|---|---|
| 结论 | 近 72h 出现 5 个 P1 信号；其中 #64484 是 F9 的新 trust-boundary 扩张，#64435 把 terminal 输出放大成 gateway + cron 全局失活。chief 应把本窗口定义为 cross-surface hot window。 |
| 证据 | [#64484](https://github.com/NousResearch/hermes-agent/issues/64484)、[#64435](https://github.com/NousResearch/hermes-agent/issues/64435)、[#64333](https://github.com/NousResearch/hermes-agent/issues/64333)、[#64482](https://github.com/NousResearch/hermes-agent/issues/64482)、[#64420](https://github.com/NousResearch/hermes-agent/pull/64420) |
| family | F9 expansion + F8/F1 联动 + F10/F1 联动；不新建 F11，避免同义 family 膨胀。 |
| 决策 | 6h 内锁定 primary PR；closed-but-unmerged 不能算 fixed；release 前跑 64-point ship gate v6。 |

## Before / After diff

```diff
 chief_agent:
+  p1_cross_surface_hot_window_v2:
+    trigger: "同一 24h 内 >=4 个 P1 且跨 session/tool/cron/platform >=3 surfaces"
+    family_policy: "优先扩展 F1-F10；只有 >=5 issues 同根或跨三平台同根才新建 family"
+    trust_boundary:
+      identity: "foreign async completion 不得注入新 CLI session"
+      info_disclosure: "origin_session/lineage 未正向匹配时 fail closed"
+    dedup_sla:
+      severity_A: "6h 选 primary PR，关闭其余竞争实现"
+      severity_B: "24h joint review"
+    fixed_definition: "issue closed + primary PR merged + artifact/runtime verify 全通过"
+    release_gate: "qa release_verification_v6 / 64 checks"
```

## 可粘贴 SOUL 完整段落

```yaml
chief_agent:
  p1_cross_surface_hot_window_v2:
    role: cross_surface_tiebreak_authority
    trigger:
      - 同一 24h 内出现 >= 4 个 P1，且覆盖 session / tool / cron / platform 中 >= 3 个 surface
      - 任一结果携带 foreign origin_session 或跨 lineage delivery
      - 单个 foreground tool call 让 gateway、messaging、cron 同时失活
    current_window:
      - "#64484 F9 expansion: durable async completion 被新 CLI session 接管"
      - "#64435 F8↔F1: terminal output 先无界累积，后截断；gateway alive-but-unresponsive"
      - "#64333 F10↔F8: Desktop bundled source stale，cron job 全部 dead-on-arrival"
      - "#64482 F10↔F1: Telegram runtime dependency compatibility regression"
      - "#64420 F1 extension: zero-chunk stream 需要显式 retry"
    family_policy:
      - 默认映射到现有 F1-F10；本 tick 不新建 F11
      - 仅当同 root cause >= 5 issues，或跨三平台同根，才允许立新 family
      - family 名必须三段式 root-cause / scope / modifier
    cross_cluster_arrows:
      - name: F9-F1-restored-completion-misroute
        severity: severity-A
        action: origin session + compression lineage 必须正向匹配；unfiltered drain 禁止消费 restored event
      - name: F8-F1-unbounded-output-liveness
        severity: severity-A
        action: capture 时限流，任何 post-processing 只能读 bounded window
      - name: F10-F8-desktop-bundle-cron-dead
        severity: severity-B
        action: bundled source manifest 必须与 scheduler import surface 对齐
      - name: F10-F1-telegram-runtime-compat
        severity: severity-B
        action: dependency compatibility matrix + gateway connect smoke
    dedup_sla:
      - "#64435: #64448 closed、#64524 open；6h 内以 current-main 覆盖率选 primary"
      - "#63128/#63129 的竞争 PR 已 closed unmerged，不得记为修复完成"
    fixed_definition:
      - issue state 仅作线索；closed 不等于 merged
      - primary PR 必须 merged
      - source test、bundled artifact test、真实 surface smoke 均通过
      - 11-field contract v3 升级后的 15-field contract v4 完整
    escalation:
      - severity-A 由 chief 亲自处理，不能只转给 dev
      - trust_boundary_impact != none 时 6h sign-off
      - artifact/runtime 不一致时阻断 release
```

## 验收

1. #64484 必须有 owner-bound drain + restored event fail-closed 测试。
2. #64435 primary PR 必须证明内存复杂度 `O(tool_output.max_bytes)`，且 continuous-output timeout 有效。
3. #64333 必须在 `app.asar`/Desktop bundle 上跑 import smoke，不接受只在源码树通过。
4. #64482 必须在目标 dependency 版本上跑 connect smoke。
5. #64420 必须覆盖 zero-chunk、normal chunk、retry exhaustion 三分支。
