#!/usr/bin/env node
/**
 * Vergleicht zwei Snapshots derselben Site und schreibt einen Änderungsbericht
 * (Markdown) nach stdout.
 *
 * Nutzung:
 *   node scripts/diff.mjs --site simplesystem                  # letzte zwei Snapshots
 *   node scripts/diff.mjs --site simplesystem --from 2026-08-01 --to 2026-09-01
 *   node scripts/diff.mjs --site simplesystem --json           # maschinenlesbar
 */
import { readdir, readFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');

function args(argv) {
  const out = {};
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--site') out.site = argv[++i];
    else if (a === '--from') out.from = argv[++i];
    else if (a === '--to') out.to = argv[++i];
    else if (a === '--dir') out.dir = argv[++i];
    else if (a === '--json') out.json = true;
  }
  return out;
}

const opts = args(process.argv);
if (!opts.site && !opts.dir) {
  console.error('--site <id> erforderlich');
  process.exit(1);
}

const dir = opts.dir ?? resolve(ROOT, 'snapshots', opts.site);
const files = (await readdir(dir)).filter((f) => /^\d{4}-\d{2}-\d{2}\.json$/.test(f)).sort();
if (files.length < 2 && !(opts.from && opts.to)) {
  console.error(`Mindestens zwei Snapshots nötig in ${dir} (gefunden: ${files.length}).`);
  process.exit(2);
}
const fromFile = opts.from ? `${opts.from}.json` : files.at(-2);
const toFile = opts.to ? `${opts.to}.json` : files.at(-1);

const prev = JSON.parse(await readFile(resolve(dir, fromFile), 'utf8'));
const curr = JSON.parse(await readFile(resolve(dir, toFile), 'utf8'));

const byUrl = (snap) => new Map(snap.pages.map((p) => [p.canonical || p.url, p]));
const a = byUrl(prev);
const b = byUrl(curr);

const added = [...b.keys()].filter((u) => !a.has(u));
const removed = [...a.keys()].filter((u) => !b.has(u));
const changed = [];

for (const [url, cp] of b) {
  const pp = a.get(url);
  if (!pp) continue;
  const fields = [];
  const cmp = (label, x, y) => {
    if (JSON.stringify(x) !== JSON.stringify(y)) fields.push({ field: label, before: x, after: y });
  };
  cmp('title', pp.title, cp.title);
  cmp('metaDescription', pp.metaDescription, cp.metaDescription);
  cmp('h1', pp.h1, cp.h1);
  cmp('status', pp.status, cp.status);
  cmp('robotsMeta', pp.robotsMeta, cp.robotsMeta);
  cmp('schemaTypes', pp.schemaTypes, cp.schemaTypes);
  cmp('prices', pp.prices, cp.prices);
  cmp('hreflang', pp.hreflang?.map((h) => h.lang).sort(), cp.hreflang?.map((h) => h.lang).sort());
  const wordDelta = (cp.wordCount ?? 0) - (pp.wordCount ?? 0);
  const bodyChanged = pp.textHash !== cp.textHash;
  if (bodyChanged) fields.push({ field: 'bodyText', before: `${pp.wordCount} Wörter`, after: `${cp.wordCount} Wörter (${wordDelta >= 0 ? '+' : ''}${wordDelta})` });
  if (fields.length) changed.push({ url, fields, h2Added: (cp.h2 ?? []).filter((h) => !(pp.h2 ?? []).includes(h)).slice(0, 8) });
}

const result = {
  site: curr.site,
  name: curr.name,
  from: fromFile.replace('.json', ''),
  to: toFile.replace('.json', ''),
  pageCountBefore: prev.pageCount,
  pageCountAfter: curr.pageCount,
  added,
  removed,
  changed,
};

if (opts.json) {
  console.log(JSON.stringify(result, null, 2));
  process.exit(0);
}

const esc = (s) => String(s).replace(/\|/g, '\\|').replace(/\s*\n\s*/g, ' ');
const fmt = (v) => {
  if (v === null || v === undefined) return '_(leer)_';
  if (Array.isArray(v)) return v.length ? v.map(esc).join(' · ') : '_(leer)_';
  return esc(v).slice(0, 300);
};
const lines = [];
lines.push(`## Änderungen: ${result.name} (${result.from} → ${result.to})`, '');
lines.push(`Seiten erfasst: ${result.pageCountBefore} → ${result.pageCountAfter}. Neu: ${added.length}, entfernt: ${removed.length}, geändert: ${changed.length}.`, '');

if (added.length) {
  lines.push('### Neue Seiten', '');
  for (const u of added) {
    const p = b.get(u);
    lines.push(`- ${u}${p?.title ? `: "${p.title}"` : ''}`);
  }
  lines.push('');
}
if (removed.length) {
  lines.push('### Entfernte Seiten', '', ...removed.map((u) => `- ${u}`), '');
}
if (changed.length) {
  lines.push('### Geänderte Seiten', '');
  for (const c of changed) {
    lines.push(`#### ${c.url}`, '');
    lines.push('| Feld | Vorher | Nachher |', '|---|---|---|');
    for (const f of c.fields) lines.push(`| ${f.field} | ${fmt(f.before)} | ${fmt(f.after)} |`);
    if (c.h2Added.length) lines.push('', `Neue H2: ${c.h2Added.map((h) => `"${h}"`).join(', ')}`);
    lines.push('');
  }
}
if (!added.length && !removed.length && !changed.length) lines.push('Keine Änderungen erkannt.', '');

console.log(lines.join('\n'));
