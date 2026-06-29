# Skill proposal: first-seen-triage — 2026-06-30

## Purpose
Filter the daily 100-200 first-seen URLs from researcher cron tick into 3 buckets: (1) write to MCP, (2) save to hits jsonl only, (3) drop. Reduces noise and saves MCP quota.

## Inputs
- /tmp/first_seen_tick<N>.jsonl (output of dedup script)
- baseline /root/.hermes/cron/output/hermes-self-evolution-digest/dedup/seen_urls.json

## Triage rules
1. P0/P1 with affects_my_env=true — write MCP propose_write (priority slot)
2. P2 with affects_my_env=true — save to hits jsonl + skip MCP
3. All other — update baseline only, no archive

## Output
- MCP entries: bug_impact_matrix / release_summary / platform_api
- hits jsonl: full list
- baseline: updated

## Why this skill
Tick22 produced 100 first-seen; writing all to MCP would burn quota on low-value items. Triage skill enforces priority to cost gate. Researcher cron can use this skill instead of manual filtering.

## Status
PROPOSAL — pending user approval.
