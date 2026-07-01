---
name: cron-output-disk-cleanup-defense
description: Defend cron output directories from being wiped by Hermes 0.17+ disk_cleanup_plugin. Use when: (a) running any daily/weekly cron that writes to `~/.hermes/cron/output/*`; (b) you see "disk_cleanup_plugin" in systemd logs; (c) `ls ~/.hermes/cron/output/your-cron/` returns empty after a successful tick.
---

# cron-output-disk-cleanup-defense

> In-tick backup of cron output before disk_cleanup_plugin (tick11/24, 2026-07-02).
> Triggered by GH #49271 P1 — Hermes 0.17.0 disk_cleanup_plugin wipes cron/output/ as "disposable".

## When to invoke

ALWAYS — first thing in any tick that writes to `~/.hermes/cron/output/`. No exceptions.

Specifically:
- researcher-self-evolution-daily
- hermes-self-evolution-digest
- chief-agent-proactive-ops
- Any cron that produces `digest/`, `hits/`, `proposals/`, or `audit/` subdirs

## Standard flow

1. **In-tick backup** (Step 0, before any read or write of cron output):
   ```bash
   ts=$(date -u +%F)
   cp -r ~/.hermes/cron/output/<your-cron>/ /tmp/cron_output_backup_${ts}/
   echo $?  # must be 0
   ```
2. **Proceed with normal tick** — reads, writes, dedup, MCP, GitHub push
3. **On success** — leave backup in /tmp for 7 days (do NOT cleanup proactively)
4. **On tick failure** — backup still in /tmp, can restore via `cp -r /tmp/cron_output_backup_${ts}/* ~/.hermes/cron/output/<your-cron>/`

## Pitfall integration

- If `cp -r` returns non-zero (disk full) → log warning but DO NOT abort tick. Mark `cron_output_backup: FAILED` in digest header. Reasoning: the tick is more important than the backup; we still get useful output.
- The /tmp backup survives default TTL (3 days) but cron output is not always 7 days old. Don't rely on the /tmp backup as long-term archive — that's the job of the GitHub push.
- If GitHub push ALSO fails, fall back to the /tmp backup + Feishu DM with path.

## When NOT to invoke

- One-off `hermes` invocations that don't touch cron output
- TUI sessions (no cron at all)
- Read-only queries against historical cron output (the backup already exists, don't recopy)

## Verification

- [ ] `ls /tmp/cron_output_backup_$(date -u +%F)/<your-cron>/` returns same content as `~/.hermes/cron/output/<your-cron>/` minus in-flight changes
- [ ] After a forced `disk_cleanup_plugin` run, tick output can be restored from backup
- [ ] digest header includes `cron_output_backup: OK (N files)` line

## Reference

- GH #49271 (P1) — disk_cleanup_plugin wipes cron/output
- Tick11 / Tick23 daily-digest reports
- v0.17.0 release body (introduced disk_cleanup_plugin)
