# 跨 Profile 影响图 — 2026-07-15（tick36）

## 结论

本 tick 新增/更新 **5 个 P1 信号**，覆盖 session ownership、terminal liveness、Desktop cron artifact、Telegram dependency compatibility、stream empty-response。归类结果：

- **不立 F11**：全部可映射到现有 F1/F8/F9/F10。
- family registry 保持 **10 family**。
- 新增 4 条 cross-cluster arrows，其中 2 条 severity-A、2 条 severity-B。
- trust-boundary 影响：`identity + info_disclosure`。

## P1 证据表

| Evidence | State at 2026-07-14 18:00Z | Family | Fix candidate |
|---|---|---|---|
| [#64484](https://github.com/NousResearch/hermes-agent/issues/64484) foreign async completion 注入新 CLI session | open P1 | F9 expansion | 暂无直接 PR；#63317 TUI-only、#63856 in-flight-only，不足以替代 |
| [#64435](https://github.com/NousResearch/hermes-agent/issues/64435) terminal unbounded capture 让 gateway/cron freeze | open P1 | F8↔F1 | #64524 open；#64448 closed unmerged |
| [#64333](https://github.com/NousResearch/hermes-agent/issues/64333) Desktop stale bundle 使所有 cron dead-on-arrival | open P1 | F10↔F8 | #64359 open，但仍需 artifact manifest/smoke |
| [#64482](https://github.com/NousResearch/hermes-agent/issues/64482) Telegram dependency regression 0 connected | open P1 | F10↔F1 | #64506 open |
| [#64420](https://github.com/NousResearch/hermes-agent/pull/64420) zero-chunk stream bounded retry | open P1 PR | F1 extension | #64420 open |

## Cross-cluster arrows

### severity-A — chief 6h triage

```text
F9-F1-restored-completion-misroute
  from: F9 session-state-integrity (#64484)
  to:   F1 message-delivery/silent-fail
  interaction: durable restore + unfiltered CLI drain 让 foreign completion 进入错误 session
  trust_boundary_impact: identity + info_disclosure
  required_fix: positive ownership + compression lineage + restored fail-closed
```

```text
F8-F1-unbounded-output-liveness
  from: F8 cron-ticker-resilience / gateway liveness (#64435)
  to:   F1 message delivery
  interaction: foreground output 先无界累积后截断，gateway alive-but-unresponsive，Telegram/Discord/cron 一起停
  trust_boundary_impact: info_disclosure（full payload 被多个 post-processor 复制）
  required_fix: capture-stage bounded collector + continuous-output timeout
```

### severity-B — chief 24h joint review

```text
F10-F8-desktop-bundle-cron-dead
  from: F10 installer/update handoff (#64333)
  to:   F8 cron liveness
  interaction: Desktop bundled code stale，scheduler import surface 与 source tree 不一致
  required_fix: artifact manifest + bundled import smoke + visible failure receipt
```

```text
F10-F1-telegram-runtime-compat
  from: F10 artifact/dependency coherence (#64482)
  to:   F1 message delivery
  interaction: runtime dependency 变更使 instance method instrumentation 失败，gateway health 仍可绿但 Telegram 0 connected
  required_fix: wrapper/subclass + dependency matrix connect smoke
```

## 状态变化（tick35 → tick36）

| Item | tick35 | tick36 verified |
|---|---|---|
| #63207 / #63219 | issue open / PR open | issue closed；PR merged 2026-07-14T11:28Z → release verify pending |
| #63128 | open | closed，但 #63130/#63172 closed unmerged → 不能宣称 fixed |
| #63008 | open | closed，但 #63018 closed unmerged → 不能宣称 fixed |
| #63129 | open | 仍 open；#63132/#63174 closed unmerged |
| #41935 | open | closed cannot-reproduce；不当作 merged fix |
| #61093 | open | 仍 open（实际是 PR URL） |

## 5 profile 依赖链

```text
External evidence
  ├─ #64484 ownership breach
  ├─ #64435 liveness/OOM
  ├─ #64333 artifact drift
  ├─ #64482 dependency compatibility
  └─ #64420 zero-chunk stream
        ↓
chief-agent
  - cross-surface hot-window 判级
  - severity-A 6h tiebreak
  - closed != merged 统一口径
        ↓
pm-orchestrator
  - acceptance v3 11-field → v4 15-field
  - 新增 ownership / boundedness / artifact coherence / dependency compatibility
        ↓
dev-worker
  - 4 组实现不变量
  - 每 root cause 只留 primary PR
        ↓
qa-worker
  - release verification v6
  - 50 + 4 contract delta + 14 runtime checks = 68 checks
        ↓
default
  - verbose output 落盘分页
  - foreign async completion fail closed
  - 禁 unattended update
  - MCP beta branch-only exact pin
```

## Skill 映射

| Skill draft | Covers |
|---|---|
| `hermes-async-completion-ownership-guard-v1` | #64484 / #63494 / #63317 / #63856 |
| `hermes-bounded-tool-output-liveness-v1` | #64435 / #64524 / #56059 |
| `hermes-artifact-dependency-coherence-gate-v1` | #64333 / #64359 / #64482 / #64506 / #64420 |

## 11-field v3 → 15-field v4

新增：

1. `session_ownership_provenance`
2. `runtime_boundedness`
3. `artifact_source_coherence`
4. `dependency_compatibility`

这 4 字段同时进入 QA gate，因此 v5 50 points 变为：

```text
50 + 4 acceptance-field delta + 14 runtime checks = 68
```

## MCP 2026-07-28 readiness（旧 anchor，距 final 13 天）

官方 RC 与 beta SDK 仍强调：stateless core、`server/discover`、legacy `initialize` fallback、authorization issuer binding、header/body consistency、cache scope。影响链：

```text
MCP official RC
  → default: branch-only exact pin
  → dev: dual-protocol compatibility
  → qa: old/new handshake + issuer binding smoke
  → chief: 未过 matrix 不切生产
```

来源：

- <https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/>
- <https://blog.modelcontextprotocol.io/posts/sdk-betas-2026-07-28/>
- <https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices>

## arXiv/社区加证（不单独升 P1）

- [arXiv:2607.11390](https://arxiv.org/abs/2607.11390): tool-grounded IaC repair，AWS benchmark scanner-verified fix rate从 26.6%→78.4%（Checkov）、44.8%→72.4%（Trivy）；缺上下文时 escalation 优于 fabrication。映射 trust-boundary `fabrication`。
- [arXiv:2607.11126](https://arxiv.org/abs/2607.11126): provider-side tool memory 在 8 services / 2 MCP benchmarks 上提升 pass@1 最多 21.61%。只作为 memory architecture 方向，不改生产。
- [arXiv:2607.11226](https://arxiv.org/abs/2607.11226): N=20 sandbox，runtime Validator 阻止全部 executed breaches，constraint memory 降 token 15.1%，CAS 降 55.9%；样本小，方向性证据。
- [HN MCP runtime sandbox](https://news.ycombinator.com/item?id=48838368): 70 servers startup/idle trace，67 clean、3 启动外连、1 `/etc/passwd` 为 benign libc lookup；强调 static scan 之外的 runtime diff，但非正式研究。
- Grok CLI home-upload HN 条目只有 X 二手链接、无法独立核验，本 tick不升级、不写 MCP。

## MCP receipt map

| Cluster | memory_id | status |
|---|---|---|
| async ownership | `a6b1ca1a-b1fe-4f57-b76c-5ff449b28779` | pending_review |
| bounded output liveness | `bad4d2b1-73a8-4b46-942a-cdc726dc31fa` | pending_review |
| artifact/dependency coherence | `bab2675e-c2c7-4c69-8647-debff7cd6456` | pending_review |
| 15-field/68-check proposal | `35ae7046-bebb-455b-9fc4-7f6f0c56d671` | pending_review |

Schema probe `ac3e24c7-3d47-462a-a146-d175b893456e` 已从 Redis hash 清理，`HEXISTS=0`。

## Watch signals

1. CLI boot 后 5s 内 foreign completion count > 0 → P1 alert。
2. foreground terminal RSS delta > `4 × max_bytes` → fail。
3. artifact manifest source commit != bundled commit → ship block。
4. messaging platform configured > 0 且 connected = 0 → gateway health fail。
5. zero-chunk stream retries > configured bound → visible error。
6. issue closed but linked primary PR mergedAt=null → state=`verification_pending`。
