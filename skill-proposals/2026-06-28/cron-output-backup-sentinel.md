---
name: cron-output-backup-sentinel
description: |
  Hermes cron output 目录 in-tick backup 护栏。Use when: 任何 cron tick 启动 Step 3
  命中归一化之前, 防 v0.17.0 disk_cleanup_plugin (GH #49271 P1) 误删 baseline + 历史
  digest。已沉淀在 tick11+ in-tick backup pattern (9 ticks 验证 OK)。
---

# Cron Output In-Tick Backup Sentinel

## 何时调用

**任何** `~/.hermes/cron/output/<job-name>/` 写入前必跑 (尤其是含 `dedup/seen_urls.json`
或 `digest/{date}.md` 的 self-evolution 类 cron)。

## 标准流程

```bash
# 1. 建 backup 目录 (用 UTC 日期避免时区漂移)
BACKUP_DIR="/tmp/cron_output_backup_$(date -u +%F)"
mkdir -p "$BACKUP_DIR"

# 2. 复制整个 cron output 目录
cp -r ~/.hermes/cron/output/hermes-self-evolution-digest/ "$BACKUP_DIR/" 2>&1

# 3. 检查退出码
if [ $? -eq 0 ]; then
  echo "BACKUP_OK: $BACKUP_DIR"
else
  echo "BACKUP_FAILED: $BACKUP_DIR" >&2
  # 注意: 不 abort tick, 只在 digest 头部标记
fi

# 4. (可选) 检查 backup 体积
du -sh "$BACKUP_DIR" | head -1
```

## 何时不该调用

- 不是 cron 模式 (interactive session, 没有 output 目录风险)
- 已经在 v0.17.x patch 含 #49271 fix (cleanup 白名单含 cron output)
- 磁盘已满 / `/tmp` 只读 — 跳过, 但飞书报警

## 为什么 in-tick 而不是 nightly

GH #49271 disk_cleanup_plugin 默认每天跑 (具体时间未文档化, 估 UTC 03:00 附近)。
一旦 cleanup 触发:
- `dedup/seen_urls.json` 丢 → 后续 tick 全部 first_seen 误判, baseline 重建成本高
- `digest/{date}.md` 历史丢 → 用户无审计轨迹
- MCP memory_id 仍 active, 但 search 时若依赖本地 hits jsonl 关联会断链

in-tick backup 的成本: 单 tick 5-50MB, `/tmp` 保留 7 天后系统清理, 总占用 < 350MB。

## 验证

- [ ] 跑 backup → `BACKUP_OK`
- [ ] `ls /tmp/cron_output_backup_*/dedup/seen_urls.json` 存在
- [ ] `du -sh /tmp/cron_output_backup_*` 体积合理 (< 100MB)
- [ ] digest 头部 `cron_output_backup: OK|FAILED` 必填
