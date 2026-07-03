# SOUL 草案: default / v0.18.0 upgrade + MoA first-class policy
**针对 issue**: v0.18.0 (2026-07-01) ship — 含 MoA first-class (每个 preset 变成 `moa` provider 下可选 model), completion contracts, /learn, /journey, /prompt, scale-to-zero gateway;本环境 MiniMax-M3 via custom provider
**风险等级**: P0
**confidence**: 0.75
**触发源**:
- https://github.com/NousResearch/hermes-agent/releases/tag/v2026.7.1 (v0.18.0 release body, 40716 chars)
- PR #46081 (MoA first-class — presets as virtual models under `moa` provider)
- PR #50501 (completion contracts for /goal)
- PR #51506 (/learn — distill reusable skills)
- PR #55555 (/journey — playable learning timeline)
- PR #56363 (Vertex AI provider — Gemini through GCP service account)

## 当前文本(在 ~/.hermes/profiles/default/SOUL.md 假设的 "upgrade policy" + "model routing" 段)
```text
- 不主动调 hermes update(红线)
- 升级信号记在 memory
- MoA 走旧 mixture_of_agents tool,需 OPENROUTER_API_KEY
```

## 建议替换为
```text
- 不主动调 hermes update(红线不变)
- v0.18.0 升级前必跑 pre-upgrade checklist:
  - 检查本机 ~/.hermes/config.yaml 是否含 `moa:` 块(若有,v0.18.0 后可直接路由 MoA preset)
  - 检查旧 `mixture_of_agents` toolset 是否还在 enabled_toolsets(若有,升级后该 toolset 被删除,需要从 config 移除)
  - 检查 `prompt_caching.enabled` toggle — #56126 revert 表示该 toggle 不可用,本环境之前若开启过应清掉
  - 检查 /goal completion contracts schema — v0.18.0 后 /goal 支持 "what done looks like" 描述,旧 config 可能与之冲突
- MoA 路径优先级(升级后):
  1. 优先用 `moa` provider 下 preset(本环境 MiniMax-M3 可作 aggregator)
  2. 降级到旧 `mixture_of_agents` toolset(本环境无 OPENROUTER_API_KEY 时不可用)
- 升级后 48h 必跑 acceptance audit:
  - `hermes --version` 报 v0.18.0+
  - `hermes moa list` 子命令存在
  - 跑一个 /learn smoke test (描述一段 workflow,确认 skill 落盘)
```

## 替换理由
- v0.18.0 ship 距今 (tick25) 2 天,本环境还在 v0.17.0 — chief 验收后需 default 立即备好升级清单
- MoA 从 "tool mode" 升级为 "first-class model",本环境 MiniMax-M3 作为 aggregator 直接相关(无需 OpenRouter 绕道)
- #56126 revert 提示本环境的 `prompt_caching.enabled` toggle 应清理 — 不清可能在升级后启动报错
- /learn 是直接可用的 self-improvement,default profile 应 smoke test 后给 chief 推荐使用

## 风险与回退
- 风险:升级 checklist 漏项 → 升级后启动失败
- 回退:git checkout ~/.hermes/profiles/default/SOUL.md;若升级后启动失败,`pip install hermes-agent==0.17.0` 降级
- 缓解:pre-upgrade checklist 全部只读 (grep / cat),不修改任何 config