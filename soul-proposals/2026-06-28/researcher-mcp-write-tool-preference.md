# SOUL 草案: researcher / MCP write tool preference (cron session fallback)

**针对 issue**: tick12 + tick18 沉淀 — `mcp_writer.py` Python urllib 路径在 researcher profile 下 payload schema 必须 8 字段, 但更稳的路径是直接 MCP tool (`mcp_project_memory_memory_propose_write`)
**风险等级**: P2 (researcher cron 写入可靠性, 不阻塞主流程但影响 8/12 个 tick 的 MCP write 成功率)
**confidence**: 0.85 (实证沉淀, tick12-18 全部验证)
**触发源**: `~/.hermes/skills/hermes-self-evolution-daily-digest` Pitfalls 段 tick12 + tick11-researcher

## 当前文本(在 `~/.hermes/profiles/researcher/SOUL.md` MCP 写入段第 X 行附近)
```text
- cron session 工具集裁剪, 走 Python urllib fallback (scripts/mcp_writer.py)
```

## 建议替换为
```text
- cron session 工具集裁剪, **优先 MCP tool** (`mcp_project_memory_memory_propose_write`):
  1. 先用 `skill_view` 或 `terminal which` 探针确认 MCP tool 在 cron session 可用
  2. 若可用 → 直接 `mcp_project_memory_memory_propose_write`, auto-injects context, 无需手填
  3. 若不可用 → 走 `scripts/mcp_writer.py` Python urllib fallback
- Python urllib 路径必须自带完整 8 字段: `content`(string) / `memory_type` / `reason` /
  `suggested_scope`(enum 字面, 不是 "private:agent_id") / `source` / `source_type` /
  `confidence` / `requires_review`, 加 `context` 顶层 dict (org_id/project_id/agent_id/role=agent)
- `role=agent` **禁止调 commit** (403 privileged_role_required), 等 chief/user 批量 commit
- token 读取统一用 `line.split("=", 1)` 模式, 不用 re.search / heredoc 命令替换 (tirith redact)
```

## 替换理由
1. tick11-researcher 实测: `scripts/mcp_writer.py` 在 researcher profile 下走 `propose_and_commit`
   会在 commit 步骤 crash (urllib HTTPError 403 未捕获), 而 MCP tool 只走 propose 不 crash
2. tick18 5 个 Python urllib 脚本虽然成功, 但每个都要手填 context + 8 字段 schema, 易出错
3. MCP tool 默认只 propose + 实际 researcher role 不能 commit, 与脚本能力上完全对齐,
   但脚本路径更 fragile

## 风险与回退
- 风险: 文本变长; MCP tool 偶尔被 cron 工具集裁剪掉 (tick16 实测) → fallback 路径必填
- 回退: `git checkout ~/.hermes/profiles/researcher/SOUL.md`
- 验证: 若 MCP tool 在 cron 100% 可用, 可删 fallback 段
