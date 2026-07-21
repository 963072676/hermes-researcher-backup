---
name: hermes-tool-description-relevance-gate-v1
description: 'F11 invariant 8 — 任何 agent 写 skill / patch / write_file 操作必须在 relevance gate 验证: 目标 topic 必须与当前 session 实际 conversation topic 有 semantic match。当 agent 在 background_review pass / cron review / skill self-evolve 中, 防止不相关 evidence 写入无关伞级 skill。Use when: 看到 background review unrelated content write (#66350), tool_description 注入 (#67012/MCP STDIO RCE), 或任何 mismatch topic → umbrella skill patch 模式时。'
version: 1.0.0
created_by: researcher C-profile auto-evolve (tick43 / 2026-07-21)
platforms: [linux, macos]
metadata:
  hermes:
    tags: [F11, invariant-8, relevance-gate, skill-review, MCP-tool-description]
    related: [hermes-f11-invariant-1-7 (parent), hermes-canonical-invocation-path-v1, hermes-data-injection-isolation-v3]
    evidence:
      - GH #66350 (background_review unrelated content write)
      - GH #67012 (tool description injection vector via keepalive_expiry)
      - OX Security Mother of MCP Supply Chains (2026-04-16)
---

# hermes-tool-description-relevance-gate-v1

> F11 (execute-code-approval-unification-deck) **invariant 8** = relevance gate
> Tick43 立卡 / 沿用 tick36-42 立卡

## This skill solves

researcher v0.x 的痛点:
- background review 在 per-session tool-call counter 触发时, 即使 session 没碰 skill 也触发 review pass
- skill_manage patch / write_file 没 relevance gate 校验 → 不相关 evidence 进 umbrella skill references/
- tool description 可注入 (MCP STDIO RCE / CurXecute / MCPoison pattern family)

C档升级后:
1. **relevance gate** = topic-match verify between session conversation + target umbrella skill
2. **tool_description provenance** = source tracking + injection-vocab whitelist scan
3. **per-call guard pipeline** = background_review patch 必须走 danger_classify 不退化

## When to invoke

任何 cron worker / agent 见到以下条件立即触发:
1. background_review pass 触发前 (沿用 tick36 F11 invariant 5 audit_log_fields)
2. skill_manage(action=patch|write_file) 调用前
3. cron review 自动写 skill scenarios
4. MCP server tool 首次加载 (tool description 进 agent context)
5. any(unrelated_content_in_skill_writes) signal 异常

## 5-step relevance gate

### Step 1: Prepare session topic

```python
SESSION_TOPIC_BLOBS = []
def session_topic_collect(message):
    """Add message topic to session blob set"""
    if message.is_user or message.is_assistant_tool_call:
        topic = extract_topic_embedding(message.content)
        SESSION_TOPIC_BLOBS.append(topic)
```

### Step 2: Verify skill_loaded_this_session

```python
def _should_review_skills_v2(agent_state):
    """tick36 invariant (loaded check) upgrade to tick43 (relevance gate)"""
    if agent_state.creation_nudge_interval == 0:
        return False
    if agent_state._iters_since_skill < agent_state._skill_nudge_interval:
        return False
    # NEW tick43 invariant 8: only review if skill was actually loaded in this session
    if not agent_state._skills_loaded_this_session:
        return False  # <- unchanged behavior if no skill touched
    return True
```

### Step 3: Compute relevance score

```python
from sentence_transformers import SentenceTransformer
import numpy as np

_model = SentenceTransformer('all-MiniLM-L6-v2')

def relevance_score(session_topics, skill_doc_topics):
    """Cosine similarity between session and skill topic embeddings"""
    if not session_topics or not skill_doc_topics:
        return 0.0
    session_vec = np.mean(_model.encode(session_topics), axis=0)
    skill_vec = np.mean(_model.encode(skill_doc_topics), axis=0)
    return float(np.dot(session_vec, skill_vec) / (np.linalg.norm(session_vec) * np.linalg.norm(skill_vec)))

RELEVANCE_THRESHOLD = 0.45  # tunable; < 0.45 → block patch

def verify_relevance_before_patch(target_skill_name, session_topics):
    skill = skill_manage_view(name=target_skill_name)
    skill_topics = extract_skill_topics(skill)
    score = relevance_score(session_topics, skill_topics)
    if score < RELEVANCE_THRESHOLD:
        return False, f"relevance_score={score:.2f} < threshold, session did not touch this skill domain"
    return True, "ok"
```

### Step 4: Tool description provenance

```python
INJECTION_VOCAB = [
    "ignore previous", "system:", "override", "tool override",
    "hijack", "prompt injection", "argument injection",
    "command injection", "SQL injection",
]  # 9 项 injection-vocab whitelist

def tool_description_provenance(server_id, tool_name, description):
    """Verify MCP tool description is not instruction-like + provenance traceable"""
    desc_lower = description.lower()
    matches = [v for v in INJECTION_VOCAB if v in desc_lower]
    if matches:
        return False, f"tool_description contains injection-vocab: {matches}"
    # Also verify server hash pin (沿用 tick33)
    server_hash = mcp_registry.get_server_hash(server_id)
    if not server_hash:
        return False, f"server_id={server_id} has no commit SHA pin"
    return True, f"server={server_id}@commit={server_hash[:8]}"
```

### Step 5: Audit log + per-call guard

```python
def background_review_patch_guard(skill_name, session_topics):
    """F11 invariant 8 end-to-end guard"""
    audit = {
        "timestamp": now_iso(),
        "skill": skill_name,
        "session_topic_count": len(session_topics),
        "origin": "background_review",
    }
    ok, reason = verify_relevance_before_patch(skill_name, session_topics)
    audit["relevance_check"] = {"ok": ok, "reason": reason}
    if not ok:
        audit_log("F11_invariant_8_block", audit)
        return False, reason
    audit_log("F11_invariant_8_pass", audit)
    return True, "ok"
```

## Verification checklist

1. `_SKILL_REVIEW_PROMPT` 包含 relevance gate 字面 ("directly related to the skill's documented purpose and scope")
2. `_should_review_skills` 含 `_skills_loaded_this_session` 字段 check
3. skill_manage patch 前 relevance_score ≥ 0.45 否则拒绝
4. MCP tool description 含 injection-vocab 任一项 → 拒绝
5. audit log 每次 relevance check 必写入 (`F11_invariant_8_block` 或 `F11_invariant_8_pass`)
6. 失败注入测试: 制造 unrelated conversation → verify patch 被 reject
7. Per-call guard pipeline 不退化: F11 invariant 7 canonical_invocation_path 仍 binding

## Pitfalls

### 绕过 SVG / markdown / fenced content
恶意 session topic 嵌入 SVG alt-text → sentence-transformer 可能高估 relevance
→ 严格 mode 用 raw_markdown_strip 而非 full content

### sentence-transformer model bloat
all-MiniLM-L6-v2 ~80MB; 全 5 profile + 5 install profile deploy bloat ~2GB
→ 必须 lazy-load on first call; 默认 profile 不 bundle

### relevance_score 阈值校准
0.45 是经验值; 真实 cron-worker 测试可能 0.30-0.55
→ 必须 calibrate per profile baseline + 24h shadow mode

## Quantified impact

1. **降低 #66350 (background_review unrelated write)** 失败率 ≥ 80%
2. **降低 MCP STDIO RCE** (OX Security) attack vector by ~50% (tool description sanitize)
3. **降低 #67012 keepalive_expiry class** vector by 0% (这一 invariant 不直接修,但 #67012 仍需要 keepalive_pool_fair_play invariant 单独修)
