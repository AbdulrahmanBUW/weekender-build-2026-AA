// Voice relay: browser mic <-> Deepgram Voice Agent (German), live transcript -> Supabase.
// Also /listen: browser mic -> Deepgram streaming STT in the user's language (intake voice input, nothing stored).
// The Deepgram key and the Supabase service key stay on this server; the browser never sees them.
import dotenv from 'dotenv';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

dotenv.config({ path: fileURLToPath(new URL('./.env', import.meta.url)) });
import { WebSocketServer, WebSocket } from 'ws';
import { createClient } from '@supabase/supabase-js';
import { templateFor, REASON_DE } from './task-templates.js';

const PORT = Number(process.env.PORT || 8787);
const DG_KEY = process.env.DEEPGRAM_API_KEY;
const DG_URL = 'wss://agent.deepgram.com/v1/agent/converse';
const THINK_PROVIDER = process.env.THINK_PROVIDER || 'anthropic';
const THINK_MODEL = process.env.THINK_MODEL || 'claude-sonnet-5';
const SPEAK_MODEL = process.env.SPEAK_MODEL || 'aura-2-viktoria-de';   // alternative: aura-2-elara-de (calm)
const LISTEN_MODEL = process.env.LISTEN_MODEL || 'nova-3';              // or flux-general-multi (Flux, v2 listen API)
const IS_FLUX = LISTEN_MODEL.startsWith('flux');
const DISCLOSURE_VARIANT = 'warm_default';
const DEMO_REQUEST_ID = '00000000-0000-0000-0000-000000000001';

if (!DG_KEY) {
  console.error('DEEPGRAM_API_KEY missing: copy .env.example to .env and fill it in.');
  process.exit(1);
}

const db = process.env.SUPABASE_URL && process.env.SUPABASE_SERVICE_ROLE_KEY
  ? createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_ROLE_KEY, { auth: { persistSession: false } })
  : null;
console.log(db ? 'Supabase: connected (transcripts are saved)' : 'Supabase: NOT configured (no-DB mode, nothing is saved)');

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// ---------- small helpers ----------
const clip = (v, n) => String(v ?? '').replace(/[\r\n\t\u0000-\u001f]+/g, ' ').replace(/\s+/g, ' ').trim().slice(0, n);
// Remove stage directions like "(Anruf beendet)" / "[lacht]" (RUN-012) before sending/saving a line.
const stripStageDirections = t => String(t || '').replace(/\([^)]*\)|\[[^\]]*\]|\*[^*]*\*/g, ' ').replace(/\s+/g, ' ').trim();
const normTime = t => { const m = /^(\d{1,2}):(\d{2})/.exec(String(t || '').trim()); return m ? `${m[1].padStart(2, '0')}:${m[2]}` : null; };
// record_result / confirm_booking details: plain object, ≤ 2000 chars, empty values dropped
const cleanDetails = d => (d && typeof d === 'object' && !Array.isArray(d) && JSON.stringify(d).length <= 2000
  ? Object.fromEntries(Object.entries(d).filter(([, v]) => v !== '' && v != null)) : {});
const RESERVED_RESULT_KEYS = ['result_type', 'booking_kind', 'date', 'time', 'doctor', 'party_size'];
const withoutReserved = (o, keys = RESERVED_RESULT_KEYS) => Object.fromEntries(Object.entries(o || {}).filter(([k]) => !keys.includes(k)));

// Local Berlin date+time -> UTC ISO string (handles CET/CEST). null if invalid.
function berlinIso(date, time) {
  const t = normTime(time);
  if (!/^\d{4}-\d{2}-\d{2}$/.test(String(date || '')) || !t) return null;
  const guess = new Date(`${date}T${t}:00Z`);
  if (Number.isNaN(guess.getTime()) || guess.toISOString().slice(0, 10) !== date) return null;
  const g = Object.fromEntries(new Intl.DateTimeFormat('en-US', {
    timeZone: 'Europe/Berlin', hourCycle: 'h23', year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit'
  }).formatToParts(guess).map(p => [p.type, p.value]));
  const offset = Date.UTC(+g.year, +g.month - 1, +g.day, +g.hour, +g.minute) - guess.getTime();
  return new Date(guess.getTime() - offset).toISOString();
}

function windowsText(windows = []) {
  return windows.map(w => {
    const d = new Date(`${w.date}T12:00:00`);
    const day = d.toLocaleDateString('de-DE', { weekday: 'long', day: 'numeric', month: 'long' });
    return `- ${day}, ${normTime(w.from)}–${normTime(w.to)} Uhr`;
  }).join('\n');
}

function inWindows(date, time, windows = []) {
  const t = normTime(time);
  return !!t && windows.some(w => w.date === date && t >= normTime(w.from) && t <= normTime(w.to));
}

// ---------- prompt building (task type specifics live in task-templates.js) ----------
function factsOf(req) {
  const list = Array.isArray(req.allowed_facts) ? req.allowed_facts : [];
  return list.filter(f => f && f.key && f.value != null)
    .slice(0, 15)
    .map(f => ({ key: clip(f.key, 40).toLowerCase(), label: clip(f.label || f.key, 40), value: clip(f.value, 80) }));
}

// Gender only from an explicit fact; otherwise neutral phrasing with the name.
function personOf(req, facts) {
  const get = k => facts.find(f => f.key === k)?.value || '';
  const name = clip(req.patient_name || 'die Person', 80);
  const surname = name.split(' ').slice(-1)[0];
  const pronoun = (get('pronoun') || get('person_pronoun')).toLowerCase();
  const salutation = (get('salutation') || get('title')).toLowerCase();
  const gender = /^(she|her|sie|f\b|female|weiblich)/.test(pronoun) ? 'f'
    : /^(he|him|er\b|m\b|male|männlich)/.test(pronoun) ? 'm' : null;
  const sal = /^frau/.test(salutation) ? 'f' : /^herr/.test(salutation) ? 'm' : null;
  return { name, surname, gender, sal };
}

function greetingOf(p, purpose) {
  const open = `Guten Tag! Hier ist die KI-Assistentin von ${p.name}.`;
  if (p.gender === 'f') return `${open} Ich rufe für sie an, weil ihr Deutsch noch nicht so gut ist, und ${purpose}.`;
  if (p.gender === 'm') return `${open} Ich rufe für ihn an, weil sein Deutsch noch nicht so gut ist, und ${purpose}.`;
  if (p.sal === 'f') return `${open} Ich rufe für Frau ${p.surname} an, die noch nicht so gut Deutsch spricht, und ${purpose}.`;
  if (p.sal === 'm') return `${open} Ich rufe für Herrn ${p.surname} an, der noch nicht so gut Deutsch spricht, und ${purpose}.`;
  return `${open} Ich rufe an, weil ${p.name} noch nicht so gut Deutsch spricht, und ${purpose}.`;
}

function buildAgent(req) {
  const tpl = templateFor(req.task_type);
  const facts = factsOf(req);
  const p = personOf(req, facts);
  const c = req.constraints && typeof req.constraints === 'object' ? req.constraints : {};
  const windows = Array.isArray(req.time_windows) ? req.time_windows : [];
  const reason = REASON_DE[req.reason_category] || 'Termin';
  const h = {
    reason,
    fact: k => facts.find(f => f.key === k)?.value || '',
    party: () => (Number.isInteger(Number(c.party_size)) && Number(c.party_size) > 0 ? Number(c.party_size) : null),
    hasWindows: windows.length > 0
  };
  const fnNames = tpl.functions(req);
  const org = clip(req.practice_name || 'die Organisation', 100);
  const goal = clip(req.goal_de, 300) || tpl.goalDe(req, h);
  const greeting = greetingOf(p, tpl.purposeDe(req, h));

  const factLines = [`- Name der Person: ${p.name}`];
  for (const f of facts) if (!['pronoun', 'person_pronoun', 'salutation', 'title'].includes(f.key)) factLines.push(`- ${f.label}: ${f.value}`);
  if (tpl.useDoctorFields) {
    if (req.patient_dob && !facts.some(f => /dob|birth|geburt/.test(f.key))) factLines.push(`- Geburtsdatum: ${req.patient_dob}`);
    if (req.insurance_type && !facts.some(f => /insur|versich/.test(f.key))) factLines.push(`- Versicherung: ${req.insurance_type === 'pkv' ? 'privat' : req.insurance_type === 'gkv' ? 'gesetzlich' : 'sonstige'}${req.insurance_name ? `, ${clip(req.insurance_name, 60)}` : ''}`);
    factLines.push(`- Neupatient: ${req.is_new_patient ? 'ja' : 'nein'}`, `- Überweisung: ${req.has_referral ? 'ja' : 'nein'}`, `- Anliegen (Kategorie): ${reason}`);
  }

  const frame = [];
  if (windows.length) frame.push(`Erlaubte Zeitfenster (nur darin zusagen):\n${windowsText(windows)}`);
  if (h.party()) frame.push(`Personenzahl: ${h.party()}`);
  if (c.budget_max_eur != null && !Number.isNaN(Number(c.budget_max_eur))) frame.push(`Budget höchstens ${Number(c.budget_max_eur)} Euro`);
  if (c.deadline) frame.push(`Frist: ${clip(c.deadline, 40)}`);
  if (c.notes_de) frame.push(`Hinweis: ${clip(c.notes_de, 200)}`);

  const pronounRule = p.gender
    ? `Sprich über ${p.name} als "${p.gender === 'f' ? 'sie' : 'er'}".`
    : p.sal ? `Sprich über die Person als "${p.sal === 'f' ? 'Frau' : 'Herr'} ${p.surname}".`
      : `Das Geschlecht von ${p.name} ist unbekannt: verwende keine Pronomen wie "sie" oder "er" und keine Anrede Frau/Herr, sondern den Namen.`;
  // how the agent refers to the person in a sentence ("… meldet sich {ref} gern selbst")
  const ref = p.gender === 'f' ? 'sie' : p.gender === 'm' ? 'er' : p.sal ? `${p.sal === 'f' ? 'Frau' : 'Herr'} ${p.surname}` : p.name;
  const tplRules = typeof tpl.rules === 'function' ? tpl.rules(req, h) : (tpl.rules || []);

  const successRule = tpl.mode === 'appointment' && fnNames.includes('confirm_booking')
    ? 'Ziel ist eine Zusage innerhalb der Zeitfenster. Wiederhole vorher Wochentag, Datum und Uhrzeit (und bei einer Praxis die Ärztin/den Arzt, falls genannt) und warte auf ein "Ja"/"Richtig". Erst danach rufst du confirm_booking auf. Nach confirm_booking: kurz bedanken, in EINEM Satz verabschieden, end_call mit outcome "booked".'
    : '';
  // family types (course/kita): the booking is the main goal, record_result only when no slot inside the windows came up
  const resultLead = tpl.bookingDetails && fnNames.includes('confirm_booking')
    ? 'Nur wenn KEIN Termin im Zeitfenster zustande kommt, und erst wenn alle Fragen aus der AUFGABE gestellt sind: fasse die Antworten kurz zusammen'
    : 'Sobald du die Antwort hast: fasse sie kurz zusammen';
  // family types: speak a short filler in the same turn as record_result, so the other side does not hear ~6-7 s of
  // silence while the result is written and the goodbye is generated (DEF-025, record_result path; RUN-016 verification)
  const resultCall = tpl.bookingDetails
    ? 'warte auf die Bestätigung, sag dann nur "Danke, ich notiere das." und rufe im selben Zug record_result auf'
    : 'warte auf die Bestätigung, rufe dann record_result auf';
  const resultRule = fnNames.includes('record_result')
    ? `${resultLead} ("Nur damit ich es richtig notiere: …"), ${resultCall} (nur ausdrücklich genannte Angaben; eine Frage ohne klare Antwort lässt du weg, ein "Gerne, auf Wiederhören" ist keine Antwort) (Details: ${tpl.resultHint || 'die wichtigsten Angaben'}), verabschiede dich in EINEM Satz und rufe end_call mit outcome "completed" auf.`
    : '';

  const rules = [
    'Du bist eine KI und sagst das ehrlich. Fragt jemand "Sind Sie ein Roboter/eine KI/ein Computer?", bestätige sofort: "Ja, genau, ich bin eine KI. Ich rufe im Auftrag an und habe alle Angaben hier." Gib dich niemals als die Person oder als Mensch aus.',
    'Nenne niemals Gesundheitsdaten, Symptome oder Diagnosen.',
    `Verwende NUR die FAKTEN oben. Wird etwas anderes gefragt: "Das kann ich leider nicht sagen, das klärt ${ref} gern selbst mit Ihnen." — oder rufe needs_user auf, wenn es wichtig ist.`,
    pronounRule,
    'Sage nichts zu, was außerhalb von AUFGABE und RAHMEN liegt. Liegt ein Angebot außerhalb, frag höflich nach einer Alternative.',
    'Wenn die Gegenseite auf der Person besteht oder nicht mit einer KI sprechen möchte: bedanke dich, rufe needs_user auf (Frage auf Englisch) und verabschiede dich.',
    'Wenn nichts erreicht werden kann: bedanke dich und rufe end_call mit dem passenden outcome ("rejected" oder "failed") auf.',
    'Nenne Namen von Ansprechpartnern NUR, wenn sie klar und vollständig gesagt wurden. Einzelne unklare Wörter sind KEINE Namen. Erfinde niemals Namen, Daten, Uhrzeiten oder Zahlen.',
    'Wenn du etwas akustisch nicht sicher verstanden hast, frag höflich nach ("Entschuldigung, habe ich richtig verstanden: …?").',
    'Stelle nie zwei Fragen in einem Satz. Kommt trotzdem nur ein "Ja" auf zwei Fragen, frag nach, worauf es sich bezieht; notiere nichts, was nicht einzeln beantwortet wurde.',   // DEF-027
    'Namen buchstabierst du nur auf Nachfrage mit dem deutschen Buchstabieralphabet ("A wie Anton").',
    ...tplRules.filter(Boolean).map(r => r.replaceAll('{reason}', reason).replaceAll('{person}', ref))
  ];

  const style = [
    'Kurze Antworten: höchstens zwei Sätze, eine Frage pro Antwort.',
    'Beginne Antworten oft mit einer kurzen, natürlichen Bestätigung ("Ja, genau." · "Alles klar." · "Mhm, verstehe." · "Gern.") und wiederhole nie dieselbe zweimal hintereinander.',
    'Schreibe Zahlen, Daten und Uhrzeiten so, wie man sie spricht: "am Dienstag, dem sechsten Oktober", "um halb zehn", "um vierzehn Uhr dreißig" — niemals "06.10." oder "9:30".',
    'Sagt die Gegenseite "Moment bitte" oder "Einen Augenblick", antworte nur "Ja, gern, ich warte." und warte still.',
    'Wirst du unterbrochen, wiederhole nicht den ganzen Satz, sondern reagiere auf das Gesagte.',
    'Schreibe NIEMALS Regieanweisungen oder Text in Klammern, z. B. "(Anruf beendet)" oder "[wartet]". Alles, was du schreibst, wird laut gesprochen. Nach der Verabschiedung sagst du nichts mehr.'
  ];

  const brief = clip(req.call_brief_de, 1500);
  const prompt = `Du bist eine freundliche, höfliche KI-Assistentin am Telefon. Du rufst im Auftrag von ${p.name} bei "${org}" an. Du sprichst ausschließlich Deutsch.

AUFGABE: ${goal}

FAKTEN (nur diese verwenden, nichts erfinden):
${factLines.join('\n')}
${frame.length ? `\nRAHMEN:\n${frame.join('\n')}\n` : ''}
${brief ? `VORBEREITETES BRIEFING (bei Widerspruch gelten AUFGABE, FAKTEN und RAHMEN):\n${brief}\n` : ''}
${[successRule, resultRule].filter(Boolean).join('\n')}

REGELN:
${rules.map((r, i) => `${i + 1}. ${r}`).join('\n')}

SPRECHSTIL:
${style.map(r => `- ${r}`).join('\n')}`;

  const keyterms = [...new Set([...p.name.split(/\s+/), org.replace(/^(Praxis|Hausarztpraxis|Kinderarztpraxis|Apotheke|Restaurant|Musikschule|Tanzschule|Kita|Kindertagesstätte|Kindergarten)\s*/i, ''), 'KI-Assistentin', ...(tpl.keyterms || [])])]
    .filter(Boolean).slice(0, 10);

  return { greeting, prompt, keyterms, functions: buildFunctions(req, tpl, fnNames), template: tpl };
}

const END_OUTCOMES = ['booked', 'completed', 'rejected', 'rejected_no_new_patients', 'needs_user', 'failed'];

function buildFunctions(req, tpl, names) {
  const fns = [];
  if (names.includes('confirm_booking')) {
    const properties = {
      date: { type: 'string', description: 'Agreed date, YYYY-MM-DD' },
      time: { type: 'string', description: 'Agreed time, HH:MM (24h)' },
      bring_items: { type: 'array', items: { type: 'string' }, description: 'Things the person must bring, in German (e.g. Versichertenkarte)' }
    };
    if (tpl.useDoctorFields) properties.doctor = { type: 'string', description: 'Doctor name ONLY if the practice clearly said it; otherwise omit' };
    if (req.task_type === 'restaurant_booking') properties.party_size = { type: 'integer', description: 'Number of people as agreed' };
    if (tpl.bookingDetails) properties.details = { type: 'object', description: `Everything else the other side explicitly said (${tpl.resultHint || 'key facts'}). Leave out anything not clearly answered ("ja, gern" before a counter-question is NOT a yes); never guess and add no own conclusions (e.g. no "no Ukrainian" when it was simply not mentioned).` };
    fns.push({
      name: 'confirm_booking',
      description: `Call ONLY after the other side explicitly confirmed your read-back. Records the agreed ${tpl.bookingKind ? tpl.bookingKind.replace(/_/g, ' ') : 'appointment/visit/table'}. The server rejects times outside the allowed windows.`,
      parameters: { type: 'object', properties, required: ['date', 'time'] }
    });
  }
  if (names.includes('record_result')) {
    fns.push({
      name: 'record_result',
      description: `Call after the other side confirmed your short summary of the answer. Records the information for the user. Details should contain: ${tpl.resultHint || 'the key facts'}.`,
      parameters: {
        type: 'object',
        properties: {
          result_type: { type: 'string', description: `Short snake_case type${tpl.resultType ? ` (use "${tpl.resultType}")` : ', e.g. how_to_book, documents, reported, answer'}` },
          details: { type: 'object', description: 'ONLY facts the other side explicitly said (numbers as numbers, times HH:MM). Leave out anything not clearly answered: a goodbye or "gerne" is NOT a yes. Never guess, no own conclusions.' },
          summary_en: { type: 'string', description: 'One or two plain English sentences for the user' }
        },
        required: ['result_type', 'details', 'summary_en']
      }
    });
  }
  fns.push({
    name: 'needs_user',
    description: 'The other side asked something only the person can answer, or insists on talking to the person.',
    parameters: { type: 'object', properties: { question: { type: 'string', description: 'What they want to know, in English' } }, required: ['question'] }
  });
  fns.push({
    name: 'end_call',
    description: 'End the call after saying goodbye.',
    parameters: {
      type: 'object',
      properties: { outcome: { type: 'string', enum: END_OUTCOMES }, summary_en: { type: 'string', description: 'One-sentence English summary for the user' } },
      required: ['outcome']
    }
  });
  return fns;
}

// ---------- tiny DB helpers (no-ops in no-DB mode) ----------
async function dbq(label, fn) {
  if (!db) return null;
  const { data, error } = await fn(db);
  if (error) console.error(`[db] ${label}:`, error.message);
  return data;
}

async function loadRequest(id) {
  const fallback = {
    id, task_type: 'doctor_appointment', user_language: 'en', patient_name: 'Priya Sharma', patient_dob: '2002-03-14',
    insurance_type: 'gkv', insurance_name: 'Techniker Krankenkasse', practice_name: 'Hausarztpraxis Dr. Weber',
    reason_category: 'first_visit', is_new_patient: true, has_referral: false, allowed_facts: [], constraints: {},
    time_windows: [{ date: nextWeekday(2), from: '08:00', to: '12:00' }], call_brief_de: null
  };
  if (!db) return fallback;
  const row = await dbq('load request', c => c.from('call_requests').select('*').eq('id', id).maybeSingle());
  return row || fallback;
}

function nextWeekday(dow) { // 0=Sun..6=Sat
  const d = new Date(); d.setDate(d.getDate() + ((dow + 7 - d.getDay()) % 7 || 7));
  return d.toISOString().slice(0, 10);
}

// ---------- HTTP: serve the test page ----------
const server = http.createServer((req, res) => {
  if (req.url === '/' || req.url.startsWith('/?')) {
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    return fs.createReadStream(path.join(__dirname, 'public', 'index.html')).pipe(res);
  }
  if (req.url === '/mic-worklet.js') {
    res.writeHead(200, { 'Content-Type': 'text/javascript' });
    return fs.createReadStream(path.join(__dirname, 'public', 'mic-worklet.js')).pipe(res);
  }
  if (req.url === '/health') { res.writeHead(200); return res.end('ok'); }
  res.writeHead(404); res.end('not found');
});

// ---------- WS security (security review 2026-09-26, medium) ----------
// Only our own pages may open calls: stops other websites in the same browser from spending
// Deepgram/Claude quota or changing request status via this relay. Applies to /call and /listen.
const ALLOWED_ORIGINS = (process.env.ALLOWED_ORIGINS || `http://127.0.0.1:${PORT},http://localhost:${PORT}`)
  .split(',').map(s => s.trim()).filter(Boolean);
// Hosted frontends (Lovable preview + published URLs change per project/branch): accept https://<sub><suffix>.
// Set ALLOWED_ORIGIN_SUFFIXES= (empty) to turn this off and rely on the exact list only.
const ALLOWED_ORIGIN_SUFFIXES = (process.env.ALLOWED_ORIGIN_SUFFIXES ?? '.lovable.app,.lovableproject.com')
  .split(',').map(s => s.trim().toLowerCase()).filter(Boolean).map(s => (s.startsWith('.') ? s : `.${s}`));

function originAllowed(origin) {
  if (ALLOWED_ORIGINS.includes(origin)) return true;
  let u; try { u = new URL(origin); } catch { return false; }
  // exactly https://host (no port, path, user info; browsers send lowercase hosts)
  if (u.protocol !== 'https:' || u.port || u.origin !== origin) return false;
  const host = u.hostname;
  return ALLOWED_ORIGIN_SUFFIXES.some(s => host.endsWith(s) && host.length > s.length);
}
const MAX_CONCURRENT_CALLS = Number(process.env.MAX_CONCURRENT_CALLS || 3);   // shared by /call and /listen
const MAX_LISTEN_SECONDS = Number(process.env.MAX_LISTEN_SECONDS || 120);
const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
// Intake languages -> Deepgram nova-3 streaming codes (all verified with probe-listen.js, 26 Sep 2026)
const LISTEN_LANGS = { en: 'en', ar: 'ar', tr: 'tr', uk: 'uk', ru: 'ru', fa: 'fa', hi: 'hi', es: 'es', fr: 'fr', pl: 'pl', vi: 'vi', zh: 'zh-CN', de: 'de' };
let activeCalls = 0;

const wss = new WebSocketServer({ noServer: true });
const listenWss = new WebSocketServer({ noServer: true });

function reject(socket, code, msg) {
  socket.write(`HTTP/1.1 ${code} ${msg}\r\nConnection: close\r\nContent-Type: text/plain\r\n\r\n${msg}`);
  socket.destroy();
}

server.on('upgrade', (req, socket, head) => {
  const url = new URL(req.url, 'http://x');
  const origin = req.headers.origin;
  if (origin && !originAllowed(origin)) return reject(socket, 403, 'origin not allowed');
  if (activeCalls >= MAX_CONCURRENT_CALLS) return reject(socket, 429, 'too many calls');
  if (url.pathname === '/call') {
    const id = url.searchParams.get('request');
    if (id && !UUID_RE.test(id)) return reject(socket, 400, 'bad request id');
    return wss.handleUpgrade(req, socket, head, ws => wss.emit('connection', ws, req));
  }
  if (url.pathname === '/listen') {
    if (!LISTEN_LANGS[url.searchParams.get('lang') || '']) return reject(socket, 400, 'language not supported');
    return listenWss.handleUpgrade(req, socket, head, ws => listenWss.emit('connection', ws, req));
  }
  reject(socket, 404, 'not found');
});

// ---------- /call: one browser connection = one call ----------
const GOODBYE_RE = /(wiederhören|wiedersehen|tschüss|schönen tag|schönes wochenende)/i;
const HOLD_RE = /\b(moment|augenblick|kurz warten|bleiben sie (bitte )?dran|ich schau(e)? (mal )?nach|ich sehe mal nach)\b/i;

wss.on('connection', async (browser, httpReq) => {
  activeCalls += 1;
  let browserGone = false;          // closed during the setup awaits below (before the real close handler exists)
  browser.once('close', () => { browserGone = true; });
  const url = new URL(httpReq.url, 'http://x');
  const requestId = url.searchParams.get('request') || DEMO_REQUEST_ID;
  const toBrowser = obj => browser.readyState === WebSocket.OPEN && browser.send(JSON.stringify(obj));

  const req = await loadRequest(requestId);
  const { greeting, prompt, keyterms, functions, template } = buildAgent(req);

  const call = await dbq('create call', c => c.from('calls')
    .insert({ request_id: req.id, provider: 'deepgram-browser', started_at: new Date().toISOString(), disclosure_variant: DISCLOSURE_VARIANT })
    .select('id').single());
  const callId = call?.id || null;
  await dbq('status calling', c => c.from('call_requests').update({ status: 'calling' }).eq('id', req.id));
  await dbq('event call_started', c => c.from('events').insert({ request_id: req.id, source: 'voice', type: 'call_started', payload: { provider: 'deepgram-browser', call_id: callId, task_type: req.task_type, listen: LISTEN_MODEL, speak: SPEAK_MODEL } }));
  console.log(`[call ${callId || 'no-db'}] started for request ${req.id} (${req.task_type || 'doctor_appointment'}, ${functions.map(f => f.name).join('/')})`);
  toBrowser({
    type: 'relay', event: 'call_started', callId, requestId: req.id, patient: req.patient_name, practice: req.practice_name,
    task_type: req.task_type || 'doctor_appointment', task_label: template.label, user_language: req.user_language || 'en', saving: !!db
  });

  const dg = new WebSocket(DG_URL, { headers: { Authorization: `Token ${DG_KEY}` } });
  let endAfterAudio = false;
  let recordedOutcome = null;
  let lastResult = null;            // calls.result as last written (booking + extra answers are merged)
  let summaryRecorded = false;
  let lastPracticeActivity = Date.now();
  let holdUntil = 0;
  let agentSpeaking = false;
  let saidGoodbye = false;          // last agent line was a goodbye
  let muteAfterEnd = false;
  let audioMuted = false;         // end_call after a goodbye: drop anything the model adds ("Termin vereinbart – danke!")
  let practiceHeard = false;      // the other side said something (so a later silence is NOT "no answer")
  let askedUser = false;          // needs_user was called
  const SILENCE_LIMIT_MS = Number(process.env.SILENCE_LIMIT_MS || 30000);
  const HOLD_LIMIT_MS = Number(process.env.HOLD_LIMIT_MS || 90000);
  const keepAlive = setInterval(() => dg.readyState === WebSocket.OPEN && dg.send(JSON.stringify({ type: 'KeepAlive' })), 8000);

  // The call stops without confirm_booking / record_result / end_call (silence, the other side hung up, Deepgram dropped):
  // record an honest outcome. Before: silence after a whole conversation was saved as "did not answer" and a hang-up
  // (browser closed) left the request "calling" with no outcome (RUN-016 verification).
  async function closeWithoutResult(why, stopped = false) {   // stopped = closed/dropped (not a silence timeout)
    if (recordedOutcome || endAfterAudio) return recordedOutcome;
    const outcome = askedUser ? 'needs_user' : (practiceHeard || stopped) ? 'failed' : 'no_answer';
    recordedOutcome = outcome;
    const summary = outcome === 'no_answer' ? 'The other side did not answer or went silent.'
      : `The call ended before anything was confirmed (${why}). Nothing was agreed or recorded${outcome === 'needs_user' ? '; an open question for the person is saved' : '; please check or try again'}.`;
    await dbq(`outcome ${outcome}`, c => c.from('calls').update({ outcome, summary_en: summary }).eq('id', callId));
    if (outcome !== 'needs_user') await dbq('status failed', c => c.from('call_requests').update({ status: 'failed' }).eq('id', req.id));
    return outcome;
  }

  // No answer / other side went silent: close the call with a recorded outcome instead of leaving it "calling".
  // During an explicit hold ("Moment bitte") the limit is raised to HOLD_LIMIT_MS.
  const silenceWatch = setInterval(async () => {
    if (agentSpeaking || recordedOutcome || endAfterAudio) return;
    const limit = Date.now() < holdUntil ? HOLD_LIMIT_MS : SILENCE_LIMIT_MS;
    if (Date.now() - lastPracticeActivity < limit) return;
    const outcome = await closeWithoutResult('the other side went silent');
    toBrowser(outcome === 'no_answer' ? { type: 'relay', event: 'no_answer' } : { type: 'relay', event: 'ending', outcome, summary_en: 'The other side went silent before anything was confirmed.' });
    finish('silence timeout');
  }, 5000);

  const listenProvider = IS_FLUX
    ? { type: 'deepgram', version: 'v2', model: LISTEN_MODEL, ...(LISTEN_MODEL.includes('multi') ? { language_hints: ['de'] } : {}), keyterms }
    : { type: 'deepgram', model: LISTEN_MODEL, keyterms };

  dg.on('open', () => {
    dg.send(JSON.stringify({
      type: 'Settings',
      mip_opt_out: true, // no Deepgram model-improvement retention: keeps our "No audio is stored" promise
      audio: {
        input: { encoding: 'linear16', sample_rate: 16000 },
        output: { encoding: 'linear16', sample_rate: 24000, container: 'none' }
      },
      agent: {
        ...(IS_FLUX ? {} : { language: 'de' }),   // Flux (v2 listen) rejects agent.language
        listen: { provider: listenProvider },
        think: { provider: { type: THINK_PROVIDER, model: THINK_MODEL }, prompt, functions },
        speak: { provider: { type: 'deepgram', model: SPEAK_MODEL } },
        greeting
      }
    }));
  });

  const reply = (fn, result) => dg.readyState === WebSocket.OPEN
    && dg.send(JSON.stringify({ type: 'FunctionCallResponse', id: fn.id, name: fn.name, content: JSON.stringify(result) }));

  async function handleFunction(fn) {
    let args = {}; try { args = JSON.parse(fn.arguments || '{}') || {}; } catch {}
    if (fn.name === 'confirm_booking') {
      const time = normTime(args.time);
      const slot = berlinIso(args.date, time);
      if (!slot) return { ok: false, error: 'Datum/Uhrzeit unklar. Bitte noch einmal bestätigen lassen.' };
      if (!inWindows(args.date, time, req.time_windows)) return { ok: false, error: 'Dieser Termin liegt außerhalb der erlaubten Zeitfenster. Bitte höflich nach einer Alternative im Zeitfenster fragen.' };
      const wantParty = Number(req.constraints?.party_size) || null;
      if (wantParty && args.party_size != null && Number(args.party_size) !== wantParty) return { ok: false, error: `Die Personenzahl muss ${wantParty} sein. Bitte korrigieren.` };
      const bring = Array.isArray(args.bring_items) ? args.bring_items.map(x => clip(x, 60)).filter(Boolean).slice(0, 8) : null;
      // earlier record_result answers + details given with the booking are kept; the booking fields always win
      const result = {
        ...withoutReserved(lastResult), ...withoutReserved(cleanDetails(args.details)),
        result_type: 'booking', ...(template.bookingKind ? { booking_kind: template.bookingKind } : {}),
        date: args.date, time, ...(args.doctor ? { doctor: clip(args.doctor, 60) } : {}), ...(wantParty ? { party_size: wantParty } : {})
      };
      lastResult = result;
      recordedOutcome = 'booked';
      await Promise.all([   // independent writes in parallel: every ms here is silence on the line (DEF-025)
        dbq('booked call', c => c.from('calls').update({ outcome: 'booked', booked_slot: slot, bring_items: bring, result }).eq('id', callId)),
        dbq('status booked', c => c.from('call_requests').update({ status: 'booked' }).eq('id', req.id)),
        dbq('event booked', c => c.from('events').insert({ request_id: req.id, source: 'voice', type: 'booking_confirmed', payload: { ...result, bring_items: bring } }))
      ]);
      toBrowser({ type: 'relay', event: 'booked', ...result, bring_items: bring });
      return { ok: true };
    }
    if (fn.name === 'record_result') {
      const details = args.details && typeof args.details === 'object' && !Array.isArray(args.details) ? args.details : null;
      if (!details || JSON.stringify(details).length > 2000) return { ok: false, error: 'details fehlt oder ist zu groß. Bitte die wichtigsten Angaben als kurze Schlüssel/Wert-Paare übergeben.' };
      const clean = cleanDetails(details);
      const summary = clip(args.summary_en, 400) || null;
      if (recordedOutcome === 'booked') {
        // already booked (e.g. Kita visit agreed): only add the extra answers, never downgrade booked -> completed
        const merged = { ...lastResult, ...withoutReserved(clean) };
        lastResult = merged;
        await dbq('result after booking', c => c.from('calls').update({ result: merged, ...(summary ? { summary_en: summary } : {}) }).eq('id', callId));
        summaryRecorded = summaryRecorded || !!summary;
        await dbq('event result', c => c.from('events').insert({ request_id: req.id, source: 'voice', type: 'result_recorded', payload: { result_type: clip(args.result_type || 'answer', 40), merged_into: 'booking' } }));
        toBrowser({ type: 'relay', event: 'result', result: merged, summary_en: summary });
        return { ok: true, note: 'Der Termin bleibt gebucht, die Angaben sind ergänzt. Jetzt in EINEM Satz verabschieden und end_call mit outcome "booked" aufrufen.' };
      }
      const result = { result_type: clip(args.result_type || 'answer', 40), ...withoutReserved(clean, ['result_type']) };
      lastResult = result;
      recordedOutcome = 'completed';
      summaryRecorded = !!summary;
      await Promise.all([
        dbq('result call', c => c.from('calls').update({ outcome: 'completed', result, summary_en: summary }).eq('id', callId)),
        dbq('status completed', c => c.from('call_requests').update({ status: 'completed' }).eq('id', req.id)),
        dbq('event result', c => c.from('events').insert({ request_id: req.id, source: 'voice', type: 'result_recorded', payload: { result_type: result.result_type } }))
      ]);
      toBrowser({ type: 'relay', event: 'result', result, summary_en: summary });
      return { ok: true };
    }
    if (fn.name === 'needs_user') {
      askedUser = true;
      const question = clip(args.question, 300);
      await dbq('status needs_user', c => c.from('call_requests').update({ status: 'needs_user' }).eq('id', req.id));
      await dbq('event needs_user', c => c.from('events').insert({ request_id: req.id, source: 'voice', type: 'needs_user', payload: { question } }));
      toBrowser({ type: 'relay', event: 'needs_user', question });
      return { ok: true };
    }
    if (fn.name === 'end_call') {
      endAfterAudio = true;
      if (saidGoodbye) muteAfterEnd = true;
      const asked = END_OUTCOMES.includes(args.outcome) ? args.outcome : 'failed';
      const outcome = asked === 'completed' && recordedOutcome === 'booked' ? 'booked' : asked;   // a booking stays a booking
      const summary = clip(args.summary_en, 400) || null;
      if (!recordedOutcome || outcome !== recordedOutcome) {
        // booked/completed without the recording function = unverified: keep the outcome, don't flip the status
        const status = { completed: 'completed', rejected: 'rejected', rejected_no_new_patients: 'rejected', needs_user: 'needs_user', failed: 'failed' }[outcome];
        await dbq('call outcome', c => c.from('calls').update({ outcome, summary_en: summary }).eq('id', callId));
        if (status && !(outcome === 'completed' && recordedOutcome === 'booked')) await dbq('status end', c => c.from('call_requests').update({ status }).eq('id', req.id));
      } else if (summary && !summaryRecorded) {   // keep record_result's summary (it describes the answer)
        await dbq('summary', c => c.from('calls').update({ summary_en: summary }).eq('id', callId));
      }
      toBrowser({ type: 'relay', event: 'ending', outcome, summary_en: summary });
      return { ok: true, note: 'Gespräch beendet. Sag nichts mehr.' };
    }
    return { ok: false, error: 'unknown function' };
  }

  dg.on('message', async (data, isBinary) => {
    if (isBinary) { if (browser.readyState === WebSocket.OPEN && !audioMuted) browser.send(data, { binary: true }); return; }
    let msg; try { msg = JSON.parse(data.toString()); } catch { return; }

    try {
      switch (msg.type) {
        case 'ConversationText': {
          const speaker = msg.role === 'assistant' ? 'agent' : 'practice';
          const text = stripStageDirections(msg.content);
          if (speaker === 'practice') { lastPracticeActivity = Date.now(); if (HOLD_RE.test(text)) holdUntil = Date.now() + HOLD_LIMIT_MS; }
          if (!text) break;
          if (speaker === 'practice') practiceHeard = true;
          if (speaker === 'agent') {
            if (muteAfterEnd) { console.log(`[call ${callId || 'no-db'}] dropped post-goodbye line`); break; }
            saidGoodbye = GOODBYE_RE.test(text);
            // Deepgram can send the end_call FunctionCallRequest BEFORE the goodbye text of the same turn (RUN-016):
            // then this goodbye is the last line; anything after it is dropped (DEF-026).
            if (endAfterAudio && saidGoodbye) muteAfterEnd = true;
          } else saidGoodbye = false;
          toBrowser({ type: 'line', speaker, text });
          if (callId) await dbq('transcript', c => c.from('transcript_lines').insert({ call_id: callId, speaker, text_de: text }));
          break;
        }
        case 'FunctionCallRequest': {
          for (const fn of msg.functions || []) {
            let result;
            const t0 = Date.now();
            try { result = await handleFunction(fn); } catch (e) { console.error('[function]', fn.name, e.message); result = { ok: false, error: 'Interner Fehler, bitte kurz fortfahren.' }; }
            console.log(`[call ${callId || 'no-db'}] ${fn.name} → ${result?.ok ? 'ok' : `rejected: ${result?.error}`} (${Date.now() - t0} ms)`);
            reply(fn, result);
          }
          break;
        }
        case 'UserStartedSpeaking': lastPracticeActivity = Date.now(); toBrowser({ type: 'barge_in' }); break;
        case 'AgentAudioDone':
          if (muteAfterEnd) audioMuted = true;   // goodbye audio finished: don't play anything after it
          agentSpeaking = false; lastPracticeActivity = Date.now();
          toBrowser({ type: 'agent_done' });
          if (endAfterAudio) setTimeout(() => finish('agent ended the call'), 1500);
          break;
        case 'AgentStartedSpeaking': agentSpeaking = true; break;
        case 'LatencyReport':   // Deepgram sends one field per report; total_latency = end of turn -> agent audio
          if (typeof msg.total_latency === 'number') {
            toBrowser({ type: 'latency', total: Number(msg.total_latency.toFixed(2)) });
            dbq('event turn_latency', c => c.from('events').insert({ request_id: req.id, source: 'voice', type: 'turn_latency', payload: { total: msg.total_latency, listen: LISTEN_MODEL } }));
          }
          break;
        case 'Error': case 'Warning':
          console.error(`[deepgram ${msg.type}]`, msg.code, msg.description);
          toBrowser({ type: 'relay', event: msg.type.toLowerCase(), code: msg.code, description: msg.description });
          break;
        default: toBrowser({ type: 'dg', event: msg.type });
      }
    } catch (e) { console.error('[call handler]', e.message); }
  });

  let audioInBytes = 0;
  browser.on('message', (data, isBinary) => {
    if (!isBinary) return;
    audioInBytes += data.length;
    if (dg.readyState === WebSocket.OPEN) dg.send(data);
  });

  let finished = false;
  async function finish(reason) {
    if (finished) return; finished = true;
    activeCalls = Math.max(0, activeCalls - 1);
    const secondsIn = (audioInBytes / 32000).toFixed(1);
    console.log(`[call ${callId || 'no-db'}] ended: ${reason} | mic audio received: ${secondsIn} s`);
    clearInterval(keepAlive);
    clearInterval(silenceWatch);
    if (callId) await closeWithoutResult(reason.startsWith('browser closed') ? 'the call was closed on the other side' : 'a technical problem with the voice service', true);
    await dbq('ended_at', c => c.from('calls').update({ ended_at: new Date().toISOString() }).eq('id', callId));
    await dbq('event call_ended', c => c.from('events').insert({ request_id: req.id, source: 'voice', type: 'call_ended', payload: { reason, mic_seconds: Number(secondsIn) } }));
    toBrowser({ type: 'relay', event: 'call_ended', reason });
    try { dg.close(); } catch {}
    try { browser.close(); } catch {}
  }

  browser.on('close', () => finish('browser closed'));
  dg.on('close', (code, reason) => finish(`deepgram closed ${code} ${reason}`));
  dg.on('error', err => { console.error('[deepgram ws]', err.message); finish('deepgram error'); });
  // the browser left while the request/call rows were being set up: its 'close' fired before the handler above existed
  if (browserGone || browser.readyState !== WebSocket.OPEN) finish('browser closed before the call started');
});

// ---------- /listen: intake voice input, speech-to-text in the user's language (nothing stored) ----------
listenWss.on('connection', (browser, httpReq) => {
  activeCalls += 1;
  const lang = LISTEN_LANGS[new URL(httpReq.url, 'http://x').searchParams.get('lang')];
  const toBrowser = obj => browser.readyState === WebSocket.OPEN && browser.send(JSON.stringify(obj));
  const qs = new URLSearchParams({ model: 'nova-3', language: lang, encoding: 'linear16', sample_rate: '16000', interim_results: 'true', smart_format: 'true', punctuate: 'true', mip_opt_out: 'true' });
  const dg = new WebSocket(`wss://api.deepgram.com/v1/listen?${qs}`, { headers: { Authorization: `Token ${DG_KEY}` } });
  const pending = [];
  let closed = false;

  const keepAlive = setInterval(() => dg.readyState === WebSocket.OPEN && dg.send(JSON.stringify({ type: 'KeepAlive' })), 8000);
  const maxTimer = setTimeout(() => stop('max duration'), MAX_LISTEN_SECONDS * 1000);

  dg.on('open', () => { toBrowser({ type: 'ready', lang }); while (pending.length) dg.send(pending.shift()); });
  dg.on('unexpected-response', (_q, res) => { toBrowser({ type: 'error', message: `speech service ${res.statusCode}` }); done('dg rejected'); });
  dg.on('message', data => {
    let m; try { m = JSON.parse(data.toString()); } catch { return; }
    if (m.type === 'Results') {
      const text = m.channel?.alternatives?.[0]?.transcript || '';
      if (text) toBrowser({ type: 'transcript', text, is_final: !!m.is_final, speech_final: !!m.speech_final });
    }
  });
  dg.on('close', () => done('dg closed'));
  dg.on('error', e => { console.error('[listen dg]', e.message); done('dg error'); });

  browser.on('message', (data, isBinary) => {
    if (!isBinary) {
      let m; try { m = JSON.parse(data.toString()); } catch { return; }
      if (m.type === 'stop') stop('user stopped');
      return;
    }
    if (dg.readyState === WebSocket.OPEN) dg.send(data);
    else if (dg.readyState === WebSocket.CONNECTING && pending.length < 50) pending.push(data);
  });
  browser.on('close', () => stop('browser closed'));

  // Ask Deepgram to flush final results, then close (closing happens on dg 'close').
  function stop(reason) {
    if (dg.readyState === WebSocket.OPEN) { try { dg.send(JSON.stringify({ type: 'CloseStream' })); } catch {} setTimeout(() => done(reason), 3000); }
    else done(reason);
  }
  function done(reason) {
    if (closed) return; closed = true;
    activeCalls = Math.max(0, activeCalls - 1);
    clearInterval(keepAlive); clearTimeout(maxTimer);
    toBrowser({ type: 'closed', reason });
    try { dg.close(); } catch {}
    try { browser.close(); } catch {}
  }
});

export { buildAgent, berlinIso, originAllowed };

// Only listen when run directly (lets tests import buildAgent without starting the server).
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  server.listen(PORT, process.env.HOST || '127.0.0.1', () => console.log(`Voice relay on http://${process.env.HOST || '127.0.0.1'}:${PORT}  (think: ${THINK_PROVIDER}/${THINK_MODEL}, speak: ${SPEAK_MODEL}, listen: ${LISTEN_MODEL})`));
}
