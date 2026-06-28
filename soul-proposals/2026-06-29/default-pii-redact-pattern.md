# SOUL 草案: default / PII Redaction Pattern in Issues

**针对 issue**: GH #54305 (URGENT Issue open, P2 security) — Issues #43769 #43770 accidentally leaked private business email + GCP project ID + service account email
**风险等级**: P2 security hygiene / awareness-only
**confidence**: 0.8 (环境无关,但模式相关)
**触发源**: https://github.com/NousResearch/hermes-agent/issues/54305

## 当前文本(在 ~/.hermes/profiles/default/SOUL.md — 假设在「secret redact」段)

> API key/token/PGPASSWORD/email 字面不进 log, 不进 memory, 不进 commit message

## 建议替换为

> **Redact 范围扩展**(覆盖 PII):
> - API key/token (原有)
> - PGPASSWORD 字面 (原有)
> - **Email 字面** (新增): `user@domain.com` 形式, redact 为 `<email_redacted>` 后写 log/memory/commit
> - **GCP / AWS 项目 ID** (新增): 12+ digit number, redact 为 `<project_id_redacted>`
> - **Service account email** (新增): `<service>@<project>.iam.gserviceaccount.com` 形式, redact 为 `<sa_email_redacted>`
> - **私有 IP + 内部 hostname** (新增): `10.x.x.x`, `192.168.x.x`, `internal.company.com`
>
> **hermes redact 层**(2026-06-22 实战沉淀)已知漏:
> - JSON secret 跨 line field value (#50423)
> - arxiv / GitHub README 含 `GH_TOKEN=*** literal (researcher profile)
> - cron terminal `$(...)` 字面被损坏
>
> **新增 PII redact 段**: 在 `~/.hermes/redact_patterns.yaml` 加 `pii: [email, gcp_id, sa_email, internal_ip]` 配置, 与现有 secret 一起跑

## 替换理由

- #54305 提醒 PII 也是 sensitive content, **不应进 commit message / log / memory**
- 本环境 researcher cron + default cron 都曾抓过 GitHub README 含 `GH_TOKEN=*** 字面, 已知 redact 层会损坏
- 默认 profile 的 `data_flow_purification_layer` (2026-06-22) 主要是 secret 维度, PII 维度未覆盖

## 风险与回退

- **风险**: PII regex 可能误伤合法内容(如 feature doc 含 example email);应配置 "user 提供的特定 keyword 才 redact"
- **回退**: 关 PII redact, 只保留 secret 维度;`git revert` default SOUL 段

## 实测锚点

```bash
# 本环境已有 redact 路径
grep -iE "(email|pii)" ~/.hermes/config.yaml
# 应为空或仅含 awareness 段
```