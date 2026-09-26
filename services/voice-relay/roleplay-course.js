// Automated role-play for course_enquiry: a synthetic German music-school receptionist (Deepgram TTS) talks to the agent.
// Scenario: asks the child's age -> offers a trial lesson OUTSIDE the windows (Saturday) -> then a Thursday slot INSIDE
// a window -> confirms the read-back. Side questions (language, price, waiting list) are answered once when the agent asks.
// Usage: node roleplay-course.js <course_enquiry requestId>   (relay must be running on :8787, or set PORT)
// Expect: calls.outcome = booked, booked_slot inside the window, result.booking_kind = trial_lesson, request status booked.
import dotenv from 'dotenv';
import { WebSocket } from 'ws';
import { fileURLToPath } from 'node:url';
import { createClient } from '@supabase/supabase-js';

dotenv.config({ path: fileURLToPath(new URL('./.env', import.meta.url)) });
const requestId = process.argv[2];
if (!requestId) { console.error('usage: node roleplay-course.js <requestId>'); process.exit(1); }
const PORT = process.env.PORT || 8787;

const db = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_ROLE_KEY, { auth: { persistSession: false } });
const { data: req } = await db.from('call_requests').select('practice_name,task_type,time_windows').eq('id', requestId).single();
if (req.task_type !== 'course_enquiry') console.warn(`warning: task_type is ${req.task_type}, not course_enquiry`);
if (!req.time_windows?.length) { console.error('the task needs time_windows (the trial lesson is booked inside one)'); process.exit(1); }
const dayOf = w => new Date(`${w.date}T12:00:00`);
const w = req.time_windows.find(x => dayOf(x).getDay() === 4) || req.time_windows[0];   // prefer a Thursday window
const dayDe = dayOf(w).toLocaleDateString('de-DE', { weekday: 'long', day: 'numeric', month: 'long' });
const insideHour = Math.min(Number(w.from.slice(0, 2)) + 1, Number(w.to.slice(0, 2)));
const weekdayWord = dayOf(w).toLocaleDateString('de-DE', { weekday: 'long' }).toLowerCase();

// main script, spoken in order
const lines = [
  `${req.practice_name}, guten Tag?`,
  'Ja, gern. Wie alt ist das Kind denn?',
  'Ah, schön. Für die Gruppe hätte ich eine Probestunde am Samstag um zehn Uhr.',
  `Oder ${dayDe} um ${insideHour} Uhr, die Gruppe trifft sich immer ${weekdayWord}s. Geht das?`,
  'Ja, richtig. Die Probestunde ist kostenlos. Bitte bequeme Kleidung und Hausschuhe mitbringen.',
  'Gerne, auf Wiederhören.'
];
// side answers: said once, only when the agent's last turn asks about the topic
const extras = [
  { re: /sprache|russisch|englisch|zweisprachig/i, text: 'Unterrichtet wird auf Deutsch, eine Lehrerin spricht aber auch Russisch.' },
  { re: /\bkostet\b|\bpreis|\bgebühr|\bkosten\b|monatlich/i, text: 'Der Kurs kostet danach achtunddreißig Euro im Monat.' },
  { re: /warteliste/i, text: 'Eine Warteliste haben wir auch, aber im Moment ist noch ein Platz frei.' },
  { re: /platz frei|freien platz|noch (einen )?platz/i, text: 'Ja, in der Gruppe ist gerade noch ein Platz frei.' },
  // reusable: the agent's clarification questions ("habe ich richtig verstanden …?") must not eat a script line (RUN-016 verification)
  { re: /richtig verstanden|habe ich (das |sie )?richtig/i, text: 'Ja, genau.', reusable: true }
];

async function tts(text) {
  const r = await fetch('https://api.deepgram.com/v1/speak?model=aura-2-julius-de&encoding=linear16&sample_rate=16000&container=none', {
    method: 'POST', headers: { Authorization: `Token ${process.env.DEEPGRAM_API_KEY}`, 'Content-Type': 'application/json' }, body: JSON.stringify({ text })
  });
  if (!r.ok) throw new Error(`TTS ${r.status} ${await r.text()}`);
  return Buffer.from(await r.arrayBuffer());
}

console.log(`Window used: ${w.date} ${w.from}–${w.to} → in-window offer ${dayDe} ${insideHour}:00. Generating receptionist voice…`);
const audio = await Promise.all(lines.map(tts));
const extraAudio = await Promise.all(extras.map(e => tts(e.text)));

const ws = new WebSocket(`ws://127.0.0.1:${PORT}/call?request=${requestId}`, { headers: { Origin: `http://127.0.0.1:${PORT}` } });
let turn = 0; let speaking = false; let agentTurn = ''; const started = Date.now();
const agentLines = [];
const silence = Buffer.alloc(3200);
const silenceTimer = setInterval(() => { if (!speaking && ws.readyState === 1) ws.send(silence); }, 100);

async function play(text, buf) {
  speaking = true;
  console.log(`\n[school → ] ${text}`);
  for (let off = 0; off < buf.length; off += 3200) { ws.send(buf.subarray(off, off + 3200)); await new Promise(r => setTimeout(r, 100)); }
  speaking = false;
}

ws.on('message', async (data, bin) => {
  if (bin) return;
  const m = JSON.parse(data.toString());
  if (m.type === 'line') { console.log(`[${m.speaker === 'agent' ? 'agent' : 'heard  '}] ${m.text}`); if (m.speaker === 'agent') { agentLines.push(m.text); agentTurn += ` ${m.text}`; } }
  if (m.type === 'relay' && m.event === 'call_started') console.log(`task: ${m.task_type} (${m.task_label}), user language ${m.user_language}`);
  if (m.type === 'latency') console.log(`   (latency ${m.total}s)`);
  if (m.type === 'relay' && m.event !== 'call_started') console.log(`   >> relay: ${m.event} ${JSON.stringify({ ...m, type: undefined, event: undefined })}`);
  if (m.type !== 'agent_done' || speaking) return;
  const asked = agentTurn; agentTurn = '';
  await new Promise(r => setTimeout(r, 600));
  const ex = turn > 1 && asked.includes('?') ? extras.findIndex(e => !e.used && e.re.test(asked)) : -1;
  if (ex >= 0) { if (!extras[ex].reusable) extras[ex].used = true; return play(extras[ex].text, extraAudio[ex]); }
  if (turn < lines.length) { const i = turn++; await play(lines[i], audio[i]); }
  else setTimeout(() => ws.close(), 4000);   // script finished: hang up like a real receptionist
});

ws.on('close', async () => {
  clearInterval(silenceTimer);
  await new Promise(res => setTimeout(res, 2000));   // let the relay write the outcome first (hang-up case)
  const { data: call } = await db.from('calls').select('id,outcome,booked_slot,bring_items,summary_en,result,disclosure_variant').eq('request_id', requestId).order('created_at', { ascending: false }).limit(1).single();
  const { data: r } = await db.from('call_requests').select('status').eq('id', requestId).single();
  const { data: tl } = await db.from('transcript_lines').select('text_de').eq('call_id', call.id);
  const brackets = (tl || []).filter(l => /[()[\]]/.test(l.text_de)).length;
  const berlin = call.booked_slot ? new Intl.DateTimeFormat('sv-SE', { timeZone: 'Europe/Berlin', dateStyle: 'short', timeStyle: 'short' }).format(new Date(call.booked_slot)) : null;
  const inWindow = !!berlin && req.time_windows.some(x => berlin.slice(0, 10) === x.date && berlin.slice(11, 16) >= x.from.slice(0, 5) && berlin.slice(11, 16) <= x.to.slice(0, 5));
  console.log(`\nDone in ${((Date.now() - started) / 1000).toFixed(0)} s → request status: ${r.status}, call:`, call);
  console.log(`checks: outcome booked=${call.outcome === 'booked'} · slot ${berlin || '-'} Berlin inside window=${inWindow} · booking_kind=${call.result?.booking_kind} · status booked=${r.status === 'booked'} · disclosure=${call.disclosure_variant} · bracket lines saved=${brackets} · extras answered=${extras.filter(e => e.used).length}`);
  // n8n 06 writes the result in the parent's language a few seconds after the outcome
  for (let i = 0; i < 12; i++) {
    const { data: s } = await db.from('calls').select('summary_user').eq('id', call.id).single();
    if (s?.summary_user) { console.log(`summary_user (parent's language): ${s.summary_user}`); break; }
    await new Promise(res => setTimeout(res, 2500));
  }
  process.exit(0);
});
setTimeout(() => ws.close(), 240000);
