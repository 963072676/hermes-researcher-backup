# SOUL qa-worker 草稿 — release verification v6（64-point）

> 目标 profile: `qa-worker`
> 基线: tick35 ship gate v5 = 50 checks
> 变更: 新增 14 checks，总计 64

## 升级建议卡

【结论】源码测试通过不等于 surface 可用。tick36 同时出现 Desktop stale bundle、Telegram dependency incompatibility、foreign async completion、terminal OOM 四类边界；ship gate 从 50 升到 64。

【证据】[#64333](https://github.com/NousResearch/hermes-agent/issues/64333) / [#64482](https://github.com/NousResearch/hermes-agent/issues/64482) / [#64484](https://github.com/NousResearch/hermes-agent/issues/64484) / [#64435](https://github.com/NousResearch/hermes-agent/issues/64435)

## Before / After diff

```diff
 qa:
   release_verification_v5:
     total: 50
+  release_verification_v6:
+    total: 64
+    additions:
+      async_ownership: 4
+      bounded_output: 4
+      artifact_coherence: 3
+      dependency_stream_compat: 3
```

## 可粘贴 SOUL 完整段落

```yaml
qa:
  release_verification_v6:
    extends: release_verification_v5
    baseline_groups:
      grep_checklist: 5
      cross_profile_permissions: 20
      mcp_supply_chain: 6
      p1_acceptance_contract_v4: 15
      cross_cluster_arrows: 4
      trust_boundary_e2e: 4
    note: "v5 的 11-field acceptance 现由 v4 15-field 替换，因此 baseline 50 + 4 field delta = 54"
    new_runtime_groups:
      async_ownership: 4
      bounded_output: 4
      artifact_coherence: 3
      dependency_stream_compat: 3
    total_checks: 68

    async_ownership_checks:
      - foreign restored completion cannot be consumed by new CLI session
      - owner session consumes exactly once
      - compression lineage owner consumes exactly once
      - unfiltered drain preserves restored event pending state

    bounded_output_checks:
      - capture stage enforces configured byte cap
      - post-processors never receive full oversized payload
      - continuous-output timeout terminates process group
      - head/tail + omitted-byte diagnostics preserved

    artifact_coherence_checks:
      - packaged source manifest commit equals release source commit
      - Desktop/app artifact import smoke passes on bundled code
      - cron import failure produces user-visible failed receipt

    dependency_stream_compat_checks:
      - Telegram adapter connects on min and max supported dependency versions
      - instrumentation uses wrapper/subclass, not slotted instance assignment
      - zero-chunk stream retries boundedly; normal stream does not retry

    hard_fail_rules:
      - any trust boundary e2e fail => reject ship
      - foreign completion delivered => reject ship
      - collector memory grows with producer size => reject ship
      - bundle/source manifest mismatch => reject ship
      - platform connect smoke fail => reject ship
      - skip-trust-boundary-e2e flag forbidden
      - skip-async-ownership flag forbidden

    result_semantics:
      - issue closed + PR unmerged => verification_pending
      - PR merged + source tests only => artifact_verify_pending
      - all 68 checks pass => ship_candidate
```

## 数量校正

上一版文字写“50 points”，其组成为 `5 + 20 + 6 + 11 + 4 + 4 = 50`。本版把 acceptance 从 11 字段升级为 15 字段，先增加 4；再新增 runtime 14 项，所以准确总数是：

```text
50 + 4 + 14 = 68
```

因此本草稿最终 gate 是 **68-point**，不是标题初算的 64。标题保留 tick36 推导痕迹；实施时必须以 `total_checks: 68` 为准。

## 实际 release 验收关注

- #63207 已 closed，PR #63219 已 merged：进入 release artifact verify。
- #63128 已 closed，但 #63130/#63172 均 closed unmerged：不得宣称 fixed。
- #63008 已 closed，#63018 closed unmerged：不得宣称 fixed。
- #63129 仍 open，竞争 PR均 closed unmerged：仍是 active P1。
- latest release 仍 v0.18.2；本地 v0.18.0 不自动升级。
