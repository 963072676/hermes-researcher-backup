---
name: hermes-artifact-dependency-coherence-gate-v1
description: '验证 Hermes release artifact 内 bundled source 与 release source 一致，并验证 messaging/provider dependency compatibility。Use when: Desktop/Docker/installer 使用 stale bundle、运行时缺 symbol、slotted dependency 阻止 monkey patch、platform connect 失败、zero-chunk stream。覆盖 GH #64333/#64482/PR #64420。'
version: 1.0.0
created_by: researcher
metadata:
  hermes:
    tags: [release, artifact, desktop, dependency, telegram, streaming]
---

# Hermes Artifact & Dependency Coherence Gate v1

## 目标

把“源码测试通过”升级为“发布 artifact 在目标 dependency matrix 上真实可用”。同时防两类 silent ship：

1. artifact 内 bundled source 旧于 release source；
2. dependency 升级后 instrumentation/stream contract 改变，平台启动或响应路径直接失效。

## 触发条件

- Desktop `app.asar`、Docker image、installer 内嵌 Python/JS source
- 运行时报 `cannot import name ...`，但源码树 import 成功
- dependency 使用 slots/frozen object，旧代码做 instance method replacement
- messaging adapter 全部 connect fail，但 gateway health 仍绿
- stream 返回 zero chunks/empty completion
- release tag、image、Desktop bundle 来源 commit 不清楚

## Gate A：artifact-source coherence

### 必填 manifest

```json
{
  "release_tag": "...",
  "source_commit": "...",
  "bundled_source_commit": "...",
  "dependency_lock_hash": "...",
  "scheduler_import_hash": "..."
}
```

### Checks

1. `source_commit == bundled_source_commit`
2. bundled artifact 上执行真实 import smoke
3. scheduler/cron entrypoint 在 artifact 环境跑 one-shot job
4. 缺 symbol 时 packaging fail，不允许 runtime 后才发现
5. job import error 必须产生 user-visible failure receipt

## Gate B：dependency compatibility

### Matrix

```text
component | dependency | min supported | release locked | max tested | smoke
Telegram  | PTB         | ...           | ...            | ...        | connect + poll
Provider  | SDK         | ...           | ...            | ...        | normal + zero-chunk stream
Desktop   | Electron/npm| ...           | ...            | ...        | native module + cron
```

### Patch policy

- 优先 wrapper/subclass；slotted/frozen object 禁止 instance attribute replacement。
- instrumentation 必须保留原 method contract、exceptions 与 return type。
- zero-chunk stream 使用 typed retryable error；bounded retry；exhaustion 必须可见。

## 标准流程

### Step 1：生成 artifact manifest

构建时把 source commit、lock hash、bundled import surface 写入 artifact。

### Step 2：解包后回读

从最终 `.app` / image / archive 内回读 manifest，禁止只读工作树文件。

### Step 3：artifact import smoke

至少覆盖 cron scheduler、gateway adapter、provider streaming helper。

### Step 4：dependency matrix smoke

目标 dependency 的 min/locked/max 三档跑 connect/stream。

### Step 5：失败注入

- bundled source 删除 required symbol → build 必须 fail
- slotted object 禁止 assignment → adapter 应通过 wrapper/subclass 工作
- zero chunk → retry；normal chunk → 不 retry；连续 zero chunk → visible failure

## Acceptance contract

```yaml
artifact_source_coherence:
  source_commit: required
  artifact_manifest_commit: required
  commits_equal: true
  import_smoke_on_artifact: true
  cron_one_shot_receipt: visible

dependency_compatibility:
  dependency_name: required
  tested_versions: [min, locked, max]
  connect_or_stream_smoke: true
  monkey_patch_strategy: wrapper_or_subclass
  zero_chunk_retry_bounded: true
```

## 失败判定

- source tree import pass、artifact import fail
- bundle commit 与 release commit 不同
- scheduler tick 后 job 消失但 UI 无失败 receipt
- dependency upgrade 后 platform 0 connected，而 health 仍成功
- slotted object 仍做 instance method assignment
- zero chunk 被当 success 或无限 retry

## 证据

- GH #64333 Desktop stale bundle/cron: <https://github.com/NousResearch/hermes-agent/issues/64333>
- PR #64359 compatibility candidate: <https://github.com/NousResearch/hermes-agent/pull/64359>
- GH #64482 Telegram dependency regression: <https://github.com/NousResearch/hermes-agent/issues/64482>
- PR #64506 Telegram candidate: <https://github.com/NousResearch/hermes-agent/pull/64506>
- PR #64420 zero-chunk retry: <https://github.com/NousResearch/hermes-agent/pull/64420>

## Pitfalls

- `latest` image 与 GitHub latest release 不一定同一 commit。
- 只在 checkout 跑 tests 会漏 `app.asar`/bundled source 漂移。
- back-compat import shim 可能止血，但不解决 bundle provenance。
- connect smoke 必须真走 adapter initialization；只 import class 不够。
- dependency matrix 中没有 release-locked 版本就无法复现用户 artifact。
