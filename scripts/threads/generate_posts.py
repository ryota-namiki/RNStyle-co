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
import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

# ──────────────────────────────────────────────
# 設定
# ──────────────────────────────────────────────

MODEL = "claude-opus-4-6"

# 月〜金、1日2投稿（12:00 & 20:00）= 週10投稿
POSTING_WEEKDAYS = [0, 1, 2, 3, 4]   # Mon=0 … Fri=4
POSTING_TIMES    = ["12:00", "20:00"] # 1日2スロット

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

def run(count: int, start_date: datetime, output_path: Path | None):
    client = anthropic.Anthropic()

    print(f"\n{'='*50}", file=sys.stderr)
    print(f"  Threads投稿生成 | {start_date.date()} 〜 | {count}本", file=sys.stderr)
    print(f"{'='*50}\n", file=sys.stderr)

    # ── Phase 1: リサーチ ──
    print("📡 Phase 1: リサーチ中...", file=sys.stderr)
    res = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        messages=[{"role": "user", "content": RESEARCH_PROMPT}],
    )
    research_raw = res.content[0].text.strip()
    try:
        research = json.loads(research_raw)
        print(f"   ✓ ペインポイント {len(research.get('pain_points', []))}件 取得", file=sys.stderr)
    except json.JSONDecodeError:
        print("   ⚠ リサーチのJSONパース失敗。テキストをそのまま使用", file=sys.stderr)
        research = {"raw": research_raw}

    # ── Phase 2: 戦略立案 ──
    month = start_date.strftime("%Y-%m")
    print("\n🎯 Phase 2: 戦略立案中...", file=sys.stderr)
    strategy_prompt = STRATEGY_PROMPT_TEMPLATE.format(
        persona=PERSONA,
        research=json.dumps(research, ensure_ascii=False, indent=2),
        month=month,
        count=count,
    )
    res = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": strategy_prompt}],
    )
    strategy_raw = res.content[0].text.strip()
    try:
        strategy = json.loads(strategy_raw)
        print(f"   ✓ 戦略: {strategy.get('strategy_summary', '')}", file=sys.stderr)
        print(f"   ✓ テーマ {len(strategy.get('themes', []))}件 立案", file=sys.stderr)
    except json.JSONDecodeError:
        print("   ✗ 戦略のJSONパース失敗", file=sys.stderr)
        sys.exit(1)

    # ── Phase 3: 投稿生成 ──
    print(f"\n✍️  Phase 3: 投稿生成中 ({count}本)...", file=sys.stderr)
    schedule = build_schedule(start_date, count)
    themes = strategy.get("themes", [])
    posts = []

    for i, theme_data in enumerate(themes[:count]):
        pillar = theme_data.get("pillar", PILLAR_DISTRIBUTION[i % len(PILLAR_DISTRIBUTION)])
        children_count = theme_data.get("children_count", 2)

        prompt = POST_GENERATION_PROMPT_TEMPLATE.format(
            persona=PERSONA,
            pillar=pillar,
            theme=theme_data.get("theme", ""),
            angle=theme_data.get("angle", ""),
            hook=theme_data.get("hook", ""),
            children_count=children_count,
        )

        res = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        post_raw = res.content[0].text.strip()

        try:
            post_content = json.loads(post_raw)
            scheduled_at = schedule[i].strftime("%Y-%m-%dT%H:%M:00+09:00") if i < len(schedule) else None
            post = {
                "id": f"post-{i+1:03d}",
                "status": "pending",
                "scheduled_at": scheduled_at,
                "pillar": pillar,
                "theme": theme_data.get("theme", ""),
                **post_content,
            }
            posts.append(post)
            print(f"   ✓ [{i+1:02d}/{count}] {pillar:12s} | {theme_data.get('theme', '')[:30]}", file=sys.stderr)
        except json.JSONDecodeError:
            print(f"   ✗ [{i+1:02d}/{count}] JSONパース失敗 — スキップ", file=sys.stderr)

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
    print(f"  投稿数: {len(posts)}本 (月〜金 × 12:00/20:00)", file=sys.stderr)
    if schedule:
        print(f"  期間: {schedule[0].strftime('%Y/%m/%d %H:%M')} 〜 {schedule[-1].strftime('%Y/%m/%d %H:%M')}", file=sys.stderr)
    print(f"{'='*50}\n", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="Threads投稿を リサーチ → 戦略立案 → JSON生成 で自動作成",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
例:
  python generate_posts.py                          # 翌週月曜から10本（デフォルト）
  python generate_posts.py --count 10 --from 2026-04-07
  python generate_posts.py --count 20              # 2週間分
        """,
    )
    parser.add_argument("--count", type=int, default=10, help="生成する投稿数（デフォルト: 10 = 1週間分）")
    parser.add_argument("--from",  type=str, default=None, dest="from_date",
                        help="開始日 YYYY-MM-DD（デフォルト: 翌週月曜日）")
    parser.add_argument("--output", type=str, default=None, help="出力ファイルパス（省略時は自動）")
    args = parser.parse_args()

    if args.from_date:
        start_date = datetime.strptime(args.from_date, "%Y-%m-%d")
    else:
        # 翌週月曜日をデフォルト開始日にする
        today = datetime.now()
        days_until_monday = (7 - today.weekday()) % 7 or 7
        start_date = today + timedelta(days=days_until_monday)

    output_path = Path(args.output) if args.output else None

    run(count=args.count, start_date=start_date, output_path=output_path)


if __name__ == "__main__":
    main()
