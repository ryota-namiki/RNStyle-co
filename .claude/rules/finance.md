---
paths:
  - ".company/finance/**"
---

# 経理 freee 連携

freee への実操作（取引・仕訳・試算表・請求書等）は必ず **keiri サブエージェント**に委譲する。
詳細ルール: `.claude/agents/keiri.md`

- API 仕様: `INDEX.md` で索引 → 該当1ファイルのみ Read（`.claude/skills/freee-api-skill/`）
- テナント固有情報: `.claude/agent-memory/keiri/`
- 本番 RNStyle `12082052` / 検証 `12726037`（取り違え厳禁）
