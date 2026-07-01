"""
Google Apps Script 連携モジュール
投稿JSONをGASウェブアプリ経由でスプレッドシートに書き込む

GASのdoPost()がJSONを受け取り、Sheetsに行を追加する。
"""

import json
import sys
import requests

GAS_URL = "https://script.google.com/macros/s/AKfycbzmUXlZmjtMM7E6tlivLWAFYb6wbZfqvtn3xR2NlwudUUr0y8qfO9kJCWsCSWsYQ-jMIQ/exec"


def _flatten(posts: list) -> list:
    """generate_posts.pyのpost構造をSheetsの行形式に変換"""
    rows = []
    for post in posts:
        scheduled_at = post.get("scheduled_at", "")
        children = post.get("children", [])
        c1 = children[0] if len(children) > 0 else {}
        c2 = children[1] if len(children) > 1 else {}

        rows.append({
            "id":               post.get("id", ""),
            "status":           post.get("status", "pending"),
            "scheduled_date":   scheduled_at[:10] if scheduled_at else "",
            "scheduled_time":   scheduled_at[11:16] if len(scheduled_at) >= 16 else "",
            "scheduled_at":     scheduled_at,
            "pillar":           post.get("pillar", ""),
            "theme":            post.get("theme", ""),
            "parent_text":      post.get("parent", {}).get("text", ""),
            "child1_delay_min": c1.get("delay_minutes", 60) if c1 else 60,
            "child1_text":      c1.get("text", "") if c1 else "",
            "child2_delay_min": c2.get("delay_minutes", "") if c2 else "",
            "child2_text":      c2.get("text", "") if c2 else "",
        })
    return rows


def push(posts: list, gas_url: str = GAS_URL) -> int:
    """
    投稿リストをGASウェブアプリにPOSTしてSheetsに書き込む。
    GAS側で重複ID(id列)はスキップされる。
    戻り値: 追加した行数
    """
    payload = {"posts": _flatten(posts)}

    res = requests.post(
        gas_url,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=30,
        allow_redirects=True,
    )
    res.raise_for_status()

    result = res.json()

    if not result.get("success"):
        raise RuntimeError(f"GASエラー: {result.get('error', '不明')}")

    added   = result.get("added", 0)
    skipped = result.get("skipped", 0)
    print(f"   GAS→Sheets: {added}行追加, {skipped}件スキップ（重複）", file=sys.stderr)
    return added
