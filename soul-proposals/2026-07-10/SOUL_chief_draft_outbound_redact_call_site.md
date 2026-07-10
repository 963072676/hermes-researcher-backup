# SOUL chief-agent 草案 — gateway outbound `redact_sensitive_text` call-site 闭环

> hermes-researcher tick32 (2026-07-10)
> source: GH #23810 (open since 2026-05-11, P1 security)
> priority: P1 (5+ token shapes leaked verbatim to Telegram/Discord/Slack)
> target: chief-agent
> action: chief 6h SLA: 评估 3 PR dedup + 亲自主导 P1 修复 close-out

## 触发

`#23810` 报告 `redact_sensitive_text()` 在 `agent/redact.py` 正确实现了 `sk-*` /
`ghp_*` / `github_pat_*` / Telegram `bot: ` / AWS / JWT / DB connect string 等
模式,正确应用到 log records (via `RedactingFormatter`) 和 tool output
(LLM context 入)。**但 outbound gateway message delivery** (`gateway/platforms/*.py`,
telegram 直接验证 + discord/slack 推断命中) **没调用**,导致:

- LLM 响应 / 用户 prompt 误回显 / 误读 credential 文件 / hallucinated token
- 全部 verbatim 发到 Telegram/Discord/Slack 用户
- `Secret redaction: ENABLED (tool output, logs, and chat responses are scrubbed before delivery)`
  日志启动 banner **骗人**,只有 logs 被 scrub,不是 bytes delivered

sibling to `#17691` (HERMES_REDACT_SECRETS default-OFF — 修了 default flag,
本 issue 修 call-site coverage)。

## root cause (loc 精确)

- `gateway/platforms/base.py`: no `redact_sensitive_text` call, no `from agent.redact` import
- `gateway/platforms/telegram.py`: no `redact_sensitive_text` call before
  `bot.send_message` / `application.bot.send_message`
- text transformation 限制到 `_escape_mdv2` / `_strip_mdv5` / `_wrap_markdown_tables`
  (formatting, NOT redaction)

contrast: `RedactingFormatter` 正确 wrap log handler output,所以同样 content
**写到 log 是 scrubbed 的**,但写到 Telegram 是原样的。

## 影响范围

对依赖 primary delivery = Telegram/Discord/Slack (v0.13 documented use case)
的部署,任何 token-shape string 进入 LLM response,**全部 verbatim delivered**,
gateway operator 信任 `Secret redaction: ENABLED` log line 但实际 security
posture 与现实不符。

## 修复路径

1. **(推荐)** 在 `gateway/platforms/base.py` canonical outbound delivery 处,
   wrap outbound text 通过 `agent.redact.redact_sensitive_text(text)` after
   Markdown formatting + before platform-specific send call:
   ```python
   text = redact_sensitive_text(text)
   await self._platform_send(chat_id, text)
   ```
2. **(alternative)** 如现有 call path 是 intentional,改启动 banner wording + 加
   `security.redact_outbound_chat: true` config flag 让 operator opt-in。

## chief 6h SLA 任务 (本草案)

- **PR dedup**:现有 PRs `#23821` (xxxigm) + `#23822` (LeonSGP43) 同时 2026-05-11 14:31Z,
  距今 60 天。继续等 24h SL + 5 PR 后仍未 merge → chief 升级评估 dedup。
- **call site audit**:chief 6h 内调用 `scripts/cross-platform-redact-audit.sh`(待立卡)
  扫 5 platform(feishu/discord/telegram/slack/whatsapp)+ 5 call site pattern,
  评估 gateway 全部 outbound path 是否统一调用。
- **default profile baseline**:`config.yaml` 加
  `security.redact_outbound_chat: true`(默认 ON),`deny_patterns` 加同 #23810
  list(`sk-*` / `ghp_*` / `github_pat_*` / `bot: ` / AWS / JWT / DB)。

## SOUL chief-agent 段落(草稿追加 §8.5)

```markdown
### §8.5 Outbound delivery redact 闭环 (新增, 2026-07-10 tick32 立卡)

PR dedup 6h SLA 扩展适用范围,从 silent-fail family (tick27) 扩展到
**gateway outbound redact call-site** family: 同 root cause 在多 PR 同时抢修时,
chief 必须 6h 内 dedup,选 1 个 primary,close 其他。window: 24h 内 ≥ 3 PRs 抢同一
redact call-site → 触发本段。fix-PR acceptance 必须附 5 platform cross-call-site
audit (base.py + 4 platform adapter),不能只 fix 一个 adapter。

audit trigger:
- `git log --since='7 days ago' --grep='redact_outbound'`
- 命中 ≥ 3 PRs → 6h SLA 启动
- 三变量评估: root cause 覆盖率 / cross-platform 影响 / diff 最小化

chief 必须亲自 triage,不 delegate dev-worker。
```

## verdict 倾向

**采纳:高**(sibling to 已 ship #17691。fix call-site 在技术上 straightforward;
chief dedup + cross-call-site audit 是 6h SLA 内可达工作量)
