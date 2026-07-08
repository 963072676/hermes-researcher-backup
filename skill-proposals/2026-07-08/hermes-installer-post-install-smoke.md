---
name: hermes-installer-post-install-smoke
description: 'Windows / macOS / Linux installer artifact 在 release ship 前必跑 5+5 项 fresh-install smoke gate。Track 1 (release artifacts): 合并冲突 grep + py_compile + JSON parse + import smoke + TODO/FIXME baseline drift。Track 2 (fresh install): clean VM + hermes update + gateway 启动 + config 往返 + log 检查。Use when: 任何 release ship 前 / hermes-update 后 / installer-related P1 涌现。'
version: 0.1.0
author: Hermes researcher (tick30)
license: MIT
created_by: agent
metadata:
  hermes:
    tags: [installer, smoke-test, ship-gate, release-verification, windows, macos, linux]
    related: [hermes-researcher-self-evolution-v1, hermes-hardening-wave-verify]
---

# hermes-installer-post-install-smoke

## 这个 skill 解决什么

**tik27 / tick30 实战 2 次 install-recurrence**:
- #59004 (2026-07-05): Windows installer web_server.py 合并冲突 ship
- #60384 (2026-07-07): Windows hermes_bootstrap.py `hermes update` 后 SyntaxError

每次 ship 都暴露相同家族,证明 release verification 流程的根本缺口。**installer artifact ship ≠ user reality**。

## 触发条件

- 任何 release ship 前
- 任何 `hermes update` 后
- 任何 installer-related P1 涌现 (#59004 / #60384 模式)
- 任何 platform/*windows* / macos / linux issue 涌现

## Track 1: release_artifacts (5 项)

### 1.1 合并冲突标记 grep

```bash
find . -type f \( -name "*.py" -o -name "*.js" -o -name "*.ts" \) | \
  xargs grep -lE "^<<<<<<<|^=======$|^>>>>>>>" 2>/dev/null | \
  head -10
# exit code 必须为 0 (无任何匹配)
```

### 1.2 py_compile

```bash
find . -type f -name "*.py" | head -100 | \
  xargs python3 -m py_compile 2>&1 | head -10
# 0 error 即通过
```

### 1.3 JSON parse

```bash
find . -type f -name "*.json" | head -50 | \
  xargs -I {} python3 -c "import json; json.load(open('{}'))"
# 0 exception 即通过
```

### 1.4 import smoke test

```bash
find . -type d -name "hermes*" | head -3 | \
  xargs -I {} python3 -c "
import sys
sys.path.insert(0, '{}')
import hermes
print('OK')
" 2>&1
# 必须 import 成功
```

### 1.5 TODO/FIXME baseline drift

```bash
# 与上一个 release 对比
find . -type f \( -name "*.py" -o -name "*.js" -o -name "*.ts" \) | \
  xargs grep -cE "TODO|FIXME" 2>/dev/null | awk -F: '{sum+=$2} END {print sum}'
# 必须 ≤ baseline + 10%
```

## Track 2: fresh_install (5 项)

### 2.1 clean VM fresh install

```bash
# 在 clean VM / container 中
hermes --version
# 必须输出版本号
```

### 2.2 hermes update 跑通

```bash
hermes update
hermes --version
# 必须输出新版本号
```

### 2.3 gateway 启动 + 1 platform adapter round-trip

```bash
hermes gateway start &
sleep 5
hermes chat -q "ping" --platform telegram
# 必须收到响应
hermes gateway stop
```

### 2.4 config write/read 往返

```bash
hermes config set test_key "test_value"
hermes config get test_key
# 必须输出 "test_value"
hermes config unset test_key
```

### 2.5 log 检查 0 ERROR / 0 CRITICAL

```bash
tail -1000 ~/.hermes/logs/*.log | grep -E "ERROR|CRITICAL" | head -10
# 必须 0 行
```

## 自动化脚本

`scripts/installer-post-install-smoke.sh`:

```bash
#!/bin/bash
# 5+5 项一键跑
set -euo pipefail

TRACK="${1:-both}"  # track1 | track2 | both
SKIP_POST_INSTALL="${SKIP_POST_INSTALL:-false}"

if [[ "$TRACK" == "track1" || "$TRACK" == "both" ]]; then
  echo "=== Track 1: release_artifacts ==="
  # 1.1-1.5 必跑
  ...

  if [[ $? -ne 0 ]]; then
    echo "TRACK 1 FAILED — release 阻断"
    exit 1
  fi
fi

if [[ "$TRACK" == "track2" || "$TRACK" == "both" ]]; then
  if [[ "$SKIP_POST_INSTALL" == "true" ]]; then
    echo "TRACK 2 SKIPPED (emergency override) — 必须 48h 内补跑"
    exit 0
  fi

  echo "=== Track 2: fresh_install ==="
  # 2.1-2.5 必跑 (需 fresh VM / container)
  ...

  if [[ $? -ne 0 ]]; then
    echo "TRACK 2 FAILED — chief 升级"
    exit 1
  fi
fi

echo "ALL PASSED"
```

## 失败回退

- Track 1 任一 fail → release 阻断
- Track 2 任一 fail → release 阻断 + chief 升级
- emergency `--skip-post-install` flag → 必须 48h 内补跑
- Track 2 失败 3 次 → 冻结 release channel

## Pitfalls

### tick30 - Windows hermes_bootstrap.py SyntaxError 是 track 1.1 的命中案例

**触发**: #60384 报告 `import asyncio.coroutines` 在 line 205 → 实际是合并冲突标记未清理。

**修正**: track 1.1 grep 必须包含 import 行附近 — `<<<<<<<` 可能嵌入 import 上下文。

### tick30 - macOS .dmg 含 codesign 必须验证

**触发**: macOS installer 含 code signature,hermes_bootstrap.py 被恶意修改时 codesign 会失败。

**修正**: track 2.2 `hermes update` 后跑 `codesign -dv` 验证。

### tick30 - Linux .deb 依赖链断

**触发**: v0.18.1 ship 后 `pip install -U hermes-agent` 在某些 Ubuntu 版本失败。

**修正**: track 2.1 在 Ubuntu LTS 20.04 / 22.04 / 24.04 各跑一次。

## 验证清单

- [ ] scripts/installer-post-install-smoke.sh 集成进 hermes-agent CI
- [ ] 5+5 项任一 fail 阻断 release
- [ ] emergency flag 必 48h 补跑
- [ ] 30d 滑动窗口 recurrence counter 集成