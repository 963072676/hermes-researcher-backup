#!/usr/bin/env bash
# ~/.hermes/scripts/lint/pre-commit.sh
#
# Pre-commit hook: 阻止任何漏 context 字段的 KB ingest 提交
#
# 安装: ln -sf ~/.hermes/scripts/lint/pre-commit.sh ~/.hermes/.git/hooks/pre-commit
#       (或 cp 到 .worktrees/<branch>/.git/hooks/pre-commit)
#
# 触发: git commit 前自动跑, 任何 .py 里 KB ingest 漏 context 即 fail

set -e

LINT_SCRIPT=~/.hermes/scripts/lint/lint_kb_ingest.py

if [ ! -f "$LINT_SCRIPT" ]; then
    echo "WARN: lint script not found at $LINT_SCRIPT, skipping"
    exit 0
fi

# 只检查 staged .py 文件
STAGED_PY=$(git diff --cached --name-only --diff-filter=ACM | grep -E "\.py$" || true)

if [ -z "$STAGED_PY" ]; then
    exit 0
fi

echo "Pre-commit: scanning KB ingest context in staged .py files..."
ISSUES=0
for f in $STAGED_PY; do
    # 用 lint 的函数直接 import 跑
    RESULT=$(python3 -c "
import sys
sys.path.insert(0, '$(dirname $LINT_SCRIPT)')
from lint_kb_ingest import lint_ingest_call
with open('$f') as fh:
    code = fh.read()
issues = lint_ingest_call(code, '$f')
if issues:
    for iss in issues:
        print(f\"  L{iss['line']}: {iss['issue']}\")
    sys.exit(1)
" 2>&1)
    RC=$?
    if [ $RC -ne 0 ]; then
        echo "FAIL: $f"
        echo "$RESULT"
        ISSUES=$((ISSUES + 1))
    fi
done

if [ $ISSUES -gt 0 ]; then
    echo ""
    echo "BLOCK: $ISSUES file(s) have KB ingest missing context field."
    echo "fix: add payload['context'] = {'org_id': 'gc-hermes', 'project_id': 'gc-hermes-config', ...}"
    exit 1
fi

echo "OK all KB ingest calls have context."
exit 0
