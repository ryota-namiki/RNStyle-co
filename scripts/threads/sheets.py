"""
Google Sheets 連携モジュール
投稿JSONをスプレッドシートに書き込む / 読み込む
"""

import gspread
from google.oauth2.service_account import Credentials
import sys

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# カラム定義（順番固定）
HEADERS = [
    "id",                # A: 投稿ID
    "status",            # B: pending / posted / skipped
    "scheduled_date",    # C: YYYY-MM-DD（Makeのフィルタ用）
    "scheduled_time",    # D: HH:MM（Makeのフィルタ用）
    "scheduled_at",      # E: ISO8601フル（参照用）
    "pillar",            # F: pain / before_after / process / results / personality
    "theme",             # G: 投稿テーマ
    "parent_text",       # H: 親投稿テキスト
    "child1_delay_min",  # I: 子1の遅延（分）
    "child1_text",       # J: 子投稿1テキスト
    "child2_delay_min",  # K: 子2の遅延（分）※なければ空
    "child2_text",       # L: 子投稿2テキスト※なければ空
    "posted_at",         # M: 投稿完了日時（Makeが記入）
    "parent_post_id",    # N: ThreadsのポストID（Makeが記入）
]


def _get_client(credentials_path: str) -> gspread.Client:
    creds = Credentials.from_service_account_file(credentials_path, scopes=SCOPES)
    return gspread.authorize(creds)


def _get_or_create_worksheet(
    spreadsheet: gspread.Spreadsheet, name: str
) -> gspread.Worksheet:
    try:
        return spreadsheet.worksheet(name)
    except gspread.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title=name, rows=2000, cols=len(HEADERS))
        ws.append_row(HEADERS, value_input_option="USER_ENTERED")
        # ヘッダー行を太字・固定
        ws.format("A1:N1", {"textFormat": {"bold": True}})
        ws.freeze(rows=1)
        return ws


def push(
    posts: list,
    spreadsheet_id: str,
    credentials_path: str,
    worksheet_name: str = "posts",
) -> int:
    """
    投稿リストをスプレッドシートに追記する。
    同じ id がすでに存在する場合はスキップ（べき等）。
    戻り値: 追加した行数
    """
    client = _get_client(credentials_path)
    spreadsheet = client.open_by_key(spreadsheet_id)
    ws = _get_or_create_worksheet(spreadsheet, worksheet_name)

    # ヘッダーが未設定なら初期化
    first_row = ws.row_values(1)
    if not first_row or first_row[0] != "id":
        ws.insert_row(HEADERS, 1)
        ws.format("A1:N1", {"textFormat": {"bold": True}})
        ws.freeze(rows=1)

    # 既存IDを取得（重複防止）
    all_ids = set(ws.col_values(1)[1:])  # 1行目はヘッダー

    rows_to_append = []
    skipped = 0

    for post in posts:
        pid = post.get("id", "")
        if pid in all_ids:
            skipped += 1
            continue

        scheduled_at = post.get("scheduled_at", "")
        scheduled_date = scheduled_at[:10] if scheduled_at else ""
        scheduled_time = scheduled_at[11:16] if len(scheduled_at) >= 16 else ""

        children = post.get("children", [])
        c1 = children[0] if len(children) > 0 else {}
        c2 = children[1] if len(children) > 1 else {}

        row = [
            pid,
            post.get("status", "pending"),
            scheduled_date,
            scheduled_time,
            scheduled_at,
            post.get("pillar", ""),
            post.get("theme", ""),
            post.get("parent", {}).get("text", ""),
            c1.get("delay_minutes", 60) if c1 else "",
            c1.get("text", "") if c1 else "",
            c2.get("delay_minutes", "") if c2 else "",
            c2.get("text", "") if c2 else "",
            "",  # posted_at  ← Makeが記入
            "",  # parent_post_id ← Makeが記入
        ]
        rows_to_append.append(row)

    if rows_to_append:
        ws.append_rows(rows_to_append, value_input_option="USER_ENTERED")

    added = len(rows_to_append)
    print(f"   Sheets: {added}行追加, {skipped}件スキップ（重複）", file=sys.stderr)
    return added
