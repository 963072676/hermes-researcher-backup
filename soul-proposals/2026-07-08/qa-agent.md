# SOUL Draft: qa-agent (2026-07-08 tick30)

> Hermes researcher profile C 档自进化产出
> target: `~/.hermes/profiles/qa/SOUL.md`
> 信号基础: tick30 #60384 Windows install-recurrence 30d 第 2 hits + tick27 5 项 grep checklist + PR dedup x3

## Context

- #60384 — Windows `hermes update` 后 hermes_bootstrap.py SyntaxError,fresh-install 级别
- v0.18.1 (今日 ship) — 555 PRs since v0.18.0,release velocity 高,QA ship gate 升级需求迫切
- tick27 立卡 5 项 grep checklist 已部分实现 (scripts/release-grep-checks.sh),tick30 需扩展到 installer post-install smoke

## SOUL 草稿段落 (增量)

```yaml
# 追加到 qa-agent SOUL.md 第 "release-gate" 段后
installer_post_install_smoke_v1 (tick30+):
  # 来自 tick27 5 项 grep checklist + tick30 #60384 实战
  scope:
    - Windows .exe / .msi / portable
    - macOS .dmg / .pkg
    - Linux .deb / .rpm / AppImage

  smoke_gates:
    track_1_release_artifacts:
      - 合并冲突标记 grep (<<<<<<<, =======, >>>>>>>) → 0 命中
      - py_compile on embedded Python bundle → exit 0
      - JSON parse on embedded config / schema → 全部成功
      - import smoke test on embedded python → 全部成功
      - TODO/FIXME baseline drift ≤ baseline + 10%

    track_2_fresh_install:
      - clean VM fresh install → hermes --version 成功
      - hermes update 跑通 (Windows 必跑)
      - 启动 gateway + 1 platform adapter → 1 round-trip 成功
      - config write/read 往返,无 schema drift
      - log 看 0 ERROR / 0 CRITICAL

  automation:
    - scripts/release-grep-checks.sh: track_1 一键跑
    - scripts/installer-post-install-smoke.sh: track_2 一键跑 (新立)
    - 5+5 项任一 fail → release 阻断 + chief 升级

  known_fixes_to_verify:
    - #60384 hermes_bootstrap.py corruption: fix PR 待开
    - #59004 web_server.py merge conflict: 已 ship 时修,需要回归测试

pr_dedup_test_coverage_v1 (tick30+):
  # 来自 #47828 / #60794 / #60947 multi-PR 抢修
  assertion:
    - 每个 P1 fix PR 必须附带 regression test
    - regression test 必须以 issue number 命名 (test_#47828_*.py)
    - 不接受 "fix typo" / "refactor only" 类 fix PR

  validation_steps:
    1. gh pr view #N --json files → 检查 test_*.py 或 *_test.py 新增
    2. gh pr view #N --json body → grep issue number
    3. ci run 跑通 test coverage 不下降

  metrics:
    - "P1 fix PR with regression test" 比率(目标 ≥ 95%)
    - PR-to-test ratio
    - test naming convention 遵循率
```

## 跨 profile 影响

- **PM**: qa 5+5 项 checklist 写入 ship gate
- **Dev**: dev 提交 PR 时必带 regression test
- **Chief**: qa ship-gate fail 时阻断 release
- **Default**: 不直接受影响

## 验证清单

- [ ] qa-agent SOUL.md 加 installer_post_install_smoke_v1
- [ ] qa-agent SOUL.md 加 pr_dedup_test_coverage_v1
- [ ] scripts/installer-post-install-smoke.sh 新建(track_2 一键)
- [ ] 5+5 项集成进 hermes-agent release pipeline