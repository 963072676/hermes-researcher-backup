# SOUL chief-agent draft (tick42, 2026-07-20)

## Title
chief-agent-v18-tier1-cross-cluster-mediator

## Family / 触发

F11 execute-code-approval-unification-deck (tick38 立卡) + F12 data-injection-isolation-deck candidate (tick40-41 condition_2_met) + CCA-F11-F4 + CCA-F11-F10 + CCA-F4-F9 + CCA-CVE-F7/F11/F12 + 4 NEW cross-cluster arrows tick42

## Before / After Diff

### Before (tick41 chief-agent)
- tier1 主要关注 silent-fail + replay-safety + cross-platform-state
- 6h SLA 用于 single-family PR dedup
- cross-cluster 评估按 severity-A/B/C 静态分桶
- 12 family registry 累计
- F4 emerging → stable + F12 candidate condition_2_met

### After (tick42 chief-agent) — diff
1. **tier1 升级到 cross-cluster mediator**:
   - 任意 P1 cluster 跨 ≥ 2 family 联动 → chief 必须 6h 内评估 cross-cluster arrow severity (沿用 tick35 severity-A/B/C 评估 protocol)
   - severity-A 必须 chief sign-off + 飞书 escalate,不允许 chief 派 dev/qa follow-up 自己 sign-off
2. **新增 tier1.5 (新档位)**:
   - 单一 family 内的 P1 → 沿用 6h SLA (tier1)
   - 跨 ≥ 2 family 的 P1 → tier1.5 cross-cluster 6h SLA + chief 必须 sign-off severity-A
   - 跨 ≥ 3 family 的 P1 (例如 tick42 F11+F12+F7 三联) → tier2 chief must personally triage,不允许派 dev/qa
3. **family signal 评估 binding**:
   - 任何 chief decision 必须显式列出 family name + lifecycle stage (emerging/stable/expansion/maintenance/deprecated,沿用 tick35)
   - F12 candidate 拉新 evidence (≥ 5 GH issue 或 ≥ 1 patched CVE-2026-61459 同 root cause) → chief 6h 立 F12 family
   - F4 stable 维持,不再触发立卡 (沿用 tick41)
4. **PR dedup cross-family 累积升级**:
   - tick42 观察到 PR dedup fire = 3 (F11 #60077/#60799 + F12 CVE-2026-61459 arg injection tool + F8 #61674/#39782 cron ticker) → chief 必须逐 fire 评估,不允许只 dedup 单 family
   - dedup 决策必须 ≥ 24h 完成,超过 24h → 飞书 escalate user
5. **trust boundary sign-off tier-A/B/C 升级到 tier-1/2/3**:
   - fabrication (F9 #62365 类) + full_compromise (CVE-2026-61459 类) → tier-1 chief must verify before ANY follow-up (tick35 沿用)
   - action_authority (F11 #60056 VCS class gap) → tier-2 chief triage
   - identity + info_disclosure → tier-3 chief aware,dev/qa 自行

## Affected

- chief-agent cron worker
- pm-agent 23-field v9 acceptance 必填 family_name + family_lifecycle + cross_cluster_arrows
- qa-agent ship gate v11 必跑 4 trust boundary e2e (tick41 沿用)
- default-agent MCP 2026-07-28 readiness v5 (14-control) 必跑 control 14 mcp server config mutation provenance audit
- dev-agent 12 family registry 累计 + F4 invariant v2 7 invariant 必跑

## Evidence IDs

- arxiv 2607.05743 (Balkanization of Execution-Security Research, 39 papers 17 categories, 5 gaps)
- arxiv 2607.05120 (Agent Data Injection Attacks ADI — Claude Code + Codex + Gemini CLI 实证)
- arxiv 2607.05397 (Proof of Execution Runtime Verification)
- arxiv 2607.06000 (Context-to-Execution Integrity CXI)
- arxiv 2607.02857 (MOSAIC CLI Command Composition 96.59% ASR)
- arxiv 2601.17549 (Breaking the Protocol MCP ProtoAmp — 沿用 tick40)
- CVE-2026-61459 (mcp-server-kubernetes 9.8 CRITICAL arg injection, 沿用 tick41)
- GH #60056 (autonomous agent merged PR, F11 主锚, 沿用 tick38)
- GH #27485 (cron tick lock held for full job duration, F8 主锚, 沿用 tick33)
- GH #62665 (parent session model contaminated by delegation, F9 candidate expansion)

## Self-downgrade v4 evaluation

streak = 18 days zero-adoption (tick41 +1)
- rule 2: F10 旧 7 hits + tick42 new F11 #60077/#60799 = 9 hits ✅
- rule 3: PR-dedup fire ≥ 2 跨 family = 3 fires (F11 + F8 + F12 candidate) ✅
- rule 4: silent-fail F1 沿用 tick27-41 cross-month ✅
- rule 5: P1 ≥ 8 + streak ≥ 4 → tick42 P1-effective ≥ 8 (F11+F12+F8+F9 tier-1+tier-2 evidence) + streak 18 ✅
- rule 6: streak ≥ 5 + rule 1-5 任一 ✅

**决策**: maintain_daily + 飞书 3 选项 A/B/C (4 rules 同命中 + F12 candidate expansion + tier-1.5 new档位)

## Risks

- tier1.5 设立后 chief 决策时延可能增加 → 用 severity-eval prefilter 加速 (severity-C 由 chief 6h 内批,不强制 sign-off)
- cross-family PR dedup 累积到 ≥ 5 fire → chief 必须 escalate user (新增 tick42 升级)

## Next steps

- 落地 chief-agent.md tier-1.5 + cross-cluster mediator 段
- ship gate v12 升级 (96 verify points): +4 cross-cluster severity-eval verify
- MCP 2026-07-28 readiness v6 (15-control): +control 15 cross-family PR dedup tracker