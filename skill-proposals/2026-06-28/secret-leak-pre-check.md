---
name: secret-leak-pre-check
description: |
  Hermes terminal 工具调用前的 secret 自检 skill。Use when: 任何在 gateway session /
  v0.17.0 main 上跑 terminal 命令前, 防止 AUXILIARY_*_API_KEY / GATEWAY_RELAY_SECRET
  泄漏到 child process。触发源: GH #53715 P1 security PR (open 2026-06-27)。
---

# Secret Leak Pre-Check (v0.17.0 临时护栏)

## 何时调用

每次 cron tick / agent run 准备调 `terminal` 工具前, 跑一次自检。
**触发场景**:
- 在 gateway session 内 (有 side-LLM, curator, vision, embedding 辅助)
- v0.17.0 + `hermes update` 报本地未到 v0.17.x patch 含 #53715 fix
- 任何 docker run / SSH / bash -c 子进程可能 fork

## 标准流程

```bash
# 1. 列出当前 process tree 中可能被泄漏的 secret
env | grep -iE '(AUXILIARY_[A-Z]+_API_KEY|GATEWAY_RELAY_SECRET|.*_API_KEY|.*_SECRET|.*_TOKEN)' | sed 's/=.*/=<REDACTED>/' | head -10

# 2. 若是 gateway session, 额外检查
python3 -c "
import os
leaks = [k for k in os.environ if k.startswith(('AUXILIARY_', 'GATEWAY_RELAY_'))]
print('LEAK_RISK:', leaks if leaks else 'NONE')
"

# 3. 必要时用 env -i 启动纯净 subshell
env -i HOME=$HOME PATH=$PATH bash -c 'echo "clean subshell, no AUXILIARY_*_API_KEY inherited"'
```

## 何时不该调用

- 已经确认本地是 v0.17.x patch 含 #53715 fix (查 `hermes --version` + commit log)
- 单进程 stateless 工具调用 (read_file / web_search) 不涉及 subprocess fork
- 已经用 `code_execution_tool` (它自己有 `_SECRET_SUBSTRINGS` substring match,
  GH #53715 描述它已正确)

## 验证

- [ ] 跑自检 → 期望 `LEAK_RISK: NONE` (干净) 或具体 key 列表
- [ ] `env -i bash -c 'env | grep AUX'` 期望无输出
- [ ] PR #53715 merge 后, 可在本 skill 头部加 `deprecation_note: safe_after_v0.17.x`
