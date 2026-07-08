---
name: freee-api-skill
description: "freee MCP 連携。API 仕様は INDEX.md → references/ を Grep/Read（1ファイルのみ）。経理操作は keiri サブエージェントに委譲。"
license: Apache-2.0
metadata:
  author: freee_jp
  homepage: https://github.com/freee/freee-mcp
---

# freee API スキル

freee MCP 経由で会計・人事労務・請求書・工数・販売・IT管理 API を操作する。

## 参照の読み方（重要）

1. **`INDEX.md`** で用途に合うファイル名を特定
2. **`references/` または `sign-references/` の該当1ファイルだけ** Read
3. 一括読み込み・全件 grep 結果の全文 Read は禁止

よく使う会計: `accounting-deals`, `accounting-account-items`, `accounting-partners`, `accounting-trial-balance`, `accounting-manual-journals`, `invoice-invoices`

## 基本ワークフロー

1. `freee_auth_status` → `freee_get_current_company`（事業所確認）
2. 不明な API → `freee_api_list_paths` でパス確認
3. `INDEX.md` → 該当 reference 1件 Read → `freee_api_*` 呼び出し
4. 書き込み前に path/body を提示して承認取得（keiri ルール）

## service パラメータ

| service | 用途 |
|---------|------|
| `accounting` | 会計（取引・勘定科目・試算表等） |
| `hr` | 人事労務 |
| `invoice` | 請求書・見積・納品 |
| `pm` | 工数管理 |
| `sm` | 販売 |
| `it_management` | IT管理 |

## レシピ（操作パターン）

`recipes/` にユースケース別サンプルあり。reference より先に recipes を確認:

- `recipes/deal-operations.md` — 取引
- `recipes/manual-journal-operations.md` — 振替伝票
- `recipes/invoice-operations.md` — 請求書
- `recipes/report-operations.md` — 試算表
- `recipes/troubleshooting.md` — エラー対応

## サイン（電子契約）

別 MCP（freee-sign-mcp）。`sign-references/` と `SIGN-GUIDE.md` を参照。

## 関連

- [freee-mcp](https://www.npmjs.com/package/freee-mcp) / Remote MCP: `https://mcp.freee.co.jp/mcp`
