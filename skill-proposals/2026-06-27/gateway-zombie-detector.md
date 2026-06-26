---
name: gateway-zombie-detector
description: 监听 Hermes gateway event loop 健康度,检测 zombie state (event loop 死了但 pid alive)。Use when: chief-agent 派工监控 + 生产 cron 守护 + 对应 PR #53183 修复验证。
---

# gateway-zombie-detector

## 何时调用
- chief-agent 派工前的强制 health check (与 chief-agent-gateway-zombie-exorcism SOUL 联动)
- 生产 cron 守护进程, 每 30s 跑一次
- PR #53183 fix 验证测试 (qa-worker-gateway-zombie-repro-test 配套)

## 标准流程

### Step 1: 配置 (从 ~/.hermes/config.yaml 读)
```yaml
gateway_zombie_detector:
  enabled: true
  interval_sec: 30
  healthz_endpoint: http://127.0.0.1:8765/healthz
  pid_file: ~/.hermes/gateway.pid
  alert_threshold: 3   # 连续 3 次 healthz 失败 = zombie
  feishu_dm: oc_c653562b
```

### Step 2: 探测循环 (Python pseudocode)
```python
import subprocess, time, json

def detect_zombie():
    # 1. pid alive?
    pid = read_pid_file()
    if not pid or not pid_alive(pid):
        return {'state': 'dead', 'action': 'restart'}
    # 2. healthz responds?
    try:
        out = subprocess.check_output(['curl', '-sS', '-m', '5',
                                        HEALTHZ_ENDPOINT], timeout=5)
        return {'state': 'alive', 'data': json.loads(out)}
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
        return {'state': 'zombie_suspect', 'action': 'wait_next_cycle'}

def loop():
    consecutive_fail = 0
    while True:
        r = detect_zombie()
        if r['state'] == 'alive':
            consecutive_fail = 0
        else:
            consecutive_fail += 1
            if consecutive_fail >= ALERT_THRESHOLD:
                trigger_alert(r)
                trigger_restart()
                consecutive_fail = 0
        time.sleep(INTERVAL_SEC)
```

### Step 3: 触发响应
| State | 动作 |
|---|---|
| `alive` | nothing |
| `dead` (pid gone) | `systemctl --user restart hermes-gateway`, 飞书 DM 通报 |
| `zombie_suspect` (连续 3 次 healthz 失败) | (a) `kill -USR1 <pid>` 触发 gateway 自检 (b) 飞书 DM 通报 + last 50 行 stack (c) 准备 restart |
| `zombie_confirmed` (5 次失败) | 强制 `kill -9 <pid>` + restart |

### Step 4: 飞书 DM (走 hermes send, 不走 send_message)
```bash
# 用 send_message 时, hermes-lark-streaming plugin 可能 suppress (#49334)
# 走"最终 assistant message"路径或 REST API 直连:
curl -X POST 'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id' \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer ${FEISHU_TENANT_TOKEN}" \
  -d '{"receive_id":"oc_c653562b","msg_type":"text","content":"{\"text\":\"🚨 gateway zombie detected: <details>\"}"}'
```

## 何时不该调用
- dev/test 环境不要开,会与 dev loop 撞 (测试环境应该有独立 watchdog)
- 不要与 systemd 自带的 watchdog 重复开 (systemd 已能 Restart=always)
- 不要在 PR #53183 merge 前开 production (zombie_detector 自己也会 zombie)

## 验证
- [ ] 模拟 gateway hang → 30s 内 detector 输出 zombie_suspect
- [ ] 连续 5 次失败后自动 restart + 飞书 DM
- [ ] pid gone 时立即 restart, 不等 3 次失败
- [ ] PR #53183 merge 后, 200 长 response 模拟下 detector 0 alert

## 关联
- 上游 skill: `ai-agent-security-defense` (gateway 死了是 security-relevant)
- 联动 SOUL: `chief-agent-gateway-zombie-exorcism` (派工前置 check)
- 联动 SOUL: `qa-worker-gateway-zombie-repro-test` (PR-time 验证)
- 主 GH issue: #53175
- 主 GH PR: #53183 (P1)