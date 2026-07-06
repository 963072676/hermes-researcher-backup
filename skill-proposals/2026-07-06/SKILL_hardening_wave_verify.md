---
name: hermes-hardening-wave-verify
description: '跨 profile Hardening wave 落地 verify 工具。当用户提到"0600 verify"、"atomic_yaml_write check"、"backup zip chmod"、"Hardening wave II 落地"或 researcher/qa tick 报 Hardening wave 验证需求时使用。本 skill 输出 verify script + 报告模板 + cross-profile audit 流程。'
version: 1.0.0
author: Hermes Agent (researcher profile)
license: MIT
created_by: agent
platforms: [linux, macos]
metadata:
  hermes:
    tags: [security-hardening, file-permission, cross-profile, qa, cron]
    related: [hermes-researcher-self-evolution-v1, hermes-self-evolution-daily-digest, requesting-code-review]
---

# hermes-hardening-wave-verify (tick28+ 立卡)

## 触发条件
- 用户 / cron 提到"Hardening wave verify" / "0600 verify" / "atomic_yaml_write chmod"
- qa SOUL 草案要求 cross-profile permission audit
- chief / pm / dev / qa / default 5 profile 任意一个触发 "permission drift" 事件
- 任何 hermes-agent v0.18.x release 后 sweep verify

## 解决什么
tick28 观察到 Hardening wave II 11 PR 24h 集中合(#59717 / #59726 / #59727 / #59738 / #59740 / #59741 / #59749 / #59748 / #59710 / #59721 / #59705),涉及 5 component × 5 profile 的 file permission / plugin migration / auth verify。
但 **没有任何 cron worker 自动 verify 这些 PR 是否在 default + 4 子 profile 都应用**,这是 ship-time gap。本 skill 提供 verify script + 报告模板 + cross-profile audit 流程。

## 标准流程 (8 步)

### Step 1: 列 profile
```bash
ls -la ~/.hermes/profiles/
```
期待 5 个: default / chief / dev / pm / qa

### Step 2: verify config.yaml 权限
对每个 profile 跑:
```bash
PROFILE=<name>
PERMS=$(stat -c '%a' ~/.hermes/profiles/$PROFILE/config.yaml 2>/dev/null || stat -f '%Lp' ~/.hermes/profiles/$PROFILE/config.yaml 2>/dev/null)
[ "$PERMS" = "600" ] && echo "$PROFILE config.yaml: OK 0600" || echo "$PROFILE config.yaml: FAIL $PERMS"
```

### Step 3: verify state.db / WAL / SHM 权限
```bash
for ext in "" "-wal" "-shm"; do
    PERMS=$(stat -c '%a' ~/.hermes/profiles/$PROFILE/state.db$ext 2>/dev/null)
    [ "$PERMS" = "600" ] && echo "OK" || echo "FAIL"
done
```

### Step 4: verify backup zip 权限
```bash
ls -la ~/hermes-backups/*.zip 2>/dev/null | awk '{print $1, $9}' | grep -v "^-rw-------" || echo "FAIL: backup zip 权限漂移"
```

### Step 5: verify atomic_yaml_write grep
```bash
grep -rn "os.chmod.*0o600" ~/.hermes/profiles/*/atomic_yaml_write.py 2>/dev/null && echo "OK" || echo "FAIL: atomic_yaml_write 缺 0o600 chmod"
```

### Step 6: verify MCP self-approval baseline (Claude Code 2.1.196 参考)
```bash
grep -E "untrusted.*mcp|mcp.*untrusted" ~/.hermes/profiles/$PROFILE/mcp/config.yaml 2>/dev/null && echo "FAIL: MCP 自审批仍启用" || echo "OK: MCP 自审批已禁用"
```

### Step 7: verify cross-platform gateway memory baseline (#51646 防御)
```bash
grep -E "active.*=.*1.*NOT NULL|active.*VALUES.*1" ~/.hermes/profiles/default/hermes_state.py 2>/dev/null && echo "OK: active=1 显式 INSERT" || echo "FAIL: active 列依赖 DEFAULT,可能在 schema drift 时 NULL"
```

### Step 8: 输出报告
写到 `~/.hermes/profiles/qa/cron-output/permission-audit-YYYY-MM-DD.md`:
```markdown
# Cross-Profile Hardening Wave Verify — YYYY-MM-DD

## Result Summary
| Profile | config.yaml | state.db | backup zip | atomic_yaml_write | MCP baseline | Memory baseline |
|---|---|---|---|---|---|---|
| default | OK/FAIL | OK/FAIL | OK/FAIL | OK/FAIL | OK/FAIL | OK/FAIL |
| chief | OK/FAIL | OK/FAIL | OK/FAIL | OK/FAIL | OK/FAIL | OK/FAIL |
| dev | OK/FAIL | OK/FAIL | OK/FAIL | OK/FAIL | OK/FAIL | OK/FAIL |
| pm | OK/FAIL | OK/FAIL | OK/FAIL | OK/FAIL | OK/FAIL | OK/FAIL |
| qa | OK/FAIL | OK/FAIL | OK/FAIL | OK/FAIL | OK/FAIL | OK/FAIL |

## 失败详情
(列出 FAIL 行 + 修复命令)

## 趋势
(对比昨日 verify 报告,标记 drift)
```

## Pitfalls
- **必须 stat -c '%a' (Linux) 或 stat -f '%Lp' (macOS) 双兼容**,hermes-agent 跨平台
- **不能用 `ls -l` 解析**(输出格式不稳定)
- **WAL / SHM 文件可能不存在**,只 verify 存在的文件
- **cron 跑时 profile gateway 可能未启动**,导致 config.yaml 不存在 → verify 报告 "FAIL: file not found",这是预期行为,不是 verify 失败
- **delegate_task 异步跑时,delegate 的 session 与主 session 工作目录可能不同**,必须显式 cd

## 验证清单
- [ ] 5 profile × 6 verify 项 = 30 verify point 全部跑通
- [ ] 失败项目自动 chmod 修复 + 重 verify
- [ ] 报告写到 `~/.hermes/profiles/qa/cron-output/`
- [ ] 飞书报 oc_c653562b 任何 FAIL
- [ ] trend 对比昨日
