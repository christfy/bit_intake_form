/**
 * BiT Intake & Review: receives confirmations from the Vercel page and writes them to this sheet.
 *
 * Setup (once):
 * 1. Make a Google Sheet. Extensions > Apps Script. Paste this file over Code.gs.
 * 2. Set SECRET below to a long random string. Put the same value in Vercel as SHEET_SECRET.
 * 3. Deploy > New deployment > Web app. Execute as: Me. Who has access: Anyone.
 *    ("Anyone" is needed so Vercel's server can reach it; the SECRET is what keeps others out.)
 * 4. Copy the web app URL into Vercel as SHEET_WEBHOOK_URL.
 * If you change this code later, use Deploy > Manage deployments > Edit > New version, so the URL stays the same.
 */
const SECRET = 'REPLACE-WITH-A-LONG-RANDOM-STRING';
const SHEET_NAME = 'Responses';
const HEADERS = ['Received at', 'Kind', 'Program ID', 'Program', 'Confirmed by', 'Role', 'Summary',
  'Changed from draft', 'Still open', 'Answers', 'Draft version', 'Payload (JSON, may continue in next columns)'];
const PAYLOAD_COL = HEADERS.length; // 1-based column where the JSON starts
const CHUNK = 45000;                // a cell holds at most 50,000 characters

function doPost(e) {
  const lock = LockService.getScriptLock();
  try {
    const body = JSON.parse(e.postData.contents);
    if (!body || body.secret !== SECRET) return json_({ok: false, error: 'forbidden'});
    const p = body.payload || {};
    lock.waitLock(20000);
    const sh = sheet_();
    const payload = JSON.stringify(p);
    // Each JSON piece starts with "~" so Sheets never reads a piece as a number or a formula.
    const chunks = [];
    for (let i = 0; i < payload.length; i += CHUNK) chunks.push('~' + payload.slice(i, i + CHUNK));
    const row = [new Date(), safe_(p.kind), safe_(p.programId), safe_(p.programName), safe_(p.confirmedBy), safe_(p.role),
      safe_(clip_(p.summary)), safe_(clip_((p.changes || []).join('\n'))), safe_(clip_((p.open || []).join('\n'))),
      safe_(clip_((p.answers || []).join('\n'))), safe_(p.draftVersion)].concat(chunks);
    sh.appendRow(row);
    return json_({ok: true});
  } catch (err) {
    return json_({ok: false, error: String(err).slice(0, 200)});
  } finally {
    try { lock.releaseLock(); } catch (x) {}
  }
}

/** Returns the newest saved answers for each program, and the newest quick-check answers. */
function doGet(e) {
  if (!e || !e.parameter || e.parameter.secret !== SECRET) return json_({ok: false, error: 'forbidden'});
  const sh = sheet_();
  const values = sh.getDataRange().getValues();
  const latest = {};
  let triage = null;
  for (let r = 1; r < values.length; r++) {
    const row = values[r];
    const raw = row.slice(PAYLOAD_COL - 1).map(String).filter(Boolean).map(s => s.charAt(0) === '~' ? s.slice(1) : s).join('');
    if (!raw) continue;
    let p;
    try { p = JSON.parse(raw); } catch (x) { continue; }
    if (p.kind === 'triage') { if (!triage || String(p.at) > String(triage.at)) triage = p; continue; }
    if (!p.programId) continue;
    const prev = latest[p.programId];
    if (!prev || String(p.at) > String(prev.at)) {
      latest[p.programId] = {kind: p.kind, at: p.at, confirmedBy: p.confirmedBy || '', role: p.role || '', profile: p.profile};
    }
  }
  return json_({ok: true, latest: latest, triage: triage});
}

function sheet_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sh = ss.getSheetByName(SHEET_NAME);
  if (!sh) {
    sh = ss.insertSheet(SHEET_NAME);
    sh.appendRow(HEADERS);
    sh.setFrozenRows(1);
    sh.getRange(1, 1, 1, HEADERS.length).setFontWeight('bold');
    sh.setColumnWidths(7, 4, 320);
  }
  return sh;
}
// Text that starts with = + - or @ would run as a formula; a leading apostrophe keeps it as plain text.
function safe_(s) { s = String(s == null ? '' : s); return /^[=+\-@]/.test(s) ? "'" + s : s; }
function clip_(s) { s = String(s || ''); return s.length > 45000 ? s.slice(0, 45000) + ' …' : s; }
function json_(o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }
