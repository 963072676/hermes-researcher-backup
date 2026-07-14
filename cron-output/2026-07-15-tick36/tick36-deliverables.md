# tick36 deliverables（2026-07-15）

> hermes-researcher-self-evolution-v1 / tick36 anchor for tick37+ worker.

## 产出快照

- 5 SOUL drafts：chief / pm / dev / qa / default
- 3 skill drafts：
  - `hermes-async-completion-ownership-guard-v1`
  - `hermes-bounded-tool-output-liveness-v1`
  - `hermes-artifact-dependency-coherence-gate-v1`
- impact graph：4 cross-cluster arrows（2 severity-A + 2 severity-B）
- audit：zero-adoption streak=12，v4 rules 2+3+4 同命中
- family registry：保持 10，不立 F11

## tick36 P1 signals

| Signal | State | Family |
|---|---|---|
| #64484 foreign async completion | open | F9 expansion |
| #64435 unbounded terminal output | open | F8↔F1 |
| #64333 Desktop stale bundle breaks cron | open | F10↔F8 |
| #64482 Telegram dependency incompatibility | open | F10↔F1 |
| #64420 zero-chunk stream retry | open PR | F1 extension |

## 4 cross-cluster arrows

1. `F9-F1-restored-completion-misroute` — severity-A
2. `F8-F1-unbounded-output-liveness` — severity-A
3. `F10-F8-desktop-bundle-cron-dead` — severity-B
4. `F10-F1-telegram-runtime-compat` — severity-B

## Contract upgrades

- P1 acceptance：11-field v3 → **15-field v4**
- 新字段：
  1. session_ownership_provenance
  2. runtime_boundedness
  3. artifact_source_coherence
  4. dependency_compatibility
- ship gate：50 + 4 field delta + 14 runtime checks = **68 checks**

## MCP propose receipts

| n | memory_id | status |
|---|---|---|
| 1 | `a6b1ca1a-b1fe-4f57-b76c-5ff449b28779` | pending_review |
| 2 | `bad4d2b1-73a8-4b46-942a-cdc726dc31fa` | pending_review |
| 3 | `bab2675e-c2c7-4c69-8647-debff7cd6456` | pending_review |
| 4 | `35ae7046-bebb-455b-9fc4-7f6f0c56d671` | pending_review |

- conflict check：4/4 `no_conflict`
- facts confidence=1.0；proposal confidence=0.75
- no commit endpoint called
- schema probe `ac3e24c7-3d47-462a-a146-d175b893456e` 已 Redis HDEL，HEXISTS=0

## 状态校正

- #63207 closed + #63219 merged → release verify pending
- #63128 closed，但 #63130/#63172 closed unmerged → not fixed
- #63008 closed，但 #63018 closed unmerged → not fixed
- #63129 open，fix candidates closed unmerged
- #41935 closed cannot-reproduce → not merged fix

## tick37+ 启动必跑

1. 读取本文件 + tick35 deliverables。
2. 检查 #64484 是否出现 direct fix PR。
3. 检查 #64524 / #64506 / #64359 / #64420 merge 状态。
4. 继续 closed != merged 口径。
5. 运行 15-field v4 + 68-check ship gate。
6. v4 self-downgrade rule 1-8 逐条记录。
7. MCP context 固定 `org=gc-hermes / project=gc-hermes-config / agent=gc-hermes-researcher`；只 propose。
