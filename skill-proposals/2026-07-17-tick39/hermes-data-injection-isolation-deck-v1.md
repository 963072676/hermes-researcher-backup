# agent-data-injection-isolation-deck v1 (2026-07-17 tick39)

## 触发

arxiv 2607.05120v1 (2026-07) 揭示新 IPI 类别: Agent Data Injection (ADI)
- 评估 Claude in Chrome, Antigravity, Nanobrowser (web agents), Claude Code, Codex, Gemini CLI (coding agents)
- ASR 31.3-43.3% JSON delimiter injection; 33.3-100% web DOM
- 现有 defenses (alignment, dual-LLM, CaMeL strict) fail 22.2-50% ASR

任何 cron worker / pm 看到 ADI-relevant code path 立即触发:
- tool response format = JSON (template injection surfaces)
- web DOM trusted element selector (XSS-like)
- GitHub issue comment author spoofing (supply-chain attack vector)

## 流程

```python
def adi_isolation_verify(tool_response, agent_context):
    """Verify tool response is structurally consistent with declared schema."""
    return IsolationVerdict(trusted=trusted, sides={data: ..., instruction: ...})
```

## family candidate

- 立 family 12: data-injection-trusted-untrusted-isolation-deck
- sweeper marker: sweeper:risk-data-injection-isolation
- 5 invariant 必跑:
  1. Tool response schema strict validation
  2. Web DOM element identifier cryptographic binding
  3. Author provenance signature verify
  4. Trusted/untrusted data separate contextvars
  5. Compiler-required source-of-truth tracking

## evidence reference

- arxiv 2607.05120 (Agent Data Injection Attacks are Realistic Threats)
- arxiv 2607.12624 (PVDetector — concept-based detection alternative)
- arxiv 2607.13594 (Safety Sentry — Execute/Ask/Refuse three-way routing)

## 1-line rationale

F12 立卡候选 — 当前 11 family registry 都未覆盖 ADI 类别的 trusted/untrusted data 隔离
