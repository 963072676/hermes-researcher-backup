---
name: hermes-release-dual-track-verify
description: 'Hermes release verification dual-track 流程(fresh install + in-place update)。Use when: researcher tick 检测到 installer-corruption-runtime family 30 天 ≥ 2 hits;或 qa-worker 准备 release verification checklist;或 chief-agent 收到 ship-time gap 升级。'
version: 0.1.0
author: Hermes Agent (researcher tick29)
license: MIT
created_by: agent
metadata:
  hermes:
    tags: [release, ship-time, installer, qa, hermes-agent]
    related: [hermes-researcher-self-evolution-v1, hermes-hardening-wave-verify]
---

# hermes-release-dual-track-verify

> Hermes release verification dual-track 流程。
> tick29 立卡 — GH #60384(2026-07-07 filed) + tick27 #59004 复发升级。

## 这个 skill 解决什么

v0.18.0 ship 后 installer-corruption-runtime family 30 天内 2 hits:
- **tick27 #59004**: Windows installer 内嵌的 web_server.py 含 merge conflict 标记 ship 给用户,fresh install 立即 SyntaxError
- **tick29 #60384**: Windows `hermes update` 后 hermes_bootstrap.py 被 corrupt,line 205 `import asyncio.coroutines` 残留导致 SyntaxError,fresh backend crash loop

**根因**: tick27 已立卡 qa 5-item grep checklist,但只覆盖 fresh install path。**in-place update**(`hermes update`)走独立 path 且未接入 qa verification。

## 何时调用

- researcher tick 检测到 installer/ship-time 相关 P1+(merge conflict / SyntaxError / partial file / Windows-specific)
- chief-agent 收到 ship-time gap 升级
- qa-worker 准备 release verification checklist
- dev-worker 修完 installer/update 代码后,跑 release verify

## 标准流程

### Step 1: 双轨定义

```bash
# track 1 — fresh install
INSTALL_CHANNELS=("exe" "msi" "dmg" "deb" "rpm" "AppImage")

# track 2 — in-place update
UPDATE_CHANNELS=("hermes update" "brew upgrade hermes" "pip install -U hermes-agent")

# track 3 — hot-fix (emergency flag, audit 必须 48h 内补跑)
HOTFIX_CHANNELS=("emergency patch" "manual .py drop-in")
```

### Step 2: 5+1 item grep checklist(dual-track 通用)

```bash
#!/bin/bash
# scripts/release-grep-checks.sh — dual-track release verification
set -e

TARGET_DIR="${1:-.}"  # 默认当前目录,可指定 installer bundle 或 update 后 install root
TRACK="${2:-fresh-install}"  # fresh-install / in-place-update / hotfix

echo "=== release-grep-checks dual-track [${TRACK}] on ${TARGET_DIR} ==="

# 1. merge conflict markers grep
echo "[1/6] merge conflict markers..."
if grep -rE '^(<<<<<<< |=======|>>>>>>> )' "${TARGET_DIR}" --include='*.py' --include='*.yaml' --include='*.json' --include='*.md' 2>/dev/null; then
    echo "FAIL: merge conflict markers found"
    exit 1
fi

# 2. TODO FIXME 暴增 ≤ baseline + 10%
echo "[2/6] TODO FIXME delta..."
TODO_BASELINE=200  # 来自 git log 历史 baseline
TODO_NOW=$(grep -rE '(TODO|FIXME)' "${TARGET_DIR}" --include='*.py' 2>/dev/null | wc -l)
TODO_DELTA=$(echo "scale=0; (${TODO_NOW} - ${TODO_BASELINE}) * 100 / ${TODO_BASELINE}" | bc)
if [[ ${TODO_DELTA} -gt 10 ]]; then
    echo "FAIL: TODO FIXME delta ${TODO_DELTA}% > 10%"
    exit 1
fi

# 3. import smoke test
echo "[3/6] import smoke test..."
python3 -c "
import sys, os
sys.path.insert(0, '${TARGET_DIR}')
for mod in ['hermes', 'hermes_cli', 'agent', 'hermes_bootstrap']:
    try:
        __import__(mod)
        print(f'  OK: {mod}')
    except ImportError as e:
        print(f'  SKIP: {mod} (not installed in ${TARGET_DIR})')
"

# 4. py_compile exit 0
echo "[4/6] py_compile..."
PY_FILES=$(find "${TARGET_DIR}" -name '*.py' -not -path '*/test/*' -not -path '*/.git/*' 2>/dev/null)
COMPILE_FAIL=0
for f in ${PY_FILES}; do
    if ! python3 -m py_compile "${f}" 2>/dev/null; then
        echo "  FAIL: py_compile ${f}"
        COMPILE_FAIL=$((COMPILE_FAIL + 1))
    fi
done
if [[ ${COMPILE_FAIL} -gt 0 ]]; then
    echo "FAIL: ${COMPILE_FAIL} py_compile failures"
    exit 1
fi

# 5. JSON parse 必须成功
echo "[5/6] JSON parse..."
JSON_FILES=$(find "${TARGET_DIR}" -name '*.json' -not -path '*/.git/*' -not -path '*/node_modules/*' 2>/dev/null)
JSON_FAIL=0
for f in ${JSON_FILES}; do
    if ! python3 -c "import json; json.load(open('${f}'))" 2>/dev/null; then
        echo "  FAIL: JSON parse ${f}"
        JSON_FAIL=$((JSON_FAIL + 1))
    fi
done
if [[ ${JSON_FAIL} -gt 0 ]]; then
    echo "FAIL: ${JSON_FAIL} JSON parse failures"
    exit 1
fi

# 6. Windows-specific(只在 Windows-like 路径名含 hermes_bootstrap.py / web_server.py 时跑)
echo "[6/6] Windows-specific critical modules..."
WIN_CRITICAL=("hermes_bootstrap.py" "web_server.py" "hermes_cli/update.py")
for mod in "${WIN_CRITICAL[@]}"; do
    if [[ -f "${TARGET_DIR}/${mod}" ]]; then
        if ! python3 -m py_compile "${TARGET_DIR}/${mod}" 2>/dev/null; then
            echo "  FAIL: Windows critical ${mod} py_compile"
            exit 1
        fi
    fi
done

echo "=== PASS: dual-track release verification [${TRACK}] ==="
exit 0
```

### Step 3: dual-track runbook

```bash
# 每次 release 前必跑
scripts/release-grep-checks.sh ./bundle-installer fresh-install
scripts/release-grep-checks.sh ./simulate-update-output in-place-update

# hot-fix release
scripts/release-grep-checks.sh ./hotfix-patch hotfix

# 全 exit 0 才允许 ship
```

### Step 4: 5-day ship-time audit(每周一发布)

```markdown
# docs/audit/ship-time-weekly-YYYY-MM-DD.md

## 5-day ship-time audit

| 日期 | release | fresh-install verify | in-place-update verify | hotfix verify |
|---|---|---|---|---|
| YYYY-MM-DD | vX.Y.Z | PASS | PASS | (N/A) |
| ... | ... | ... | ... | ... |

## installer-corruption-runtime family 30-day recurrence
- #59004 (2026-06-XX) — fresh install — fresh-install verify 漏检 → checklist 扩展
- #60384 (2026-07-07) — in-place update — in-place update verify 漏检 → checklist dual-track

## 趋势
- ↑ / ↓ / =

## 若 30 天内 ≥ 3 hits → 冻结对应 release channel
```

### Step 5: 失败回退

```bash
# dual-track verify 失败立即:
# 1. 飞书报错(oc_c653562b)
# 2. 阻断 release
# 3. 启动 rollback 流程(in-place update 回退到 backup, fresh install 重下 bundle)
# 4. 立 issue 标 sweeper:risk-installer-corruption-runtime
# 5. 5-day audit 报告 +1 hit,触发升级条件判定
```

## 验证清单

- [ ] `scripts/release-grep-checks.sh` 存在且 chmod +x
- [ ] 6-item 全 exit 0(fresh-install + in-place-update + hotfix 三 track)
- [ ] 每周一 `docs/audit/ship-time-weekly-*.md` 自动产出
- [ ] 30-day installer-corruption-runtime family 计数 ≥ 3 → 自动冻结 release channel
- [ ] qa-worker 每日 09:00 UTC 跑 dual-track verify,失败立即飞书报错

## Pitfalls

- 不要只跑 fresh install — in-place update 是 Windows 用户主要路径
- 不要 skip Windows-specific(第 6 item)— #60384 是 Windows update 通道,Linux/macOS 不复现
- TODO FIXME baseline 不能用当前数 — 必须 git log 历史查 30 天前的 baseline,避免自我 baseline 偏差
- hot-fix 必须事后 48h 内补跑 full dual-track audit,emergency flag 是临时放行不是豁免
- Windows py_compile 必须显式调 python3 — Windows 默认无 python3 符号链接

## 关联

- 上游: GH #59004(tick27) + #60384(tick29)
- 关联 family: silent-fail(tick27) / cross-platform-state(tick28) / **installer-corruption-runtime(tick29 新立卡)**
- 关联 skill: hermes-hardening-wave-verify(tick28,补全权限侧 ship-time gap)
- 关联 SOUL 草案: `soul-proposals/2026-07-07/SOUL_qa_draft.md` + `SOUL_pm_draft.md`

## 历史立卡

- 2026-07-07: tick29 初版,基于 #60384 复发升级
- 2026-07-05: tick27 立卡 5-item grep checklist(只覆盖 fresh install)
- 2026-07-06: tick28 立卡 `hermes-hardening-wave-verify`(权限侧 ship-time gap)