---
type: department
name: 経理
role: 請求書・経費・売上管理
---

# 経理

ローカル文書管理を担当。freee 実操作は **keiri サブエージェント**（`.claude/agents/keiri.md`）に委譲。

> freee 連携ルール: `.claude/rules/finance.md`

## ローカル文書
- 請求書: `invoices/YYYY-MM-DD-client-name.md`（draft → sent → paid → overdue）
- 経費: `expenses/YYYY-MM-category.md`（金額は税込・税抜を明記、デフォルト税込）
- 未入金請求書 → 秘書 TODO にリマインダー
- 月末: 経費集計 + freee 試算表と突合
- freee 確定取引は要約を残す（金額・相手・日付・freee ID）
