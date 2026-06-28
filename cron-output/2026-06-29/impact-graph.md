# 跨 profile 影响图 (2026-06-29 / tick21)

> Hermes researcher deep tick 5 SOUL + 3 skill 草稿的跨 profile 依赖链分析。

## 触发源

54 first_seen (70 PR + 30 issues + 5 OR new + 3 HN in 3d), 经过 P1/P2 筛选后选 5 SOUL + 3 skill。

## 影响图

| 触发 | 直接影响 profile | 隐含影响 profile | 风险 | 处理 |
|---|---|---|---|---|
| **#54361 deps CVE** (starlette 1.0.1→1.3.1, crypto 46→49) | chief(扫描), default(实际部署) | researcher(用 memory_service 18080), qa(dev env) | P2 security | chief SOUL draft 等 PR merge |
| **#54340 cost-amplification guard** | dev(session 内 guardrails), default(memory_service 调用) | researcher(cron fire 时 cost loop), qa(test scenario) | P2 cost | dev SOUL draft + skill `cost-amplification-guard` |
| **#54329 deliver=origin silent drop** | pm(cron), chief(dashboard alert) | default(cron job 不送), researcher(cron fallback) | P2 UX | pm SOUL draft; 等 #54341 PR |
| **#54288 cron profile mismatch** | qa(multi-profile test), chief(cron manifest audit) | researcher(active profile 切换), pm(同 PM job) | P2 functional | qa SOUL draft + skill `cron-profile-sanity` |
| **#54305 URGENT PII delete** | chief(security hygiene SOP), default(redact 扩展) | researcher(web search 抓 README), dev(commit log) | P2 awareness | default SOUL draft + skill `pii-redact-pattern` |

## 依赖链

```
PR #54361 merge
  └─> chief scan pip-audit 周一 10:00
        └─> 命中 CVE → 提案给 default profile `pip install --upgrade starlette cryptography`
              └─> memory_service 重启 (researcher 依赖 18080 端口)
                    └─> 影响 researcher cron deliver (飞书 DM)

#54340 PR merge
  └─> dev session guardrails 升级
        └─> researcher cron fire 时 cost loop 触发 L3
              └─> 推 chief-agent incident ticket
                    └─> chief 决定降级或继续

#54288 + #54329 同时修
  └─> qa multi-profile test 加 2 个 case
        └─> pm SOUL 加 deliver fallback chain
              └─> researcher cron 不再 silent drop
```

## 隐含风险

1. **5 SOUL 草稿全部 open** = 同一周 5 个 profile 都需要 review, 可能 user 反馈延迟 → 降级机制待评估
2. **PR #54361 merge 触发 memory_service 升级** → researcher cron 当日 deliver 可能延迟 → 提前与 chief 沟通升级窗口
3. **skill `cost-amplification-guard` L3 硬停可能误伤** → 建议先灰度 dev profile → 验证 → 再推 default
4. **skill `cron-profile-sanity` 探测时 hermes cron list --json schema 未稳定** → version drift 风险

## 处理路径

- **chief / default**: PR-merge-driven,等信号
- **dev / qa**: SOUL draft 可手动 commit (`~/.hermes/profiles/{dev,qa}/SOUL.md`),user review 采纳
- **pm**: SOUL draft 含 fallback chain,建议先在 default profile 试跑
- **researcher**: 本 profile,直接采纳 5 SOUL + 3 skill draft 的相关段

## Quota 状态

- SOUL 草稿: **5/5 (full)** — 第 6 条不进飞书
- skill 草稿: **3/3 (full)**
- MCP propose: 4-5 条 (1 per P1 cluster)
- audit JSONL: 1 条