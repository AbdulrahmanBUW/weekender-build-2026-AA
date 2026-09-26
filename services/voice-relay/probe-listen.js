// Checks (1) which listen models the Voice Agent accepts (Flux vs Nova-3) and
// (2) which language codes Deepgram's streaming STT accepts for /listen.
// Usage: node probe-listen.js            (needs DEEPGRAM_API_KEY in .env; prints no secrets)
import dotenv from 'dotenv';
import { WebSocket } from 'ws';
import { fileURLToPath } from 'node:url';

dotenv.config({ path: fileURLToPath(new URL('./.env', import.meta.url)) });
const KEY = process.env.DEEPGRAM_API_KEY;

const agent = (label, listen) => new Promise(resolve => {
  const ws = new WebSocket('wss://agent.deepgram.com/v1/agent/converse', { headers: { Authorization: `Token ${KEY}` } });
  const done = r => { try { ws.close(); } catch {} resolve(`${label.padEnd(44)} ${r}`); };
  ws.on('open', () => ws.send(JSON.stringify({
    type: 'Settings',
    audio: { input: { encoding: 'linear16', sample_rate: 16000 }, output: { encoding: 'linear16', sample_rate: 24000, container: 'none' } },
    agent: {
      ...(listen.version === 'v2' ? {} : { language: 'de' }),  // Flux rejects agent.language
      listen: { provider: listen },
      think: { provider: { type: 'anthropic', model: 'claude-sonnet-5' }, prompt: 'Test' },
      speak: { provider: { type: 'deepgram', model: 'aura-2-elara-de' } }
    }
  })));
  // keep sending silence so a late error (after SettingsApplied) is also seen
  const t = setInterval(() => ws.readyState === 1 && ws.send(Buffer.alloc(3200)), 100);
  let applied = false;
  ws.on('message', (d, bin) => {
    if (bin) return;
    const m = JSON.parse(d);
    if (m.type === 'SettingsApplied') applied = true;
    if (m.type === 'Error') { clearInterval(t); done(`ERR ${m.code || ''} ${m.description}`); }
  });
  ws.on('error', e => { clearInterval(t); done(`WS ERR ${e.message}`); });
  setTimeout(() => { clearInterval(t); done(applied ? 'OK (settings applied, no error in 4 s)' : 'timeout'); }, 4000);
});

const stt = lang => new Promise(resolve => {
  const url = `wss://api.deepgram.com/v1/listen?model=nova-3&language=${lang}&encoding=linear16&sample_rate=16000`;
  const ws = new WebSocket(url, { headers: { Authorization: `Token ${KEY}` } });
  const done = r => { try { ws.close(); } catch {} resolve(`${lang.padEnd(8)} ${r}`); };
  ws.on('open', () => { ws.send(JSON.stringify({ type: 'CloseStream' })); done('OK'); });
  ws.on('unexpected-response', (_q, res) => done(`HTTP ${res.statusCode} ${res.headers['dg-error'] || ''}`));
  ws.on('error', e => done(`WS ERR ${e.message}`));
  setTimeout(() => done('timeout'), 6000);
});

console.log('--- Voice Agent listen models');
for (const [label, p] of [
  ['nova-3', { type: 'deepgram', model: 'nova-3' }],
  ['flux-general-multi v2 hints [de]', { type: 'deepgram', version: 'v2', model: 'flux-general-multi', language_hints: ['de'] }],
  ['flux-general-multi v2 (no hints)', { type: 'deepgram', version: 'v2', model: 'flux-general-multi' }],
  ['flux-general-en v2', { type: 'deepgram', version: 'v2', model: 'flux-general-en' }]
]) console.log(await agent(label, p));

console.log('--- Streaming STT nova-3 language codes');
for (const l of (process.argv[2] || 'en,ar,tr,uk,ru,fa,hi,es,fr,pl,vi,zh,zh-CN,de,multi').split(',')) console.log(await stt(l));
process.exit(0);
