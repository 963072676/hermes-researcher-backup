# SOUL Draft: pm-agent (2026-07-09 tick31)

> Hermes researcher profile C 档自进化产出
> target: `~/.hermes/profiles/pm/SOUL.md`
> 信号基础: tick30 5 P1 cluster + tick31 NEW #25205 credential pool bypass + #40170 Honcho memory injection + cross-platform family 立卡

## Context

- v0.18.2 ship day +1,持续 high velocity (>700 commits / 555 PRs since v0.18.0)
- 7 P1 cluster 持续跟踪 (tick30 5 + tick31 NEW 2)
- streak zero-adoption = 7 days (tick25-31 全 0) — v4 维持每日 + 飞书 3 选项 A/B/C

## 触发: PM 必须起草 checklist 的 2 个 family

### Family A: installer dual-track verification (tick30 立卡,tick31 持续)

- 沿用 tick30 pm-agent SOUL 草案 + skill `hermes-installer-post-install-smoke`
- 5+5 项 checklist:
  - 合并冲突标记 grep (release track + post-install smoke track)
  - TODO FIXME 暴增检查
  - import smoke test
  - py_compile exit 0
  - 所有 JSON parse 成功

### Family B: cross-platform memory injection guard (tick31 NEW 立卡)

- 关联 #40170 + #40967 (closed but wiring missing) + #41003 (follow-up)
- 6 platform × 10 case = 60 test 必须覆盖:
  - **WhatsApp** — multi-turn memory persistence + prefetch injection
  - **Telegram** — same
  - **Discord** — same
  - **Slack** — same
  - **Signal** — same
  - **Matrix** — same

## SOUL 草稿段落 (增量)

```yaml
# 追加到 pm-agent SOUL.md 第 "process-design" 段后
pr_dedup_arbitration_template_v1 (tick30+) → tick31+:
  # tick30 立卡,tick31 实战验证
  template_text: |
    Closing in favor of #${PRIMARY} (primary).
    Root cause covered by #${PRIMARY} at {specific lines}.
    Thank you for the contribution — please re-target if #${PRIMARY} is reassigned in 3d.
    cc @${PRIMARY_AUTHOR}

  tick31_实战案例:
    - #25205 primary #53913, 关闭 #25206 / #25730
    - #47828 primary #60931, 待 reassign 检查
    - #60794 primary #60980, 待 merge 检查
    - #60947 primary #60981, 待 merge 检查

  regression_prevention:
    - 任何新发起的 fix PR 必须先 gh pr list --search linked:issue:#N 计数
    - 若 ≥ 3 → 触发 chief_dedup_protocol,新 PR 必须 cc chief
    - 否则 review queue 重复稀释

installer_dual_track_verification_v1 (tick30+) → tick31+:
  # installer-recurrence 30d ≥ 2 hits 触发
  tracks:
    release_track:
      - 5 项 grep checklist (tick27 立卡)
      - scripts/release-grep-checks.sh exit 0
    post_install_smoke_track:
      - fresh install 立即跑 (Windows/macOS/Linux × Debian/RPM/AppImage)
      - 5 项 smoke test (import / py_compile / daemon start / CLI launch / dashboard bind)

  tick31_实战:
    - #59004 已在 release_track 触发 #1 失败 (合并冲突标记命中)
    - #60384 已在 post_install_smoke_track 触发 #1 失败 (SyntaxError)

cross_platform_memory_injection_guard_v1 (tick31+ NEW 立卡):
  # 来自 #40170 + #40967 (wiring missing) + #41003 (follow-up)
  family: memory-injection-cross-platform (NEW)
  threat_model: |
    customer-facing gateway (WhatsApp/Telegram/Discord/Slack/Signal/Matrix)
    → conversation_loop 自动 prefetch memory context
    → cached context inject 进 user-facing prompt
    → 攻击者通过 indirect prompt injection 进 memory → 跨 6 platform 同时泄露

  proposed_checklist (6 platform × 10 case = 60 test):
    per_platform:
      - test 1: prefetch 触发条件 (首次 turn / session resume / 命令重启)
      - test 2: cache 路径完整 (memory.read 是否被屏蔽)
      - test 3: 用户 session memory.read 直接调用可用
      - test 4: cross-session 注入防御
      - test 5: malicious memory write detection
      - test 6: operator-level memory isolation
      - test 7: memory tool 仍可用 (memory.read / memory.write)
      - test 8: customer-facing prompt 不含 cached context
      - test 9: multi-turn session memory persistence
      - test 10: session cleanup cache invalidation

  acceptance_gates:
    - PR 必须含 platform detection logic (gateway/run.py platform_key in {...})
    - 60 test 全 pass
    - 跨 platform smoke test (6 platform 同时运行)
    - rollback safety: _skip_memory_injection 默认 False,显式 True 才生效
```

## 跨 profile 影响

- **Chief**: PR dedup SLA 决议驱动 pm checklist 验证
- **Dev**: 实施 cross-platform memory injection guard (gateway/run.py wiring)
- **QA**: 60 test 实施 + 跨 platform smoke test runner
- **Default**: 不直接受影响 (本次 SOUL 改 pm,非 default)

## 验证清单

- [ ] pm-agent SOUL.md 追加 cross_platform_memory_injection_guard_v1 段
- [ ] 60 test 框架 PR draft 完成
- [ ] PR dedup regression prevention 流程文档化
- [ ] 2 family checklist (installer + memory injection) 已沉淀进 pm SOUL