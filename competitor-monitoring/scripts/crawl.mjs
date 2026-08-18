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
import { mkdir, readFile, writeFile } from 'node:fs/promises';
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
    else if (a === '--out') out.out = argv[++i];
    else if (a === '--config') out.config = argv[++i];
    else if (a === '--date') out.date = argv[++i];
  }
  return out;
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const sha = (s) => createHash('sha256').update(s).digest('hex').slice(0, 16);

/* ---------------------------------------------------------------- fetching */

async function makeFetcher(useBrowser) {
  if (useBrowser !== false) {
    try {
      const { chromium } = await import('playwright');
      const browser = await chromium.launch({
        executablePath: process.env.PLAYWRIGHT_CHROMIUM_PATH || undefined,
      });
      const ctx = await browser.newContext({ userAgent: UA, locale: 'de-DE' });
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
    close: async () => {},
  };
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
    const res = await fetcher.get(sitemapUrl, { timeoutMs: opts.timeoutMs });
    if (res.status >= 400) return [];
    xml = res.html;
  } catch { return []; }
  const locs = [...xml.matchAll(/<loc>\s*([^<\s]+)\s*<\/loc>/gi)].map((m) => m[1]);
  if (/<sitemapindex/i.test(xml)) {
    const nested = [];
    for (const loc of locs) nested.push(...(await sitemapUrls(fetcher, loc, opts, seen)));
    return nested;
  }
  return locs;
}

async function robotsSitemaps(fetcher, host, opts) {
  try {
    const res = await fetcher.get(`https://${host}/robots.txt`, { timeoutMs: opts.timeoutMs });
    if (res.status >= 400) return { robots: null, sitemaps: [] };
    return {
      robots: res.html.slice(0, 4000),
      sitemaps: [...res.html.matchAll(/^\s*sitemap:\s*(\S+)/gim)].map((m) => m[1]),
    };
  } catch { return { robots: null, sitemaps: [] }; }
}

async function crawlSite(site, opts) {
  const fetcher = await makeFetcher();
  const excludes = (site.excludePatterns ?? []).map((p) => new RegExp(p, 'i'));
  const allowedHost = (h) => site.hosts.some((sh) => h === sh || h.endsWith(`.${sh}`));
  const inScope = (u) => {
    try {
      const url = new URL(u);
      return /^https?:$/.test(url.protocol) && allowedHost(url.hostname) && !excludes.some((r) => r.test(u));
    } catch { return false; }
  };

  const primaryHost = site.hosts[0];
  const { robots, sitemaps } = await robotsSitemaps(fetcher, primaryHost, opts);
  const sitemapCandidates = [...new Set([...(site.sitemaps ?? []), ...sitemaps])];

  const discovered = [];
  for (const sm of sitemapCandidates) discovered.push(...(await sitemapUrls(fetcher, sm, opts)));

  const queue = [...new Set([
    ...Object.values(site.keyPages ?? {}),
    ...(site.bases ?? []),
    ...discovered.filter(inScope),
  ])].filter(inScope);

  const visited = new Set();
  const pages = [];
  const errors = [];

  while (queue.length && pages.length < opts.maxPages) {
    const url = queue.shift();
    if (visited.has(url)) continue;
    visited.add(url);
    let shot;
    if (opts.screenshots && Object.values(site.keyPages ?? {}).includes(url)) {
      shot = resolve(opts.outDir, 'screenshots', `${sha(url)}.png`);
      await mkdir(dirname(shot), { recursive: true });
    }
    try {
      const res = await fetcher.get(url, { timeoutMs: opts.timeoutMs, screenshotPath: shot });
      const page = extract(url, res.finalUrl, res.status, res.html);
      if (shot) page.screenshot = shot.replace(`${ROOT}/`, '');
      pages.push(page);
      if (res.status < 400) {
        for (const link of linkUrls(res.html, res.finalUrl || url)) {
          if (inScope(link) && !visited.has(link) && queue.length + pages.length < opts.maxPages * 3) queue.push(link);
        }
      }
      process.stderr.write(`  [${pages.length}/${opts.maxPages}] ${res.status} ${url}\n`);
    } catch (err) {
      errors.push({ url, error: String(err.message ?? err).split('\n')[0] });
      process.stderr.write(`  [err] ${url}: ${errors.at(-1).error}\n`);
    }
    await sleep(opts.delayMs);
  }

  await fetcher.close();

  return {
    site: site.id,
    name: site.name,
    role: site.role,
    crawledAt: new Date().toISOString(),
    fetchMode: fetcher.mode,
    robotsTxtPresent: Boolean(robots),
    robotsTxtExcerpt: robots,
    sitemapsFound: sitemapCandidates,
    sitemapUrlCount: discovered.length,
    pageCount: pages.length,
    truncated: queue.length > 0,
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
  const snapshot = await crawlSite(site, { ...opts, outDir });
  const file = resolve(outDir, `${date}.json`);
  await writeFile(file, `${JSON.stringify(snapshot, null, 2)}\n`);
  console.error(`-> ${snapshot.pageCount} Seiten, ${snapshot.errors.length} Fehler, geschrieben nach ${file}`);
}
