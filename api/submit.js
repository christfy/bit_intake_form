// POST /api/submit: a confirmation, saved progress, or the quick-check answers. Forwards to the team sheet.
const data = require('../data/programs.json');
const {codeOk, sheet, readBody} = require('./_lib');

const KINDS = new Set(['confirmed', 'progress', 'triage']);
const IDS = new Set(data.programs.map(p => p.id));
const MAX = 200 * 1024;

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  if (req.method !== 'POST') { res.status(405).json({error: 'method_not_allowed'}); return; }
  if (!codeOk(req)) { res.status(401).json({error: 'passcode'}); return; }
  const p = readBody(req);
  if (!p || typeof p !== 'object') { res.status(400).json({error: 'bad_json'}); return; }
  if (!KINDS.has(p.kind)) { res.status(400).json({error: 'bad_kind'}); return; }
  if (p.kind !== 'triage' && !IDS.has(p.programId)) { res.status(400).json({error: 'unknown_program'}); return; }
  if (p.kind === 'confirmed' && !String(p.confirmedBy || '').trim()) { res.status(400).json({error: 'missing_name'}); return; }
  if (JSON.stringify(p).length > MAX) { res.status(413).json({error: 'too_large'}); return; }
  p.receivedAt = new Date().toISOString();
  const s = await sheet('POST', p);
  if (!s || !s.ok) { res.status(s && s.error === 'not_configured' ? 503 : 502).json({error: (s && s.error) || 'sheet_failed'}); return; }
  res.status(200).json({ok: true});
};
