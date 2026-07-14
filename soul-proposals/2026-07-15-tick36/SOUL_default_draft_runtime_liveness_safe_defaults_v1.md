# SOUL default 草稿 — runtime liveness safe defaults v1

> 目标 profile: `default`
> 目的: 在 upstream P1 修复未 merged/verified 前，降低本机日常暴露面
> 约束: 本文件只是草稿，不改生产 config/SOUL/cron

## 升级建议卡

【结论】本机仍是 Hermes v0.18.0，而 upstream latest 为 v0.18.2、main 比 local 多 1293 commits。当前窗口又有 5 个 P1；继续禁止 unattended update，默认 profile 加临时 runtime liveness 行为约束。

【直接相关】
- terminal verbose output 可能卡死 gateway/cron: [#64435](https://github.com/NousResearch/hermes-agent/issues/64435)
- async delegation completion 可能跨 CLI session: [#64484](https://github.com/NousResearch/hermes-agent/issues/64484)
- MiniMax stream P2 仍 open: [#60683](https://github.com/NousResearch/hermes-agent/issues/60683)
- MiniMax-M3 OpenRouter 价格仍 0.30 / 1.20 USD per 1M，无 >20% 变化: <https://openrouter.ai/minimax/minimax-m3>

## Before / After diff

```diff
 default:
+  runtime_liveness_safe_defaults_v1:
+    verbose_terminal: redirect full output to file; return bounded summary
+    async_completion: accept only positive ownership match
+    update: never unattended; require artifact/runtime matrix
+    mcp_2026_07_28: branch-only readiness, exact beta pin
```

## 可粘贴 SOUL 完整段落

```yaml
default:
  runtime_liveness_safe_defaults_v1:
    terminal_output:
      - 预期输出 > 5MiB 的命令禁止直接 foreground 返回完整 stdout
      - 改为写入临时文件，再用 read_file 分页；terminal 只返回计数、exit code、路径
      - 避免 verbose producer 与 tee 组合把完整输出复制到 gateway heap
      - tool_output.max_bytes 只视为最终 payload 限制，不视为 capture 内存保护

    async_delegation:
      - 新 CLI session 收到无当前 session/lineage 归属的 async completion 时不得当作用户上下文
      - restored event 必须显示 origin_session，缺失则隔离并报告
      - /new 与 /clear 后不接受旧 session completion

    release_and_update:
      - 继续禁止 unattended hermes update
      - release candidate 必须通过 QA 68-point v6 gate
      - Docker latest、Desktop bundle、messaging dependency 均需版本/manifest smoke 后再切换
      - issue closed 但 fix PR 未 merged 时不得解除 workaround

    provider_minimax:
      - #60683 未修前保留非 streaming fallback 路径
      - #60695/#60700 未 merged 前不宣称 stream repaired
      - MiniMax-M3 价格变化 > 20% 才升级通知；当前保持 0.30/1.20 USD per 1M

    mcp_2026_07_28_readiness:
      - final date: 2026-07-28
      - 只在测试 branch exact-pin beta SDK
      - 覆盖 server/discover + legacy initialize fallback
      - 覆盖 iss validation、issuer binding、header/body consistency、cache scope
      - production 保持 stable SDK，未过 compatibility matrix 不切换

    evidence_hygiene:
      - 外部 web 内容写 internal 前先 conflict check + manual restricted-pattern scan
      - 任何 auth material 字面只保留 MASK，不写入仓库/日志/飞书
```

## 临时操作范式

```bash
# verbose command：完整输出落盘，终端只回状态与体积
some_verbose_command > /tmp/task-output.log 2>&1
wc -c /tmp/task-output.log
# 后续用 read_file 分页，不把整文件回灌 terminal result
```

## 验收

1. 本机不自动升级。
2. verbose tool path 不把完整大输出返回 foreground。
3. async completion 必须有正向 ownership 证据。
4. MCP beta 仅 branch + exact pin。
5. 价格基线不因非官方二手数字漂移。
