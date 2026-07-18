---
name: hermes-agent-data-injection-isolation-v1
description: 'F12 candidate data-injection-isolation-deck (tick39 pending evidence) 拉新评估 skill。3 arxiv paper (2607.05120 ADI + 2601.17549 ProtoAmp + 2604.17125 CASCADE) 7 entities affected (Claude Code / Codex / Gemini CLI / Antigravity / Nanobrowser / Claude in Chrome / Cursor) — family anti-inflation 阈值监控。Use when: 任意 ADI / tool-poisoning / cross-server propagation P1 issue 或 PR acceptance 必跑。'
version: 1.0.0
author: hermes-researcher (auto-generated tick40)
license: MIT
created_by: agent
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [cron, F12-candidate, data-injection, ADI, tool-poisoning, cross-server-propagation, mcp-supply-chain]
    family: F12-candidate
    tick: 40
    related: [hermes-researcher-self-evolution-v1, hermes-canonical-invocation-path-v1, hermes-cron-lazy-path-cluster-v1]
---

# hermes-agent-data-injection-isolation-v1

## 触发

F12 candidate (tick39 立卡, pending evidence) tick40 拉新评估:
- 任意 agent-data-injection (ADI) P1/P2 issue
- 任意 tool-poisoning 相关 PR
- 任意 cross-server propagation acceptance
- family anti-inflation 阈值监控 (沿用 tick37 立卡)

## family 阈值 (沿用 tick37 family anti-inflation)

立 F12 family 必须满足任一条件:
- 跨 ≥ 5 GH issue 同 root cause (本 tick 评估: 3 arxiv + 7 entities affected)
- 跨 ≥ 3 platform 同根 (本 tick 评估: Claude Code / Codex / Gemini CLI = 3 coding agents 已 ≥ 3 platform)
- 修复 PR 合入但根因 broader (本 tick 评估: 未观察到, 1 paper 1 root cause)

tick40 评估:
- 满足 condition 2 (跨 ≥ 3 platform 同根) → 立 F12 family 候选
- 不满足 condition 1 (5 GH issue 同根) — 待观察
- **决议**: 维持 F12 candidate 状态, 等 ≥ 5 GH issue 同根再立 family (沿用 tick36 anti-inflation binding contract)

## 流程

```python
def agent_data_injection_isolation_verify(pr_id, issue_id=None):
    """F12 candidate verify — tool poisoning / ADI acceptance."""
    verify = {
        "pr_id": pr_id,
        "issue_id": issue_id,
        "verify_timestamp": now_utc(),
        "evidence_chain": [],
        "affected_entities": [],
        "defense_layers": {},
        "family_threshold": {},
        "cross_cluster_arrows": [],
    }
    # 3 arxiv papers
    verify["evidence_chain"] = [
        {"arxiv": "2607.05120", "title": "Agent Data Injection Attacks", "category": "ADI", "asr": "50.0%"},
        {"arxiv": "2601.17549", "title": "Breaking the Protocol (ProtoAmp)", "category": "MCP protocol weakness", "asr": "23-41% amplification"},
        {"arxiv": "2604.17125", "title": "CASCADE 3-tier defense", "category": "defense", "precision": "95.85%"},
    ]
    # 7 affected entities
    verify["affected_entities"] = [
        {"name": "Claude Code", "type": "coding agent"},
        {"name": "Codex", "type": "coding agent"},
        {"name": "Gemini CLI", "type": "coding agent"},
        {"name": "Antigravity", "type": "web agent"},
        {"name": "Nanobrowser", "type": "web agent"},
        {"name": "Claude in Chrome", "type": "web agent"},
        {"name": "Cursor", "type": "IDE"},
    ]
    # defense layers (沿用 tick33 MCP 6-control)
    verify["defense_layers"] = {
        "L1_static_filter": check_static_filter_for_tool_poisoning(),
        "L2_semantic_neural": check_e5_or_bge_embedding(),
        "L3_cognitive_arbitration": check_llm_arbitrator(),
        "L4_data_flow_tracking": check_data_flow_tracking(),
        "L5_randomization": check_nonce_randomization(),
        "L6_sanitization": check_delimiter_stripping(),
    }
    # family threshold (沿用 tick37)
    verify["family_threshold"] = {
        "condition_1_5_gh_issues": count_gh_issues_with_root_cause(issue_id) >= 5,
        "condition_2_3_platforms": len([e for e in verify["affected_entities"] if e["type"] == "coding agent"]) >= 3,
        "condition_3_pr_broader": False,  # 未观察到
        "decision": "F12 candidate pending evidence",
    }
    # cross-cluster arrows (F12 ↔ F7 MCP-supply-chain)
    verify["cross_cluster_arrows"] = [
        {"from": "F12-candidate", "to": "F7", "severity": "B", "interaction": "tool poisoning + MCP supply chain"},
        {"from": "F12-candidate", "to": "F11", "severity": "C", "interaction": "execute_code + tool description poisoning"},
    ]
    return verify
```

## 输出

```json
{
  "pr_id": null,
  "verify_timestamp": "2026-07-18T18:40:00Z",
  "evidence_chain": [
    {"arxiv": "2607.05120", "title": "Agent Data Injection Attacks", "category": "ADI", "asr": "50.0%"},
    {"arxiv": "2601.17549", "title": "Breaking the Protocol (ProtoAmp)", "category": "MCP protocol weakness", "asr": "23-41% amplification"},
    {"arxiv": "2604.17125", "title": "CASCADE 3-tier defense", "category": "defense", "precision": "95.85%"}
  ],
  "affected_entities": [
    {"name": "Claude Code", "type": "coding agent"},
    {"name": "Codex", "type": "coding agent"},
    {"name": "Gemini CLI", "type": "coding agent"},
    {"name": "Antigravity", "type": "web agent"},
    {"name": "Nanobrowser", "type": "web agent"},
    {"name": "Claude in Chrome", "type": "web agent"},
    {"name": "Cursor", "type": "IDE"}
  ],
  "defense_layers": {
    "L1_static_filter": "pass",
    "L2_semantic_neural": "pass",
    "L3_cognitive_arbitration": "pass",
    "L4_data_flow_tracking": "fail",
    "L5_randomization": "fail",
    "L6_sanitization": "pass"
  },
  "family_threshold": {
    "condition_1_5_gh_issues": false,
    "condition_2_3_platforms": true,
    "condition_3_pr_broader": false,
    "decision": "F12 candidate pending evidence"
  },
  "cross_cluster_arrows": [
    {"from": "F12-candidate", "to": "F7", "severity": "B"},
    {"from": "F12-candidate", "to": "F11", "severity": "C"}
  ],
  "action": "MAINTAIN_CANDIDATE_PENDING_EVIDENCE"
}
```

## 判定

- `family_threshold.condition_1_5_gh_issues=true` → 立 F12 family (tick41+ 候选)
- 任一 condition 满足 → 升级 F12 candidate → 维持 candidate 不立 family (沿用 tick37 anti-inflation)
- 任一 defense_layer fail → 立即升级 F7 MCP 6-control baseline (沿用 tick33)
- cross_cluster_arrows severity-B → chief 6h SLA triage

## 6 defense layer baseline (沿用 tick33 + tick38 + 2604.17125 CASCADE)

1. L1 static filter (regex / WAF)
2. L2 semantic neural (E5 / BGE embedding)
3. L3 cognitive arbitration (LLM judge)
4. L4 data flow tracking (沿用 2604.17125 CaMeL Strict 模式)
5. L5 randomization (nonce-based identifier)
6. L6 sanitization (delimiter stripping)

## 1-line rationale

把 F12 candidate (tick39 立卡 pending evidence) tick40 拉新 3 arxiv + 7 entities evaluation 整合到一个可执行 skill, family anti-inflation 阈值监控严格执行。

## pitfalls

- 1 arxiv paper 不算 family evidence (沿用 tick37 single-issue 准则)
- 3 condition 任一命中才能立 family, 沿用 tick37 anti-inflation
- 任一 defense_layer fail 升级 F7 MCP 6-control baseline
- cross_cluster_arrows severity-B 触发 chief 6h SLA
- family decision MUST 写入 audit log (tick36 anti-inflation binding)

## 相关 references

- `references/tick39-deliverables.md` — F12 candidate 立卡
- `references/tick37-deliverables.md` — family anti-inflation binding
- `references/cron-tick-mcp-writer.md` — tick32 canonical writer
- arxiv 2607.05120 — ADI (Agent Data Injection)
- arxiv 2601.17549 — ProtoAmp (MCP protocol weakness)
- arxiv 2604.17125 — CASCADE 3-tier defense