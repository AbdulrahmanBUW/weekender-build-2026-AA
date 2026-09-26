// Voice relay: browser mic <-> Deepgram Voice Agent (German), live transcript -> Supabase.
// The Deepgram key and the Supabase service key stay on this server; the browser never sees them.
import dotenv from 'dotenv';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

dotenv.config({ path: fileURLToPath(new URL('./.env', import.meta.url)) });
import { WebSocketServer, WebSocket } from 'ws';
import { createClient } from '@supabase/supabase-js';

const PORT = Number(process.env.PORT || 8787);
const DG_KEY = process.env.DEEPGRAM_API_KEY;
const DG_URL = 'wss://agent.deepgram.com/v1/agent/converse';
const THINK_PROVIDER = process.env.THINK_PROVIDER || 'anthropic';
const THINK_MODEL = process.env.THINK_MODEL || 'claude-sonnet-4-20250514';
const SPEAK_MODEL = process.env.SPEAK_MODEL || 'aura-2-viktoria-de';
const LISTEN_MODEL = process.env.LISTEN_MODEL || 'nova-3';
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

// ---------- prompt building ----------
const REASON_DE = {
  first_visit: 'Erstuntersuchung', checkup: 'Vorsorgeuntersuchung', acute: 'Akuttermin',
  follow_up: 'Folgetermin', specialist: 'Facharzttermin', other: 'Termin'
};

function windowsText(windows = []) {
  return windows.map(w => {
    const d = new Date(`${w.date}T12:00:00`);
    const day = d.toLocaleDateString('de-DE', { weekday: 'long', day: '2-digit', month: '2-digit', year: 'numeric' });
    return `- ${day}, ${w.from}–${w.to} Uhr`;
  }).join('\n');
}

function buildAgent(req) {
  const reason = REASON_DE[req.reason_category] || 'Termin';
  const greeting = `Guten Tag, hier spricht die KI-Assistentin von ${req.patient_name}. `
    + `${req.patient_name.split(' ')[0]} spricht leider noch kein Deutsch, deshalb rufe ich in ihrem Auftrag an. `
    + `Ich möchte gern einen Termin für eine ${reason} vereinbaren.`;

  const prompt = `Du bist eine freundliche, höfliche KI-Assistentin am Telefon. Du rufst im Auftrag von ${req.patient_name} in der Praxis "${req.practice_name}" an, um einen Termin zu vereinbaren. Du sprichst ausschließlich Deutsch, in kurzen, natürlichen Sätzen (höchstens zwei Sätze pro Antwort).

FAKTEN (nur diese verwenden, nichts erfinden):
- Patientin/Patient: ${req.patient_name}
- Geburtsdatum: ${req.patient_dob || 'unbekannt'}
- Versicherung: ${req.insurance_type === 'pkv' ? 'privat' : req.insurance_type === 'gkv' ? 'gesetzlich' : 'unbekannt'}${req.insurance_name ? `, ${req.insurance_name}` : ''}
- Neupatient: ${req.is_new_patient ? 'ja' : 'nein'}
- Überweisung: ${req.has_referral ? 'ja' : 'nein'}
- Anliegen: ${reason}

ERLAUBTE ZEITFENSTER (nur Termine darin annehmen):
${windowsText(req.time_windows)}

${req.call_brief_de ? `VORBEREITETES BRIEFING:\n${req.call_brief_de}\n` : ''}
REGELN:
1. Du bist eine KI und sagst das ehrlich. Gib dich niemals als die Patientin aus.
2. Nenne niemals Symptome oder Diagnosen. Wenn gefragt: "Es geht um eine ${reason}, weitere Details bespricht sie gern persönlich."
3. Namen buchstabierst du auf Nachfrage mit dem deutschen Buchstabieralphabet (z. B. "P wie Paula").
4. Nimm nur einen Termin innerhalb der erlaubten Zeitfenster an. Liegt ein Angebot außerhalb, frage höflich nach einer Alternative im Zeitfenster.
5. Bevor du bestätigst: wiederhole Wochentag, Datum, Uhrzeit und Ärztin/Arzt und warte auf ein "Ja"/"Richtig". Erst danach rufst du confirm_booking auf.
6. Wenn die Praxis etwas fragt, das du nicht weißt, oder auf der Patientin besteht: rufe needs_user auf und biete einen Rückruf an.
7. Wenn keine Neupatienten angenommen werden oder kein Termin möglich ist: bedanke dich und rufe end_call mit dem passenden Ergebnis auf.
8. Nach confirm_booking bedankst du dich kurz, verabschiedest dich und rufst end_call mit outcome "booked" auf.`;

  const keyterms = [...new Set([...req.patient_name.split(/\s+/), req.practice_name.replace(/^(Praxis|Hausarztpraxis|Kinderarztpraxis)\s*/i, ''), 'KI-Assistentin'])]
    .filter(Boolean).slice(0, 10);

  return { greeting, prompt, keyterms };
}

const FUNCTIONS = [
  {
    name: 'confirm_booking',
    description: 'Call ONLY after the practice explicitly confirmed the read-back. Records the booked appointment.',
    parameters: {
      type: 'object',
      properties: {
        date: { type: 'string', description: 'Appointment date, YYYY-MM-DD' },
        time: { type: 'string', description: 'Appointment time, HH:MM (24h)' },
        doctor: { type: 'string', description: 'Doctor name if mentioned' },
        bring_items: { type: 'array', items: { type: 'string' }, description: 'Things the patient must bring, in German (e.g. Versichertenkarte, Überweisung)' }
      },
      required: ['date', 'time']
    }
  },
  {
    name: 'needs_user',
    description: 'The practice asked something only the patient can answer, or insists on talking to the patient.',
    parameters: { type: 'object', properties: { question: { type: 'string', description: 'What the practice wants to know, in English' } }, required: ['question'] }
  },
  {
    name: 'end_call',
    description: 'End the call after saying goodbye.',
    parameters: {
      type: 'object',
      properties: { outcome: { type: 'string', enum: ['booked', 'rejected_no_new_patients', 'needs_user', 'failed'] }, summary_en: { type: 'string', description: 'One-sentence English summary for the patient' } },
      required: ['outcome']
    }
  }
];

function inWindows(date, time, windows = []) {
  return windows.some(w => w.date === date && time >= w.from && time <= w.to);
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
    id, patient_name: 'Priya Sharma', patient_dob: '2002-03-14', insurance_type: 'gkv', insurance_name: 'Techniker Krankenkasse',
    practice_name: 'Hausarztpraxis Dr. Weber', reason_category: 'first_visit', is_new_patient: true, has_referral: false,
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

// ---------- WS: one browser connection = one call ----------
const wss = new WebSocketServer({ server, path: '/call' });

wss.on('connection', async (browser, httpReq) => {
  const url = new URL(httpReq.url, 'http://x');
  const requestId = url.searchParams.get('request') || DEMO_REQUEST_ID;
  const toBrowser = obj => browser.readyState === WebSocket.OPEN && browser.send(JSON.stringify(obj));

  const req = await loadRequest(requestId);
  const { greeting, prompt, keyterms } = buildAgent(req);

  const call = await dbq('create call', c => c.from('calls')
    .insert({ request_id: req.id, provider: 'deepgram-browser', started_at: new Date().toISOString() })
    .select('id').single());
  const callId = call?.id || null;
  await dbq('status calling', c => c.from('call_requests').update({ status: 'calling' }).eq('id', req.id));
  await dbq('event call_started', c => c.from('events').insert({ request_id: req.id, source: 'voice', type: 'call_started', payload: { provider: 'deepgram-browser', call_id: callId } }));
  toBrowser({ type: 'relay', event: 'call_started', callId, requestId: req.id, patient: req.patient_name, practice: req.practice_name, saving: !!db });

  const dg = new WebSocket(DG_URL, { headers: { Authorization: `Token ${DG_KEY}` } });
  let endAfterAudio = false;
  let outcomeRecorded = false;
  const keepAlive = setInterval(() => dg.readyState === WebSocket.OPEN && dg.send(JSON.stringify({ type: 'KeepAlive' })), 8000);

  dg.on('open', () => {
    dg.send(JSON.stringify({
      type: 'Settings',
      audio: {
        input: { encoding: 'linear16', sample_rate: 16000 },
        output: { encoding: 'linear16', sample_rate: 24000, container: 'none' }
      },
      agent: {
        language: 'de',
        listen: { provider: { type: 'deepgram', model: LISTEN_MODEL, keyterms } },
        think: { provider: { type: THINK_PROVIDER, model: THINK_MODEL }, prompt, functions: FUNCTIONS },
        speak: { provider: { type: 'deepgram', model: SPEAK_MODEL } },
        greeting
      }
    }));
  });

  dg.on('message', async (data, isBinary) => {
    if (isBinary) { if (browser.readyState === WebSocket.OPEN) browser.send(data, { binary: true }); return; }
    let msg; try { msg = JSON.parse(data.toString()); } catch { return; }

    switch (msg.type) {
      case 'ConversationText': {
        const speaker = msg.role === 'assistant' ? 'agent' : 'practice';
        toBrowser({ type: 'line', speaker, text: msg.content });
        if (callId) await dbq('transcript', c => c.from('transcript_lines').insert({ call_id: callId, speaker, text_de: msg.content }));
        break;
      }
      case 'FunctionCallRequest': {
        for (const fn of msg.functions || []) {
          let args = {}; try { args = JSON.parse(fn.arguments || '{}'); } catch {}
          let result = { ok: true };
          if (fn.name === 'confirm_booking') {
            if (!inWindows(args.date, args.time, req.time_windows)) {
              result = { ok: false, error: 'Dieser Termin liegt außerhalb der erlaubten Zeitfenster. Bitte höflich nach einer Alternative im Zeitfenster fragen.' };
            } else {
              outcomeRecorded = true;
              const slot = new Date(`${args.date}T${args.time}:00+02:00`).toISOString();
              await dbq('booked call', c => c.from('calls').update({ outcome: 'booked', booked_slot: slot, bring_items: args.bring_items || null }).eq('id', callId));
              await dbq('status booked', c => c.from('call_requests').update({ status: 'booked' }).eq('id', req.id));
              await dbq('event booked', c => c.from('events').insert({ request_id: req.id, source: 'voice', type: 'booking_confirmed', payload: args }));
              toBrowser({ type: 'relay', event: 'booked', ...args });
            }
          } else if (fn.name === 'needs_user') {
            await dbq('status needs_user', c => c.from('call_requests').update({ status: 'needs_user' }).eq('id', req.id));
            await dbq('event needs_user', c => c.from('events').insert({ request_id: req.id, source: 'voice', type: 'needs_user', payload: args }));
            toBrowser({ type: 'relay', event: 'needs_user', ...args });
          } else if (fn.name === 'end_call') {
            endAfterAudio = true;
            if (!outcomeRecorded || args.outcome !== 'booked') {
              const status = { rejected_no_new_patients: 'rejected', needs_user: 'needs_user', failed: 'failed' }[args.outcome];
              await dbq('call outcome', c => c.from('calls').update({ outcome: args.outcome, summary_en: args.summary_en || null }).eq('id', callId));
              if (status) await dbq('status end', c => c.from('call_requests').update({ status }).eq('id', req.id));
            } else if (args.summary_en) {
              await dbq('summary', c => c.from('calls').update({ summary_en: args.summary_en }).eq('id', callId));
            }
            toBrowser({ type: 'relay', event: 'ending', ...args });
          }
          dg.send(JSON.stringify({ type: 'FunctionCallResponse', id: fn.id, name: fn.name, content: JSON.stringify(result) }));
        }
        break;
      }
      case 'UserStartedSpeaking': toBrowser({ type: 'barge_in' }); break;
      case 'AgentAudioDone':
        toBrowser({ type: 'agent_done' });
        if (endAfterAudio) setTimeout(() => finish('agent ended the call'), 1500);
        break;
      case 'AgentStartedSpeaking': toBrowser({ type: 'latency', total: msg.total_latency }); break;
      case 'Error': case 'Warning':
        console.error(`[deepgram ${msg.type}]`, msg.code, msg.description);
        toBrowser({ type: 'relay', event: msg.type.toLowerCase(), code: msg.code, description: msg.description });
        break;
      default: toBrowser({ type: 'dg', event: msg.type });
    }
  });

  browser.on('message', (data, isBinary) => {
    if (isBinary && dg.readyState === WebSocket.OPEN) dg.send(data);
  });

  let finished = false;
  async function finish(reason) {
    if (finished) return; finished = true;
    clearInterval(keepAlive);
    await dbq('ended_at', c => c.from('calls').update({ ended_at: new Date().toISOString() }).eq('id', callId));
    await dbq('event call_ended', c => c.from('events').insert({ request_id: req.id, source: 'voice', type: 'call_ended', payload: { reason } }));
    toBrowser({ type: 'relay', event: 'call_ended', reason });
    try { dg.close(); } catch {}
    try { browser.close(); } catch {}
  }

  browser.on('close', () => finish('browser closed'));
  dg.on('close', (code, reason) => finish(`deepgram closed ${code} ${reason}`));
  dg.on('error', err => { console.error('[deepgram ws]', err.message); finish('deepgram error'); });
});

server.listen(PORT, '127.0.0.1', () => console.log(`Voice relay on http://127.0.0.1:${PORT}  (think: ${THINK_PROVIDER}/${THINK_MODEL}, speak: ${SPEAK_MODEL}, listen: ${LISTEN_MODEL})`));
