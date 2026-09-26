---
type: concept
tags: [deploy, domain, seo, lovable, legal, launch]
sources: ["https://docs.lovable.dev/features/publish", "https://docs.lovable.dev/features/custom-domain", "https://docs.lovable.dev/tips-tricks/launch-on-a-custom-domain", "https://docs.lovable.dev/introduction/subscription-plans", "https://docs.lovable.dev/features/projects/settings", "https://docs.lovable.dev/features/analytics", "https://docs.lovable.dev/features/privacy-and-security-settings", "https://docs.lovable.dev/tips-tricks/seo-geo", "https://docs.lovable.dev/features/seo-aeo", "https://docs.lovable.dev/features/upgrade-to-tanstack-start", "https://docs.lovable.dev/changelog", "https://lovable.dev/blog/building-apps-using-tanstack-start", "https://tanstack.com/start/latest/docs/framework/react/guide/seo", "https://tanstack.com/start/latest/docs/framework/react/guide/server-routes", "https://tanstack.com/router/latest/docs/framework/react/guide/document-head-management", "https://tanstack.com/router/latest/docs/framework/react/guide/path-params", "https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics", "https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites", "https://developers.google.com/search/docs/specialty/international/localized-versions", "https://developers.google.com/search/docs/specialty/international/locale-adaptive-pages", "https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap", "https://developers.google.com/search/docs/crawling-indexing/block-indexing", "https://developers.google.com/search/docs/appearance/structured-data/event", "https://developers.google.com/search/docs/appearance/structured-data/local-business", "https://developers.google.com/search/docs/appearance/structured-data/article", "https://support.google.com/webmasters/answer/9008080", "https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/", "https://supabase.com/docs/guides/auth/redirect-urls", "https://github.com/supabase/supabase/issues/42033", "https://www.gesetze-im-internet.de/ddg/__5.html", "https://www.gesetze-im-internet.de/ttdsg/__25.html", "https://www.lfk.de/fileadmin/PDFs/Dokumente_und_Rechtsgrundlagen/Leitfaeden/leitfaden-impressumspflicht-2024.pdf", "https://www.ra-plutte.de/lg-muenchen-dynamische-einbindung-google-web-fonts-ist-dsgvo/", "https://eur-lex.europa.eu/eli/reg/2016/679/oj", "https://www.strato.de/domains/domain-kosten/", "https://www.inwx.de/de/domain/pricelist", "https://cdn.jsdelivr.net/npm/@fontsource-variable/fraunces/", services/voice-relay/server.js, n8n/workflows/04-task-intake.json, docs/deploy-relay.md, "Lovable repo clone hallotermin-paper (read-only: package.json, vite.config.ts, src/routes/__root.tsx, public/robots.txt, .lovable/project.json)"]
---
# Deploy, Domain and SEO

**Definition:** how "Dresden mit Kind" gets its final public URL on Sunday, what that URL means for the rest of our system (relay, n8n, Supabase), how search engines and link previews see the app, and the legal minimum for a public German website. Researched 26 Sep 2026. Lovable changes fast, so every Lovable fact below has a dated source.

**Why it matters for us:** the only success rule is a working build under its own URL by Sun 27.09, 14:00 ([[Deadline - live by Sunday 14h]]). The URL goes on the pitch slide and into WhatsApp messages to the jury. It has to be stable, show the right name in link previews, and must not break the intake or the call flow.

**Related:** [[Frontend and UX Plan v3 (merged)]] (routes in B, prompts in G) · [[Monday-Morning Plan]] · [[Lovable - Practical Guide]] · [[Relay Hosting Options]] · [[Pitch Kit v2 (merged)]] · [[Idea B - Dies-Das-Ana-Nas]] (Q1: final name and domain) · [[No secrets in repo]] · [[DEF-047 Role-play calls mark real providers as checked by phone]]

> Legal points are general information, not legal advice.

---

## 0. Important: our Lovable app is TanStack Start with server-side rendering

The read-only clone of the Lovable repo (`hallotermin-paper`) shows: `package.json` name `tanstack_start_ts`, `@tanstack/react-start` 1.168, React 19.2, Vite 8, file routes in `src/routes/` with `head()` in `__root.tsx`, `.lovable/project.json` template `tanstack_start_ts_current`. `vite.config.ts` says the Lovable config builds with "nitro (build-only using cloudflare as a default target)".

This matches Lovable's docs: projects created from **13 May 2026** use TanStack Start with SSR, and "every publish builds a server-rendered app, pre-generates the routes that can be served statically, and deploys it all as an edge Worker" ([Lovable blog, 1 Jun 2026](https://lovable.dev/blog/building-apps-using-tanstack-start), [SEO docs](https://docs.lovable.dev/tips-tricks/seo-geo)). A `*.lovable.app` host answered with `Server: cloudflare` on 26 Sep.

What this changes compared with a plain Vite SPA:

| Topic | Old React + Vite SPA | Our TanStack Start app |
|---|---|---|
| What crawlers and link-preview bots get | Empty shell; Lovable pre-renders only for verified crawlers | Full HTML for everyone, every request |
| Titles, descriptions, Open Graph | react-helmet or `document.title` | Each route's `head()`; nested routes override the parent ("last wins") |
| Page data in the HTML | Only after JavaScript runs | Only if the route **loader** fetches it (data fetched inside a component arrives later) |
| `sitemap.xml`, `robots.txt` | Static files in `public/` | Static files in `public/` **or** server routes (`src/routes/sitemap[.]xml.ts`) |
| 404 | Always HTTP 200 (soft 404) | Server can answer a real 404 (check after publishing) |
| UI language | Client only | The server does not know `localStorage`, so it renders English first (see 2.5) |

Plan v3 was written for the SPA model (`index.html`, `document.title`). Lovable adapts that, but the SEO prompt P14 below is written for TanStack Start.

---

## 1. Deploy and domain

### 1.1 How publishing works today

| Question | Answer (source: [Publish docs](https://docs.lovable.dev/features/publish), [Project settings](https://docs.lovable.dev/features/projects/settings)) |
|---|---|
| Where | **Publish** button, top right of the editor, next to Share |
| URL | `<subdomain>.lovable.app`. Our project shows "URL subdomain: No URL subdomain", so it has never been published |
| Choose or rename the subdomain | First publish: type it in the **Website URL** field. Later: **Project settings → URL subdomain → Update URL subdomain**. Renaming the project does **not** change the URL. The docs don't say whether the old subdomain redirects, so pick the name before sharing the URL |
| Changes after publishing | Publishing deploys a **snapshot**. Nothing goes live automatically. Click **Publish → Publish changes**. A dot on the button means unpublished changes. Commits pushed from GitHub also need this click |
| Cost | Publishing is free (0 credits). Published sites don't expire; preview links expire (7 days by default), so never share a preview link |
| Visibility | Free and Pro: "Anyone with the link", no restriction possible. Workspace-only or invite-only is Business/Enterprise only |
| Before publishing | A ~10 s **Quick scan** (database rules, dependencies). If the workspace setting **Block publishing with critical issues** is on, critical findings block the publish |
| Badge | **Hide Lovable badge** toggle in Project settings (Pro and up). It comes back after a downgrade |
| Visitor analytics | On by default, starts on first publish. Toggle: **Project settings → General → Publishing → Visitor analytics** ([Analytics docs](https://docs.lovable.dev/features/analytics)) |
| Unpublish | Project settings → Unpublish project |

Free check on 26 Sep: `https://dresden-mit-kind.lovable.app` answered **404 "Project not found"**, so no published project uses that name. Lovable confirms availability when we type it.

### 1.2 Custom domains

| Question | Answer (source: [Custom domain docs](https://docs.lovable.dev/features/custom-domain), [Launch guide](https://docs.lovable.dev/tips-tricks/launch-on-a-custom-domain), [Plans](https://docs.lovable.dev/introduction/subscription-plans)) |
|---|---|
| Plan | Custom domains are included in **Pro** (all paid plans). No extra Lovable fee |
| Where | **Project settings → Domains**: buy a domain, connect one you own, or transfer one |
| Buy through Lovable | In the Domains tab or, since 7 Sep 2026, **from chat**: Lovable shows the price in USD and a confirmation card, then a Stripe checkout. A and TXT records and SSL are set automatically, auto-renew is on by default, WHOIS privacy is on where the TLD supports it. Setup "usually completes within 30 minutes but can take up to a day". Root and `www` are both set up |
| TLDs you can buy through Lovable | Most gTLDs (.com, .app …) plus a fixed list of ccTLDs (ag, ai, … ch, … io, … pl, … uk …). **`.de` is not on the list**, so a `.de` domain has to be bought at a German registrar and connected |
| Connect a domain you own | **Automatic (Entri):** Lovable detects the registrar, you log in and authorise Entri to write the records. **Manual:** `A` record for `@` (and one for `www`) → `185.158.133.1`, plus `TXT` `_lovable` (or `_lovable.www`) = `lovable_verify=…` (value shown in Lovable). Remove old A/AAAA records for that host. Cloudflare DNS: "DNS only" (grey cloud). CAA records must allow `letsencrypt.org`, `pki.goog` or `ssl.com` |
| `www` vs root | Connect the root domain and keep **Redirect www → root** enabled (default) |
| SSL | Automatic. Contact support if it is missing after 72 h |
| Propagation | "Most changes are live within a few hours, some take up to 72 hours" |
| Primary domain | One domain can be primary. All others redirect to it with a **302** (Lovable hosting has no 301) |
| Search Console | Changing the custom domain means verifying the property again |

**Domain options and prices (for the founders to decide, nothing bought):**

| Option | Where | Price (26 Sep 2026) | Notes |
|---|---|---|---|
| `dresden-mit-kind.lovable.app` | Lovable | free | Recommended for Sunday |
| `dresden-mit-kind.de` or `dresdenmitkind.de` | German registrar, then connect (Entri or manual DNS) | INWX about €4–5/year net ([price list](https://www.inwx.de/de/domain/pricelist)); Strato €0.05/month in year 1, then €1/month ([Strato](https://www.strato.de/domains/domain-kosten/)) | Best fit for a Dresden audience. Not sold by Lovable. A DNS lookup on 26 Sep found no records for either name, which suggests they are free (check at the registrar) |
| `dresdenmitkind.com` or another gTLD | Lovable (chat or Domains tab) or any registrar | .com is typically $12–20/year; Lovable shows its price before checkout | Fastest to connect because Lovable sets DNS itself |

The name and domain are still open question Q1 in [[Idea B - Dies-Das-Ana-Nas]]. Buying one is a founder decision for Monday, not a Saturday-night task.

### 1.3 Recommendation for Sunday 14:00

1. **Publish as `dresden-mit-kind.lovable.app` today** (first publish: type `dresden-mit-kind` in Website URL). It is free, instant, needs no DNS and cannot fail on propagation. Put this URL on the slide, in the QR code and in the submission.
2. Before the first publish, set three toggles (free): **Hide Lovable badge** on; **Visitor analytics** off (see 3.3); **Auto-fix security issues** off (see 3.6).
3. Publish after every checked prompt (Plan v3 G.3). Last deliberate publish **by 12:30 Sunday**, then freeze. Because a publish is a snapshot, the teammate's unfinished prompts never reach the live URL until someone clicks Publish.
4. **Custom domain: optional, not on the critical path.** If the founders want one for Sunday anyway, connect it by **Saturday 22:00** so DNS and SSL have the night. Do **not** make it primary unless it shows "Live" and works on a phone by Sunday 11:00. If it becomes primary, `lovable.app` 302-redirects to it, so a broken custom domain would break the official URL too.

### 1.4 What changes in our system for the final URL

The app talks to four things: Supabase (data), n8n 04 (intake), the relay (call page; mic only in P13) and nothing else. Checked in the code on 26 Sep:

| Where | Change for `https://dresden-mit-kind.lovable.app` | Extra if a custom domain is connected |
|---|---|---|
| **Relay host env** (`services/voice-relay/server.js` reads it; set on Render, no code change) | `ALLOWED_ORIGINS=https://<relay-host>,https://dresden-mit-kind.lovable.app` and `ALLOWED_ORIGIN_SUFFIXES=` (empty). Why: "Start the call" opens `${RELAY_URL}/?request=<id>`, and **that page** (relay origin) opens `/call`, so the relay's own origin is the one that must be listed. The app origin only matters for `/listen` (intake mic) and P13. The default suffixes `.lovable.app,.lovableproject.com` let any Lovable app use our Deepgram quota. To test the mic inside the Lovable editor, also add the preview origin (DevTools console → `location.origin` in the preview) | add `https://dresden-mit-kind.de,https://www.dresden-mit-kind.de` |
| **Lovable app `src/config.ts`** (Plan v3 G.0 step 3, created by P1b) | `RELAY_URL` default = the relay's **https** origin, e.g. `https://voice-relay-xxxx.onrender.com` (a `wss://` value is converted). This value does not depend on the app URL. New `SITE_URL` default = `https://dresden-mit-kind.lovable.app` (P14 adds it; used for canonical and `og:url`). Both are public. The tracked `.env` in the Lovable repo already holds `VITE_SUPABASE_*`, so `VITE_RELAY_URL=` and `VITE_SITE_URL=` lines there probably work, but whether Lovable's publish build reads them is unverified. The defaults in `config.ts` are the safe path | `SITE_URL` = the primary domain, once it is primary |
| **n8n workflow 04** (`n8n/workflows/04-task-intake.json`) | **No change.** The webhook node has `allowedOrigins: "*"`. The real gate is the Code node "Check Origin + Size", whose list already matches `https://*.lovable.app` (403 `origin_not_allowed` otherwise). Tested live on 26 Sep: an `OPTIONS` preflight from `https://dresden-mit-kind.lovable.app` returned `204` with `Access-Control-Allow-Origin` set to that origin (no POST sent, so no execution) | Add `/^https:\/\/(www\.)?dresden-mit-kind\.de$/` to `ALLOWED_ORIGINS` in "Check Origin + Size", publish the workflow, re-export it to `n8n/workflows/`. Without this line the intake answers 403 on the custom domain |
| **Supabase** | **None.** We use no auth, so Site URL and Redirect URLs are unused ([docs](https://supabase.com/docs/guides/auth/redirect-urls); `supabase/config.toml` `site_url` is local dev only). The Data API always answers `Access-Control-Allow-Origin: *` and can't be restricted ([issue](https://github.com/supabase/supabase/issues/42033)). No workflow sends the user a link to the app (n8n 06 only calls Supabase REST) | none |
| **Lovable repo `public/`** (GitHub, 0 credits) | `robots.txt`: add `Sitemap: https://dresden-mit-kind.lovable.app/sitemap.xml`. `sitemap.xml`: absolute URLs on this host | regenerate both with the new host |
| **Docs** (after the URL is fixed) | `docs/deploy-relay.md` (`<name>.lovable.app` placeholders), `README.md` (Lovable app line), [[Pitch Kit v2 (merged)]] (URL, QR), `ONBOARDING.md` status | same |

Tighten after Sunday (Monday): in n8n 04 replace the `*.lovable.app` pattern with the exact origins (published + editor preview), and in the relay `REQUIRE_ORIGIN` / signed token (see `docs/deploy-relay.md`, "Security note").

---

## 2. SEO from here

### 2.1 What search engines see

- **Google renders JavaScript** (crawl → render queue → index) and asks SPAs for unique titles and descriptions, History-API routes, real `<a href>` links, and either a real 404 or `noindex` on error pages ([JS SEO basics, updated 4 Mar 2026](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics)).
- **Our app doesn't depend on that:** TanStack Start sends full HTML for every request. Link-preview bots (WhatsApp, Slack, LinkedIn) don't run JavaScript, so the `head()` of each route decides what the preview shows.
- **Current state of the live `head()`** (clone, 26 Sep): the root route has `author: HalloTermin`, and `/` says "HalloTermin — Doctor's appointments, spoken in German". Unless a prompt replaces these, a WhatsApp preview of the Sunday URL shows the old product. **This is the one SEO item that matters for the demo.**
- **What Lovable offers:** the **SEO & AI search** review (More → SEO & AI search → Scan project) is **free on all plans**. It checks metadata, Open Graph, structured data, `robots.txt`, `sitemap.xml`, indexing, and Search Console status. **Try to fix** runs a normal build prompt (costs credits) and may create or overwrite files in `public/`. Lovable does not need `llms.txt`. The docs have no hreflang guidance ([SEO docs](https://docs.lovable.dev/features/seo-aeo)).
- **Timing:** Google takes days to weeks to index a new site. Nothing we do tonight will be in Google by Sunday 14:00. For the weekend, "SEO" means correct link previews and not exposing private pages.

### 2.2 Weekend vs later

| Item | Sunday | Later |
|---|---|---|
| Clean URL `dresden-mit-kind.lovable.app` | **yes** (free) | custom domain after Q1 |
| Brand-correct title, description, `og:image` on every route | **yes** (P14 + `og-image.png`) | localised per language |
| `noindex` on `/r/:id`, `/ask`, `/suggest`, `/demo`, 404, demo listing | **yes** (P14). `/r/:id` shows names and transcripts, and demo-mode RLS lets anyone with the link read them | owner-scoped RLS (Monday plan) |
| `robots.txt` with `Sitemap:` line, static `sitemap.xml` | nice to have (0 credits) | dynamic server route |
| Google Search Console | after the demo (10 min) | Domain property when a custom domain exists |
| Language URLs + hreflang | no | **the main SEO lever** (2.5) |
| Event rich results | no | needs `/events/:id` leaf pages |
| Guide bodies in 5 languages | no | content depth for search |

### 2.3 Per route: titles, descriptions, Open Graph

Use the strings that already exist in `src/i18n/strings/en.json` (no new keys): page H1 as title, page intro as description. Head text stays **English** for now, because the server does not know the visitor's UI language (2.5) and Googlebot crawls without `Accept-Language` from US IPs ([Google](https://developers.google.com/search/docs/specialty/international/locale-adaptive-pages)).

| Route | Title | Description | Index? | Structured data |
|---|---|---|---|---|
| `/` | `Dresden mit Kind · ` + `home.title` | `home.subtitle` | yes | `WebSite` (optional) |
| `/courses` | `directory.coursesTitle` | `directory.coursesIntro` | yes | — |
| `/events` | `events.title` | `events.intro` | yes | none (list page, see 2.6) |
| `/communities` | `directory.communitiesTitle` | `directory.communitiesIntro` | yes | — |
| `/services` | `directory.servicesTitle` | `directory.servicesIntro` | yes | — |
| `/library` | `library.title` | `library.intro` | yes | — |
| `/guides/:slug` | guide `title_en` | `summary_en` | yes | `Article` |
| `/p/:id` | place name | `description_en` / `notes_en` | yes, **except** `subcategory = 'demo'` | minimal `LocalBusiness` (not for the demo listing) |
| `/ask`, `/r/:id`, `/suggest`, `/demo`, 404 | H1 | — | **noindex** | — |

- Canonical = `SITE_URL` + path **without** the query string, so filter URLs like `/courses?age=3-6&act=music` count as `/courses`. Set it per route, not in the root: TanStack dedupes `title` and `meta` by name ("last wins"), but a canonical link in the root plus one in a child would both render.
- `og:image`: one 1200×630 image, a few hundred KB (Lovable's guidance), at `public/og-image.png`: wordmark on paper `#F7F4EC` in pine, no photos, no children (Plan v3 D4 bans). Without our own image, Lovable uses "the latest screenshot", which could show a request page with a name on it.
- `/p/:id` and `/guides/:slug` must fetch their row in the **route loader**, so `head()` can use `loaderData` and the server HTML contains the text. Otherwise previews show generic text.
- `noindex` pages must **not** be blocked in `robots.txt`, or Google never sees the `noindex` ([Google](https://developers.google.com/search/docs/crawling-indexing/block-indexing)). `/r/<uuid>` URLs aren't linked anywhere public, so crawlers won't find them in the first place.

### 2.4 `sitemap.xml` and `robots.txt`

**`robots.txt`:** the Lovable template already ships `public/robots.txt` (Allow for Googlebot, Bingbot, Twitterbot, facebookexternalhit, `*`). Only add one line: `Sitemap: https://dresden-mit-kind.lovable.app/sitemap.xml`. Don't add `Disallow` lines.

**`sitemap.xml`: static file now, dynamic later.**

| | Static `public/sitemap.xml` from a script in our repo | Dynamic server route `src/routes/sitemap[.]xml.ts` |
|---|---|---|
| Freshness | as fresh as the last script run | always current (runs in the Worker on each request) |
| Risk on Sunday | none (a file can't break the build) | new code in the app. A mistake breaks the build or shows in the scan |
| Credits | 0 (Claude Code + GitHub sync) | 0 if written in the repo, or 1 prompt |
| When | **Sunday** | Monday, once data changes daily. Delete the static file then (both can't exist) |

Content: 6 pillar pages + 8 guides + every `resources` row except `subcategory = 'demo'` (about 150 URLs, far below the 50,000 limit), absolute URLs, `lastmod` from `guides.updated_at` or the later of `resources.retrieved_at` / `last_checked_at`. Google ignores `priority` and `changefreq` and uses `lastmod` only if it is accurate ([Google](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)). `/events` stays one URL (no per-event pages yet).

Sketch for Claude Code (proposal; not in the repo yet; Node 18+, no dependencies; the publishable key comes from the environment, never from a committed file):

```js
// scripts/seo/build-sitemap.mjs  →  node scripts/seo/build-sitemap.mjs <lovable-repo>/public/sitemap.xml
import { writeFileSync } from 'node:fs';
const SITE = (process.env.SITE_URL || 'https://dresden-mit-kind.lovable.app').replace(/\/+$/, '');
const REST = 'https://ycyrtlzympxzlfcocazh.supabase.co/rest/v1';
const KEY = process.env.SUPABASE_PUBLISHABLE_KEY;          // anon/publishable key; RLS allows SELECT on resources + guides
const get = p => fetch(`${REST}/${p}`, { headers: { apikey: KEY, Authorization: `Bearer ${KEY}` } }).then(r => r.json());
const [places, guides] = await Promise.all([
  get('resources?select=id,retrieved_at,last_checked_at&or=(subcategory.is.null,subcategory.neq.demo)'),   // neq alone drops NULLs
  get('guides?select=slug,updated_at'),
]);
const day = d => (d ? new Date(d).toISOString().slice(0, 10) : '');
const url = (path, mod) => `  <url><loc>${SITE}${path}</loc>${mod ? `<lastmod>${mod}</lastmod>` : ''}</url>`;
const rows = [
  ...['/', '/courses', '/events', '/communities', '/services', '/library'].map(p => url(p)),
  ...guides.map(g => url(`/guides/${g.slug}`, day(g.updated_at))),
  ...places.map(r => url(`/p/${r.id}`, day([r.retrieved_at, r.last_checked_at].filter(Boolean).sort().pop()))),
];
writeFileSync(process.argv[2] || 'sitemap.xml',
  `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${rows.join('\n')}\n</urlset>\n`);
console.log(`${rows.length} URLs`);
```

Then commit and push in the Lovable repo, and click **Publish → Publish changes**.

### 2.5 Multilingual SEO: language in the URL

Today (Plan v3 P1b) the UI language lives in `localStorage` `dmk_ui_lang` and every page has **one URL for six languages**. Consequences:
- Google indexes **English only**. It asks for "different URLs for each language version … rather than using cookies or browser settings" and advises against automatic redirects between language versions ([Google, updated 10 Dec 2025](https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites)).
- **hreflang is impossible** without language URLs. Each language version must list itself and all others, with absolute URLs ([Google, updated 21 Sep 2026](https://developers.google.com/search/docs/specialty/international/localized-versions)).
- **SSR side effect:** the server renders English with `<html lang="en" dir="ltr">`, then the client switches to Russian or Arabic after hydration, so the page briefly shows English and briefly the wrong direction. The LanguageProvider must read `localStorage` in an effect, not during the first render, or React reports hydration mismatches. Acceptable for Sunday; check the console.

| Option | hreflang | Fit with Plan v3 | Effort | Verdict |
|---|---|---|---|---|
| Status quo (`localStorage`) | no | as built | 0 | Sunday |
| `?lang=ru` | technically yes | **Collides:** `?lang=` already means *course language* on `/courses`, `/events` and the communities links (`/events?lang=ru`). A UI parameter would need another name (`?hl=`) and every internal link must carry it. Google marks URL parameters "Not recommended" | medium, fragile | no |
| Cookie `dmk_ui_lang` read by the server | no | Fixes the English flash (the server renders the right language). A language cookie the user chose counts as strictly necessary (§ 25 (2) no. 2 TDDDG, see 3.3). Mention it in the privacy page | small | optional Monday quick fix |
| **Path prefix `/{-$lang}/…`** (English unprefixed: `/courses`, `/ru/courses`, `/ar/p/<id>`) | **yes** | TanStack Router supports optional path params exactly for this (`/{-$locale}/about` matches `/about` and `/fr/about`, [docs](https://tanstack.com/router/latest/docs/framework/react/guide/path-params)). The server renders the right language and `dir`; `head()` gets localised titles from `params.lang`; existing links and the QR code keep working; the language menu switches the prefix instead of `localStorage`; `/` never auto-redirects (show the existing `common.languageBar` "Showing … in {language}. Change" instead) | one focused prompt or a repo change + route test | **Monday** |
| Subdomains or ccTLDs per language | yes | wrong tool (one city, one audience) | high | no |

With the prefix, hreflang goes in each route's `head()` links (`en`, `de`, `ru`, `uk`, `ar`, `tr`, `x-default` = English) or into the sitemap as `xhtml:link` (the script above can generate them; Google accepts either). Languages go in the path, not per country (`ru`, not `ru-DE`). The payoff: parents search in Russian, Ukrainian, Arabic and Turkish for Dresden courses and Kitas, where there is little competition. Our content already has `i18n` for places, events and guide summaries.

### 2.6 Structured data

| Type | Where | Worth it? |
|---|---|---|
| `Event` | family events | **Not yet.** Google needs "a unique URL (a leaf page)" per event and "only supports pages that focus on a single event". `/events` is a list with `#id` anchors ([Google, updated 8 Sep 2026](https://developers.google.com/search/docs/appearance/structured-data/event)). Monday: add `/events/:id`, then mark up `name`, `startDate`, `location` (name + address) as required, plus `eventStatus`, `offers` (free/paid), `organizer` |
| `LocalBusiness` | `/p/:id` | **Minimal only.** Google's guide is written for a business describing itself, and knowledge panels come from elsewhere ([Google](https://developers.google.com/search/docs/appearance/structured-data/local-business)). Only `name`, `address`, `telephone`, `url`, `geo` when present. **Never on the demo listing** (a fictional business) and never invented values. Our phones and hours are "not verified" |
| `Article` | `/guides/:slug` | **Yes, cheap.** No required fields; `headline`, `dateModified`, `author` are recommended ([Google](https://developers.google.com/search/docs/appearance/structured-data/article)) |
| `WebSite` / `Organization` | `/` | optional; Lovable's review says missing it is not an issue |

### 2.7 Google Search Console (after the demo)

- `*.lovable.app`: we don't control DNS, so use a **URL-prefix property** `https://dresden-mit-kind.lovable.app/` and verify with the **HTML file** method: put `public/google<token>.html` in the Lovable repo via GitHub (0 credits), publish, verify. Keep the file forever, because Google re-checks it ([Google](https://support.google.com/webmasters/answer/9008080)). Alternative: Lovable's Search Console connector via "Try to fix" in the SEO review (costs credits).
- Submit `sitemap.xml`, then run URL Inspection → "Test live URL" on `/`, one `/p/<id>` and one `/guides/<slug>`.
- With a custom domain: a **Domain property** (DNS TXT, covers www, root, http and https). Verify again after a domain change.

### 2.8 P14: SEO basics (ready to paste)

> Agent mode, one step. Run after P12 (at the earliest after P3 and P6, because it needs `/p/$id` and `/guides/$slug`). Before sending, push `public/og-image.png` via GitHub. Expect a few credits (it touches each route file once). If a route doesn't exist yet, Lovable should skip it.

```text
P14: SEO basics. One step. No new features, no new UI text, no schema or policy changes; do not change routing, the i18n setup or page layouts. This project is TanStack Start: set everything through each route's head() so it is in the server-rendered HTML. Skip routes that do not exist yet.

1. src/config.ts: add export const SITE_URL = (import.meta.env.VITE_SITE_URL ?? "https://dresden-mit-kind.lovable.app").replace(/\/+$/, ""). Public URL, not a secret.
2. Create src/lib/seo.ts with seo({ title, description, path, noindex, jsonLd }) returning { meta, links, scripts } for head():
   - meta: title = `${title} · Dresden mit Kind` (the home page passes its full title); description (max 160 characters, cut at a word boundary); og:site_name "Dresden mit Kind"; og:type "website"; og:title; og:description; og:url = canonical; og:image = SITE_URL + "/og-image.png"; og:image:width "1200"; og:image:height "630"; twitter:card "summary_large_image"; if noindex: robots "noindex".
   - links: canonical = SITE_URL + path (path only, no query string, no hash). Never put a canonical in the root route.
   - scripts: if jsonLd, [{ type: "application/ld+json", children: JSON.stringify(jsonLd) }].
3. Head text is English, read from src/i18n/strings/en.json (import it; the server does not know the visitor's UI language). Use existing keys only:
   / -> title "Dresden mit Kind · " + home.title, description home.subtitle, jsonLd {"@context":"https://schema.org","@type":"WebSite","name":"Dresden mit Kind","url":SITE_URL}
   /courses -> directory.coursesTitle / directory.coursesIntro
   /events -> events.title / events.intro
   /communities -> directory.communitiesTitle / directory.communitiesIntro
   /services -> directory.servicesTitle / directory.servicesIntro
   /library -> library.title / library.intro
   /guides/$slug and /p/$id: fetch the row in the route loader with the existing anon client from @/integrations/supabase/client (never client.server.ts), let the component read Route.useLoaderData() (or keep its query if that is less change), and build head() from loaderData. If the row does not exist, throw notFound().
     guide -> title_en, summary_en; jsonLd {"@context":"https://schema.org","@type":"Article","headline":title_en,"description":summary_en,"dateModified":updated_at,"inLanguage":"en","author":{"@type":"Organization","name":"Dresden mit Kind","url":SITE_URL},"publisher":{"@type":"Organization","name":"Dresden mit Kind","url":SITE_URL},"mainEntityOfPage":canonical}.
     place -> name, description_en ?? notes_en ?? home.subtitle. If subcategory is "demo": noindex and no jsonLd. Otherwise jsonLd {"@context":"https://schema.org","@type":"LocalBusiness","name":name,"address":{"@type":"PostalAddress","streetAddress":address,"addressLocality":city ?? "Dresden","addressCountry":"DE"},"url":canonical} plus telephone (phone), sameAs (website) and geo {"@type":"GeoCoordinates","latitude":lat,"longitude":lng} only when present. Never invent values.
   /ask, /r/$id, /suggest, /demo and the root notFoundComponent -> noindex; title = the page's H1 from en.json (404: common.notFoundTitle).
4. Root route head(): keep charSet, viewport, the stylesheet and font links and the icon; remove the "author" meta "HalloTermin"; add a default title "Dresden mit Kind", description home.subtitle, og:site_name, og:image, twitter:card as above and theme-color "#F7F4EC". Replace the old HalloTermin texts in any existing head() (index, new, r.$id).
5. public/robots.txt, public/sitemap.xml, public/og-image.png, public/favicon.ico and public/google*.html are maintained in GitHub: reference /og-image.png, but do not create, change or delete files in public/, and do not add sitemap or robots server routes.
6. Do not add hreflang, language prefixes in URLs, analytics, cookies or tracking scripts.
Report the files you changed.
```

**Check it worked (free):** in the editor, hover the preview's page selector: the **Social** and **Search** cards show "Dresden mit Kind" titles and our image (Lovable, 8 Sep 2026). After publishing: `curl -s https://dresden-mit-kind.lovable.app/courses | grep -E '<title>|og:|canonical'` shows the tags in the raw HTML; `curl -sI https://dresden-mit-kind.lovable.app/nope` shows the status (hope for 404); a `/p/<id>` link pasted into WhatsApp shows the place name; `/r/<id>` source contains `noindex`. Then run the free SEO & AI search scan for information only.

### 2.9 SEO work to do in the repo instead (GitHub sync, 0 Lovable credits)

1. `public/og-image.png` (1200×630, < 300 KB; render an HTML card with headless Chrome).
2. `public/favicon.ico`: replace Lovable's default file under the same name, so no code change is needed. Optional `apple-touch-icon.png` 180×180.
3. `public/robots.txt`: add the `Sitemap:` line.
4. `public/sitemap.xml` from `scripts/seo/build-sitemap.mjs` (2.4). Re-run after data changes, then publish.
5. `public/google<token>.html` for Search Console.
6. After the demo: move the canonical host into `VITE_SITE_URL` if a custom domain becomes primary, and regenerate the sitemap.
7. Monday: `src/routes/sitemap[.]xml.ts` dynamic route (then delete the static file), hreflang alternates in the sitemap, `/events/$id` + `Event` JSON-LD. These are code changes. Do them in the repo only when the teammate is not mid-prompt, and run `npm run build` first.

Every push to `main` syncs into the Lovable editor ("keep the branch in a working state", `AGENTS.md`). Coordinate with Anastasia before pushing, and never force-push.

---

## 3. Launch checklist (found along the way)

| # | Item | Why | How / cost | When |
|---|---|---|---|---|
| 1 | **Impressum** page + footer link "Impressum" on every page | § 5 DDG: providers of "geschäftsmäßige, in der Regel gegen Entgelt angebotene digitale Dienste" must show name, postal address and email, "leicht erkennbar, unmittelbar erreichbar" ([§ 5 DDG](https://www.gesetze-im-internet.de/ddg/__5.html)). § 18 (1) MStV asks for name and address on any site "nicht rein persönlicher oder familiärer Natur", and § 18 (2) for a person responsible for editorial content (our guides) ([LFK guide 2024](https://www.lfk.de/fileadmin/PDFs/Dokumente_und_Rechtsgrundlagen/Leitfaeden/leitfaden-impressumspflicht-2024.pdf)). A public site with founders and a Monday plan is not purely private | one teammate's full name, a postal address where they can receive mail (no P.O. box), email. Text in the repo (0 credits) or one small prompt. **Conflict:** P1b's footer says "No other links", which needs an exception for Impressum and Datenschutz | Sunday if 30 min are free; otherwise Monday, and don't promote the URL beyond the event before that |
| 2 | **Datenschutzerklärung** (privacy page) + footer link | GDPR Art. 13 information whenever personal data is processed ([GDPR](https://eur-lex.europa.eu/eli/reg/2016/679/oj)). We process: hosting logs (Lovable/Cloudflare), `call_requests` in Supabase Frankfurt (parent name, place phone, optional email, child age and start month, time windows), transcripts (text), results, `suggestions`; processors n8n Cloud, Anthropic (intake, brief, translation via n8n), Deepgram (voice) | short, honest page: controller, data, purposes, legal basis (consent for the call), processors and transfers outside the EU, retention, rights, the three browser storage keys. Footer already says "This is a demo. Please use test data only." | Monday plan item 2 (Anastasia). A minimal version on Sunday together with item 1 |
| 3 | **No cookie banner needed**, if and only if… | § 25 TDDDG requires consent for storing or reading anything on the device (cookies, `localStorage`), except when "unbedingt erforderlich" for a service the user "ausdrücklich gewünscht" ([§ 25 TDDDG](https://www.gesetze-im-internet.de/ttdsg/__25.html)). Ours: `dmk_ui_lang` (chosen language), `dmk_draft` (sessionStorage, the running request), `dmk_guide_<slug>` (checklist ticks). All three serve functions the user asked for | (a) **Visitor analytics off**: Lovable's docs say it measures traffic, not people, but don't say whether it stores anything on the device or how IPs are handled. (b) **Self-host the fonts**: the root route loads `fonts.googleapis.com`; LG München I (20.01.2022, 3 O 17493/20) found that dynamic Google Fonts send the IP to Google without a legal basis ([summary](https://www.ra-plutte.de/lg-muenchen-dynamische-einbindung-google-web-fonts-ist-dsgvo/)). Fontsource packages ship the files, including Fraunces with the SOFT axis (`@fontsource-variable/fraunces/full.css`, [files](https://cdn.jsdelivr.net/npm/@fontsource-variable/fraunces/)); change `__root.tsx` + `styles.css` in the repo. (c) No embedded maps or videos (Plan v3 uses OSM links: good). (d) Check after publishing: DevTools → Application shows only `dmk_*` keys and no cookies. List the keys in the privacy page. Plan v3's ban on a cookie banner holds only under (a)–(d) | (a) before first publish; (b) Sunday if time, else Monday; (d) Sunday |
| 4 | **Favicon and app name** | Lovable's default `favicon.ico` and the `author: HalloTermin` meta are live today | replace `public/favicon.ico` (0 credits); P14 fixes the meta; P1b the wordmark. Optional `apple-touch-icon.png` | Sunday |
| 5 | **404 page** | Exists (root `notFoundComponent`, "This page doesn't exist." + link home) | P14 adds `noindex`; P1b should use `common.notFoundTitle/Body/Link` so it is translated. Check the HTTP status with `curl -I` | Sunday |
| 6 | **Hide Lovable badge** | A clean demo | Project settings toggle (Pro), free | before first publish |
| 7 | **Auto-fix security issues: off** for this project | When on, Lovable adds the latest critical database findings to **every** build prompt, spends credits and tries to fix "common row-level security (RLS) misconfigurations" ([docs](https://docs.lovable.dev/features/privacy-and-security-settings)). Our `call_requests` SELECT-for-anyone policy is a deliberate demo-mode choice ([[Data Model]]); Knowledge says Lovable never touches policies | Project settings → Auto-fix security issues | now |
| 8 | **Block publishing with critical issues: off** (workspace) | The Quick scan will likely flag the demo-mode RLS as critical. If blocking is on, we can't publish on Sunday | Workspace settings → Privacy & security; check it once. Note the finding as known; owner-scoped RLS is a Monday item | Saturday |
| 9 | **Demo listing hygiene** | "Olgas Musikstudio" is fictional | `noindex`, not in the sitemap, no `LocalBusiness` (P14 + script); "Demo listing" tag (Plan v3); reset real listings after tests ([[DEF-047 Role-play calls mark real providers as checked by phone]]) | Sunday |
| 10 | **Share only the published URL** | Preview links expire and can show unfinished work | QR code + slide use `https://dresden-mit-kind.lovable.app` | Sunday |
| 11 | **Final publish window** | A publish during the demo could change the page on stage | last publish by 12:30; test on a phone over 4G in a private tab: home in Русский, a provider, `/ask` intake (no 403), "Start the call" opens the relay tab, `/r/<id>` updates live | Sunday 12:30–13:30 |
| 12 | **Emergency and AI lines** | Trust, [[AI discloses itself in first sentence]] | already in the footer (P1b) | done |

---

## 4. Summary

1. **Deploy and domain:** publish now as **`dresden-mit-kind.lovable.app`** (free, instant, the name was unused on 26 Sep). Custom domains are included in Pro. `.de` can't be bought through Lovable (German registrar, about €4–12/year, then Entri or A `185.158.133.1` + TXT `_lovable`). Only connect one if it is Live by Sunday 11:00, and don't make it primary on Sunday. The domain choice is a Monday founder decision (Q1). For the final URL: set relay `ALLOWED_ORIGINS` (relay origin + app origin) and empty `ALLOWED_ORIGIN_SUFFIXES`, set the `RELAY_URL` default and a new `SITE_URL` in `src/config.ts`, add the `Sitemap:` line to `robots.txt`. **Nothing** changes in n8n 04 for `*.lovable.app` (preflight tested) and **nothing** in Supabase. A custom domain adds one regex in n8n 04 and two relay origins.
2. **SEO:** the app is server-rendered (TanStack Start on an edge Worker), so crawlers and link previews get real HTML. For Sunday, fix the stale HalloTermin `head()`, add an `og:image`, and `noindex` the private and demo pages (P14 + repo files). Language URLs (`/{-$lang}/…`) with hreflang are the real Monday lever. `?lang=` is ruled out because it collides with the course-language filter.
3. **Launch:** add Impressum + Datenschutz links (P1b's "no other links" needs an exception). Turn Visitor analytics off and self-host the fonts, so no cookie banner is needed. Replace the favicon, hide the badge, turn auto-fix off, check the publish-blocking setting, and freeze publishing at 12:30.
