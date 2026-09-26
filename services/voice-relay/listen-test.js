// Tests the /listen endpoint (intake voice input): streams 16 kHz mono linear16 audio in real time and prints the transcript.
// Usage: node listen-test.js <lang> <file.raw | "tts:<text>">     (relay must be running on :8787, or set PORT)
//   file.raw  = raw s16le 16 kHz mono, e.g. ffmpeg -i sample.ogg -t 20 -ac 1 -ar 16000 -f s16le sample.raw
//   tts:<txt> = synthesise with Deepgram Aura (only languages Aura speaks, e.g. de, en, es, fr)
// Also checks that a foreign Origin and an unsupported language are rejected.
import dotenv from 'dotenv';
import fs from 'node:fs';
import { WebSocket } from 'ws';
import { fileURLToPath } from 'node:url';

dotenv.config({ path: fileURLToPath(new URL('./.env', import.meta.url)) });
const [lang = 'de', src = 'tts:Guten Tag, ich brauche einen Termin beim Bürgeramt.'] = process.argv.slice(2);
const port = process.env.PORT || 8787;
const base = `ws://127.0.0.1:${port}/listen`;

const expectReject = (url, headers) => new Promise(res => {
  const ws = new WebSocket(url, { headers });
  ws.on('unexpected-response', (_q, r) => res(r.statusCode));
  ws.on('open', () => { ws.close(); res('OPENED (should have been rejected)'); });
  ws.on('error', () => res('error'));
});
console.log('foreign origin →', await expectReject(`${base}?lang=de`, { Origin: 'https://evil.example' }));
console.log('unsupported lang →', await expectReject(`${base}?lang=xx`, {}));

let audio;
if (src.startsWith('tts:')) {
  const r = await fetch('https://api.deepgram.com/v1/speak?model=aura-2-julius-de&encoding=linear16&sample_rate=16000&container=none', {
    method: 'POST', headers: { Authorization: `Token ${process.env.DEEPGRAM_API_KEY}`, 'Content-Type': 'application/json' }, body: JSON.stringify({ text: src.slice(4) })
  });
  audio = Buffer.from(await r.arrayBuffer());
} else audio = fs.readFileSync(src);

const ws = new WebSocket(`${base}?lang=${lang}`, { headers: { Origin: `http://127.0.0.1:${port}` } });
const finals = []; let interims = 0; const t0 = Date.now(); let firstText = null;
ws.on('message', d => {
  const m = JSON.parse(d.toString());
  if (m.type === 'transcript') {
    if (firstText === null) firstText = Date.now() - t0;
    if (m.is_final) { finals.push(m.text); console.log(`[final] ${m.text}`); } else interims++;
  } else console.log(`[${m.type}]`, m.lang || m.reason || m.message || '');
});
ws.on('open', async () => {
  for (let off = 0; off < audio.length; off += 3200) {         // 100 ms chunks, real time
    ws.send(audio.subarray(off, off + 3200));
    await new Promise(r => setTimeout(r, 100));
  }
  ws.send(JSON.stringify({ type: 'stop' }));
});
ws.on('close', () => {
  console.log(`\n${lang}: ${finals.length} final segments, ${interims} interim updates, first text after ${firstText} ms`);
  console.log(`text: ${finals.join(' ')}`);
  process.exit(finals.length ? 0 : 1);
});
setTimeout(() => ws.close(), 90000);
