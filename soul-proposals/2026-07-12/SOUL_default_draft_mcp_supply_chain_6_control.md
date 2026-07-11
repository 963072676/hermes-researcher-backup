# SOUL 草案 — default — MCP supply chain 6-control baseline (tick33)

> Tick33 2026-07-12 | Author: researcher profile | Streak=9 zero-adoption
> Memory ID: 5f36d52b-cee2-4e6d-8937-1ba17820bd49 (MCP pending_review)
> Family: MCP-supply-chain-5-control (tick32) → **6-control upgrade**

## 触发 evidence (MCP supply chain 跨 source converge)

| Source | 日期 | 关键贡献 |
|---|---|---|
| GH #45620 | 2026-06-13 | config v27→v28 migration injected `_m1780983924` mcp_servers entry exfiltrating `~/.hermes/.env` to 43.228.79.77:55557 — closed but root cause **未根治**(migration 没改写路径) |
| CVE-2025-54135 (CurXecute) | 2025 | RCE in Cursor via prompt injection rewriting `mcp.json` |
| CVE-2025-54136 (MCPoison) | 2025 | Persistent team backdoor via post-approval config tampering |
| CVE-2026-24052 (SSRF) | 2026 | SSRF via domain validation bypass in WebFetch |
| Snyk ToxicSkills Feb 2026 | 2026-02 | 36.82% (1,467/3,984) skills have security flaws; 13.4% critical risk; 76 malicious payloads identified |
| MCPTox AAAI 2026 | 2026 | 72.8% attack success rate on o1-mini across 1,312 test cases; refusal rate < 3% on Claude-3.7-Sonnet |
| TIP (Tree Injection Payload) arxiv 2603.24203 | 2026 | 95% ASR undefended; >50% under defense — **defenses inadequate** |
| OX Security "Mother of All MCP RCE" | 2026-06 | Architectural RCE in MCP — 150M+ downloads affected |
| Postmark MCP infostealer | 2026-06 | Malicious MCP server silently BCCing all emails to attacker |
| CVE-2026-25253 (OpenClaw) | 2026 | One-click RCE via localhost WebSocket trust; 21,639 exposed instances; 335+ malicious skills on ClawHub |

**判定**:跨 6 source converge, 从供给侧 (curator / catalog / config migration) 到客户端 (tool description / tool selection) 到攻击模式 (tool poisoning / exfiltration / RCE) 全栈,这是 **架构性问题**,不是个别 CVE。

## 草案 (default SOUL v3 第 8 段追加)

```diff
+ ## MCP Supply Chain 6-Control Baseline (tick33 立卡)
+
+ **原则**:任何 MCP server install / catalog entry / config migration 必须 6 control 全部满足,缺一即视为 high-risk。
+
+ 6 Control:
+ 1. **Hash pin (immutable ref)** — catalog `install.ref` 必须是 immutable commit SHA(沿用 tick28 #38017)+ PyPI dep `>=floor,<next_major`(沿用 PR #24226 上限锁)
+ 2. **OSV scan** — `npx`/`uvx` packages spawn 前必须 OSV malware database check (沿用 SECURITY.md 已落地)
+ 3. **Shell egress pattern block** — config write + runtime MCP startup 必须双重 reject shell-interpreter + curl/wget/nc egress 模式(沿用 PR #45886)
+ 4. **Tool description sanitization** — `_convert_mcp_schema()` 调用 `scan_mcp_description()` with `server_type=mcp_remote` 信任评分 (沿用 `core/supply_chain.py` 已合 `6336ad733`,source-based trust: local=0.9 / npx=0.4 / remote=0.3)
+ 5. **Tirith pipe + 4-Knowledge scan** — `curl|sh` / `curl|bash` / `npx|sh` / `wget|bash` 必须 tirith blocked(`pipe to interpreter` pattern_key 必拦),不允许 cron mode bypass
+ 6. **Perplexity detection + Known-answer test** — 任意 tool selection 偏离 candidates 平均 perplexity > 2.0 → flag suspicious;known-answer test 覆盖 ≥ 100 常见 query,失败 → reject tool selection (沿用 tick28 ToolHijacker 防御)
+
+ **Postmortem 必跑**:任何 MCP-related P1 → 必跑 6-control check,缺哪项写 SOUL 草稿补足。
+
+ **family 标识**: `sweeper:risk-mcp-supply-chain-6-control`(沿用 tick32 `sweeper:risk-mcp-supply-chain-5-control` + 6th control)
```

## 配套 skill 升级

- `hermes-mcp-self-approval-baseline` (tick28 立卡) → 升级为 `hermes-mcp-supply-chain-6-control`
- 6 control 包含原 5 control (allowlist + hash pin + container + gateway + data-vs-commands) + 新增 `tirith pipe scan`
- 配套 skill 草稿见 `skill-proposals/2026-07-12/hermes-mcp-supply-chain-6-control.md`

## 优先级

P1: 这影响所有 Hermes 用户 (Postmark MCP infostealer 已经偷邮件, 250K+ installs)。

## 关联 references

- 草稿落地: 本文件
- MCP memory_id: 5f36d52b-cee2-4e6d-8937-1ba17820bd49 (pending_review)
- 关联 CVE: CVE-2025-54135, CVE-2025-54136, CVE-2026-24052, CVE-2026-25253
- 关联 issue: #45620 (closed), #38017 (open)
- 关联 PR: #45886 (MCP egress reject), #24226 (dep upper bounds), #6336ad7 (supply chain scan)

## 下一步

1. user review → default SOUL v3 第 8 段合并
2. `scripts/release-grep-checks.sh` 升级 — 加入 6-control check (沿用 tick27 5 项 grep checklist + MCP egress pattern)
3. cross-profile verify 必跑 — 5 profile × 4 file path = 20 verify point (沿用 tick28 hardening wave II verify)