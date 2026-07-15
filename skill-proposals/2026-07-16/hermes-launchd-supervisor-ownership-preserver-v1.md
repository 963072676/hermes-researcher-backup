---
name: hermes-launchd-supervisor-ownership-preserver-v1
description: '验证 Hermes gateway 在 macOS launchd / Linux systemd supervisor wrapper 下不被 setsid 让 PPID=1, 防止 orphaned gateway / KeepAlive churn / config silently not applied。覆盖 #64778 + fix #65105 external-supervisor flag + supervisor ownership preservation invariant。Use when: macOS launchd wrapper 部署、systemd wrapper 部署、KeepAlive 异常、config reload 不生效、gateway orphan 检测。'
version: 1.0.0
created_by: researcher
metadata:
  hermes:
    tags: [gateway, launchd, systemd, supervisor, ownership, macOS, trust-boundary]
---

# Hermes Launchd/Supervisor Ownership Preserver v1

## 目标

在 macOS launchd / Linux systemd 等 supervisor wrapper 部署下, 保证 Hermes gateway 不被 setsid 让 PPID=1, 保留外部 supervisor ownership, 防止 orphaned gateway / KeepAlive churn / config silently not applied。核心是 **positive ownership**: gateway 必须证明自己在 launchd/systemd 监督下, 否则 fail closed。

## 触发条件

- macOS LaunchAgent plist 部署
- Linux systemd unit 部署
- supervisor wrapper (init.d / runit / s6 / supervisord) 部署
- Gateway 启动 30s 内 PPID=1 (orphan)
- KeepAlive 触发 churn (反复 restart)
- config reload 不生效
- `gateway run --external-supervisor` flag (fix #65105)
- 修改 `gateway/launch.py` / `gateway/supervisor.py`

## 不变量

1. wrapped launchd/systemd gateway 永远不 setsid (除非显式 `--external-supervisor`)
2. PPID 必须是 launchd (1) 或 systemd (1) 或 wrapper 进程, 而非 init
3. config reload 信号经 supervisor KeepAlive 传播, 不允许 in-process restart
4. config change applied within 5s of plist reload
5. orphaned gateway auto-recovered within 30s
6. LaunchAgent plist label 与 gateway `gateway_id` 必须一致
7. `.plist` 必须包含 `<key>KeepAlive</key><true/>` (default)
8. systemd unit 必须 `Restart=on-failure` + `RestartSec=10s`

## 标准流程

### Step 1: 状态表

```text
deployment_mode | supervisor       | expected_ppid_chain | flag_required
launchd_plist   | launchd          | launchd(1) > gateway | none
systemd_unit    | systemd          | systemd(1) > gateway | none
docker          | docker           | container-init(1) > gateway | none
wrapper         | init.d/runit/s6  | wrapper > gateway | --external-supervisor
standalone      | none             | shell > gateway | --no-supervisor
test            | ephemeral        | arbitrary | --test-mode
```

### Step 2: launchd plist 模板

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.nousresearch.hermes.gateway</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/hermes</string>
        <string>gateway</string>
        <string>run</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
        <key>HERMES_HOME</key>
        <string>/root/.hermes</string>
    </dict>
    <key>KeepAlive</key>
    <true/>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/var/log/hermes/gateway.log</string>
    <key>StandardErrorPath</key>
    <string>/var/log/hermes/gateway.error.log</string>
    <key>SoftResourceLimits</key>
    <dict>
        <key>NumberOfFiles</key>
        <integer>65536</integer>
    </dict>
</dict>
</plist>
```

### Step 3: systemd unit 模板

```ini
[Unit]
Description=Hermes Agent Gateway
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/usr/local/bin/hermes gateway run
Restart=on-failure
RestartSec=10s
Environment="HERMES_HOME=/root/.hermes"
StandardOutput=journal
StandardError=journal
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
```

### Step 4: 检测 PPID orphan

```bash
# 在 gateway 启动 30s 内检测
PID=$(pgrep -f "hermes gateway run" | head -1)
if [ -n "$PID" ]; then
    PPID=$(ps -o ppid= -p $PID | tr -d ' ')
    if [ "$PPID" = "1" ]; then
        echo "WARN: gateway PPID=1, possible orphan"
        echo "Expected supervisor: launchd / systemd / docker-init / wrapper"
        echo "Fix: use --external-supervisor flag OR deploy with proper plist/unit"
    fi
fi
```

### Step 5: config reload 信号链 verify

```bash
# 修改 config.yaml 后, supervisor 必须感知 + reload
# launchd: 用 launchctl unload + load 触发 KeepAlive restart
launchctl unload /Library/LaunchAgents/com.nousresearch.hermes.gateway.plist
launchctl load /Library/LaunchAgents/com.nousresearch.hermes.gateway.plist

# systemd: 用 daemon-reload + restart
systemctl daemon-reload
systemctl restart hermes-gateway.service

# 5s 内 config change 必须 visible
sleep 5
hermes gateway status | grep "config_applied_at"
```

### Step 6: orphan auto-recovery smoke

```python
# 模拟 supervisor 崩溃后 gateway orphan
import os, signal, subprocess, time
gateway_pid = subprocess.check_output(["pgrep", "-f", "hermes gateway run"]).split()[0]
os.kill(int(gateway_pid), signal.SIGTERM)
time.sleep(2)

# 30s 内 supervisor 应自动 restart gateway
for _ in range(30):
    new_pid = subprocess.check_output(["pgrep", "-f", "hermes gateway run"]).split()
    if new_pid:
        new_ppid = subprocess.check_output(["ps", "-o", "ppid=", "-p", new_pid[0]]).strip()
        if new_ppid != b"1":
            print(f"PASS: gateway restarted under supervisor PPID={new_ppid}")
            break
    time.sleep(1)
else:
    print("FAIL: gateway not restarted within 30s")
```

### Step 7: cross-platform fix verification

```bash
# macOS
launchctl list | grep hermes
# 期望 Label 列 com.nousresearch.hermes.gateway, PID 列非 -

# Linux
systemctl status hermes-gateway
# 期望 Active: active (running), Main PID 非 1
```

## Acceptance contract

```yaml
launchd_supervisor_ownership:
  deployment_mode: enum[launchd, systemd, docker, wrapper, standalone, test]
  expected_ppid_chain: required_string
  actual_ppid: required_integer
  ownership_match: required_boolean
  external_supervisor_flag_used: required_boolean
  keepalive_enabled: required_boolean
  config_reload_within_5s: required_boolean
  orphan_recovery_within_30s: required_boolean
  plist_or_unit_path: required_string
  plist_label_or_unit_name_matches_gateway_id: required_boolean
```

## 失败判定

- wrapped gateway PPID=1 (orphan)
- config reload 后 5s 内不 visible
- orphan 后 30s 内不 auto-recover
- LaunchAgent label != gateway gateway_id
- systemd unit Restart=No / Restart=always (churn 风险)
- launchd KeepAlive=false (default-true 必须)
- in-process restart without supervisor signal
- 修改 plist/unit 后不 daemon-reload 直接 restart

## 证据

- GH #64778: <https://github.com/NousResearch/hermes-agent/issues/64778>
- PR #65105: <https://github.com/NousResearch/hermes-agent/pull/65105> (open)
- F9 session-state-integrity-deck expansion (cross-cluster arrow F9-F1-launchd-supervisor-misroute)
- tick27 PR dedup 立卡 (chief 6h SLA)
- tick33 cron-ticker-resilience-deck 第 8 family (BaseException catch, lock granularity)

## Pitfalls

- macOS launchd plist 误用 `RunAtLoad=false` 导致开机不启动
- Linux systemd unit `Type=forking` 误用导致 supervisor 误判进程结束
- `--external-supervisor` flag 必须显式传, 不传默认 assume in-process restart
- config reload 必须经 supervisor, 不要 in-process signal reload (避免 race)
- LaunchAgent plist label 与 gateway gateway_id 不一致导致 launchctl 操作失败
- systemd `Restart=always` 在 release bug 时会 churn, 建议 on-failure + RestartSec
- PPID=1 不一定 orphan, Docker 容器内 PID 1 通常是 entrypoint, 必须结合 deployment_mode 判断
- supervisor 崩溃后 standalone gateway 不会 auto-restart, 必须 deploy with supervisor
- test branch exact-pin SDK 不要在 production 跑, supervisor ownership 不一定 establish