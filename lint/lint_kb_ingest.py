#!/usr/bin/env python3
"""
lint_kb_ingest.py - 防止 KB ingest 漏 context 字段
=====================================================

背景: 2026-06-22 发现 memory_slim v1/v2 的 ingest_to_kb 都没送 context, 导致 doc 写入
org=''/project='' 孤儿 namespace, list API 查不到. 9 个 doc 进了孤儿区, 全部清理.

这个 lint 抓两类问题:
  1. 静态扫描: grep 所有调 KB POST /knowledge/ingest_text 的代码, 校验 context 必填
  2. 运行时自检: 作为装饰器/上下文, ingest 前校验 payload 有 context

用法:
  # 静态扫描整个 hermes 仓 (默认 ~/.hermes/scripts + ~/.hermes/profiles/*/scripts)
  python3 lint_kb_ingest.py scan

  # 运行时包装 (在 memory_slim 之类的脚本里)
  from lint_kb_ingest import guarded_ingest
  doc_id = guarded_ingest(payload, token, "my-script")
"""

import os
import re
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional


# 关键 path: 必须送 context 的 endpoint
KB_INGEST_PATHS = [
    "/knowledge/ingest_text",
    "/knowledge/ingest_url",
]

# 必填 context 字段
REQUIRED_CONTEXT_FIELDS = ["org_id", "project_id"]


def lint_ingest_call(code: str, filepath: str) -> list[dict]:
    """
    扫一段代码,找调 KB ingest 的位置,校验 context 字段.

    Returns: list of issues, each: {"line": int, "file": str, "issue": str, "snippet": str}

    启发式: KB_INGEST_PATHS 在 payload / url 字段出现 + 紧跟 data=json.dumps(payload) 才算真调用.
    单纯的 path 常量或 docstring 提到不算.
    """
    issues = []
    lines = code.split(chr(10))
    n = len(lines)
    # 滑动窗口: 找 path 出现且 5 行内有 data=json.dumps
    for i, line in enumerate(lines):
        if not any(path in line for path in KB_INGEST_PATHS):
            continue
        # 5 行内必须有 data=json.dumps(payload)
        window_end = min(i + 6, n)
        window = chr(10).join(lines[i:window_end])
        if "data=json.dumps" not in window:
            continue
        # 触发: 真 POST 块开始, 现在看 20 行内有没有 context + org_id + project_id
        block_end = min(i + 25, n)
        block = chr(10).join(lines[i:block_end])
        has_context = '"context"' in block or "'context'" in block
        has_org_id = '"org_id"' in block or "'org_id'" in block
        has_project_id = '"project_id"' in block or "'project_id'" in block
        if not has_context:
            issues.append({
                "line": i + 1,
                "file": filepath,
                "issue": "KB ingest missing 'context' field in payload",
                "snippet": line.strip()[:80]
            })
        elif not has_org_id or not has_project_id:
            missing = []
            if not has_org_id: missing.append("org_id")
            if not has_project_id: missing.append("project_id")
            issues.append({
                "line": i + 1,
                "file": filepath,
                "issue": f"KB ingest context missing field(s): {', '.join(missing)}",
                "snippet": line.strip()[:80]
            })
    return issues


def scan_directory(root: str = "~/.hermes", exclude_self: bool = True) -> list[dict]:
    """扫根目录下所有 .py 文件, 找 KB ingest 不带 context 的."""
    all_issues = []
    root = os.path.expanduser(root)
    try:
        self_path = os.path.abspath(__file__)
    except NameError:
        self_path = None
    for dirpath, dirnames, filenames in os.walk(root):
        # 跳过虚拟环境和 node_modules
        if any(skip in dirpath for skip in [".venv", "node_modules", "__pycache__", ".git", "site-packages"]):
            continue
        for f in filenames:
            if not f.endswith(".py"):
                continue
            fp = os.path.join(dirpath, f)
            if exclude_self and self_path:
                try:
                    if os.path.abspath(fp) == self_path:
                        continue
                except Exception:
                    pass
            try:
                with open(fp) as fh:
                    code = fh.read()
            except Exception:
                continue
            issues = lint_ingest_call(code, fp)
            all_issues.extend(issues)
    return all_issues


def guarded_ingest(payload: dict, token: str, script_name: str = "unknown") -> Optional[str]:
    """
    运行时 guard: ingest 前校验 context, 缺则 fail-fast 而不是写孤儿 doc.

    用法 (替换原 urllib POST):
        from lint_kb_ingest import guarded_ingest
        doc_id = guarded_ingest(payload, token, "memory_slim_v2")
    """
    # 1. 校验 context
    ctx = payload.get("context")
    if not ctx:
        sys.stderr.write(f"BLOCK [{script_name}]: KB ingest missing 'context'. Refusing to write to orphan namespace.\n")
        sys.stderr.write(f"  payload keys: {list(payload.keys())}\n")
        sys.stderr.write(f"  fix: add payload['context'] = {'{'}org_id, project_id, agent_id, role{'}'}\n")
        return None
    for field in REQUIRED_CONTEXT_FIELDS:
        if not ctx.get(field):
            sys.stderr.write(f"BLOCK [{script_name}]: KB ingest context missing '{field}'.\n")
            return None

    # 2. 实际 POST
    url = "http://127.0.0.1:18081/knowledge/ingest_text"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "X-Admin-Token": token},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = json.loads(resp.read())
            if body.get("ok"):
                return body.get("data", {}).get("document_id")
    except (urllib.error.URLError, urllib.error.HTTPError) as e:
        sys.stderr.write(f"ERROR [{script_name}]: KB ingest failed: {e}\n")
    return None


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "scan":
        print("=== 扫描 KB ingest 漏 context 的代码 ===")
        issues = scan_directory()
        if not issues:
            print("OK 所有 KB ingest 调用都送了 context.")
            return 0
        print(f"发现 {len(issues)} 个问题:\n")
        for iss in issues:
            print(f"  [{iss['file']}:{iss['line']}] {iss['issue']}")
            print(f"    snippet: {iss['snippet']}")
        return 1
    else:
        print(__doc__)
        return 0


if __name__ == "__main__":
    sys.exit(main())
