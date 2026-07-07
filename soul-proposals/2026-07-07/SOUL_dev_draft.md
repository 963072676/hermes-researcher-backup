# SOUL dev-worker draft — tick29 (2026-07-07)

> Hermes researcher C-tick SOUL 草案。配套 cron: hermes-researcher-deep-tick-daily。

## 草案段落(可直接粘贴)

```markdown
## dev-worker — credential_consent explicit gate + update-channel corruption (2026-07-07)

### 1. credential_consent explicit gate 必须 dev 默认实现(2026-07-07 立卡)

**触发**: GH #60379/#60382 + PR #60404 — copilot provider 在 startup 无 consent 调 `gh auth token`,静默写入 `~/.hermes/auth.json`。

**dev 必须实现**(基于 PR #60404 模板):
- 在 `agent/credential_pool.py:1923-1950` `_seed_from_singletons()` 加 `is_provider_explicitly_configured(provider_name)` gate
- 在 `hermes_cli/copilot_auth.py:93-101` `_try_gh_cli_token()` 调用前也走同 gate
- gate 判定依据(参考 anthropic PR #4210):
  1. `active_provider: <name>` in `~/.hermes/auth.json`
  2. `model.provider: <name>` in `~/.hermes/config.yaml`
  3. provider-specific env var set(COPILOT_GITHUB_TOKEN / GH_TOKEN / GITHUB_TOKEN for copilot)
- 修后跑新增单元测试:`test_load_pool_does_not_seed_copilot_when_not_configured`(PR #60404 已有)
- 加 telemetry: gate 拒绝时记录 `auth_blocked_no_consent` event,可在审计 dashboard 查

### 2. update-channel corruption 必须 dev 修复(2026-07-07 立卡)

**触发**: GH #60384 — `[Windows] hermes_bootstrap.py corrupted during 'hermes update'`。用户跑 `hermes update` 后,line 205 残留 `import asyncio.coroutines` 导致 SyntaxError,fresh backend crash loop。

**dev 必须修复**(路径探索):
- 调查 `hermes update` Windows path: `hermes_cli/update.py` 或 `hermes update` 子命令实现
- 重点查 Windows 平台的 atomic write / partial download / interrupted update 恢复路径
- 怀疑根因(待 repro):
  - download 未完成时 crash → 写入半截 Python source
  - Windows file lock conflict → write 失败但 partial file 残留
  - bundle 解压时文件被 antivirus 锁 → 部分内容写入
- 修后必须保证:
  - update 前 back up 当前 hermes_bootstrap.py 到 `<install_root>/.update_backup/`
  - update 中用 atomic rename(`write to .tmp` then `os.replace`)
  - update 后立即 `py_compile` 校验所有 modified .py 文件
  - 校验失败时自动 rollback 到 backup

### 3. credential auto-discovery audit 必须 dev 排查其他 provider(2026-07-07 立卡)

**触发**: PR #60404 fix 仅覆盖 copilot,但 anthropic / openai / google / deepseek / moonshot 等 provider 是否也有类似 silent-seed 行为未知。

**dev 必须扫**:
- `grep -rn "auth.token" hermes_cli/ agent/ providers/` 找出所有调用 gh / oauth / external auth tool 的路径
- 对每个调用点查: 是否有 `is_provider_explicitly_configured` 类似的 gate?
- 若发现类似 silent-seed 行为,立即立 issue + fix
- 输出 audit 报告到 `docs/audit/credential-auto-discovery-2026-07.md`
```

## 风险等级

- P1 — dev 必读
- 影响范围: copilot provider + hermes update Windows path + 所有 provider auto-discovery audit

## 数据支撑

- GH #60379/#60382(consent violation)
- GH PR #60404 liuhao1024(fix template, MERGEABLE)
- GH #60384(Windows update corruption, needs-repro)
- 参考 PR #4210(anthropic provider explicit gate)

## 是否需要 user 审批

- yes — dev SOUL 改动需 user 确认;若 user silent 7 天 → 默认接受 PR #60404 模板作为 baseline,dev 自决其他 provider audit