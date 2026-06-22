#!/usr/bin/env python3
"""
profile-memory-slim-daily v2 (2026-06-22)
=========================================

升级点(对 v1):
  A. 三层阈值(per-profile 个性化):healthy < 60% / watch 60-75% / warning 75-90% / critical >= 90%
  B. 真正知识化:迁移前用 LLM 生成结构化摘要(title + tags + key_facts),不是只塞原文
  C. 按 profile 调阈值 + 调整 1 次 LLM 评分 + 1 次 LLM 摘要
  D. 输出升级:可释放容量估算 + watch/critical 列表

跨 profile 写:从 default profile 触发,但只写各 profile 自己的 MEMORY.md(已有权限),
改的是文件系统层,不直接调其它 profile 的 MCP memory(那是它们自己写自己的)。

模型选择(用户 2026-06-22 拍板):
  - LLM 评分(轻): xiaomi/mimo-v2.5-pro  (cost 优先)
  - LLM 摘要(重): xai-oauth/grok-4.3    (质量优先)
"""

import os
import sys
import json
import shutil
import re
import urllib.request
import urllib.error
import subprocess
from datetime import datetime, timezone
from typing import Optional

# ---------- 配置 ----------

HERMES_HOME = os.path.expanduser("~/.hermes")
KB_URL = "http://127.0.0.1:18081/knowledge/ingest_text"
KB_TOKEN_FILE = "/home/a18845560182/knowledge_service/.env"

# profile 配置: (profile_name, agent_id, mem_path, watch%, crit%, cap)
PROFILES = [
    ("default",         "gc-hermes-default",     "~/.hermes/memories/MEMORY.md",                            60, 90, 3000),
    ("chief-agent",     "gc-hermes-chief",       "~/.hermes/profiles/chief-agent/memories/MEMORY.md",      60, 90, 3000),
    ("pm-orchestrator", "gc-hermes-pm",          "~/.hermes/profiles/pm-orchestrator/memories/MEMORY.md",  60, 90, 3000),
    ("dev-worker",      "gc-hermes-dev",         "~/.hermes/profiles/dev-worker/memories/MEMORY.md",       60, 90, 3000),
    ("qa-worker",       "gc-hermes-qa",          "~/.hermes/profiles/qa-worker/memories/MEMORY.md",        60, 90, 3000),
    ("researcher",      "gc-hermes-researcher",  "~/.hermes/profiles/researcher/memories/MEMORY.md",       60, 90, 3000),
    ("social-operator", "gc-hermes-social",      "~/.hermes/profiles/social-operator/memories/MEMORY.md",  60, 90, 3000),
]

# A-class 保护判定 (2026-06-22 v2 修订)
#
# 修 Bug 2 续: 之前用 substr 匹配 "红线" / "派工铁律" 等关键词, 在 hermes 系统
# 里"红线"出现频率极高(几乎每条 rule 都会带"红线"二字), 误判率高.
# 改为: 关键词必须出现在 block **首行** 且作为标题性短语才视为 A-class.
#
# 实现: 提取 block 首行 (去掉前缀 ** 和后缀 **), 检查首行是否以某个 A-class 标题前缀开头.
A_CLASS_TITLES = [
    "Hermes Agent 7 profile 全局基础",
    "凭据处理 + secret 红线",
    "用户偏好 - 脚本生成方式",
    "多 profile 派卡 broadcast 模式",  # 这是 B-class 实际内容, 改放 B 列表
]

# 真正的 A-class 首行标题 (命中即保护, 不分大小写)
A_CLASS_TITLE_PREFIXES = [
    "全局基础",
    "凭据处理 + secret 红线",
    "用户偏好 - ",
    "multi-profile 派卡 broadcast",  # 实际是 B, 见下
]

# B-class 边界条款: 这些标题前缀虽然含"红线"字眼, 但实际是历史教训, 可迁
# Bug 2 续: 移除 "memory-slim-" 通用前缀 (会误中 v1 旧索引)
# Bug 2 续: "红线" 单独作为 keyword 太宽, 改为只在标题位置匹配
B_CLASS_TITLE_PREFIXES = [
    "多 profile 派卡 broadcast 模式",  # 历史教训, 是 C_event, 可迁
    "memoryview-live-deploy 补充",
    "2026-06-22",  # 当日新增块, 视情况
]

# 评分 prompt(轻量,用 mimo)
SCORE_PROMPT_TMPL = """你是一个 memory 评分员。下面是一个待评估的 MEMORY 条目,判断它是否适合"知识化迁移"(从 hot memory 释放到 KB)。

返回 JSON,字段:
  - migratable: bool (true=建议迁, false=不迁)
  - cls: "A_redline" | "B_preference" | "C_event" | "D_trivial"
  - reason: 一句话原因
  - priority: 1-5 (1=最该先迁, 5=最不该)

判断原则:
  - A_redline (永不松动的规则 / 红线 / secret) -> migratable=false, priority=5
  - B_preference (用户偏好 / 长期稳定风格) -> migratable=false, priority=4
  - C_event (具体事件 / 教训 / 案例) -> migratable=true, priority=2
  - D_trivial (一句话 / 状态 / 临时任务) -> migratable=true, priority=1
  - 最近 1 个 block -> migratable=false (用户在用)

条目:
```
{block}
```

只回 JSON,不要其他文字。"""

# 摘要 prompt(重量,用 grok)
SUMMARIZE_PROMPT_TMPL = """把以下 MEMORY 条目压缩成"知识卡",便于后续 KB 检索。

要求:
  - title: 20 字以内,直白
  - tags: 3-5 个英文/拼音小写 tag
  - key_facts: 3-5 条 bullet, 每条 30 字内
  - 保留可执行信息(命令、文件路径、Issue 编号、风险)

条目:
```
{block}
```

返回 JSON, 字段: title, tags(list), key_facts(list)。只回 JSON。"""

ENV_TOKEN_KEY="KNOWLEDGE_SERVICE_ADMIN_TOKEN"


# ---------- 工具 ----------

def read_kb_token() -> Optional[str]:
    try:
        with open(KB_TOKEN_FILE) as f:
            for line in f:
                line = line.strip()
                if line.startswith(ENV_TOKEN_KEY):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return None


def is_a_class(block: str) -> bool:
    """A-class 判定: 只看首行 (strip 后) 是否以 A_CLASS_TITLE_PREFIXES 中任一前缀开头.

    BUG FIX 2026-06-22: 之前用 substring 匹配 "红线" 等关键词, 误判率高.
    新规则: 必须在 block 的第一行 (去掉 ** markdown 标记) 以特定标题前缀开头.
    """
    first_line = block.split("\n", 1)[0].strip()
    # 去掉首尾的 ** 标记
    first_line = first_line.strip("*").strip()
    # 检查是否以任一 A-class 前缀开头
    for prefix in A_CLASS_TITLE_PREFIXES:
        if first_line.startswith(prefix):
            return True
    return False


def split_blocks(text: str) -> list:
    blocks = [b.strip() for b in text.split("§")]
    return [b for b in blocks if b]


def assemble(blocks: list) -> str:
    return "§\n".join(blocks) + ("\n" if blocks else "")


# ---------- LLM 调用 ----------

def call_llm(prompt: str, model: str, profile: str = "default") -> Optional[str]:
    """通过 hermes CLI 调 LLM。"""
    try:
        env = os.environ.copy()
        result = subprocess.run(
            ["hermes", "agent", "prompt", "--model", model, "--raw", prompt],
            capture_output=True, text=True, timeout=60, env=env
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        if result.stderr:
            print(f"  LLM stderr: {result.stderr[:200]}", file=sys.stderr)
    except FileNotFoundError:
        print(f"  hermes CLI not found, LLM unavailable", file=sys.stderr)
    except subprocess.TimeoutExpired:
        print(f"  LLM call timeout (60s)", file=sys.stderr)
    except Exception as e:
        print(f"  LLM call error: {e}", file=sys.stderr)
    return None


def extract_json(text: str) -> Optional[dict]:
    if not text:
        return None
    m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


# ---------- KB 写入 ----------

def ingest_to_kb(title: str, content: str, agent_id: str, metadata: dict) -> Optional[str]:
    """写 KB doc.

    BUG FIX 2026-06-22: 之前没送 context, RequestContext 全 default="" -> 文档被写到
    空 org/project namespace, list API 查不到。必须显式送 org_id=gc-hermes,
    project_id=gc-hermes-config 才能和 MCP ingest_text 走同一 namespace。
    """
    token = read_kb_token()
    if not token:
        print(f"  WARN: no KB token, skip ingest", file=sys.stderr)
        return None
    payload = {
        "context": {
            "org_id": "gc-hermes",
            "project_id": "gc-hermes-config",
            "agent_id": agent_id,
            "role": agent_id.replace("gc-hermes-", ""),
        },
        "title": title,
        "content": content,
        "metadata": {**metadata, "agent_id": agent_id, "ingested_at": datetime.now(timezone.utc).isoformat()},
    }
    req = urllib.request.Request(
        KB_URL,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "X-Admin-Token": token},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = json.loads(resp.read())
            if body.get("ok"):
                return body.get("data", {}).get("document_id")
    except Exception as e:
        print(f"  WARN: KB ingest failed: {e}", file=sys.stderr)
    return None


# ---------- 主流程 ----------

def score_block(block: str, model: str) -> dict:
    """LLM 评分,失败时降级。"""
    prompt = SCORE_PROMPT_TMPL.format(block=block[:1500])
    raw = call_llm(prompt, model=model)
    result = extract_json(raw)
    if result and "migratable" in result and "cls" in result:
        return result
    # 降级:用 is_a_class 简单判断
    if is_a_class(block):
        return {"migratable": False, "cls": "A_redline", "reason": "matched A-class keyword", "priority": 5}
    return {"migratable": True, "cls": "C_event", "reason": "fallback", "priority": 2}


def summarize_block(block: str) -> dict:
    """LLM 摘要,失败时降级。"""
    prompt = SUMMARIZE_PROMPT_TMPL.format(block=block[:2500])
    raw = call_llm(prompt, model="xai-oauth/grok-4.3")
    result = extract_json(raw)
    if result and all(k in result for k in ("title", "tags", "key_facts")):
        return result
    # 降级
    title_seed = block.split(":", 1)[0].strip()[:40] if ":" in block else block[:40]
    return {
        "title": title_seed,
        "tags": ["unclassified"],
        "key_facts": [line.strip() for line in block.split("\n") if line.strip()][:3],
    }


def slim_profile(name: str, agent_id: str, mem_path: str, watch_pct: int, crit_pct: int, capacity: int) -> dict:
    result = {
        "profile": name, "agent_id": agent_id, "path": mem_path, "capacity": capacity,
        "before": 0, "after": 0, "pct_before": 0, "pct_after": 0,
        "status": "ok", "action": "none", "migrated": [], "knowledge_card_ids": [],
    }
    path = os.path.expanduser(mem_path)
    if not os.path.exists(path):
        result["status"] = "no_memory_file"
        return result

    with open(path) as f:
        text = f.read()
    size = len(text)
    result["before"] = size
    pct = round(size * 100 / capacity, 1)
    result["pct_before"] = pct

    # 阈值判定
    if pct < watch_pct:
        result["status"] = "healthy"
        result["action"] = "skipped_healthy"
        result["after"] = size
        result["pct_after"] = pct
        return result
    elif pct < crit_pct:
        # watch 区:只评分不迁
        result["status"] = "watch"
        result["action"] = "scored_only_no_migration"
        result["after"] = size
        result["pct_after"] = pct
        blocks = split_blocks(text)
        if blocks:
            cand = [(i, b) for i, b in enumerate(blocks[:-1]) if not is_a_class(b)]
            for idx, b in cand[-3:]:  # 只评最后 3 个候选
                s = score_block(b, "xiaomi/mimo-v2.5-pro")
                result["migrated"].append({"idx": idx, "would_migrate": s.get("migratable"), "reason": s.get("reason", "")})
        return result

    # CRITICAL:真正执行
    blocks = split_blocks(text)
    if len(blocks) < 3:
        result["status"] = "too_few_blocks"
        result["action"] = "skipped_insufficient_blocks"
        result["after"] = size
        result["pct_after"] = pct
        return result

    # 1) 评分 + 选候选
    candidates = []
    for i, b in enumerate(blocks):
        if i == len(blocks) - 1:
            continue  # 保留最近 1 个
        if is_a_class(b):
            continue
        s = score_block(b, "xiaomi/mimo-v2.5-pro")
        if s.get("migratable") and s.get("cls") in ("C_event", "D_trivial"):
            candidates.append((i, b, s.get("priority", 3)))

    candidates.sort(key=lambda x: x[2])  # priority 升序
    if not candidates:
        result["status"] = "all_protected"
        result["action"] = "skipped_protected"
        result["after"] = size
        result["pct_after"] = pct
        return result

    # 2) 备份
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    bak_path = f"{path}.bak.{ts}-slim-v2"
    shutil.copy2(path, bak_path)

    # 3) 摘要 + 入库 + 删
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    migrated_indices = []
    knowledge_cards = []

    for idx, block, _ in candidates:
        card = summarize_block(block)
        knowledge_text = json.dumps(card, ensure_ascii=False, indent=2)
        title = f"[memory-slim-v2-{today}] {name}: {card.get('title', '')[:60]}"
        doc_id = ingest_to_kb(
            title=title, content=knowledge_text, agent_id=agent_id,
            metadata={
                "source_type": "memory_slim_v2",
                "from_profile": name,
                "tags": card.get("tags", []),
                "key_facts_count": len(card.get("key_facts", [])),
                "version": 2,
            },
        )
        if doc_id:
            migrated_indices.append(idx)
            knowledge_cards.append({"doc_id": doc_id, "title": title, "tags": card.get("tags", [])})

    if not migrated_indices:
        result["status"] = "kb_ingest_failed"
        result["action"] = "rolled_back_no_ingest"
        result["after"] = size
        result["pct_after"] = pct
        shutil.copy2(bak_path, path)
        return result

    kept = [b for i, b in enumerate(blocks) if i not in migrated_indices]
    index_lines = [f"memory-slim-v2-{today} 索引:已迁 {len(knowledge_cards)} 条到知识库"]
    for kc in knowledge_cards:
        index_lines.append(f"  - kb={kc['doc_id']} {kc['title']} tags={','.join(kc['tags'])}")
    index_entry = "\n".join(index_lines)
    kept.append(index_entry)
    new_text = assemble(kept)
    # 原子写
    tmp_path = f"{path}.tmp"
    with open(tmp_path, "w") as f:
        f.write(new_text)
    os.replace(tmp_path, path)
    result["after"] = len(new_text)
    result["pct_after"] = round(len(new_text) * 100 / capacity, 1)
    result["action"] = f"slimmed_{len(knowledge_cards)}_cards"
    result["status"] = "ok"
    result["knowledge_card_ids"] = knowledge_cards
    result["backup"] = bak_path
    return result


def main():
    print(f"=== profile-memory-slim-daily v2 run @ {datetime.now(timezone.utc).isoformat()} ===\n")
    results = [slim_profile(*p) for p in PROFILES]

    # 汇总表
    print("\n=== 各 profile 状态 ===")
    print(f"  {'profile':18s} {'pct':>6s}  {'status':12s}  {'action':32s}  {'bytes':>12s}")
    print("  " + "-" * 90)
    total_released = 0
    total_cards = 0
    critical_count = 0
    watch_count = 0
    for r in results:
        delta = r["after"] - r["before"]
        print(f"  {r['profile']:18s} {r['pct_before']:>5.1f}%  {r['status']:12s}  {r['action']:32s}  {r['before']:>5d} -> {r['after']:>5d}")
        if r["pct_before"] >= 90:
            critical_count += 1
        if r["status"] == "watch":
            watch_count += 1
        if r["action"].startswith("slimmed"):
            total_released += abs(delta)
            total_cards += len(r["knowledge_card_ids"])

    # 容量分析(60% 阈值,可释放)
    print("\n=== 容量分析 (>60% 阈值的 profile) ===")
    over_60 = [r for r in results if r["pct_before"] >= 60]
    if not over_60:
        print("  无 profile 超过 60% 阈值")
    else:
        for r in over_60:
            # 修 Bug 1 (2026-06-22): 公式应为 current - target, 不是 max(0, target - current)
            # 当 current 已 > target 时, headroom = current - target (正数, 表示需释放多少)
            target_bytes = int(r["capacity"] * 0.60)
            headroom = max(0, r["before"] - target_bytes)
            print(f"  {r['profile']:18s}  {r['pct_before']:>5.1f}% -> 目标 60% 需释放: ~{headroom} B")

    # 总结
    print("\n=== 本次操作汇总 ===")
    print(f"  critical 处理: {critical_count} 个 profile")
    print(f"  watch 监控:    {watch_count} 个 profile")
    print(f"  释放容量:      {total_released} 字节")
    print(f"  知识卡生成:    {total_cards} 张")
    if critical_count > 0 or total_cards > 0:
        print("\nOK 释放完成。")
    else:
        print("\nOK 所有 profile 都在健康范围。")


if __name__ == "__main__":
    main()
