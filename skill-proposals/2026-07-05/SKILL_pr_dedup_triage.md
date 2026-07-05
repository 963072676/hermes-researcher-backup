---
name: pr-duplicate-fix-detector
description: 当同一 bug 在 24h 内出现 ≥ 3 个独立 PR 抢同一 root cause 时(如 #58777/#58874/#58992 都抢 #58818)主动触发 dedup + 单一 owner 指派。Use when: pm-orchestrator 看到 PR 列表同 issue #N 关联 ≥ 3 个未 merged PR,或 chief-agent 收到 silent-fail 升级。本 skill 帮助 pm 仲裁"哪个 PR 是 root cause 修复,其他关闭"。
---

# pr-duplicate-fix-detector

## 何时调用

- PR 列表关联同一 issue #N ≥ 3 个未 merged(github search: `is:open linked:issue:N`)
- chief-agent 收到 silent-fail 升级(same root cause 24h 内 ≥ 3 PR)
- 用户 / chief 显式触发

## 标准流程

1. **收集 PR 元数据**:
   ```bash
   gh pr list --search "linked:issue:#N" --state open --json number,title,author,createdAt,additions,deletions,mergeable
   ```

2. **评分维度**(0~10,加总得 total):
   - root cause 覆盖率:测试是否真复现原 bug(grep 测试 case vs issue body)
   - 改动最小化:diff 行数 vs 同 PR 修复范围
   - 跨 subsystem 影响:改动是否触达 issue 之外的模块
   - 作者 cron 经验:作者是否在最近 30d 提过同 family PR
   - review signal:PR 是否有 maintainer comment / label

3. **指派**:
   - 最高分 PR = primary fix,**指派单一 owner**(在 PR 评论 `cc @author — 你负责,其他 PR 关闭`)
   - 其他 PR 模板回复: "Closing in favor of #N — your analysis is helpful, please review primary fix"
   - chief-agent 同步通知 6h 内 deadline

4. **追踪**:
   - daily check 一次,如果 primary 3 天内未合并 → 强制 reassign 给次高分 PR

## 何时不该调用

- 仅 1~2 PR 抢同一 issue — 不算 dedup,正常 review
- PR 修复方向完全不同(同一 issue,不同子问题)— 让 PR 各走各的

## 验证

- 输出 primary PR # + closed PR list + assigned owner + deadline
- 24h 内 chief-agent 收到 dedup 报告