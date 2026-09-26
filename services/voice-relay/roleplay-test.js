// Automated role-play: a synthetic German receptionist (Deepgram TTS) talks to the agent through the relay.
// Usage: node roleplay-test.js <requestId> [scenario]   (relay must be running on :8787)
// Scenario "book": offers a slot OUTSIDE the window first, then the first allowed window, then confirms the read-back.
import dotenv from 'dotenv';
import { WebSocket } from 'ws';
import { fileURLToPath } from 'node:url';
import { createClient } from '@supabase/supabase-js';

dotenv.config({ path: fileURLToPath(new URL('./.env', import.meta.url)) });
const requestId = process.argv[2];
if (!requestId) { console.error('usage: node roleplay-test.js <requestId>'); process.exit(1); }

const db = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_ROLE_KEY, { auth: { persistSession: false } });
const { data: req } = await db.from('call_requests').select('practice_name,time_windows').eq('id', requestId).single();
const w = req.time_windows[0];
const d = new Date(`${w.date}T12:00:00`);
const dayDe = d.toLocaleDateString('de-DE', { weekday: 'long', day: 'numeric', month: 'long' });
const inside = w.from.slice(0, 2) === '08' ? '9' : String(Number(w.from.slice(0, 2)) + 1);

const lines = [
  `${req.practice_name}, guten Tag?`,
  'Ja, verstehe. Ist die Patientin neu bei uns, und hat sie eine Überweisung?',
  'Ich könnte ihr einen Termin am Samstag um siebzehn Uhr anbieten.',
  `Dann ${dayDe} um ${inside} Uhr, geht das?`,
  'Ja, richtig. Bitte die Versichertenkarte mitbringen.',
  'Gerne, auf Wiederhören.'
];

async function tts(text) {
  const r = await fetch('https://api.deepgram.com/v1/speak?model=aura-2-julius-de&encoding=linear16&sample_rate=16000&container=none', {
    method: 'POST', headers: { Authorization: `Token ${process.env.DEEPGRAM_API_KEY}`, 'Content-Type': 'application/json' }, body: JSON.stringify({ text })
  });
  if (!r.ok) throw new Error(`TTS ${r.status} ${await r.text()}`);
  return Buffer.from(await r.arrayBuffer());
}

console.log('Generating receptionist voice…');
const audio = await Promise.all(lines.map(tts));

const ws = new WebSocket(`ws://127.0.0.1:${process.env.PORT || 8787}/call?request=${requestId}`);
let turn = 0; let speaking = false; const started = Date.now();
const silence = Buffer.alloc(3200);
const silenceTimer = setInterval(() => { if (!speaking && ws.readyState === 1) ws.send(silence); }, 100);

async function say(i) {
  speaking = true;
  console.log(`\n[practice → ] ${lines[i]}`);
  const buf = audio[i];
  for (let off = 0; off < buf.length; off += 3200) {          // stream in real time, 100 ms chunks
    ws.send(buf.subarray(off, off + 3200));
    await new Promise(r => setTimeout(r, 100));
  }
  speaking = false;
}

ws.on('message', async (data, bin) => {
  if (bin) return;
  const m = JSON.parse(data.toString());
  if (m.type === 'line') console.log(`[${m.speaker === 'agent' ? 'agent' : 'heard  '}] ${m.text}`);
  if (m.type === 'latency') console.log(`   (latency ${m.total}s)`);
  if (m.type === 'relay' && m.event !== 'call_started') console.log(`   >> relay: ${m.event} ${JSON.stringify({ ...m, type: undefined, event: undefined })}`);
  if (m.type === 'agent_done' && turn < lines.length) { await new Promise(r => setTimeout(r, 600)); await say(turn++); }
});
ws.on('close', async () => {
  clearInterval(silenceTimer);
  const { data: call } = await db.from('calls').select('outcome,booked_slot,bring_items,summary_en').eq('request_id', requestId).order('created_at', { ascending: false }).limit(1).single();
  const { data: r } = await db.from('call_requests').select('status').eq('id', requestId).single();
  console.log(`\nDone in ${((Date.now() - started) / 1000).toFixed(0)} s → request status: ${r.status}, call:`, call);
  process.exit(0);
});
setTimeout(() => ws.close(), 180000);
