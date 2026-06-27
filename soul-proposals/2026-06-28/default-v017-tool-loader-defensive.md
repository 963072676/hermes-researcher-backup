# SOUL 草案: default / v0.17.0 fresh install defensive check

**针对 issue**: GH #53667 P1 — v0.17.0 fresh install 上 tool loader 只加载 cronjob, doctor 报正常但运行时其他 tools 全掉 (`cannot import name 'get_environment' from 'tools.environment'`)
**风险等级**: P1 (default profile 跑 hermes-self-evolution-digest 完全依赖 web/file/terminal tool, 若 fresh install 触发就 0 产出)
**confidence**: 0.75 (issue 标 needs-repro, 描述清楚但尚未确认复现路径)
**触发源**: https://github.com/NousResearch/hermes-agent/issues/53667

## 当前文本(在 `~/.hermes/profiles/default/SOUL.md` Daily Setup 段第 X 行附近)
```text
- 假设 hermes 工具链完整可用, cron tick 直接调 web_search / terminal / file 即可
```

## 建议替换为
```text
- v0.17.0 上假设工具链完整可用, cron tick 直接调 web_search / terminal / file 即可
- **但每次 cron 启动先跑 1 行自检** (防 GH #53667 type silent collapse):
  ```bash
  python3 -c "from hermes_tools import web_search, terminal, read_file, write_file; print('TOOL_LOADER_OK')" 2>&1 | head -3
  ```
  若失败 → digest 头部标 `tool_loader: FAIL`, 跳过本 tick MCP 写入, 飞书报用户
- 已知 fallback: web_search 不可用 → 走 `curl https://api.github.com/...` + HN Algolia + OpenRouter
  直连, 不依赖 hermes web_search wrapper
- terminal 不可用 → 走 `python3` heredoc + urllib 直连, 不依赖 hermes terminal wrapper
```

## 替换理由
1. GH #53667 描述 "fresh install v0.17.0" 触发 tool loader collapse, doctor 报正常但 runtime
   只剩 cronjob tool, 这是 silent degradation (不报错, 只是 tools 全没了)
2. default profile 跑 hermes-self-evolution-digest 完全依赖 web/file/terminal 三件套,
   若全部 collapse → tick 静默失败, 没有 sentinel 报警
3. 1 行自检 + fallback 路径已沉淀在 tick13-18 的 pitfalls, 是经过验证的降级方案

## 风险与回退
- 风险: cron 启动多 1 行 (≈200ms); 误把临时 issue 当长期问题
- 回退: `git checkout ~/.hermes/profiles/default/SOUL.md`
- 验证: 若 #53667 在 v0.17.1 修, 可降级为 "trust hermes 工具链完整可用" 单行
