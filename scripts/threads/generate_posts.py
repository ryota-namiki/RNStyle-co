#!/usr/bin/env python3
"""
Threads投稿 自動生成スクリプト
リサーチ → 戦略立案 → ツリー形式JSON生成

スケジュール: 月〜金 × 1日2投稿（12:00 / 20:00）= 週10投稿
生成サイクル: 5日ごとに1週間分（10本）を生成

Usage:
    python generate_posts.py                         # デフォルト: 翌週分10本
    python generate_posts.py --count 10 --from 2026-04-07
    python generate_posts.py --count 20              # 2週間分

必要な環境変数:
    ANTHROPIC_API_KEY

出力先:
    .company/marketing/content-plan/threads-posts-YYYY-MM-DD.json
"""

import anthropic
import json
import re
import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# ──────────────────────────────────────────────
# 設定
# ──────────────────────────────────────────────

MODEL = "claude-opus-4-6"

# 月〜土、1日2投稿（7:32 & 21:31）= 週12投稿
POSTING_WEEKDAYS = [0, 1, 2, 3, 4, 5]   # Mon=0 … Sat=5
POSTING_TIMES    = ["07:32", "21:31"]    # 1日2スロット

# 柱の配分（10本で1周）
PILLAR_DISTRIBUTION = (
    ["pain"] * 3 +
    ["before_after"] * 2 +
    ["process"] * 2 +
    ["results"] * 2 +
    ["personality"] * 1
)

OUTPUT_DIR = Path(__file__).parent.parent.parent / ".company" / "marketing" / "content-plan"

PERSONA = """
あなたはUIUXデザイン・WEB制作フリーランサーです。
- 得意: UIUXデザイン、WEBサイト制作、ユーザー体験設計
- ターゲットクライアント: 中小企業・スタートアップのオーナー・マーケ担当
- 典型的な依頼者の悩み: 「サイトはあるが問い合わせが来ない」「リニューアルしたい」「競合より見劣りする」
- SNSの目的: 信頼構築 → 受託案件獲得
"""

# ──────────────────────────────────────────────
# Phase 1: リサーチ
# ──────────────────────────────────────────────

RESEARCH_PROMPT = f"""
{PERSONA}

あなたのターゲットクライアント（中小企業・スタートアップオーナー）が
今まさに抱えているWEB・UIUXに関する悩みやペインポイントを深く分析してください。

以下のJSON形式のみで出力してください（コードブロック不要）:
{{
  "pain_points": [
    "具体的なペインポイント1",
    "具体的なペインポイント2",
    "...（10個）"
  ],
  "common_misconceptions": [
    "よくある誤解1（これを正す投稿が効果的）",
    "よくある誤解2",
    "...（5個）"
  ],
  "desire_keywords": [
    "ターゲットが検索・気にしているキーワード1",
    "...（8個）"
  ],
  "effective_angles": [
    "Threadsで反応が取れやすい切り口1",
    "...（5個）"
  ]
}}
"""

# ──────────────────────────────────────────────
# Phase 2: 戦略立案
# ──────────────────────────────────────────────

STRATEGY_PROMPT_TEMPLATE = """
{persona}

【リサーチ結果】
{research}

上記のリサーチをもとに、今月（{month}）のThreadsコンテンツ戦略を立案してください。
{count}本の投稿テーマを、以下の柱の配分で決めてください:

- pain（痛みを言語化）: 30% → 共感・リーチ拡大
- before_after（事例・ビフォーアフター）: 25% → 実力証明
- process（プロセス公開）: 20% → 信頼・差別化
- results（数字・結果）: 15% → 信頼証明
- personality（人柄・考え方）: 10% → 親近感

以下のJSON形式のみで出力してください（コードブロック不要）:
{{
  "month": "{month}",
  "strategy_summary": "今月の戦略を一言で",
  "key_message": "今月を通じて伝えたいメッセージ",
  "themes": [
    {{
      "index": 1,
      "pillar": "pain",
      "theme": "投稿テーマ",
      "angle": "具体的な切り口・視点",
      "hook": "冒頭の一文（続きを読みたくなる）",
      "children_count": 2
    }},
    ...（{count}個）
  ]
}}
"""

# ──────────────────────────────────────────────
# Phase 3: 投稿生成
# ──────────────────────────────────────────────

POST_GENERATION_PROMPT_TEMPLATE = """
{persona}

【テーマ】
- 柱: {pillar}
- テーマ: {theme}
- 切り口: {angle}
- フック（冒頭案）: {hook}
- 子投稿数: {children_count}個

【ツリー投稿のルール】
- 親投稿: 50-120文字。フック・問題提起。「続きを読みたい」と思わせる。絵文字OK（1-2個）
- 子投稿1: 100-280文字。親の答え・解説・具体例
- 子投稿2（{children_count}個の場合）: 100-200文字。まとめ or CTA。最後に「UIUXデザイン×WEB制作のご相談はプロフから」などCTAを1回だけ入れる
- 子が1個の場合: その子投稿の末尾にCTAを入れる
- 改行は積極的に使う（Threads向け）
- ハッシュタグは使わない

以下のJSON形式のみで出力してください（コードブロック不要）:
{{
  "parent": {{
    "text": "親投稿のテキスト"
  }},
  "children": [
    {{
      "order": 1,
      "delay_minutes": 60,
      "text": "子投稿1のテキスト"
    }},
    {{
      "order": 2,
      "delay_minutes": 60,
      "text": "子投稿2のテキスト"
    }}
  ]
}}
"""

# ──────────────────────────────────────────────
# スケジュール生成
# ──────────────────────────────────────────────

def parse_json(text: str) -> dict:
    """コードブロックや前後テキストを除去して堅牢にJSONをパースする"""
    text = text.strip()

    # コードブロック除去
    if "```" in text:
        parts = text.split("```")
        for part in parts:
            candidate = part.lstrip("json").strip()
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                continue

    # そのままパース
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 最初の { から最後の } までを抽出して再試行
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return json.loads(match.group())

    raise json.JSONDecodeError("JSONが見つかりません", text, 0)


def build_schedule(start_date: datetime, count: int) -> list[datetime]:
    """月〜金 × 12:00/20:00 の投稿スロットを count 個生成"""
    slots = []
    current = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

    while len(slots) < count:
        if current.weekday() in POSTING_WEEKDAYS:
            for time_str in POSTING_TIMES:   # 同じ日に12:00と20:00の両方を追加
                if len(slots) >= count:
                    break
                h, m = map(int, time_str.split(":"))
                slots.append(current.replace(hour=h, minute=m))
        current += timedelta(days=1)

    return slots

# ──────────────────────────────────────────────
# メイン処理
# ──────────────────────────────────────────────

def run(count: int, start_date: datetime, output_path: Optional[Path]):
    client = anthropic.Anthropic()

    print(f"\n{'='*50}", file=sys.stderr)
    print(f"  Threads投稿生成 | {start_date.date()} 〜 | {count}本", file=sys.stderr)
    print(f"{'='*50}\n", file=sys.stderr)

    def tool_call(prompt_text: str, tool_name: str, tool_schema: dict, max_tokens: int = 4096) -> dict:
        """tool_use で構造化JSONを確実に取得する"""
        res = client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            tools=[{"name": tool_name, "description": "結果を返す", "input_schema": tool_schema}],
            tool_choice={"type": "tool", "name": tool_name},
            messages=[{"role": "user", "content": prompt_text}],
        )
        for block in res.content:
            if block.type == "tool_use":
                return block.input
        raise ValueError("tool_useブロックが見つかりません")

    # ── Phase 1: リサーチ ──
    print("📡 Phase 1: リサーチ中...", file=sys.stderr)
    research = tool_call(
        prompt_text=RESEARCH_PROMPT,
        tool_name="research_result",
        tool_schema={
            "type": "object",
            "properties": {
                "pain_points":           {"type": "array", "items": {"type": "string"}},
                "common_misconceptions": {"type": "array", "items": {"type": "string"}},
                "desire_keywords":       {"type": "array", "items": {"type": "string"}},
                "effective_angles":      {"type": "array", "items": {"type": "string"}},
            },
            "required": ["pain_points", "common_misconceptions", "desire_keywords", "effective_angles"],
        },
    )
    print(f"   ✓ ペインポイント {len(research.get('pain_points', []))}件 取得", file=sys.stderr)

    # ── Phase 2: 戦略立案（シンプル・ネスト不使用）──
    month = start_date.strftime("%Y-%m")
    print("\n🎯 Phase 2: 戦略立案中...", file=sys.stderr)
    strategy = tool_call(
        prompt_text=(
            f"{PERSONA}\n\n"
            f"【リサーチ】\n{json.dumps(research, ensure_ascii=False, indent=2)}\n\n"
            f"今月（{month}）のThreadsコンテンツ戦略の方向性を一言でまとめてください。"
        ),
        tool_name="strategy_result",
        tool_schema={
            "type": "object",
            "properties": {
                "strategy_summary": {"type": "string"},
                "key_message":      {"type": "string"},
            },
            "required": ["strategy_summary", "key_message"],
        },
    )
    print(f"   ✓ 戦略: {strategy.get('strategy_summary', '')[:60]}", file=sys.stderr)

    # ── Phase 3: テーマ決定 + 投稿生成（1本ずつ、フラット構造）──
    print(f"\n✍️  Phase 3: 投稿生成中 ({count}本)...", file=sys.stderr)
    schedule = build_schedule(start_date, count)
    posts = []
    pillar_seq = PILLAR_DISTRIBUTION * ((count // len(PILLAR_DISTRIBUTION)) + 1)

    post_schema = {
        "type": "object",
        "properties": {
            "pillar":           {"type": "string", "enum": ["pain", "before_after", "process", "results", "personality"]},
            "theme":            {"type": "string"},
            "parent_text":      {"type": "string"},
            "child1_text":      {"type": "string"},
            "child1_delay_min": {"type": "integer"},
            "child2_text":      {"type": "string"},
            "child2_delay_min": {"type": "integer"},
        },
        "required": ["pillar", "theme", "parent_text", "child1_text", "child1_delay_min"],
    }

    for i in range(count):
        pillar = pillar_seq[i]
        try:
            result = tool_call(
                prompt_text=(
                    f"{PERSONA}\n\n"
                    f"戦略方針: {strategy.get('strategy_summary', '')}\n"
                    f"今回の柱: {pillar}\n"
                    f"参考ペイン: {', '.join(research.get('pain_points', [])[:3])}\n\n"
                    f"Threadsツリー投稿を1本作成してください。\n"
                    f"親投稿: 50-120文字、フック・問題提起、絵文字OK\n"
                    f"子投稿1: 100-280文字、答え・解説\n"
                    f"子投稿2(任意): 100-200文字、まとめ+CTA。不要ならchild2_textを空文字に\n"
                    f"CTA例: UIUXデザイン×WEB制作のご相談はプロフから\n"
                    f"改行を使う。ハッシュタグなし。delay_minutesは60固定。"
                ),
                tool_name="post_result",
                tool_schema=post_schema,
                max_tokens=1200,
            )
            scheduled_at = schedule[i].strftime("%Y-%m-%dT%H:%M:00+09:00") if i < len(schedule) else None
            children = [{"order": 1, "delay_minutes": result.get("child1_delay_min", 60), "text": result["child1_text"]}]
            if result.get("child2_text"):
                children.append({"order": 2, "delay_minutes": result.get("child2_delay_min", 60), "text": result["child2_text"]})
            post = {
                "id":           f"post-{i+1:03d}",
                "status":       "pending",
                "scheduled_at": scheduled_at,
                "pillar":       result.get("pillar", pillar),
                "theme":        result.get("theme", ""),
                "parent":       {"text": result["parent_text"]},
                "children":     children,
            }
            posts.append(post)
            print(f"   ✓ [{i+1:02d}/{count}] {post['pillar']:12s} | {post['theme'][:30]}", file=sys.stderr)
        except Exception as e:
            print(f"   ✗ [{i+1:02d}/{count}] 失敗: {e} — スキップ", file=sys.stderr)

    # ── 出力 ──
    output = {
        "generated_at": datetime.now().isoformat(),
        "period_start": start_date.strftime("%Y-%m-%d"),
        "period_end": schedule[-1].strftime("%Y-%m-%d") if schedule else "",
        "strategy_summary": strategy.get("strategy_summary", ""),
        "key_message": strategy.get("key_message", ""),
        "total": len(posts),
        "posts": posts,
    }

    if output_path is None:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_path = OUTPUT_DIR / f"threads-posts-{start_date.strftime('%Y-%m-%d')}.json"

    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n{'='*50}", file=sys.stderr)
    print(f"  ✅ 完了: {output_path}", file=sys.stderr)
    print(f"  投稿数: {len(posts)}本 (月〜土 × 7:32/21:31)", file=sys.stderr)
    if schedule:
        print(f"  期間: {schedule[0].strftime('%Y/%m/%d %H:%M')} 〜 {schedule[-1].strftime('%Y/%m/%d %H:%M')}", file=sys.stderr)
    print(f"{'='*50}\n", file=sys.stderr)

    return posts


def main():
    parser = argparse.ArgumentParser(
        description="Threads投稿を リサーチ → 戦略立案 → JSON生成 → Sheets書き込み で自動作成",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
例:
  python generate_posts.py                                      # 翌週月曜から12本（デフォルト）
  python generate_posts.py --count 12 --from 2026-04-07
  python generate_posts.py --sheet-id 1aBcD... --credentials credentials.json
        """,
    )
    parser.add_argument("--count",    type=int,  default=12,   help="生成する投稿数（デフォルト: 12 = 6日分）")
    parser.add_argument("--from",     type=str,  default=None, dest="from_date",
                        help="開始日 YYYY-MM-DD（デフォルト: 翌週月曜日）")
    parser.add_argument("--output",   type=str,  default=None, help="JSON出力パス（省略時は自動）")
    parser.add_argument("--gas-url",  type=str,  default=None, dest="gas_url",
                        help="GASウェブアプリURL（省略時はSheets書き込みをスキップ）")
    parser.add_argument("--no-sheet", action="store_true",    dest="no_sheet",
                        help="GASへの送信をスキップ（JSONのみ生成）")
    args = parser.parse_args()

    if args.from_date:
        start_date = datetime.strptime(args.from_date, "%Y-%m-%d")
    else:
        # 翌週月曜日をデフォルト開始日にする（日曜に実行 → 翌日月曜）
        today = datetime.now()
        days_until_monday = (7 - today.weekday()) % 7 or 7
        start_date = today + timedelta(days=days_until_monday)

    output_path = Path(args.output) if args.output else None

    posts = run(count=args.count, start_date=start_date, output_path=output_path)

    # ── GAS経由でSheets書き込み ──
    if not args.no_sheet and posts:
        print("\n📊 GAS経由でSheetsに書き込み中...", file=sys.stderr)
        try:
            from gas import push, GAS_URL
            url = args.gas_url or GAS_URL
            added = push(posts=posts, gas_url=url)
            print(f"   ✅ Sheets書き込み完了: {added}行追加", file=sys.stderr)
        except Exception as e:
            print(f"   ✗ GAS書き込みエラー: {e}", file=sys.stderr)
            print("   ヒント: --no-sheet オプションでスキップできます", file=sys.stderr)


if __name__ == "__main__":
    main()
