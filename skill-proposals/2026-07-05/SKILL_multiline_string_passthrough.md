---
name: hermes-multiline-string-passthrough
description: 在 xai-oauth/grok-4.3 MCP tool call 路径上,对 multiline optional string 参数做 typed-guard 的 skill。Use when: 任一 grok-4.3 路径的 tool call 包含 multi-line string(典型:Markdown body, code fence, structured message),同时需要避免 issue #58345(可选 multiline string 被 grok-4.3 silent drop)。
---

# hermes-multiline-string-passthrough

## 何时调用

- researcher / chief / pm 任一 cron 调 `tool_call(...)` 若参数含 multiline optional string(典型: `body`, `content`, `description`, `body_markdown`)
- 临时切 provider 时(从 grok-4.3 切到 MiniMax-M3),自动 unhook 本 skill
- user 在 Grok 平台报告 "发邮件对方看到没换行" / "表格发过去塌缩" 类 symptom

## 标准流程

### Step 1: 检测 multiline payload

```python
def multiline_payload_check(name: str, value: str) -> dict:
    """
    任意 tool call 调前 probe:
    """
    has_newline = "\n" in value
    has_special = any(c in value for c in ["```", "|", "#", "*&*", "---", "...", "$", ""])
    is_optional_field = name in OPTIONAL_MULTILINE_FIELDS  # {"body", "content", "description", "body_markdown", "notes", "summary"}
    return {
        "name": name,
        "value_len": len(value),
        "has_newline": has_newline,
        "has_special": has_special,
        "is_optional_field": is_optional_field,
        "risk": has_newline and is_optional_field,
    }
```

### Step 2: path A - 自动 promote to required

```python
def promote_optional_to_required(tool_call: dict) -> dict:
    """
    per PR #58352 schema fix direction,但 client-side workaround:
    把 optional 空字段改成 required 空字符串
    """
    for param in tool_call.get("params", {}):
        if param["name"] in OPTIONAL_MULTILINE_FIELDS and param.get("default") is None:
            param["required"] = True
            param["default"] = ""
    return tool_call
```

### Step 3: path B - 加 prompt prefix

```python
def multiline_aware_prompt_prefix() -> str:
    """
    任何 openai-tool-call 调前注入 system prefix:
    "When invoking tools that accept multiline string parameters:
    ALWAYS pass the value as a literal string even if it contains
    \\n, ```, |, or markdown syntax. Never silently drop optional
    multi-line string args."
    """
    return _MULTILINE_PREFIX  # exported constant
```

### Step 4: fallback

```python
def request_provider_fallback() -> str:
    """
    实在不行:本环境 fallback provider = minimax-cn/MiniMax-M3
    不在 grok 路径承担 multiline风险
    """
    return "minimax-cn/MiniMax-M3"
```

## 何时不该调用

- 任何 openai/anthropic 走 native 路径(tests 已确认 native Anthropic 处理 multiline OK)
- tool call 参数是 array / object 非 string

## 验证

- 测试用例在 `tests/multiline_passthrough/test_grok_drop.py`:
  - 4 个 multiline payload scenario(简单换行 / Markdown 表格 / code fence / 长 paragraph)
  - 每个验证: 调前 multiline_payload_check 标 risk=True → 走 promote / prefix → 重调 → 对端收到含换行的内容
  - 必须用 live xAI provider(no mock — issue #58345 的 silent fail 是 behavior-level, mock 不可见)
- 离线可用模式: 在 dryrun 模式仅调 multiline_payload_check,不真正发 tool call
