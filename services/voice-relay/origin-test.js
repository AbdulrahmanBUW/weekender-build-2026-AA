// Origin allow-list check against a running relay (no Deepgram usage: every probe uses /listen?lang=xx).
// Passed the Origin check -> 400 "language not supported"; blocked -> 403. No Origin header (curl, scripts) -> allowed.
// Usage: node origin-test.js   (relay on :8787, or set PORT). Defaults assume ALLOWED_ORIGIN_SUFFIXES is not set.
import { WebSocket } from 'ws';
const PORT = process.env.PORT || 8787;
const cases = [
  ['https://preview--my-app.lovable.app', 400], ['https://abc123.lovableproject.com', 400], [`http://127.0.0.1:${PORT}`, 400], [null, 400],
  ['https://evil-lovable.app', 403], ['https://lovable.app', 403], ['https://lovable.app.evil.com', 403], ['http://my-app.lovable.app', 403],
  ['https://my-app.lovable.app:8443', 403], ['null', 403], ['https://example.com', 403]
];
const probe = origin => new Promise(resolve => {
  const ws = new WebSocket(`ws://127.0.0.1:${PORT}/listen?lang=xx`, origin ? { headers: { Origin: origin } } : {});
  ws.on('unexpected-response', (_q, res) => { resolve(res.statusCode); ws.terminate(); });
  ws.on('open', () => { resolve(101); ws.close(); });
  ws.on('error', () => resolve('error'));
});
let fail = 0;
for (const [origin, want] of cases) {
  const got = await probe(origin);
  if (got !== want) fail++;
  console.log(`${got === want ? 'ok  ' : 'FAIL'} ${(origin ?? '(no Origin header)').padEnd(40)} → ${got} (want ${want})`);
}
console.log(fail ? `${fail} failed` : 'all origin checks passed');
process.exit(fail ? 1 : 0);
