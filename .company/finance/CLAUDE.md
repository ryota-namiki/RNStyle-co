---
type: department
name: 経理
role: 請求書・経費・売上管理・freee 会計連携
---

# 経理

RNStyle のお金周り（請求書・経費・売上・仕訳・試算表）を管理する。
実際の freee 会計操作は **keiri サブエージェント**（`.claude/agents/keiri.md`）に委譲する。

## freee 連携（実操作の担当）
- freee への取引登録・仕訳・試算表・請求書・経費・取引先などの実操作は、必ず `keiri` サブエージェントに委譲する。
- keiri は freee MCP サーバー（`.mcp.json` の `freee`）経由で `freee_*` ツールを使う。
- API 仕様が不明なときは `freee-api-skill`（`.claude/skills/freee-api-skill/`）の `references/` を検索してから呼び出す。
- テナント固有情報（勘定科目 ID・税区分・仕訳パターン）は `.claude/agent-memory/keiri/` に記録済み。名称から ID を推測しない。

### 対象事業所（取り違え厳禁）
- 本番: **RNStyle**（company_id `12082052`）
- 検証: **開発用テスト事業所**（company_id `12726037`）
- freee 作業前に `freee_auth_status` → `freee_get_current_company` を必ず確認する。

### 書き込み時の安全ルール（keiri が遵守）
- POST/PUT/PATCH/DELETE の前に、対象事業所・内容・金額と、実際の `path`・`body`(JSON) を提示して承認を得る。
- 承認なしに書き込まない。実行後は GET で読み直して結果を報告する。
- 現行 OAuth ユーザーは `company_admin` 権限がないため、経費申請 API（`/api/1/expense_applications`）は RNStyle で 401 になる（権限不足）。

## ルール（ローカル文書）
- 請求書は `invoices/YYYY-MM-DD-client-name.md`
- 経費は `expenses/YYYY-MM-category.md`
- 金額は税込・税抜を明記する（デフォルト税込）
- 請求書のステータス: draft → sent → paid → overdue
- 未入金の請求書は秘書のTODO（`secretary/todos/YYYY-MM-DD.md`）にリマインダーを入れる
- 月末に月次の経費集計を行い、freee の試算表と突き合わせる
- freee で確定した重要な取引・請求は、このフォルダにも要約を残す（金額・相手・日付・freee 上の ID）

## フォルダ構成
- `invoices/` - 請求書（1請求1ファイル）
- `expenses/` - 経費（月別またはカテゴリ別）
