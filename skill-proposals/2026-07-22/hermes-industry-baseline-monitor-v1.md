---
name: hermes-industry-baseline-monitor-v1
description: 'F12 (data-injection-isolation-deck) promote trigger。监测主要 agent SDK 自身 trust boundary violation 作为 hermes baseline shift 信号:Anthropic / OX Security / AI Now / MCP CVEs / arxiv 5 source converge 7d → F12 promote candidate。Use when: 看到 Anthropic Code backdoor 通报 / 5 source converge 任何时间窗 / hermes 自家 telemetry audit 时。'
version: 1.0.0
created_by: researcher C-profile auto-evolve (tick44 / 2026-07-22)
platforms: [linux, macos]
metadata:
  hermes:
    tags: [F12, industry-baseline, trust-boundary, telemetry-backdoor, ANthropic, OX-MCP, AI-Now, MCP-CVEs, arxiv]
    related: [hermes-f12-data-injection-isolation-v3, hermes-data-injection-isolation-v3]
    evidence:
      - Anthropic_NVDB_2_1_91_2_1_196_telemetry_backdoor (CN NVDB 2026-07-08)
      - OX_Security_Mother_of_MCP_security_report (10+ CVE, 200K instances)
      - AI_Now_Institute_Friendly_Fire_RCE (2026-07-10)
      - MCP_Python_SDK_CVE_2026_52870_52869_59950 (2026-07-15 ~ 16)
      - arxiv_2607_05120_ADI_Agent_Data_Injection
---

# hermes-industry-baseline-monitor-v1

> F12 (data-injection-isolation-deck) **promote trigger** = industry baseline shift 5-source converge
> Tick44 立卡 / 沿用 tick39/40/41 F12 candidate evidence 累计

## This skill solves

researcher v0.x 的痛点:
- hermes-agent 自家底层依赖 Anthropic SDK + MCP SDK,任何上游 trust boundary violation 都直接影响 hermes 自身
- 5 source converge 7d 没有自动监控 → F12 promote candidate 必须等用户手动 identify → 错过最佳 promote window
- default profile 没主动 industry baseline monitor → 仅靠 chief tier-1.5 24h decision 延迟

C档升级后:
1. **daily industry baseline scan** = 6 source monitor: Anthropic / OX / AI Now / MCP CVEs / arxiv / Reddit/HN
2. **5-source-converge-7d detector** = 自动 tally + escalate chief tier-1.5
3. **hermes own SDK dependency audit** = pre-check `pip show anthropic mcp` + alert on stale
4. **telemetry posture audit** = hermes subprocess network outbound 监控,防 Anthropic 2.1.91-2.1.196 type backdoor
5. **trust boundary industry shift score** = 0-100 综合评分,≥70 触发 chief 24h escalation

## When to invoke

任何 cron worker / agent 见到以下条件立即触发:
1. daily cron run(默认 02:00 UTC)
2. new CVE in MCP / Anthropic / Codex / Gemini CLI 通报
3. arxiv new paper on agent security
4. Anthropic / OX / AI Now institute 通报
5. hermes subprocess 网络 outbound 异常
6. chief tier-1.5 24h decision pending

## 6-step industry baseline monitor

### Step 1: 6 source daily scan

```python
SOURCES = {
    'anthropic_advisory': 'https://github.com/anthropics/claude-code/security/advisories',
    'ox_security_blog': 'https://www.ox.security/blog/',
    'ai_now_institute': 'https://ainowinstitute.org/publications/',
    'mcp_python_sdk_advisory': 'https://github.com/modelcontextprotocol/python-sdk/security/advisories',
    'arxiv_agent_security': 'http://arxiv.org/list/cs.CR/recent',
    'reddit_hermes_agent': 'https://www.reddit.com/r/ClaudeAI/search/?q=hermes',
}

def daily_industry_baseline_scan(date):
    """Tick44 — daily scan 6 source for trust boundary events."""
    new_entries = []
    for source_name, source_url in SOURCES.items():
        fetched = web_fetch(source_url)
        new_in_window = filter_last_24h(fetched, since=date)
        new_entries.extend([
            {'source': source_name, 'title': entry.title, 'url': entry.url,
             'severity': classify_severity(entry), 'detected_at': date}
            for entry in new_in_window
        ])
    return new_entries
```

### Step 2: 5-source-converge-7d detector

```python
def detect_5_source_converge(new_entries):
    """F12 promote trigger — 5 source converge in 7d window."""
    sources_hit = {e['source'] for e in new_entries}
    return {
        'converge_5_count': len(sources_hit) >= 5,
        'sources_hit': sorted(sources_hit),
        'new_entries_count': len(new_entries),
        'f12_promote_trigger': len(sources_hit) >= 5 and any(
            e['severity'] == 'CRITICAL' for e in new_entries
        ),
    }
```

### Step 3: hermes own SDK dependency audit

```python
def hermes_sdk_dependency_audit():
    """Tick44 — verify hermes uses latest patched Anthropic / MCP SDK."""
    anthropic_ver = subprocess.run(['pip', 'show', 'anthropic'], capture_output=True).stdout
    mcp_ver = subprocess.run(['pip', 'show', 'mcp'], capture_output=True).stdout
    anthropic_pinned = '2.1.198' in anthropic_ver  # NO backdoor version
    mcp_pinned = '1.28.1' in mcp_ver  # CVE-2026-59950 fix
    mcp_tasks_pinned = '1.27.2' in mcp_ver  # CVE-2026-52870/52869 fix
    return {
        'anthropic_safe': anthropic_pinned,
        'mcp_safe': mcp_pinned,
        'mcp_tasks_safe': mcp_tasks_pinned,
        'all_safe': anthropic_pinned and mcp_pinned and mcp_tasks_pinned,
    }
```

### Step 4: telemetry posture audit (subprocess network outbound)

```python
def hermes_telemetry_posture_audit():
    """Tick44 — detect Anthropic 2.1.91-2.1.196 type backdoor in hermes subprocess."""
    hermes_subprocess_outbound = monitor_all_hermes_children_network_connections()
    suspicious_destinations = [
        conn for conn in hermes_subprocess_outbound
        if conn.dst not in OFFICIAL_DESTINATIONS and
        not conn.dst.endswith('.internal') and
        conn.bytes_sent > 1024  # not just health probe
    ]
    return {
        'suspicious_outbound_count': len(suspicious_destinations),
        'backdoor_pattern_detected': any(
            is_steganographic_destination(conn) for conn in suspicious_destinations
        ),
    }
```

### Step 5: trust boundary industry shift score

```python
def trust_boundary_industry_shift_score(new_entries, sdk_audit, telemetry_audit):
    """Tick44 — F12 promote trigger score 0-100, ≥70 escalate."""
    score = 0
    score += len({e['source'] for e in new_entries}) * 10  # 10 per source
    score += sum(15 for e in new_entries if e['severity'] == 'CRITICAL')  # +15 per critical
    score += -10 if sdk_audit['all_safe'] else 20  # bonus if all safe
    score += 30 if telemetry_audit['backdoor_pattern_detected'] else 0
    return min(score, 100)
```

### Step 6: F12 promote escalation

```python
def f12_promote_escalation(score, converge_5):
    """Tick44 — escalate chief tier-1.5 if score ≥ 70 or 5-source-converge."""
    if score >= 70 or converge_5:
        write_f12_promote_trigger(
            score=score,
            evidence_summary=collect_recent_evidence(),
            escalates_to='chief_tier_1_5',
            sla='24h',
            decision_required='promote_F12_candidate_to_family_v1_or_maintain_pending',
        )
```

## Verification checklist

- [ ] 6_source_daily_scan_must_pass
- [ ] 5_source_converge_7d_detector_must_pass
- [ ] hermes_sdk_dependency_audit_must_pass(anthropic>=2.1.198 + mcp>=1.28.1+1.27.2)
- [ ] telemetry_posture_audit_must_pass(zero suspicious outbound)
- [ ] trust_boundary_industry_shift_score_must_be_calculated
- [ ] F12_promote_escalation_must_fire_when_score_ge_70

## Reference

- Anthropic Claude Code 2.1.198 fix (CN NVDB 2026-07-08) — telemetry backdoor
- OX Security "Mother of MCP" (2026-04, 10+ CVE, 150M+ downloads, 200K instances)
- AI Now Institute "Friendly Fire" RCE (2026-07-10, Codex auto-review + Claude Code auto-mode)
- MCP Python SDK CVE-2026-59950 (websocket auth bypass, fixed 1.28.1)
- MCP Python SDK CVE-2026-52870 (task handler cross-client, fixed 1.27.2)
- MCP Python SDK CVE-2026-52869 (HTTP transport auth principal, fixed 1.27.2)
- arxiv 2607.05120 ADI Agent Data Injection (new IPI subtype, F12 candidate evidence)
- F12 promote trigger anchor (沿用 tick37 + tick41 family_anti_inflation binding)
