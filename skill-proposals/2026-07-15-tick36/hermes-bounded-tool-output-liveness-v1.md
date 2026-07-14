---
name: hermes-bounded-tool-output-liveness-v1
description: '验证 terminal/execute_code/MCP 等工具输出在 capture 阶段有界，避免先无界聚合后截断导致 gateway OOM、messaging/cron 停摆。Use when: verbose subprocess、continuous stdout、tool_output.max_bytes、terminal timeout、GH #64435/#56059 类输出放大问题。'
version: 1.0.0
created_by: researcher
metadata:
  hermes:
    tags: [terminal, output-bounds, liveness, gateway, cron, oom]
---

# Hermes Bounded Tool Output Liveness v1

## 目标

保证任何工具输出在**读取/捕获阶段**就受限，内存复杂度为 `O(configured_limit)`。最终响应截断不等于 capture 安全；禁止把完整输出 join 成字符串后再做截断。

## 触发条件

- foreground command 可能输出 > 5 MiB
- 使用 `tee`、编译器 verbose、模型 loading spinner、测试全日志
- gateway RSS 与 subprocess output 同步增长
- timeout 在 continuous output 下失效
- post-processing 对巨大字符串执行 `.lower()`、ANSI strip、scrub、plugin hook
- 修改 `BaseEnvironment._wait_for_process()` 或 terminal result transform

## 不变量

1. collector 在 drain chunk 时限流。
2. 内存复杂度 `O(max_bytes)`，与 producer 总输出无关。
3. 保留 bounded head + tail + omitted byte count。
4. timeout/interrupt/natural exit 三条路径使用同一个 bounded collector。
5. 禁止 `"".join(all_chunks)`。
6. sudo detection、restricted-data scrub、ANSI strip、plugin hook 只接收 bounded view。
7. continuous output 不得延后 wall-clock timeout。
8. process group 必须在 timeout 后被终止并回收。

## 安全 collector 参考

```python
class BoundedCollector:
    def __init__(self, max_bytes: int):
        self.max_bytes = max_bytes
        self.head_budget = max_bytes // 2
        self.tail_budget = max_bytes - self.head_budget
        self.head = bytearray()
        self.tail = bytearray()
        self.total = 0

    def feed(self, chunk: bytes) -> None:
        self.total += len(chunk)
        if len(self.head) < self.head_budget:
            take = min(self.head_budget - len(self.head), len(chunk))
            self.head.extend(chunk[:take])
            chunk = chunk[take:]
        if chunk:
            self.tail.extend(chunk)
            if len(self.tail) > self.tail_budget:
                del self.tail[:-self.tail_budget]

    def render(self) -> bytes:
        omitted = max(0, self.total - len(self.head) - len(self.tail))
        marker = f"\n... {omitted} bytes omitted ...\n".encode()
        if omitted == 0:
            return bytes(self.head + self.tail)
        budgeted_tail = self.tail[-max(0, self.max_bytes - len(self.head) - len(marker)):]
        return bytes(self.head) + marker + bytes(budgeted_tail)
```

## 标准验证

### Test 1：容量

生成 100 MiB output，但返回值不超过 cap，collector peak memory 与 cap 同阶。

### Test 2：head/tail

首尾放 sentinel；最终结果必须保留两者并报告 omitted bytes。

### Test 3：continuous timeout

无限输出进程设置短 timeout；必须按 wall clock 结束，且 process group 无残留。

### Test 4：post-processing

对 detector/hook 注入 spy，确认输入长度不超过 cap。

### Test 5：多 surface liveness

terminal 大输出期间，gateway heartbeat、messaging poll、cron ticker 不应停止。

## 操作 workaround（修复未 merged 前）

```bash
some_verbose_command > /tmp/task-output.log 2>&1
wc -c /tmp/task-output.log
```

随后用文件读取工具分页，禁止把整文件经 terminal stdout 回灌。

## Acceptance contract

```yaml
runtime_boundedness:
  capture_limit_bytes: required_integer
  bound_applied_stage: capture
  memory_complexity: O(limit)
  head_tail_preserved: true
  omitted_count_reported: true
  timeout_under_continuous_output: true
  post_processors_receive_bounded_view: true
```

## 失败判定

- 输出 100 MiB 时 gateway RSS 增长近 100 MiB
- 任何路径 join 完整 chunks
- timeout 依赖“无新 output 的 inactivity”而非 wall clock
- full payload 先经过 detector/hook 再截断
- messaging/cron heartbeat 在 terminal call 期间饿死

## 证据

- GH #64435: <https://github.com/NousResearch/hermes-agent/issues/64435>
- PR #64524: <https://github.com/NousResearch/hermes-agent/pull/64524>
- PR #64448（closed, unmerged）: <https://github.com/NousResearch/hermes-agent/pull/64448>
- GH #56059 MCP result size: <https://github.com/NousResearch/hermes-agent/issues/56059>

## Pitfalls

- `tool_output.max_bytes=50000` 若只作用于 final response，不能防 OOM。
- `.lower()`、正则、strip、JSON encode 都可能复制 full string。
- 只测 finite output 不够；continuous producer 才能暴露 timeout 饥饿。
- closed PR 不算 landed，必须看 `mergedAt`。
