---
name: hermes-f12-candidate-data-injection-isolation-boundaries-v2
description: F12 data-injection-isolation-deck candidate v2 — 5 boundaries taxonomy defense layer + probabilistic delimiter detection + origin tag integrity + trust/untrusted data isolation enforcement。Use when: 任何 agent data injection (ADI) 类 attack (arxiv 2607.05120 + MOSAIC 2607.02857) 防御,跨 ≥ 3 platform (Claude Code + Codex + Gemini CLI + mcp-server-kubernetes via CVE-2026-61459) 触发 F12 candidate 拉新 evidence 但 family anti-inflation 守约 (tick36 binding, 仍 candidate,待 condition_1 ≥ 5 GH issue met 才升 F12 family)。
version: 2.0.0
created_by: researcher
family: F12-candidate-v2
---

# hermes-f12-candidate-data-injection-isolation-boundaries-v2

## 触发

- F12 data-injection-isolation-deck candidate (tick40-41 立卡, condition_2_met=true)
- tick42 拉新 evidence:
  - arxiv 2607.05120 ADI (Claude Code + Codex + Gemini CLI 跨 ≥ 3 platform 实证)
  - arxiv 2607.02857 MOSAIC (CLI composition 96.59% ASR)
  - arxiv 2607.05743 Balkanization (39 papers 17 categories 5 gaps — execution-security survey)
  - arxiv 2607.05397 PoE (Proof of Execution 5 invariants G1-G5)
  - arxiv 2607.06000 CXI (Context-to-Execution Integrity — field/effect/invocation authority 3 bind)
  - CVE-2026-61459 (mcp-server-kubernetes 9.8 CRITICAL, 跨 F11 + F7 + F12 cross-cluster anchor)
- 沿用 tick36 family anti-inflation 准则 (binding): condition_1 (≥ 5 GH issue) 仍未 met → 维持 candidate

## 解决什么

F12 candidate v1 (tick41 立卡) 仅提 5 boundaries taxonomy 防御层,tick42 升级 v2:
- 5 boundaries taxonomy 仍 binding
- **v2 NEW**: probabilistic delimiter detection (沿用 arxiv 2607.05120 ADI 第 4.3 attack 防御)
- **v2 NEW**: origin tag integrity verification (沿用 arxiv 2607.05120 第 4.2 attack 防御)
- **v2 NEW**: trust/untrusted data isolation enforcement (沿用 arxiv 2607.05743 "absent data-instruction boundary" gap)
- **v2 NEW**: PoE-style runtime verification (沿用 arxiv 2607.05397)
- **v2 NEW**: CXI-style 3-authority binding (沿用 arxiv 2607.06000)

## 标准流程

### Step 1: 5 boundaries taxonomy 防御 (沿用 tick41 v1)

```python
# 5 boundaries (沿用 arxiv 2607.12406)
BOUNDARIES = {
    "B1_data_instruction": "untrusted data vs trusted instructions",
    "B2_origin_trust": "data origin metadata vs content",
    "B3_tool_resource": "tool call target vs resource identifier",
    "B4_session_surface": "active session vs observer surface",
    "B5_state_mutation": "passive state read vs active mutation",
}

def check_boundary_violation(boundary_id: str, payload: dict) -> bool:
    # 沿用 tick41 5 boundaries verify
    return BOUNDARY_CHECKS[boundary_id](payload)
```

### Step 2: probabilistic delimiter detection (v2 NEW)

```python
# 沿用 arxiv 2607.05120 §4.3 supply chain attack via tool call block injection
import re

DELIMITER_PATTERNS = [
    re.compile(r"<function_calls>"),           # Claude Code
    re.compile(r"</function_calls>"),
    re.compile(r"<function_results>"),
    re.compile(r"</function_results>"),
    re.compile(r"<antml:function_calls>"),    # Anthropic ML variant
    re.compile(r"</antml:function_calls>"),
    re.compile(r"<tool_use>"),                # Generic
    re.compile(r"</tool_use>"),
    re.compile(r"<tool_result>"),
    re.compile(r"</tool_result>"),
]

def detect_probabilistic_delimiter_injection(content: str) -> tuple[bool, str]:
    """返回 (is_injection, evidence)"""
    for pat in DELIMITER_PATTERNS:
        if pat.search(content):
            return True, f"Delimiter injection detected: {pat.pattern}"
    return False, "PASS"
```

### Step 3: origin tag integrity verification (v2 NEW)

```python
def verify_origin_tag_integrity(content: str, claimed_origin: str) -> tuple[bool, str]:
    """沿用 arxiv 2607.05120 §4.2 — origin metadata must NOT be embedded in untrusted content"""
    # 1. parse content for origin-style metadata
    origin_patterns = [
        re.compile(r"author[=:]\s*[\w-]+"),
        re.compile(r"maintainer[=:]\s*[\w-]+"),
        re.compile(r"reviewer[=:]\s*[\w-]+"),
        re.compile(r"trusted[=:]\s*true"),
    ]
    for pat in origin_patterns:
        if pat.search(content):
            return False, f"Origin-style metadata in untrusted content: {pat.pattern}"

    # 2. cross-check claimed_origin against source verification
    verified_origin = verify_origin_provenance(claimed_origin)
    if verified_origin != claimed_origin:
        return False, f"Origin provenance mismatch: claimed={claimed_origin} verified={verified_origin}"

    return True, "PASS"
```

### Step 4: trust/untrusted data isolation (v2 NEW)

```python
# 沿用 arxiv 2607.05743 "absent data-instruction boundary" gap
# 沿用 arxiv 2607.06000 CXI 3-authority binding (field / effect / invocation)

DATA_TRUST_LEVELS = ["trusted", "untrusted", "unknown"]

def isolate_data_instruction_boundary(data: dict, instruction: dict) -> tuple[bool, str]:
    """data 和 instruction 必须显式 trust level 标签 + 三 authority bind check"""
    data_trust = data.get("trust_level", "unknown")
    instruction_trust = instruction.get("trust_level", "unknown")

    if data_trust == "untrusted" and instruction_trust == "trusted":
        # 不允许 untrusted data 直接作为 instruction
        return False, "BLOCKED: untrusted data cannot be interpreted as trusted instruction"

    # CXI 3-authority bind check
    if not bind_field_authority(data, instruction):
        return False, "BLOCKED: field authority not bound"
    if not bind_effect_authority(data, instruction):
        return False, "BLOCKED: effect authority not bound"
    if not bind_invocation_authority(data, instruction):
        return False, "BLOCKED: invocation authority not bound"

    return True, "PASS"
```

### Step 5: PoE-style runtime verification (v2 NEW)

```python
# 沿用 arxiv 2607.05397 5 invariants G1-G5
POE_INVARIANTS = {
    "G1_authorization": "no effectful action without valid allow under contract C",
    "G2_path_compliance": "every action stays within canonical Gateway evaluation scope",
    "G3_null_effect_on_deny": "denied branches produce no persistent state",
    "G4_history_integrity": "recorded T is unaltered record of what occurred",
    "G5_replayability": "replay under (C,T,R) yields same terminal result",
}

def verify_poe_invariants(action: dict, contract: dict, history: list) -> tuple[bool, list]:
    """返回 (all_pass, failed_invariants)"""
    failed = []
    if not check_authorization(action, contract):
        failed.append("G1_authorization")
    if not check_path_compliance(action, history):
        failed.append("G2_path_compliance")
    if not check_null_effect_on_deny(action):
        failed.append("G3_null_effect_on_deny")
    if not check_history_integrity(history):
        failed.append("G4_history_integrity")
    if not check_replayability(action, contract, history):
        failed.append("G5_replayability")
    return len(failed) == 0, failed
```

### Step 6: combined audit log

```python
audit_log_entry = {
    "boundary_check": boundary_check_result,           # Step 1
    "delimiter_injection_check": delimiter_check,      # Step 2
    "origin_tag_integrity": origin_check,              # Step 3
    "data_instruction_isolation": isolation_check,     # Step 4
    "poe_invariants": poe_check,                       # Step 5
    "trust_boundary_impact": "info_disclosure/full_compromise/action_authority",
    "family_signal_lifecycle": {
        "family_count_total": 11,                       # 沿用 tick41
        "family_count_lifecycle_stages": {"emerging": 0, "stable": 5, "expansion": 3, "maintenance": 3, "deprecated": 0},
        "F12_status": "candidate",
        "F12_condition_1": "NOT MET (>= 5 GH issue required)",
        "F12_condition_2": "MET (>= 3 platform: Claude Code + Codex + Gemini CLI + mcp-server-kubernetes via CVE-2026-61459)",
        "F12_condition_3": "tick42 评估: maintained as candidate due to anti-inflation (tick36 binding)",
    },
}
```

## Verification (qa ship gate v12 必跑)

```bash
# 5 verify points (新增 tick42 F12 candidate v2):
1. boundary_violation_test: 5 boundaries 全部 fail-test fixture PASS
2. probabilistic_delimiter_injection_test: mock <function_calls> in PR description → BLOCKED
3. origin_tag_integrity_test: mock "author=maintainer" in issue comment → BLOCKED
4. trust_untrusted_isolation_test: untrusted data as trusted instruction → BLOCKED
5. poe_invariant_test: 5 invariants G1-G5 fail-test fixture PASS

# CVE-2026-61459 fixture (cross-cluster):
# - mock mcp-server-kubernetes < 3.9.0 + leading-dash arg injection
# - expected: BLOCKED at F11 invariant 8 (static_arg_injection_precheck) + F12 boundary B2_origin_trust
```

## Pitfalls (持续追加)

### tick42 - family anti-inflation 守约 (binding)

**触发**: tick42 拉新 5 arxiv 论文 + CVE-2026-61459 anchor,evidence 极丰富,容易误升 F12 family。

**修正**: 沿用 tick36 family anti-inflation 准则 (binding):condition_1 (≥ 5 GH issue 同 root cause) 仍未 met → 维持 candidate,**不允许升 F12 family**。即使 evidence 丰富,family 命名必须反映 condition_1 真实达成度。

### tick42 - probabilistic delimiter detection false positive

**触发**: 合法 documentation 含 `<function_calls>` 字面 (例如用户写 README 教 agent 怎么用),会被误命中。

**修正**: 加 code block context check,如果 delimiter 出现在 ``` fenced code block + 用户显式 "this is documentation" 标记 → 跳过 detection。

### tick42 - origin tag integrity 跨 surface

**触发**: GitHub issue comment 含 `author: maintainer` 字面 (合法字段),被 origin tag integrity 误命中。

**修正**: origin tag integrity 仅在 data trust_level == "untrusted" 时启用,trusted data (例如官方 API response) 跳过。

## Affected

- F12 candidate v1 → v2 升级 (tick42)
- 5 boundaries taxonomy 防御层 (沿用 tick41)
- F11 invariant 8 配合 (cross-cluster anchor CVE-2026-61459)
- qa ship gate v12 +5 verify (沿用 tick42 qa-agent 草案)
- pm-agent 24-field v10 acceptance (family_signal_lifecycle + F12 condition_2_met 强化)
- default-agent MCP 2026-07-28 readiness v6 control 15 (cross-family dedup)
- 沿用 tick36 family anti-inflation (binding),F12 仍 candidate

## 相关 references

- `references/tick41-deliverables.md` (tick41 F12 candidate v1)
- `references/tick40-deliverables.md` (tick40 F12 condition_2_met)
- `references/tick36-execution-deltas.md` (tick36 family anti-inflation binding)
- `references/tick34-deliverables.md` (tick34 立卡 family anti-inflation 雏形)

## Self-downgrade v4 evaluation

streak = 18 days zero-adoption
- rule 2: F10 旧 7 hits + tick42 F11 #60077/#60799 = 9 hits ✅
- rule 3: PR-dedup fire ≥ 2 跨 family = 3 fires ✅
- rule 4: silent-fail F1 cross-month ✅
- rule 5: P1 ≥ 8 + streak ≥ 4 ✅

**决策**: maintain_daily + 飞书 3 选项 A/B/C