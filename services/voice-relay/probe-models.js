// Checks which think models Deepgram's Voice Agent accepts: node probe-models.js anthropic:<model> open_ai:<model> ...
import dotenv from 'dotenv';
import { WebSocket } from 'ws';
import { fileURLToPath } from 'node:url';

dotenv.config({ path: fileURLToPath(new URL('./.env', import.meta.url)) });

const test = (provider, model) => new Promise(resolve => {
  const ws = new WebSocket('wss://agent.deepgram.com/v1/agent/converse', { headers: { Authorization: `Token ${process.env.DEEPGRAM_API_KEY}` } });
  const done = r => { try { ws.close(); } catch {} resolve(r); };
  ws.on('open', () => ws.send(JSON.stringify({
    type: 'Settings',
    audio: { input: { encoding: 'linear16', sample_rate: 16000 }, output: { encoding: 'linear16', sample_rate: 24000, container: 'none' } },
    agent: {
      language: 'de',
      listen: { provider: { type: 'deepgram', model: 'nova-3' } },
      think: { provider: { type: provider, model }, prompt: 'Test' },
      speak: { provider: { type: 'deepgram', model: 'aura-2-viktoria-de' } }
    }
  })));
  ws.on('message', (d, bin) => {
    if (bin) return;
    const m = JSON.parse(d);
    if (m.type === 'SettingsApplied') done('OK');
    if (m.type === 'Error') done(`ERR ${m.description}`);
  });
  ws.on('error', e => done(`WS ERR ${e.message}`));
  setTimeout(() => done('timeout'), 8000);
});

for (const c of process.argv.slice(2)) {
  const [p, m] = c.split(':');
  console.log(c.padEnd(42), await test(p, m));
}
process.exit(0);
