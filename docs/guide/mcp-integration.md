# MCP連携ガイド

cc-company は MCP（Model Context Protocol）サーバーと連携できます。MCP サーバーを設定すると、秘書が外部サービスを直接操作できるようになります。

## 仕組み

cc-company 側に特別な設定は不要です。Claude Code に MCP サーバーを追加するだけで、秘書が自動的に活用します。

```
あなた: 明日の14時にA社とミーティング入れて

秘書: カレンダーに追加しました！
      TODOにも「A社ミーティング資料準備」を入れておきますね。
```

## おすすめ MCP サーバー

### Notion（公式）

ナレッジベースやデータベースとの連携。秘書がNotionのページを参照・更新できます。

**方法1: OAuth（おすすめ）**

```bash
claude mcp add-json notion '{"type":"http","url":"https://mcp.notion.com/mcp"}'
```

実行後、ブラウザで OAuth 認証が開きます。API キーの手動設定は不要です。

**方法2: API トークン**

```bash
claude mcp add notion -e NOTION_TOKEN=ntn_YOUR_TOKEN -- npx -y @notionhq/notion-mcp-server
```

[Notion Integrations](https://www.notion.so/my-integrations) で API トークンを作成してください。

**できること:**
- Notion ページの参照・作成・更新
- データベースの検索・更新
- 既存のナレッジベースを秘書が参照

---

### Google Calendar

スケジュール管理。秘書がミーティングの登録やリマインダーを設定できます。

```bash
claude mcp add google-calendar \
  -e GOOGLE_OAUTH_CREDENTIALS=/path/to/gcp-oauth.keys.json \
  -- npx -y @cocal/google-calendar-mcp
```

**事前準備:**
1. [Google Cloud Console](https://console.cloud.google.com/) でプロジェクトを作成
2. Calendar API を有効化
3. OAuth 2.0 認証情報を作成（デスクトップアプリ）
4. 認証情報の JSON をダウンロード

**できること:**
- 予定の作成・確認・変更・削除
- 今日・今週のスケジュール表示
- 空き時間の確認
- 繰り返し予定の管理

---

### GitHub（公式）

リポジトリ管理。開発部門と相性が良いです。

**方法1: HTTP（おすすめ）**

```bash
claude mcp add-json github '{"type":"http","url":"https://api.githubcopilot.com/mcp","headers":{"Authorization":"Bearer YOUR_GITHUB_PAT"}}'
```

**方法2: Docker**

```bash
claude mcp add github \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=YOUR_PAT \
  -- docker run -i --rm -e GITHUB_PERSONAL_ACCESS_TOKEN ghcr.io/github/github-mcp-server
```

[GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens) でトークンを作成してください。

**できること:**
- Issue の作成・確認・検索
- PR の管理・レビュー
- リポジトリの状況確認
- コード検索

---

### Slack（公式）

チームコミュニケーション。営業部門やPM部門と連携して活用できます。

**方法1: OAuth（おすすめ）**

```bash
claude mcp add-json slack '{"type":"http","url":"https://mcp.slack.com/mcp","oauth":{"clientId":"1601185624273.8899143856786","callbackPort":3118}}'
```

実行後、ブラウザで Slack の OAuth 認証が開きます。

**方法2: プラグインとしてインストール**

```bash
claude plugin install slack
```

**できること:**
- メッセージの送信・確認
- チャンネルの状況把握
- ユーザー情報の参照
- クライアントへの連絡リマインダー

::: warning 注意
ワークスペースの管理者が MCP 連携を許可している必要があります。
:::

---

## 設定方法

### コマンドで追加（おすすめ）

上記の `claude mcp add` コマンドを実行するだけです。設定後、Claude Code を再起動してください。

### 手動で設定ファイルを編集

**グローバル設定（全プロジェクト共通）:** `~/.claude/settings.json`

```json
{
  "mcpServers": {
    "notion": {
      "type": "http",
      "url": "https://mcp.notion.com/mcp"
    }
  }
}
```

**プロジェクト設定（特定プロジェクトのみ）:** `.claude/settings.json`

::: tip ポイント
よく使うサービス（カレンダー、Notion）はグローバル設定に、プロジェクト固有のもの（GitHub）はプロジェクト設定に置くのがおすすめです。
:::

---

## 秘書との連携例

MCP サーバーを設定すると、秘書が自然に活用します。

```
> 今週のスケジュール教えて
秘書: カレンダーを確認しますね。
      - 月曜 10:00 A社定例
      - 水曜 14:00 B社ヒアリング
      - 金曜 終日 確定申告締切
      水曜のB社、提案書の準備は大丈夫ですか？

> A社との議事録をNotionにまとめて
秘書: 承知しました。Notionに議事録ページを作成しました。
      secretary/notes/ にもサマリーを保存しておきますね。

> このバグのIssue立てて
秘書: GitHubにIssueを作成しました。
      engineering/debug-log/ にもログを残しておきます。
```

## MCP なしでも問題なし

MCP サーバーがなくても cc-company は完全に動作します。秘書は `.company/` フォルダ内でのファイル管理だけでも十分に機能します。

MCP は「あるともっと便利」なオプションです。
