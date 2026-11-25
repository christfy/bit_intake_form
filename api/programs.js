// GET /api/programs: the drafts, plus the latest saved answers per program from the team sheet.
const data = require('../data/programs.json');
const {codeOk, sheet} = require('./_lib');

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  if (req.method !== 'GET') { res.status(405).json({error: 'method_not_allowed'}); return; }
  if (!codeOk(req)) { res.status(401).json({error: 'passcode'}); return; }
  let latest = {}, triage = null, status = 'not_configured';
  const s = await sheet('GET');
  if (s && s.ok) { latest = s.latest || {}; triage = s.triage || null; status = 'ok'; }
  else if (s && s.error) status = s.error;
  res.status(200).json({data, latest, triage, sheet: status});
};
