# SOUL 草案: dev / Security Boundary (terminal env leak)

**针对 issue**: GH #53715 P1 — `terminal` tool subprocess leaks `AUXILIARY_*_API_KEY` + `GATEWAY_RELAY_SECRET` to child processes
**风险等级**: P1 (security boundary — 任何跑在 gateway / side-LLM 路径下的 dev 任务都受影响)
**confidence**: 0.85 (issue open 2026-06-27, PR 已 open, 修复待 review; 描述清楚 repro)
**触发源**: https://github.com/NousResearch/hermes-agent/pull/53715 + https://api.github.com/repos/NousResearch/hermes-agent/issues?since=2026-06-25

## 当前文本(在 `~/.hermes/profiles/dev/SOUL.md` Security Boundary 段第 X 行附近)
```text
- terminal 工具输出统一过 redact, 但 child process env 隔离是 hermes 内部责任, dev 无需关注
```

## 建议替换为
```text
- terminal 工具输出统一过 redact, 但 **child process env 隔离是 dev 的责任**:
  - v0.17.0 之前 terminal subprocess 仍可能泄漏 `AUXILIARY_*_API_KEY` / `GATEWAY_RELAY_SECRET`
    (GH #53715, code_execution_tool 已修, terminal 待 PR #53715 merge)
  - dev 跑任何命令前先 `env | grep -iE '(api_?key|secret|token)' | head -5` 自检
  - 涉及 docker run / SSH / bash -c 时显式 unset 这些前缀, 或用 `env -i` 启动纯净 subshell
- 已知修复路径: PR #53715 在 `local.py` 加 `_is_hermes_internal_secret(name)` 子串匹配 helper,
  `_make_run_env` + `_sanitize_subprocess_env` 切换到新 helper, 3 文件 +110/-3
```

## 替换理由
1. GH #53715 已确认 v0.17.0 main 上 `terminal` 工具的 env blocklist 是 name-based exact match,
   `AUXILIARY_*_API_KEY` 是动态注入, blocklist 抓不到, 直接传给 child process
2. researcher tick 自身就是 "terminal run + bash subprocess", 极易受影响
3. dev 是 5 profile 中 terminal 使用频率最高的, 必须主动防御

## 风险与回退
- 风险: 文本变长, dev 启动 SOUL 时 token cost 微增; 误把临时修复当永久护栏
- 回退: `git checkout ~/.hermes/profiles/dev/SOUL.md`
- 验证: PR #53715 merge → 本 SOUL 段可降级为 "trust hermes 0.17.x patch" 单行
