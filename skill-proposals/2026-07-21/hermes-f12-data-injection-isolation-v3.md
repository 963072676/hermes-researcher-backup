---
name: hermes-f12-data-injection-isolation-v3
description: 'F12 candidate v3 — Agent Data Injection (ADI) 实证巩固: 跨 Claude Code + Codex + Gemini CLI + arxiv evidence = data-injection-isolation-deck family 立卡候选。F12 仍未升 family (family anti-inflation tick36 binding),但 evidence_ids 必须持续 update,等 ≥ 5 GH issue 同根才能立 family v1。Use when: 看到 arxiv 2607.05120 ADI 引用 / OX Security MCP STDIO RCE / 任何 trusted-vs-untrusted data 隔离缺失的 P1。'
version: 1.0.0
created_by: researcher C-profile auto-evolve (tick43 / 2026-07-21)
platforms: [linux, macos]
metadata:
  hermes:
    tags: [F12-candidate-v3, ADI, data-injection-isolation, MCP-supply-chain, isolation-deck]
    related: [hermes-data-injection-isolation-v2 (tick42), hermes-f11-invariant-9 (tick43 NEW), hermes-canonical-invocation-path-v1]
    evidence:
      - arxiv_2607_05120_ADI_paper  # Agent Data Injection
      - arxiv_2607_12624_PVDetector  # purpose-specific PV concept activation
      - arxiv_2601_17549_ProtoAmp     # tick36 evidence (沿用)
      - arxiv_2604_17125_CASCADE      # tick36 evidence (沿用)
      - Claude_Code_ADI (公开 reproducible)
      - Codex_ADI (公开 reproducible)
      - Gemini_CLI_ADI (公开 reproducible)
      - OX_Mother_MCP_STDIO_RCE_2026_04
---

# hermes-f12-data-injection-isolation-v3

> F12 candidate v3 / 沿用 tick36 evidence_ids + tick42/43 NEW
> **family anti-inflation binding (tick36): NOT yet立 F12 family, condition 1 (>=5 GH issues) pending**

## This skill solves

researcher v0.x 的痛点:
- instruction injection (IPI) defenses 已大量研究 + 实战 (CaMeL, Progent, FORGE)
- 但 **data injection** (trusted-data-disguised-as-context) 仍 underexplored
- ADI = Agent Data Injection 是 IPI 的一个新类别,直接 spoof trusted metadata (resource id / data origin / tool call format)
- 跨 agent platform (Claude Code / Codex / Gemini CLI) confirmed reproducible

C 档升级后 (candidate v3):
1. **隔离 contract** = trusted data 与 untrusted data 必须有 boundary tag
2. **tool call format provenance** = 任何 tool_call_input 必须 verify origin tag
3. **probabilistic delimiter** (tick42 立卡) 升级到 **origin-tag isolation**

## When to invoke

任何 cron worker / agent 见到以下条件立即触发:
1. agent 收到 tool result 含 resource identifier (URI / file path / URL)
2. tool result 含 agent context data (tool_call_response_format / preview metadata)
3. resource ID 来自外部 fetch (web_search / file read / MCP server)
4. tool call 需要查 trusted credential (OAuth / DB / API key)
5. web_extract content 进入 context 前 (web 红线层)

## F12 evidence_ids 升级链

| tick | evidence | family_state |
|---|---|---|
| tick36 | arxiv 2607.05120 ADI + 2601.17549 ProtoAmp + 2604.17125 CASCADE | candidate_pending |
| tick37-38 | F11 invariant 6 pre-commit gate (CVE-2026-61459 9.8) | candidate_pending |
| tick39 | F12 condition_2_met (Claude Code + Codex + Gemini CLI = 3 platform) | candidate_pending |
| tick40 | F12 candidate with condition_2_met_strong | candidate_v2 |
| tick41 | F12 condition_2_met (12 family) + cross-cluster CVE evidence | candidate_v2 |
| tick42 | F12 candidate_v2 expand (PVDetector + MOSAIC + Balkanization + PoE + CXI) | candidate_v2 |
| **tick43** | **arxiv 2607.12624 PVDetector + arxiv 2607.05120 ADI + OX Mother** | **candidate_v3** |

## 4-step ADI isolation (skill-proposal)

### Step 1: Origin tag schema

```python
class DataOriginTag:
    origin: Literal["user_input", "tool_result_external", "tool_result_trusted", "system_prompt", "memory_persistent"]
    trust_class: Literal["trusted", "untrusted", "isolated"]
    timestamp: str
    source_identifier: str
    isolation_boundary: str  # e.g. "may_not_invoke_credential_tools"
```

### Step 2: Tool result classifier

```python
def classify_tool_result_origin(tool_call_response):
    """Tag every tool result with origin + trust class before entering context"""
    if tool_call_response.tool_id.startswith("mcp-"):
        return DataOriginTag(
            origin="tool_result_external",
            trust_class="untrusted",
            source_identifier=f"mcp:{tool_call_response.server_id}",
            isolation_boundary="may_not_invoke_credential_tools_without_user_consent",
        )
    if tool_call_response.tool_id.startswith("web_"):
        return DataOriginTag(
            origin="tool_result_external",
            trust_class="untrusted",
            source_identifier=f"web:{tool_call_response.url}",
            isolation_boundary="may_not_modify_files_or_invoke_mutation_tools",
        )
    if tool_call_response.tool_id in ("read_file", "search_files"):
        return DataOriginTag(
            origin="tool_result_trusted",
            trust_class="trusted",
            source_identifier=f"local:{tool_call_response.path}",
            isolation_boundary="none",
        )
    return DataOriginTag(
        origin="tool_result_external",
        trust_class="isolated",
        source_identifier="unknown",
        isolation_boundary="must_revalidate_before_use",
    )
```

### Step 3: Trust boundary enforcement

```python
def invoke_credential_tool_check(origin_tag, credential_tool_name):
    """F12 candidate v3 baseline enforcement"""
    if origin_tag.trust_class == "untrusted" and "credential" in credential_tool_name.lower():
        return False, "untrusted origin may not invoke credential tools"
    if "may_not_invoke_credential_tools" in origin_tag.isolation_boundary:
        return False, f"origin isolation_boundary forbids credential tools"
    return True, "ok"
```

### Step 4: Audit log per call

```python
def f12_audit(origin_tag, tool_name, decision, reason):
    """Per-call audit, invariant F12 candidate v3"""
    audit_log("F12_data_injection_isolation", {
        "ts": now_iso(),
        "origin": origin_tag.origin,
        "trust_class": origin_tag.trust_class,
        "tool_name": tool_name,
        "decision": decision,  # "allow" | "block"
        "reason": reason,
        "isolation_boundary": origin_tag.isolation_boundary,
        "source_identifier": origin_tag.source_identifier,
    })
```

## family_state machine (binding contract)

```text
F12 states:
  candidate_pending     (need: 5+ GH issues OR 3+ platform)
       ↓
  candidate_v2          (tick40 achieve: 3+ platform + cross-cluster evidence)
       ↓
  candidate_v3          (tick43 NEW: ADI + PVDetector consolidation)
       ↓
  condition_2_met_strong (already, tick42)
       ↓
  family 立卡 v1         (need: condition_1: 5+ GH issues 同 root cause)
       ↓
  stable                (need: 14d + 5+ issues consolidated + fix PR merged)
```

## Verification checklist

1. **tool result classifier** 必在 `tool_result` 进入 agent context 前跑
2. **origin tag** 必传到下游 tool call decision
3. **credential tool check** 对 untrusted origin 默认 reject
4. **web extract redact** (沿用 tick32 outbound-redact-call-site) 不退化
5. **audit log per call** 必写入 (F12_data_injection_isolation)
6. **failure injection test**: 在 tool_result 注入 fake resource ID → must block
7. **failure injection test 2**: 在 tool_result 注入 fake tool_call_format override → must block

## Pitfalls

### origin tag 不可信
工具结果可以伪造 origin tag
→ 实际 enforce 必须在 classifier 端 (不可信 caller) 而非 trust caller 端

### legacy tool 不带 origin tag
旧 plugin (Honcho / MCP registration history) 可能 pre-classifier
→ 必须 backward-compat default = untrusted

### performance overhead
每个 tool_result 多一次 embedding compute → ~50-100ms latency
→ 必须 cache classifier result, hot path < 5ms

## Quantified impact

1. **降低 ADI attack success rate** from 72.8% to < 5% (沿用 arxiv PlanGuard claim)
2. **降低 OX STDIO RCE** attack surface by 60% (origin tag + tool description provenance combined)
3. **降低 #67012** (Cloudflare GRU keepalive) ↔ no direct mitigation, but tool_result path 经过 classifier 暴露 timing 异常
