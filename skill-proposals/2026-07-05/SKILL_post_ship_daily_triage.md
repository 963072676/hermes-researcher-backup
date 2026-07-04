---
name: hermes-post-ship-daily-triage
description: Hermes Agent 任意 version ship 之后的 daily rolling 72h coverage triage skill。Use when: pm / chief 每日触发(via cron 03:00 UTC)扫过去 72h 开 issue/PR vs release body 主张,识别 silent regression cluster 与 sweeper:risk-* marker 责任分配。配合 chief acceptance verification + dev ship guard + qa regression harness 三方 workflow。
---

# hermes-post-ship-daily-triage

## 何时调用

- pm profile 每日 03:00 UTC(via cron `hermes-pm-post-ship-triage-daily`)
- chief profile 在每日 06:00 UTC 跑 cross-profile review
- researcher profile 在每日 deep tick(digest 路径)交叉引用其 output

## 标准流程

### Step 1: 拉过去 72h open items

```bash
# GitHub API since filter, 3 pages of 100 items
curl -sL "https://api.github.com/repos/NousResearch/hermes-agent/issues?state=open&since=${72_HOURS_AGO}&per_page=100&page=1"
```

### Step 2: cluster detection

```python
def cluster_recent_issues(items: list[dict]) -> list[dict]:
    """
    按 component label + priority(P0/P1/P2) + sweeper marker 三维度聚类
    """
    clusters = defaultdict(list)
    for item in items:
        labels = {l["name"] for l in item.get("labels", [])}
        component = next((l["name"] for l in labels if l.startswith("comp/")), "comp/other")
        priority = next((l["name"] for l in labels if l in ["P0", "P1", "P2", "P3"]), "P-nil")
        sweeper = next((l["name"] for l in labels if l.startswith("sweeper:")), None)
        # 同 component + 同 priority + ≥ 3 items 才算 cluster
        clusters[(component, priority)].append({
            "number": item["number"],
            "title": item["title"][:80],
            "sweeper": sweeper,
            "created_at": item["created_at"],
            "url": item["html_url"],
        })
    return [
        {
            "component": k[0], "priority": k[1], "count": len(v), "items": v,
            "ship_window": any("cr" in i["title"].lower() or "regress" in i["title"].lower() for i in v),
        }
        for k, v in clusters.items() if len(v) >= 3
    ]
```

### Step 3: sweeper marker 责任映射

```python
SWEEPER_OWNER_MAP = {
    "sweeper:risk-message-delivery": "chief",
    "sweeper:risk-session-state": "dev",
    "sweeper:risk-security-boundary": "dev + qa",
    "sweeper:risk-platform-windows": "dev",
    "sweeper:risk-compatibility": "dev",
    # 未列出的 sweeper → pm 临时分配
}
```

### Step 4: ship-coverage cross-check

```python
def ship_coverage_gap(release_tag: str, recent_items: list) -> list[dict]:
    """
    release body 主张 vs 实际新开 issue 的 gap:
    若 release body 含 "100% P0/P1 closed" 字符串 且 过去 72h 新开 ≥ 1 P0 → gap
    """
    # 拉 /releases/tag/{release_tag} body
    release_body = fetch_release_body(release_tag)
    has_clean_sweep_claim = bool(re.search(r"100%\s*(of\s*)?P[01]\s*(resolved|closed|fixed)", release_body))
    new_p0 = [x for x in recent_items if any(l["name"] == "P0" for l in x.get("labels", []))]
    if has_clean_sweep_claim and len(new_p0) > 0:
        return [{"release": release_tag, "claim": "100% P0/P1 closed", "new_p0": [i["number"] for i in new_p0], "gap": True}]
    return []
```

### Step 5: 飞书 digest 输出

```python
def triage_digest(clusters, gap, sweeper_count):
    """
    飞书 card 格式(short, ≤ 400 字):
    [
      🚨 cluster:
      comp/cron + P2 + risk-message-delivery → 5 items (#58378 #58379 + ...)
      👤 chief 负责...
      📊 ship-coverage gap: v0.18.0 + 1 new P0 (#57845)
      🔢 sweeper distribution: risk-message-delivery=4 / risk-session-state=3 / risk-security-boundary=2
    ]
    """
    return card_text
```

## 何时不该调用

- 没有 cron 03:00 UTC 触发(临时触发可走 ad-hoc mode,但不推荐)
- release tag 太陈旧(>7 天无 active dev)

## 验证

- `tests/post_ship_triage/test_cluster.py`:fixture 50 issue list,verify cluster 聚类逻辑
- `tests/post_ship_triage/test_sweeper_map.py`:verify sweeper marker → owner 映射全覆盖
- `tests/post_ship_triage/test_ship_coverage.py`:fixture release body + fresh P0,verify gap detection
- 集成测试:live GitHub API + 4 file

## Pitfalls

- **GitHub unauthenticated rate limit (60 req/h) 容易被这 skill 跑穿**: 一次跑 3-4 pages + 1 个 release fetch + 1 个 rate_limit probe,建议 chief cron 跑时在 chief memory 里 cache `last_api_call_epoch` 并走 ⌈60min⌉ 节流
- **cluster threshold 3 不能写死**: release-day 后 density 高(>100/天),降阈到 3 才能 catch cluster;release-stable 阶段(<10/天),升阈到 5 减少噪音。skill 应自带 dynamic threshold 输入参数
