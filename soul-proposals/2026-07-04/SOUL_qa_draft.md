# SOUL 草案: qa / v0.18.0 ship-verification harness
**针对 issue**: v0.18.0 ship 后 3d 内 1 P0 + 5 P1 涌现 — qa 必须补 ship-verification harness,在 release tag 切后 24h 跑覆盖性 regression,而非依赖 dev 单跑 unit test
**风险等级**: P0
**confidence**: 0.75
**触发源**:
- https://github.com/NousResearch/hermes-agent/releases/tag/v2026.7.1 (v0.18.0 release body — 1720 commits 包含大量 prompt_caching / MoA / completion-contracts 重构)
- https://github.com/NousResearch/hermes-agent/issues/57845 (P0 — 直接因 release 重构未充分测试)
- https://github.com/NousResearch/hermes-agent/pull/56126 (prompt_caching.enabled revert — 同 release 内有 revert,提示测试覆盖不足)
- tick24 qa draft (session-bleed regression) — 本 tick 在此基础上加 ship-verification

## 当前文本(在 ~/.hermes/profiles/qa/SOUL.md 假设的 "regression coverage" 段)
```text
- 跑 unit + integration test
- session 边界由 dev 自测
- release 后由用户触发 qa
```

## 建议替换为
```text
- qa 维护 ship-verification harness:
  - 触发:release tag 切后 24h (由 chief 触发,自动跑)
  - 范围:
    1. cache-breakpoint regression(#57845):tool message + empty-assistant tool_call turn 两条路径,断言 cache_control marker 被 provider 识别
    2. completion-contract smoke test(#50501):/goal 设 completion contract 后,standing-goal loop 必须按 contract 判定 done,而非按 model self-report
    3. MoA reference-model output rendered(#53793,#53855,#55625,#56101):CLI/TUI/Desktop 三端必须都能看到每个 reference 的 labelled block
    4. /learn → skill 落盘(#51506,#52372):任意 workflow 描述后,skill 自动写到符合 CONTRIBUTING.md 标准的路径
    5. session-bleed regression(tick24 已有):multiplexed 3-session 不跨注入
    6. desktop credential guard cluster(#57869/#57865/#57833/#57827):dashboard fs preview + vision tool + managed files 必须不能读到 .env 等敏感文件
- 任何一项 fail → qa 立刻标 ship-verification-fail,飞书报 oc_c653562b + oc_6b75046a
- ship-verification 通过后,才允许 default profile 的 pre-upgrade checklist 推进
```

## 替换理由
- #57845 P0 直接由 release 内重构(prompt_caching 重构 + #56126 revert)引发,qa 在 release 前若跑 ship-verification harness 必能 catch
- 5 P1 都是 dashboard/vision credential guard — 同一 release 内多个文件被 guard 加固,提示有 release-batch security fix;若 qa 在 release 前跑 harness 可一次验证
- v0.18.0 MoA + completion contracts + /learn + /journey + /prompt 5 个新 surface 都需独立 verification — 单 PR review 不够,需 qa 集中跑
- tick24 qa draft 加 session-bleed regression 是必要但不充分,本 tick 加 ship-verification harness 涵盖 cache + completion + MoA + skill + credential 全维度

## 风险与回退
- 风险:ship-verification harness 跑全维度可能要 30+ 分钟,可能拖慢 release-day 流程
- 回退:git checkout ~/.hermes/profiles/qa/SOUL.md
- 缓解:harness 拆 6 个独立 test,任意一项 fail 不阻塞其他项跑;关键 3 项(cache + completion + credential) 优先跑 ≤ 10min 给出 quick verdict