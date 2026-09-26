# Product Requirements Document: Dresden mit Kind (working title)

> Status: Draft v0.2 — 26 Sep 2026 (launch languages set)
> Built from the template in cpjet64/vibecoding `prd-guide.md`. Items marked **[ASSUMPTION]** or listed under Open Questions need a decision before build.

---

## Product Overview

**Product Vision:** The place an expat parent opens in their first year in Dresden to answer "what can we do, where can my child learn, who speaks our language, and how does this system work here?" — combining a curated guide with a review-driven directory of kids' providers ("Yelp for parents in Dresden").

**Target Users:**
- Primary: international/expat parents new to Dresden (0–3 years in the city), children aged 0–12.
- Secondary: providers — independent teachers, creatives, studios, supplementary/language schools, bilingual communities that want to reach these families.
- Tertiary: long-term local and international parents looking for activities.

**Business Objectives:**
1. Become the reference resource for international families in Dresden (organic search + word of mouth in parent chats).
2. Build a provider network that keeps listings current without the founder updating everything manually.
3. Create a basis for revenue (featured listings, provider subscriptions, partnerships) once there is audience. **[ASSUMPTION — monetization not yet decided]**

**Success Metrics:** see Analytics & Monitoring. MVP headline metric: returning visitors per month and number of active (self-updating) provider profiles.

---

## The Four Parent Needs (Home Page Pillars)

| # | Pillar | What the parent gets |
|---|--------|---------------------|
| 1 | **Events** | Fun, family-relevant events: concerts, festivals, meetups, seasonal markets. |
| 2 | **Courses** | Kids' and parent-child classes: yoga, music, dance, sport, art, etc. |
| 3 | **Bilingual communities** | Activities in other languages (e.g., music in Russian, a Finnish café with Finnish-language events), parent meetups, info on libraries and schools for international families. |
| 4 | **Experience library** | Articles: documents and bureaucracy, when and how to enrol in courses/Kita/school, restaurants, playgrounds, practical recommendations. |

Plus a fifth, provider-facing pillar:

| 5 | **Provider pages** | Each teacher, creative or school has a profile: description, rating, calendar of classes, reviews/comments from parents; providers can publish classes and edit their profile. |

---

## User Personas

### Persona 1: Newly arrived parent — "Maria"
- **Demographics:** 30–40, relocated for her or her partner's job, child 1–6 years; German A1–B1; high smartphone use; English and/or native language (e.g., Russian, Ukrainian, Spanish, Finnish).
- **Goals:** find activities quickly; find a community in her language; understand deadlines (Kita, school, registrations) before missing them.
- **Pain Points:** information scattered across German-only sites, Facebook/Telegram groups and word of mouth; can't judge quality of providers; doesn't know "how things are done here."
- **User Journey:** lands from Google or a parents' chat → reads an article → browses courses filtered by age + language + district → saves or contacts a provider → returns for weekend events.

### Persona 2: Established international parent — "Ahmed"
- **Demographics:** 35–45, in Dresden 3+ years, two kids 5–12.
- **Goals:** discover new activities, keep kids' heritage language alive, share recommendations.
- **Pain Points:** the same few options; no place to leave a structured recommendation.
- **User Journey:** checks weekly events → leaves reviews for places he knows → suggests a missing provider.

### Persona 3: Independent provider — "Olga, music teacher"
- **Demographics:** teaches kids' music classes in Russian and German, runs her own small business, limited marketing time.
- **Goals:** fill classes, be found by international families, look credible.
- **Pain Points:** Instagram alone doesn't reach new arrivals; building a website is expensive; no easy way to show a schedule.
- **User Journey:** claims or creates profile → gets verified → adds classes and dates → responds to reviews.

### Persona 4: Admin / editor (founder)
- **Goals:** curate quality, moderate reviews, publish articles, seed the directory before providers join.
- **Pain Points:** time; keeping data current; legal exposure from user content.

---

## Feature Requirements

Priorities use MoSCoW, scoped to the **MVP** (see Release Planning for sequencing).

| Feature | Description | User Stories | Priority | Acceptance Criteria | Dependencies |
|---|---|---|---|---|---|
| **Home page with 4 pillars** | Entry points to Events, Courses, Communities, Library; "this weekend" highlights | As a new parent, I want to see at a glance what the site offers so I know where to start | Must | 4 pillar blocks; ≥3 upcoming events shown; loads <2.5s LCP on mobile | Events, Listings, Articles data |
| **Provider directory** | Searchable list of providers/courses | As a parent, I want to filter by child age, category, language, district, price and day of week | Must | Filters combinable; results update without full reload; empty state suggests nearby alternatives | Taxonomy, provider data |
| **Provider profile page** | Public page per provider | As a parent, I want description, photos, languages, ages, location, prices, contact and upcoming classes on one page | Must | All fields render; map pin; contact link (email/phone/website/Instagram); schema.org `LocalBusiness`/`Organization` markup | Provider data model |
| **Class/offering calendar** | Recurring and one-off classes per provider | As a parent, I want to see when classes happen; as a provider, I want to add weekly recurring classes | Must (admin-entered) → Should (provider-entered) | Recurring rules (weekly, date range, exceptions); iCal export per provider | Provider accounts for self-service |
| **Events listing** | Family events with date, place, age, language, price | As a parent, I want to see what's on this weekend | Must | Filter by date range, age, language, free/paid; past events auto-hide; `Event` schema markup | — |
| **Bilingual communities section** | Communities, language groups, heritage-language classes, libraries/schools for internationals | As a parent, I want to find activities in my language | Must | Filter by language; each entry links to a profile or external page | Language taxonomy |
| **Experience library (articles)** | Editorial guides and recommendations | As a new parent, I want a step-by-step guide on e.g. Kita registration and when to apply | Must | Categories + tags; last-updated date shown on every article; related listings shown in article | CMS |
| **Multilingual UI** | Interface + key content in 11 launch languages (see Localization) | As a parent with weak German, I want the site in my own language | Must | Language switcher; hreflang tags; untranslated content falls back to EN with a visible notice; Arabic renders right-to-left | Localization setup, translation workflow |
| **Parent accounts** | Sign-up/login | As a parent, I want an account to save favourites and leave reviews | Should | Email magic link or password; GDPR consent; account deletion self-service | Auth |
| **Favourites** | Save providers/events | As a parent, I want to bookmark options to compare later | Could | Save/unsave; list page | Parent accounts |
| **Provider accounts & self-service** | Providers claim/create profile, edit it, publish classes | As a provider, I want to update my schedule myself | Should (Phase 2) | Claim flow with verification; admin approval before first publish; edit history | Auth, roles, moderation |
| **Reviews & ratings** | Parents rate (1–5) and comment | As a parent, I want to read other parents' experiences; as a provider, I want to reply | Should (Phase 3) | Only logged-in users; one review per user per provider; provider reply; report button; disclosure of how reviews are verified; moderation queue | Parent accounts, moderation, legal review |
| **Suggest a place/event** | Public submission form | As a parent, I want to suggest a provider that's missing | Should | Form → admin queue; spam protection | Admin panel |
| **Admin panel** | Manage all content, users, moderation | As admin, I want to add/edit/approve everything in one place | Must | CRUD for all entities; moderation queue; role management | — |
| **Newsletter** | Weekly "what's on" email | As a parent, I want a weekly digest | Could | Double opt-in (required in DE) | Email provider |
| **Booking / payments** | Book or pay for classes on-site | — | Won't (v1) | — | Revisit after traction |
| **Messaging between parents & providers** | In-app chat | — | Won't (v1) | Use external contact links instead | — |

---

## Taxonomy (drives filters — decide early)

- **Category:** Music, Dance, Sport & movement, Yoga, Art & crafts, Languages, STEM, Swimming, Theatre, Nature/outdoor, Parent–baby, Parent meetups, Libraries, Schools & Kita info, Restaurants/cafés (family-friendly), Playgrounds.
- **Age range:** 0–1, 1–3, 3–6, 6–10, 10+ (store as min/max months/years, display as bands).
- **Language(s) of instruction:** the 11 launch languages plus others as needed (e.g., FI, FR) — multi-select, independent of interface language.
- **District:** Dresden Stadtbezirke/Stadtteile (e.g., Neustadt, Altstadt, Blasewitz, Plauen…).
- **Price type:** free, per session, subscription, trial available.
- **Format:** recurring course, workshop, one-off event, community group, place.

---

## Localization

**Launch languages (11):**

| # | Language | Code | Notes |
|---|----------|------|-------|
| 1 | English | `en` | Default and fallback language |
| 2 | German | `de` | Local reference; official names of offices/documents kept in German with explanation |
| 3 | Ukrainian | `uk` | Cyrillic |
| 4 | Russian | `ru` | Cyrillic |
| 5 | Arabic | `ar` | **Right-to-left** — layout must mirror (use CSS logical properties) |
| 6 | Hindi | `hi` | Devanagari font required |
| 7 | Chinese | `zh-Hans` | Simplified; CJK font required |
| 8 | Polish | `pl` | |
| 9 | Vietnamese | `vi` | Diacritics — check font coverage |
| 10 | Turkish | `tr` | Watch casing rules (i/İ) in search and uppercase text |
| 11 | Spanish | `es` | |

**Requirements:**
- All UI strings (navigation, filters, buttons, forms, emails) translated in all 11 languages at launch.
- Taxonomy labels (categories, age bands, districts) translated in all 11.
- Articles: written in EN first, then translated; each translation shows its own "last updated" date. Missing translations fall back to EN with a notice ("This article isn't available in your language yet").
- Provider-written content (descriptions, classes, reviews) is shown in the language it was written in, with a "language of this text" label; machine translation on demand is a Could-have.
- Separate URL per language (`/en/…`, `/ar/…`) with hreflang tags for SEO.
- Language of instruction (a filter) is separate from the interface language.
- Dates, times and numbers formatted per locale.

**Workload note:** 11 languages multiplies the effort of every article and every UI change. Plan a translation workflow (AI draft + native-speaker review, ideally volunteers from the bilingual communities) and decide which article categories must be fully translated at launch.

---

## User Flows

### Flow 1: New parent finds a course
1. Lands on home page (or on an article from Google).
2. Clicks "Courses" → sets child age + language + district.
3. Opens a provider profile → sees schedule, prices, reviews.
4. Clicks contact / website / "add to calendar."
   - Alternative: no results → sees closest matches (other districts, other languages) + "Suggest a provider."
   - Error: provider data outdated → "Report outdated info" link → admin queue.

### Flow 2: Provider claims and updates a profile (Phase 2)
1. Finds own (admin-seeded) profile → "Is this you? Claim this page."
2. Signs up with email → verification (email on the listed domain, or admin manual check).
3. Admin approves → provider edits profile, adds recurring class (weekly, time, dates, exceptions).
4. Changes go live; major changes (name, category) require re-approval.
   - Error: someone claims a profile that isn't theirs → admin rejects; audit log.

### Flow 3: Parent leaves a review (Phase 3)
1. Logged-in parent opens profile → "Write a review."
2. Selects rating, writes text, confirms they attended (checkbox + optional date).
3. Review goes live after automated checks (or into queue if flagged).
4. Provider is notified and can reply publicly once.
   - Alternative: provider disputes review → report → admin review, notice-and-action process.
   - Edge: review contains personal data about a teacher/child → removed per moderation policy.

### Flow 4: Admin publishes an article
1. Writes in CMS (EN, optionally DE/RU).
2. Links related providers/events.
3. Sets "last reviewed" date; article flagged for re-check after X months.

---

## Non-Functional Requirements

### Performance
- **Load Time:** LCP < 2.5 s on mid-range mobile, 4G.
- **Concurrent Users:** low hundreds at launch; design for thousands.
- **Response Time:** filter results < 500 ms.

### Security
- **Authentication:** email-based auth (magic link or password + reset); no social login in v1 **[ASSUMPTION]**.
- **Authorization:** roles — `visitor`, `parent`, `provider`, `editor`, `admin`. Providers edit only their own profiles (enforce at database level, e.g., row-level security).
- **Data Protection:** GDPR-compliant; EU data hosting; minimal personal data; no data about children stored (reviews must not name children); cookie consent only if non-essential cookies/analytics are used. See the repo's `full-stack-security-guide.md` before build.

### Legal & Compliance (Germany/EU) — verify with a professional
- Impressum and privacy policy (Datenschutzerklärung).
- User-generated reviews: moderation policy, report mechanism, and information on whether/how reviews are verified (EU consumer-law rules on reviews).
- Handling of platform content complaints under the EU Digital Services Act (notice-and-action, statement of reasons on removal).
- Double opt-in for newsletter.
- Photos of children: providers must confirm they have consent to publish.

### Compatibility
- **Devices:** mobile-first (most traffic will come from phones and chat links).
- **Browsers:** last 2 versions of Chrome, Safari, Firefox, Edge.
- **Screen Sizes:** 360 px and up.

### Accessibility
- **Compliance Level:** WCAG 2.1 AA.
- **Specific Requirements:** simple language, readable for non-native speakers; clear icons for language and age.

---

## Technical Specifications

> Note: the current Tilda catalog is fine for a curated directory and articles, but provider accounts, reviews, per-provider calendars and role-based editing go beyond what Tilda is built for. Recommendation: keep Tilda (or a static landing page) for validation, and build the platform on a stack that supports accounts and a real database.

### Frontend
- **Technology Stack:** Next.js (React) + Tailwind CSS **[ASSUMPTION — well-supported by AI coding tools]**
- **Design System:** simple component library (e.g., shadcn/ui); warm, calm, family-oriented visual language.
- **Responsive Design:** mobile-first.

### Backend
- **Technology Stack:** Supabase (Postgres, auth, storage, row-level security) in an EU region.
- **API Requirements:** REST/RPC via Supabase; server actions in Next.js.
- **Database:** Postgres. Core entities:
  - `users` (role), `providers`, `provider_members` (who can edit which provider)
  - `offerings` (course/class definition) → `sessions` (recurrence rule + exceptions)
  - `events` (one-off, may belong to a provider)
  - `communities`, `places` (playgrounds, libraries, restaurants)
  - `articles` (with translations), `reviews`, `review_replies`, `reports`
  - `taxonomies` (categories, languages, districts, age bands) + join tables
- **Content:** articles in a headless CMS or Supabase tables with a simple editor.

### Infrastructure
- **Hosting:** Vercel or an EU host (e.g., Hetzner) — prefer EU for GDPR simplicity.
- **Scaling:** managed services; no custom infrastructure in v1.
- **CI/CD:** GitHub → automatic preview deployments; separate dev/staging/prod (see `development-environments.md`).

---

## Analytics & Monitoring

- **Key Metrics:**
  - Monthly unique and returning visitors
  - Directory searches per visit; filter combinations used (reveals demand, e.g., "Russian + music + 3–6")
  - Outbound provider contacts (clicks on phone/email/website)
  - Number of listings, % updated in last 90 days
  - Provider claim rate; active providers (edited in last 60 days)
  - Reviews per provider (Phase 3)
- **Events:** search, filter_applied, profile_view, contact_click, add_to_calendar, article_read, suggest_submitted, review_submitted.
- **Dashboards:** weekly overview (traffic, contacts, stale listings).
- **Alerting:** uptime check; error tracking (e.g., Sentry).
- **Privacy:** cookieless analytics (e.g., Plausible/Umami) to avoid a consent banner where possible.

---

## Release Planning

The main risk in a "Yelp for X" product is the cold start: reviews and provider self-service are worthless without audience, and an empty rating widget reduces trust. So value for parents comes first, marketplace mechanics later.

### Phase 1 — MVP: Curated guide (v1.0)
- **Features:** home page, directory with filters, provider profiles (admin-entered), events, bilingual communities, articles, UI in all 11 launch languages (articles with EN fallback), "suggest a place," admin panel.
- **Content target at launch:** ~60–100 providers/places, 10–15 articles, events for the next 4 weeks **[ASSUMPTION]**.
- **Timeline:** TBD.
- **Success Criteria:** returning visitors growing month over month; providers asking to be listed.

### Phase 2 — Provider self-service (v1.1)
- Claim flow, provider accounts, providers publish classes and events, iCal export, parent accounts + favourites.

### Phase 3 — Reviews & ratings (v1.2)
- Reviews, ratings, provider replies, reporting, moderation queue, review-verification disclosure.

### Phase 4 — Monetization & growth (v2.0)
- Featured listings / provider subscriptions, newsletter, more languages, possibly booking.

---

## Open Questions & Assumptions

- **Q1:** Final name and domain — keep "Dresden mit Kind"? (A German name signals local; an English name may signal "for internationals".)
- **Q2:** ~~Which languages at launch?~~ Decided: 11 languages (see Localization). Open: which article categories must be fully translated at launch, and who reviews translations per language?
- **Q3:** Monetization: free for providers forever, freemium, or paid featured listings?
- **Q4:** Who writes and maintains articles and events — only you, or guest authors from communities?
- **Q5:** Build on a code stack (recommended above) or push Tilda further for Phase 1?
- **Q6:** Should parents be able to review without an account (lower friction, more spam) or only with one?
- **Q7:** Is the Impact Hub "Business, Baby!" mentoring relevant to scope/timeline decisions?
- **A1:** Most traffic comes from mobile and from links shared in parent chats.
- **A2:** Providers will update their profiles only if it brings them visible bookings/contacts.
- **A3:** Parents trust curated recommendations more than anonymous ratings in the early stage.

---

## Appendix

### Competitive Analysis (to be researched)
- **Expat Facebook/Telegram/WhatsApp groups:** high trust and activity; information not searchable, repeats constantly, gets lost.
- **Google Maps reviews:** broad coverage; no filtering by child age or language of instruction; no class schedules.
- **City / tourism event calendars:** official and current; mostly German, not family- or language-focused.
- **Meetup / Instagram:** good for communities; fragmented, no directory.
- **Gap:** no single, searchable, multilingual source combining activities, language communities and "how-to" knowledge for families.

### User Research Findings (to do)
- Interview 8–10 expat parents: how they found their current activities, what they wish they'd known earlier.
- Interview 5 providers: how they get new families; would they update a profile themselves?

### AI Conversation Insights
- **Conversation 1:** 25 Sep 2026, Claude — initial PRD draft from founder's description; identified cold-start risk and phased release; flagged Tilda limitations for accounts/reviews.
- **AI-Generated Edge Cases:** outdated schedules; profile claimed by the wrong person; review naming a child; provider running classes in several locations; courses with waitlists or registration windows; events cancelled last-minute; same provider teaching in two languages.

### Glossary
- **Provider:** any teacher, creative, studio, school or community that offers something for families.
- **Offering:** a course or class a provider runs; has one or more sessions.
- **Session:** a dated occurrence (or recurrence rule) of an offering.
- **Place:** a location without a provider behind it (playground, library, restaurant).
