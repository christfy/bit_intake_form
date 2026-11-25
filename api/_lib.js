// Shared helpers for the two API routes. Files starting with "_" are not deployed as routes.
const crypto = require('crypto');

// The passcode lives only in the ACCESS_CODE environment variable on Vercel.
function codeOk(req) {
  const want = process.env.ACCESS_CODE || '';
  const got = String(req.headers['x-access-code'] || '');
  if (!want || !got) return false;
  const a = crypto.createHash('sha256').update(got).digest();
  const b = crypto.createHash('sha256').update(want).digest();
  return crypto.timingSafeEqual(a, b);
}

// Talks to the Google Apps Script web app that writes to the team sheet.
// SHEET_WEBHOOK_URL and SHEET_SECRET stay on the server; the browser never sees them.
async function sheet(method, payload) {
  const url = process.env.SHEET_WEBHOOK_URL;
  const secret = process.env.SHEET_SECRET;
  if (!url || !secret) return {ok: false, error: 'not_configured'};
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), 15000);
  try {
    let r;
    if (method === 'GET') {
      r = await fetch(url + (url.includes('?') ? '&' : '?') + 'secret=' + encodeURIComponent(secret), {redirect: 'follow', signal: ctrl.signal});
    } else {
      // Apps Script answers a POST with a redirect; fetch follows it with a GET, which returns the JSON result.
      r = await fetch(url, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({secret, payload}), redirect: 'follow', signal: ctrl.signal});
    }
    const text = await r.text();
    try { return JSON.parse(text); } catch (e) { return {ok: false, error: 'bad_response', detail: text.slice(0, 200)}; }
  } catch (e) {
    return {ok: false, error: e.name === 'AbortError' ? 'timeout' : 'unreachable'};
  } finally {
    clearTimeout(timer);
  }
}

function readBody(req) {
  if (req.body && typeof req.body === 'object') return req.body;
  if (typeof req.body === 'string') { try { return JSON.parse(req.body); } catch (e) { return null; } }
  return null;
}

module.exports = {codeOk, sheet, readBody};
