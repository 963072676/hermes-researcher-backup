# Impact Graph — 2026-06-30

## Tick 22 (researcher cron) — 2026-06-30 02:06 CST

### 5-Profile Impact Matrix

| Profile | P0 | P1 | P2 | Total | Top Issue |
|---|---|---|---|---|---|
| **default** | 2 (#55029 cache, #55030 moa) | 8 | 12 | 22 | #55029 cross-session cache scope |
| **chief** | 1 (#55013) | 9 | 11 | 21 | #55013 cross-process guard |
| **pm** | 0 | 7 | 10 | 17 | #55019/#55017 feishu multi-app |
| **dev** | 1 (#55030 moa) | 6 | 13 | 20 | #55030 MoA KV-cache |
| **qa** | 0 | 11 | 14 | 25 | #55013/#55016/#55025/#55026 sweep batch |

### Cross-Profile Themes
1. **Gateway correctness** (#55029, #55013, #55016, #55025, #55026, #55045, #55031) — 7 PRs touching cross-session/cross-process semantics. Affects every profile that runs multi-process.
2. **Feishu multi-app** (#55019, #55017) — 2 PRs, affect pm + chief + default.
3. **Sweep regression hunt** — 20+ sweep-tagged PRs in 24h, suggests NousResearch ran a regression suite and surfaced a wave of issues.
4. **MoA** (#55030) — affects default+dev cost, awareness for chief (MoA never shipped chief).

### Severity Distribution
- P0: 3 (cache scope, cross-process guard, MoA KV-cache)
- P1: 19 (gateway correctness + auth + win-pty + cron)
- P2: 28 (regression hunt aftermath + feature work)

### Tracked PRs (status as of 2026-06-30)
- **Open, awaiting review**: #55029, #55013, #55030, #55031, #55017, #55045, #55026, #55016, #54997, #55008
- **Closed, merged**: #55033 (feat:desktop spectator)
- **Closed, not-merged**: #55019, #54992, #54991, #55032

### Risk Assessment
- **HIGH**: cross-session cache leak (#55029) — security boundary
- **HIGH**: cross-process guard false positive (#55013) — reliability
- **MEDIUM**: MoA KV-cache miss (#55030) — cost only
- **LOW**: feishu multi-app (#55017) — UX polish

### Action Items
1. Watch #55029 merge — when merged, default SOUL needs cross-session cache policy
2. Watch #55013 merge — when merged, chief SOUL needs session-scoped lock policy
3. Watch #55030 merge — when merged, dev SOUL needs KV-cache placement rule
4. Audit all 5 profiles' feishu streaming config before next bot send (per #49334 risk)
