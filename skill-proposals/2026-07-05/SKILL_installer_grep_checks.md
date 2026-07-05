---
name: installer-artifact-grep-checks
description: Windows / macOS / Linux installer artifact 发布前必跑的 5 项 grep 检查(冲突标记 / TODO 暴增 / import 验证 / py_compile / JSON parse)。Use when: qa-worker 在 release 前 / post-ship 收到 SyntaxError 报告 / researcher tick 报 GH #59004 类合并冲突 ship 事件。Catch merge conflict markers + syntax errors before users see them.
---

# installer-artifact-grep-checks

## 何时调用

- release 前(qa-worker release checklist)
- 收到用户 "fresh install 立即 SyntaxError" 报告 → 立即跑确认是否为 artifact 级别问题
- researcher tick 报 installer-related P1 ship

## 标准流程

跑 `scripts/release-grep-checks.sh <installer_dir>` 一键 5 项检查:

1. **Merge conflict markers**: `grep -E '^(<<<<<<<|=======|>>>>>>>)' **/*.py`
   - 命中 → CRITICAL,block ship
2. **TODO/FIXME 暴增**: `grep -rn 'TODO\|FIXME\|XXX' **/*.py | wc -l`
   - 必须 ≤ baseline + 10%
3. **Import smoke test**: `python3 -c "import hermes_cli.web_server"`
   - exit 0 → pass
4. **py_compile**: `python3 -m py_compile hermes_cli/web_server.py`
   - exit 0 → pass
5. **JSON parse**: 找所有 *.json → `python3 -c "import json; json.load(open(file))"`
   - 任何文件 exit ≠ 0 → CRITICAL

`scripts/release-grep-checks.sh` 必须 exit 0 才允许 ship。

## 何时不该调用

- 源码仓库(master / dev branch)的 PR review — 那是 dev-worker 范围
- 用户报 syntax error 但不涉及 installer(可能 runtime 引入)— 先跑正常 troubleshooting

## 验证

- 5 项 grep 全 exit 0 才算 skill 跑通
- 失败时输出 first_failure_file + first_failure_line,便于 dev-worker 定位