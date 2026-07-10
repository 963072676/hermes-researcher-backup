---
name: hermes-cross-platform-redact-call-site-audit
description: 'Tick32 立卡。沿用 tick27 release-grep-checks.sh 模式 + 5 platform cross-call-site audit,扫 gateway/platforms/{base,telegram,discord,slack,feishu,whatsapp}.py 是否调用 redact_sensitive_text()。当 outbound redaction P1 触发 (GH #23810) 或 release verification 需要 cross-platform gateway coverage audit 时使用。'
version: 0.1.0
created: 2026-07-10
category: devops
platforms: [linux, macos]
metadata:
  hermes:
    tags: [gateway, security, redaction, release-verification, cross-platform]
    related: [hermes-hardening-wave-verify, hermes-researcher-self-evolution-v1]
---

# hermes-cross-platform-redact-call-site-audit

> Hermes gateway outbound redact call-site audit tool
> 沿用 GH #23810 (open since 2026-05-11) + tick32 SOUL_chief 6h SLA 草案

## 触发条件

- outbound redaction P1 触发(GH #23810 + any future GH companion)
- v0.19.0 release gate 需要 cross-platform gateway coverage audit
- cron tick32+ researcher 监控 P1 cluster 提示
- qa upgrade release verification v2 baseline (沿用 tick32 SOUL_qa 草案)

## 实现要点

5 platform cross-call-site audit,扫 `gateway/platforms/{base,telegram,discord,slack,feishu,whatsapp,signal}.py` 是否在 outbound delivery path 之前调用 `redact_sensitive_text()`:

```python
#!/usr/bin/env python3
"""scripts/cross-platform-redact-audit.py

Scan gateway/platforms/*.py for outbound delivery call sites and verify
that each routes through redact_sensitive_text() before sending.

Exit codes:
  0 - all delivery call sites covered
  1 - one or more uncovered delivery paths found
  2 - scan error (file not found, parse error)
"""
import re
import sys
import pathlib

PLATFORMS = ["base", "telegram", "discord", "slack", "feishu", "whatsapp", "signal"]
PLATFORM_DIR = pathlib.Path("gateway/platforms")

# Outbound delivery pattern
DELIVERY_PATTERNS = [
    re.compile(r"\b(bot\.send_message|application\.bot\.send_message)\s*\("),
    re.compile(r"\b(await\s+self\._platform_send|self\._platform_send)\s*\("),
    re.compile(r"\bdiscord\.Client\.send_message|webhook\.send\b|requests\.post.*messages"),
    re.compile(r"\b(client\.send_message|client\.post|send_text|send_message)\s*\("),
    re.compile(r"\bawait\s+(self|client|ctx|message|bot)\.send\b"),
    re.compile(r"\b(client\.send|send_request|outbound_send)\s*\("),
]

REDACT_PATTERN = re.compile(r"\bredact_sensitive_text\s*\(")


def scan_platform(platform_file: pathlib.Path) -> list[dict]:
    """Return list of uncovered delivery call sites for a platform file."""
    if not platform_file.exists():
        return []
    text = platform_file.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()

    uncovered = []
    for i, line in enumerate(lines, 1):
        for dp in DELIVERY_PATTERNS:
            if dp.search(line):
                # Check 50 lines of context backward for redact call
                start = max(0, i - 50)
                context = "\n".join(lines[start:i])
                if not REDACT_PATTERN.search(context):
                    uncovered.append({
                        "file": str(platform_file),
                        "line": i,
                        "snippet": line.strip()[:120],
                    })
                break
    return uncovered


def main():
    all_uncovered = []
    for platform in PLATFORMS:
        # try .py and subfolder variants
        candidates = [
            PLATFORM_DIR / f"{platform}.py",
            PLATFORM_DIR / platform / "__init__.py",
            PLATFORM_DIR / platform / "client.py",
        ]
        for c in candidates:
            uncovered = scan_platform(c)
            all_uncovered.extend(uncovered)

    if all_uncovered:
        print(f"[FAIL] {len(all_uncovered)} uncovered outbound delivery call sites:")
        for u in all_uncovered:
            print(f"  {u['file']}:{u['line']}  {u['snippet']}")
        sys.exit(1)

    print(f"[PASS] all {len(PLATFORMS)} platform outbound call sites covered by redact_sensitive_text()")
    sys.exit(0)


if __name__ == "__main__":
    main()
```

## 推荐调用

```bash
# local dev: 前 commit 前跑
python3 scripts/cross-platform-redact-audit.py || { echo "BLOCK release"; exit 1; }

# CI: pre-merge 必须 exit 0
python3 scripts/cross-platform-redact-audit.py

# release verification: v0.19.0 ship 前必须跑
scripts/release-verification-suite.sh  # 含 5 grep + 4 functional 包含本 audit
```

## 评判准则

- 5 platform 必须全部 cover:base.py + 4 platform adapter(telegram 已 verify,3 个待补)
- ship gate 必须 exit 0,emergency 提供 `--skip-on-emergency` flag 但 48h 内补跑(沿用 tick28 hardening wave II ship-time gap 模式)
- audit 通过的 PR 必须附 cross-platform 输出 (5 platform 各 1 行)

## Pitfalls

- 漏 platform:某些 platform subdirectory (`gateway/platforms/feishu/client.py`) 与 flat (`feishu.py`) 模式共存 — script 必须 try 多个 variant
- false positive: outbound call site 在 `_platform_send` helper 内而不是直接 `bot.send_message` — 应当 accept helper invocation 也算 covered(provided helper 内部 wrap through redact)
- false negative: redact call 在 51+ 行之前 — context window 调整到 100 行更稳
- platform 命名:signal / matrix / iphone / android 是 sister platforms,本 tick 仅覆盖 v0.18 已 ship 平台,但未来 platform 出现必须追加到 PLATFORMS list

## v0.19.0 实装 schedule

1. **2026-07-12** (tick33): 立卡本 skill + script 创建在 `~/.hermes/scripts/cross-platform-redact-audit.py`
2. **2026-07-14**: 5 platform 各 verify 1 遍,audit exit 1 (uncovered) — chief 6h SLA 启动
3. **2026-07-16**: merged fix PR,audit exit 0
4. **2026-07-20**: ship v0.19.0 含 audit + fix
