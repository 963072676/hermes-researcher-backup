---
name: cron-profile-sanity
description: 当 hermes cron 报 "Script not found" 时, 自动 cross-profile 探测脚本位置 + 建议 fix。Use when: 任何 cron job fire 报 path 错误, 怀疑 #54288-style active-profile-vs-job-profile mismatch。
---

# cron-profile-sanity

> Hermes cron 多 profile 路径解析问题诊断 + 自动 fallback 推荐。

## 何时调用

- `hermes cron list --profile <X>` 报 "Script not found" 而脚本在另一 profile 下存在
- 多 profile 环境 (≥ 2 个 profile 同时 active)
- 切换 active profile 后 cron 行为异常 (脚本路径错)

## 标准流程

### Step 1: 探针当前状态

```bash
# 找 cron job 的 profile 字段
hermes cron list --json 2>&1 | python3 -c "
import sys, json
jobs = json.load(sys.stdin)
for j in jobs:
    print(f'job={j[\"name\"]:<30} profile={j.get(\"profile\",\"<unset>\"):<12} script={j.get(\"script\",\"?\")}')
"
```

### Step 2: 探测所有 profile 的 scripts 目录

```bash
for prof in chief pm dev qa researcher default; do
  echo "=== profile=$prof ==="
  ls -la ~/.hermes/profiles/$prof/scripts/ 2>/dev/null | head -10
done
```

### Step 3: 判定

- 若 job.profile=unset 且 active profile=researcher → `_get_hermes_home()` 返回 researcher home → 找 chief script 失败 → **#54288 confirmed**
- 若 job.profile=explicit (e.g. "chief") → 路径应解析到 `~/.hermes/profiles/chief/scripts/` → 若失败是 bug

### Step 4: 修复建议

- **临时 fix**: 在 job 创建时显式 `--profile <X>`, 不依赖 active profile
- **永久 fix**: 跟 PR #54288 (待开) 的 solution, 等 main ship
- **Workaround**: 用 `~/.hermes/scripts/<job-name>.sh` 软链到各 profile 共享目录

### Step 5: 验证

```bash
# 跑一遍 dry-run
hermes cron run --profile chief --dry-run --job hermes-self-evolution-digest 2>&1 | head -20
```

## 何时不该调用

- 单 profile 环境 (只有 default), 不存在 cross-profile 冲突
- 脚本确实不存在, 与 profile 无关

## Pitfalls

- **`hermes cron list --json` 字段名 version drift**: 不同版本可能用 `profile`/`profile_name`/`job_profile`, 用 `j.keys()` 探测后再取
- **HERMES_HOME env override**: 若用户设了 `HERMES_HOME=/custom/path`, `_get_hermes_home()` 返回 override 而非 default profile path, **会与 #54288 现象叠加**

## 关联监控

- GH #54288 (open 2026-06-28) — issue 本身
- 待开 PR — 解决方案 (cron/scheduler.py 改用 job.profile)