---
paths:
  - ".company/**"
---

# 仮想組織 共通ルール

## 秘書が窓口
- ユーザーとの対話は常に秘書が担当する
- 部署の作業が必要な場合、秘書が該当部署フォルダに書き込む

## 自動記録
- 意思決定 → `secretary/notes/YYYY-MM-DD-decisions.md`
- 学び → `secretary/notes/YYYY-MM-DD-learnings.md`
- アイデア → `secretary/inbox/YYYY-MM-DD.md`

## ファイル操作
- 同日1ファイル: 存在する場合は追記、新規作成しない
- 操作前に今日の日付を確認する
- 日次: `YYYY-MM-DD.md` / トピック: `kebab-case-title.md`
- 既存ファイルは上書きしない（追記のみ、タイムスタンプ付き）
- 迷ったら `secretary/inbox/` に入れる

## TODO形式
```
- [ ] タスク | 優先度: 高/通常/低 | 期限: YYYY-MM-DD
- [x] 完了タスク | 完了: YYYY-MM-DD
```
