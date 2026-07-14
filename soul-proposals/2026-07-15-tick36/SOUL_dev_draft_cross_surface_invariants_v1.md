# SOUL dev-worker 草稿 — cross-surface implementation invariants v1

> 目标 profile: `dev-worker`
> 证据: GH #64484 / #64435 / #64333 / #64482 / PR #64420
> 变更类型: append-only 草稿

## 升级建议卡

| 优先级 | 实现目标 | 当前证据 |
|---|---|---|
| P1-A | restored async completion 只允许 owner session/lineage 消费 | [#64484](https://github.com/NousResearch/hermes-agent/issues/64484) |
| P1-A | terminal 输出在 capture 阶段限流，不能先聚合后截断 | [#64435](https://github.com/NousResearch/hermes-agent/issues/64435) |
| P1-B | Desktop bundle 与源码 import surface 一致 | [#64333](https://github.com/NousResearch/hermes-agent/issues/64333) |
| P1-B | Telegram polling instrumentation 不做 instance monkey patch | [#64482](https://github.com/NousResearch/hermes-agent/issues/64482) |
| P1-C | zero-chunk stream 进入 bounded retry | [#64420](https://github.com/NousResearch/hermes-agent/pull/64420) |

## Before / After diff

```diff
 dev_worker:
+  cross_surface_implementation_invariants_v1:
+    async_completion: positive ownership + lineage match
+    terminal_output: bound while draining, not after join
+    packaged_runtime: manifest/import smoke on artifact
+    dependency_patch: wrapper/subclass only; instance patch forbidden on slotted objects
+    zero_chunk_stream: typed retry with bounded attempts
```

## 可粘贴 SOUL 完整段落

```yaml
dev_worker:
  cross_surface_implementation_invariants_v1:
    async_delegation_ownership:
      root_issue: 64484
      invariants:
        - restored event 必须携带 origin_session 与 origin_lineage
        - consumer 必须正向证明 session 或 compression lineage ownership
        - unfiltered drain 不得消费 restored event
        - keyless legacy event 只允许 same-process、non-restored 路径
        - /new、/clear、process exit 后的 pending completion 保留给 owner resume，不注入新 session
      tests:
        - foreign restored event + unfiltered drain => not consumed
        - owner restored event + lineage-aware drain => consumed exactly once
        - new CLI boot idle drain => zero foreign turns
        - same-process keyless legacy event => behavior unchanged

    bounded_terminal_output:
      root_issue: 64435
      invariants:
        - BaseEnvironment drain 时使用 bounded collector
        - collector 保留 head + tail + omitted byte count
        - join full output 禁止出现在正常与 timeout 分支
        - sudo detector、scrub、ANSI strip、plugin hook 只接收 bounded payload
        - continuous producer 下 timeout 仍按 wall clock 生效
      tests:
        - 100MiB producer => returned payload <= configured cap
        - RSS growth 与 output size 解耦，复杂度 O(cap)
        - head/tail sentinel retained
        - timeout kills process group under continuous output

    artifact_source_coherence:
      root_issue: 64333
      invariants:
        - Desktop bundle 生成 manifest: source_commit + scheduler_import_hash
        - scheduler import smoke 必须对 app.asar/bundled source 执行
        - bundled symbol 缺失时 packaging fail，不允许 runtime quiet failure
        - cron job import error 必须回写 UI receipt，不得删除 job 后只留 errors.log
      tests:
        - build_keepalive_http_client symbol present in packaged runtime
        - source and bundle manifest commit equal
        - one-shot cron artifact smoke produces visible receipt

    dependency_compatibility:
      roots: [64482, 64420]
      invariants:
        - slotted/frozen dependency object 禁止 instance method replacement
        - instrumentation 使用 wrapper 或 subclass，并保持原 method contract
        - dependency min/max versions 进入 CI matrix
        - stream zero chunks 被分类为 retryable typed error
        - retry 次数有上限，正常 streaming 无行为变化
      tests:
        - Telegram target dependency connect smoke
        - do_request instrumentation preserves request semantics
        - zero chunks => retry
        - valid chunks => no retry
        - exhausted retries => visible terminal/delivery error

    implementation_order:
      - 1: async_delegation_ownership
      - 2: bounded_terminal_output
      - 3: artifact_source_coherence
      - 4: dependency_compatibility
    merge_policy:
      - 每个 root cause 只保留一个 primary PR
      - closed-but-unmerged implementation 只能当 design evidence
      - 不在同 PR 混入 unrelated refactor
```

## Primary PR 建议

- #64435: 在 #64448（closed）与 #64524（open）中选择 current-main 覆盖更完整者；当前优先 review #64524。
- #64484: 尚无直接 PR，不要用 TUI-only #63317 或 `/new` interrupt #63856 代替 CLI durable restore fix。
- #64333: #64359 只补 backward import compatibility；仍必须补 bundle manifest + artifact smoke。
- #64482: #64506 是当前 primary candidate。
- #64420: 独立 small fix，可并行，但 release gate 必须覆盖 retry exhaustion。
