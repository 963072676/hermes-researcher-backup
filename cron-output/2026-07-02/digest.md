# researcher tick24 digest (2026-07-02)

Scan signals: 113 first-seen (95 GH + 18 HN)
New SOUL drafts: 5 -> soul-proposals/2026-07-02/
New skill drafts: 3 -> skill-proposals/2026-07-02/
Adoption rate (7d): 0/today, 6/avg known (2026-06-18~22)
Audit: upgrade readiness -- v0.17.1 imminent, 1945 commits ahead

Top 3 recommendations:
1. v0.17.1 imminent signal -- /compare/v2026.6.19...main returns ahead_by=1945, pushed_at 0.5h ago, 3 consecutive ticks first_seen > 50. pm should pre-arrange release-day triage, default profile should prepare pre-upgrade check.
2. session context bleeding P1 -- #56456 closed but multiplexed gateway path still vulnerable (#56508 / #56523 same root cause). chief must enable session_fence=true, dev must add multiplexed env test, qa must run session-bleed regression.
3. 3 skill drafts pending -- gateway-multiplexed-session-fence (P1 fix scaffold) + v0-release-day-triage (5-profile release coordination) + cron-output-disk-cleanup-defense (GH #49271 defense).

Review at: https://github.com/963072676/hermes-researcher-backup/tree/main/soul-proposals/2026-07-02
