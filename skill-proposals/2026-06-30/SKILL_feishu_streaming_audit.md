# Skill proposal: feishu-streaming-audit — 2026-06-30

## Purpose
Audit feishu bot deployment against the v0.17.0 streaming card + multi-app session model. Detect configurations that will silently fail due to issue 49334 (streaming suppression of send_message).

## Inputs
- ~/.hermes/profiles/<profile>/config.yaml
- platforms/feishu runtime state
- Recent feishu send_message calls and their delivery status

## Output
- Audit report: which feishu bots have streaming card session active + send_message called
- Risk score per bot: HIGH (streaming + send_message) / LOW (no streaming) / UNKNOWN
- Recommendations: switch to direct REST API call OR disable streaming card

## Implementation sketch
```python
def audit():
    bots = list_feishu_bots()
    for bot in bots:
        streaming = check_streaming_card_session(bot)
        sends = count_recent_send_message(bot)
        risk = "HIGH" if streaming and sends > 0 else "LOW"
        report(bot, risk)
```

## Why this skill
Default + chief + pm profiles all use feishu. Issue 49334 silently drops send_message when streaming is active. Without audit, user thinks message was sent but recipient never sees it. Skill detects the misconfiguration.

## Status
PROPOSAL — pending user approval.
