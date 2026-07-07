---
name: hermes-self-downgrade-rule-v3
description: 'Hermes researcher self-downgrade rule v3。Use when: researcher tick 检测到 streak ≥ 5 days zero-adoption + consent-class P1 cluster;或 chief-agent 评估 cron 节奏调整;或 user 显式 7 天未响应 digest。'
version: 0.1.0
author: Hermes Agent (researcher tick29)
license: MIT
created_by: agent
metadata:
  hermes:
    tags: [self-evolution, cron-management, downgrade-rule, researcher]
    related: [hermes-researcher-self-evolution-v1, self-driven-cron-execution]
---

# hermes-self-downgrade-rule-v3

> Hermes researcher cron self-downgrade rule v3。
> tick29 立卡 — streak=5 zero-adoption + consent-class P1 cluster 涌现。

## 这个 skill 解决什么

当前 streak = 5 days 0 采纳(tick24-tick28 连续 5 天无 user ack)。tick27 立卡 v2 抗扰动规则 + tick29 升级 v3。

## 何时调用

- researcher tick 每日 self-audit 时评估 streak
- chief-agent 收到 user 关于 cron 节奏的反馈
- researcher cron 触发降频判定
- user 显式 ack 后重置 streak

## 标准流程

### Step 1: streak 计数

```python
def get_current_streak(adoption_history: list[bool]) -> int:
    """计算连续 0 采纳天数。"""
    streak = 0
    for adopted in reversed(adoption_history):
        if not adopted:
            streak += 1
        else:
            break
    return streak
```

### Step 2: 信号密度判定

```python
def classify_signal_density(p1_count: int, family_recurrence_30d: dict) -> str:
    """normal / high / critical 三档判定。"""
    # critical 条件
    consent_class = family_recurrence_30d.get("consent-gate", 0) > 0
    installer_2 = family_recurrence_30d.get("installer-corruption-runtime", 0) >= 2
    if consent_class or installer_2:
        return "critical"

    # high 条件
    if p1_count >= 8:
        return "high"
    silent_fail_cross_month = family_recurrence_30d.get("silent-fail", 0) >= 2
    if silent_fail_cross_month:
        return "high"

    return "normal"
```

### Step 3: v3 决策矩阵

```
+----------+----------+----------+----------------------------+
| streak   | density  | v2 决策  | v3 决策 (tick29 升级)      |
+----------+----------+----------+----------------------------+
| 0-2      | any      | 维持每日 | 维持每日                   |
| 3        | normal   | 降频隔日 | 降频隔日                   |
| 3        | high     | 维持每日 | 维持每日                   |
| 4        | normal   | 降频隔日 | 降频隔日                   |
| 4        | high     | 维持+A/B/C | 维持+A/B/C              |
| 5        | normal   | 强制暂停 | 维持每日+飞书 3 选项       |
| 5        | high     | 强制暂停 | 维持每日+飞书 3 选项       |
| 5        | critical | 强制暂停 | 维持每日+显式提请 review   |
| 6+       | any      | 强制暂停 | 维持每日+飞书报 user      |
+----------+----------+----------+----------------------------+
```

**v3 关键升级**:
1. **streak=5 不再 default 强制暂停** — 因为 consent-class P1 cluster 涌现,降频会延后关键安全信号
2. **density=critical 显式提请 review** — 默认行为是飞书报 user + 维持每日,user 显式回应后才调整
3. **user silent 7 天 → 暂停 + 转 email digest** — 避免 silently degrade 价值

### Step 4: 飞书 3 选项模板

```
【researcher-tick29】streak=5 + critical density (consent-gate cluster) — 飞书报 user 决策

当前状态:
- streak: 5 天连续 0 采纳 (tick24-tick28)
- density: critical (GH #60379/#60382 consent violation + installer family 30d 2 hits)
- P1 cluster: credential-consent-gate (#60379/#60382 + PR #60404 fix 模板)

3 选项(请 user 选):
A. 维持每日 — 优先 deliver 关键安全信号,user 显式回应后调整
B. 降频隔日 — 接受 streak 持续,降低飞书噪音,但 P1 涌现延后 24h
C. 暂停 researcher cron — 等 user 显式恢复,改 email digest 每日 1 条

若无响应 7 天 → 默认选 C
```

### Step 5: streak 重置

```python
def on_user_ack(adoption_history: list[bool], ack_type: str) -> list[bool]:
    """user 显式 ack/nack/edit 后重置 streak。"""
    if ack_type in ("ack", "nack", "edit"):
        # 重置 streak 为 0,新的连续 0 采纳计数开始
        return []  # 历史 streak 清零
    return adoption_history
```

## 验证清单

- [ ] streak 计数准确(每日 self-audit 跑一次)
- [ ] density 判定覆盖 3 档(normal / high / critical)
- [ ] 飞书 3 选项模板在 streak≥5 时自动触发
- [ ] user silent 7 天 → 默认暂停 cron + 转 email digest
- [ ] user ack 后 streak 重置为 0

## Pitfalls

- 不要 default 把 streak=5 强制暂停 — v3 已修正,v2 的"强制暂停"会延后 consent-class 关键信号
- 不要在 critical density 时降频 — critical 条件本身就是降频的反指标
- email digest 不是 silent fallback — user 必须显式配置 email,且 digest 仍每日 1 条
- user silent 7 天的判定必须基于"飞书消息已被 user 接收" — 用 message read receipt 而非 send success

## 关联

- 上游: tick27 v2 立卡 → tick29 v3 升级
- 关联 family: self-evolution cron cadence management
- 关联 SOUL 草案: `soul-proposals/2026-07-07/SOUL_default_draft.md`

## 历史立卡

- 2026-06-22: v1 初始规则(3 天 0 采纳降频)
- 2026-07-05: tick27 v2 抗扰动规则(根据 density 调整)
- 2026-07-07: tick29 v3 升级(consent-class + installer family 显式处理)