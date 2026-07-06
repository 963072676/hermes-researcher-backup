---
name: hermes-cross-platform-p1-cluster-triage
description: '跨 platform P1 cluster 诊断 + PR dedup + owner 单一化。当用户提到"cross-platform P1"、"多 platform 同 root cause"、"PR dedup"或 researcher/chief/pm tick 报 3+ PR 抢同一 root cause 时使用。本 skill 输出 cluster 判定 + PR owner dedup 模板 + 24h triage SLA。'
version: 1.0.0
author: Hermes Agent (researcher profile)
license: MIT
created_by: agent
platforms: [linux, macos]
metadata:
  hermes:
    tags: [triage, pr-dedup, cross-platform, chief, pm]
    related: [hermes-researcher-self-evolution-v1, hermes-self-evolution-daily-digest, pr-duplicate-fix-detector (tick27)]
---

# hermes-cross-platform-p1-cluster-triage (tick28+ 立卡)

## 触发条件
- 用户 / cron 提到"cross-platform P1 cluster" / "multi-platform 同 root cause"
- researcher / chief tick 报 ≥ 1 P1 issue 影响 2+ platform
- 24h 内 ≥ 3 PR 抢修同一 root cause(沿用 tick27 立卡,本 tick 升级为 cluster triage)
- 同 component P2/P3 cluster ≥ 3 个(sweeper marker)

## 解决什么
tick28 观察到 #59607 (P1 cross-platform replay-safety) + #59614 (P1 Telegram polling hang) + #51646 (P1 cross-platform gateway memory) — **3 个 P1 都是 cross-platform 影响**,且 #59607 已有 #59640 PR fix candidate。
tick27 立卡 `pr-duplicate-fix-detector` 处理 "24h 内 ≥ 3 PR 抢同 root cause",但 **没处理跨 platform 同 root cause**。本 skill 扩展为 cluster triage,加 cross-platform 维度。

## 标准流程 (7 步)

### Step 1: cluster 判定
```python
# 用 GitHub REST API 收集 issue + PR
import urllib.request, json
repo = "NousResearch/hermes-agent"
issues = json.loads(urllib.request.urlopen(
    f"https://api.github.com/repos/{repo}/issues?state=all&since=2026-07-04T00:00:00Z&per_page=100",
    headers={"User-Agent": "tick28-cron"}
).read())
# 提取 label 包含 cross-platform 平台的 issue
cross_platform_indicators = ['platform/telegram', 'platform/discord', 'platform/feishu', 'platform/qqbot', 'platform/slack', 'platform/windows', 'platform/macos']
for i in issues:
    labels = [l['name'] for l in i.get('labels', [])]
    platforms = [l for l in labels if l in cross_platform_indicators]
    if len(platforms) >= 2 and 'P1' in labels:
        print(f"  #{i['number']} cross-platform P1: {platforms} - {i['title'][:60]}")
```

### Step 2: root cause 提取
对每个 cluster P1,读 body 提取 root cause:
- #59607: dangerous-confirmation 历史在 host reboot 后 re-execute → **replay-safety gap**
- #59614: Telegram `_handle_polling_network_error` start_polling 无 timeout wrapper → **3-tier recovery hang**
- #51646: hermes_state.py INSERT omit `active` column → **SQLite DEFAULT 在 schema drift 时 NULL**

### Step 3: PR 关联
```bash
# 用 gh CLI 列 PR linked 到 issue
gh pr list --search "linked:issue:#N" --state all --json number,title,author,createdAt
```
期望: 每个 P1 有 1-3 个 PR candidate,标记 status(open / merged / closed)

### Step 4: 24h dedup
对每个 cluster:
- 若 ≥ 3 PR 抢同一 root cause → chief 必须 6h 内 dedup(沿用 tick27)
- 选 owner 标准: root cause 覆盖率 / 改动最小化 / cross-subsystem 影响
- 其他 PR 关闭模板: "Closing in favor of #N. Root cause covered by primary PR."

### Step 5: cross-platform verify
对每个 PR fix,验证是否覆盖所有受影响的 platform:
- #59607 fix #59640: 覆盖 Telegram + Windows 文本 confirmation 历史 — 是否覆盖 cron delivery 通道?
- #51646 fix(候选): 验证 `active=1` INSERT 覆盖所有 4 platform
- #59614 fix #59721 wait_for: 仅 Telegram,但 sweeper:risk-message-delivery 暗示 cross-platform

### Step 6: 飞书报 cluster status
写到 `oc_c653562b`:
```
🚨 Cross-platform P1 cluster (tick28)
- #59607 replay-safety: Telegram + Windows + cron delivery (PR #59640 candidate, 24h dedup needed)
- #59614 polling hang: Telegram only (PR #59721 wait_for merged)
- #51646 memory loss: Discord + Feishu + Dashboard (no PR yet)
→ chief 6h 内 dedup;pm 协调 sweeper:risk-replay-safety + cross-platform-state 责任分配
```

### Step 7: 24h SLA
- 6h: chief 完成 PR dedup(若 ≥ 3)
- 12h: pm 分配 sweeper marker 责任
- 24h: dev 出 cross-platform test 矩阵(沿用 SOUL dev 草案)
- 48h: default profile baseline verify(沿用 SOUL default 草案)

## Pitfalls
- **cross-platform ≠ multi-platform**: 必须读 issue body 确认 root cause 是否真正跨 platform,不要只看 label
- **PR dedup ≠ PR close**: chief 必须给被 close 的 PR owner 回复 "感谢 + 解释 primary 选择",不能冷 close
- **cluster 判定不能只看 label**: #51646 label 是 Discord + Feishu + Dashboard 三个 platform,但 root cause 是 SQLite schema drift,影响所有 platform
- **必须 verify PR 是否真的跨 platform fix**: 单 platform fix 不能标 "cross-platform fix",否则回归时跨 platform 漏

## 验证清单
- [ ] cluster 判定基于 root cause,不是基于 platform label
- [ ] PR dedup 在 6h 内完成,owner 选定有依据
- [ ] cross-platform verify 报告每 PR 是否真覆盖所有受影响 platform
- [ ] 飞书 cluster status 24h 内发出
- [ ] sweeper marker 责任分配到具体 profile
