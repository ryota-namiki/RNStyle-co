---
created: "2026-03-31"
campaign: "Threads自動投稿 Make設定ガイド"
status: planning
---

# Threads自動投稿 Make設定ガイド

## 全体フロー

```
[スクリプト実行] → JSON生成 → Googleドライブ同期
                                    ↓
                              [Make シナリオ]
                                    ↓
                    ┌───────────────────────────┐
                    │  JSONを読み込み             │
                    │  ↓                         │
                    │  親投稿 → Threads API       │
                    │  ↓                         │
                    │  Wait (delay_minutes)       │
                    │  ↓                         │
                    │  子投稿1 → リプライ          │
                    │  ↓（子が2つの場合）          │
                    │  Wait (delay_minutes)       │
                    │  ↓                         │
                    │  子投稿2 → リプライ          │
                    └───────────────────────────┘
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

## Step 2: Makeシナリオの構成

### モジュール一覧（順番通り）

```
1. [Trigger] Google Drive: Watch Files in a Folder
2. [Google Drive] Download a File
3. [JSON] Parse JSON
4. [Iterator] Iterate over posts[]
5. ── ここからポスト1件ずつ ──
6. [HTTP] 親投稿コンテナ作成
7. [HTTP] 親投稿パブリッシュ → post_id 取得
8. [Sleep] child[0].delay_minutes 分待機
9. [HTTP] 子投稿1コンテナ作成（reply_to_id = post_id）
10. [HTTP] 子投稿1パブリッシュ
11. [Router] children[1] が存在するか分岐
    → Yes:
      12. [Sleep] child[1].delay_minutes 分待機
      13. [HTTP] 子投稿2コンテナ作成
      14. [HTTP] 子投稿2パブリッシュ
    → No: スキップ
```

---

## Step 3: 各HTTPモジュールの設定

### 6. 親投稿コンテナ作成

```
Method: POST
URL: https://graph.threads.net/v1.0/{{USER_ID}}/threads

Body (JSON):
{
  "text": "{{parent.text}}",
  "media_type": "TEXT",
  "access_token": "{{ACCESS_TOKEN}}"
}

Response: { "id": "CREATION_ID" }
```

### 7. 親投稿パブリッシュ

```
Method: POST
URL: https://graph.threads.net/v1.0/{{USER_ID}}/threads_publish

Body (JSON):
{
  "creation_id": "{{6.id}}",
  "access_token": "{{ACCESS_TOKEN}}"
}

Response: { "id": "POST_ID" }  ← これがreply_to_idになる
```

### 8. Sleep（子投稿1の前）

```
Duration: {{children[0].delay_minutes}} 分
（デフォルト60分 = 3600秒）
```

### 9. 子投稿1コンテナ作成

```
Method: POST
URL: https://graph.threads.net/v1.0/{{USER_ID}}/threads

Body (JSON):
{
  "text": "{{children[0].text}}",
  "media_type": "TEXT",
  "reply_to_id": "{{7.id}}",
  "access_token": "{{ACCESS_TOKEN}}"
}
```

### 10. 子投稿1パブリッシュ

```
Method: POST
URL: https://graph.threads.net/v1.0/{{USER_ID}}/threads_publish

Body (JSON):
{
  "creation_id": "{{9.id}}",
  "access_token": "{{ACCESS_TOKEN}}"
}
```

### 13. 子投稿2コンテナ作成（存在する場合）

```
Body (JSON):
{
  "text": "{{children[1].text}}",
  "media_type": "TEXT",
  "reply_to_id": "{{7.id}}",   ← 親のpost_idにリプライ（兄弟ではなく親に）
  "access_token": "{{ACCESS_TOKEN}}"
}
```

> **ポイント**: 子投稿2も `reply_to_id` は親のIDを使う。
> 子→子へのリプライではなく、親に対して兄弟リプライする形。

---

## Step 4: スケジューリング

### 投稿スケジュール
```
月〜金 × 12:00 / 20:00 = 1日2投稿 × 週5日 = 週10投稿
```

### Make シナリオのトリガー設定（推奨）

```
スケジュール: 毎日 11:50 と 19:50 に起動（月〜金）
  → 11:50起動 → 12:00投稿の親を作成 → 60分後に子投稿
  → 19:50起動 → 20:00投稿の親を作成 → 60分後に子投稿
```

フィルタ条件（Makeの Filter モジュール）:
```
scheduled_at の日付  = today
AND scheduled_at の時刻 = "12:00" or "20:00"（起動時刻に応じて）
AND status = "pending"
```

### JSONファイルの読み込み方式

```
- トリガー: Google Drive - Watch Files in a Folder
- 監視フォルダ: .company/marketing/content-plan/
- 新しいJSONが検知されたらデータストアに登録
- 各投稿時刻のシナリオがデータストアから該当投稿を取得
```

---

## Step 5: 生成サイクル（5日ごと）

```
生成 → 5日間投稿 → 生成 → 5日間投稿 → ...

[月] 生成実行（10本 = 月〜金分）
 ↓
[月〜金] Makeが毎日12:00/20:00に自動投稿
 ↓
[土] 次の生成（翌週月曜〜金曜分）
 ↓
繰り返し
```

### 実行コマンド

```bash
# 自動（Claude Codeクロン: 5日ごと8:00に自動実行）
# ↑ セットアップ済み（Claude Codeセッション中のみ有効）

# 手動実行
cd "/Users/ryota/Library/CloudStorage/Google Drive/.../RNstyle co."
python scripts/threads/generate_posts.py         # 翌週月曜から10本

# 特定日から生成
python scripts/threads/generate_posts.py --from 2026-04-14

# 確認
cat .company/marketing/content-plan/threads-posts-2026-04-07.json | jq '.posts[0]'
```

> **注意**: Claude Codeクロンはセッション終了で消えます（7日上限）。
> 恒久的な自動生成には Mac の launchd か Make 自体のスケジューラーを使ってください。

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
