---
created: "2026-03-31"
campaign: "Threads自動投稿 Make設定ガイド"
status: planning
---

# Threads自動投稿 Make設定ガイド

## 全体フロー

```
[日曜: スクリプト実行]
  generate_posts.py --sheet-id XXXX --credentials credentials.json
        ↓
  JSON生成 + Google Sheetsに自動書き込み
        ↓
  ┌─────────────────────────────────────┐
  │         Google Sheets               │
  │  id | status | date | time | ...    │
  │  001 | pending | 04-07 | 07:32 | ...│
  │  002 | pending | 04-07 | 21:31 | ...│
  │  ...                                │
  └─────────────────────────────────────┘
        ↓ Make が毎日 7:20 / 21:20 に読み込み
  ┌─────────────────────────────────────┐
  │         Make シナリオ               │
  │  Sheets検索（当日・当該時刻・pending）│
  │  ↓                                  │
  │  親投稿 → Threads API               │
  │  ↓                                  │
  │  Wait (child1_delay_min 分)         │
  │  ↓                                  │
  │  子投稿1 → リプライ                  │
  │  ↓（child2_textがある場合）          │
  │  Wait (child2_delay_min 分)         │
  │  ↓                                  │
  │  子投稿2 → リプライ                  │
  │  ↓                                  │
  │  Sheetsを更新: status=posted        │
  └─────────────────────────────────────┘
```

---

## Step 1: Threads APIの準備

### 1-1. Meta開発者アカウント設定

1. https://developers.facebook.com/ でアプリ作成
2. 「Threads API」プロダクトを追加
3. 権限を申請:
   - `threads_basic`
   - `threads_content_publish`
4. アクセストークンを取得（長期トークン推奨: 60日）

### 1-2. 必要な情報

```
USER_ID       = Threadsのユーザーid（数字）
ACCESS_TOKEN  = 長期アクセストークン
BASE_URL      = https://graph.threads.net/v1.0
```

---

## Step 2: Google Sheetsの準備

### 2-1. スプレッドシート作成

新規スプレッドシートを作成し、シート名を `posts` にする。
ヘッダーはスクリプトが自動挿入するため手動設定不要。

### 2-2. サービスアカウント作成

1. Google Cloud Console でプロジェクト作成
2. 「Google Sheets API」「Google Drive API」を有効化
3. 「サービスアカウント」を作成 → JSON鍵をダウンロード
4. ファイル名を `credentials.json` にしてプロジェクトルートに配置
5. スプレッドシートをサービスアカウントのメールアドレスに**編集者として共有**

### 2-3. スプレッドシートIDの確認

```
URL: https://docs.google.com/spreadsheets/d/【ここがID】/edit
```

### 2-4. カラム構成（自動生成）

| 列 | カラム名 | 内容 |
|---|---|---|
| A | id | post-001 など |
| B | status | pending / posted / skipped |
| C | scheduled_date | 2026-04-07（Makeのフィルタ用） |
| D | scheduled_time | 07:32（Makeのフィルタ用） |
| E | scheduled_at | ISO8601フル |
| F | pillar | pain / before_after 等 |
| G | theme | 投稿テーマ |
| H | parent_text | 親投稿テキスト |
| I | child1_delay_min | 遅延（分） |
| J | child1_text | 子投稿1テキスト |
| K | child2_delay_min | 遅延（分）※なければ空 |
| L | child2_text | 子投稿2テキスト※なければ空 |
| M | posted_at | **Makeが記入** |
| N | parent_post_id | **Makeが記入** |

---

## Step 3: Makeシナリオの構成

### モジュール一覧（順番通り）

```
1. [Trigger] Schedule: 毎日 7:20 と 21:20（月〜土）
2. [Google Sheets] Search Rows
   → scheduled_date = today AND scheduled_time = "07:32"（or "21:31"）AND status = "pending"
3. [Router] 該当行があるか分岐
   → なし: 終了
   → あり: 続行
4. [HTTP] 親投稿コンテナ作成
5. [HTTP] 親投稿パブリッシュ → parent_post_id 取得
6. [Google Sheets] Update Row: status = "in_progress"
7. [Sleep] child1_delay_min 分待機
8. [HTTP] 子投稿1コンテナ作成（reply_to_id = parent_post_id）
9. [HTTP] 子投稿1パブリッシュ
10. [Router] child2_text が空でないか分岐
    → あり:
      11. [Sleep] child2_delay_min 分待機
      12. [HTTP] 子投稿2コンテナ作成（reply_to_id = parent_post_id）
      13. [HTTP] 子投稿2パブリッシュ
    → なし: スキップ
14. [Google Sheets] Update Row:
    status = "posted", posted_at = now, parent_post_id = {{5.id}}
```

---

## Step 4: 各モジュールの設定

### 2. Google Sheets - Search Rows（朝シナリオ）

```
Spreadsheet ID: {{YOUR_SPREADSHEET_ID}}
Sheet: posts
Filter:
  Column C (scheduled_date) = {{formatDate(now; "YYYY-MM-DD")}}
  Column D (scheduled_time) = "07:32"
  Column B (status)         = "pending"
Limit: 1
```

> 夜シナリオは scheduled_time = "21:31" に変えるだけ。

### 4. HTTP - 親投稿コンテナ作成

```
Method: POST
URL: https://graph.threads.net/v1.0/{{USER_ID}}/threads

Body (JSON):
{
  "text": "{{2.H}}",           ← Sheetsの H列 (parent_text)
  "media_type": "TEXT",
  "access_token": "{{ACCESS_TOKEN}}"
}

Response: { "id": "CREATION_ID" }
```

### 5. HTTP - 親投稿パブリッシュ

```
Method: POST
URL: https://graph.threads.net/v1.0/{{USER_ID}}/threads_publish

Body (JSON):
{
  "creation_id": "{{4.id}}",
  "access_token": "{{ACCESS_TOKEN}}"
}

Response: { "id": "POST_ID" }  ← これがreply_to_idになる
```

### 7. Sleep（子投稿1の前）

```
Duration: {{2.I}} 分（Sheetsの I列 child1_delay_min）
（デフォルト60分）
```

### 8. HTTP - 子投稿1コンテナ作成

```
Method: POST
URL: https://graph.threads.net/v1.0/{{USER_ID}}/threads

Body (JSON):
{
  "text": "{{2.J}}",           ← Sheetsの J列 (child1_text)
  "media_type": "TEXT",
  "reply_to_id": "{{5.id}}",  ← 親のpost_id
  "access_token": "{{ACCESS_TOKEN}}"
}
```

### 9. HTTP - 子投稿1パブリッシュ

```
Method: POST
URL: https://graph.threads.net/v1.0/{{USER_ID}}/threads_publish

Body (JSON):
{
  "creation_id": "{{8.id}}",
  "access_token": "{{ACCESS_TOKEN}}"
}
```

### 12. HTTP - 子投稿2コンテナ作成（child2_text が空でない場合）

```
Body (JSON):
{
  "text": "{{2.L}}",           ← Sheetsの L列 (child2_text)
  "media_type": "TEXT",
  "reply_to_id": "{{5.id}}",  ← 親のpost_idにリプライ（兄弟ではなく親に）
  "access_token": "{{ACCESS_TOKEN}}"
}
```

> **ポイント**: 子投稿2も `reply_to_id` は親のIDを使う。
> 子→子へのリプライではなく、親に対して兄弟リプライする形。

### 14. Google Sheets - Update Row（投稿完了記録）

```
Spreadsheet ID: {{YOUR_SPREADSHEET_ID}}
Sheet: posts
Row number: {{2.rowNumber}}
Values:
  Column B (status):         "posted"
  Column M (posted_at):      {{formatDate(now; "YYYY-MM-DD HH:mm:ss")}}
  Column N (parent_post_id): {{5.id}}
```

---

## Step 5: スケジューリング（Make トリガー設定）

### 投稿スケジュール
```
月〜土 × 7:32 / 21:31 = 1日2投稿 × 週6日 = 週12投稿
日曜日: 翌週分（12本）を生成してSheetsに自動書き込み
```

### Make シナリオ2本構成

```
シナリオA（朝）: 毎日 7:20 起動（月〜土）
  → Sheets検索: scheduled_date=today, scheduled_time="07:32", status="pending"
  → 投稿 → 完了記録

シナリオB（夜）: 毎日 21:20 起動（月〜土）
  → Sheets検索: scheduled_date=today, scheduled_time="21:31", status="pending"
  → 投稿 → 完了記録
```

### JSONファイルの読み込み方式（旧方式 / 参考）

```
- トリガー: Google Drive - Watch Files in a Folder
- 監視フォルダ: .company/marketing/content-plan/
- 新しいJSONが検知されたらデータストアに登録
- 各投稿時刻のシナリオがデータストアから該当投稿を取得
```

---

## Step 5: 生成サイクル（毎週日曜）

```
[日曜] 翌週分を生成（12本 = 月〜土分）
 ↓
[月〜土] Makeが毎日 7:32 / 21:31 に自動投稿
 ↓
[日曜] 翌週分を生成 → 繰り返し
```

### 実行コマンド

```bash
# 手動実行（毎週日曜に実行）
cd "/Users/ryota/Library/CloudStorage/Google Drive/.../RNstyle co."
python scripts/threads/generate_posts.py         # 翌週月曜から12本

# 特定日から生成
python scripts/threads/generate_posts.py --from 2026-04-07

# 確認
cat .company/marketing/content-plan/threads-posts-2026-04-07.json | jq '.posts[0]'
```

> **注意**: Claude Codeクロン（日曜8:17）はセッション終了で消えます（最大7日）。
> 恒久的な自動生成には Mac の launchd か Make 自体のスケジューラーを使ってください。「launchd設定して」と言えばセットアップします。

---

## トラブルシューティング

| エラー | 原因 | 対処 |
|---|---|---|
| `403 Permissions error` | アクセス権限不足 | Threads APIの権限を再確認 |
| `400 Invalid reply_to_id` | post_idの取得ミス | モジュール7の出力を確認 |
| `429 Rate limit` | API制限 | 投稿間隔を広げる（delay_minutesを増やす） |
| Sleep が機能しない | Make無料プランの制限 | 有料プランへアップグレード or 別シナリオに分割 |

---

## Makeプランについて

| 機能 | 無料 | Core ($9/月) |
|---|---|---|
| Sleep モジュール | ✗ 制限あり | ✓ |
| 実行回数 | 1,000回/月 | 10,000回/月 |
| 推奨 | テスト用 | 本運用 |

**月12投稿 × 1投稿あたり6〜8操作 ≒ 約80〜100回/月**
→ 無料プランでもギリギリ可能だが、Core推奨。
