# SEO Analysis: www.hivebuy.com (v2, first-party data)

**Date:** 2026-08-20
**Analyst:** Claude (automated analysis)
**Branch:** claude/seo-analysis-hivebuy-nlk2v
**Supersedes:** v1 (commit `bd9464c`, 2026-03-30)

---

## Data basis

This revision is built on first-party HubSpot data plus live HTTP checks, not on
Google search snippets. Everything below is traceable to one of these sources:

| Source | Scope |
|---|---|
| HubSpot content analytics, portal `145132698` | 2026-02-19 to 2026-08-19, TOTALS mode, top 100 rows by raw views |
| HubSpot CRM inventory | `SITE_PAGE` (175 records), `LANDING_PAGE` (16), `BLOG_POST` (52) |
| Live HTTP fetches | `robots.txt`, `sitemap.xml` (180 URLs), on-page audit of 25 pages |

### Why v1 had to be replaced

v1 was written when `www.hivebuy.com` returned HTTP 403 to the fetch tool, so it
inferred the site from Google result snippets. That inference was wrong on most
of its central points. The 403 turned out to be user-agent filtering only: with a
normal browser user agent the site responds 200, so a real audit was possible.

**v1 findings that are factually wrong and are retracted:**

| v1 claim | Verified reality |
|---|---|
| "Critical: German slugs under `/en/`" (`/en/preise-hivebuy`, `/en/ueber-hivebuy`) | Those URLs do not exist. German pages sit at root (`/preise-hivebuy`, `/ueber-hivebuy`). 105 root pages, 70 `/en/` pages. Partially valid in a different form, see 2.3. |
| "Critical: enforce www vs non-www 301" | Already correct. `http://hivebuy.com`, `https://hivebuy.com`, `http://www.hivebuy.com` all resolve to `https://www.hivebuy.com/`. |
| "robots.txt unknown, may throttle Googlebot" | robots.txt is clean, minimal, and declares the sitemap. No important section is blocked. |
| "No structured data confirmed, add `Organization` and `SoftwareApplication`" | Already implemented. Homepage emits `Organization`, `SoftwareApplication`, `Offer`, `PriceSpecification`, `ContactPoint`, `PostalAddress`, `ImageObject`, `Person`, `PropertyValue`. Blog posts emit `BlogPosting` and `WebPage`. |
| "Missing hreflang across all pages" | `hreflang` de/en is present on the bilingual page pairs. It is genuinely missing on the top landing page and on blog posts, see 2.4. |
| "No case study pages, only one references page" | Case studies exist (`/case_study_brera`, 800 percent ROI; Case Study OUNDA, 521 percent ROI), plus industry pages and per-integration pages. |
| "Roughly 15 to 20 `/en/` pages plus 10 blog posts indexed" | 180 URLs in the sitemap, 243 content objects in the portal, 52 blog posts. |
| Keyword table with no AI or KI entry | The site has repositioned around AI. Homepage title is `Hivebuy.com - Die KI-Einkaufssoftware für Ihr Unternehmen`, and the single largest marketing page is `/ki-beschaffungsplattform`. |

---

## Executive summary

Technical SEO fundamentals are in better shape than v1 suggested: canonicalisation,
domain handling, robots, sitemap hygiene, and structured data are largely correct.

The real problems are elsewhere, and they are commercial rather than architectural:

1. **Roughly 15,200 pageviews over six months land on 404s** because four legacy
   pages were unpublished without redirects. One of them, `/old`, drew 9.3 times
   the traffic of the actual homepage and produced a paying customer.
2. **Traffic and conversion are inversely correlated.** The two biggest marketing
   pages convert at 0.06 and 0.29 percent. Webinar pages convert at 17 to 34 percent.
3. **The blog is a sunk investment.** 52 posts with a solid topical cluster, and not
   one of them appears in the top 100 pages by views.
4. **A handful of concrete, cheap defects** on high-intent pages: a missing canonical
   and a placeholder title on the blog hub, a 20 character meta description on the
   English homepage, and money pages titled `Preise` and `Prices`.

**Overall SEO health: moderate.** Foundations are sound. Value is leaking through
redirects, conversion design, and content ROI, not through crawlability.

---

## 1. Performance baseline (2026-02-19 to 2026-08-19)

| Metric | Value |
|---|---|
| Raw views | 462,804 |
| Form submissions | 598 |
| Contacts | 363 |
| Leads | 83 |
| Customers | 123 |
| Bounce rate | 77.6 percent |
| Avg. time per pageview | 358 s |

Note on scope: these totals mix `www.hivebuy.com` marketing pages with the
`hivebuy.de` application and tenant subdomains, which dominate raw views. The
application is not a marketing surface, so marketing conclusions below are drawn
from `www.hivebuy.com` rows only.

---

## 2. Technical SEO

### 2.1 What is already correct

| Item | Status |
|---|---|
| Domain canonicalisation | All host and scheme variants resolve to `https://www.hivebuy.com/` |
| robots.txt | Minimal and correct. Blocks only previews, preference centres, two tag pages, and cache-buster parameters. Declares the sitemap. |
| Sitemap hygiene | 180 URLs, no draft, test, temporary, or lorem ipsum URLs leaked into it |
| Canonical tags | Present and self-referencing on every live page tested, with two exceptions noted below |
| Structured data | Rich and correctly typed, including `SoftwareApplication` with `Offer` and `PriceSpecification` |
| H1 | Exactly one on every page tested except `/workflows-einkauf` |

### 2.2 Critical: legacy pages 404 instead of redirecting

Four pages that carried real traffic and real conversions were unpublished. They now
return HTTP 404 and canonicalise to `/404`. No 301 redirect was put in place.

| URL | Views (6 mo) | Submissions | Contacts | Customers | Current status |
|---|---|---|---|---|---|
| `/old` | 12,820 | 6 | 6 | 1 | 404 |
| `/homepage-old` | 1,486 | 0 | 2 | 1 | 404 |
| `/en/old` | 713 | 0 | 1 | 0 | 404 |
| `/loesungen-old` | 157 | 0 | 0 | 0 | 404 |
| **Total** | **15,176** | **6** | **9** | **2** | |

For comparison, the live homepage `https://www.hivebuy.com` recorded 1,376 views in
the same window. `/old` therefore attracted 9.3 times the traffic of the page that
replaced it, and it converted a customer while doing so.

A fifth dead page, `/en/lösungen-old`, exists with no traffic in the top 100 and
should be redirected in the same pass.

**Action:** 301 `/old` and `/homepage-old` to `/`, `/en/old` to `/en/`,
`/loesungen-old` to `/lösungen`, and `/en/lösungen-old` to `/en/lösungen`. Note the
live solutions pages carry umlauts, and the ASCII form `/loesungen` returns 404, so
the redirect target must be the umlaut URL. Do this before anything else in this report.

### 2.3 Language architecture

The site is genuinely bilingual: German at root, English under `/en/`.

| Prefix | Page count |
|---|---|
| root, no prefix (German) | 105 |
| `/en/` (English) | 70 |

v1's slug criticism was aimed at URLs that do not exist, but a real version of the
problem is present: several `/en/` pages reuse German slugs, so the English tree is
not consistently English.

```
/en/workflows-einkauf                        German slug, English page
/en/industrien/logistik                      German slug, English page
/en/industrien/gesundheitswesen              German slug, English page
/en/industrien/kmu-dezentrale-organisationen German slug, English page
/en/industrien/dienstleistungen              German slug, English page
/en/lösungen                                 German slug plus umlaut
/en/ki-agenten-backoffice                    German slug
/en/testzugang                               German slug
/en/ersparnisrechner_hivebuy                 German slug plus underscore
```

Meanwhile `/en/pricing`, `/en/helpcenter`, and `/en/management` do use English slugs,
so the tree is internally inconsistent rather than uniformly wrong.

### 2.4 hreflang defects

`hreflang` is implemented, but not uniformly.

| Page group | hreflang | Issue |
|---|---|---|
| Main site pages | `de`, `en` | Correct |
| Blog hub `/blog` | `de-de`, `en` | Value inconsistent with the rest of the site (`de-de` vs `de`) |
| Blog posts | none | Missing entirely |
| `/ki-beschaffungsplattform` | none | Missing on the highest-traffic marketing page |
| `/lp_kostenlose_demo_0825` | none | Missing |

The English blog is also a shell: `/en/blog` returns 200, but
`/en/blog/ki-im-einkauf` and `/en/blog/beschaffungsprozess-optimieren` both return
404. So `/blog` advertises an English alternate that has no English articles behind it.

**Global validation of the hreflang graph.** A second full crawl checked every
language link across all 180 sitemap URLs. Where hreflang exists it is genuinely
correct, which is rare on bilingual sites:

| Check | Result |
|---|---|
| Language pairs | 59 |
| Self-reference present | 118 of 118, 100 % correct |
| Reciprocity, A points to B and back | 0 errors |
| hreflang targets resolve and sit in the sitemap | 0 errors |
| `x-default` set | **0 of 180 pages** |
| `html lang` consistent | **three different values in use** |
| English slugs actually translated | **18 of 59** |

Structure: 121 German pages, 59 English pages, 59 pairs, 62 German pages with no
English counterpart, zero English pages without a German one. The 62 unpaired German
pages correctly omit hreflang because no English version exists. What matters is which
pages they are: 45 blog posts, 9 webinars, the whitepaper and webinar hubs, the help
centre. The product layer is bilingual, the demand-generation layer is not.

Three further defects beyond the `de-de` and blog-post gaps in the table above:

1. **`/en/helpcenter` is paired with `/hilfecenter-videos`, not `/hilfecenter`.** The
   German help centre hub sits outside the language structure entirely, and both German
   pages share the title `Hivebuy Hilfecenter`.
2. **`html lang` contradicts hreflang.** 45 German pages declare `lang="de-de"` while
   their hreflang says `de`. Three listing pages are outright wrong: `/webinare` and
   `/whitepaper-blog` declare `lang="en"` on German pages, `/en/blog` declares `de-de`.
3. **`x-default` is absent everywhere**, so Google chooses the fallback for unmatched
   locales itself.

Full analysis and the global instruction are in `language-variants-anweisung.md`.

### 2.4b Landing pages: excluded from the sitemap but left indexable

No HubSpot landing page appears in `sitemap.xml`. That includes every `/lp_*` campaign
page and `/ki-beschaffungsplattform`.

The exclusion itself is correct: these are paid-ads landing pages and do not belong in
a sitemap. The defect is the inconsistency around it. **All of them are fully
indexable**, with no `noindex` and a self-referencing canonical. A sitemap is a
suggestion, not an exclusion, so Google indexes them anyway.

Confirmed: a `site:` query returns `https://www.hivebuy.com/lp_kostenlose_demo_0825`
with the title `Hivebuy eProcurement System - Kostenlose Demo Vereinbaren`.

Consequence: four demo landing pages sharing an identical title compete with each other
in the index and with `/produktdemo` and `/kontakt` for the same demo intent. `/kontakt`
converts at 7.1 percent, `/lp_kostenlose_demo_0825` at 0.29 percent. Every time Google
serves the landing page instead of `/kontakt`, that gap is the cost.

**Action:** set `noindex, follow` on all `/lp_*` pages. Keep `follow` so the internal
links to product pages still pass equity, `/lp_video_integrationen` alone carries six
of them. Do not add them to the sitemap.

This also dissolves the landing page consolidation item in section 5.2: separate
campaign variants are legitimate for ads, they were only a problem because they were
competing in the organic index.

**`/ki-beschaffungsplattform`: decided 2026-08-20.** Confirmed by the site owner as a
landing page, so it goes to `noindex` with the rest. It sits outside `/lp_`, draws
26,715 views and links three times into the product pages, which is why it looked
ambiguous from the data alone.

That settles the SEO question and opens a paid-media one: 26,715 paid clicks producing
16 form submissions is a 0.06 percent conversion rate. That belongs to the ads budget
rather than this report, but the number is large enough that it should not be lost.

Its 236 character meta description should still be trimmed. A `noindex` page can still
be shown in ad previews and shared links.

### 2.5 Canonical and sitemap disagree on umlaut encoding

The sitemap is correct here: it percent-encodes all seven affected URLs, for example
`https://www.hivebuy.com/l%C3%B6sungen`. The canonical tag on the page does not.
`/en/lösungen` emits `<link rel="canonical" href="https://www.hivebuy.com/en/lösungen">`
with a raw umlaut.

So the sitemap and the canonical tag point at two different string representations of
the same page. Affected slugs:

```
/lösungen                                                    /en/lösungen
/blog/strategischer-einkäufer-aufgaben-kompetenzen
/blog/effizientes-vertragsmanagement-optimieren-sie-ihre-geschäftsprozesse
/blog/lieferantenmanagement-definition-ziele-prozesse-und-software-der-komplette-überblick
/blog/maverick-buying-ursachen-risiken-und-lösungsansätze-im-einkauf
/blog/automatisierter-preisvergleich-im-indirekten-einkauf-hiveiq-ist-jetzt-für-alle-hivebuy-kunden-live
```

Note also that the ASCII spelling `/loesungen` returns 404, so the solutions page is
reachable only via the umlaut URL. Any internal link or external citation using the
ASCII form is a dead link.

This is a low-severity consistency issue, not a crawl blocker. The durable fix is to
migrate these slugs to ASCII and 301 the umlaut forms.

### 2.6 Second domain and application surfaces

`hivebuy.de` is a separate indexed domain. Google returns both
`https://app.hivebuy.de/` (title `Hivebuy eProcurement - www.hivebuy.com`) and
`https://hivebuy.de/de/datenschutz/`, so the application login and a legacy legal
page are in the index and split brand signals away from `www.hivebuy.com`.

Customer-named tenant subdomains carry substantial tracked traffic:

| Subdomain | Views (6 mo) |
|---|---|
| `app.hivebuy.de` (all paths) | ~200,000 |
| `mediamarktsaturn.hivebuy.de` | 23,153 |
| `igus.hivebuy.de` | 3,152 |
| `vflbochum.hivebuy.de` | 1,423 |
| `secde.hivebuy.de` | 882 |
| `hydrogenious.hivebuy.de` | 600 |
| `heo.hivebuy.de` | 187 |
| `frontend.staging.hivebuy.de` | 1,118 |

Two things follow. First, a **staging environment** is receiving real traffic and is
being tracked in production analytics. Second, tenant subdomains embed customer names
in hostnames. Neither should be indexable.

**Could not verify:** these hosts were unreachable from the analysis environment
(the outbound proxy refused the CONNECT tunnel), so their `robots.txt` and
`noindex` status is unconfirmed. Treat this as a to-check item, not a proven defect,
with the exception of `app.hivebuy.de`, which Google demonstrably has indexed.

Application error pages are also accumulating traffic worth investigating on their
own merits: `/not-allowed` 1,931 views, `/not-found` 1,807, `/something-went-wrong` 353.

---

## 3. On-page SEO

### 3.1 Title defects on high-intent pages

| Page | Current title | Length | Issue |
|---|---|---|---|
| `/preise-hivebuy` | `Preise` | 6 | Bare label on the highest commercial-intent page |
| `/en/pricing` | `Prices` | 6 | Same |
| `/blog` | `blog` | 4 | Lowercase placeholder |
| `/kontakt` | `Kontaktieren Sie Hivebuy` | 24 | Acceptable |
| Homepage | `Hivebuy.com - Die KI-Einkaufssoftware für Ihr Unternehmen` | 56 | Good, keyword-led. `.com` in the title is still unusual. |

28 of 172 titled site pages exceed 60 characters, the longest at 100
(`/webinar-tennispoint`). Those will truncate in results.

Suggested rewrites for the two money pages:

```
/preise-hivebuy  ->  Preise & Pakete | Einkaufssoftware ab … | Hivebuy
/en/pricing      ->  Pricing & Plans | Procurement Software | Hivebuy
```

### 3.2 Missing canonical on four listing pages

A full crawl of all 180 sitemap URLs found exactly four pages with **no canonical tag
at all**, and they are all listing pages:

```
/blog            /en/blog            /webinare            /whitepaper-blog
```

Blog posts themselves do emit a canonical, and the rest of the standard head is
present on the listing pages (`og:url`, `og:title`, `twitter:*`, JSON-LD, and
`rel="next"` on `/blog`). So the canonical specifically is being suppressed or omitted
in the listing template, not the whole head.

`/blog` is paginated, which is where a missing canonical does the most damage: every
pagination state becomes a near-duplicate of the same page.

### 3.3 Meta descriptions: 83 pages, now fixed

**Status 2026-08-20: done.** 83 pages were rewritten through the CMS API and verified
live. 176 of 180 sitemap pages now sit in the 70 to 165 character range, up from 91.
Zero remain over length. See `ergebnis-2026-08-20.md`.

**Correction to the figures first published here.** My crawl regex was
`content=["\']([^"\']*)`, which stops at the first quote character, including an
apostrophe inside a double-quoted attribute. Any meta containing an apostrophe was
truncated and scored as too short. Real distribution was 80 too long, 1 too short, 2
absent, so 83 rather than 88. Three pages I had missed were genuinely over length:
`/en/about-us` at 227, `/en/` at 201, `/en/analytics-reportings` at 182.

The corrected pattern uses a backreference: `content=(["\'])(.*?)\1`.

The numbers below are the corrected pre-fix state.

| Verdict | Pages | Share |
|---|---|---|
| Within 70 to 165 characters | 92 | 51 % |
| **Over 165 characters** | **75** | **42 %** |
| Under 70 characters | 11 | 6 % |
| Absent entirely | 2 | 1 % |

The over-length group is not a formatting quirk. The worst cases run to 480, 477, and
468 characters, all on blog posts. At that length the text is almost certainly being
auto-generated from the article body because no meta description field is filled in.
HubSpot falls back to page content when the field is empty, and that fallback is what
Google sees.

Worst offenders:

| Page | Length |
|---|---|
| `/blog/einkaufssoftware-4-bereiche-fuer-optimierung` | 480 |
| `/blog/einkaufssoftware-vorteile-unternehmen` | 477 |
| `/blog/hivebuy-im-procurement-summit-magazin` | 468 |
| `/blog/3-herausforderungen-bei-der-einfuehrung-von-einkaufssoftware` | 440 |
| `/blog/wie-waehle-ich-die-richtige-einkaufssoftware-5-wichtige-kriterien-zur-auswahl` | 407 |
| `/webinar-tennispoint` | 352 |
| `/kundenbericht-thermondo` | 336 |

Absent entirely: `/en/career` and `/deine-karriere-bei-hivebuy`.

Shortest: `/webinare` at 8 characters, `/whitepaper-blog` at 10, `/en/testzugang` at 11,
`/en/helpcenter` and `/en/resources` at 16, `/hilfecenter` at 19, and the English
homepage `/en/` at 20.

Written replacements for all 88 pages, each between 110 and 160 characters, are in
`meta-descriptions-vorschlaege.md` and `meta-descriptions-vorschlaege.csv`.

**Note on method:** HubSpot exposes no readable meta description property on
`SITE_PAGE` or `LANDING_PAGE` objects, so these lengths come from the rendered HTML of
all 180 sitemap URLs. Content objects outside the sitemap were not measured.

### 3.4 Double-escaped ampersand on three English pages

Three pages have the literal string `&amp;` stored in their HubSpot HTML title
field. That value is then escaped again on output to `&amp;amp;`, so the page title
visibly displays `&amp;` instead of an ampersand.

| Page | Stored title field | Rendered source |
|---|---|---|
| `/en/management` | `Cost control &amp; scaling in management \| Hivebuy` | `&amp;amp;` |
| `/en/industrien/dienstleistungen` | `… Manage Purchasing &amp; Costs \| Hivebuy` | `&amp;amp;` |
| `/en/case_study_tennis-point` | `Tennis-Point Case Study: Procure-to-Pay with Hivebuy &amp; SAP` | `&amp;amp;` |

This is a data-entry problem on three specific pages, not a template defect. Titles
that store a plain `&` render correctly: `/industrien/dienstleistungen` and
`/blog/ki-im-einkauf` both emit a single `&amp;` in the HTML source, which is the
correct escaping and displays as `&`. Only the German-to-English page duplication
path introduced the entity.

**Fix:** edit the three title fields and replace `&amp;` with `&`. No template change.

### 3.5 Heading structure: 56 pages, but only four templates

The full crawl shows only 124 of 180 pages emit exactly one H1. The first pass caught
just `/workflows-einkauf` because the sample was too small.

| H1 count | Pages | Pattern |
|---|---|---|
| 0 | 25 | Case studies, savings calculator, `/lösungen`, `/kundenreferenzen`, help centre |
| 1 | 124 | Correct |
| 2 | 24 | Every integration page (DE and EN), blog listings, `/finanzabteilung` |
| 3 | 1 | `/anbindungsanleitung-sap-business-one` |
| 4 | 6 | Every `ki-agenten` page (DE and EN) |

The grouping is the good news: these are not 56 independent mistakes but roughly four
templates. Fix the integration template, the case study template, the `ki-agenten`
template, and the listing template, and 56 pages resolve at once.

Highest priority within that set: the 25 pages with **no H1 at all**, which includes
`/lösungen` and `/kundenreferenzen`, both commercially important, and the six
`ki-agenten` pages with four H1 each, which sit on the strategically central AI line.

### 3.6 Inconsistent title decoration

Blog titles mix decorative glyphs without a rule: `✅ KPIs im Einkauf`,
`RFQ-Prozess im Einkauf ✅`, `✓ Purchase-to-Pay einfach erklärt`,
`Indirekter Einkauf ➤ Definition`, `Was ist Beschaffung? ➤ Strategie`. Pick one
convention or drop them; leading glyphs in particular push the keyword rightwards.

---

## 4. Conversion analysis

This is the most actionable finding in the report, and v1 could not see it at all.

| Page | Views | Submissions | Rate | Bounce |
|---|---|---|---|---|
| `/webinar-ki-einkaufsassistent` | 215 | 72 | **33.5 %** | 47.7 % |
| `/webinar-ask-hivebuy` | 544 | 92 | **16.9 %** | 67.7 % |
| `/kontakt` | 1,871 | 132 | **7.1 %** | 74.6 % |
| `/whitepaper_ki_prompts` | 168 | 7 | 4.2 % | 89.8 % |
| `/partnerprogramm` | 160 | 5 | 3.1 % | 93.2 % |
| `/produktdemo` | 859 | 8 | 0.9 % | 77.5 % |
| `/lp_kostenlose_demo_0825` | 14,597 | 43 | **0.29 %** | 89.8 % |
| `/ki-beschaffungsplattform` | 26,715 | 16 | **0.06 %** | 87.9 % |

`/webinar-ki-einkaufsassistent` converts roughly **560 times better per view** than
`/ki-beschaffungsplattform`, and has by far the lowest bounce rate on the site.

Read together: the two pages absorbing 41,312 views produce 59 submissions, while
three webinar and contact pages absorbing 2,630 views produce 296. The traffic is
arriving; the conversion path on the large pages is not working.

**Actions:**
1. Treat `/ki-beschaffungsplattform` as a conversion problem, not a traffic problem.
   88 percent bounce at 190 s time-on-page suggests people read and leave, so the page
   informs but never asks. Add the webinar or demo offer that demonstrably converts.
2. Consolidate the six competing demo landing pages (see 5.2).
3. Make the webinar format a repeatable programme rather than one-off events. It is
   the single best-performing asset class on the site.

---

## 5. Content inventory

### 5.1 The blog does not earn its keep

52 posts exist, with a genuinely coherent topical cluster around procurement
terminology: `bedarfsanforderung-banf`, `rfq-bedeutung`, `purchase-order`,
`purchase-to-pay`, `eprocurement`, `kennzahlen-im-einkauf`, `beschaffungsstrategien`,
`lieferantenklassifizierung`, `lieferantenmanagement`, `indirekter-einkauf`,
`ki-im-einkauf`, `lieferkettengesetz-deutschland`, plus a seven part
`ProcurementHeroes` podcast series. Publishing is current through July 2026.

And yet: **not a single blog post appears in the top 100 pages by views.** The `/blog`
hub itself drew 170 views. The author page `/blog/author/bettina-fischer` drew 185,
which means an author archive outperforms the hub it belongs to.

This is a content ROI problem, not a content quality problem. The likely causes are
the defects in 2.4 and 3.2: no canonical on the hub, no hreflang on posts, an English
blog that 404s at article level, and no internal linking from the money pages into the
cluster.

**Actions:** fix the blog hub canonical and title, add hreflang to posts, either build
or remove the English blog, and link the cluster from `/produkt`, `/loesungen`, and
`/preise-hivebuy`.

### 5.2 Six demo landing pages, competing only because they are indexable

| Slug | Title |
|---|---|
| `lp_kostenlose_demo` | `Hivebuy Kostenlose Demo buchen` |
| `lp_kostenlose_demo_v2` | `Hivebuy Kostenlose Demo buchen` |
| `lp_kostenlose_demo_v3` | `Hivebuy eProcurement System - Kostenlose Demo Vereinbaren` |
| `lp_kostenlose_demo_v3-0` | `Hivebuy eProcurement System - Kostenlose Demo Vereinbaren` |
| `lp_kostenlose_demo_0825` | `Hivebuy eProcurement System - Kostenlose Demo Vereinbaren` |
| `lp_beschaffung` | `Hivebuy eProcurement System - Kostenlose Demo Vereinbaren` |

Four share an identical title. **Correction to an earlier draft of this report:** these
are paid-ads landing pages, and separate variants per campaign are entirely legitimate.
They do not need consolidating.

The problem is only that they are indexable, so they compete in organic results with
each other and with `/produktdemo` and `/kontakt`. Fix the indexability per section
2.4b and the duplication stops mattering.

### 5.3 Portal hygiene

The portal holds draft and test objects. **All of these return 404, so they are not an
active SEO problem**, and none of them leaked into the sitemap. They are a governance
issue worth a cleanup pass:

- 5 pages with `-temporary-slug-<uuid>` slugs, 3 with no title at all
- 6 test pages (`/testing`, `/testing-1`, `/testing-2`, `/testing-4`,
  `/test-step-formtest-step-form`, `/contact-testing-german`, `/en/contact-testing`)
- 6 blog posts still titled `Lorem ipsum dolor sit amet, consetetur sadipscing elitr…`
  under `/whitepaper-blog/` and `/webinare/`
- 1 landing page titled `Untitled` at `/untitled`
- 1 page whose slug and title both carry a file extension: `/ai-procurement-software.html`
- 4 pages titled `AVV` and 3 titled `testing`

### 5.4 Content that exists and v1 missed

For the record, since v1 recommended building these: industry pages
(`/industrien/logistik`, `/gesundheitswesen`, `/kmu-dezentrale-organisationen`,
`/dienstleistungen`, each in DE and EN), case studies (`/case_study_brera` at 800
percent ROI, Case Study OUNDA at 521 percent ROI), per-integration pages (SAP ECC,
SAP Business One, DATEV, Microsoft Dynamics, d.Velop), and an AI product line
(`/ki-beschaffungsplattform`, `/ki-agenten-bedarfsanforderung`, `/ki-agenten-finance`,
`/ki-agenten-backoffice`, `/savings-agent`, `/whitepaper_ki_prompts`).

---

## 6. Keyword and positioning

The site has repositioned from procurement software to **AI procurement software**.
The title history is visible in the portal: `/homepage-old` still reads
`Hivebuy.com - Einkaufssoftware für Ihr Unternehmen`, while the live homepage reads
`Hivebuy.com - Die KI-Einkaufssoftware für Ihr Unternehmen`.

| Theme | Coverage | Traffic outcome |
|---|---|---|
| KI / AI procurement | Strong: dedicated LP, 4 agent pages, whitepaper, blog post | `/ki-beschaffungsplattform` is the #1 marketing page at 26,715 views |
| Einkaufssoftware | Strong: homepage, blog cluster | Homepage only 1,376 views |
| Procure-to-Pay, eProcurement | Blog cluster, LP titles | No page in top 100 |
| Industry verticals | 4 verticals, DE and EN | 0 in top 100 |
| Vertragsmanagement, Rechnungsmanagement | Dedicated pages | 177 and 140 views |
| Preise / Pricing | Dedicated pages | 1,898 views, only 2 submissions |

The AI bet is working on acquisition and failing on conversion. Vertical and feature
pages are effectively invisible.

---

## 7. Off-page signals

Unchanged from v1 and still qualitative: no Ahrefs, Semrush, or Search Console access
was available, so no backlink or ranking figures are asserted here.

| Platform | Status |
|---|---|
| Capterra | Active listing, positive sentiment, ease of use cited |
| OMR Reviews | Listed, not enough reviews for an aggregate rating |
| G2 | No confirmed listing |
| LinkedIn | Active, roughly 2,200 followers |
| German trade press | Mentioned by wirtschaftsforum.de, it-daily.net, d-velop.de |
| Startup databases | Tracxn, CB Insights |

Recurring user complaints from review platforms that also carry SEO weight: no mobile
app, and missing integrations (Sevdesk, Google Chat).

Opportunities, in priority order: claim and populate G2 to make `AggregateRating`
markup legitimate; pitch the ProcurementHeroes podcast to German procurement press;
co-market with named integration partners; pursue inclusion in
`beste Einkaufssoftware` roundups.

---

## 8. Prioritised action plan

### Critical, do this week

1. ~~**301 the five dead legacy pages.**~~ **DONE, verified 2026-08-20.** All six
   redirects resolve correctly: `/old` and `/homepage-old` to `/`, `/en/old` to
   `/en/`, `/loesungen-old` and `/en/lösungen-old` to the umlaut solutions pages, plus
   the ASCII fallback `/loesungen` to `/lösungen`. Recovers roughly 15,200 views per
   six months that were hitting 404s.
2. **Add a canonical tag to the blog listing template.** Affects four pages: `/blog`,
   `/en/blog`, `/webinare`, `/whitepaper-blog`. Replace the placeholder titles
   (`blog`, `Webinare`, `Whitepaper`) at the same time. See `blog-fix-anleitung.md`.
3. **Fix the 88 meta descriptions.** 75 over length, 11 too short, 2 absent. Written
   replacements for every one are in `meta-descriptions-vorschlaege.csv`. Start with
   `/en/` (20 characters), `/ki-beschaffungsplattform` (236), and the five blog posts
   over 400.
4. **Replace `&amp;` with `&`** in the title field of `/en/management`,
   `/en/industrien/dienstleistungen`, and `/en/case_study_tennis-point`.

### High, next 30 days

5. **Rewrite `/preise-hivebuy` and `/en/pricing` titles.** Highest intent, zero keyword.
6. **Fix the H1 templates.** 56 pages are wrong, but they trace to roughly four
   templates: integrations (2 H1), case studies and `/lösungen` (0 H1), `ki-agenten`
   (4 H1), and the listing template. Start with the 25 pages that have no H1 at all,
   including `/lösungen` and `/kundenreferenzen`.
7. **Rebuild `/ki-beschaffungsplattform` for conversion.** Add the webinar or demo
   offer. A 0.06 percent rate on 26,715 views is the largest single opportunity here.
8. **Set `noindex, follow` on all `/lp_*` landing pages.** They are ads pages and
   correctly absent from the sitemap, but they are indexable, and
   `/lp_kostenlose_demo_0825` is confirmed in Google's index competing with `/kontakt`
   for demo intent. Keep `follow` to preserve the internal links. No consolidation
   needed once they are out of the index.
9. **Fix the language variant layer.** Unify `html lang` on `de` and `en` (45 pages
   currently say `de-de`), repair the three listing pages whose `lang` contradicts
   their tree, repair the `/en/helpcenter` to `/hilfecenter` pairing, and add
   `x-default` pointing at the English version. Do not touch the 59 pairs themselves,
   they are correct. See `language-variants-anweisung.md`.
10. **Decide the English blog.** Either publish English articles under `/en/blog/` or
    remove the `hreflang="en"` pointer from `/blog`.

### Medium, next 90 days

11. **Verify `noindex` on `app.hivebuy.de`, the tenant subdomains, and staging.**
    `app.hivebuy.de` is confirmed indexed and should not be.
12. **Take `frontend.staging.hivebuy.de` out of production analytics** and restrict access.
13. **Align canonical tags with the sitemap's percent-encoding**, or migrate the seven
    umlaut slugs to ASCII with 301s. Also make `/loesungen` resolve instead of 404.
14. **Make `/en/` slugs consistently English**, with 301s from the German-slugged
    `/en/` URLs.
15. **Internally link the blog cluster** from `/produkt`, `/loesungen`, `/preise-hivebuy`.
16. **Fix the remaining H1 outliers** after the template work in item 6:
    `/anbindungsanleitung-sap-business-one` (3 H1) and `/finanzabteilung` (2 H1).
17. **Shorten the 28 titles over 60 characters.**
18. **Clean up portal junk**: temporary slugs, test pages, lorem ipsum posts, `/untitled`.
19. **Investigate the app error pages** drawing 4,091 combined views
    (`/not-allowed`, `/not-found`, `/something-went-wrong`).
20. **Productise the webinar programme.** Best converting asset class on the site by
    two orders of magnitude.

---

## 9. Metrics to track

| Metric | Source | Frequency |
|---|---|---|
| 404 hits and redirect coverage | Search Console, server logs | Weekly until item 1 is closed |
| Submission rate on `/ki-beschaffungsplattform` | HubSpot content analytics | Weekly |
| Views and submissions per webinar page | HubSpot | Per campaign |
| Blog cluster views | HubSpot, Search Console | Monthly |
| Indexed URL count for `hivebuy.de` subdomains | `site:` queries, Search Console | Monthly |
| Organic sessions and CTR by page | Search Console | Monthly |
| Title and meta length compliance | Crawler (Screaming Frog, Sitebulb) | Quarterly |

---

## 10. Limitations

State these plainly rather than papering over them:

1. **No traffic-source split.** The HubSpot content analytics pull did not break views
   down by organic, direct, or paid. All view counts in this report are all-sources.
   No claim is made about organic share.
2. **Meta descriptions sampled, not crawled.** HubSpot exposes no readable meta
   description property on page objects, so lengths come from a 25 page live sample of
   243 content objects.
3. **`hivebuy.de` hosts unreachable** from the analysis environment, so their
   `robots.txt` and `noindex` status is unverified except where Google's index proves
   otherwise.
4. **No backlink or rank-tracking data.** Section 7 stays qualitative.
5. **Core Web Vitals not measured.** Requires PageSpeed Insights or CrUX access, which
   was not available here. Still worth running.

---

## Appendix: verification

```bash
# robots.txt and sitemap (site requires a browser user agent, plain fetchers get 403)
curl -sS -A "Mozilla/5.0 ..." https://www.hivebuy.com/robots.txt
curl -sS -A "Mozilla/5.0 ..." https://www.hivebuy.com/sitemap.xml

# confirm the 404s and the missing canonical
curl -sSI -A "Mozilla/5.0 ..." https://www.hivebuy.com/old            # expect 404
curl -sS  -A "Mozilla/5.0 ..." https://www.hivebuy.com/blog | grep canonical   # expect no match

# domain canonicalisation
curl -sS -o /dev/null -w '%{http_code} %{url_effective}\n' -L https://hivebuy.com/
```

HubSpot side: `get_content_analytics_report` in TOTALS mode over
2026-02-19 to 2026-08-19, and `search_crm_objects` against `SITE_PAGE`,
`LANDING_PAGE`, and `BLOG_POST` with `hs_url`, `hs_html_title`, `hs_slug`.
