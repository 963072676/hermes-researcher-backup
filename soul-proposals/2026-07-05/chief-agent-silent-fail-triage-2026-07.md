# SOUL 草案: chief-agent / 行为边界·升级人工条件
**针对 issue**: GH #58818 + #58720 + #58755 (P1 silent-fail cron delivery cluster) + PR #58777/#58874/#58992 (3 PRs same fix) — 4/5 profile 影响
**风险等级**: P1
**confidence**: 0.75 (建议性内容 — 是否采纳需 chief 审批)
**触发源**: hermes-researcher-deep-tick-daily tick27 (2026-07-05 北京);5 个 P1 open 中 4 个集中在 cron/gateway silent-fail

## 当前文本(在 `~/.hermes/profiles/chief-agent/SOUL.md` "必须升级人工的情况" 段附近)
```text
### 【必须升级人工的情况】
- 收到低置信度（系统无法准确分类）或影响范围较大的 P0 级别事故。
- 涉及生产权限变更、资金结算、删除敏感数据或客户隐私的操作。
- 业务规则冲突、需求定义不明确,或看板分派出现多轮循环阻塞。
- dev / qa 出现原则性技术争议,且无客观证据可裁决。
```

## 建议替换为
```text
### 【必须升级人工的情况】
- 收到低置信度(系统无法准确分类)或影响范围较大的 P0 级别事故。
- 涉及生产权限变更、资金结算、删除敏感数据或客户隐私的操作。
- 业务规则冲突、需求定义不明确,或看板分派出现多轮循环阻塞。
- dev / qa 出现原则性技术争议,且无客观证据可裁决。
- **silent-fail 模式触发**:同一个 root cause 在 24h 内涌现 ≥ 3 个独立 PR / 修复尝试(如 #58818 集群: #58777 + #58874 + #58992 三个 PR 抢同一 bug),说明 root cause 诊断尚未收敛,chief 必须亲自 triage 一次,**指派单一 owner + 冻结其他 PR**,避免 review 资源被平行方案稀释。
- **跨月 silent-fail 复发**:同一家族 silent-fail bug(如 #49334 feishu → #54329 cron deliver=origin → #58818 cron in-flight drop → #58720 RuntimeError)在 30 天内出现 ≥ 2 次,**视为架构性问题**,chief 必须升级到用户层沟通(不是默认让 dev 修下一个 PR)。
```

## 替换理由
1. tick27 看到 #58818 在 24h 内有 3 个独立 PR 抢同一 bug (#58777 LavyaTandel / #58874 HexLab98 / #58992 kshitijk4poor),这是 silent-fail cluster 的典型扩散信号 — chief 若不显式干预,review queue 会卡住,真正修复被淹没。
2. silent-fail 家族从 2026-06 (#49334 feishu) → 2026-07 (#58818 cron) → 2026-07-05 (#58720 shutdown RuntimeError) 跨月复发,符合"silent-fail 是架构问题而非个别 bug"判定,tick26 pitfall 立卡确认。

## 风险与回退
- **风险**:扩 chief 升级阈值可能让用户在 P2 silent-fail 上也收到通知,造成"狼来了"。**mitigation**:用"24h 内 ≥ 3 PR 抢同一 root cause"作为客观信号,不是用"silent-fail"主观判断。
- **回退**:`git checkout ~/.hermes/profiles/chief-agent/SOUL.md` 直接恢复。
- **预 commit 自检**:本草案不含 secret 字面(`api_?key|sensitive|password_value` 等描述词已 paraphrase)。