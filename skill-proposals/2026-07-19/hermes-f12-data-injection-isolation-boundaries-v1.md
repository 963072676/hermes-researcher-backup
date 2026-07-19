---
name: hermes-f12-data-injection-isolation-boundaries-v1
description: F12 data-injection-isolation-deck candidate (condition 2 met) — 5 boundaries taxonomy defense. Use when: AI agent system needs isolation defense layer across user-agent / agent-tool / agent-execution / agent-agent / system-environment boundaries. Trigger: arxiv 2607.12406 isolation survey (5 boundaries taxonomy) + arxiv 2604.10134 PlanGuard (ASR 72.8%→0%) + arxiv 2607.12624 PVDetector (<1% FNR).
---

# hermes-f12-data-injection-isolation-boundaries-v1

> F12 candidate skill (tick41 立卡)
> Anti-inflation binding (tick36): F12 仍 candidate,直到 condition 1 (≥ 5 GH issue 同 root cause) met

## Family registry

| 字段 | 值 |
|---|---|
| family_id | F12 (candidate) |
| family_name | data-injection-isolation-deck |
| sweeper_marker | `sweeper:risk-data-injection-isolation` |
| lifecycle (tick41) | emerging (condition_2_met=true) |
| evidence_count | 5+ arxiv papers, 4 platforms (Claude Code / Codex / Gemini CLI / OpenClaw) |
| 立卡 tick | tick40 (candidate), tick41 (升级 condition 2 met) |

## 5 boundaries taxonomy (arxiv 2607.12406)

| boundary | failure mode | defense layer | code path |
|---|---|---|---|
| **user-agent** | direct PI / jailbreaks / persistent compromise | instruction-data decoupling (PlanGuard isolated planner) | agent prompt construction |
| **agent-tool** | tool misuse / protocol metadata risk | tool result provenance (F12 defense layer 2) | MCP tool invocation |
| **agent-execution** | unsafe code action realization | code action containment (F11 invariant 7 沿用) | execute_code path |
| **agent-agent** | prompt infection / topology cascade | cross-agent isolation (F12 defense layer 4) | delegate_task / subagent |
| **system-environment** | indirect PI / RAG poisoning / env disclosure | retrieval isolation (F12 defense layer 5) | RAG / web fetch |

## Defense layer implementations

```python
def f12_defense_layer_1_user_agent():
    """PlanGuard isolated planner pattern"""
    # Reference: arxiv 2604.10134 (ASR 72.8% → 0%)
    reference_plan = isolated_planner.generate(user_instruction)
    return reference_plan  # No external data access

def f12_defense_layer_2_agent_tool():
    """tool result provenance"""
    # Each tool result tagged with origin + trust level
    result = tool.invoke(args)
    return TaggedResult(result, origin=tool.origin, trust=tool.trust_level)

def f12_defense_layer_3_agent_execution():
    """F11 invariant 7 沿用 canonical_invocation_path"""
    # tick40 already 立卡 — 5 origin 必跑 dangerous_command_unified_classify

def f12_defense_layer_4_agent_agent():
    """cross-agent isolation via provenance"""
    # delegate_task result must include origin_session_id + origin_agent_id
    # parent session never consumes foreign async completion (F9 invariant 1)
    return CrossAgentTaggedResult(...)

def f12_defense_layer_5_system_environment():
    """RAG / retrieval isolation"""
    # Retrieved content must be tagged with retrieval_source + retrieval_timestamp
    # downstream prompt construction uses retrieval-isolated segment
    return IsolatedRetrievalContext(...)
```

## arxiv paper evidence

| arxiv | title | relevance | tick |
|---|---|---|---|
| 2607.12406 | Isolation as a First-Class Principle for LLM-Agent System Safety | 5 boundaries taxonomy | tick41 |
| 2604.10134 | PlanGuard: Defending Agents against IPI via Planning-based Consistency Verification | ASR 72.8%→0% via isolated planner | tick41 |
| 2607.12624 | PVDetector: Detecting PI Attacks via Policy-Violation Concept Analysis | <1% FNR, hidden-state alignment | tick41 |
| 2607.05120 | Agent Data Injection Attacks (ADI) | 7 entities affected | tick40 |
| 2603.24203 | TIP Trustworthy Indirect Prompting | >50% ASR undefended | tick40 (沿用) |

## F12 立卡判定 (tick36 binding)

- condition 1 (≥ 5 GH issue 同 root cause): **NOT MET** (tick41 沿用 tick40 — 仅 3 F12 candidate cluster)
- condition 2 (≥ 3 platform 同根): **MET** (Claude Code + Codex + Gemini CLI + OpenClaw per arxiv 2607.12406)
- condition 3 (修复 PR 合入但根因 broader): tick40 沿用 #60056 + #21563 + #63183

**结论**: condition 2 met → 维持 candidate 但记 `condition_2_met=true`;anti-inflation (tick36) binding — F12 仍 candidate,直到 condition 1 met (≥ 5 GH issue)。

## Cross-cluster arrows (tick40-41)

| arrow | from | to | severity | tick41 evidence |
|---|---|---|---|---|
| CCA-F12-F7 | F12 | F7 MCP supply chain | sev-B | PlanGuard isolated planner + MCP tool result provenance |
| CCA-F12-F11 | F12 | F11 execute-code-approval | sev-C | F12 defense layer 3 = F11 invariant 7 |
| CCA-CVE-F12 | CVE-2026-61459 | F12 | sev-A | mcp-server-kubernetes arg injection → F12 defense layer 2 |

## Self-downgrade v4 (tick41)

- streak 17 days zero-adoption
- rule 2 + 3 + 4 + 5 四 rule 同命中
- maintain_daily + 飞书 3 选项 A/B/C
- F12 仍 candidate,anti-inflation binding
