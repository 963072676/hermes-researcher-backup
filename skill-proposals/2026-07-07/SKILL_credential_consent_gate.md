---
name: hermes-credential-consent-gate
description: 'Hermes credential auto-discovery consent boundary 防御。Use when: researcher tick 检测到 provider 静默调用外部 auth tool(如 gh auth token / oauth flow / API key scrape)且 user 未 explicit configured 该 provider;或 chief-agent 收到 consent-gate 类 P1 issue;或 qa 跑 provider audit 时发现类似 silent-seed 行为。'
version: 0.1.0
author: Hermes Agent (researcher tick29)
license: MIT
created_by: agent
metadata:
  hermes:
    tags: [security, consent-gate, credential-pool, provider, hermes-agent]
    related: [hermes-researcher-self-evolution-v1, hermes-hardening-wave-verify, hermes-mcp-self-approval-baseline]
---

# hermes-credential-consent-gate

> Hermes credential auto-discovery consent boundary 防御。
> tick29 立卡 — GH #60379/#60382(2026-07-07 filed) + PR #60404(fix 模板, MERGEABLE)。

## 这个 skill 解决什么

v0.18.0 ship 后 7-day window 内出现第一个 "consent class" P1:
- **#60379/#60382**: copilot provider 在 startup 无 consent 调 `gh auth token`,静默写入 `~/.hermes/auth.json`
- 根因: `agent/credential_pool.py:1923-1950` `_seed_from_singletons()` + `hermes_cli/copilot_auth.py:93-101` `_try_gh_cli_token()` 无 consent gate
- 风险面: 任何 provider(anthropic / openai / google / deepseek / moonshot)都可能存在类似 silent-seed 行为,未知

## 何时调用

- researcher tick 检测到新 issue 含 `area/auth` + `provider/*` + `type/security` 组合
- chief-agent review PR 时发现涉及 silent credential load
- qa-worker 跑 provider audit 时发现 `auth.token` 调用未走 explicit gate
- dev-worker 实现新 provider 时,默认行为应是 explicit-only

## 标准流程

### Step 1: 探针 — 扫所有 provider 的 credential load 路径

```bash
# 找出所有调用外部 auth tool 的路径
grep -rn "auth.token\|oauth\|external.*auth" hermes_cli/ agent/ providers/ | \
  grep -v test | grep -v ".pyc" > /tmp/credential_load_paths.txt

# 对每个调用点查: 是否有 is_provider_explicitly_configured 类似的 gate?
grep -l "is_provider_explicitly_configured\|explicit.*config\|consent" /tmp/credential_load_paths.txt
```

### Step 2: 评估 — silent-seed 行为判定

对每个发现的 credential load 路径,评估 4 个标准:

1. **是否 silent?**: 调用前是否 user 知情?(warn / log / telemetry 至少 1 项)
2. **是否 auto-discover?**: 是否调外部 auth tool(如 gh auth token)而非 explicit user input?
3. **是否涉及用户已有 credential?**: 调的是 user 在本机已 authenticated 的 token(如 gh cli)还是 server-side secret?
4. **是否 explicit gate?**: 是否 check `active_provider` / `model.provider` / provider-specific env var 至少 1 项?

4 个标准全中 → silent-seed violation,必须 fix。任意 1 项有 defensive → acceptable。

### Step 3: fix 模板(参考 PR #60404)

```python
# agent/credential_pool.py 修改模式
def _seed_from_singletons(self, provider_name: str):
    # 加 gate 检查
    if not self.is_provider_explicitly_configured(provider_name):
        # log telemetry event for audit
        log_event("credential_load_attempt", {
            "provider": provider_name,
            "source": "gh_cli",
            "user_consent_explicit": False,
            "blocked": True,
        })
        return None  # 拒绝静默 auto-discover

    # ... 原有逻辑
```

```python
def is_provider_explicitly_configured(self, provider_name: str) -> bool:
    """检查 provider 是否 user explicit configured。"""
    auth_cfg = self._read_auth_json()
    if auth_cfg.get("active_provider") == provider_name:
        return True

    model_cfg = self._read_config_yaml()
    if model_cfg.get("model", {}).get("provider") == provider_name:
        return True

    # provider-specific env var
    provider_env_map = {
        "copilot": ["COPILOT_GITHUB_TOKEN", "GH_TOKEN", "GITHUB_TOKEN"],
        "anthropic": ["ANTHROPIC_API_KEY"],
        "openai": ["OPENAI_API_KEY"],
        # ... 其他 provider
    }
    env_vars = provider_env_map.get(provider_name, [])
    if any(os.environ.get(v) for v in env_vars):
        return True

    return False
```

### Step 4: 测试覆盖

```python
# tests/consent/test_provider_explicit_gate.py
import pytest

@pytest.mark.parametrize("provider_name", [
    "copilot", "anthropic", "openai", "google", "deepseek", "moonshot",
])
def test_load_pool_does_not_seed_provider_when_not_configured(provider_name, tmp_path, monkeypatch):
    """Provider 未 configured 时,credential load 不调外部 auth tool。"""
    # mock 外部 auth tool 调用
    mock_calls = []
    monkeypatch.setattr("subprocess.run", lambda *a, **kw: mock_calls.append((a, kw)) or MagicMock(returncode=1))

    # 设置未 configured 状态
    (tmp_path / "auth.json").write_text(json.dumps({"active_provider": "different"}))
    (tmp_path / "config.yaml").write_text(yaml.dump({"model": {"provider": "different"}}))

    # 跑 credential load
    pool = CredentialPool(auth_dir=tmp_path)
    result = pool.load(provider_name)

    # 验证: 不调外部 auth tool
    assert not mock_calls, f"silent_seed detected for {provider_name}: {mock_calls}"
    assert result is None
```

### Step 5: telemetry 集成

```python
# telemetry events for audit dashboard
EVENT_CONSENT_BLOCKED = "credential_load_blocked_no_consent"
EVENT_CONSENT_ALLOWED = "credential_load_allowed_with_consent"

def log_event(event_name, payload):
    """Log to hermes telemetry (any sink)."""
    # 实现依具体 telemetry backend
    pass
```

## 验证清单

- [ ] `grep -rn "auth.token" hermes_cli/ agent/ providers/` 全扫,每个调用点都走 `is_provider_explicitly_configured` gate
- [ ] 新 provider 添加时必须 default 走 explicit gate,不能 silent auto-discover
- [ ] unit test `test_load_pool_does_not_seed_provider_when_not_configured` 全 provider 覆盖
- [ ] telemetry event `credential_load_blocked_no_consent` 触发,可在 audit dashboard 查
- [ ] `~/.hermes/config.yaml` `consent.allow_silent_credential_discovery: bool` 默认 false
- [ ] hermes 启动时检测到 silent auto-discovery 路径 → 输出一次性 warn 到 stdout

## Pitfalls

- 不要 default 把所有 provider 改 explicit-only — anthropic / openai 等标准 API key provider 走 env var 已是 explicit,可保留 auto-discover(仅从 env var / config file 读,不调 gh auth token)
- 不要在 fix 中 hardcode provider 列表 — 用 `provider_env_map` 配置化
- consent gate 不能阻挡 user 显式 `hermes auth login copilot` 的命令 — 这条路径是 explicit user action,不是 silent
- 测试必须 mock subprocess.run 全局,避免真实调外部 auth tool

## 关联

- 上游: GH #60379/#60382, PR #60404
- 关联 PR: #4210(anthropic provider explicit gate 模板)
- 关联 family: silent-fail(tick27) / cross-platform-state(tick28) / **consent-gate(tick29 新立卡)**
- 关联 skill: hermes-mcp-self-approval-baseline(MCP 侧 consent boundary)
- 关联 SOUL 草案: `soul-proposals/2026-07-07/SOUL_default_draft.md`

## 历史立卡

- 2026-07-07: tick29 初版,基于 PR #60404 fix 模板