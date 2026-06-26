# SOUL 草案: dev-worker / memory-privacy-redact
**针对 arxiv**: 2606.26627 (2026-06-25) — Agents That Know Too Much: A Data-Centric Survey of Privacy in LLM Agents
**风险等级**: P1
**confidence**: 0.81
**触发源**:
- https://arxiv.org/abs/2606.26627 (2026-06-25, cs.MA / cs.CR)
- 续接 tick15 (2026-06-24) default-redact-followup.md 提案
- 关联 memory_service `sensitive_content_detected` 自动 reject (tick8 Pydantic validator)

## 当前文本(在 `~/.hermes/profiles/dev-worker/SOUL.md` "###【可做事项】" 段 "###【不可做事项】" 段,约 40~45 行)
```text
- **禁止**在未经 chief-agent 审批或 qa-worker 验证前擅自合并代码。
- **禁止**执行任何生产重启、服务器配置修改或生产数据库写操作(只读诊断可以)。
```

## 建议替换为
```text
- **禁止**在未经 chief-agent 审批或 qa-worker 验证前擅自合并代码。
- **禁止**执行任何生产重启、服务器配置修改或生产数据库写操作(只读诊断可以)。
- **隐私数据自动 redact (2026-06-27 升级, ref arxiv 2606.26627 + tick15)**:
  dev-worker 在以下场景必须先 redact 再 commit / push / write_file / propose_write:
  1. **API key 字面**:`sk-...`, `gho_...`, `ghp_...`, `xai-...`, `AKIA...` 等
     → 必须替换为 `***MASK***` 或 `<REDACTED-PROVIDER>`
  2. **Bearer / Authorization header 字面**:`Bearer eyJhbGc...` → `Bearer ***MASK***`
  3. **DB connection string 字面**:`PGPASSWORD='xxx'`, `mongodb://user:pass@...`
     → 改 placeholder,绝不写真密码
  4. **Webhook URL with token**:`https://open.feishu.cn/open-apis/.../<token>`
     → 拆 host + path,把 token 段替换为 `<TOKEN>`
  5. **PII 字面**:邮箱 / 手机号 / 身份证 / 银行卡 → 走 privacy hash (sha256 + 后 4 位)
  - **执行机制**:
    a. `git diff --cached` 阶段自动跑 `~/.hermes/scripts/redact_pre_commit.py` 扫,
       命中即 abort commit
    b. `write_file` / `patch` 工具调用前,在 agent context 内已强制 redact(token pattern 匹配)
    c. `mcp_project_memory_memory_propose_write` 走 memory_service 自动 validator
       (已有 `sensitive_content_detected` 拒绝逻辑,见 tick8)
  - **dev-worker 的红线**: 即使为了"复现 bug"也必须脱敏,**不写 secret 字面 = 不破例**。
```

## 替换理由
- arxiv 2606.26627 综述:L agent memory 是攻击者最爱的目标,因为 memory 一旦 persist,
  跨 session 跨 user 都能读出 secret。常见攻击: prompt injection → agent log sensitive
  content → memory ingest → 后续 session search 到。
- 本环境已有 3 层保护:
  (1) memory_service Pydantic validator (tick8 沉淀)
  (2) researcher SOUL 的 data-flow 净化层 (2026-06-22 redact followup)
  (3) cross-profile soft guard (write_file 不让写到其他 profile)
- **但 dev-worker 是最常接触真实 secret 的角色**(写代码 + 调 API + 跑 production deploy),
  必须把 redact 从"建议"升为"硬规则 + 自动 pre-commit hook"。

## 风险与回退
- 风险: 自动 redact 可能误伤合法字面(例如 README 里要展示 `Bearer *** 测试 token)。
  修正: pre-commit hook 提供 `--allow-pattern` 选项,具体名单由 chief 审批。
- 回退: `git checkout ~/.hermes/profiles/dev-worker/SOUL.md` 还原。
- 待 dev-worker 角色 commit 后激活。

## 升级影响
| Profile | 升级优先级 | 备注 |
|---|---|---|
| dev-worker | **HIGH** | 本 SOUL 直接受益,获得自动 redact hook |
| chief-agent | MEDIUM | 例外审批 `--allow-pattern` 走 chief |
| qa-worker | **HIGH** | 必须测 dev 的 redact hook 是否真生效(可用 false-positive fixture) |
| pm-orchestrator | LOW | 不直接相关 |
| default | MEDIUM | 跨 profile 的 write_file gate 已部分覆盖 |