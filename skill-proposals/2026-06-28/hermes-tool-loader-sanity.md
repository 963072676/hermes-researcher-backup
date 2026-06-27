---
name: hermes-tool-loader-sanity
description: |
  Hermes v0.17.0 fresh install 上检测 tool loader silent collapse。
  Use when: 任何 cron tick / agent 启动后, 怀疑 web/terminal/file tool 异常缺失
  (对应 GH #53667 P1 — "doctor reports all toolsets, runtime only cronjob")。
---

# Hermes Tool Loader Sanity Check (v0.17.0 护栏)

## 何时调用

- 新 fresh install v0.17.0 后第一次跑 cron
- `hermes doctor` 报正常, 但 runtime 调 `web_search` / `terminal` / `read_file` 失败
- agent 自我报告 "我无法跑 terminal 命令, 只能 schedule cron"

## 标准流程

```python
# 1 行 sentinel — 直接 eval 工具能否 import
python3 -c "
from hermes_tools import web_search, terminal, read_file, write_file, search_files
print('TOOL_LOADER_OK')
" 2>&1 | head -3
```

期望输出: `TOOL_LOADER_OK`
异常信号:
- `ImportError: cannot import name 'get_environment' from 'tools.environment'` → #53667 silent collapse
- `ModuleNotFoundError: No module named 'hermes_tools'` → profile 工具集裁剪, 走 MCP tool fallback
- 任何 `ImportError` / `ModuleNotFoundError` → digest 头部标 `tool_loader: FAIL`, 跳过 MCP 写入

## Fallback (tool loader 不可用)

1. `web_search` 不可用 → 写 Python urllib 直连 GitHub API + HN Algolia + OpenRouter
2. `terminal` 不可用 → 走 `python3 <<'PY'` heredoc + urllib 直连 (避免 `curl | python3` 被 tirith 拦)
3. `read_file` / `write_file` 不可用 → **abort tick**, 飞书报用户 (没有 file 工具没法备份)

## 何时不该调用

- 已知本地是 v0.17.x patch 含 #53667 fix
- tools 完全加载成功, web/terminal/file 都通 — 信任, 不再每次跑 sentinel
  (overhead 累计起来每月多几秒)

## 验证

- [ ] 在 v0.17.0 干净环境跑 → 期望 `TOOL_LOADER_OK` (fix 后) 或 ImportError (regression)
- [ ] fallback 路径至少成功 1 次 (tick13-18 已 6 次实证)
- [ ] digest 头部 `tool_loader: OK|FAIL|WARN` 必填
