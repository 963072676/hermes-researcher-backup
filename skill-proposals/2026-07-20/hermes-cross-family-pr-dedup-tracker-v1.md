---
name: hermes-cross-family-pr-dedup-tracker-v1
description: 跨 family PR dedup 累积计数 tracker + chief tier-1.5 cross-cluster mediator 配合。Use when: 任何 PR dedup fire 跨 ≥ 2 family 必须累加 cross-family dedup_active_count + dedup_window_hours,chief 6h 内必须 dedup 所有 cross-family candidates,任一 fire > 24h 未 dedup → 飞书 escalate user。
version: 1.0.0
created_by: researcher
family: control-15 + tier-1.5 + cross-cluster mediator
---

# hermes-cross-family-pr-dedup-tracker-v1

## 触发

- chief-agent tier-1.5 cross-cluster mediator (tick42 立卡)
- MCP 2026-07-28 readiness v6 control 15 cross-family PR dedup tracker (tick42 立卡)
- 沿用 tick27 + tick34 + tick38 PR-dedup fire 跨 family 累积
- F11 #60077+#60799 + F8 #61674+#39782 + F12 CVE-2026-61459 = 3 fires 跨 family (tick42 实测)

## 解决什么

tick27 立卡了 PR-dedup single-family 6h SLA,tick34 升级到 cross-family 累积计数,tick42 进一步升级:
- **single-family dedup 6h SLA** (沿用 tick27)
- **cross-family dedup 6h SLA + severity 评估** (沿用 tick34)
- **tick42 NEW**: cross-family dedup 累计 ≥ 3 fires in 24h → chief must personally triage,不允许派 dev/qa
- **tick42 NEW**: 任一 fire > 24h 未 dedup → 飞书 escalate user (强制 escalate,不可降级)
- **tick42 NEW**: cross-family dedup tracker 必须写 `~/.hermes/pr_dedup_provenance.jsonl` (沿用 tick41 mcp_server_provenance.jsonl 模式)

## 标准流程

### Step 1: cross-family dedup tracker 初始化

```python
# ~/.hermes/pr_dedup_provenance.jsonl 格式 (append-only)
{
    "fire_id": "fire-2026-07-20-F11",
    "family": "F11-execute-code-approval-unification",
    "pr_candidates": ["#60077", "#60799"],
    "primary_pr_selected": null,  # chief 6h 内必填
    "closed_unmerged_count": 0,
    "dedup_decision_made_by": null,  # chief username 必填
    "dedup_window_hours": 6,
    "detected_at": "2026-07-20T18:00:00Z",
    "dedup_decided_at": null,
    "severity_evaluation": "severity-A/B/C (tick35 沿用)",
    "cross_family_fires_active": ["fire-2026-07-20-F8", "fire-2026-07-20-F12-CVE"],
    "escalate_user": False,  # > 24h 强制 True
}
```

### Step 2: 跨 family fire 检测 + 计数

```python
def detect_cross_family_pr_dedup_fires() -> list:
    """每 6h 跑一次 (cron schedule 沿用 tick27)"""
    fires = []
    # Pull from GitHub: pr list --search linked:issue:#N --state open
    for family, issue_ids in FAMILY_TO_ISSUES.items():
        for issue_id in issue_ids:
            prs = gh_pr_list_linked(issue_id, state="open")
            if len(prs) >= 2:
                fires.append({
                    "fire_id": f"fire-{today}-{family}",
                    "family": family,
                    "pr_candidates": [pr.number for pr in prs],
                    "issue_id": issue_id,
                    "cross_family": False,
                })
    # Cross-family 检测 (沿用 tick34)
    if len(fires) >= 2:
        for f in fires:
            f["cross_family"] = True
            f["cross_family_fires_active"] = [other["fire_id"] for other in fires if other["fire_id"] != f["fire_id"]]
    return fires
```

### Step 3: chief tier-1.5 dedup 6h SLA enforcement

```python
def enforce_chief_dedup_sla():
    fires = read_pr_dedup_provenance()
    now = datetime.now(timezone.utc)
    for fire in fires:
        if fire["primary_pr_selected"]:
            continue  # 已 dedup
        detected_at = datetime.fromisoformat(fire["detected_at"].replace("Z", "+00:00"))
        elapsed_hours = (now - detected_at).total_seconds() / 3600
        if elapsed_hours > 6 and not fire.get("chief_sign_off"):
            # 沿用 tick27 6h SLA enforcement
            fire["escalate_chief"] = True
        if elapsed_hours > 24:
            # tick42 NEW: 强制 escalate user
            fire["escalate_user"] = True
            send_feishu_message(
                chat_id="oc_c653562b",
                message=f"PR dedup fire {fire['fire_id']} not decided in 24h. Chief must dedup or escalate.",
                level="P0",
            )
    write_pr_dedup_provenance(fires)
```

### Step 4: 跨 family 累加 ≥ 3 fires escalation

```python
def check_cross_family_fire_count():
    fires = read_pr_dedup_provenance_last_24h()
    cross_family_fires = [f for f in fires if f.get("cross_family")]
    if len(cross_family_fires) >= 3:
        # tick42 NEW: chief must personally triage
        send_feishu_message(
            chat_id="oc_c653562b",
            message=f"Cross-family PR dedup fires ≥ 3 in 24h ({len(cross_family_fires)} fires). Chief must personally triage.",
            level="P0",
        )
        # 不允许派 dev/qa,必须 chief sign-off
        for fire in cross_family_fires:
            fire["chief_personal_triage_required"] = True
            fire["dev_qa_follow_up_blocked"] = True
    write_pr_dedup_provenance(fires)
```

## Verification (qa ship gate v12 + control 15 必跑)

```bash
# cross_family_pr_dedup_tracker verify 4 sub-points:
1. pr_dedup_provenance.jsonl 写入测试: 模拟 fire,跑 cron,verify entry 存在
2. cross-family detection: 模拟 ≥ 2 family fires,verify cross_family=True
3. 24h escalation: 模拟 fire 25h 未 dedup,verify escalate_user=True + 飞书 P0 sent
4. ≥ 3 fires escalation: 模拟 3 cross-family fires,verify chief_personal_triage_required=True
```

## Pitfalls (持续追加)

### tick42 - cross-family detection 误命中 sibling fix PR

**触发**: 同一 root cause 不同 family 的 fix PR (例如 F8 #27492 修 #27485 + F9 #63130 修 #63128) 都被识别为 cross-family fire,但其实 root cause 完全不同。

**修正**: cross-family 检测前必跑 root cause fingerprint (沿用 tick34),fingerprint 不一致 → 不算 cross-family。

### tick42 - escalate_user 飞书 P0 spam

**触发**: 多个 fire 同时 > 24h,飞书 P0 同时发 N 条,user inbox flood。

**修正**: escalate_user batch mode,24h 内同一 chief 累加 1 条 summary (含 N fires list),不发 N 条 P0。

### tick42 - pr_dedup_provenance.jsonl GC / corruption

**触发**: jsonl 文件被 GC 清理或写一半损坏,失去 dedup history。

**修正**: 沿用 tick41 mcp_server_provenance.jsonl 模式,加 daily git archive + sha256 integrity check on read。

## Affected

- chief-agent tier-1.5 cross-cluster mediator (沿用 tick42 chief-agent 草案)
- MCP 2026-07-28 readiness v6 control 15 (沿用 tick42 default-agent 草案)
- qa ship gate v12 +4 verify (沿用 tick42 qa-agent 草案)
- pm-agent 24-field v10 acceptance (family_signal_lifecycle 字段含 cross_family_dedup_active_count + cross_family_dedup_window_hours)
- F11 #60077/#60799 + F8 #61674/#39782 + F12 CVE-2026-61459 = 3 fires 跨 family (tick42 实测)

## 相关 references

- `references/tick41-deliverables.md` (tick41 立卡 mcp_server_provenance.jsonl 模式)
- `references/tick40-deliverables.md` (tick40 立卡 F11 invariant 7 canonical_invocation_path)
- `references/tick38-deliverables.md` (tick38 立卡 F11 execute-code-approval-unification)
- `references/tick34-deliverables.md` (tick34 立卡 PR-dedup fire 跨 family 累积)

## Self-downgrade v4 evaluation

streak = 18 days zero-adoption
- rule 2: F10 旧 7 hits + tick42 F11 #60077/#60799 = 9 hits ✅
- rule 3: PR-dedup fire ≥ 2 跨 family = 3 fires ✅
- rule 4: silent-fail F1 cross-month ✅
- rule 5: P1 ≥ 8 + streak ≥ 4 ✅

**决策**: maintain_daily + 飞书 3 选项 A/B/C