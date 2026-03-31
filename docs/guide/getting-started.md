# クイックスタート

## インストール

Claude Code で以下を実行します。

```
/plugin marketplace add Shin-sibainu/cc-company
/plugin install company@cc-company
```

## セットアップ（3ステップ）

### 1. `/company` を実行

```
> /company
```

### 2. 秘書の質問に答える

```
秘書: はじめまして！あなたの秘書になります。
      まず、事業や活動を教えてください。
あなた: フリーランスのWeb開発やってます

秘書: 今の目標や困りごとは？
あなた: SaaSを作って月10万目指してる。タスクが散らかるのが悩み
```

### 3. 完了！

```
→ .company/secretary/ が自動生成される

秘書: 秘書室のセットアップが完了しました！
      これからは /company でいつでも話しかけてください。
```

たったこれだけです。以下のフォルダが作られます：

```
.company/
├── CLAUDE.md              ← 組織ルール
└── secretary/
    ├── CLAUDE.md           ← 秘書の振る舞い
    ├── inbox/              ← クイックキャプチャ
    ├── todos/              ← 日次タスク管理
    │   └── 2026-03-16.md   ← 今日のTODO
    └── notes/              ← 壁打ち・相談メモ
```

## 次のステップ

- [秘書との日常](/guide/daily-usage) — 実際にどう使うか
- [部署を追加する](/guide/adding-departments) — 組織を育てる
