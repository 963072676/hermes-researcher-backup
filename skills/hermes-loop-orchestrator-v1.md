---
name: hermes-loop-orchestrator-v1
description: Loop engineering primitive implementations for Hermes cron: fan-out (parallel sub-tasks), verify (adversarial review), loop-until-done (convergent self-evolution). Use when: any hermes cron needs to "run until goal met" instead of fixed schedule, or needs cross-profile parallel sub-tasks, or needs adversarial verification before reporting. Maps to Claude Code /loop + /goal + sub-agents primitives.
version: 1.0.0
author: researcher (2026-06-22)
metadata:
  hermes:
    tags: [specialized, loop-engineering, multi-agent, orchestration]
    see_also: [docs/engineering/AGENT_CONTEXT.md, .agent/rules/write-policy.md]
---

# hermes-loop-orchestrator-v1

> Loop engineering primitive implementation for Hermes cron.
> Inspired by Addy Osmani's 2026-06-07 essay + Anthropic Dynamic Workflows 2026-05-28.
> 配套 KB doc: `[research-tick12-20260622] Loop Engineering: 2026 多 agent 编排主流范式`

## 提供三种 primitive

### Primitive 1: fan-out (跨 profile 并行子任务)

**何时用**: 一个任务需要 N 个 profile 各自出一份产出,合并后再决策

**接口**:
```bash
# 用 hermes-cli 调多个 profile 并发
for profile in pm-orchestrator dev-worker qa-worker researcher; do
  nohup hermes chat -p $profile -q "<task prompt>" > /tmp/loop_${profile}.log 2>&1 &
done
wait
# 合并: cat /tmp/loop_*.log | 你的合并逻辑
```

**实现注意**:
- 异步必须(`nohup ... &`)+ `wait` 等齐
- 每个子任务限定 5-15 min,超时 kill
- 合并时识别"冲突" (不同 profile 同建议矛盾时,默认 chief 拍板)

### Primitive 2: verify (adversarial 双 agent 互审)

**何时用**: 单个 profile 出的产出,需要另一个 profile 视角审一遍才发出去

**接口**:
```python
# Python 伪代码,实际用 hermes-cli 调用
def verify(producer_output, reviewer_profile, source_prompt):
    review_prompt = f"""
    你是 {reviewer_profile}。请从你的视角审以下产出,要求:
    1. 找出至少 1 个潜在问题
    2. 评估置信度 (0-1)
    3. 给出 PASS / FAIL / NEEDS_REVISE
    4. 列出最关键的 3 条改进

    原任务: {source_prompt}
    产出: {producer_output}
    """
    return call_hermes(review_prompt, profile=reviewer_profile)
```

**实现注意**:
- reviewer 必须**不同 profile**(同 profile 自审 = 摆设)
- 优先用 chief-agent 做 review(chief 不动手,最适合作 critic)
- 若 review = FAIL,自动触发 producer 再来一轮(走 loop-until-done)

### Primitive 3: loop-until-done (self-evolution 收敛循环)

**何时用**: 跑多轮"产出 → 判定 → 补一轮",直到满足 stop condition

**接口**:
```python
def loop_until_done(producer_profile, reviewer_profile, initial_prompt, max_iters=3):
    """
    核心循环:
    1. producer 跑一轮,产出 P_i
    2. reviewer 审 P_i,给 V_i (采纳率/通过率)
    3. 若 V_i >= threshold 或 i == max_iters: 退出,返 P_i
    4. 否则 producer 拿 V_i 当输入再跑,产出 P_{i+1}
    """
    history = []
    for i in range(1, max_iters + 1):
        # producer
        P_i = call_hermes(initial_prompt, profile=producer_profile,
                           context=history if history else None)
        # reviewer
        V_i = verify(P_i, reviewer_profile, initial_prompt)
        history.append({"iter": i, "P": P_i, "V": V_i})
        # 收敛判定
        if V_i.get("verdict") == "PASS":
            log(f"Converged at iter {i}")
            return P_i, history
    log(f"Max iters reached ({max_iters}), returning best")
    return history[-1]["P"], history
```

**实现注意**:
- `max_iters` 默认 3,够用且不烧 token
- 收敛阈值: 采纳率 >= 0.5 (≥一半被采纳) 或 verifier 显式 PASS
- 每次 iteration 必须 log 到 KB (跨 session 可追溯)
- 超过 max_iters 不重试,直接返 best,让用户看

## 组合用法 (real-world)

### 用法 1: chief-agent daily digest 加 self-evolution 循环

**问题**: chief 现在 cron 跑完就发日报,用户来不及反应 → 报告石沉大海

**解法**: digest 跑完后,自动查 researcher 过去 24h 提议,若采纳率 < 50%,触发 researcher 再补一轮

```python
# chief cron 新增 step (替换原 "完成输出后本任务结束")
last_report = generate_digest()
post_to_feishu(last_report)

# Self-evolution loop
proposals_24h = mcp_memory_review_pending(scope="private:gc-hermes-default", last_24h=True)
adoption_rate = count_adoptions(proposals_24h) / max(1, len(proposals_24h))
if adoption_rate < 0.5 and len(proposals_24h) >= 2:
    log(f"⚠ 采纳率 {adoption_rate:.0%} < 50%,触发 researcher 补一轮")
    extra = call_hermes(
        "昨日采纳率偏低,请基于以下已有提议生成更精炼的 3 条新建议...",
        profile="researcher"
    )
    post_to_feishu(extra, thread_id=last_report.thread_id)
```

### 用法 2: 多 profile 并行评估 SOUL 草稿

**问题**: researcher 出的 SOUL 草稿没人 review → 质量不均

**解法**: 草稿生成后,fan-out 给 5 个 profile 各审一遍,合并意见

```python
souli_draft = researcher.generate_soul_draft(target_profile, change_spec)
reviews = []
for reviewer in ["chief-agent", "pm-orchestrator", "dev-worker", "qa-worker", "default"]:
    r = verify(soul_draft, reviewer, change_spec)
    reviews.append({"reviewer": reviewer, "verdict": r["verdict"], "issues": r["issues"]})
# 合并: 多数 PASS 才真发,否则回到 researcher
pass_count = sum(1 for r in reviews if r["verdict"] == "PASS")
if pass_count >= 3:
    post_to_user(soul_draft, reviews)
else:
    researcher.refine(soul_draft, reviews)  # loop-until-done 内部
```

## 红线 (硬约束)

- 禁: 用这个 skill 直接写生产 profile 的 SOUL / config / 红线文件
- 禁: 跨 profile 写不通过 kanban-broadcast.sh 派单
- 禁: loop-until-done 跑超过 3 轮不退出
- 禁: fan-out 调超过 5 个 profile (token 烧太快)
- 禁: verify 走同 profile 自审
- 必: 每次循环必须 log 到 KB / 飞书,可追溯
- 必: stop condition 必须显式 (verdict=PASS / 采纳率>=阈值 / 达到 max_iters)
- 必: 异常时 graceful fallback (回退到单 profile 模式,不要整体挂)

## 失败回退

- hermes chat 超时 → 标记 sub-task FAILED,continue 不阻塞整体
- producer profile 不可用 → 自动降级到 chief-agent
- reviewer profile 给模糊 verdict → 视为 NEEDS_REVISE,继续下一轮
- KB / 飞书不可用 → log 写到本地 ~/.hermes/profiles/<profile>/.plur/,等通道恢复后重传

## 配套引用

- 关联 KB doc: `document_id=956a2a33-a29b-4549-a92a-bbb2441774c6` (Loop Engineering 总览)
- 关联 SOUL: chief-agent 标准输出格式 (见 ~/.hermes/profiles/chief-agent/SOUL.md)
- 关联 cron: chief-agent-daily-digest (job_id 01e914afd70a) — 是这个 skill 的第一个用户
- 关联 backup: ~/hermes-researcher-backup/ (SOUL/skill 草稿备份)
