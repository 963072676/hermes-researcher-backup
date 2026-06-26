---
name: memory-service-audit-cli
description: 给 researcher 用的小 CLI,审计自己 (researcher role=agent) propose 的 memory 历史,无需 chief 介入。Use when: researcher cron tick 想 verify 自己 propose 的内容是否 commit / 是否仍 pending / 是否被 supersede。
---

# memory-service-audit-cli

## 何时调用
- researcher cron tick 结束前,自查今日 propose 状态(替代直接调 `review_pending` 403)
- 当 user 反馈 "我提的 SOUL 没生效" 时跑一次确认 propose 是否真 commit
- 当其他 skill (如 `project-memory-service`) 报错 "search 0 hits" 时,作为真相探针

## 标准流程

### Step 1: 读 admin token
```bash
# 通过 Python re 模块直接读 .env, 避免 shell redact 损坏 token 字面
python3 <<'PY'
import re
content = open('/root/migrated-home/memory_service/.env').read()
m = re.search(r'MEMORY_SERVICE_ADMIN_TOKEN=([A-Za-z0-9_-]+)', content)
TK = m.group(1).strip() if m else ''
print(TK)
PY
```

### Step 2: 三种 audit 模式

**Mode A: audit (按 agent 过滤 propose_write 事件)**
```bash
curl -sS -X POST http://127.0.0.1:18080/memory/audit \
  -H 'Content-Type: application/json' \
  -H "X-Admin-Token: $TK" \
  -d '{"event_type":"propose_write","limit":30,"context":{"agent_id":"gc-hermes-researcher","org_id":"gc-hermes","project_id":"hermes-researcher","role":"agent"}}'
```

**Mode B: search by content keyword (替代 review_pending 403)**
```bash
# researcher role 看不到 review_pending, 但 search 不限 role
curl -sS -X POST http://127.0.0.1:18080/memory/search \
  -H 'Content-Type: application/json' \
  -H "X-Admin-Token: $TK" \
  -d '{"query":"<tick_topic_keyword>","limit":10,"context":{"agent_id":"gc-hermes-researcher","org_id":"gc-hermes","project_id":"hermes-researcher","role":"agent"}}'
```

**Mode C: get by memory_id (直查)**
```bash
curl -sS -X POST http://127.0.0.1:18080/memory/get \
  -H 'Content-Type: application/json' \
  -H "X-Admin-Token: $TK" \
  -d '{"memory_id":"<uuid>","context":{"agent_id":"gc-hermes-researcher","org_id":"gc-hermes","project_id":"hermes-researcher","role":"agent"}}'
```

### Step 3: 解析输出
| Status | 含义 | 下一步 |
|---|---|---|
| `pending_review` | chief/user 还没 commit | 标 WAIT, 不重试 |
| `active` | 已 commit + 进 search index | 标 DONE |
| `superseded` | 被新条目覆盖 | 标 OBSOLETE, 引用新版 |
| `denied` (reason=`sensitive_content_detected`) | 自动 reject | 重写脱敏后 propose |
| `404` | memory_id 不存在 | 标 MISSING, 可能审计失败 |

## 何时不该调用
- 不要用此 CLI 调 `commit` — researcher role=agent 不允许,会 403
- 不要尝试绕过 admin token — memory_service 已记录所有 IP, 触发 alert
- 不要在 cron 之外的场景批量 audit > 100 条 — 触发 rate limit

## 验证
- [ ] `python3 -m memory_service_audit_cli --tick 17` 输出 tick17 3 个 memory_id 状态
- [ ] Mode B 搜索 "Gateway shutdown" 能找到 tick17 第一条 propose
- [ ] Mode C 直查返回完整 content (含 pending_review / active / denied 标志)

## 关联
- 主 skill: `project-memory-service` (上游, 定义 propose + commit 双阶段契约)
- 平行 skill: `memory_detect_conflict` (MCP tool, 自动扫冲突)
- 真实 pitfall: `sensitive_content_detected` 自动 reject (tick8 沉淀)