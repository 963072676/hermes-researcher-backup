# SOUL 草案: qa / in-tick backup sentinel

**针对 issue**: tick11 沉淀 (P1 #49271) — v0.17.0 disk_cleanup_plugin 默认把 `cron/output/` 当 disposable, 会一次性删除本 tick 全部历史
**风险等级**: P1 (qa 必须守护所有 profile 的 cron output 完整性, 否则 baseline + 历史 digest 全失)
**confidence**: 0.85 (tick11 实证, 立即落地 in-tick backup pattern)
**触发源**: GH #49271 (disk_cleanup_plugin P1) + hermes-self-evolution-daily-digest tick11 pitfalls

## 当前文本(在 `~/.hermes/profiles/qa/SOUL.md` Cron Integrity 段第 X 行附近)
```text
- 监控 cron output 目录大小, 超 1GB 报警
```

## 建议替换为
```text
- 监控 cron output 目录大小, 超 1GB 报警
- **每次 cron tick 启动 Step 3 命中归一化之前必跑 in-tick backup**:
  ```bash
  mkdir -p /tmp/cron_output_backup_$(date -u +%F)
  cp -r ~/.hermes/cron/output/hermes-self-evolution-digest/ /tmp/cron_output_backup_$(date -u +%F)/ 2>&1
  ```
  退出 0 → 继续 tick; 退出非 0 → digest 头部标 `cron_output_backup: FAILED`, **不 abort tick**
  (disk 满, backup 失败不阻塞主流程, 但要可见)
- 若 GH #49271 未修 → **backup 必须 in-tick**, 不能等 v0.17.x patch (cleanup 触发后 baseline 全失)
- qa 每日额外跑: `du -sh /tmp/cron_output_backup_* | tail -5` 检查 backup 体积, 异常报警
- backup 保留策略: `/tmp/cron_output_backup_YYYY-MM-DD/` 保留 7 天后由系统 tmp 清理自动回收
```

## 替换理由
1. GH #49271 (disk_cleanup_plugin) 是真实风险, 一旦触发 baseline + 历史 digest 全失,
   后续 tick 无法 dedup, MCP search probe 也失效
2. 已有 in-tick backup pattern 沉淀 (tick11+ 验证 9 次 OK), 但只在 researcher self-evolution
   skill 文档里, qa profile 不知道
3. qa 是 5 profile 中 cron 监控的主责, 必须把这层护栏拉到 qa SOUL 里固化

## 风险与回退
- 风险: 文本变长; backup 占 `/tmp/` 空间 (单 tick ~5-50MB)
- 回退: `git checkout ~/.hermes/profiles/qa/SOUL.md`
- 验证: 若 GH #49271 在 v0.17.x 修 (添加 cleanup 白名单 / 标记 cron output non-disposable),
   可降级为单行 trust hermes
