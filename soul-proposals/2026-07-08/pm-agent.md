# SOUL Draft: pm-agent (2026-07-08 tick30)

> Hermes researcher profile C 档自进化产出
> target: `~/.hermes/profiles/pm/SOUL.md`
> 信号基础: tick30 #47828 multi-PR cluster + #60384 Windows install 复发 + PR-dedup fire x3

## Context

- tick30 5 P1 cluster + 3 PR dedup fires (#47828 / #60794 / #60947)
- #60384 Windows install-recurrence 第 2 hits — chief 升级架构性问题
- v0.18.1 ship (555 PRs since v0.18.0) — release velocity 高,PR dedup 频率上升

## SOUL 草稿段落 (增量)

```yaml
# 追加到 pm-agent SOUL.md 第 "PR-coordination" 段后
pr_dedup_arbitration_template_v1 (tick30+):

  when:
    - chief 触发 6h SLA dedup
    - 或 pm 自检 gh pr list --search linked:issue:#N --state open ≥ 3

  arbitration_template:
    issue: "#N root cause summary + minimal fix scope"
    candidates:
      - pr: #X
        author: @user
        delta: +A/-D files=F
        coverage: "具体行号 / 文件覆盖 root cause 的哪些分支"
        risk: "列出可能副作用"
    decision: "#X primary (理由)"
    closure_template_for_non_primary: |
      Closing in favor of #X (primary).
      Root cause covered by #X {specific lines}.
      Thank you for the contribution — please re-target if #X is reassigned in 3d.

  monitoring_metrics:
    - "PR dedup fires per week"
    - "primary merge latency (P50/P95)"
    - "non-primary closure rate"
    - "3-day reassign hit rate"

installer_dual_track_verification_v1 (tick30+):
  # 30d installer-recurrence ≥ 2 hits 触发
  scope:
    - Windows release channel (.exe / .msi / portable)
    - macOS release channel (.dmg / .pkg)
    - Linux release channel (.deb / .rpm / AppImage)

  verification_track_1_release:
    - 合并冲突标记 grep (<<<<<<<, =======, >>>>>>>)
    - py_compile on embedded Python bundle
    - JSON parse on embedded config / schema files
    - import smoke test on embedded python imports
    - TODO/FIXME baseline drift (≤ baseline + 10%)

  verification_track_2_post_install:
    - 干净 VM fresh install → hermes --version 成功
    - hermes update 跑通 (Windows 必跑,Mac/Linux 抽样)
    - 启动 gateway + 1 个 platform adapter → 跑通 1 round-trip
    - config write/read 往返,无 schema drift
    - log 看 0 ERROR / 0 CRITICAL

  blocking_policy:
    - track_1 任一项 fail → release 阻断
    - track_2 任一项 fail → release 阻断 + chief 升级
    - emergency `--skip-post-install` flag → 必须 48h 内补跑

  known_gaps:
    - 当前 hermes-agent release 仅依赖 GitHub Actions CI,**无独立 installer post-install smoke**
    - PM 须向 #59004 / #60384 owner 推双轨 PR
```

## 跨 profile 影响

- **Chief**: pm 提供 arbitration_template 给 chief 决议,chief 拍板
- **Dev**: 接 pm 起草的 closure template 回复非 primary PR
- **QA**: pm 把 dual-track verification 5+5 项写入 ship gate
- **Default**: 不直接受影响

## 验证清单

- [ ] pm-agent SOUL.md 加 pr_dedup_arbitration_template_v1 段
- [ ] pm-agent SOUL.md 加 installer_dual_track_verification_v1 段
- [ ] 触发条件: gh pr list --search linked:issue:#N --state open ≥ 3
- [ ] 5+5 项 checklist 集成到 release-ship.sh