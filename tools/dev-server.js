// Local test server: serves public/, runs the two API routes, and runs the real Apps Script code
// (google-apps-script/Code.gs) against an in-memory sheet so the whole path can be tested without Google.
// Usage: node tools/dev-server.js [port]   (NO_SHEET=1 to test the "sheet not connected" path)
const http = require('http'), fs = require('fs'), path = require('path'), vm = require('vm'), url = require('url');
const ROOT = path.join(__dirname, '..');
const PORT = Number(process.argv[2] || 3100);
process.env.ACCESS_CODE = process.env.ACCESS_CODE || 'test-code';
process.env.SHEET_SECRET = 'dev-secret';
if (!process.env.NO_SHEET) process.env.SHEET_WEBHOOK_URL = `http://localhost:${PORT}/mock-sheet/exec`;

/* ---------- fake Google Sheets + Apps Script runtime ---------- */
const rows = [];
const fakeSheet = {
  appendRow(row) {
    rows.push(row.map(v => {
      if (typeof v !== 'string') return v;
      if (v.length > 50000) throw new Error('Your input contains more than the maximum of 50000 characters in a single cell.');
      if (v.startsWith("'")) return v.slice(1);
      if (/^[=+\-@]/.test(v)) return '#FORMULA ' + v;
      if (v.trim() !== '' && !isNaN(Number(v))) return Number(v);
      return v;
    }));
  },
  getDataRange() { return {getValues: () => rows.map(r => r.slice())}; },
  setFrozenRows() {}, getRange() { return {setFontWeight() {}}; }, setColumnWidths() {}
};
let created = false;
const sandbox = {
  SpreadsheetApp: {getActiveSpreadsheet: () => ({getSheetByName: () => created ? fakeSheet : null, insertSheet: () => { created = true; return fakeSheet; }})},
  ContentService: {createTextOutput: s => ({s, setMimeType() { return this; }}), MimeType: {JSON: 'json'}},
  LockService: {getScriptLock: () => ({waitLock() {}, releaseLock() {}})},
  JSON, String, Date
};
let code = fs.readFileSync(path.join(ROOT, 'google-apps-script', 'Code.gs'), 'utf8').replace("'REPLACE-WITH-A-LONG-RANDOM-STRING'", "'dev-secret'");
vm.createContext(sandbox);
vm.runInContext(code + '\nthis.doPost = doPost; this.doGet = doGet;', sandbox);
const results = new Map();

/* ---------- Vercel-style req/res shim ---------- */
function shim(res) {
  res.status = c => { res.statusCode = c; return res; };
  res.json = o => { if (!res.getHeader('Content-Type')) res.setHeader('Content-Type', 'application/json'); res.end(JSON.stringify(o)); return res; };
  return res;
}
const MIME = {'.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.json': 'application/json', '.css': 'text/css'};

http.createServer((req, res) => {
  const u = url.parse(req.url, true);
  let body = '';
  req.on('data', c => body += c);
  req.on('end', async () => {
    shim(res);
    try {
      if (u.pathname === '/mock-sheet/exec' && req.method === 'POST') {
        const out = sandbox.doPost({postData: {contents: body}});
        const id = String(results.size + 1); results.set(id, out.s);
        res.statusCode = 302; res.setHeader('Location', `/mock-sheet/result?id=${id}`); return res.end();
      }
      if (u.pathname === '/mock-sheet/result') { res.setHeader('Content-Type', 'application/json'); return res.end(results.get(u.query.id) || '{}'); }
      if (u.pathname === '/mock-sheet/exec' && req.method === 'GET') { const out = sandbox.doGet({parameter: u.query}); res.setHeader('Content-Type', 'application/json'); return res.end(out.s); }
      if (u.pathname === '/mock-sheet/rows') return res.json(rows);
      if (u.pathname.startsWith('/api/')) {
        const name = u.pathname.slice(5).replace(/[^a-z]/g, '');
        const file = path.join(ROOT, 'api', name + '.js');
        if (!fs.existsSync(file) || name.startsWith('_')) return res.status(404).json({error: 'not_found'});
        try { req.body = body && /json/.test(req.headers['content-type'] || '') ? JSON.parse(body) : body; } catch (e) { req.body = body; }
        return await require(file)(req, res);
      }
      const p = path.join(ROOT, 'public', u.pathname === '/' ? 'index.html' : path.normalize(u.pathname).replace(/^(\.\.[/\\])+/, ''));
      if (!p.startsWith(path.join(ROOT, 'public')) || !fs.existsSync(p)) { res.statusCode = 404; return res.end('not found'); }
      res.setHeader('Content-Type', MIME[path.extname(p)] || 'application/octet-stream');
      fs.createReadStream(p).pipe(res);
    } catch (e) { console.error(e); res.statusCode = 500; res.end(String(e)); }
  });
}).listen(PORT, () => console.log(`dev server on http://localhost:${PORT}  passcode: ${process.env.ACCESS_CODE}  sheet: ${process.env.NO_SHEET ? 'off' : 'mock'}`));
