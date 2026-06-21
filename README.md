# Hermes Researcher Self-Evolution Backup

**Owner**: `963072676/hermes-researcher-backup`
**Source Profile**: `~/.hermes/profiles/researcher/`
**Backup Strategy**: real-time critical commits + daily 23:50 UTC aggregate push

## 目录结构

```
.
├── README.md                          # 本文件
├── config.yaml                        # researcher profile 配置快照(脱敏)
├── soul-drafts/                       # SOUL.md 演进历史
│   ├── SOUL-v1-20260612.md            # 初始版
│   └── SOUL-v2-20260621.md            # 自进化版(C 档升级后)
├── skills/                            # skill 草稿与版本
│   ├── researcher-propose-v1.md
│   ├── researcher-scan-v1.md
│   └── hermes-researcher-self-evolution-v1.md  # 新增:自进化 skill
├── cron-output/                       # 每日 cron tick 产出(完整历史)
│   ├── digest/                        # 摘要报告
│   └── hits/                          # 原始命中 JSONL
├── memory-snapshots/                  # MCP memory_propose_write 内容备份
│   └── YYYY-MM-DD/
│       └── proposals.jsonl
├── soul-proposals/                    # 自动产出的 SOUL 草稿(等你 review)
│   └── YYYY-MM-DD/
│       └── <target-profile>-<section>.md
├── skill-proposals/                   # 自动产出的新 skill 草稿
│   └── YYYY-MM-DD/
│       └── <skill-name>.md
└── docs/
    ├── weekly/                        # 周报(每周一 00:10 UTC 自动生成)
    │   └── YYYY-Www.md
    └── audit/                         # 自我审计:昨日建议采纳率
        └── YYYY-MM-DD.md
```

## 推送策略

| 触发 | 推送内容 | 频率 |
|---|---|---|
| 关键变更产生 | SOUL 草稿 / 新 skill 草稿 / config 变更 | 实时(< 5 min) |
| 每日 tick 完成 | cron-output + memory-snapshots 当天文件 | 每日 23:50 UTC |
| 每周一 00:10 | docs/weekly/YYYY-Www.md | 周一 |

## 与上游 GitHub 凭证配合

- 推送用 `gh auth` (已配 963072676 + repo scope)
- 不在仓库内保存任何 token
- repo public,**只**放 SOUL / skill / cron 摘要 / 周报,**绝不**包含真 secret

## 关联 Profile

- 上游: `hermes-self-evolution-daily-digest` (default profile)
- 同级: chief-agent / pm-orchestrator / dev-worker / qa-worker / default
- 消费: chief-agent-daily-digest(读 docs/weekly + soul-proposals)

## Backup Driver

由 cron `hermes-researcher-backup-pusher` 驱动,详见 `~/.hermes/profiles/researcher/cron/hermes-researcher-backup-pusher.md`(待生成)。
