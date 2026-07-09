# SOUL Draft: dev-agent (2026-07-09 tick31)

> Hermes researcher profile C 档自进化产出
> target: `~/.hermes/profiles/dev/SOUL.md`
> 信号基础: tick30 5 P1 cluster + tick31 NEW #25205 + #40170 + Claude Code 2.1.196 MCP self-approval baseline + ToolHijacker 防御

## Context

- v0.18.2 ship day +1,持续 high velocity
- 7 P1 cluster 持续跟踪
- Claude Code 2.1.196 (2026-07-01) 已 ship MCP self-approval fix — hermes-agent baseline 缺位
- ToolHijacker NDSS 2026 96.7% ASR 防御 — Tool library validator 必须立卡

## 触发: dev 必须实施的 4 个新防御 pattern

### Pattern A: PR dedup acceptance protocol (tick30+ → tick31+)

- 接 chief_dedup_protocol 决议,合并 primary,关闭非 primary
- 4 P1 dedup 决议 (tick30+tick31):
  - #25205 primary #53913 → 关闭 #25206 / #25730
  - #47828 primary #60931 → 3 天 reassign 检查
  - #60794 primary #60980 → merge 检查
  - #60947 primary #60981 → merge 检查

### Pattern B: fallback_chain_index_reset_pattern_v1 (沿用 tick30)

- 来自 #60955 `_fallback_index` 不回滚
- 实施: `_restore_primary_runtime` 后必须 `_fallback_index = 0` 重置

### Pattern C: provider_base_url_symmetric_guard_v1 (沿用 tick30)

- 来自 #47828 `/mode model switch` 保留 OLD provider base_url
- 实施: switch_model() 双向 guard,reset base_url 与 provider 同时

### Pattern D: cross_platform_memory_injection_guard (NEW tick31+)

- 来自 #40170 + #40967 (closed but wiring missing)
- 实施: gateway/run.py platform_key detection → `agent._skip_memory_injection = True`
- 平台集合: {telegram, discord, slack, whatsapp, signal, matrix}

### Pattern E: ToolHijacker 防御 pattern (Claude Code 2.1.196 + ToolHijacker NDSS 2026)

- 来自 hermes-mcp-tool-library-validator skill
- 实施: scan tool description 不含 injection keyword (ignore previous / tool override / hijack)
- perplexity detection: tool selection 偏离 candidates 平均 perplexity > 2.0 → flag suspicious
- known-answer test: 覆盖 ≥ 100 常见 query,失败 → reject tool selection

## SOUL 草稿段落 (增量)

```yaml
# 追加到 dev-agent SOUL.md 第 "implementation-patterns" 段后
pr_dedup_acceptance_protocol_v1 (tick30+) → tick31+:
  # tick30 立卡,tick31 实战
  trigger:
    - chief 触发 6h SLA dedup 决议
    - gh pr list --search linked:issue:#N 计数 ≥ 3

  action:
    primary:
      - 接 chief 决议,merge primary PR
      - regression test 必跑 (沿用 cross_platform_memory_injection_guard)
      - 24h 内 comment "merged as primary per chief dedup"
    non_primary:
      - gh pr close --comment "${TEMPLATE}"
      - template: "Closing in favor of #${PRIMARY} (primary). Root cause covered by #${PRIMARY} at {lines}. cc @${PRIMARY_AUTHOR}"
    reassign:
      - 3 天 primary 未合并 → gh pr reassign 给次高分 PR author
      - cc chief 重新决策

  tick31_实战:
    - #25205: merge #53913, close #25206/#25730
    - #47828: 3 天 reassign 检查 → #60931 未合并 → reassign #60970
    - #60794: check #60980 merge status
    - #60947: check #60981 merge status

fallback_chain_index_reset_pattern_v1 (tick30+ → tick31+):
  # 来自 #60955
  pattern: |
    在 _restore_primary_runtime() 后必须显式重置 _fallback_index = 0
    否则 fallback gate 永久跳过

  implementation: |
    def _restore_primary_runtime(self):
        self.api_key = rt["api_key"]
        self._fallback_index = 0  # NEW: reset
        ...

provider_base_url_symmetric_guard_v1 (tick30+ → tick31+):
  # 来自 #47828
  pattern: |
    switch_model() 必须双向 guard:
    - reset base_url when provider changes
    - reset provider when base_url changes

  implementation: |
    def switch_model(self, new_model):
        old_provider = self.provider
        old_base_url = self.base_url
        self.provider = new_model.provider
        self.base_url = new_model.base_url
        # NEW: symmetric guard
        if old_provider != self.provider:
            assert self.base_url != old_base_url, "base_url drift"

cross_platform_memory_injection_guard_v1 (tick31+ NEW):
  # 来自 #40170 + #40967 (wiring missing) + #41003
  family: memory-injection-cross-platform
  pattern: |
    在 gateway/run.py 平台检测时设置 agent._skip_memory_injection = True
    平台: {telegram, discord, slack, whatsapp, signal, matrix}

  implementation: |
    # gateway/run.py L12713
    agent = AIAgent(...)
    platform_key = request.headers.get("x-platform", "cli")
    if platform_key in {"telegram", "discord", "slack", "whatsapp", "signal", "matrix"}:
        agent._skip_memory_injection = True  # NEW

  verification:
    - #40967 已合并但 wiring 缺失 → #41003 follow-up 必须含完整 diff
    - memory.read / memory.write 仍可用 (test 7)
    - 60 test (6 platform × 10 case) 全 pass

toolhijacker_defense_pattern_v1 (tick31+ NEW):
  # 来自 ToolHijacker NDSS 2026 + Claude Code 2.1.196
  threat_model:
    - tool description 嵌入 prompt injection (ignore previous / tool override / hijack)
    - tool selection 被 hijacked (96.7% ASR 实证)

  defense_layers:
    layer_1_tool_description_scan:
      scan_keywords: ["ignore previous", "tool override", "hijack", "override", "disregard"]
      reject_threshold: 0 (any match → reject)

    layer_2_perplexity_detection:
      metric: tool_selection_perplexity
      threshold: 2.0
      alert: "suspicious tool selection"

    layer_3_known_answer_test:
      coverage: "≥ 100 common queries"
      failure: reject tool selection

    layer_4_trust_policy:
      strict: true
      untrusted_repo_self_approval: false
      pending_label: "Pending approval"

  reference:
    - github.com/anthropics/claude-code/blob/main/CHANGELOG.md (2.1.196)
    - claude-code-2.1.196 self-approval fix
    - ToolHijacker NDSS 2026 paper
```

## 跨 profile 影响

- **Chief**: PR dedup SLA 决议 → dev 实施 primary merge + non_primary close
- **PM**: checklist 验证 dev 实施 (60 test, PR dedup regression prevention)
- **QA**: tool library validator 集成到 ship gate
- **Default**: ToolHijacker 防御 pattern 可作为 default profile SOUL baseline

## 验证清单

- [ ] dev-agent SOUL.md 追加 cross_platform_memory_injection_guard_v1 + toolhijacker_defense_pattern_v1 段
- [ ] 4 P1 dedup 决议实施 (merge primary, close non-primary)
- [ ] ToolHijacker 防御 4 层集成到 MCP runtime
- [ ] cross-platform memory injection guard wiring 完成