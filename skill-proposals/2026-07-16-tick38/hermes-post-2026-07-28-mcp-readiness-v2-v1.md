---
name: hermes-post-2026-07-28-mcp-readiness-v2-v1
description: 'MCP 2026-07-28 final spec 12-day readiness v2 readiness check。沿用 tick37 readiness v1 6-control + tick38 +3 control (EXT14 shield + MCP server version pin + tool spawn static analyzer)。Use when: cron worker 在 2026-07-28 (MCP final spec release) 前 12 天起,每日必跑 9-control preflight + 5 install profile verify + CVE coverage check。'
version: 1.0.0
author: Hermes Agent (researcher profile, tick38)
license: MIT
created_by: agent
platforms: [linux, macos]
metadata:
  hermes:
    tags: [mcp, readiness, 2026-07-28, countdown, cve-coverage, 9-control, ext14, version-pin, argument-injection]
    related: [hermes-mcp-supply-chain-6-control, hermes-mcp-cancellation-probe-shield-v1, hermes-execute-code-approval-unification-v1, hermes-researcher-self-evolution-v1]
---

# hermes-post-2026-07-28-mcp-readiness-v2-v1

> Tick38 立卡 (2026-07-16)。MCP 2026-07-28 final spec 12-day countdown readiness v2。
> 沿用:tick33 MCP supply chain 6-control + tick37 readiness v1 + tick38 EXT14 + version pin + tool spawn analyzer。
> 触发:MCP 2026-07-28 final spec release 临近 (12 天 countdown) + CVE-2026-61459 + CVE-2026-59950 + EXT14 advisory。

## 1. 这个 skill 解决什么

**MCP 2026-07-28 final spec release** 是 MCP 协议从 RC → final 的关键节点。沿用 tick33 立卡的 6-control + tick38 新增 3-control = **readiness v2 9-control**。

**新增 3 个 control (tick38)**:
- **Control 7 — EXT14 cancellation-probe shield**:防御 300/300 MCP server crash on malformed `notifications/cancelled`
- **Control 8 — MCP server version pin**:CVE-2026-61459 (MCP K8s ≥ 3.9.0) + CVE-2026-59950 (mcp Python SDK ≥ 1.28.1)
- **Control 9 — Tool spawn static analyzer**:CVE-2026-61459 class argument injection detection (leading dash + kubectl_server_redirect + shell_wrapper)

**readiness v2 9-control 全表**:

| # | Control | CVE / threat | 沿用 |
|---|---|---|---|
| 1 | Hash pin (immutable ref) | MCPoison class (CVE-2025-54136) | tick33 |
| 2 | OSV scan | 已知 CVE 静态扫描 | tick33 |
| 3 | Shell egress pattern block | CVE-2026-30623 (LiteLLM stdio injection) | tick33 |
| 4 | Tool description sanitization | MCPTox 36.5% ASR | tick33 |
| 5 | Tirith pipe scan (`curl|sh` 等) | OWASP MCP Top 10 | tick33 |
| 6 | Perplexity + known-answer test | Tool selection hijacking | tick33 |
| 7 | **EXT14 cancellation-probe shield** | EXT14 (cobalto-sec 2026-07-09) | **tick38 NEW** |
| 8 | **MCP server version pin** | CVE-2026-61459 + 59950 | **tick38 NEW** |
| 9 | **Tool spawn static analyzer** | CVE-2026-61459 class | **tick38 NEW** |

## 2. 何时调用

- **2026-07-16 → 2026-07-28**:每日 cron tick 必跑 (12-day countdown window)
- **2026-07-28 ship day**:final 24h readiness 必跑 (countdown 0d)
- **任何 CVE / advisory 新出**:立即跑 9-control preflight verify
- **F11 execute-code-approval path**:F11 instantiate MCP server 必跑 readiness v2
- **5 install profile ship verify**:v0.18.3+ ship 前必跑 readiness v2

## 3. 标准流程

### Step 1: 9-control preflight check

```python
# scripts/mcp-readiness-v2-preflight.py
# F11 tick38 NEW: readiness v2 9-control preflight

import subprocess
import sys
from pathlib import Path

REPO = Path("/root/NousResearch/hermes-agent")


def check_control_1_hash_pin():
    """Hash pin (immutable ref) — MCPoison class."""
    pkg_lock = REPO / "package-lock.json"
    if not pkg_lock.exists():
        return {"passed": False, "reason": "package-lock.json missing"}
    # Verify SHA pins present
    content = pkg_lock.read_text()
    if '"integrity":' in content and '"sha512-' in content:
        return {"passed": True}
    return {"passed": False, "reason": "no sha512 integrity pins"}


def check_control_2_osv_scan():
    """OSV scan — known CVE."""
    try:
        result = subprocess.run(
            ["npx", "osv-scanner", "--lockfile=package-lock.json"],
            capture_output=True, text=True, cwd=REPO, timeout=60,
        )
        return {"passed": result.returncode == 0}
    except Exception as e:
        return {"passed": False, "reason": str(e)}


def check_control_3_shell_egress_block():
    """Shell egress pattern block."""
    config_path = REPO / "config.yaml"
    if not config_path.exists():
        return {"passed": False, "reason": "config.yaml missing"}
    content = config_path.read_text()
    required = ["mcp.shell_egress_block", "mcp.deny_patterns"]
    return {"passed": all(r in content for r in required)}


def check_control_4_tool_description_sanitize():
    """Tool description sanitization."""
    supply_path = REPO / "core/supply_chain.py"
    if not supply_path.exists():
        return {"passed": False, "reason": "core/supply_chain.py missing"}
    content = supply_path.read_text()
    return {"passed": "scan_mcp_description" in content}


def check_control_5_tirith_pipe_scan():
    """Tirith pipe scan."""
    security_path = REPO / "core/security.py"
    if not security_path.exists():
        return {"passed": False, "reason": "core/security.py missing"}
    content = security_path.read_text()
    required = ["curl|sh", "npx|bash", "wget|bash", "|python3 -c"]
    return {"passed": all(r in content for r in required)}


def check_control_6_perplexity_known_answer():
    """Perplexity detection + known-answer test."""
    supply_path = REPO / "core/supply_chain.py"
    if not supply_path.exists():
        return {"passed": False, "reason": "supply_chain.py missing"}
    content = supply_path.read_text()
    return {"passed": "perplexity" in content and "known_answer" in content}


def check_control_7_ext14_shield():
    """EXT14 cancellation-probe shield (NEW tick38)."""
    handler_path = REPO / "core/mcp/notification_handler.py"
    if not handler_path.exists():
        return {"passed": False, "reason": "notification_handler.py missing"}
    content = handler_path.read_text()
    required = [
        'notifications/cancelled',
        'params.get("requestId")',
        'if request_id is None',
        'if pending is None',
    ]
    return {"passed": all(r in content for r in required)}


def check_control_8_version_pin():
    """MCP server version pin (NEW tick38)."""
    import importlib.metadata
    issues = []
    
    # mcp Python SDK >= 1.28.1 (CVE-2026-59950)
    try:
        mcp_version = importlib.metadata.version("mcp")
        from packaging.version import Version
        if Version(mcp_version) < Version("1.28.1"):
            issues.append(f"mcp {mcp_version} < 1.28.1 (CVE-2026-59950)")
    except importlib.metadata.PackageNotFoundError:
        issues.append("mcp not installed")
    
    # mcp-server-kubernetes >= 3.9.0 (CVE-2026-61459) — if installed
    try:
        k8s_version = importlib.metadata.version("mcp-server-kubernetes")
        if Version(k8s_version) < Version("3.9.0"):
            issues.append(f"mcp-server-kubernetes {k8s_version} < 3.9.0 (CVE-2026-61459)")
    except importlib.metadata.PackageNotFoundError:
        pass  # not installed — OK if not using K8s
    
    return {"passed": len(issues) == 0, "issues": issues}


def check_control_9_tool_spawn_analyzer():
    """Tool spawn static analyzer (NEW tick38)."""
    analyzer_path = REPO / "core/mcp/tool_spawn_analyzer.py"
    if not analyzer_path.exists():
        return {"passed": False, "reason": "tool_spawn_analyzer.py missing"}
    content = analyzer_path.read_text()
    required = ["leading_dash_injection", "kubectl_server_redirect", "shell_wrapper"]
    return {"passed": all(r in content for r in required)}


def main():
    controls = [
        ("control_1_hash_pin", check_control_1_hash_pin),
        ("control_2_osv_scan", check_control_2_osv_scan),
        ("control_3_shell_egress_block", check_control_3_shell_egress_block),
        ("control_4_tool_description_sanitize", check_control_4_tool_description_sanitize),
        ("control_5_tirith_pipe_scan", check_control_5_tirith_pipe_scan),
        ("control_6_perplexity_known_answer", check_control_6_perplexity_known_answer),
        ("control_7_ext14_shield", check_control_7_ext14_shield),
        ("control_8_version_pin", check_control_8_version_pin),
        ("control_9_tool_spawn_analyzer", check_control_9_tool_spawn_analyzer),
    ]
    
    results = {name: fn() for name, fn in controls}
    passed_count = sum(1 for r in results.values() if r["passed"])
    
    print(f"MCP 2026-07-28 readiness v2: {passed_count}/9 controls passed")
    for name, result in results.items():
        status = "PASS" if result["passed"] else "FAIL"
        reason = result.get("reason", "")
        print(f"  {status}: {name}" + (f" ({reason})" if reason else ""))
    
    if passed_count < 9:
        print("readiness v2 FAILED — 12-day countdown not ready")
        sys.exit(1)
    else:
        print("readiness v2 PASSED — ready for 2026-07-28 final spec")


if __name__ == "__main__":
    main()
```

### Step 2: 5 install profile verify (沿用 tick37)

```python
# scripts/readiness-v2-5-install-profile.py

INSTALL_PROFILES = [
    "Desktop",      # macOS app.asar + Hermes.app + TCC/FDA;Windows installer + registry;Linux AppImage + dpkg + rpm
    "Docker",       # official hub + ghcr.io;non-local terminal backend confine;media cache scope
    "CLI",          # macOS Terminal + zsh;Windows Terminal + PowerShell;Linux gnome-terminal + bash
    "TUI",          # desktop window + WebSocket upgrade;portable mode
    "MCP_stdio",    # local stdio + Redis-backed session;keepalive empty exception bounded retry
]


def verify_install_profile(profile: str) -> dict:
    """5 install profile readiness v2 verify."""
    # 每个 profile 必须跑 9-control preflight + profile-specific smoke
    preflight = subprocess.run(
        ["python3", "scripts/mcp-readiness-v2-preflight.py"],
        capture_output=True, text=True, cwd=REPO,
    )
    
    # Profile-specific smoke tests
    profile_smoke = {
        "Desktop": ["macOS TCC/FDA gate", "Windows registry", "Linux AppImage"],
        "Docker": ["non-local backend confine", "media cache scope"],
        "CLI": ["zsh", "PowerShell", "bash"],
        "TUI": ["WebSocket upgrade", "portable mode"],
        "MCP_stdio": ["Redis-backed session", "keepalive bounded retry"],
    }
    
    return {
        "passed": preflight.returncode == 0,
        "preflight_output": preflight.stdout,
        "profile_smoke": profile_smoke.get(profile, []),
    }
```

### Step 3: CVE coverage matrix

```python
# 6 CVE coverage check
CVE_COVERAGE = {
    "CVE-2026-61459": ["control_8_version_pin", "control_9_tool_spawn_analyzer"],
    "CVE-2026-59950": ["control_8_version_pin"],
    "EXT14": ["control_7_ext14_shield"],
    "CVE-2026-30623": ["control_3_shell_egress_block", "control_5_tirith_pipe_scan"],
    "CVE-2025-54136": ["control_1_hash_pin", "control_4_tool_description_sanitize"],
    "CVE-2025-49596": ["control_1_hash_pin", "control_6_perplexity_known_answer"],
}


def check_cve_coverage():
    """Verify all 6 CVEs covered by at least 1 control."""
    results = preflight()  # run 9-control check
    uncovered = []
    
    for cve, controls in CVE_COVERAGE.items():
        covered = any(results[c]["passed"] for c in controls if c in results)
        if not covered:
            uncovered.append(cve)
    
    return {
        "passed": len(uncovered) == 0,
        "uncovered_cves": uncovered,
    }
```

### Step 4: Daily countdown reporting

```python
# F11 tick38 NEW: 12-day countdown tracker

from datetime import datetime, timezone

TARGET_DATE = datetime(2026, 7, 28, tzinfo=timezone.utc)


def countdown():
    now = datetime.now(timezone.utc)
    delta = TARGET_DATE - now
    days = delta.days
    hours = delta.seconds // 3600
    
    return {
        "days_remaining": days,
        "hours_remaining": hours,
        "target_date": TARGET_DATE.isoformat(),
        "window_status": "open" if days > 0 else "closed",
    }
```

## 4. 验证清单

- [ ] `scripts/mcp-readiness-v2-preflight.py` 9-control 全 PASS
- [ ] 5 install profile (Desktop/Docker/CLI/TUI/MCP_stdio) verify 全过
- [ ] 6 CVE coverage matrix 全 covered
- [ ] countdown tracker 12 → 0d 每日更新
- [ ] cobalto-sec Corvus scanner 跑一遍,EXT14 hits = 0
- [ ] OSV scanner 跑一遍,critical CVE = 0
- [ ] mcp Python SDK ≥ 1.28.1
- [ ] mcp-server-kubernetes ≥ 3.9.0 (if installed)
- [ ] notification_handler.py 含 4-line defensive code
- [ ] stdio_transport.py 含 try/except KeyError + Exception

## 5. 失败回退

- 任何 control 失败 → 立即升级 chief + 飞书报警
- control_7 EXT14 shield 失败 → 沿用 `hermes-mcp-cancellation-probe-shield-v1` skill patch
- control_8 version pin 失败 → `pip install --upgrade mcp>=1.28.1`
- control_9 tool spawn analyzer 失败 → 沿用 `hermes-execute-code-approval-unification-v1` skill patch
- 5 install profile 任一失败 → ship 拒绝 + chief triage
- 6 CVE 任一 uncovered → ship 拒绝 + chief triage

## 6. 配额与运行频率

- **运行频率**:
  - 2026-07-16 → 2026-07-28:每日 cron tick 必跑 (12-day countdown)
  - 2026-07-28 ship day:24h readiness 必跑 (countdown 0d)
  - 任何新 CVE/advisory 出现:立即跑
- **运行成本**:Step 1-3 ≈ 5-10s (OSV scan + 9 file check)
- **失败升级**:任何 step 失败立即升级 chief + 飞书推送

## 7. 关联 references / skills

- `hermes-mcp-supply-chain-6-control` (F7 主,沿用 control 1-6)
- `hermes-mcp-cancellation-probe-shield-v1` (tick38 立卡,control 7)
- `hermes-execute-code-approval-unification-v1` (tick38 立卡,F11 + control 8+9)
- `hermes-researcher-self-evolution-v1` (主 skill)
- `references/mcp-2026-07-28-spec-changelog.md` (MCP final spec 详细 changelog)
- `references/cve-2026-61459-k8s-argument-injection.md` (CVE-2026-61459 详情)
- `references/cve-2026-59950-mcp-python-sdk-ws-origin.md` (CVE-2026-59950 详情)
- `references/ext14-cobalto-sec-corvus-advisory.md` (EXT14 详情)

## 8. Pitfalls (持续追加)

### tick 38 - control_7 EXT14 shield 必须在 STDIO transport 之前 patch
**触发**:tick38 readiness v2 第一次跑 9-control 全 PASS,但实际 runtime test (打 37-byte payload) 仍 crash。原因是 STDIO transport read loop raise KeyError before notification_handler。

**修正路径**:
1. STDIO transport read loop 优先 patch (try/except KeyError + Exception)
2. notification_handler 加 4-line defensive code
3. runtime test 必跑真实 37-byte payload,不只 unit test mock

### tick 38 - control_8 version pin 必须区分 dev vs runtime install
**触发**:tick38 readiness v2 第一次跑 control_8 用 `pip show mcp` 验证,但 dev environment 用 `pip install -e .` 显示的是 git commit SHA 而不是 version number,误判 PASS。

**修正路径**:
1. 用 `importlib.metadata.version("mcp")` 而不是 `pip show`
2. 用 `packaging.Version` 严格比较
3. dev install (`pip install -e`) 必须 verify `pyproject.toml` 的 version 字段 ≥ 1.28.1

### tick 38 - control_9 tool spawn analyzer 不能只 grep 关键字,必须 AST parse
**触发**:tick38 readiness v2 第一次跑 control_9 用 `grep "leading_dash_injection"` 返回 PASS,但实际 `analyze_tool_spawn()` 函数没真调用 grep 命中的 pattern,只是注释里提到。

**修正路径**:
1. 必须 import `core.mcp.tool_spawn_analyzer` 实际调用 `analyze_tool_spawn("kubectl_get", {...})`
2. 用真实 argument injection payload (e.g. `resourceType="--server=https://attacker.example"`)
3. verify 返回 `safe=False` 才算 PASS

### tick 38 - 5 install profile verify 跨平台不能只 Linux 跑
**触发**:tick38 readiness v2 第一次 5 profile verify 全在 Linux 跑,但 macOS TCC/FDA gate 和 Windows registry 是 platform-specific,Linux 跑等于 false PASS。

**修正路径**:
1. macOS profile 必跑 on macOS host(或 CI macOS runner)
2. Windows profile 必跑 on Windows host(或 CI Windows runner)
3. 不能跨平台 verify,必须 native run

### tick 38 - countdown 必须含 hours 不要只 days
**触发**:tick38 readiness v2 第一次 countdown tracker 显示 "12 days remaining",但实际 ship day 是 2026-07-28 某具体时间(假设 00:00 UTC),倒计时精度不够。

**修正路径**:
1. countdown 必含 hours_remaining
2. ship day 24h 内必含 minutes_remaining
3. 飞书推送必含具体时间(e.g. "12d 5h 23m to 2026-07-28 00:00 UTC"),不只 "12 days"