---
type: concept
tags: [lovable, ui]
sources: [anti-ai-slop-ui-ux, component-reference-design, ui-ux-pro-max, "[[Idea A - HalloTermin (Abdul)]]", "[[Lovable - Practical Guide]]", supabase/migrations/20260925190000_init_schema.sql, supabase/seed.sql]
---
# Lovable Prompt Pack (HalloTermin)

**What this is:** everything we paste into Lovable, in order. Step 0 (setup), then the Knowledge block, then 7 build prompts. Each prompt is small enough to check in the preview before sending the next one.

**Before you start (step 0, costs no credits):**
1. Lovable project → **More → Cloud → "Already have a Supabase project? Connect it here"** → pick project `ycyrtlzympxzlfcocazh` (Frankfurt). **Never click "Enable Cloud".** Check that the Cloud icon shows the Supabase logo and our project name ([[Decide Lovable backend before first prompt]]).
2. Connect GitHub (Settings → Connectors → GitHub). Then small text fixes can be made in the repo for free.
3. Paste **Knowledge part A** (section 2) followed by **Knowledge part B** (the banned list in section 1) into **Project settings → Knowledge**. Together they come to about 8,000 characters, under the 10,000 limit.
4. Then send P1 to P7 one at a time. Check the preview after each one.

---

## 1. Visual direction: "Bilingual paper"

**The idea:** the app looks like a calm, well-set letter on warm paper, written in pine-green ink. German gets a serif voice and English gets a clean sans, so the user can see at a glance which language is which. Only one colour signals "live": amber, used for the call in progress.

**Why this and not the tool's suggestion (4 lines):**
- The `ui-ux-pro-max` search suggested the **"Accessible & Ethical"** style (WCAG, 16px+, 44px targets, visible focus). We keep all of that. We **reject** its cyan #0891B2 + green palette, because every health app uses clinical cyan and the logo-swap test would fail.
- The second query ("live call transcript, editorial, bilingual") suggested an editorial serif pairing (Newsreader). We keep the idea that the transcript reads like a script, but not its pink CTA.
- Warm paper + pine ink feels personal and trustworthy (like a letter from someone who is helping you), not like a hospital or a startup. A serif for the German lines makes the language switch obvious without flags or badges.
- Every colour pairing below passes WCAG AA (ratios noted). Light mode only, on purpose: we don't have the time to test a dark mode properly.

### Palette (hex + HSL for shadcn tokens)

| Token | Hex | HSL (for `index.css`) | Use | Contrast |
|---|---|---|---|---|
| `--paper` (background) | `#F7F4EC` | `44 41% 95%` | page background | — |
| `--card` (surface) | `#FFFDF8` | `43 100% 99%` | cards, form panels, transcript | — |
| `--ink` (foreground) | `#1C2420` | `149 12% 13%` | body text, headings | 14:1 on paper |
| `--ink-muted` | `#5B635E` | `143 4% 37%` | helper text, English subtitles, meta | 5.6:1 on paper |
| `--pine` (primary) | `#1F5C4A` | `162 49% 24%` | primary buttons, links, "booked", focus ring | 7.1:1 on paper; white on pine 7.8:1 |
| `--pine-hover` | `#174A3B` | `162 53% 19%` | primary hover | — |
| `--pine-tint` | `#E6EEE9` | `143 19% 92%` | agent lines in the transcript, selected states | ink on it: 12:1 |
| `--amber` (live signal) | `#D98E04` | `39 96% 43%` | **only** the "calling / live" dot and the live step fill; ink text on amber | ink on amber 5.9:1 (never amber text on paper) |
| `--amber-text` | `#8A5A00` | `39 100% 27%` | "needs your answer" text | 5.4:1 on paper |
| `--amber-tint` | `#FBF0D9` | `41 81% 92%` | "needs your answer" panel background | — |
| `--brick` (destructive) | `#A63A2A` | `8 60% 41%` | errors, "declined", "didn't go through" | 5.8:1 on paper |
| `--brick-tint` | `#F6E4DF` | `13 56% 92%` | error panel background | — |
| `--line` (border) | `#D9D2C3` | `41 22% 81%` | dividers, card borders (decorative) | — |
| `--line-strong` (input border) | `#8C8577` | `40 8% 51%` | input borders (need 3:1) | 3.3:1 on paper |

Distribution (60-30-10): paper/card 60%, ink 30%, pine 10%. Amber and brick only appear as status signals.

### Type
- **Display + German text:** **Fraunces** (Google Fonts, variable serif). Headings at weight 600, German transcript lines and the German brief at 400. `https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=Source+Sans+3:wght@400;600&display=swap`
- **UI + English text:** **Source Sans 3** at 400 and 600. It is very legible for non-native readers. Use `font-variant-numeric: tabular-nums` for times and dates.
- Scale (major third, base 17px because our users read in their second language): 14 / 17 / 21 / 26 / 33 / 41, and 52 for the landing headline only. Headings `line-height 1.15`, body `1.6`, body width ≤ 65ch, always left-aligned.
- No gradient text, no all-caps eyebrows above sections, no monospace.

### Spacing, radius, elevation
- 8px grid. Contextual gaps: 4–8px inside a control, 16px inside cards, 24px between form groups, 48–96px between landing sections (vary it, never one uniform padding).
- Radius **scale**: inputs/buttons/badges 6px, cards 10px, dialogs 14px. `rounded-full` only for the live dot.
- Elevation: flat by default, 1px `--line` borders. At most one soft neutral shadow, for the result card (`0 1px 2px rgb(28 36 32 / 0.06), 0 4px 12px rgb(28 36 32 / 0.06)`).
- Icons: **lucide-react only**, 16–20px, stroke 1.75, one colour (ink or pine). No emoji anywhere.

### Motion rules
- Hover/focus colour changes 120ms. New transcript lines and status changes enter in 200ms (opacity + 4px translate), ease-out. Exits are 150ms, ease-in.
- One ambient animation in the whole app: the amber live dot pulses (opacity only) while `status = 'calling'`.
- No scroll-triggered animations, no parallax, no typewriter, no springs, no `hover:scale`.
- `@media (prefers-reduced-motion: reduce)` turns off all transitions and the pulse. Content still appears immediately.

### Tone of voice
- Plain English at B1 level: short sentences, one idea each. Our readers are smart but read English or German as a second language.
- Calm and honest. Say what happens next and what we don't do. No exclamation marks, no hype.
- Introduce a German term once, with its meaning: "Überweisung (referral letter)".
- Specific CTAs: "Ask HalloTermin to call", "See a finished demo call", "Add to my calendar". Never "Get started" or "Learn more".
- Always name the AI: "our AI assistant". Never pretend a human is calling.

### Knowledge part B: banned list (paste after part A)

```text
DESIGN BANS (hard rules; if a change would add one of these, don't make it)
- No purple, violet or indigo anywhere. No gradients on text, buttons, borders or backgrounds. No aurora or blurred blobs.
- No Inter or Geist. Fonts are Fraunces (display + German text) and Source Sans 3 (UI + English) only. Max 2 weights per family.
- No glassmorphism (backdrop-blur, translucent white cards), no neon glow shadows, no shadow-lg/2xl on cards.
- No 3 identical cards in a row (icon-in-square + title + blurb). Vary size and structure; use lists, steps or definition lists instead.
- No centered hero with two equal buttons. Hero is left-aligned: one primary button + one text link.
- No eyebrow pill badges ("New", "AI-powered"), no uppercase tracking-widest labels above every section.
- No rounded-2xl on everything, no rounded-full pill buttons. Radius scale: 6px controls, 10px cards, 14px dialogs.
- No left-border accent cards (border-l-4). No emoji as icons or bullets. lucide-react only, 16-20px, one colour.
- No hover:scale, no fade-in-up on scroll, no transition-all, no animation longer than 300ms, no bouncing. Always honour prefers-reduced-motion.
- No fake social proof: no "Trusted by 5,000+", no invented testimonials, no avatar rows, no star ratings, no invented numbers.
- No hype words: supercharge, unlock, seamless, effortless, revolutionize, empower, cutting-edge, in seconds, get started, learn more.
- No glass or floating navbar, no sticky CTA bar, no mega-footer with dead links, no cookie banner (we use no tracking).
- No stock photos, no AI-generated people, no blob-people illustrations. Show real product UI (transcript, status) instead.
- No low-contrast grey body text. Body text is ink #1C2420 or ink-muted #5B635E only. Colour is never the only signal: always icon + text.
- No dark mode (light only for this build).
```

---

## 2. Project Knowledge (part A): paste into Lovable → Project settings → Knowledge

```text
PRODUCT
HalloTermin: a newcomer in Germany types an appointment request in English; our AI voice assistant phones the doctor's practice in German, books a slot inside the times the user approved, and the user watches the call live with English subtitles.
Users: international students and new arrivals in Dresden with little German (main persona: Priya, 24, Master's student at TU Dresden, public insurance with TK, A1 German). They are on phones, reading English as a second language.
UI language: English only. German appears only in the call brief and transcript, always with an English line next to it.

ARCHITECTURE (do not change)
- Backend = our OWN Supabase project (ref ycyrtlzympxzlfcocazh, Frankfurt), already connected. Never enable or suggest Lovable Cloud.
- The schema already exists and is managed by SQL migrations in a separate git repo. NEVER create, alter or drop tables, columns, enums, policies, triggers, functions or storage buckets. NEVER propose a migration. If you think the schema is missing something, say so in chat and stop.
- The frontend uses only the publishable/anon key via the generated client: import { supabase } from "@/integrations/supabase/client". Never put any secret or service_role key, n8n URL or webhook secret in code.
- The browser does exactly two things: (1) INSERT one row into call_requests, (2) READ and subscribe (Supabase Realtime postgres_changes) to call_requests, calls, transcript_lines, events. Everything else (brief, phone call, transcript, result, emails) is done by n8n with the service key. Do not call n8n or any webhook from the browser. Do not create Edge Functions.
- No login, no accounts, no auth screens. Anyone with a request link can view it (demo mode).

HARD PRODUCT RULES
- Never ask for symptoms, diagnoses or any free-text health details. Reason is a category only. No "notes" or "message" field anywhere.
- Always show the AI disclosure: the assistant introduces itself as an AI ("KI-Assistentin") in its first sentence and calls on the user's behalf. It never pretends to be the user.
- Never store or play audio. The app shows text only. Never add audio upload, recording or playback.
- The assistant only books inside the user's time windows; say this next to the time-window picker and on the consent checkbox.
- Show dates/times in Europe/Berlin time, formatted en-GB (e.g. "Tue 29 Sep, 08:15").

DATA CONTRACT (exact names; enum/check values are lowercase and must be sent exactly)
Table call_requests (anon may INSERT only when consent_ai_call = true; anon may SELECT)
  id uuid (default gen_random_uuid; we generate it client-side with crypto.randomUUID())
  created_at, updated_at timestamptz (DB sets)
  status request_status: 'submitted' | 'briefed' | 'calling' | 'booked' | 'needs_user' | 'rejected' | 'failed' (DB default 'submitted'; never sent by the app)
  patient_name text NOT NULL
  patient_dob date (nullable, 'YYYY-MM-DD')
  insurance_type text: 'gkv' | 'pkv' | 'other' (nullable)
  insurance_name text (nullable)
  user_email text NOT NULL
  user_language text default 'en' (send 'en')
  practice_name text NOT NULL
  practice_phone text NOT NULL
  reason_category text NOT NULL: 'first_visit' | 'checkup' | 'acute' | 'follow_up' | 'specialist' | 'other'
  has_referral boolean NOT NULL default false
  is_new_patient boolean NOT NULL default true
  time_windows jsonb NOT NULL: array of 1-3 objects [{"date":"2026-09-29","from":"08:00","to":"12:00"}] (send a real array, not a string)
  consent_ai_call boolean NOT NULL, must be true
  consent_at timestamptz (DB default now(); don't send)
  call_brief_de text (written by n8n; read-only for the app)
Table calls (read-only for the app; one row per phone attempt)
  id uuid, request_id uuid -> call_requests.id, created_at, provider text, provider_call_id text, started_at, ended_at timestamptz,
  outcome text: 'booked' | 'rejected_no_new_patients' | 'needs_user' | 'no_answer' | 'voicemail' | 'failed' (nullable while the call runs),
  booked_slot timestamptz, bring_items text[] (German words, e.g. {'Versichertenkarte','Überweisung'}), summary_en text, error text
Table transcript_lines (read-only; streams in during a call)
  id bigint (ordering key), call_id uuid -> calls.id, created_at, speaker speaker: 'agent' | 'practice' | 'system', text_de text NOT NULL, text_en text (nullable, may arrive empty)
Table events (read-only; audit log of automation steps)
  id bigint, created_at, request_id uuid, source text ('app' | 'n8n' | 'voice' | 'system'), type text (e.g. 'request_submitted', 'brief_created', 'call_started', 'call_ended', 'email_sent'), payload jsonb
Realtime is enabled on all four tables.
Demo request with a finished call: /r/00000000-0000-0000-0000-000000000001

ROUTES
/ landing · /new request form · /r/:id request status + live call · /demo redirects to the demo request · * friendly 404

DESIGN SYSTEM ("Bilingual paper")
Colours (map to shadcn HSL tokens in index.css): background paper #F7F4EC; card #FFFDF8; foreground ink #1C2420; muted-foreground #5B635E; primary pine #1F5C4A (hover #174A3B, text white); accent/pine-tint #E6EEE9; live amber #D98E04 (only for the live/calling signal, with ink text); amber-text #8A5A00 on amber-tint #FBF0D9 for "needs your answer"; destructive brick #A63A2A on brick-tint #F6E4DF; border #D9D2C3; input border #8C8577; focus ring pine, 3px, offset 2px.
Fonts (Google Fonts): Fraunces 400/600 for headings, the wordmark and every German text (brief, transcript text_de). Source Sans 3 400/600 for UI, body and every English text. Base size 17px; scale 14/17/21/26/33/41 (52 landing headline only). Tabular numbers for times.
Radius: 6px controls, 10px cards, 14px dialogs. Flat surfaces with 1px borders; the only shadow is on the result card.
Icons: lucide-react, 16-20px, stroke 1.75, single colour. Touch targets at least 44px.
Motion: 120ms colour transitions; 200ms opacity + 4px entrance for new items; the live dot pulse is the only looping animation; everything off under prefers-reduced-motion.
Voice: plain B1 English, short sentences, calm and specific, no exclamation marks. Explain German terms once in brackets.
```

---

## 3. Build prompts (send in this order)

> Tip: send each prompt in **Agent mode** exactly as written. If something is wrong, fix it with one short follow-up; don't re-send the whole prompt.

### P1: App shell, design tokens, routes

**Goal:** fonts, colours and layout primitives are in place before any feature exists, so later prompts inherit them.

```text
Set up the app shell for HalloTermin. Follow the Knowledge (design system + banned list) exactly. No database code in this step.

1. Design tokens: in index.css, set the shadcn CSS variables (HSL) to our palette: --background 44 41% 95%; --card 43 100% 99%; --foreground 149 12% 13%; --muted-foreground 143 4% 37%; --primary 162 49% 24%; --primary-foreground 0 0% 100%; --accent 143 19% 92%; --accent-foreground 149 12% 13%; --destructive 8 60% 41%; --border 41 22% 81%; --input 40 8% 51%; --ring 162 49% 24%; --radius 0.625rem. Add custom tokens --pine-hover 162 53% 19%, --amber 39 96% 43%, --amber-text 39 100% 27%, --amber-tint 41 81% 92%, --brick-tint 13 56% 92% and expose them in tailwind.config (colors: amber, amber-text, amber-tint, brick-tint, pine-hover). Remove the dark theme block; light mode only.
2. Fonts: load Fraunces (opsz, wght 400;600) and Source Sans 3 (400;600) from Google Fonts in index.html. Tailwind fontFamily: display = Fraunces, sans = Source Sans 3 (make sans the default). Base font-size 17px, body line-height 1.6, headings font-display weight 600 line-height 1.15. Add a utility class .de for German text (Fraunces 400) and .tnum for tabular numbers.
3. Global CSS: visible focus ring (3px pine, 2px offset) on all interactive elements; @media (prefers-reduced-motion: reduce) disables all transitions and animations.
4. Layout: a solid header (paper background, 1px bottom border, not sticky, not blurred) with the wordmark "HalloTermin" in Fraunces 600 on the left ("Hallo" in pine, "Termin" in ink) linking to /, and one text link on the right: "Start a request" -> /new. A minimal footer with two lines in muted text: "HalloTermin is a demo built at Weekender Build Dresden, September 2026. Our AI assistant always says it is an AI." and "Not for emergencies: call 112. Out-of-hours doctor: 116117." No other footer links, no social icons.
5. Routes with react-router: / (Landing placeholder with just the H1 "We call the doctor in German, so you don't have to."), /new (placeholder H1 "Book a doctor's appointment"), /r/:id (placeholder showing the id), /demo (redirect to /r/00000000-0000-0000-0000-000000000001), and a 404 page with the text "This page doesn't exist." and a link "Go to the start page".
6. Page container: content max width 72rem with 16px side padding on mobile and 32px from md; text blocks max 65ch.
Do not add any cards, hero images, gradients or placeholder features.
```

**Check it worked:** the preview has a warm off-white background, a serif wordmark and sans body text, and no purple anywhere. `/demo` jumps to `/r/0000…0001`, a random URL shows the 404 page, and pressing Tab shows green focus rings.

---

### P2: Request form → insert into `call_requests`

**Goal:** one form writes one valid row, which fires the n8n trigger. After submitting, the user lands on `/r/:id`.

```text
Build the request form on /new. It inserts exactly one row into the existing table call_requests (see Knowledge data contract). Do NOT create or change any table or policy.

Layout: single column, max width 40rem, left-aligned. Page H1 "Book a doctor's appointment", intro line: "Tell us who, where and when. Our AI assistant calls the practice in German and books a time that fits." Top-right of the form a small text button "Use demo details" that fills name Priya Sharma, date of birth 2002-03-14, insurance public / Techniker Krankenkasse, practice "Hausarztpraxis Dr. Weber", reason first_visit, new patient yes, referral no, email priya@example.com, and one window next Tuesday 08:00-12:00. It must NOT fill the phone number.

Fieldsets (use <fieldset> + <legend>, 24px between groups, labels above inputs, helper text in muted colour):
1. "Who is the appointment for?"
   - Full name (patient_name, required) helper "As written on the insurance card."
   - Date of birth (patient_dob, optional, native date input) helper "The practice usually asks for it."
   - Health insurance (insurance_type, radio group, required in the form): gkv "Public (gesetzlich), e.g. TK, AOK, Barmer" | pkv "Private (privat)" | other "Other or not sure"
   - Insurance company (insurance_name, optional) placeholder "e.g. Techniker Krankenkasse"
   - "Have you been to this practice before?" (is_new_patient, radio: "No, I'm a new patient" = true (default) | "Yes" = false)
   - "Do you have a referral letter (Überweisung)?" (has_referral, radio: "No" = false (default) | "Yes" = true)
2. "Which practice should we call?"
   - Practice name (practice_name, required)
   - Practice phone number (practice_phone, required) helper "German number, e.g. +49 351 1234567". Validate: after removing spaces, / and -, it must match ^(\+49|0)\d{6,14}$.
3. "What kind of appointment?"
   - reason_category as a shadcn Select, required, these exact values and labels:
     first_visit "First visit (Erstuntersuchung)"; checkup "Check-up (Vorsorge)"; acute "Urgent, this week (Akuttermin)"; follow_up "Follow-up visit"; specialist "Specialist appointment (Facharzt)"; other "Something else"
   - Fixed note under it: "We never ask about symptoms. The practice only needs the type of appointment."
4. "When can you go?" (time_windows)
   - 1 to 3 rows, each: date (native date, min today, max today+60 days), from and to (native time inputs, step 900). Button "Add another time" (hidden at 3), each extra row has a "Remove" icon button with aria-label. Validation per row: all three set, from < to, at least 30 minutes long.
   - Note: "The assistant will only accept a time inside these windows. If the practice offers something else, we ask you first."
5. "Where should we send the result?" - Email (user_email, required, valid email).
6. Consent (consent_ai_call): one required checkbox with this label: "I ask HalloTermin's AI assistant to call this practice for me in German and to book a time only inside my windows. It will say it is an AI in its first sentence. No audio is recorded; only a text transcript is kept."

Validation: zod + react-hook-form. Validate on blur and on submit. Every invalid field gets a red (destructive) border, an inline message under it with an alert icon, and aria-invalid + aria-describedby. On submit with errors, move focus to the first invalid field. Never disable the submit button silently.

Submit button (primary, full width on mobile): "Ask HalloTermin to call". While sending: spinner + "Sending your request...". Insert exactly like this (generate the id on the client so we don't need to read the row back):

  const id = crypto.randomUUID();
  const { error } = await supabase.from("call_requests").insert({
    id,
    patient_name, patient_dob: patient_dob || null,
    insurance_type, insurance_name: insurance_name || null,
    user_email, user_language: "en",
    practice_name, practice_phone,
    reason_category, has_referral, is_new_patient,
    time_windows: windows.map(w => ({ date: w.date, from: w.from, to: w.to })), // real array, not JSON.stringify
    consent_ai_call: true,
  });
  if (!error) navigate(`/r/${id}`);

Do not send status, consent_at, call_brief_de, created_at or updated_at. On error show a brick-coloured panel above the button: "We couldn't send your request. Please try again." plus the error message in small muted text, and keep all entered values.
```

**Check it worked:** submit with demo details and your own phone number. You land on `/r/<uuid>`, the row appears in the Supabase Table Editor with `time_windows` as a JSON array (not a string), and within about 10–40 s n8n sets `status = 'briefed'` and fills `call_brief_de`. Submitting an empty form shows inline errors, and focus jumps to the first one.

---

### P3: Status page `/r/:id` with stepper, German brief and "behind the scenes" log

**Goal:** the page loads the request, then follows it live via Realtime. It must survive a page refresh at any status.

```text
Build the status page /r/:id. Read-only. Do NOT create or change tables.

Data:
- Load the request: supabase.from("call_requests").select("*").eq("id", id).maybeSingle(). If null, show "We can't find this request." with a link to /new. Show a quiet skeleton while loading (no shimmer on real content).
- Subscribe to live changes. Use this pattern and always remove the channel on unmount:

  useEffect(() => {
    const ch = supabase
      .channel(`req-${id}`)
      .on("postgres_changes",
          { event: "UPDATE", schema: "public", table: "call_requests", filter: `id=eq.${id}` },
          (p) => setRequest(p.new as CallRequest))
      .on("postgres_changes",
          { event: "INSERT", schema: "public", table: "events", filter: `request_id=eq.${id}` },
          (p) => setEvents(prev => prev.some(e => e.id === p.new.id) ? prev : [...prev, p.new as EventRow]))
      .subscribe((status) => { if (status === "SUBSCRIBED") refetchAll(); }); // refetch once to close the gap between first load and subscribe
    return () => { supabase.removeChannel(ch); };
  }, [id]);

- Load events once: from("events").select("*").eq("request_id", id).order("id").

Layout (asymmetric): on desktop, two columns: a narrow left column (about 20rem, sticky top) and a wide right column (max 42rem). On mobile, one column: stepper first.

Left column:
1. Status stepper as an ordered list (<ol>), vertical, 4 steps with states complete / current / upcoming, each with a lucide icon + text (colour is never the only signal):
   1 "Request received" (status submitted)
   2 "Call brief ready" (briefed)
   3 "Calling the practice" (calling). When current: an amber dot that pulses (opacity only; no pulse under reduced motion) + text "Live now".
   4 Result, label depends on status: booked "Appointment booked" (pine, check icon); needs_user "We need your answer" (amber-text, message icon); rejected "The practice said no" (brick, x icon); failed "The call didn't go through" (brick, phone-off icon); otherwise "Result" (upcoming).
   Derive the stepper ONLY from request.status (never from local state), so a refresh shows the right step. Wrap the current step label in an aria-live="polite" region so screen readers hear changes.
2. "Your request" summary as a definition list (<dl>): Practice (name + phone), Appointment type (English label of reason_category), Patient (name, date of birth en-GB), Insurance (Public/Private/Other + name), New patient (Yes/No), Referral (Yes/No), Your times (each window as "Tue 29 Sep, 08:00-12:00"), Result goes to (email). Show dates with timeZone "Europe/Berlin", locale en-GB.

Right column:
1. A short status sentence at the top in Fraunces 26px that changes with status: submitted "We're preparing the call."; briefed "The call brief is ready. The call starts soon."; calling "Our assistant is on the phone with the practice."; booked "Your appointment is booked."; needs_user "The practice asked something only you can answer."; rejected "The practice couldn't give you an appointment."; failed "We couldn't reach the practice."
2. Panel "What our assistant will say (German)": when call_brief_de is null show "Writing the brief..." in muted text; otherwise show call_brief_de in the .de serif style inside a card. Under it, in muted English: "This German brief uses only the details you entered (listed on the left). No symptoms." and a separate line with an info icon: "The assistant starts every call with: 'Hier spricht die KI-Assistentin von [name]' (This is [name]'s AI assistant). It never pretends to be you."
3. Leave an empty section with id="call" and the heading "The call" and muted text "The live transcript appears here when the call starts." (we fill it in the next step).
4. Collapsible section "Behind the scenes" (closed by default, a <details> element): the events list as a compact <ol> timeline: time (HH:mm:ss, Europe/Berlin, tabular numbers), a small source tag (app / n8n / voice / system, neutral outline badge), and a friendly label: request_submitted "Request saved", brief_created "German call brief written", call_started "Call started", call_ended "Call ended", email_sent "Confirmation email sent"; any other type: replace underscores with spaces.
Set document.title to "Request status - HalloTermin".
```

**Check it worked:** open a fresh request's page. In the Supabase SQL editor run `update call_requests set status='calling' where id='<ID>';` and the stepper moves to "Calling" with the amber dot, **without a reload**. Refresh the page and it stays on "Calling". `/r/0000…0001` shows "Appointment booked" and five events under "Behind the scenes".

---

### P4: Live transcript (German line + English subtitle)

**Goal:** show the latest call's transcript as a script that grows while the call runs.

```text
On /r/:id, fill the section id="call" with a live transcript. Read-only. Do NOT create or change tables.

Data:
- Latest call for this request: from("calls").select("*").eq("request_id", id).order("created_at", { ascending: false }).limit(1).maybeSingle().
- Lines for that call: from("transcript_lines").select("*").eq("call_id", call.id).order("id").
- Realtime (add to the page, remove on unmount):
  * calls: event "*" with filter `request_id=eq.${id}`. On INSERT, switch to the new call (it's a new attempt) and clear the lines. On UPDATE of the current call, replace the call object.
  * transcript_lines: a separate channel created when call.id is known, event "INSERT", filter `call_id=eq.${call.id}`. Append the line if its id isn't already in the list, keep the list sorted by id. Recreate this channel when call.id changes; always supabase.removeChannel the old one.
  * On subscribe status "SUBSCRIBED", refetch the lines once (to close the gap).

Display, as a script and not as chat bubbles:
- Container: card, role="log", aria-live="polite", aria-label "Call transcript".
- Each line is a row with two parts: a left speaker column (7rem on desktop; on mobile the speaker label sits above the text) and the text.
  * speaker 'practice': label "Practice", ink text, no background.
  * speaker 'agent': label "AI assistant" with a small bot icon, the row has the pine-tint background and 6px radius.
  * speaker 'system': no speaker column; one centered small muted italic line (e.g. "Call connected").
  * text_de in the .de style (Fraunces, 19px, ink), lang="de". Under it text_en in Source Sans 15px muted colour, lang="en". If text_en is null, show "Translating..." in muted italic, and replace it when an UPDATE arrives (also subscribe to transcript_lines UPDATE with the same filter).
  * Right-aligned small tabular time HH:mm:ss (Europe/Berlin) from created_at.
- New lines enter with 200ms opacity + 4px translate (none under reduced motion). Auto-scroll to the newest line only if the user is already near the bottom; otherwise show a small "New lines below" button.
- Header of the section: "The call" + when call.started_at exists and ended_at is null: amber live dot + "Live" and a running duration mm:ss; when ended_at exists: "Call ended, lasted m:ss".
- States: no call yet -> keep the muted text "The live transcript appears here when the call starts."; call exists but 0 lines -> "Connecting to the practice..."
- Under the transcript, a one-line muted note with a lock icon: "Text only. We never record audio."
```

**Check it worked:** `/r/0000…0001` shows 7 lines, alternating Practice and AI assistant, with the German serif line above the English grey line. To test live: in the SQL editor, `insert into calls (request_id, provider, started_at) values ('<ID>','mock',now()) returning id;` then `insert into transcript_lines (call_id, speaker, text_de, text_en) values ('<CALL_ID>','practice','Praxis Dr. Weber, guten Tag?','Dr. Weber''s practice, hello?');`. The line appears without a reload.

---

### P5: Result card + "Add to my calendar" (.ics)

**Goal:** when the call ends, give the user one clear answer: what was booked, when, what to bring, and a calendar file.

```text
On /r/:id, add a result card in the right column, directly below the status sentence and above the German brief panel. It shows only when the latest call has an outcome or request.status is booked, needs_user, rejected or failed. Use the call data already loaded in the page (live via Realtime). Do NOT create or change tables.

Variants:
- booked (outcome 'booked'): the only card in the app with the soft shadow. Big line in Fraunces 33px: booked_slot formatted "Tuesday 29 September, 08:15" (timeZone Europe/Berlin, en-GB), second line: practice_name + practice_phone. Section "Bring with you": each bring_items entry as a list row with a check icon, the German word in .de style plus the English meaning in muted text. Use this map, and show the raw word if it's not listed: Versichertenkarte "health insurance card", eGK "health insurance card", Überweisung "referral letter", Impfpass "vaccination record", Medikamentenliste "list of your medicines", Personalausweis/Reisepass "ID or passport". Then summary_en as a paragraph. Primary button "Add to my calendar", and a text link "Start another request" -> /new.
- needs_user: amber-tint panel, amber-text heading "The practice asked something only you can answer", summary_en as the explanation (fallback: "We sent you an email with the details."), link "Start a new request".
- rejected / outcome 'rejected_no_new_patients': brick-tint panel, heading "This practice isn't taking new patients" (for other rejections: "The practice couldn't give you an appointment"), summary_en, link "Try a different practice" -> /new.
- failed / outcome 'no_answer' | 'voicemail' | 'failed': brick-tint panel, heading "No answer" | "We reached the voicemail" | "The call didn't go through", summary_en if present, link "Try again" -> /new. Never show call.error to the user.

"Add to my calendar": generate an .ics file in the browser (no server) and download it as hallotermin-appointment.ics:
  BEGIN:VCALENDAR / VERSION:2.0 / PRODID:-//HalloTermin//EN / CALSCALE:GREGORIAN / METHOD:PUBLISH
  BEGIN:VEVENT
  UID:<request.id>@hallotermin
  DTSTAMP:<now in UTC, format YYYYMMDDTHHMMSSZ>
  DTSTART:<booked_slot in UTC, format YYYYMMDDTHHMMSSZ>
  DTEND:<booked_slot + 30 minutes, same format>
  SUMMARY:Doctor appointment - <practice_name>
  LOCATION:<practice_name>
  DESCRIPTION:Bring: <bring_items joined with comma + English meanings>. Phone: <practice_phone>. Booked by HalloTermin.
  END:VEVENT / END:VCALENDAR
Use CRLF line endings, escape commas, semicolons and backslashes in text values (\, \; \\) and newlines as \n. Download via a Blob with type "text/calendar;charset=utf-8" and a temporary <a download>.
```

**Check it worked:** on `/r/0000…0001` the card says "Tuesday 29 September, 08:15" (not 06:15, which would mean a timezone bug) and lists "Versichertenkarte – health insurance card". The downloaded .ics opens in Google/Apple/Outlook Calendar at 08:15 Berlin time.

---

### P6: Landing page (the 30-second pitch as a page)

**Goal:** the jury understands the problem and the product in one scroll, and can open the demo call in one click.

```text
Build the landing page on /. Follow the banned list strictly. Each section uses a different layout; vary section padding (hero larger, others smaller). No stock images, no illustrations, no testimonials, no logos.

1. Hero, asymmetric split (text 7/12 left, product excerpt 5/12 right; stacked on mobile, text first):
   - H1 (Fraunces 52px desktop / 36px mobile): "We call the doctor in German, so you don't have to."
   - Subline (21px, max 34rem): "Tell us in English which practice and which times work for you. Our AI assistant phones the practice, books a time inside your windows and shows you the whole call with English subtitles."
   - One primary button "Book a doctor's appointment" -> /new, and next to it a text link with arrow icon "See a finished demo call" -> /demo.
   - Right side: a static excerpt of the real transcript component (reuse the transcript row styling from /r/:id) showing these 3 lines from the demo call, with a small caption "From our demo call":
     practice: "Praxis Dr. Weber, guten Tag?" / "Dr. Weber's practice, hello?"
     agent: "Guten Tag, hier spricht die KI-Assistentin von Frau Priya Sharma. Sie spricht leider noch kein Deutsch, deshalb rufe ich in ihrem Auftrag an." / "Hello, this is Ms Priya Sharma's AI assistant. She doesn't speak German yet, so I'm calling on her behalf."
     practice: "Dienstag, 8:15 Uhr?" / "Tuesday, 8:15?"
2. The problem, a narrow text column (max 40rem) with one large number line: "About 402,000 international students study in Germany. Many practices still book only by phone." Paragraph: "The receptionist has 30 seconds and speaks fast. Words like Überweisung (referral) and Versichertenkarte (insurance card) come up. Many newcomers freeze, hang up, or wait for a German friend to call for them." Tiny source line in muted text: "Source: DAAD/DZHW, Wissenschaft weltoffen 2025 (winter semester 2024/25)."
3. How it works: a numbered ordered list with 4 steps laid out horizontally on desktop (connected by a thin line, not cards), vertical on mobile:
   1 "You fill in one form in English" (who, which practice, when you're free; about 1 minute)
   2 "We prepare a German call brief" (only what the practice needs, never symptoms)
   3 "Our assistant calls and says it's an AI" (it books only inside your times and reads the time back before confirming)
   4 "You get the result" (time, what to bring, a calendar file)
4. "What we never do": a two-column definition list on a pine-tint full-width band (the one full-bleed break on the page):
   "Record your call" - We keep a text transcript only. No audio is stored.
   "Ask about symptoms" - The practice only needs the type of appointment.
   "Pretend to be you" - The assistant says it is an AI calling on your behalf, in its first sentence.
   "Book a time you didn't approve" - Anything outside your windows comes back to you first.
5. Closing CTA, left-aligned, small: heading "Try it with a demo practice" + text "Watch a finished call from start to booking." + primary button "See a finished demo call" -> /demo + text link "Or start your own request" -> /new.
Set document.title "HalloTermin - we call the doctor in German for you" and a meta description with the same subline.
```

**Check it worked:** at 375px width the hero reads top to bottom with no horizontal scroll. There is exactly one filled button per section, and there are no cards in a 3-column grid. "See a finished demo call" opens the booked demo request.

---

### P7: Polish and accessibility pass

**Goal:** make it demo-proof. No new features.

```text
Polish and accessibility pass across all pages. No new features, no schema changes, keep the design system.
1. Keyboard: every control reachable in order; visible pine focus ring everywhere; add a "Skip to content" link as the first focusable element.
2. Semantics: one H1 per page, correct heading order, <main>, <nav>, <footer>; form fields all have labels; icon-only buttons have aria-label; decorative icons aria-hidden.
3. Touch targets at least 44x44px (radio rows, "Remove" buttons, "Add another time", links in the stepper).
4. Contrast: body text only in ink or ink-muted; placeholder text at least #5B635E; no text on amber except ink.
5. Motion: confirm every transition and the live pulse stop under prefers-reduced-motion; remove any transition-all, hover:scale, or animation longer than 300ms.
6. Responsiveness: test 375px, 768px, 1280px; no horizontal scrolling; the status page stacks with the stepper first on mobile; the transcript speaker column collapses above the text on mobile.
7. States: loading skeletons on /r/:id, the not-found state for unknown ids, and a friendly message if Realtime disconnects ("Live updates paused. Reconnecting...") that clears itself when the channel is SUBSCRIBED again.
8. Language attributes: html lang="en"; every German text element has lang="de".
9. Copy check: remove any "Get started", "Learn more", exclamation marks, emoji, lorem ipsum, or placeholder text you find.
10. Favicon: a simple SVG with a pine "H" in Fraunces on paper colour. Page titles per route.
Report back a short list of what you changed.
```

**Check it worked:** Lighthouse (Chrome DevTools) Accessibility ≥ 95 on `/`, `/new` and `/r/0000…0001`. Tab through `/new` without a mouse and submit. Set Windows to "reduce animations" (Settings → Accessibility → Visual effects → Animation effects off) and the live dot stops pulsing.

---

### Free test script: simulate n8n in the Supabase SQL editor

Use this to test P3–P5 without the voice pipeline. Replace `<ID>` with a request id; after step 2, copy the returned call id into `<CALL_ID>`.

```sql
-- 1) brief ready
update call_requests set status='briefed',
  call_brief_de='Termin für eine Erstuntersuchung, Neupatientin, gesetzlich versichert (TK), keine Überweisung.'
where id='<ID>';
-- 2) call starts
insert into calls (request_id, provider, started_at) values ('<ID>','mock', now()) returning id;
update call_requests set status='calling' where id='<ID>';
-- 3) lines stream in (run one at a time to watch them appear)
insert into transcript_lines (call_id, speaker, text_de, text_en) values
 ('<CALL_ID>','practice','Praxis Dr. Weber, guten Tag?','Dr. Weber''s practice, hello?');
insert into transcript_lines (call_id, speaker, text_de) values
 ('<CALL_ID>','agent','Guten Tag, hier spricht die KI-Assistentin von Frau Priya Sharma.');  -- tests "Translating..."
-- 4) result
update calls set ended_at=now(), outcome='booked', booked_slot='2026-09-29 08:15+02',
  bring_items=array['Versichertenkarte'], summary_en='Booked: Tue 29 Sep, 08:15 with Dr. Weber. Bring your insurance card.'
where id='<CALL_ID>';
update call_requests set status='booked' where id='<ID>';
```

(The SQL editor bypasses RLS, so this only tests the *display*. The insert test in P2 must be done from the app itself; see [[RLS - test inserts as anon]].)

---

## 4. Credit-saving tips

1. **Knowledge first, then prompts.** Rules in Knowledge are free and apply to every prompt, so you don't have to repeat them.
2. **One prompt = one step above.** Don't chat with the Agent. Use **Chat mode** for questions like "why is X happening?" (cheaper), and switch to Agent only to build.
3. **Check with the SQL test script, not with prompts.** Simulating statuses in the Supabase SQL editor costs nothing.
4. **Small text or colour fixes:** use Lovable's Visual Edits, or edit the file in the GitHub repo (or ask Claude Code on the synced repo) and push. Both are free or near free.
5. **Undo through History (restore a version), not by asking "undo that".** Restoring costs nothing.
6. **Two strikes rule:** if Lovable fails to fix the same error twice, stop. Copy the error and fix it in the repo with Claude Code.
7. **Attach a screenshot** for visual problems ("the stepper overlaps the transcript at 375px"). It works better than long descriptions.
8. **One driver.** Only one of us prompts Lovable at a time, and accepts drafts, so we don't pay for conflicting changes.
9. **Publish often** (Publish → Update). It costs no credits, and the demo URL goes stale if you forget.

## 5. If Lovable does X, reply with Y

| Lovable does… | Reply (copy-paste) |
|---|---|
| Offers "Enable Cloud" / Lovable Cloud / "set up a backend" | Don't click it. "No. We use our own connected Supabase project ycyrtlzympxzlfcocazh. Don't enable Lovable Cloud." |
| Proposes a migration, `create table`, new policy or enum | **Reject the migration dialog.** "The tables, enums and RLS policies already exist in the connected Supabase project and are managed in a separate repo. Don't create migrations. Use the existing tables from src/integrations/supabase/types.ts and the data contract in Knowledge." |
| Types file doesn't know our tables (TS errors like `"call_requests" not assignable`) | "Refresh the Supabase types from the connected project; don't create tables." Free fallback: locally run `npx supabase gen types typescript --project-id ycyrtlzympxzlfcocazh > src/integrations/supabase/types.ts` in the Lovable repo and push. |
| Adds login/signup, an auth page or a profiles table | "Remove authentication. This demo has no accounts; requests are viewed by link." |
| Creates an Edge Function or calls an n8n webhook from the browser | "Remove it. A database trigger already sends new call_requests rows to n8n. The browser only inserts and reads." |
| Insert fails with `42501 new row violates row-level security policy` | "The insert must send consent_ai_call: true and use the anon client from @/integrations/supabase/client. Don't change policies." (Also check that the form isn't sending `status`.) |
| Insert fails with `23514 ... violates check constraint` | "Send the lowercase values, not labels: reason_category in first_visit/checkup/acute/follow_up/specialist/other, insurance_type in gkv/pkv/other." |
| `time_windows` shows as a string `"[{...}]"` in the table | "Send time_windows as a JavaScript array of {date, from, to} objects, not JSON.stringify." |
| Realtime doesn't update the page | "Use supabase.channel(...).on('postgres_changes', { event, schema:'public', table, filter:`id=eq.${id}` }, ...).subscribe(); create it in useEffect with [id] and call supabase.removeChannel on cleanup. Don't add polling." Then test with the SQL `update` from P3. |
| Times are 2 hours off | "Format all timestamps with timeZone 'Europe/Berlin', locale 'en-GB'. For the .ics use UTC with a trailing Z." |
| Stepper is wrong after refresh | "Derive the stepper only from request.status loaded from the database, not from local state." |
| Adds a "notes", "symptoms" or "message to the doctor" field | "Remove it. We never collect free-text health information (GDPR Art. 9). Reason is a category only." |
| Drifts to purple, Inter, gradients, glass cards, a 3-card grid or emoji | "That breaks the design bans in Knowledge. Revert to the Bilingual paper tokens: pine #1F5C4A on paper #F7F4EC, Fraunces + Source Sans 3, flat surfaces." |
| Adds an audio player, "listen to the call" or a recording upload | "Remove it. We never store or play audio (§201 StGB). Text transcript only." |
| Writes hype copy ("Seamlessly book in seconds!") | "Rewrite in plain B1 English, calm, no exclamation marks, no hype words. Say concretely what happens." |
| Wants to "improve" the schema (add a column) | "No schema changes from Lovable. Tell me what you need in chat and we'll add it by migration in our repo." Then add it via `npx supabase migration new …`. |

**Related:** [[Lovable - Practical Guide]] · [[Supabase - Practical Guide]] · [[Data Model]] · [[Personas]] · [[Moment of Truth - First 15 Seconds]] · [[Glossary - German Healthcare Terms]] · [[AI Disclosure]] · [[Decide Lovable backend before first prompt]] · [[Never put service keys in frontend]] · [[Data minimisation - no symptoms]]
