// Builds a single self-contained preview page (drafts embedded, nothing sent anywhere)
// for a private Claude artifact or for opening straight from disk.
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
let html = fs.readFileSync(path.join(ROOT, 'public', 'index.html'), 'utf8');
const data = fs.readFileSync(path.join(ROOT, 'data', 'programs.json'), 'utf8');
const seed = `<script id="seed" type="application/json">${JSON.stringify(JSON.parse(data)).replace(/</g, '\\u003c')}</script>\n`;
const i = html.indexOf('<script>\n(() => {');
if (i < 0) throw new Error('app script not found');
html = html.slice(0, i) + seed + html.slice(i);
// The artifact host adds its own document skeleton, charset and viewport.
const forArtifact = process.argv.includes('--artifact');
if (forArtifact) {
  html = html
    .replace(/<!doctype html>\s*/i, '')
    .replace(/<html[^>]*>\s*/i, '').replace(/<\/html>\s*$/i, '')
    .replace(/<head>\s*/i, '').replace(/<\/head>\s*/i, '')
    .replace(/<meta charset="utf-8">\s*/i, '')
    .replace(/<meta name="viewport"[^>]*>\s*/i, '')
    .replace(/<body>\s*/i, '').replace(/<\/body>\s*/i, '');
}
const out = path.join(ROOT, 'dist', forArtifact ? 'bit-intake-review.html' : 'bit-intake-review-offline.html');
fs.mkdirSync(path.dirname(out), {recursive: true});
fs.writeFileSync(out, html);
console.log('wrote', out, (html.length / 1024).toFixed(1) + 'KB');
