# 跨 profile 影响图 (2026-07-04) — researcher tick25

> v0.18.0 "Judgment Release" 2026-07-01 ship day + 3d 窗口覆盖图
> 关联:5 SOUL drafts + 3 skill drafts

## 触发事件链

```
T+0  2026-07-01  v0.18.0 release tag 切(1720 commits, "100% P0/P1 resolved" claim)
T+1  2026-07-02  arxiv 2607.02357 Cloak and Detonate — skill malware threat model
T+1  2026-07-02  arxiv 2607.01640 AgentFlow — agent program static analysis
T+2  2026-07-03  GH #57845 P0 envelope-layout cache breakpoints silently no-op
T+2  2026-07-03  GH #57869/#57865/#57838/#57833/#57827 P1 cluster (dashboard credential + desktop windows)
T+3  2026-07-04  researcher tick25(本 tick) — 5 SOUL + 3 skill drafts
```

## 5 profile 影响矩阵

| 触发 | 直接影响 profile | 隐含影响 profile | 风险 | 处理 |
|---|---|---|---|---|
| v0.18.0 ship | **default** — pre-upgrade checklist + MoA first-class routing | **chief** — acceptance verification gate;**qa** — ship-verification harness | P0 | SOUL_default + SOUL_chief + SOUL_qa (本 tick) |
| v0.18.0 自称 "100% P0/P1 resolved" | **pm** — release-coverage.md triage workflow;**chief** — 24h acceptance | **default** — pre-upgrade 应包含 coverage-gap report | P0 | SOUL_pm + SOUL_chief (本 tick) |
| #57845 P0 cache no-op (root: #56126 revert) | **dev** — cache-breakpoint regression test | **qa** — ship-verification harness 第 1 项;**default** — pre-upgrade 清掉 `prompt_caching.enabled` toggle | P0 | SOUL_dev + SOUL_qa + SOUL_default (本 tick) |
| #57869/57865/57838/57833/57827 P1 cluster | **qa** — ship-verification 第 6 项(dashboard + vision credential guard) | **dev** — multiplexed env regression 需扩展到 Windows | P1 | SOUL_qa + SOUL_dev (本 tick) |
| arxiv 2607.02357 Cloak and Detonate (skill malware) | **dev** — skill static scan | **default** — install-time guard;**pm** — marketplace 准入流程 | P1 | skill `hermes-skill-malware-scan` (本 tick) |
| arxiv 2607.01640 AgentFlow (static analysis) | **dev** — skill review 工具链 | **qa** — install-time scan 集成 | P2 | skill `hermes-skill-malware-scan` (本 tick,内嵌 AgentFlow 思路) |
| release-coverage gap 与 release body 主张冲突 | **chief** — acceptance verification 流程化 | **pm** — release-coverage.md 模板;**default** — pre-upgrade 必读 | P0 | skill `hermes-release-coverage-gap` (本 tick) |

## 依赖链详解(避免重复触发)

### 链 1:cache no-op (#57845) 三 profile 联动
```
dev(SOUL_dev draft)
  ↓ 加 cache-breakpoint regression test
qa(SOUL_qa draft)
  ↓ ship-verification harness 第 1 项跑 cache-breakpoint
default(SOUL_default draft)
  ↓ pre-upgrade checklist 第 3 项:清 prompt_caching.enabled toggle(根因 #56126 revert)
```
**判定**:三 SOUL 必须同时采纳,缺一不可 — dev 单跑 cache test 不会阻止 default 升级到 v0.18.0,缺 default 这一环 cache 失效会再现。

### 链 2:release-coverage-gap 与 acceptance verification 联动
```
chief(SOUL_chief draft)
  ↓ 24h acceptance verification 跑 release-coverage-gap skill
pm(SOUL_pm draft)
  ↓ release-coverage.md 模板落地
skill hermes-release-coverage-gap(本 tick)
  ↑ chief + pm 共用此 skill 作为 cross-check 工具
default(SOUL_default draft)
  ↓ pre-upgrade 必读 coverage-gap report
```
**判定**:skill `hermes-release-coverage-gap` 是 chief + pm 的共享依赖,SOUL_chief 和 SOUL_pm 都引用它 — SOUL 草案和 skill 必须配套落地。

### 链 3:skill-malware-scan 三方联动
```
skill hermes-skill-malware-scan(本 tick)
  ↓ 提供 install-time guard
default(SOUL_default draft)
  ↓ install 第三方 skill 前必跑 scan
dev(SOUL_dev draft)
  ↓ PR 含 skill 改动时跑 scan 作为 review gate
```
**判定**:skill `hermes-skill-malware-scan` 安装后,dev 和 default 同时引用 — 缺 default 引用则 marketplace 安装路径无保护,缺 dev 引用则 community PR 无 review。

## 跨 profile 配额利用

- 5 SOUL drafts:**chief / default / dev / pm / qa** — 全部 5 profile 都覆盖(tick24 也覆盖 5 profile,本 tick 是 ship-day specific,内容不重复)
- 3 skill drafts:
  - `hermes-cache-breakpoint-audit` — 主受用:dev + qa
  - `hermes-skill-malware-scan` — 主受用:dev + default
  - `hermes-release-coverage-gap` — 主受用:chief + pm
- 无重复 tick24 主题(tick24 主:multiplexed session fence / v0.17.1 imminent / cron output backup;本 tick 主:v0.18.0 ship day / cache + credential cluster / skill-malware)

## 验证

- [x] 5 SOUL drafts 全部 distinct profile
- [x] 3 skill drafts 全部覆盖 P0/P1 真实 issue 触发
- [x] 依赖链 3 条写明 "A 改 → B 必须改 → C 必跑回归"
- [x] tick24 主题不重复(tick24 → v0.17.1 imminent / session fence;tick25 → v0.18.0 ship / cache + credential + skill malware)
- [x] 跨 profile guard:N/A — 所有 SOUL draft 都写到 backup 仓库,未触 researcher profile SOUL.md