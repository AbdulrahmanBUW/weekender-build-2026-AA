// Automated role-play for an INFORMATION task: a synthetic German pharmacy (Deepgram TTS) answers a stock question.
// Also checks: honest answer to "Sind Sie eine KI?", waiting on "Moment bitte", no bracketed stage directions.
// Usage: node roleplay-pharmacy.js <pharmacy_question requestId>   (relay must be running on :8787, or set PORT)
// Expect: calls.outcome = completed, calls.result filled, request status = completed.
import dotenv from 'dotenv';
import { WebSocket } from 'ws';
import { fileURLToPath } from 'node:url';
import { createClient } from '@supabase/supabase-js';

dotenv.config({ path: fileURLToPath(new URL('./.env', import.meta.url)) });
const requestId = process.argv[2];
if (!requestId) { console.error('usage: node roleplay-pharmacy.js <requestId>'); process.exit(1); }

const db = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_ROLE_KEY, { auth: { persistSession: false } });
const { data: req } = await db.from('call_requests').select('practice_name,task_type').eq('id', requestId).single();
if (req.task_type !== 'pharmacy_question') console.warn(`warning: task_type is ${req.task_type}, not pharmacy_question`);

// [text, extra pause in ms after the agent finished before this line is spoken]
const lines = [
  [`${req.practice_name}, guten Tag?`, 0],
  ['Sind Sie eigentlich eine KI?', 0],
  ['Ah, okay. Moment bitte, ich schaue kurz nach.', 0],
  ['So, ja, Ibuprofen 400 haben wir da. Zwanzig Tabletten kosten drei Euro neunundvierzig, abholen kann sie es heute bis halb sieben.', 6000],
  ['Ja, genau, richtig.', 0],
  ['Gerne, auf Wiederhören.', 0]
];

async function tts(text) {
  const r = await fetch('https://api.deepgram.com/v1/speak?model=aura-2-julius-de&encoding=linear16&sample_rate=16000&container=none', {
    method: 'POST', headers: { Authorization: `Token ${process.env.DEEPGRAM_API_KEY}`, 'Content-Type': 'application/json' }, body: JSON.stringify({ text })
  });
  if (!r.ok) throw new Error(`TTS ${r.status} ${await r.text()}`);
  return Buffer.from(await r.arrayBuffer());
}

console.log('Generating pharmacy voice…');
const audio = await Promise.all(lines.map(([t]) => tts(t)));

const ws = new WebSocket(`ws://127.0.0.1:${process.env.PORT || 8787}/call?request=${requestId}`, { headers: { Origin: `http://127.0.0.1:${process.env.PORT || 8787}` } });
let turn = 0; let speaking = false; const started = Date.now();
const agentLines = [];
const silence = Buffer.alloc(3200);
const silenceTimer = setInterval(() => { if (!speaking && ws.readyState === 1) ws.send(silence); }, 100);

async function say(i) {
  speaking = true;
  console.log(`\n[pharmacy → ] ${lines[i][0]}`);
  const buf = audio[i];
  for (let off = 0; off < buf.length; off += 3200) { ws.send(buf.subarray(off, off + 3200)); await new Promise(r => setTimeout(r, 100)); }
  speaking = false;
}

ws.on('message', async (data, bin) => {
  if (bin) return;
  const m = JSON.parse(data.toString());
  if (m.type === 'line') { console.log(`[${m.speaker === 'agent' ? 'agent' : 'heard  '}] ${m.text}`); if (m.speaker === 'agent') agentLines.push(m.text); }
  if (m.type === 'relay' && m.event === 'call_started') console.log(`task: ${m.task_type} (${m.task_label}), user language ${m.user_language}`);
  if (m.type === 'latency') console.log(`   (latency ${m.total}s)`);
  if (m.type === 'relay' && m.event !== 'call_started') console.log(`   >> relay: ${m.event} ${JSON.stringify({ ...m, type: undefined, event: undefined })}`);
  if (m.type === 'agent_done' && turn < lines.length) { const i = turn++; await new Promise(r => setTimeout(r, 600 + lines[i][1])); await say(i); }
});
ws.on('close', async () => {
  clearInterval(silenceTimer);
  const { data: call } = await db.from('calls').select('id,outcome,result,summary_en,disclosure_variant').eq('request_id', requestId).order('created_at', { ascending: false }).limit(1).single();
  const { data: r } = await db.from('call_requests').select('status').eq('id', requestId).single();
  const { data: tl } = await db.from('transcript_lines').select('text_de').eq('call_id', call.id);
  const brackets = (tl || []).filter(l => /[()[\]]/.test(l.text_de)).length;
  const kiAnswer = agentLines.some(t => /\bKI\b/.test(t) && /ja/i.test(t));
  console.log(`\nDone in ${((Date.now() - started) / 1000).toFixed(0)} s → request status: ${r.status}, call:`, call);
  console.log(`checks: outcome completed=${call.outcome === 'completed'} · result filled=${!!call.result} · status completed=${r.status === 'completed'} · disclosure=${call.disclosure_variant} · bracket lines saved=${brackets} · confirmed KI=${kiAnswer}`);
  process.exit(0);
});
setTimeout(() => ws.close(), 180000);
