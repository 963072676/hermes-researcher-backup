---
name: hermes-researcher-self-evolution-v1
description: Hermes researcher profile 的 C 档自进化 skill。叠加在 researcher-propose + researcher-scan 之上,提供 SOUL 草稿自动产出 + 新 skill 草稿 + 跨 profile 影响图 + 自我审计闭环 + GitHub 备份。Use when: researcher tick 需要从"出建议卡片"升级到"出可粘贴 diff + 草稿",以及需要防止建议永远停在 memory 里的情况。
---

# hermes-researcher-self-evolution-v1

> Hermes researcher C 档自进化 v1(2026-06-21)。
> 配套 SOUL v2 / cron: hermes-researcher-deep-tick-daily。

## 这个 skill 解决什么

researcher v1 的痛点:
- 建议卡片停在 memory,user 不点开就等于没产出
- 不会自动给"可执行 diff",user 还得自己写
- 没有闭环:不知道昨天建议被采纳没
- 没有备份:产出丢了就丢了

C 档升级后(本 skill 配套):
1. **SOUL 草稿自动产出** — 给每个受影响的 profile,产出完整 SOUL 段落,带 before/after diff
2. **新 skill 草稿** — 发现新能力缺口,产出新 skill 的 SKILL.md 全文
3. **跨 profile 影响图** — 识别"PM 改 X → 迫使 Dev 改 Y → 迫使 QA 加 Z",标注依赖链
4. **自我审计闭环** — 每日 tick 开始前先扫昨日采纳率,据此调参
5. **GitHub 备份** — 关键变更实时 push,日终聚合 push,周一推周报

## 何时调用

每次 `hermes-researcher-deep-tick-daily` 跑完,产出建议卡片后,**紧接着**调用本 skill:
1. 对每个 ≥ P1 风险的建议,自动生成 SOUL 草稿
2. 对每个新能力缺口,自动生成 skill 草稿
3. 跑影响图分析(若有跨 profile 依赖)
4. 跑自我审计扫昨日
5. 实时 push GitHub(用 gh CLI,已认证)
6. 飞书汇总(每日 09:00 UTC 一次性)

## 标准流程

### Step 1: 准备

```bash
# 确认 gh 认证
gh auth status | head -3

# 确认 backup repo 在
ls ~/hermes-researcher-backup/.git 2>/dev/null && echo "OK" || echo "MISSING"

# 拉最新
cd ~/hermes-researcher-backup && git pull --rebase --autostash
```

### Step 2: 生成 SOUL 草稿

对每条 P1+ 建议,生成 `soul-proposals/YYYY-MM-DD/<target-profile>-<section>.md`:

```markdown
# SOUL 草案: <profile> / <section>
**针对 issue**: <建议简述>
**风险等级**: P1 / P2
**confidence**: <0.6~0.85>
**触发源**: <信号链接 / arxiv id / GitHub PR>

## 当前文本(在 ~/.hermes/profiles/<profile>/SOUL.md 第 X 行)
```text
<原文粘贴>
```

## 建议替换为
```text
<新文>
```

## 替换理由
<2-3 句话>

## 风险与回退
- 风险: <一句话>
- 回退: git checkout ~/.hermes/profiles/<profile>/SOUL.md
```

### Step 3: 生成 skill 草稿

对每个新能力缺口,生成 `skill-proposals/YYYY-MM-DD/<skill-name>.md`(完整 SKILL.md 模板):

```markdown
---
name: <skill-name>
description: <一行说明,含 use when>
---

# <Skill Title>

## 何时调用
...

## 标准流程
1. ...

## 何时不该调用
...

## 验证
- ...
```

### Step 4: 跨 profile 影响图

读所有 P1+ 建议的 target profile,找以下模式:
- profile A 改 SOUL 第 N 行 → 隐含要求 profile B 的 cron 行为变化
- profile A 加 skill X → profile B 必须能调用
- profile A 的 config 改 → profile B 的 deny_patterns 必须跟进

输出在 `cron-output/YYYY-MM-DD/impact-graph.md`:
```markdown
# 跨 profile 影响图 (YYYY-MM-DD)

| 触发 | 直接影响 | 隐含影响 | 风险 | 处理 |
|---|---|---|---|---|
| <A 的某改> | B 须改 | C 须改 | P1 | 待用户 review |
```

### Step 5: 自我审计

读昨日 `docs/audit/` 不存在则视为 "no prior",读:
- `mcp_project_memory_memory_review_pending` 状态
- 飞书 ack(用户 24h 内回 ✅/❌/✏️/🔇 的次数,如有)
- GitHub commit 历史(soul-proposals 被覆盖回 SOUL 草稿的次数)

输出 `docs/audit/YYYY-MM-DD.md`:
```markdown
# 自我审计 YYYY-MM-DD

| 指标 | 昨日 | 过去 7 天均值 | 阈值 | 状态 |
|---|---|---|---|---|
| 提议数 | N | - | - | - |
| 采纳数 | N | - | - | - |
| 采纳率 | P% | - | < 10% 降级 / > 50% 升级 | OK / 降 / 升 |
| 误报数 | N | - | - | - |
| GH push 失败 | 0 | - | < 2 正常 | OK |

## 调参决策
- <如有降级/升级,列具体行动>
```

### Step 6: 实时 push GitHub

```bash
cd ~/hermes-researcher-backup
# 1. pre-commit 自检 secret
git diff --cached -- . ':(exclude)cron-output/*' | grep -iE "(api_?key|secret|token)" && { echo "BLOCK: secret in diff"; exit 1; }

# 2. add + commit
git add soul-proposals/ skill-proposals/ memory-snapshots/ docs/audit/ cron-output/ config.yaml soul-drafts/ skills/
git commit -m "researcher-tick $(date -u +%Y-%m-%d) | signals=N | proposals=M | soul-drafts=K | skill-drafts=L" 2>&1

# 3. push
git push origin main 2>&1
```

### Step 7: 飞书汇总

每天 09:00 UTC(北京时间 17:00)一次性发到 `oc_c653562b` (Home):
```text
🔬 researcher 自进化日报 (YYYY-MM-DD)

扫描信号: N
新增提议: M (待你 review)
新增 SOUL 草稿: K → github.com/963072676/hermes-researcher-backup/tree/main/soul-proposals
新增 skill 草稿: L → .../skill-proposals
采纳率(7d): P%
审计: [OK / 降级 / 升级]

【Top 3 建议】
1. <一句话>
2. <一句话>
3. <一句话>

【草稿 review】点链接看,回 ✅ 采纳 / ❌ 拒 / ✏️ 改写 / 🔇 静音一天
```

## 配额(防刷屏)

- 每日 SOUL 草稿: 最多 5 条
- 每日 skill 草稿: 最多 3 条
- 每日飞书汇总: 1 条(09:00 UTC)
- 实时 push 失败累计 2 次: 暂停推送,飞书报错

## 失败回退

- `gh auth` 失效 → 飞书报错,不阻塞 tick
- pre-commit 命中 secret → 阻断 commit,飞书报错,草稿暂存到 `~/hermes-researcher-backup/QUARANTINE/`
- push 冲突 → `git pull --rebase --autostash` 重试 3 次,仍失败报错

## 验证清单(本 skill 上线后第一次跑)

- [ ] 草稿生成正常,落到 backup 仓库对应目录
- [ ] pre-commit secret 自检通过
- [ ] 实时 push 成功(`git log` 看到新 commit)
- [ ] docs/audit/YYYY-MM-DD.md 产出
- [ ] 飞书汇总发出 + 链接可点
- [ ] 5 条 SOUL 配额生效(第 6 条不进飞书)
