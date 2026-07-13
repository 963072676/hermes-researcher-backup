---
name: hermes-update-handoff-readiness-v1
description: 'Hermes researcher v1 立卡 skill。F10 update handoff + Docker config migration readiness 验证 — 5 profile × config.yaml 跨 release 累积 stale 检测 + raw_config_version_check + non-interactive migrate + opt-out env var。Use when: 任意 researcher tick 报 F10 cron-installer-handoff-state family P1 + 默认 profile 启动 readiness + v0.18.x/v0.19.x release day ship gate。'

# hermes-update-handoff-readiness-v1

> Hermes researcher update handoff readiness v1 (2026-07-13 立卡, tick35)。
> 配套 SOUL:default update_handoff_readiness_v1 + dev f10_docker_migration_dev_fix + chief cross_cluster_integration_v1 F10 立卡 + qa release_verification_v5 f10_docker_migration_check。

## 这个 skill 解决什么

tick35 立卡 F10 cron-installer-handoff-state family,根因 3 层:

1. **#61093 (open)** — Desktop update handoff home resolution — profile-scoped home + base home fallback for staged updater。`resolveUpdaterBinary()` 可能 miss staged `hermes-setup(.exe)`,marker parking 读到不同 home,recovery handoff 跑错 managed checkout。

2. **#35406 (closed but root cause broader)** — Docker image update 不跑 config migration + `check_config_version()` 用错了 source of truth。**closed PR #35458/#35508/#36627 只修了 stage2-hook 加 migrate_config 调用,没修 dev 根因 — `check_config_version()` 读 `_config_version` 从 `load_config()` 来的 effective config,不是 raw on-disk 文件**。raw config 无 `_config_version` 时 inherit 最新 default version,check 误以为"已 migrate"。

3. **5 profile × config.yaml 跨 release 累积 stale** — 任何 release day,如果 user 没主动 `hermes update`(Docker install),`hermes config migrate` 不会跑,persisted config 跨 release 累积 stale,hardening control(F7 MCP hardening / F7 read_pwd permission)不生效。

本 skill 提供 readiness gate 验证,在 default profile 启动 + cron worker 启动 + release day ship gate 时强制跑。

## 何时调用

- 任意 researcher tick 报 F10 cron-installer-handoff-state family P1 → 立即触发
- default profile 启动 → 跑 readiness_gate 5 步
- cron worker 启动 → 跑 cron_worker_checklist 4 项
- v0.18.x / v0.19.x release day → 跑 ship_gate 必过项
- 5 profile × config.yaml 跨 release 累积 stale 检测到 → 升级 chief triage
- Docker install path → 跑 docker_migration_verify 4 项

## 标准流程

### Step 1: HERMES_HOME single source verification

```bash
# 检查 active HERMES_HOME + base home (profiles/ 父目录) 一致性
ACTIVE_HOME="${HERMES_HOME:-$HOME/.hermes}"
BASE_HOME=$(dirname "$ACTIVE_HOME")  # 如果 active 是 profile-scoped, base 是 .hermes

if [ ! -d "$ACTIVE_HOME" ]; then
    echo "FAIL: active HERMES_HOME $ACTIVE_HOME not exist"
    exit 1
fi

# 验证 staged updater 在 active 或 base home
for home in "$ACTIVE_HOME" "$BASE_HOME"; do
    if [ -x "$home/bin/hermes-setup" ] || [ -x "$home/bin/hermes-setup.exe" ]; then
        STAGED_UPDATER="$home/bin/hermes-setup"
        break
    fi
done

if [ -z "$STAGED_UPDATER" ]; then
    echo "FAIL: staged updater not found in active or base home"
    exit 1
fi
```

### Step 2: raw_config_version_check

```python
def read_raw_config_version(path: Path) -> Optional[int]:
    """Read _config_version directly from raw on-disk config.yaml, no merge."""
    if not path.exists():
        return None
    with open(path) as f:
        cfg = yaml.safe_load(f)
    if cfg is None:
        return None
    return cfg.get("_config_version")  # may be None for unversioned raw

def check_config_version_raw_and_effective(home: Path) -> dict:
    """Compare raw on-disk version vs effective load_config() version."""
    raw = read_raw_config_version(home / "config.yaml")
    effective = load_config().get("_config_version")
    return {
        "raw": raw,
        "effective": effective,
        "needs_migrate": raw != effective,
        "raw_unversioned": raw is None,
    }
```

如果 `needs_migrate=True` 或 `raw_unversioned=True` → 触发 migrate (Docker non-interactive / Linux interactive)。

### Step 3: cron worker no_agent end_session verification

```bash
# 抽样 5 个最近的 cron no_agent session, 验证 end_session 被调用
sqlite3 ~/.hermes/state.db "
SELECT COUNT(*) FROM sessions
WHERE source='cron'
AND ended_at IS NULL
AND started_at < datetime('now', '-7 day')
" > zombie_count

if [ "$zombie_count" -gt 5 ]; then
    echo "FAIL: zombie cron session count $zombie_count > 5 (F5 #41935 + F9 #63128 cross-cluster)"
    exit 1
fi
```

### Step 4: update marker dual-home write verification

```bash
# 检查 pre-written update markers 覆盖 active + base home
for home in "$ACTIVE_HOME" "$BASE_HOME"; do
    if [ ! -f "$home/.update_marker" ] && [ ! -f "$home/.update_in_progress" ]; then
        continue  # no marker, OK
    fi
    # If marker exists, verify it points to the right updater
    grep -l "staged_updater" "$home/.update_marker" 2>/dev/null && {
        echo "FAIL: update marker at $home points to wrong updater"
        exit 1
    }
done
```

### Step 5: trust boundary e2e (5 项,FORBIDDEN to skip)

沿用 hermes-trust-boundary-e2e-v1 的 4 tests:
- fabrication / fail-open / observer disconnect / info_disclosure

### Step 6: 集成到 default profile readiness_gate

```bash
#!/bin/bash
# qa/scripts/update-handoff-readiness.sh

set -e

ACTIVE_HOME="${HERMES_HOME:-$HOME/.hermes}"
BASE_HOME=$(dirname "$ACTIVE_HOME")

echo "Step 1: HERMES_HOME single source"
bash /tmp/step1_home_single_source.sh

echo "Step 2: raw_config_version_check"
python3 -c "
from hermes_cli.config import read_raw_config_version, load_config
import sys
result = check_config_version_raw_and_effective(Path('$ACTIVE_HOME'))
if result['needs_migrate']:
    print(f'FAIL: raw {result[\"raw\"]} != effective {result[\"effective\"]}')
    sys.exit(1)
"

echo "Step 3: cron worker no_agent end_session"
bash /tmp/step3_cron_no_agent_audit.sh

echo "Step 4: update marker dual-home write"
bash /tmp/step4_update_marker_dual.sh

echo "Step 5: trust boundary e2e"
bash qa/scripts/trust-boundary-e2e.sh

echo "Update handoff readiness: all pass"
```

## 标准输出模板

```markdown
# Update handoff readiness result — YYYY-MM-DD (tickN)

## Step results

- Step 1 (HERMES_HOME single source): PASS / FAIL
- Step 2 (raw_config_version_check): PASS / FAIL
  - raw: 28 / None
  - effective: 32
  - needs_migrate: True / False
- Step 3 (cron worker no_agent end_session): PASS / FAIL
  - zombie session count: 0 / > 5
- Step 4 (update marker dual-home write): PASS / FAIL
- Step 5 (trust boundary e2e): PASS / FAIL

## Cross-cluster arrows status

- CCA-2 (F7 MCP hardening ↔ F10 Docker migration gap): stale config detected → migrate triggered
- CCA-3 (F9 lock fail-open ↔ F8 ticker silent die): checked in step 5

## Readiness gate decision

- if all 5 steps PASS → readiness gate allow
- if any FAIL → readiness gate BLOCK + 飞书报警
- emergency skip:
  - HERMES_READINESS_SKIP=update_handoff (only for hotfix)
  - HERMES_READINESS_SKIP=docker_migration (only for non-Docker install)
  - HERMES_READINESS_SKIP=trust_boundary (FORBIDDEN)
```

## 失败回退

- 5 steps 任意 FAIL → readiness gate BLOCK + 立即升级 chief + 飞书报警
- Step 2 (raw_config_version) FAIL → 自动触发 `hermes config migrate --non-interactive`
- Step 3 (cron worker) FAIL → 立即 `end_session` 清理 zombie, 然后 retry
- Step 5 (trust boundary) FAIL → FORBIDDEN to skip, ship gate BLOCK

## 验证清单

- [ ] 5 steps 全部 PASS 才允许升级 / 启动 cron worker / ship
- [ ] 任意 FAIL 立即升级 chief
- [ ] Step 2 raw_config_version_check 必须 dev 升级后跑通
- [ ] Step 3 cron worker zombie 阈值 ≤ 5
- [ ] 跨 release 累积 readiness 状态

## 配额(防刷屏)

- 每日 readiness_gate 必跑(no quota,必须跑)
- 飞书 readiness 报警不限制
- Step 2 migrate 触发不限次数

## 相关 references

- `references/update-handoff-readiness-tick35.md` — tick35 实战 5 steps + 测例
- `references/f10-docker-migration-fix.md` — dev 角度 fix strategy

## Pitfalls

### tick35 - raw_config_version_check 不可只读 effective,必须 raw + effective 双读

**触发**:tick35 Step 2 写 `check_config_version_raw_and_effective()` 时,如果只读 effective(沿用 Hermes 原代码),raw missing _config_version 时 effective 已是最新 default version(通过 deep-merge),check 误以为"已 migrate",F10 #35406 根因未修。

**修正**:必须双读,raw 优先。raw != effective 或 raw is None → 触发 migrate。

### tick35 - Docker non-interactive migrate 必须 backup config.yaml + .env

**触发**:tick35 Step 2 migrate 触发时,如果直接 rewrite config.yaml + .env 而不备份,user 现有 config 丢失。

**修正**:Docker non-interactive migrate 必须先:
```bash
cp -a "$HERMES_HOME/config.yaml" "$HERMES_HOME/config.yaml.bak.$(date -u +%Y%m%dT%H%M%SZ)"
cp -a "$HERMES_HOME/.env" "$HERMES_HOME/.env.bak.$(date -u +%Y%m%dT%H%M%SZ)"
```
然后再跑 migrate。

### tick35 - cron worker zombie 阈值不可太低,避免误杀

**触发**:tick35 Step 3 阈值 ≤ 5,如果 user 有 6 个 cron job 跑长 LLM turn(每个 turn 30 分钟),可能 > 5 zombie,但实际是 in-progress 不是 leaked。

**修正**:zombie 阈值 ≤ 5 + zombie age ≥ 7 day 才算 leak。in-progress session(最近 30 分钟 active)不算 zombie。

### tick35 - HERMES_SKIP_CONFIG_MIGRATION 不可 silent skip

**触发**:tick35 opt-out env var 如果 silent skip,user 不知道自己 config 累积 stale。

**修正**:skip 时必须写 warning log + 飞书报"skip detected, config may be stale"。