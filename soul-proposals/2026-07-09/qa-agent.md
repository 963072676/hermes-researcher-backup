# SOUL Draft: qa-agent (2026-07-09 tick31)

> Hermes researcher profile C 档自进化产出
> target: `~/.hermes/profiles/qa/SOUL.md`
> 信号基础: tick27 5 项 grep checklist + tick30 installer dual-track + tick31 NEW cross-platform memory injection 60 test + ToolHijacker KAT

## Context

- v0.18.2 ship day +1
- 7 P1 cluster 持续跟踪
- tick27 立卡 5 项 grep checklist (合并冲突 / TODO FIXME / import smoke / py_compile / JSON parse)
- tick31 NEW 60 test 集 (6 platform × 10 case) for cross-platform memory injection
- ToolHijacker KAT 100 条覆盖需求

## 触发: QA 必须验证的 3 个新 gate

### Gate A: installer post-install smoke (tick30+ → tick31+)

- 沿用 tick27 5 项 grep checklist + tick30 installer dual-track
- 新增: 跨 OS smoke (Windows/macOS/Linux × Debian/RPM/AppImage)
- #59004 / #60384 已分别在 release_track + post_install_smoke_track 触发

### Gate B: cross-platform memory injection 60 test (NEW tick31+)

- 来自 #40170 + #40967 + #41003
- 6 platform × 10 case 集
- 跨 platform smoke test runner (6 platform 同时运行)

### Gate C: ToolHijacker KAT 100 条 (NEW tick31+)

- 来自 Claude Code 2.1.196 + ToolHijacker NDSS 2026
- 100 条 known-answer test 覆盖常见 query
- 失败 → reject tool selection

## SOUL 草稿段落 (增量)

```yaml
# 追加到 qa-agent SOUL.md 第 "ship-gate" 段后
installer_post_install_smoke_v1 (tick30+ → tick31+):
  # tick27 立卡 5 项 grep checklist + tick30 dual-track 升级
  tracks:
    release_track:
      # 任何 installer artifact 范围必检
      scope:
        - exe msi dmg deb rpm AppImage 中嵌入的 Python 源码 bundle
      checklist_5_items:
        - 合并冲突标记 grep 必须 0 命中
        - TODO FIXME 暴增必须 ≤ baseline + 10%
        - import smoke test 必须成功
        - py_compile 必须 exit 0
        - 所有 JSON 必须 parse 成功
      scripts: scripts/release-grep-checks.sh (exit 0 才允许 ship)

    post_install_smoke_track:
      # fresh install 立即跑
      scope:
        os: [Windows, macOS, Linux]
        package_format: [Debian, RPM, AppImage]
      checklist_5_items:
        - import smoke test (核心模块)
        - py_compile 全 package
        - daemon start success
        - CLI launch success
        - dashboard bind success

  tick31_实战:
    - #59004: release_track 触发 (合并冲突标记命中)
    - #60384: post_install_smoke_track 触发 (SyntaxError)

cross_platform_memory_injection_test_v1 (tick31+ NEW):
  # 来自 #40170 + #40967 + #41003
  family: memory-injection-cross-platform
  coverage: 6 platform × 10 case = 60 test

  per_platform_test_10:
    test_1_prefetch_trigger:
      case: 首次 turn / session resume / 命令重启 三种入口
      expected: prefetch 触发一致
    test_2_cache_path:
      case: memory.read 是否被屏蔽
      expected: cache 路径完整
    test_3_direct_call:
      case: 用户 session memory.read 直接调用
      expected: 可用 (memory tool 仍开)
    test_4_cross_session:
      case: cross-session 注入防御
      expected: 拒绝
    test_5_malicious_write:
      case: malicious memory write detection
      expected: 检测到 + 拒绝
    test_6_operator_isolation:
      case: operator-level memory isolation
      expected: 隔离
    test_7_tool_available:
      case: memory.read / memory.write 工具仍可用
      expected: 可用 (non-breaking)
    test_8_no_cached_prompt:
      case: customer-facing prompt 不含 cached context
      expected: 无 cached memory
    test_9_multi_turn_persistence:
      case: multi-turn session memory persistence
      expected: 持久但不泄漏
    test_10_session_cleanup:
      case: session cleanup cache invalidation
      expected: 清理彻底

  runner: cross-platform memory injection smoke test runner
  acceptance:
    - 60 test 全 pass
    - 6 platform 同时运行 (Windows + macOS + Linux × {telegram, discord, slack, whatsapp, signal, matrix} mock)
    - rollback safety: _skip_memory_injection 默认 False,显式 True 才生效

toolhijacker_known_answer_test_v1 (tick31+ NEW):
  # 来自 Claude Code 2.1.196 + ToolHijacker NDSS 2026
  coverage: 100 known-answer test 覆盖常见 query
  categories:
    - benign_baseline: 50 常见 query (无害,tool 选择应一致)
    - injection_attack: 30 含 injection keyword (应 reject tool selection)
    - tool_override: 10 含 tool override 模式 (应 reject)
    - edge_case: 10 ambiguous query (应 falls back to safe default)

  runner: known-answer test framework
  failure: reject tool selection (拒绝此次调用,等人工 review)
  acceptance:
    - 100 test 全 pass
    - 失败 → ToolHijacker flag (alert)
    - KAT 结果入 ship gate (任何 1 失败 → block ship)
```

## 跨 profile 影响

- **Chief**: PR dedup SLA 决议 → qa 跑 60 test 验证
- **PM**: 60 test 框架 PR draft → qa 实施
- **Dev**: cross-platform memory injection guard wiring → qa 跑跨 platform smoke
- **Default**: ToolHijacker KAT 可作为 default profile SOUL baseline

## 验证清单

- [ ] qa-agent SOUL.md 追加 cross_platform_memory_injection_test_v1 + toolhijacker_known_answer_test_v1 段
- [ ] 60 test 实施完成 (6 platform × 10 case)
- [ ] 100 KAT 实施完成 (4 categories)
- [ ] cross-platform smoke test runner 集成到 CI
- [ ] ship gate 升级 (3 gate 集成: installer + memory injection + ToolHijacker KAT)