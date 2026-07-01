/**
 * Threads投稿管理 - GAS Webアプリ
 *
 * 設定:
 *   デプロイ → ウェブアプリ
 *   実行ユーザー: 自分
 *   アクセスできるユーザー: 全員
 *
 * 受け取るJSON:
 * {
 *   "posts": [
 *     {
 *       "id": "post-001",
 *       "status": "pending",
 *       "scheduled_date": "2026-04-07",
 *       "scheduled_time": "07:32",
 *       "scheduled_at": "2026-04-07T07:32:00+09:00",
 *       "pillar": "pain",
 *       "theme": "...",
 *       "parent_text": "...",
 *       "child1_delay_min": 60,
 *       "child1_text": "...",
 *       "child2_delay_min": 60,
 *       "child2_text": "..."
 *     }
 *   ]
 * }
 */

const SHEET_NAME = "posts";

const HEADERS = [
  "id",               // A
  "status",           // B: pending / posted / skipped
  "scheduled_date",   // C: YYYY-MM-DD（Makeのフィルタ用）
  "scheduled_time",   // D: HH:MM（Makeのフィルタ用）
  "scheduled_at",     // E: ISO8601フル
  "pillar",           // F
  "theme",            // G
  "parent_text",      // H
  "child1_delay_min", // I
  "child1_text",      // J
  "child2_delay_min", // K
  "child2_text",      // L
  "posted_at",        // M ← Makeが記入
  "parent_post_id",   // N ← Makeが記入
];

// ── POSTリクエスト受信 ──────────────────────────────────

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    const posts = data.posts || [];

    const result = writePosts(posts);

    return ContentService
      .createTextOutput(JSON.stringify({ success: true, ...result }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ success: false, error: err.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

// ── GETリクエスト（動作確認用） ─────────────────────────

function doGet(e) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const ws = ss.getSheetByName(SHEET_NAME);
  const rowCount = ws ? Math.max(ws.getLastRow() - 1, 0) : 0;

  return ContentService
    .createTextOutput(JSON.stringify({
      status: "ok",
      sheet: SHEET_NAME,
      total_rows: rowCount,
    }))
    .setMimeType(ContentService.MimeType.JSON);
}

// ── Sheets書き込み ──────────────────────────────────────

function writePosts(posts) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let ws = ss.getSheetByName(SHEET_NAME);

  // シートがなければ作成
  if (!ws) {
    ws = ss.insertSheet(SHEET_NAME);
    ws.appendRow(HEADERS);
    ws.getRange(1, 1, 1, HEADERS.length).setFontWeight("bold");
    ws.setFrozenRows(1);
    ws.setColumnWidth(8, 400);  // parent_text列を広く
    ws.setColumnWidth(10, 400); // child1_text列
    ws.setColumnWidth(12, 400); // child2_text列
  }

  // 既存IDを取得（重複防止）
  const lastRow = ws.getLastRow();
  const existingIds = new Set(
    lastRow > 1
      ? ws.getRange(2, 1, lastRow - 1, 1).getValues().flat().filter(v => v !== "")
      : []
  );

  let added = 0;
  let skipped = 0;
  const rowsToAppend = [];

  for (const post of posts) {
    if (existingIds.has(post.id)) {
      skipped++;
      continue;
    }

    rowsToAppend.push([
      post.id               || "",
      post.status           || "pending",
      post.scheduled_date   || "",
      post.scheduled_time   || "",
      post.scheduled_at     || "",
      post.pillar           || "",
      post.theme            || "",
      post.parent_text      || "",
      post.child1_delay_min !== undefined ? post.child1_delay_min : 60,
      post.child1_text      || "",
      post.child2_delay_min !== undefined ? post.child2_delay_min : "",
      post.child2_text      || "",
      "",  // posted_at    ← Makeが記入
      "",  // parent_post_id ← Makeが記入
    ]);
    added++;
  }

  if (rowsToAppend.length > 0) {
    ws.getRange(ws.getLastRow() + 1, 1, rowsToAppend.length, HEADERS.length)
      .setValues(rowsToAppend);
  }

  return { added, skipped };
}
