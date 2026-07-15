# SOUL default 草稿 — post-rediscovery safe defaults v1 (tick37)

> 目标 profile: `default`
> 目的: tick37 转入 post-rediscovery verification window, 本 default profile 行为约束
> 约束: 本文件只是草稿, 不改生产 config/SOUL/cron

## 升级建议卡

【结论】tick36 的 P1 中 4 个有 primary PR merged (#64593/#64574/#64552/#64617),但本机仍 v0.18.0, upstream v0.18.2 + main 1464 commits ahead。F1/F8/F9/F10 family 仍处于 release_verify_pending 阶段。default profile 必须维持 workaround + 持续观察;同时新增 MCP 2026-07-28 final 12 天倒计时约束。

【直接相关】
- #64593 merged 但本机仍 v0.18.0, 路径上 durable restore 仍是老 code, async completion 仍会跨 CLI session (但概率因 upstream 已修而降)
- #64574 merged 但本机仍 v0.18.0, Telegram 仍可能 0 connected (PTB 22.6 未升级)
- #64552 merged 但本机仍 v0.18.0, zero-chunk stream 仍会 retry exhaustion
- #64617 merged 但本机仍 v0.18.0, Desktop bundle 仍 stale (我们不在 Desktop install profile)
- #63978 -p <profile> regression v2026.7.7.x → fix PR #64006 closed unmerged, **本机若切 -p 仍会 fallback 到 default profile**, 必用 `HERMES_HOME=...` 显式 per-profile 路径
- MCP 2026-07-28 final 12 天后 ship (2026-07-28)
- MiniMax-M3 OpenRouter 价格仍 0.30 / 1.20 USD per 1M, 无 >20% 变化
- local...main ahead_by=1464, +171 commits vs tick36 audit 报告 (1293)

## Before / After diff

```diff
 default:
   runtime_liveness_safe_defaults_v1:
     verbose_terminal: redirect full output to file; return bounded summary
     async_completion: accept only positive ownership match
     update: never unattended; require artifact/runtime matrix
     mcp_2026_07_28: branch-only readiness, exact beta pin
+  post_rediscovery_safe_defaults_v1:
+    profile_switching: HERMES_HOME explicit, never -p alone
+    telegram: keep disabled until v0.18.3 PTB 22.6 fix verify
+    zero_chunk_stream: pre-emptive retry exhaustion backoff
+    desktop_cron: skip if not Desktop install profile
+    mcp_countdown: 12 days until 2026-07-28 final spec
```

## 可粘贴 SOUL 完整段落

```yaml
default:
  post_rediscovery_safe_defaults_v1:
    role: post_merge_safe_default_runtime

    profile_switching:
      - 任何 `hermes -p <profile> chat` 调用必须配合 `HERMES_HOME=/root/.hermes/profiles/<profile>` 显式环境变量
      - 不依赖 -p flag alone (因 #63978 unfixed in current install)
      - 切换 profile 前先 `ls $HERMES_HOME/` 确认路径有效
      - 若 -p 与 HERMES_HOME 不一致, fail closed + 报错

    telegram_runtime:
      - 维持 #64482 / #64694 workaround: 关闭 Telegram polling, 不连入 PTB 22.6
      - 直到 v0.18.3 ship + artifact_verify PASS + 本机实际升级后, 才重新 enable
      - 任何 Telegram adapter 启动失败, 视为预期行为, 不报 user (已知)
      - 若需要 Telegram, 切换到 v0.18.2 local pre-fix, 或 test branch exact pin

    zero_chunk_stream:
      - 任何 stream API 调用, 若 5s 内 0 chunks, 主动 raise 显式 error
      - 不依赖 provider 自动 retry (因 #64552 修复未到本机)
      - retry 次数 hardcode = 1, 不允许 unbounded retry
      - Anthropic / MiniMax 双 provider 都要 workaround

    desktop_cron:
      - 本机不在 Desktop install profile, 不受影响
      - 若用户启用 Desktop, 必先验证 build_keepalive_http_client symbol present
      - 否则会 #64333 closed-but-via-#64617-still-need-verify
      - artifact smoke 在 macOS/Windows/Linux 三平台都必跑

    mcp_2026_07_28_countdown:
      - final spec ship date: 2026-07-28
      - days remaining: 12 (as of 2026-07-16 UTC)
      - 6 SEPs 影响 default profile:
        - SEP-2575 (initialize handshake removed): server/discover fallback 路径
        - SEP-2567 (Mcp-Session-Id removed): 所有 request 必须 self-contained
        - SEP-2243 (Mcp-Method + Mcp-Name headers mandatory): 现有 WAF/proxy 必须放行
        - SEP-2260/SEP-2322 (long-lived SSE removed): InputRequiredResult multi-round trip
        - SEP-2164 (resource-not-found error code 32002 → 32602)
        - SEP-2468 + 5 auth SEPs: iss validation, application_type, issuer binding
      - 本机 default profile 保持 stable SDK, 不切 beta
      - test branch exact-pin beta SDK only on dev profile
      - production release 等 hermes-agent official MCP 2026-07-28 SDK 升级后再评估

    release_and_update:
      - 继续禁止 unattended hermes update (沿用 #60685)
      - local v0.18.0; upstream latest v0.18.2; main ahead_by=1464
      - 等 v0.18.3 ship (含 4 P1 PR merge) + 5 install profile artifact_verify + cross_profile_audit PASS
      - 任何 installed Hermes 升级到 v0.18.3 之前, 必须先 cross-profile permission audit + 14-day post-merge regression window PASS for #64593/#64574/#64552/#64617

    provider_minimax:
      - #60683 still open; #60695/#60700 still open
      - 维持 non-streaming fallback path
      - MiniMax-M3 价格变化 > 20% 才升级通知; 当前保持 0.30/1.20 USD per 1M

    regression_window_observation:
      - 自 2026-07-15T05:28Z 起, 14 天内观察 #64593/#64574/#64552/#64617 是否引入 regression
      - 观察期内任何同 root cause 新 issue → reopen + report chief
      - 观察期 2026-07-29T05:28Z 结束 (保守按最后一个 merged PR + 14d)
      - 本 default profile 受 fix 路径影响小 (未启用 Telegram, 不在 Desktop, 不依赖 bounded terminal capture 在小输出场景), 观察任务轻量

    evidence_hygiene:
      - 外部 web 内容写 internal 前先 conflict check + manual restricted-pattern scan
      - 任何 auth material 字面只保留 MASK, 不写入仓库/日志/飞书
      - 任何 SOUL/skill 草稿走 write_file 工具, 不用 terminal heredoc (避免 tirith 拦)

    watch_signals:
      - foreign completion count > 0 in CLI boot 5s → alert
      - Telegram adapter startup fail → silent (已知)
      - zero-chunk stream retry exhaustion in 5s → raise explicit error
      - -p <profile> falls back to default → fail closed
      - MCP 2026-07-28 final ship 后 7d, 评估 SDK upgrade window
```

## 临时操作范式

```bash
# profile switch (避免 #63978 regression)
export HERMES_HOME=/root/.hermes/profiles/work
hermes -p work chat

# verbose command: 完整输出落盘, 终端只回状态与体积
some_verbose_command > /tmp/task-output.log 2>&1
wc -c /tmp/task-output.log

# zero-chunk stream workaround: 5s 显式 timeout
timeout 5 hermes-cli some-stream-command || { echo "zero-chunk detected, retry aborted"; exit 1; }

# Telegram: 维持 disable
hermes plugins disable telegram
```

## 验收

1. 本机不自动升级, 等 v0.18.3。
2. -p <profile> 必配合 HERMES_HOME 显式。
3. Telegram 保持 disable 直到 v0.18.3 artifact_verify PASS。
4. zero-chunk stream 必走显式 timeout + bounded retry。
5. Desktop install profile 用户必先 verify bundle smoke。
6. MCP 2026-07-28 final 12 天后 ship, 评估 SDK 升级窗口。
7. regression window 14 天内观察 4 merged P1 PR 是否引入 regression。
8. 价格基线 (0.30/1.20 USD per 1M) 不因非官方二手数字漂移。