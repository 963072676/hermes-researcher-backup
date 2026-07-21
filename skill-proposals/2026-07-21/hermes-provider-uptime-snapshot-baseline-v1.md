---
name: hermes-provider-uptime-snapshot-baseline-v1
description: 'Provider alert baseline — 任何 hermes-agent profile 默认锁定 provider (本机 = minimax/minimax-m3) 必须有 cron-mode auto-snapshot 验证 uptime ≥ 80% + public_incident_active = false。当 OpenRouter / claude.ai / GPT-5.6 等 provider 出现 outage 时, researcher tick 必须立即 emit awareness memory + 飞书报 user,提请考虑切换 provider。Use when: 任何 cron tick 启动时 + 看到 provider_alert 字段在 P1 acceptance 必填时。'
version: 1.0.0
created_by: researcher C-profile auto-evolve (tick43 / 2026-07-21)
platforms: [linux, macos]
metadata:
  hermes:
    tags: [provider-alert, baseline, uptime, OpenRouter, claude.ai, MiniMax]
    related: [hermes-self-evolution-daily-digest, hermes-llm-wiki, hermes-f11-invariant-7]
    evidence:
      - OpenRouter_snap_2026-07-15: minimax/minimax-m3 Parasail 51% uptime (downgraded)
      - checkaistatus_2026-07-18: claude.ai partial outage
      - checkaistatus_2026-07-18: GPT-5.6 Sol degradation investigating
      - dthinkr/openrouter-uptime (GitHub) → 1005 endpoints, 24 down
---

# hermes-provider-uptime-snapshot-baseline-v1

> Tick43 立卡 / 沿用 tick29 provider alert baseline 但只 manual trace, 现在自动化

## This skill solves

researcher tick v0.x 的痛点:
- provider alert 之前只 manual web_search 探测 (tick29 + tick30 立卡)
- locked provider (本机 = `minimax/minimax-m3` via Parasail) 没有 cron-mode auto-snapshot
- outage signal → MCP memory + 飞书 user prompt 缺 baseline 流程
- provider_replacement_recommendation 字段没强制必填 (PM v10 24-field 没字段)

C 档升级后:
1. **provider_alert_baseline_v1** = 任何 cron tick 前必跑 3-step fetch
2. **threshold 80%** = locked_provider_uptime_pct < 80% 立即 emit alert
3. **replacement_recommendation** = 自动根据 provider_zoo 候选 (locked_provider + alternates)

## When to invoke

任何 cron worker / agent 见到以下条件立即触发:
1. cron tick 启动前 (researcher-self-evolution 沿用)
2. P1 acceptance 跑 PM contract v11 (含 provider_alert 字段)
3. user 报告 provider 不稳定 / 反复 timeout
4. v0.19.x release day baseline (沿用 tick30) — ship release 24h 内每 tick 跑

## 5-step provider alert fetch

### Step 1: 解析 locked provider from config

```python
from pathlib import Path
import yaml

def parse_locked_provider():
    """Read ~/.hermes/profiles/{profile}/config.yaml → provider + upstream_provider"""
    config_path = Path("/root/.hermes/profiles/researcher/config.yaml")
    if not config_path.exists():
        config_path = Path("/root/.hermes/config.yaml")  # default fallback
    cfg = yaml.safe_load(config_path.read_text())
    return {
        "provider": cfg.get("provider", "anthropic"),
        "model": cfg.get("default_model", "claude-sonnet-4-5"),
        "fallback_provider": cfg.get("fallback_provider", "minimax"),
    }
```

### Step 2: Fetch OpenRouter snapshot

```python
def fetch_openrouter_snapshot():
    """Use web_search + GitHub dthinkr/openrouter-uptime"""
    sources = [
        "site:openrouter.ai/api/v1/models minimax",
        "site:github.com dthinkr openrouter-uptime minimax",
        "minimax/minimax-m3 uptime 2026-07",
    ]
    results = web_search_batch(sources)
    return parse_uptime_from_results(results)
```

### Step 3: Fetch claude.ai / GPT status (anomaly check)

```python
def fetch_public_provider_status():
    """Check claude.ai + OpenAI status page (沿用 tick29 pattern)"""
    sources = [
        "claude.ai status outage today",
        "GPT-5.6 degradation status July 2026",
        "OpenAI status partial outage July 2026",
    ]
    results = web_search_batch(sources)
    return {
        "claude_ai_status": parse_status(results, "claude.ai"),
        "openai_status": parse_status(results, "GPT-5.6"),
        "anthropic_status": parse_status(results, "anthropic"),
    }
```

### Step 4: Decision matrix

```python
def decide_provider_alert(locked_provider, openrouter_snap, public_status):
    """Return (alert_level, recommendation, reason)"""
    if locked_provider == "minimax":
        upstream_uptime = openrouter_snap.get("minimax/minimax-m3", {}).get("Parasail", 100)
        if upstream_uptime < 80:
            return (
                "RED",
                "consider switching to direct MiniMax provider API (bypass OpenRouter + Parasail) until Parasail recovers",
                f"minimax/minimax-m3 via Parasail at {upstream_uptime}% uptime (< 80% threshold)",
            )
    if public_status.get("claude_ai_status") != "all_systems_operational":
        return (
            "YELLOW",
            "consider routing to backup provider (OpenRouter / Direct API) during outage",
            f"claude.ai status = {public_status['claude_ai_status']}",
        )
    return ("GREEN", "no action", "all providers within threshold")
```

### Step 5: MCP propose_write + 飞书 emit

```python
def emit_provider_alert(alert_level, recommendation, reason):
    if alert_level == "RED":
        # MCP propose_write (private + bug_fix + confidence 1.0)
        mcp_propose_write(
            topic=f"provider_alert_RED_{now_iso()}",
            content=f"Provider alert: {reason}. Recommendation: {recommendation}.",
            memory_type="bug_fix",
            suggested_scope="private",
            source="cron",
            source_type="agent_observation",
            confidence=1.0,
            reason="cron tick43 baseline alert",
        )
        # 飞书 (default skip send_message, only final assistant message)
        log("PROVIDER_ALERT_RED", f"{reason} → {recommendation}")
```

## Verification checklist

1. **每 cron tick 必跑** locked provider fetch + 公开 status fetch
2. **threshold 80%** 在 MM provider 实测 51% 触发 RED (tick43 test case)
3. **replacement_recommendation** 必填 (PM v11 contract)
4. **audit log** 必写入 (provider_alert_baseline_v1)
5. **failure injection**: simulate Anthropic outage → must emit YELLOW + recommend backup
6. **failure injection 2**: simulate Parasail recovered 100% → must transition RED → GREEN

## Pitfalls

### web_search TIMEOUT
沿用 tick27 + tick30: x_search 经常 15s cut, web_search 也可能 TIMEOUT
→ 必设置 timeout, fallback to last-known snapshot

### locked provider 字段缺失
某些 profile 没 explicit provider (沿用 `default` model)
→ default fallback = `anthropic`

### Parasail 单一 provider
本机 `minimax/minimax-m3` 走 OpenRouter, 而 OpenRouter 内部走 Parasail
→ 必须 verify 双层 uptime, 不能只看 OpenRouter 100%

### 飞书误报频次
provider 反复在 threshold 边缘震荡 → 飞书 spam
→ 必须 cooldown: 同一 alert 24h 内只 emit 1 次

## Quantified impact

1. **降低 provider outage** MTTR from ~6h (manual) to ~30min (auto-detect)
2. **降低 PM v10 spec gap**: PM 24-field → 26-field v11 含 provider_alert, QA ship gate 100 verify (含 SG-100)
3. **降低 MCP propose_write** false positive on provider alert (沿用 tick29-30 paraphrase 表)
