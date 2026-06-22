---
name: loop-engineering-orchestrator
description: 编排 builder/judge 双循环 + cross-vendor verification,把 LangChain RubricMiddleware / RALPH Loop / architect-loop 模式落到 Hermes 跨 profile 场景。Use when: 任何 ≥ P1 风险、需 multi-turn verification、用户给了 rubric 但没说怎么 enforce、单 model 评估不可信的 task。
---

# Loop Engineering Orchestrator(2026-06-22)

> Hermes v0.17.0 (Raft agent network + async subagents + profile builder) 让 chief / pm 现在能真正落地"builder ≠ judge"模式。本 skill 是其官方 workflow。

## 何时调用

1. **判定条件**(满足任一即调用)
   - 任务含 ≥ P1 风险(代码改 SOUL / config / skill / cron)
   - 用户给了 rubric 但没说怎么 enforce
   - 同 profile 同 model 自评(reward hacking 风险)
   - 单次 cron tick 包含 ≥ 3 个改写动作

2. **不调用场景**
   - 纯 read-only 调研(researcher scan)
   - < 30 行 pure trivial diff
   - 用户明确写"不用 review"

## 标准流程(7 步)

### Step 1: Define Rubric
- 评分维度强制 3-5 条,每条独立可量化
- 模板:
  ```yaml
  rubric:
    - name: functional_correctness
      weight: 0.3
      pass_threshold: 4/5
      evidence_required: true   # 必填 repro command / test output
    - name: safety_boundary
      weight: 0.25
      pass_threshold: 4/5
    - name: perf_budget
      weight: 0.15
      pass_threshold: 3/5
    - name: consistency
      weight: 0.15
      pass_threshold: 4/5
    - name: rollback_clarity
      weight: 0.15
      pass_threshold: 4/5
  ```

### Step 2: Builder Profile Selection
- **首选**: dev-worker(model: 主路由 × MiniMax-M3 × Grok)
- **避免**: 与 verifier 同 model / 同 profile / 同 session
- **tooling**: `delegate_task(goal, toolsets=['coding'])`

### Step 3: Verifier Profile Selection (cross-vendor mandatory)
- **首选**: qa-worker(model: 与 builder 不同;推荐 Opus 4.8 × GLM-5.2 / Claude × Grok)
- **fallback**: 若用户只配 1 个 model → 强制 fresh session + 独立 system prompt(context 隔离)
- **tooling**: `delegate_task(goal, toolsets=['coding','web'])`

### Step 4: Hill-Climbing Loop (max 3 iterations)
```
for iter in 1..3:
    builder.execute(rubric, current_diff)
    output = builder.report
    verifier.grade(output, rubric)  # 5 维度评分
    if all_5_dimensions >= threshold:
        return PASS
    else:
        builder.refine(verifier.feedback_per_dimension)
        if iter == 3 and still_failing:
            return ESCALATE_TO_USER
```

### Step 5: Reward Hacking Self-Check
- 触发条件:verifier PASS 但单维度出现 "test-only-passes" 模式
- 例: 安全分 5/5 但 dev 改了 `deny_patterns` 把测试 target 排除
- **强制 escalate**: 任何 verifier 与 builder 共享 `deny_patterns` 写入历史 → 进 chief-agent

### Step 6: Memory Anchoring
- 成功通过后:`mcp_project_memory_memory_propose_write` 写"rubric-pass" fact,scope=`shared`
- 失败 escalate: 写"rubric-fail-N-times"到 chief pending_review

### Step 7: Audit Trail
- 把 builder output + verifier score + iteration log 全存到 `~/hermes-researcher-backup/cron-output/<date>/loop-engineering/<task-id>.md`

## 验证清单
- [ ] Rubric 3-5 维度,每条独立 pass_threshold
- [ ] Builder ≠ Verifier (cross-vendor 或 cross-context)
- [ ] Max 3 iterations,ESCALATE 路径明确
- [ ] Memory propose 路径走 MCP,不走直写 memory
- [ ] Audit trail 落到 backup 仓库

## 反模式 (anti-patterns)
- ❌ Builder = Verifier (reward hacking)
- ❌ Rubric 维度 < 3 (单维度 = 自评陷阱)
- ❌ Iteration > 5 (无 stop condition,reward hacking)
- ❌ 把 verifier score 加权平均(应 all-pass 而非 weighted-sum)

## 参考
- https://www.langchain.com/blog/the-art-of-loop-engineering
- https://www.i-scoop.eu/loop-engineering/
- https://gowrishankar.info/blog/ralph-loop-building-self-improving-ai-systems-without-claude/
- https://github.com/DanMcInerney/architect-loop/blob/main/DESIGN.md