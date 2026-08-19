#!/usr/bin/env node
/**
 * Crawlt eine im Registry (competitors.json) definierte Site und schreibt einen
 * strukturierten Snapshot nach snapshots/<site-id>/<YYYY-MM-DD>.json
 *
 * Nutzung:
 *   node scripts/crawl.mjs --site simplesystem
 *   node scripts/crawl.mjs --site hivebuy --max-pages 200 --screenshots
 *   node scripts/crawl.mjs --all
 *
 * Holt Seiten per Playwright/Chromium (falls installiert, umgeht die meisten
 * Bot-Blocker) und fällt sonst auf fetch() mit Browser-User-Agent zurück.
 * Erfordert freigeschalteten Netzwerk-Egress für die Ziel-Domains.
 */
import { createHash } from 'node:crypto';
import { mkdir, readdir, readFile, stat, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36';

function args(argv) {
  const out = { maxPages: 120, delayMs: 700, timeoutMs: 25000 };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--site') out.site = argv[++i];
    else if (a === '--all') out.all = true;
    else if (a === '--max-pages') out.maxPages = Number(argv[++i]);
    else if (a === '--delay-ms') out.delayMs = Number(argv[++i]);
    else if (a === '--screenshots') out.screenshots = true;
    else if (a === '--no-screenshots') out.screenshots = false;
    else if (a === '--no-browser') out.noBrowser = true;
    else if (a === '--out') out.out = argv[++i];
    else if (a === '--config') out.config = argv[++i];
    else if (a === '--date') out.date = argv[++i];
  }
  return out;
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const sha = (s) => createHash('sha256').update(s).digest('hex').slice(0, 16);

/* ---------------------------------------------------------------- fetching */

/**
 * Playwright bringt eine eigene Chromium-Build-Nummer mit. Passt die nicht zu dem
 * Chromium, das in der Umgebung liegt, schlägt der Standard-Launch fehl. Dann
 * suchen wir die vorhandene Binary selbst.
 */
async function resolveChromiumPath() {
  if (process.env.PLAYWRIGHT_CHROMIUM_PATH) return process.env.PLAYWRIGHT_CHROMIUM_PATH;
  const root = process.env.PLAYWRIGHT_BROWSERS_PATH || '/opt/pw-browsers';
  const candidates = [];
  try {
    for (const entry of await readdir(root)) {
      if (entry.startsWith('chromium-')) candidates.push(resolve(root, entry, 'chrome-linux', 'chrome'));
      if (entry.startsWith('chromium_headless_shell-')) candidates.push(resolve(root, entry, 'chrome-linux', 'headless_shell'));
    }
  } catch { return undefined; }
  for (const c of candidates) {
    try { await stat(c); return c; } catch { /* weiter */ }
  }
  return undefined;
}

async function makeFetcher(useBrowser) {
  if (useBrowser !== false) {
    try {
      const { chromium } = await import('playwright');
      const httpsProxy = process.env.HTTPS_PROXY || process.env.https_proxy;
      const launchOpts = httpsProxy ? { proxy: { server: httpsProxy } } : {};
      let browser;
      try {
        browser = await chromium.launch(launchOpts);
      } catch (launchErr) {
        const executablePath = await resolveChromiumPath();
        if (!executablePath) throw launchErr;
        browser = await chromium.launch({ ...launchOpts, executablePath });
        process.stderr.write(`[info] Chromium aus der Umgebung genutzt: ${executablePath}\n`);
      }
      const ctx = await browser.newContext({ userAgent: UA, locale: 'de-DE', viewport: { width: 1440, height: 900 } });
      return {
        mode: 'playwright',
        async get(url, { timeoutMs, screenshotPath }) {
          const page = await ctx.newPage();
          try {
            const res = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: timeoutMs });
            await page.waitForLoadState('networkidle', { timeout: 5000 }).catch(() => {});
            if (screenshotPath) await page.screenshot({ path: screenshotPath, fullPage: true });
            return { status: res?.status() ?? 0, html: await page.content(), finalUrl: page.url() };
          } finally {
            await page.close();
          }
        },
        async shot({ url, selector, fullPage, path, timeoutMs, hideSelectors }) {
          const page = await ctx.newPage();
          try {
            await page.goto(url, { waitUntil: 'domcontentloaded', timeout: timeoutMs });
            await page.waitForLoadState('networkidle', { timeout: 8000 }).catch(() => {});
            for (const sel of hideSelectors ?? []) {
              await page.locator(sel).first().evaluate((el) => { el.style.display = 'none'; }).catch(() => {});
            }
            if (selector) {
              const target = page.locator(selector).first();
              await target.waitFor({ state: 'visible', timeout: 10000 });
              await target.scrollIntoViewIfNeeded().catch(() => {});
              await target.screenshot({ path });
            } else {
              await page.screenshot({ path, fullPage: fullPage !== false });
            }
          } finally {
            await page.close();
          }
        },
        close: () => browser.close(),
      };
    } catch (err) {
      console.error(`[info] Playwright nicht nutzbar (${err.message.split('\n')[0]}), fallback auf fetch()`);
    }
  }
  return {
    mode: 'fetch',
    async get(url, { timeoutMs }) {
      const res = await fetch(url, {
        headers: { 'user-agent': UA, 'accept-language': 'de-DE,de;q=0.9,en;q=0.8' },
        redirect: 'follow',
        signal: AbortSignal.timeout(timeoutMs),
      });
      return { status: res.status, html: await res.text(), finalUrl: res.url };
    },
    async shot() {
      throw new Error('Screenshots brauchen Playwright (npm install playwright)');
    },
    close: async () => {},
  };
}

/**
 * Textdateien (robots.txt, Sitemaps) direkt laden. Über den Browser käme der
 * Inhalt in ein <pre> verpackt zurück und wäre nicht mehr zeilenweise parsebar.
 */
async function getText(fetcher, url, timeoutMs) {
  try {
    const res = await fetch(url, {
      headers: { 'user-agent': UA },
      redirect: 'follow',
      signal: AbortSignal.timeout(timeoutMs),
    });
    return { status: res.status, text: await res.text() };
  } catch {
    const res = await fetcher.get(url, { timeoutMs });
    const pre = res.html.match(/<pre[^>]*>([\s\S]*?)<\/pre>/i);
    const text = (pre ? pre[1] : res.html)
      .replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&amp;/g, '&');
    return { status: res.status, text };
  }
}

/* -------------------------------------------------------------- extraction */

const attr = (tag, name) => tag.match(new RegExp(`${name}\\s*=\\s*["']([^"']*)["']`, 'i'))?.[1] ?? null;
const metaTags = (html) => html.match(/<meta\b[^>]*>/gi) ?? [];

function metaContent(html, key) {
  for (const tag of metaTags(html)) {
    const n = (attr(tag, 'name') || attr(tag, 'property') || '').toLowerCase();
    if (n === key) return attr(tag, 'content');
  }
  return null;
}

function visibleText(html) {
  return html
    .replace(/<head\b[\s\S]*?<\/head>/i, ' ')
    .replace(/<(script|style|noscript|svg|template)\b[\s\S]*?<\/\1>/gi, ' ')
    .replace(/<!--[\s\S]*?-->/g, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/\s+/g, ' ')
    .trim();
}

function headings(html, level) {
  return [...html.matchAll(new RegExp(`<h${level}\\b[^>]*>([\\s\\S]*?)</h${level}>`, 'gi'))]
    .map((m) => visibleText(m[1]))
    .filter(Boolean)
    .slice(0, 25);
}

function jsonLdTypes(html) {
  const types = new Set();
  for (const m of html.matchAll(/<script\b[^>]*application\/ld\+json[^>]*>([\s\S]*?)<\/script>/gi)) {
    try {
      const walk = (n) => {
        if (Array.isArray(n)) return n.forEach(walk);
        if (n && typeof n === 'object') {
          if (n['@type']) [].concat(n['@type']).forEach((t) => types.add(String(t)));
          Object.values(n).forEach(walk);
        }
      };
      walk(JSON.parse(m[1].trim()));
    } catch { types.add('__parse_error__'); }
  }
  return [...types].sort();
}

function priceMentions(text) {
  const hits = new Set();
  for (const m of text.matchAll(/(?:€|EUR|USD|\$)\s?\d[\d.,]*(?:\s?(?:\/|pro |per )\s?\w+)?|\d[\d.,]*\s?(?:€|EUR)(?:\s?(?:\/|pro |per )\s?\w+)?/gi)) {
    hits.add(m[0].replace(/\s+/g, ' ').trim());
  }
  return [...hits].slice(0, 40);
}

function linkUrls(html, baseUrl) {
  const urls = new Set();
  for (const m of html.matchAll(/<a\b[^>]*href\s*=\s*["']([^"']+)["']/gi)) {
    try {
      const u = new URL(m[1], baseUrl);
      u.hash = '';
      urls.add(u.toString());
    } catch { /* ignore */ }
  }
  return [...urls];
}

function extract(url, finalUrl, status, html) {
  const text = visibleText(html);
  const hreflang = [...html.matchAll(/<link\b[^>]*rel=["']alternate["'][^>]*>/gi)]
    .map((m) => ({ lang: attr(m[0], 'hreflang'), href: attr(m[0], 'href') }))
    .filter((h) => h.lang);
  return {
    url,
    finalUrl: finalUrl !== url ? finalUrl : undefined,
    status,
    title: html.match(/<title\b[^>]*>([\s\S]*?)<\/title>/i)?.[1]?.trim() ?? null,
    metaDescription: metaContent(html, 'description'),
    robotsMeta: metaContent(html, 'robots'),
    canonical: (html.match(/<link\b[^>]*rel=["']canonical["'][^>]*>/i)?.[0] ?? '') ? attr(html.match(/<link\b[^>]*rel=["']canonical["'][^>]*>/i)[0], 'href') : null,
    ogTitle: metaContent(html, 'og:title'),
    lang: html.match(/<html\b[^>]*\blang\s*=\s*["']([^"']+)["']/i)?.[1] ?? null,
    hreflang,
    h1: headings(html, 1),
    h2: headings(html, 2),
    wordCount: text ? text.split(/\s+/).length : 0,
    schemaTypes: jsonLdTypes(html),
    prices: priceMentions(text),
    textHash: sha(text),
    textExcerpt: text.slice(0, 1200),
  };
}

/* ---------------------------------------------------------------- crawling */

async function sitemapUrls(fetcher, sitemapUrl, opts, seen = new Set()) {
  if (seen.has(sitemapUrl) || seen.size > 40) return [];
  seen.add(sitemapUrl);
  let xml;
  try {
    const res = await getText(fetcher, sitemapUrl, opts.timeoutMs);
    if (res.status >= 400) return [];
    xml = res.text;
  } catch { return []; }
  const locs = [...xml.matchAll(/<loc>\s*([^<\s]+)\s*<\/loc>/gi)].map((m) => m[1]);
  if (/<sitemapindex/i.test(xml)) {
    const nested = [];
    for (const loc of locs) nested.push(...(await sitemapUrls(fetcher, loc, opts, seen)));
    return nested;
  }
  return locs;
}

/** Disallow-Regeln der für uns geltenden User-Agent-Blöcke ("*" und Chrome). */
function parseRobots(text) {
  const disallow = [];
  let applies = false;
  for (const raw of text.split(/\r?\n/)) {
    const line = raw.replace(/#.*$/, '').trim();
    if (!line) continue;
    const [rawKey, ...rest] = line.split(':');
    const key = rawKey.trim().toLowerCase();
    const value = rest.join(':').trim();
    if (key === 'user-agent') {
      applies = value === '*' || /chrome|mozilla/i.test(value);
    } else if (applies && key === 'disallow' && value) {
      disallow.push(value);
    } else if (applies && key === 'allow' && value) {
      disallow.push(`!${value}`);
    }
  }
  return disallow;
}

/** Sehr einfache robots-Auswertung: längste passende Regel gewinnt, Allow schlägt Disallow. */
function robotsAllows(rules, url) {
  if (!rules?.length) return true;
  const path = new URL(url).pathname;
  let best = { length: -1, allow: true };
  for (const rule of rules) {
    const allow = rule.startsWith('!');
    const literal = (allow ? rule.slice(1) : rule).replace(/\*+$/, '');
    if (path.startsWith(literal) && literal.length > best.length) best = { length: literal.length, allow };
  }
  return best.allow;
}

/**
 * robots.txt pro Origin (Schema + Host + Port), nicht pro Host: Subdomains und
 * abweichende Ports haben jeweils eigene Regeln.
 */
async function robotsForOrigins(fetcher, origins, opts) {
  const byOrigin = new Map();
  const sitemaps = [];
  for (const origin of origins) {
    let entry = { robots: null, rules: [] };
    try {
      const res = await getText(fetcher, `${origin}/robots.txt`, opts.timeoutMs);
      if (res.status < 400 && /disallow|allow|user-agent|sitemap/i.test(res.text)) {
        entry = { robots: res.text.slice(0, 4000), rules: parseRobots(res.text) };
        sitemaps.push(...[...res.text.matchAll(/^\s*sitemap:\s*(\S+)/gim)].map((m) => m[1]));
      }
    } catch { /* kein robots.txt erreichbar */ }
    byOrigin.set(origin, entry);
  }
  return { byOrigin, sitemaps };
}

async function crawlSite(site, opts) {
  const fetcher = await makeFetcher(opts.noBrowser ? false : undefined);
  const excludes = (site.excludePatterns ?? []).map((p) => new RegExp(p, 'i'));
  const allowedHost = (h) => site.hosts.some((sh) => h === sh || h.endsWith(`.${sh}`));
  const inScope = (u) => {
    try {
      const url = new URL(u);
      return /^https?:$/.test(url.protocol) && allowedHost(url.hostname) && !excludes.some((r) => r.test(u));
    } catch { return false; }
  };
  // robots.txt wird respektiert: gesperrte Pfade werden nicht abgerufen, aber protokolliert.
  const crawlable = (u) => {
    if (!inScope(u)) return false;
    if (robotsAllows(rulesFor(u), u)) return true;
    if (!robotsSkipped.includes(u) && robotsSkipped.length < 200) robotsSkipped.push(u);
    return false;
  };

  const startUrls = [...Object.values(site.keyPages ?? {}), ...(site.bases ?? [])];
  const origins = [...new Set([
    ...startUrls.map((u) => { try { return new URL(u).origin; } catch { return null; } }).filter(Boolean),
    ...site.hosts.map((h) => `https://${h}`),
  ])];
  const { byOrigin: robotsByOrigin, sitemaps } = await robotsForOrigins(fetcher, origins, opts);
  const rulesFor = (u) => {
    try { return robotsByOrigin.get(new URL(u).origin)?.rules ?? []; } catch { return []; }
  };
  const robotsSkipped = [];
  const sitemapCandidates = [...new Set([...(site.sitemaps ?? []), ...sitemaps])];

  const discovered = [];
  for (const sm of sitemapCandidates) discovered.push(...(await sitemapUrls(fetcher, sm, opts)));

  const queue = [...new Set([
    ...Object.values(site.keyPages ?? {}),
    ...(site.bases ?? []),
    ...discovered,
  ])].filter(crawlable);

  const visited = new Set();
  const pages = [];
  const errors = [];

  while (queue.length && pages.length < opts.maxPages) {
    const url = queue.shift();
    if (visited.has(url)) continue;
    visited.add(url);
    try {
      const res = await fetcher.get(url, { timeoutMs: opts.timeoutMs });
      const page = extract(url, res.finalUrl, res.status, res.html);
      pages.push(page);
      if (res.status < 400) {
        for (const link of linkUrls(res.html, res.finalUrl || url)) {
          if (crawlable(link) && !visited.has(link) && queue.length + pages.length < opts.maxPages * 3) queue.push(link);
        }
      }
      process.stderr.write(`  [${pages.length}/${opts.maxPages}] ${res.status} ${url}\n`);
    } catch (err) {
      errors.push({ url, error: String(err.message ?? err).split('\n')[0] });
      process.stderr.write(`  [err] ${url}: ${errors.at(-1).error}\n`);
    }
    await sleep(opts.delayMs);
  }

  // Screenshots: definierte Ausschnitte je Site, sonst Vollseite der keyPages.
  const shotSpecs = site.shots?.length
    ? site.shots
    : Object.entries(site.keyPages ?? {}).map(([name, url]) => ({ name, url, fullPage: true }));
  const screenshots = [];
  if (opts.screenshots !== false) {
    const shotDir = resolve(opts.outDir, 'screenshots', opts.date);
    await mkdir(shotDir, { recursive: true });
    for (const spec of shotSpecs) {
      const file = resolve(shotDir, `${spec.name.replace(/[^a-z0-9_-]+/gi, '-')}.png`);
      const entry = { name: spec.name, url: spec.url, selector: spec.selector ?? null, file: file.replace(`${ROOT}/`, '') };
      if (!robotsAllows(rulesFor(spec.url), spec.url)) {
        entry.error = 'per robots.txt gesperrt';
      } else {
        try {
          await fetcher.shot({ ...spec, path: file, timeoutMs: opts.timeoutMs });
          process.stderr.write(`  [shot] ${spec.name}${spec.selector ? ` (${spec.selector})` : ''}\n`);
        } catch (err) {
          entry.error = String(err.message ?? err).split('\n')[0];
          delete entry.file;
          process.stderr.write(`  [shot-err] ${spec.name}: ${entry.error}\n`);
        }
      }
      screenshots.push(entry);
      await sleep(opts.delayMs);
    }
  }

  await fetcher.close();

  return {
    site: site.id,
    name: site.name,
    role: site.role,
    crawledAt: new Date().toISOString(),
    fetchMode: fetcher.mode,
    robots: Object.fromEntries([...robotsByOrigin].map(([origin, r]) => [origin, {
      present: Boolean(r.robots),
      disallowRules: r.rules,
    }])),
    sitemapsFound: sitemapCandidates,
    sitemapUrlCount: discovered.length,
    pageCount: pages.length,
    truncated: queue.length > 0,
    robotsSkipped,
    screenshots,
    pages,
    errors,
  };
}

/* -------------------------------------------------------------------- main */

const opts = args(process.argv);
const configPath = opts.config ?? resolve(ROOT, 'competitors.json');
const config = JSON.parse(await readFile(configPath, 'utf8'));
const targets = opts.all ? config.sites : config.sites.filter((s) => s.id === opts.site);

if (!targets.length) {
  console.error(`Keine Site gefunden. Verfügbar: ${config.sites.map((s) => s.id).join(', ')}`);
  process.exit(1);
}

const date = opts.date ?? new Date().toISOString().slice(0, 10);
for (const site of targets) {
  const outDir = opts.out ?? resolve(ROOT, 'snapshots', site.id);
  await mkdir(outDir, { recursive: true });
  console.error(`\n=== ${site.name} (${site.id}) ===`);
  const snapshot = await crawlSite(site, { ...opts, outDir, date });
  const file = resolve(outDir, `${date}.json`);
  await writeFile(file, `${JSON.stringify(snapshot, null, 2)}\n`);
  console.error(`-> ${snapshot.pageCount} Seiten, ${snapshot.errors.length} Fehler, geschrieben nach ${file}`);
}
