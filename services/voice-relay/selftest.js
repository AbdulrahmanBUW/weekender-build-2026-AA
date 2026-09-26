// Headless check: connects to the running relay, streams 6 s of silence,
// and prints what Deepgram sends back (settings applied, German greeting, latency).
import { WebSocket } from 'ws';
const port = process.env.PORT || 8787;
const req = process.argv[2] || '00000000-0000-0000-0000-000000000001';
const ws = new WebSocket(`ws://127.0.0.1:${port}/call?request=${req}`);
let audioBytes = 0; const seen = [];
ws.on('open', () => {
  const silence = Buffer.alloc(3200); // 100 ms @ 16 kHz Int16
  const t = setInterval(() => ws.readyState === 1 && ws.send(silence), 100);
  setTimeout(() => { clearInterval(t); ws.close(); }, 12000);
});
ws.on('message', (d, bin) => {
  if (bin) { audioBytes += d.length; return; }
  const m = JSON.parse(d.toString());
  seen.push(m.type === 'dg' ? m.event : m.type === 'relay' ? `relay:${m.event}` : m.type);
  if (m.type === 'line') console.log(`[${m.speaker}] ${m.text}`);
  if (m.type === 'relay' && (m.event === 'error' || m.event === 'warning')) console.log('!!', m.code, m.description);
});
ws.on('close', () => {
  console.log('events:', [...new Set(seen)].join(', '));
  console.log(`agent audio received: ${(audioBytes / 48000).toFixed(1)} s`);
  process.exit(0);
});
