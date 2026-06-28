---
name: pii-redact-pattern
description: 扩展 hermes redact 层到 PII 维度 (email / GCP project ID / service account email / 内部 IP/hostname)。Use when: 用户 commit / log / memory 内容含 PII 字面, 触发 #54305 模式, 或 researcher 抓回 GitHub README 含私有配置。
---

# pii-redact-pattern

> Hermes redact 模式扩展:从 secret 维度升级到 PII 维度。

## 何时调用

- commit message 含 `user@domain.com` 字面
- log 输出含 GCP/AWS project ID (12+ digit)
- send_message 输出含 `*@*.iam.gserviceaccount.com`
- researcher profile 抓回 GitHub README 含私有 config
- pre-commit 自检失败: `git diff --cached | grep -E "(user@|project[_-]?id|service[_-]?account)"`

## 标准流程

### Step 1: 加载 PII 模式

```python
import re

PII_PATTERNS = {
    "email": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    "gcp_project_id": re.compile(r"\b\d{12,30}\b"),  # GCP / AWS 12+ digit ID
    "sa_email": re.compile(r"[a-zA-Z0-9-]+@[a-zA-Z0-9-]+\.iam\.gserviceaccount\.com"),
    "internal_ip": re.compile(r"\b(10|192\.168|172\.(1[6-9]|2[0-9]|3[01]))\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"),
    "internal_hostname": re.compile(r"\b[a-z0-9-]+\.(internal|corp|lan|local)\b"),
}

def redact_pii(text: str) -> str:
    out = text
    for kind, pat in PII_PATTERNS.items():
        out = pat.sub(f"<{kind}_redacted>", out)
    return out
```

### Step 2: 在 commit / log / memory 写入前跑

```python
# pre-commit hook
import subprocess
diff = subprocess.check_output(["git", "diff", "--cached"], text=True)
redacted = redact_pii(diff)
if redacted != diff:
    print("BLOCK: PII in commit, see /tmp/redacted_diff.txt")
    open("/tmp/redacted_diff.txt", "w").write(redacted)
    exit(1)
```

### Step 3: 在 MCP payload 内容写入前跑

```python
# mcp_writer.py add this
import json
payload = json.loads(open(sys.argv[1]).read())
if "content" in payload:
    payload["content"] = redact_pii(payload["content"])
```

### Step 4: 验证

```python
test = "Contact alice@chrishamptonlaw.com about GCP project 391162310014"
assert "alice@" not in redact_pii(test)
assert "391162310014" not in redact_pii(test)
print("OK")
```

## 何时不该调用

- 用户明确提供 PII 作为业务数据 (e.g. CRM 记录), 不应 redact
- 测试 fixture 含 example.com / 192.0.2.0 (RFC 5737 文档 IP) — regex 应保留 doc IP
- 已经走官方 hermes redact 层处理的 token 类 (sk-..., Bearer ***)

## Pitfalls

- **gcp_project_id regex 12-30 digit 会误伤长数字** (e.g. 1000000 = 7 digit, 不命中; 但 invoice 总额 123456789012 可能误命中): 增加 context check "前 30 char 含 'project'/'id'/'account'"
- **internal_ip regex 172.16-31 与公网 172.x.x.x 冲突**: 加 boundary `(?:^|[^\d.])`
- **sa_email 模式可能被 github bot email 误伤**: `noreply@github.com` 不应 redact, 加 allowlist

## 关联监控

- GH #54305 (URGENT Issue open 2026-06-28) — PII 泄漏事件
- 现有 `~/.hermes/redact_patterns.yaml` (secret 维度, 加 pii 段)
- hermes 现有 `data_flow_purification_layer` (2026-06-22) 仅 secret

## 验证清单

```bash
# 单测
python3 -c "
from pii_redact import redact_pii
print(redact_pii('alice@chrishamptonlaw.com GCP 391162310014 sa@proj.iam.gserviceaccount.com 10.0.0.1'))
# 期望: <email_redacted> GCP <gcp_project_id_redacted> <sa_email_redacted> <internal_ip_redacted>
"
```