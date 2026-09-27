// Screenshots of the LIVE app for the launch deck and videos.
// Usage (from the repo root):  node scripts/launch/shoot_screens.mjs [--only=home,provider] [--no-approval] [--approval-only]
// Output: docs/launch/assets/screens/*.png + manifest.json (merged with an existing manifest on partial runs).
// Headless Chrome via puppeteer-core (installed in the scratch tools folder, override with LAUNCH_TOOLS=<path to package.json>).
// Safety: the approval step calls the n8n intake at most twice and never ticks consent or creates a call request
// (POSTs to call_requests are aborted by request interception as a second guard).
import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const TOOLS =
  process.env.LAUNCH_TOOLS ||
  "C:/Users/a_rahman/AppData/Local/Temp/claude/C--Users-a-rahman-Desktop-Automation-Weekender-Build/bc0649a2-1b68-40fd-bce5-cd66ad9c3d51/scratchpad/tools/package.json";
const require = createRequire(TOOLS);
const puppeteer = require("puppeteer-core");

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const OUT = path.join(ROOT, "docs/launch/assets/screens");
const CHROME = process.env.CHROME_PATH || "C:/Program Files/Google/Chrome/Application/chrome.exe";
const HOST = "ankommen-dresden.lovable.app";
const BASE = `https://${HOST}`;
const PROVIDER = "ae0ae23b-0dd7-4f82-adf8-6fd78aa3456d";
const RESULT = "fb99c45e-660b-4882-affa-1a71505f8f02";
const ASK = `/ask?resource=${PROVIDER}&type=course_enquiry`;
const MAX_FULL = 6000; // css px cap for full-page captures
const INTAKE_TEXT = "Хочу записать дочку на музыку. Ей четыре года. Лучше во вторник или в четверг после трёх.";
const MAX_INTAKE_POSTS = 2;

const STRINGS = JSON.parse(fs.readFileSync(path.join(ROOT, "docs/i18n/ui-strings.json"), "utf-8"));
const t = (lang, key) => key.split(".").reduce((o, k) => (o && typeof o === "object" ? o[k] : undefined), STRINGS[lang]) ?? "";

const args = process.argv.slice(2);
const only = (args.find((a) => a.startsWith("--only=")) || "").slice(7).split(",").filter(Boolean);
const noApproval = args.includes("--no-approval");
const approvalOnly = args.includes("--approval-only");

const VIEW = {
  desktop: { width: 1440, height: 900, deviceScaleFactor: 2 },
  full: { width: 1440, height: 900, deviceScaleFactor: 2 },
  crop: { width: 1440, height: 900, deviceScaleFactor: 2 },
  mobile: { width: 390, height: 844, deviceScaleFactor: 2, isMobile: true, hasTouch: true },
};

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const log = (...a) => console.log(...a.map((x) => (typeof x === "string" ? x.replace(/[^\x20-\x7E]/g, "?") : x)));

// ---------- page helpers ----------
async function openPage(browser, kind, lang) {
  const ctx = await browser.createBrowserContext();
  const page = await ctx.newPage();
  await page.setViewport(VIEW[kind]);
  await page.emulateMediaFeatures([{ name: "prefers-reduced-motion", value: "reduce" }]);
  await page.setCookie({ name: "dmk_ui_lang", value: lang, domain: HOST, path: "/" });
  page.setDefaultTimeout(30000);
  return { ctx, page };
}

async function settle(page, ms = 1500) {
  try {
    await page.waitForNetworkIdle({ idleTime: 600, timeout: 15000 });
  } catch {}
  await page.evaluate(() => document.fonts.ready.then(() => true));
  await sleep(ms);
}

async function go(page, route) {
  await page.goto(BASE + route, { waitUntil: "networkidle2", timeout: 60000 });
  await settle(page);
}

async function scrollThrough(page) {
  await page.evaluate(async () => {
    const step = Math.round(window.innerHeight * 0.8);
    for (let y = 0; y < document.documentElement.scrollHeight; y += step) {
      window.scrollTo(0, y);
      await new Promise((r) => setTimeout(r, 180));
    }
    window.scrollTo(0, document.documentElement.scrollHeight);
    await new Promise((r) => setTimeout(r, 400));
    window.scrollTo(0, 0);
  });
  await settle(page, 800);
}

async function pageInfo(page, lang) {
  const info = await page.evaluate(() => ({
    htmlLang: document.documentElement.lang,
    dir: document.documentElement.dir || getComputedStyle(document.documentElement).direction,
    title: document.title,
    h1: document.querySelector("main h1, h1")?.textContent?.trim() ?? "",
    url: location.href,
  }));
  const bad = ["common.notFoundTitle", "provider.notFound", "call.notFound", "errors.loadFailed", "directory.error"]
    .map((k) => t(lang, k))
    .filter(Boolean);
  info.errorPage = bad.some((b) => info.h1 === b) || /404|not found/i.test(info.title);
  info.langOk = info.htmlLang.startsWith(lang) && (lang === "ar" ? info.dir === "rtl" : info.dir !== "rtl");
  return info;
}

/** Document-coordinate box of the element picked by fn (runs in the page), padded; null if not found/invisible. */
async function boxOf(page, fn, pad = 16) {
  const handle = await page.evaluateHandle(fn); // no eval inside the page (CSP-safe)
  const box = await page.evaluate(
    (el, pad) => {
      if (!el) return null;
      const els = Array.isArray(el) ? el : [el];
      let x1 = Infinity, y1 = Infinity, x2 = -Infinity, y2 = -Infinity;
      for (const e of els) {
        const r = e.getBoundingClientRect();
        if (r.width < 2 || r.height < 2) continue;
        x1 = Math.min(x1, r.left); y1 = Math.min(y1, r.top); x2 = Math.max(x2, r.right); y2 = Math.max(y2, r.bottom);
      }
      if (!isFinite(x1)) return null;
      const sx = window.scrollX, sy = window.scrollY, W = document.documentElement.scrollWidth;
      const x = Math.max(0, x1 - pad + sx), y = Math.max(0, y1 - pad + sy);
      return { x, y, width: Math.min(W - x, x2 - x1 + pad * 2), height: y2 - y1 + pad * 2 };
    },
    handle,
    pad,
  );
  await handle.dispose();
  return box;
}

// ---------- blank check (pixel variance on a downscaled copy, in a tiny canvas page) ----------
let checker;
async function variance(buf) {
  const b64 = Buffer.from(buf).toString("base64");
  return checker.evaluate(async (b64) => {
    const img = new Image();
    img.src = "data:image/png;base64," + b64;
    await img.decode();
    const w = 160, h = Math.max(1, Math.round((160 * img.height) / img.width));
    const c = document.createElement("canvas");
    c.width = w; c.height = h;
    const g = c.getContext("2d");
    g.drawImage(img, 0, 0, w, h);
    const d = g.getImageData(0, 0, w, h).data;
    let s = 0, s2 = 0, n = 0;
    const colors = new Set();
    for (let i = 0; i < d.length; i += 4) {
      const l = 0.2126 * d[i] + 0.7152 * d[i + 1] + 0.0722 * d[i + 2];
      s += l; s2 += l * l; n++;
      colors.add(((d[i] >> 4) << 8) | ((d[i + 1] >> 4) << 4) | (d[i + 2] >> 4));
    }
    const mean = s / n;
    return { std: Math.sqrt(Math.max(0, s2 / n - mean * mean)), colors: colors.size, px: [img.width, img.height] };
  }, b64);
}

// ---------- recording ----------
const manifest = [];
const problems = [];

async function save(page, entry, opts = {}) {
  const file = entry.file;
  const buf = await page.screenshot({ type: "png", ...opts });
  fs.writeFileSync(path.join(OUT, file), buf);
  const v = await variance(buf);
  const kb = Math.round(buf.length / 1024);
  const blank = v.std < 4 || v.colors < 6;
  const item = {
    file,
    kind: entry.kind,
    route: entry.route,
    lang: entry.lang,
    css_width: Math.round(v.px[0] / 2),
    css_height: Math.round(v.px[1] / 2),
    scale: 2,
    shows: entry.shows,
  };
  const i = manifest.findIndex((m) => m.file === file);
  if (i >= 0) manifest[i] = item;
  else manifest.push(item);
  const flag = blank ? " BLANK?" : kb < 30 ? " SMALL" : "";
  if (blank) problems.push(`${file}: looks blank (std ${v.std.toFixed(1)})`);
  log(`  saved ${file} ${v.px[0]}x${v.px[1]} ${kb}KB std=${v.std.toFixed(1)} colors=${v.colors}${flag}`);
  return item;
}

function want(name) {
  if (approvalOnly) return false;
  return !only.length || only.some((o) => name.includes(o));
}

// ---------- shot definitions ----------
const LANG_NAME = { en: "English", de: "German", ru: "Russian", uk: "Ukrainian", ar: "Arabic (RTL)", tr: "Turkish" };

const COURSES_FILTERED = "/courses?age=3-6&act=music&lang=ru";

function shots() {
  const list = [];
  const add = (kind, page, lang, route, shows, extra = {}) =>
    list.push({ kind, page, lang, route, shows, file: `${kind}-${page}-${lang}.png`, ...extra });

  const fab = (l) => (l === "ar" ? "bottom-left" : "bottom-right");
  for (const l of ["ru", "en", "de", "ar", "uk", "tr"])
    add("desktop", "home", l, "/", `Home page in ${LANG_NAME[l]}: header with wordmark and nav, hero headline 'Courses, events and help for your family in Dresden', two buttons (browse courses, upcoming events), age card with a bar chart of courses per age (22 for age 4); round Call-for-me mic button ${fab(l)}.`);
  add("desktop", "courses", "ru", COURSES_FILTERED, "Courses page in Russian filtered to age 3-6, music and Russian: active filter chips, result count and the matching listings (Musikschule Adagio, Olgas Musikstudio with the 'checked by phone' badge at the bottom edge).", { fallback: "/courses?age=3-6&act=music" });
  add("desktop", "courses-all", "ru", "/courses", "Courses and activities page in Russian, unfiltered: view switch (all / courses / places), age buttons, filter dropdowns and the first listings.");
  for (const l of ["ru", "en", "ar"])
    add("desktop", "provider", l, `/p/${PROVIDER}`, `Olgas Musikstudio provider page (marked as demo listing) in ${LANG_NAME[l]}: German name, description, offer table (age 3-6, music, languages, format, price, address); Call-for-me box ${l === "ar" ? "on the left" : "on the right"} with 3 steps and the button to ask about a free place or trial lesson.`);
  add("desktop", "ask", "ru", ASK, "Call-for-me page in Russian for Olgas Musikstudio: 4-step progress bar, 'where we will call' card with name and phone, title 'Find out about a free place or trial lesson', voice start button.");
  for (const l of ["ru", "en"])
    add("desktop", "result", l, `/r/${RESULT}`, `Result page of the real end-to-end test call (RUN-026) in ${LANG_NAME[l]}: 4-step stepper done, 'your task' column (goal, time windows, allowed facts), result card 'booked for a trial lesson, Thursday 1 October at 14:00' with summary, things to bring (German + translation) and details.`);
  add("desktop", "events", "ru", "/events", "Events page in Russian: 'Family events in the next 5 weeks', age and language filters, 'free only', 29 events, this week's list with date blocks and 'today' marks.");
  add("desktop", "communities", "ru", "/communities", "Bilingual communities page in Russian: language chips with counts (Russian 6, Arabic 4, Ukrainian 5 ...), Russian-speaking groups listed first, each with a Call-for-me link.");
  add("desktop", "services", "ru", "/services", "Health and services page in Russian: category buttons (Kita and school, doctors, pharmacies, authorities, banks, counselling), name search, district filter, 94 places.");
  add("desktop", "library", "ru", "/library", "Library (guides) page in Russian: guides grouped by topic (Kita and school, documents and registration), each with summary, update date and a Call-for-me link.");
  for (const l of ["ru", "ar"])
    add("desktop", "guide-kita", l, "/guides/kita-place-dresden", `Guide 'Finding a Kita place in Dresden: Kita-Portal, waiting list and costs' in ${LANG_NAME[l]}: title, summary, update date, checklist '0 of 10 done', related guides column.`);

  add("full", "home", "ru", "/", "Full home page in Russian, top to footer: hero with age chart, 'what is here' pillars with counts, this week's events, guides, footer.", { full: true });
  add("full", "provider", "ru", `/p/${PROVIDER}`, "Full Olgas Musikstudio page in Russian: description, offer table, 'checked by phone 26 Sep 2026 - booked' badge, Call-for-me box with contact.", { full: true });
  add("full", "result", "ru", `/r/${RESULT}`, "Full result page in Russian with the call expanded: result card (Thu 1 Oct 14:00), call card (1:38, 'said it is an AI at the start') and the German transcript with Russian lines (the list scrolls inside its box, so only the later lines show).", { full: true, expandCall: true });

  add("mobile", "home", "ru", "/", "Home page on a phone (390 px) in Russian: hero headline, two buttons, top of the age card; round Call-for-me mic button bottom-right.");
  add("mobile", "provider", "ru", `/p/${PROVIDER}`, "Olgas Musikstudio page on a phone in Russian: name, demo-listing mark, description and the Call-for-me box in the page flow.");
  add("mobile", "result", "ru", `/r/${RESULT}`, "Result page on a phone in Russian, top: title 'Live call', 4-step stepper done, 'your task' summary (goal, time windows, allowed facts); the booked result card is further down, see mobile-result-card-ru.");
  add("mobile", "result-card", "ru", `/r/${RESULT}`, "Result page on a phone in Russian scrolled to the result card: 'booked for a trial lesson, Thursday 1 October at 14:00', summary and things to bring.", { scrollTo: () => document.querySelector("div.min-w-0.space-y-6 > section") });
  add("mobile", "home", "ar", "/", "Home page on a phone in Arabic, right-to-left: headline, buttons, age card; Call-for-me mic button bottom-left.");
  add("mobile", "ask", "ru", ASK, "Call-for-me page on a phone in Russian: step 1 of 4, 'where we will call' card, title, big round 'Speak' mic button.");
  return list;
}

// Element crops: [file, route, lang, picker(arg) run in page, shows, prep]
const CROPS = [
  {
    file: "crop-wordmark-ru.png", route: "/", lang: "ru", pad: 12,
    pick: () => document.querySelector("header a[href='/']"),
    shows: "Header wordmark 'Ankommen' ('An' ink + 'kommen' pine) with the tagline, Russian UI.",
  },
  {
    file: "crop-fab-ru.png", route: "/", lang: "ru", pad: 20, hover: "a.fixed.rounded-full",
    pick: () => { const a = document.querySelector("a.fixed.rounded-full"); return a ? [a, a.querySelector("span")] : null; },
    shows: "Floating Call-for-me button (pine disc with microphone) with its hover label in Russian.",
  },
  {
    file: "crop-fab-en.png", route: "/", lang: "en", pad: 20, hover: "a.fixed.rounded-full",
    pick: () => { const a = document.querySelector("a.fixed.rounded-full"); return a ? [a, a.querySelector("span")] : null; },
    shows: "Floating Call-for-me button with its hover label 'Call for me' in English.",
  },
  {
    file: "crop-askbox-ru.png", route: `/p/${PROVIDER}`, lang: "ru", pad: 12,
    pick: () => [...document.querySelectorAll("aside")].find((a) => a.offsetParent !== null),
    shows: "Call-for-me box on the Olgas Musikstudio page in Russian: 'We can call there for you', AI says it is an AI, three steps, pine button 'Find out about a free place or trial lesson', contact phone.",
  },
  {
    file: "crop-askbox-en.png", route: `/p/${PROVIDER}`, lang: "en", pad: 12,
    pick: () => [...document.querySelectorAll("aside")].find((a) => a.offsetParent !== null),
    shows: "Call-for-me box on the Olgas Musikstudio page in English: title, three steps, pine button, contact phone.",
  },
  {
    file: "crop-checked-ru.png", route: `/p/${PROVIDER}`, lang: "ru", pad: 10,
    pick: () => [...document.querySelectorAll("article span.bg-secondary")].find((s) => s.querySelector("button")),
    shows: "'Checked by phone' badge on the Olgas Musikstudio page in Russian: 'checked by phone 26 September 2026 - booked' with info icon.",
  },
  {
    file: "crop-checked-en.png", route: `/p/${PROVIDER}`, lang: "en", pad: 10,
    pick: () => [...document.querySelectorAll("article span.bg-secondary")].find((s) => s.querySelector("button")),
    shows: "'Checked by phone' badge on the Olgas Musikstudio page in English.",
  },
  {
    file: "crop-resultcard-ru.png", route: `/r/${RESULT}`, lang: "ru", pad: 12,
    pick: () => document.querySelector("div.min-w-0.space-y-6 > section"),
    shows: "Result card of the test call in Russian: 'booked for a trial lesson', Thursday 1 October at 14:00, summary, things to bring (German + Russian), details table, add-to-calendar button.",
  },
  {
    file: "crop-resultcard-en.png", route: `/r/${RESULT}`, lang: "en", pad: 12,
    pick: () => document.querySelector("div.min-w-0.space-y-6 > section"),
    shows: "Result card of the test call in English: booked trial lesson Thursday 1 October at 14:00, summary, things to bring, details, add-to-calendar button.",
  },
  {
    file: "crop-transcript-ru.png", route: `/r/${RESULT}`, lang: "ru", pad: 12, expandCall: true,
    pick: () => document.getElementById("call-h")?.closest("section"),
    shows: "End of the call transcript: read-back 'Ist das richtig?' / 'Ja, richtig', free trial, bring Hausschuhe, goodbye; German lines with Russian below, Russian UI.",
  },
  {
    file: "crop-transcript-start-ru.png", route: `/r/${RESULT}`, lang: "ru", pad: 12, expandCall: true, innerTop: true,
    pick: () => document.getElementById("call-h")?.closest("section"),
    shows: "Start of the call transcript: the assistant's first sentence 'Guten Tag! Hier ist die KI-Assistentin von Maria Ivanova ...' (says it is an AI) with Russian below, place answers; Russian UI.",
  },
  {
    file: "crop-callcard-ru.png", route: `/r/${RESULT}`, lang: "ru", pad: 12, expandCall: true,
    pick: () => [...document.querySelectorAll("section")].find((s) => s.style.viewTransitionName === "dmk-call-card"),
    shows: "Call card of the test call: Olgas Musikstudio, phone, timer 01:38, call ended, assistant and course organiser tiles, 'at the start the assistant said it is an AI'; Russian UI.",
  },
];

async function expandCall(page) {
  const clicked = await page.evaluate(() => {
    const b = document.querySelector("p.border-y button[aria-expanded='false']");
    if (!b) return false;
    b.click();
    return true;
  });
  if (clicked) await settle(page, 1200);
  return clicked;
}

// ---------- main shots ----------
async function runShot(browser, s) {
  const { ctx, page } = await openPage(browser, s.kind === "full" ? "full" : s.kind, s.lang);
  try {
    await go(page, s.route);
    let route = s.route;
    if (s.fallback) {
      const rows = await page.evaluate(() => document.querySelectorAll("main ul.border-t > li").length);
      log(`  filtered rows: ${rows}`);
      if (rows === 0) {
        route = s.fallback;
        await go(page, route);
        s.shows = "Courses page in Russian filtered to age 3-6 and music (the Russian-language filter had no match): active filter chips, result count, listings.";
      } else {
        s.shows = s.shows.replace("result count", `result count (${rows})`);
      }
    }
    const info = await pageInfo(page, s.lang);
    log(`  html lang=${info.htmlLang} dir=${info.dir} h1="${info.h1.slice(0, 60)}"`);
    if (info.errorPage) problems.push(`${s.file}: error/404 page (${info.h1})`);
    if (!info.langOk) problems.push(`${s.file}: html lang/dir mismatch (${info.htmlLang}/${info.dir})`);
    if (s.expandCall) await expandCall(page);
    if (s.scrollTo) {
      const handle = await page.evaluateHandle(s.scrollTo);
      const ok = await page.evaluate((el) => {
        if (!el) return false;
        el.scrollIntoView({ block: "start" });
        window.scrollBy(0, -16);
        return true;
      }, handle);
      await handle.dispose();
      if (!ok) problems.push(`${s.file}: scroll target not found`);
      await sleep(700);
    }
    if (s.full) {
      await scrollThrough(page);
      const h = await page.evaluate(() => document.documentElement.scrollHeight);
      const capH = Math.min(h, MAX_FULL);
      await page.setViewport({ ...VIEW.full, height: capH });
      await settle(page, 1000);
      if (h > MAX_FULL) s.shows += ` (cut at ${MAX_FULL} css px of ${h})`;
      await save(page, { ...s, route }, { fullPage: false });
    } else {
      await save(page, { ...s, route });
    }
  } finally {
    await ctx.close();
  }
}

async function runCrop(browser, c) {
  const { ctx, page } = await openPage(browser, "crop", c.lang);
  try {
    await go(page, c.route);
    if (c.expandCall) await expandCall(page);
    if (c.innerTop) {
      // The transcript list scrolls inside its own box and opens at the end; show the beginning instead.
      await page.evaluate(() => {
        const sec = document.getElementById("call-h")?.closest("section");
        for (const el of sec ? sec.querySelectorAll("*") : []) {
          const oy = getComputedStyle(el).overflowY;
          if ((oy === "auto" || oy === "scroll") && el.scrollHeight > el.clientHeight + 4) el.scrollTop = 0;
        }
      });
      await sleep(600);
    }
    let box;
    if (c.hover) {
      await page.evaluate(() => window.scrollTo(0, 0));
      await page.hover(c.hover);
      await sleep(900);
      box = await boxOf(page, c.pick, c.pad);
      if (!box) throw new Error("element not found");
      await save(page, { file: c.file, kind: "crop", route: c.route, lang: c.lang, shows: c.shows }, { clip: box, captureBeyondViewport: false });
    } else {
      // Scroll the element near the top so sticky/lazy parts render, then clip in document coordinates.
      const handle = await page.evaluateHandle(c.pick);
      const found = await page.evaluate((el) => {
        const e = Array.isArray(el) ? el[0] : el;
        if (!e) return false;
        e.scrollIntoView({ block: "start" });
        window.scrollBy(0, -40);
        return true;
      }, handle);
      await handle.dispose();
      if (!found) throw new Error("element not found");
      await sleep(700);
      box = await boxOf(page, c.pick, c.pad);
      if (!box) throw new Error("element not visible");
      await save(page, { file: c.file, kind: "crop", route: c.route, lang: c.lang, shows: c.shows }, { clip: box, captureBeyondViewport: true });
    }
  } finally {
    await ctx.close();
  }
}

// ---------- approval card (typed intake) ----------
function nextWeekday(dow) {
  // dow: 0 Sun .. 6 Sat; next date strictly after today (Berlin date is fine at demo time)
  const d = new Date();
  do d.setDate(d.getDate() + 1);
  while (d.getDay() !== dow);
  return d.toISOString().slice(0, 10);
}

async function clickByText(page, text, scope = "button") {
  return page.evaluate(
    (text, scope) => {
      const el = [...document.querySelectorAll(scope)].find((b) => b.textContent.trim() === text && !b.disabled);
      if (!el) return false;
      el.click();
      return true;
    },
    text,
    scope,
  );
}

async function waitForState(page, ms) {
  const end = Date.now() + ms;
  while (Date.now() < end) {
    const st = await page.evaluate(() => {
      if (document.getElementById("approval-title")) return "approval";
      const clarify = document.getElementById("clarify");
      if (clarify && clarify.querySelector("form")) return "questions";
      if (document.querySelector("[role=alert] button")) return "failed";
      if (clarify) return "clarify";
      return "waiting";
    });
    if (st !== "waiting" && st !== "clarify") return st;
    await sleep(500);
  }
  return "timeout";
}

/** After answering questions: wait until the round number changes and the form is idle again, or the card shows. */
async function waitAfterAnswer(page, prevRound, ms) {
  const end = Date.now() + ms;
  while (Date.now() < end) {
    const st = await page.evaluate((prev) => {
      if (document.getElementById("approval-title")) return "approval";
      const clarify = document.getElementById("clarify");
      const btn = clarify?.querySelector("form button[type=submit]");
      if (clarify && clarify.dataset.round !== prev && btn && !btn.disabled) return "questions";
      return "waiting";
    }, prevRound);
    if (st !== "waiting") return st;
    await sleep(500);
  }
  return "timeout";
}

/** Fill the Questions form (only inside #clarify form; never touches the approval card). */
async function fillQuestions(page) {
  const tue = nextWeekday(2);
  return page.evaluate((tue) => {
    const form = document.querySelector("#clarify form");
    if (!form || document.getElementById("approval-title")) return [];
    const setVal = (el, v) => {
      const proto = el.tagName === "SELECT" ? HTMLSelectElement.prototype : HTMLInputElement.prototype;
      Object.getOwnPropertyDescriptor(proto, "value").set.call(el, v);
      el.dispatchEvent(new Event("input", { bubbles: true }));
      el.dispatchEvent(new Event("change", { bubbles: true }));
    };
    const done = [];
    const radioGroups = new Set();
    for (const el of form.querySelectorAll("input, select")) {
      const type = el.type;
      if (type === "radio") {
        if (!radioGroups.has(el.name)) { radioGroups.add(el.name); el.click(); done.push("radio"); }
      } else if (type === "checkbox") {
        continue; // never tick checkboxes
      } else if (type === "date") { setVal(el, tue); done.push("date"); }
      else if (type === "time") { setVal(el, done.filter((d) => d === "time").length % 2 === 0 ? "15:00" : "17:30"); done.push("time"); }
      else if (type === "number") { setVal(el, "4"); done.push("number"); }
      else if (type === "month") { setVal(el, tue.slice(0, 7)); done.push("month"); }
      else if (el.tagName === "SELECT") { if (!el.value && el.options.length) setVal(el, el.options[el.options.length > 1 ? 1 : 0].value); done.push("select"); }
      else if (type === "tel") { if (!el.value) { setVal(el, "0351 1234567"); done.push("tel"); } }
      else if (type === "text") { if (!el.value) { setVal(el, "Maria Petrova"); done.push("text"); } }
    }
    return done;
  }, tue);
}

async function runApproval(browser) {
  log("approval flow (ru, desktop)");
  const { ctx, page } = await openPage(browser, "desktop", "ru");
  let intakePosts = 0;
  const notes = [];
  await page.setRequestInterception(true);
  page.on("request", (req) => {
    const url = req.url();
    const m = req.method();
    if (m === "POST" && /\/rest\/v1\/call_requests/.test(url)) {
      notes.push("blocked a call_requests insert");
      return req.abort();
    }
    if (m === "POST" && /webhook\/task-intake/.test(url)) {
      intakePosts++;
      if (intakePosts > MAX_INTAKE_POSTS) {
        notes.push(`intake POST #${intakePosts} aborted (local merge)`);
        return req.abort();
      }
      log(`  intake POST #${intakePosts}`);
    }
    req.continue();
  });
  try {
    await go(page, ASK);
    const typeLabel = t("ru", "voice.typeInstead");
    if (!(await clickByText(page, typeLabel))) throw new Error("'type instead' button not found");
    await page.waitForSelector("textarea");
    await sleep(400);
    await page.focus("textarea");
    await page.keyboard.sendCharacter(INTAKE_TEXT);
    await sleep(800);
    await save(page, { file: "desktop-ask-typed-ru.png", kind: "desktop", route: ASK, lang: "ru", shows: "Call-for-me typed path in Russian: place card, title, Maria's request typed into the text field ('Хочу записать дочку на музыку ...'), dictate button, quick chips." });

    const cont = t("ru", "common.continue");
    let state = "timeout";
    for (let attempt = 1; attempt <= 2; attempt++) {
      if (attempt === 1) {
        // Bring the text field and the loading line below it into view for the "reading" shot.
        await page.evaluate(() => {
          document.querySelector("textarea")?.scrollIntoView({ block: "start" });
          window.scrollBy(0, -140);
        });
        if (!(await clickByText(page, cont))) throw new Error("Continue button not found");
        await sleep(1800);
        await save(page, { file: "desktop-ask-reading-ru.png", kind: "desktop", route: ASK, lang: "ru", shows: "Call-for-me in Russian right after Continue: 'Reading your request...' with 'your words' and a skeleton of the German call card being prepared." });
      } else {
        if (!(await clickByText(page, t("ru", "common.tryAgain")))) break;
      }
      state = await waitForState(page, 40000);
      log(`  attempt ${attempt}: ${state}`);
      if (state !== "failed" && state !== "timeout") break;
      if (state === "timeout") break; // the app itself aborts after 20 s; a timeout here means no answer at all
    }
    if (state === "timeout" || state === "failed") {
      problems.push(`approval card: intake did not answer (${state}); skipped`);
      return;
    }

    for (let round = 0; round < 3 && state === "questions"; round++) {
      await page.evaluate(() => document.getElementById("clarify")?.scrollIntoView({ block: "start" }));
      await sleep(600);
      if (round === 0)
        await save(page, { file: "desktop-ask-questions-ru.png", kind: "desktop", route: ASK, lang: "ru", shows: "Call-for-me in Russian after the first intake answer: the understood goal in Russian and the follow-up question 'What is your name (to introduce you to the studio)?' with Continue." });
      const filled = await fillQuestions(page);
      log(`  filled: ${filled.join(",")}`);
      await sleep(400);
      const prevRound = await page.evaluate(() => document.getElementById("clarify")?.dataset.round ?? "");
      const submitted = await page.evaluate(() => {
        const b = document.querySelector("#clarify form button[type=submit]");
        if (!b || b.disabled) return false;
        b.click();
        return true;
      });
      if (!submitted) break;
      state = await waitAfterAnswer(page, prevRound, 40000);
      log(`  after questions round ${round + 1}: ${state}`);
    }

    if (state !== "approval") {
      problems.push(`approval card: did not reach the approval card (last state ${state})`);
      return;
    }
    await settle(page, 2500);
    await page.evaluate(() => {
      const s = document.getElementById("approval-title")?.closest("section");
      s?.scrollIntoView({ block: "start" });
      window.scrollBy(0, -24);
    });
    await sleep(800);
    await save(page, { file: "desktop-ask-approval-ru.png", kind: "desktop", route: ASK, lang: "ru", shows: "Approval card in Russian (viewport at the card): heading 'Here is what I will say', German opening line ('Hier ist die KI-Assistentin von Maria Petrova ...') with Russian below, goal, what it will ask, time windows Tue 29 Sep and Thu 1 Oct 15:00-19:00, allowed fact 'Alter des Kindes: 4 Jahre'. Heading has a keyboard focus outline." });
    const box = await boxOf(page, () => document.getElementById("approval-title")?.closest("section"), 16);
    if (box) {
      await save(page, { file: "crop-approval-ru.png", kind: "crop", route: ASK, lang: "ru", shows: "The whole approval card in Russian: German opening line with Russian below, goal, place and phone, what it will ask, time windows (Tue 29 Sep / Thu 1 Oct 15:00-19:00), allowed facts, what it never does, consent checkbox (not ticked), disabled 'Call now' button. Heading has a keyboard focus outline." }, { clip: box, captureBeyondViewport: true });
    }
    await page.evaluate(() => window.scrollTo(0, 0));
    const h = await page.evaluate(() => document.documentElement.scrollHeight);
    await page.setViewport({ ...VIEW.full, height: Math.min(h, MAX_FULL) });
    await settle(page, 1000);
    await save(page, { file: "full-ask-approval-ru.png", kind: "full", route: ASK, lang: "ru", shows: `Full Call-for-me page in Russian with the typed request and the approval card${h > MAX_FULL ? ` (cut at ${MAX_FULL} of ${h} css px)` : ""}.` });
  } catch (e) {
    problems.push(`approval card: ${e.message}`);
  } finally {
    log(`  intake POSTs: ${intakePosts}; ${notes.join("; ")}`);
    if (notes.length) problems.push(`approval notes: ${notes.join("; ")}`);
    await ctx.close();
  }
}

// ---------- run ----------
fs.mkdirSync(OUT, { recursive: true });
const manifestPath = path.join(OUT, "manifest.json");
if (fs.existsSync(manifestPath) && (only.length || approvalOnly || noApproval)) {
  try { manifest.push(...JSON.parse(fs.readFileSync(manifestPath, "utf-8"))); } catch {}
}

const browser = await puppeteer.launch({
  executablePath: CHROME,
  headless: "new",
  args: ["--hide-scrollbars", "--lang=en-US", "--font-render-hinting=none"],
});
checker = await browser.newPage();

try {
  for (const s of shots()) {
    if (!want(s.file)) continue;
    log(`${s.file}  ${s.route}`);
    try { await runShot(browser, s); } catch (e) { problems.push(`${s.file}: ${e.message}`); log(`  FAILED ${e.message}`); }
  }
  for (const c of CROPS) {
    if (!want(c.file)) continue;
    log(`${c.file}  ${c.route}`);
    try { await runCrop(browser, c); } catch (e) { problems.push(`${c.file}: ${e.message}`); log(`  FAILED ${e.message}`); }
  }
  if (!noApproval && (approvalOnly || !only.length || only.some((o) => "approval".includes(o)))) await runApproval(browser);
} finally {
  await browser.close();
}

const order = (f) => ["desktop", "full", "mobile", "crop"].indexOf(f.split("-")[0]);
manifest.sort((a, b) => order(a.file) - order(b.file) || a.file.localeCompare(b.file));
fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2) + "\n", "utf-8");
log(`\n${manifest.length} entries in manifest.json`);
if (problems.length) {
  log("PROBLEMS:");
  for (const p of problems) log("  - " + p);
}
