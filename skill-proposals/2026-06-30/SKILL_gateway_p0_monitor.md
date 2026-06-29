# Skill proposal: gateway-p0-monitor — 2026-06-30

## Purpose
Real-time monitor for open P0/P1 PRs in NousResearch/hermes-agent with comp/gateway or comp/agent label. Notify default + chief profiles when a new P0 PR lands affecting their surface.

## Inputs
- GitHub API: /repos/NousResearch/hermes-agent/issues?labels=P0,P1,comp/gateway
- Polling interval: 5 minutes
- Notification target: feishu DM oc_c653562b38ee197f3dce9921ace502c2

## Output
- Feishu card with PR number, title, affected components, link
- MCP propose_write with bug_impact_matrix entry
- local: ~/.hermes/profiles/<profile>/gateway-monitor/<date>.jsonl

## Implementation sketch
```python
def poll():
    items = gh_get("repos/NousResearch/hermes-agent/issues?labels=P0,P1&state=open")
    for it in items:
        if "gateway" in ",".join(l["name"] for l in it["labels"]):
            notify(it)
```

## Why this skill
Today: cron tick22 alone surfaces P0 signals, 24h+ delay. With 5-min monitor, default+chief profile learns about P0 cache scope (PR 55029) within 5 min of PR open, not 24h later.

## Status
PROPOSAL — pending user approval before creating skill.
