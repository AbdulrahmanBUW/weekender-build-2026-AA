#!/usr/bin/env node
// render_n8n.mjs: images of the n8n workflows 01, 04, 05, 06 for the Sunday deck.
//
// Output (docs/launch/assets/n8n/):
//   <nn>-<slug>.png        n8n canvas at 3840x2160 (1280x720 CSS px @3x, same pixels as 1920x1080 @2x)
//   <nn>-<slug>.paper.svg  the same workflow in the Ankommen paper style, for the deck's own motion
//                          (<g data-node data-order>, <path data-from data-to data-main data-order>)
//   manifest.json          what each image shows
//
// Canvas modes (--mode=auto|component|own, default auto):
//   component  official n8n demo web component (@n8n_io/n8n-demo-component, needs internet at render time)
//   own        built-in faithful renderer (offline): dotted grid, rounded nodes, bezier links
//   auto       component first, own renderer for any workflow the component cannot draw
//
// Needs puppeteer-core and Chrome. Set PUPPETEER_PKG to a package.json whose folder has puppeteer-core
// installed if it is not resolvable from this repo. No secrets are read or written: credentials,
// webhook ids, code and header values are stripped before rendering (the workflow files are public anyway).

import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const OUT = path.join(ROOT, 'docs', 'launch', 'assets', 'n8n');
const CHROME = process.env.CHROME_PATH || 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const PUPPETEER_PKG = process.env.PUPPETEER_PKG ||
  'C:/Users/a_rahman/AppData/Local/Temp/claude/C--Users-a-rahman-Desktop-Automation-Weekender-Build/bc0649a2-1b68-40fd-bce5-cd66ad9c3d51/scratchpad/tools/package.json';
const MODE = (process.argv.find(a => a.startsWith('--mode=')) || '--mode=auto').slice(7);
const VIEW = { width: 1280, height: 720, dpr: 3 };

// Plain-English copy for the deck (B1). main_path is computed from the connections.
const WORKFLOWS = [
  {
    nn: '01', slug: 'new-request-brief', file: 'n8n/workflows/01-new-request-brief.json',
    title: '01 · Writes the German call brief',
    what_it_does: 'When a parent sends a new request, Claude writes a short German brief for the call and saves it in the database.',
    trigger: 'A new row in call_requests (Supabase calls the webhook)',
  },
  {
    nn: '04', slug: 'task-intake', file: 'n8n/workflows/04-task-intake.json',
    title: '04 · Turns free text into a call task',
    what_it_does: 'The parent says what they need in their own language, and Claude turns it into a clear call task and lists what is still missing.',
    trigger: 'The app sends the parent\'s text (browser POST, nothing is saved)',
  },
  {
    nn: '05', slug: 'translate-transcript-line', file: 'n8n/workflows/05-translate-transcript-line.json',
    title: '05 · Translates each call line',
    what_it_does: 'During the call, each new German line from the other side is translated into the parent\'s language and saved as a subtitle.',
    trigger: 'A new row in transcript_lines (Supabase calls the webhook)',
  },
  {
    nn: '06', slug: 'call-result', file: 'n8n/workflows/06-call-result.json',
    title: '06 · Brings the answer back in the parent\'s language',
    what_it_does: 'When the call ends, Claude writes the result in the parent\'s language, saves it and marks the request as booked or done.',
    trigger: 'The call outcome changes in the calls table (Supabase calls the webhook)',
  },
];

// Render-only positions (the workflow files stay untouched). The n8n canvas draws AI nodes wide
// (about 236 px), so nodes to their right are moved to avoid overlaps; 04 gets its AI sub-nodes
// sorted under the chain; 06 is folded into two rows so the labels stay readable at 16:9.
// Sticky notes are left out of the images (they are internal notes and shrink the fit).
const RENDER_LAYOUT = {
  '01': {
    'New Call Request (from Supabase)': [240, 304], 'Prepare Task Brief': [450, 304], 'Valid Task?': [660, 304],
    'Write German Call Brief (Claude)': [880, 208], 'Parse Brief + Re-check': [1240, 208],
    'Save Brief (PATCH call_requests)': [1450, 208], 'Log Events (brief_created, sensitive_stripped)': [1660, 208],
    'Mark Request Failed': [1240, 470],
  },
  '04': {
    'Task Intake (browser POST)': [240, 304], 'Check Origin + Size': [480, 304], 'Allowed?': [720, 304],
    'Draft Task (Claude)': [960, 208], 'Validate + Clean Draft': [1360, 208], 'Respond Draft (200)': [1600, 208],
    'Respond Intake Failed (502)': [1480, 480], 'Claude Haiku 4.5': [920, 440], 'Task Draft Schema': [1060, 440],
    'Claude Haiku (fixer)': [1061, 620], 'Respond Rejected (4xx)': [900, 700],
  },
  '05': {
    'Translate Line Request': [240, 304], 'Translate (Claude Haiku)': [480, 304], 'Parse Translation': [860, 208],
    'Save Subtitles (PATCH transcript_lines)': [1100, 208], 'Leave Line Untouched': [1100, 460],
  },
  '06': {
    'Call Result Request': [240, 208], 'Get Task Type (GET call_requests)': [480, 208],
    'Get Untranslated Lines (GET transcript_lines)': [720, 208], 'Prepare Result': [960, 208],
    'Write Result in User Language (Claude)': [1200, 208],
    'Parse Result': [240, 620], 'Save Summary (PATCH calls)': [480, 620], 'Booked or Completed?': [720, 620],
    'Set Request Status (only if not final)': [960, 450], 'Log Event: result_translated': [1200, 620],
    'Split Line Translations': [480, 840], 'Save Line Subtitles (PATCH transcript_lines)': [720, 840],
  },
};
const KEEP_STICKIES = false;

function applyLayout(w, nn) {
  const lay = RENDER_LAYOUT[nn] || {};
  w.nodes = w.nodes.filter(n => KEEP_STICKIES || !isSticky(n));
  for (const n of w.nodes) if (lay[n.name]) n.position = [...lay[n.name]];
  return w;
}

// ---------------------------------------------------------------- helpers
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
const sleep = ms => new Promise(r => setTimeout(r, ms));
const isSticky = n => n.type === 'n8n-nodes-base.stickyNote';
const SUB_TYPES = new Set(['@n8n/n8n-nodes-langchain.lmChatAnthropic', '@n8n/n8n-nodes-langchain.outputParserStructured']);
const isSub = n => SUB_TYPES.has(n.type) || /\.lmChat|\.outputParser|\.memory|\.tool/.test(n.type);
const isTrigger = n => /webhook$|Trigger$/i.test(n.type) && n.type !== 'n8n-nodes-base.respondToWebhook';

function loadPuppeteer() {
  try { return createRequire(import.meta.url)('puppeteer-core'); } catch { /* fall through */ }
  return createRequire(PUPPETEER_PKG)('puppeteer-core');
}

function sanitizeUrl(u) {
  const m = String(u).match(/https?:\/\/[^/]+(\/rest\/v1\/[A-Za-z_]+)/);
  return m ? `https://<project>.supabase.co${m[1]}` : 'https://<hidden>';
}

// Copy that is safe to hand to a renderer: no credentials, webhook ids, code, header values or query strings.
function cleanWorkflow(w) {
  const nodes = w.nodes.map(n => {
    const c = JSON.parse(JSON.stringify(n));
    delete c.credentials; delete c.webhookId; delete c.pinData;
    const p = c.parameters || {};
    if (p.jsCode) p.jsCode = '// omitted for the image';
    if (p.url) p.url = sanitizeUrl(p.url);
    for (const key of ['headerParameters', 'queryParameters']) {
      for (const h of (p[key]?.parameters || [])) if ('value' in h) h.value = '';
    }
    if (p.jsonBody) p.jsonBody = '{}';
    if (p.body) p.body = '';
    // the public preview service knows HTTP Request up to 4.2 (4.5 renders as "?")
    if (c.type === 'n8n-nodes-base.httpRequest' && c.typeVersion > 4.2) c.typeVersion = 4.2;
    // ... and its icon path for Anthropic Chat Model breaks above 1.3
    if (c.type === '@n8n/n8n-nodes-langchain.lmChatAnthropic' && c.typeVersion > 1.3) c.typeVersion = 1.3;
    return c;
  });
  return { nodes, connections: w.connections };
}

// Main path: start at the trigger, always follow the first "main" link of output 0.
function mainPath(w) {
  const start = w.nodes.find(isTrigger);
  const out = [];
  let cur = start && start.name;
  while (cur && !out.includes(cur)) {
    out.push(cur);
    const next = w.connections[cur]?.main?.[0]?.[0];
    cur = next && next.node;
  }
  return out;
}

// ---------------------------------------------------------------- geometry (shared by paper SVG and own renderer)
const N = 100;       // main node size
const SUBR = 40;     // sub-node radius (80x80 circle)
const WIDE = 236;    // AI chain node width on the n8n canvas
const WIDE_SUB = 250;
const isWide = n => /langchain\.(anthropic|chainLlm|agent)$/.test(n.type);

function geometry(w) {
  const nodes = w.nodes.filter(n => !isSticky(n));
  const byName = Object.fromEntries(nodes.map(n => [n.name, n]));
  const outCount = {};
  for (const n of nodes) {
    let k = 1;
    if (n.type === 'n8n-nodes-base.if') k = 2;
    if (n.onError === 'continueErrorOutput') k = 2;
    const used = (w.connections[n.name]?.main || []).length;
    outCount[n.name] = Math.max(k, used);
  }
  const hasAiIn = new Set();
  for (const c of Object.values(w.connections)) for (const [kind, outs] of Object.entries(c)) {
    if (kind !== 'main') for (const o of outs) for (const t of (o || [])) hasAiIn.add(t.node);
  }
  // like the n8n canvas: AI chain nodes are wide cards, a sub-node with its own model input is a wide sub-node
  const box = n => {
    const [x, y] = n.position;
    if (isSub(n)) return hasAiIn.has(n.name) ? { x, y, w: WIDE_SUB, h: SUBR * 2, sub: true, wide: true } : { x, y, w: SUBR * 2, h: SUBR * 2, sub: true };
    if (isWide(n)) return { x, y, w: WIDE, h: N, sub: false, wide: true };
    return { x, y, w: N, h: N, sub: false };
  };
  const outPt = (n, i) => {
    const b = box(n);
    if (b.sub) return { x: b.x + b.w / 2, y: b.y };                   // sub-nodes connect upwards
    const k = outCount[n.name] || 1;
    return { x: b.x + b.w, y: b.y + (b.h * (i + 1)) / (k + 1) };
  };
  const aiInputs = {};                                                  // parent -> [kind order]
  for (const [src, c] of Object.entries(w.connections)) for (const [kind, outs] of Object.entries(c)) {
    if (kind === 'main') continue;
    for (const o of outs) for (const t of (o || [])) {
      (aiInputs[t.node] ||= []);
      if (!aiInputs[t.node].includes(kind)) aiInputs[t.node].push(kind);
    }
  }
  for (const k of Object.keys(aiInputs)) aiInputs[k].sort((a, b) => (a === 'ai_languageModel' ? -1 : b === 'ai_languageModel' ? 1 : 0));
  const inPt = (n, kind) => {
    const b = box(n);
    if (kind === 'main') return { x: b.x, y: b.y + b.h / 2 };
    const list = aiInputs[n.name] || [kind];
    const i = Math.max(0, list.indexOf(kind));
    return { x: b.x + (b.w * (i + 1)) / (list.length + 1), y: b.y + b.h };
  };
  const links = [];
  for (const [src, c] of Object.entries(w.connections)) {
    if (!byName[src]) continue;
    for (const [kind, outs] of Object.entries(c)) outs.forEach((o, i) => (o || []).forEach(t => {
      if (!byName[t.node]) return;
      const a = kind === 'main' ? outPt(byName[src], i) : outPt(byName[src], 0);
      const b = inPt(byName[t.node], t.type || kind);
      let label = '';
      const sn = byName[src];
      if (kind === 'main' && sn.type === 'n8n-nodes-base.if') label = i === 0 ? 'true' : 'false';
      else if (kind === 'main' && sn.onError === 'continueErrorOutput') label = i === 0 ? 'success' : 'error';
      links.push({ from: src, to: t.node, kind, output: i, a, b, label });
    }));
  }
  // bounding box incl. labels (labels up to ~200px wide, two lines under the node)
  let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
  for (const n of nodes) {
    const b = box(n);
    x0 = Math.min(x0, b.x + b.w / 2 - Math.max(105, b.w / 2)); x1 = Math.max(x1, b.x + b.w / 2 + Math.max(105, b.w / 2));
    y0 = Math.min(y0, b.y - 10); y1 = Math.max(y1, b.y + b.h + (b.wide ? 10 : 56));
  }
  for (const l of links) { x1 = Math.max(x1, l.a.x + 70); }
  return { nodes, byName, box, links, bbox: { x0, y0, x1, y1 }, outCount };
}

function linkPath(l) {
  const { a, b } = l;
  if (l.kind !== 'main') {                         // sub-node (bottom) -> parent (bottom input), upwards
    const dy = Math.max(40, (a.y - b.y) / 2);
    return `M${a.x} ${a.y} C${a.x} ${a.y - dy} ${b.x} ${b.y + dy} ${b.x} ${b.y}`;
  }
  if (b.x >= a.x + 40) {
    const dx = Math.max(40, (b.x - a.x) / 2);
    return `M${a.x} ${a.y} C${a.x + dx} ${a.y} ${b.x - dx} ${b.y} ${b.x} ${b.y}`;
  }
  // backwards / straight down: out to the right, down, back left, into the input from the left
  const r = 16, xr = a.x + 36, xl = b.x - 36;
  // run the return line just under the source row (below its labels), not through nodes further down
  const ym = b.y > a.y ? Math.min(a.y + 142, b.y - 40) : Math.max(a.y - 90, b.y + 40);
  const s = b.y > a.y ? 1 : -1;
  return [
    `M${a.x} ${a.y}`, `H${xr - r}`, `Q${xr} ${a.y} ${xr} ${a.y + s * r}`,
    `V${ym - s * r}`, `Q${xr} ${ym} ${xr - r} ${ym}`, `H${xl + r}`,
    `Q${xl} ${ym} ${xl} ${ym + s * r}`, `V${b.y - s * r}`, `Q${xl} ${b.y} ${xl + r} ${b.y}`, `H${b.x}`,
  ].join(' ');
}

function wrapLabel(name, max = 22) {
  const words = name.split(/\s+/);
  const lines = [];
  let cur = '';
  for (const w of words) {
    if (!cur) cur = w;
    else if ((cur + ' ' + w).length <= max) cur += ' ' + w;
    else { lines.push(cur); cur = w; }
  }
  if (cur) lines.push(cur);
  if (lines.length > 3) return [...lines.slice(0, 2), lines.slice(2).join(' ')];
  return lines;
}

// 24x24 line glyphs, drawn for this project (no icon set, no brand marks)
function glyphKind(n) {
  const t = n.type;
  if (/webhook$/.test(t) && !/respond/i.test(t)) return 'webhook';
  if (/respondToWebhook$/.test(t)) return 'respond';
  if (/\.code$/.test(t)) return 'code';
  if (/httpRequest$/.test(t)) return 'http';
  if (/\.if$/.test(t)) return 'if';
  if (/supabase$|postgres$/.test(t)) return 'db';
  if (/lmChat/.test(t)) return 'model';
  if (/outputParser/.test(t)) return 'schema';
  if (/langchain\.(anthropic|chainLlm|agent)/.test(t)) return 'ai';
  if (/splitOut$/.test(t)) return 'split';
  if (/noOp$/.test(t)) return 'noop';
  if (/\.set$/.test(t)) return 'set';
  return 'noop';
}
const GLYPHS = {
  webhook: '<circle cx="12" cy="6" r="2.6"/><circle cx="6" cy="17" r="2.6"/><circle cx="18" cy="17" r="2.6"/><path d="M10.7 8.4 L7.4 14.7 M8.7 17 H15.3 M13.3 8.4 L16.6 14.7"/>',
  code: '<path d="M9 5.5 C6.6 5.5 7 8.6 7 10.3 C7 11.4 6.2 12 5 12 C6.2 12 7 12.6 7 13.7 C7 15.4 6.6 18.5 9 18.5 M15 5.5 C17.4 5.5 17 8.6 17 10.3 C17 11.4 17.8 12 19 12 C17.8 12 17 12.6 17 13.7 C17 15.4 17.4 18.5 15 18.5"/>',
  http: '<circle cx="12" cy="12" r="8"/><ellipse cx="12" cy="12" rx="3.6" ry="8"/><path d="M4 12 H20"/>',
  if: '<path d="M4 12 H9.5 L15 6.5 H20 M9.5 12 L15 17.5 H20 M17.5 4 L20 6.5 L17.5 9 M17.5 15 L20 17.5 L17.5 20"/>',
  db: '<ellipse cx="12" cy="6" rx="7" ry="2.6"/><path d="M5 6 V18 C5 19.4 8.1 20.6 12 20.6 C15.9 20.6 19 19.4 19 18 V6 M5 12 C5 13.4 8.1 14.6 12 14.6 C15.9 14.6 19 13.4 19 12"/>',
  ai: '<path d="M5 6.5 C5 5.1 6.1 4 7.5 4 H16.5 C17.9 4 19 5.1 19 6.5 V13.5 C19 14.9 17.9 16 16.5 16 H11 L7.5 19.5 V16 C6.1 16 5 14.9 5 13.5 Z M8.5 8.3 H15.5 M8.5 11.6 H13.2"/>',
  model: '<rect x="7" y="7" width="10" height="10" rx="1.6"/><path d="M10 4 V7 M14 4 V7 M10 17 V20 M14 17 V20 M4 10 H7 M4 14 H7 M17 10 H20 M17 14 H20"/>',
  schema: '<path d="M5 7 H13 M5 12 H11 M5 17 H9 M13.5 15 L16 17.5 L20 12.5"/>',
  respond: '<path d="M10 7 L5 12 L10 17 M5 12 H14 C17 12 19 14 19 17.5"/>',
  split: '<path d="M4 12 H9.5 M9.5 12 C12.5 12 12.5 6 15.5 6 H20 M9.5 12 H20 M9.5 12 C12.5 12 12.5 18 15.5 18 H20"/>',
  noop: '<path d="M5 12 H18 M14 8 L18 12 L14 16"/>',
  set: '<path d="M5 19 L6 15 L15.5 5.5 L18.5 8.5 L9 18 Z M13.5 7.5 L16.5 10.5"/>',
};
function glyph(kind, cx, cy, size, stroke, sw = 1.8) {
  const s = size / 24;
  return `<g transform="translate(${cx - 12 * s} ${cy - 12 * s}) scale(${s})" fill="none" stroke="${stroke}" stroke-width="${sw}" stroke-linecap="round" stroke-linejoin="round">${GLYPHS[kind] || GLYPHS.noop}</g>`;
}


// node outline like the n8n canvas: trigger = rounded left side, sub-node = circle, wide sub-node = rounded bar
function shapeSvg(n, b, attrs, inset = 0) {
  const x = b.x + inset, y = b.y + inset, w = b.w - 2 * inset, h = b.h - 2 * inset, cy = b.y + b.h / 2;
  if (b.sub && !b.wide) return `<circle cx="${b.x + b.w / 2}" cy="${cy}" r="${b.w / 2 - inset}" ${attrs}/>`;
  if (b.sub && b.wide) return `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="16" ${attrs}/>`;
  if (isTrigger(n)) {
    const r = 10;
    return `<path d="M${x + 40} ${y} H${x + w - r} Q${x + w} ${y} ${x + w} ${y + r} V${y + h - r} Q${x + w} ${y + h} ${x + w - r} ${y + h} H${x + 40} A40 ${h / 2} 0 0 1 ${x} ${cy} A40 ${h / 2} 0 0 1 ${x + 40} ${y} Z" ${attrs}/>`;
  }
  return `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="10" ${attrs}/>`;
}
// label under a square node, or inside (right of the glyph) for wide nodes
function labelSvg(lines, b, cx, cy, attrs) {
  if (b.wide) {
    const tx = b.x + (b.sub ? 64 : 80);
    const top = cy - ((lines.length - 1) * 18) / 2 + 5;
    return `<text text-anchor="start" ${attrs}>${lines.map((t, i) => `<tspan x="${tx}" y="${top + i * 18}">${esc(t)}</tspan>`).join('')}</text>`;
  }
  const ly = b.y + b.h + 22;
  return `<text text-anchor="middle" ${attrs}>${lines.map((t, i) => `<tspan x="${cx}" y="${ly + i * 18}">${esc(t)}</tspan>`).join('')}</text>`;
}

// ---------------------------------------------------------------- paper SVG (Ankommen design system)
const PAPER = { card: '#FFFDF8', border: '#D9D2C3', ink: '#1C2420', muted: '#5B635E', pine: '#1F5C4A', pineTint: '#E6EEE9' };
const FONT = "'Source Sans 3', 'Source Sans Pro', system-ui, sans-serif";

function paperSvg(wf, w, mp) {
  const g = geometry(w);
  const pad = 24;
  const { x0, y0, x1, y1 } = g.bbox;
  const vb = [Math.floor(x0 - pad), Math.floor(y0 - pad), Math.ceil(x1 - x0 + 2 * pad), Math.ceil(y1 - y0 + 2 * pad)];
  const id = `n8n${wf.nn}`;
  const order = name => mp.indexOf(name);
  const onMain = l => l.kind === 'main' && order(l.from) >= 0 && order(l.to) === order(l.from) + 1;
  const parts = [];
  parts.push(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="${vb.join(' ')}" width="${vb[2]}" height="${vb[3]}" role="img" aria-label="${esc(wf.title)}" data-workflow="${esc(wf.nn)}" font-family="${esc(FONT)}">`);
  parts.push(`<title>${esc(wf.title)}</title>`);
  parts.push(`<defs><marker id="${id}-arrow-main" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M1 1.5 L9 5 L1 8.5 Z" fill="${PAPER.pine}"/></marker>` +
    `<marker id="${id}-arrow-side" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M1 1.5 L9 5 L1 8.5 Z" fill="${PAPER.muted}"/></marker></defs>`);
  // connections first (under the nodes)
  parts.push(`<g data-layer="connections">`);
  g.links.forEach((l, i) => {
    const main = onMain(l);
    const d = linkPath(l);
    const attrs = [
      `id="${id}-c${i}"`, `data-from="${esc(l.from)}"`, `data-to="${esc(l.to)}"`, `data-kind="${l.kind === 'main' ? (l.label || 'main') : l.kind}"`,
      `data-output="${l.output}"`, `data-main="${main ? 1 : 0}"`, `data-order="${main ? order(l.from) : -1}"`, `d="${d}"`, 'fill="none"',
    ];
    if (main) attrs.push(`stroke="${PAPER.pine}"`, 'stroke-width="2.25"', `marker-end="url(#${id}-arrow-main)"`);
    else if (l.kind !== 'main') attrs.push(`stroke="${PAPER.muted}"`, 'stroke-width="1.5"', 'stroke-dasharray="5 5"');
    else attrs.push(`stroke="${PAPER.muted}"`, 'stroke-width="1.5"', `marker-end="url(#${id}-arrow-side)"`, 'stroke-opacity="0.7"');
    parts.push(`<path ${attrs.join(' ')}/>`);
  });
  // branch labels (true/false, success/error) next to the output
  for (const l of g.links) {
    if (!l.label || l.kind !== 'main') continue;
    if (l.label === 'true' || l.label === 'success') {
      if (onMain(l)) continue; // the main path does not need a label
    }
    // label just above its own line (the curve leaves the handle sideways, so above stays clear)
    parts.push(`<text data-branch-label="${esc(l.label)}" data-from="${esc(l.from)}" x="${l.a.x + 8}" y="${l.a.y - 6}" font-size="12" fill="${PAPER.muted}">${esc(l.label)}</text>`);
  }
  parts.push(`</g>`);
  // nodes
  parts.push(`<g data-layer="nodes">`);
  for (const n of g.nodes) {
    const b = g.box(n);
    const o = order(n.name);
    const main = o >= 0;
    const cx = b.x + b.w / 2, cy = b.y + b.h / 2;
    const gk = glyphKind(n);
    const stroke = main ? PAPER.pine : PAPER.muted;
    const shape = shapeSvg(n, b, `data-shape="card" fill="${PAPER.card}" stroke="${PAPER.border}" stroke-width="1"`, 0.5);
    const lines = wrapLabel(n.name, b.wide ? 17 : b.sub ? 18 : 22);
    const txt = `font-size="${b.sub ? 13 : 14}" font-weight="${main ? 600 : 400}" fill="${main ? PAPER.ink : PAPER.muted}"`;
    const gx = b.wide ? b.x + (b.sub ? 34 : 42) : cx;
    const label = labelSvg(lines, b, cx, cy, txt);
    parts.push(`<g data-node="${esc(n.name)}" data-order="${o}" data-type="${esc(n.type)}" data-glyph="${gk}"${isTrigger(n) ? ' data-trigger="1"' : ''}${b.sub ? ' data-sub="1"' : ''} data-cx="${cx}" data-cy="${cy}">` +
      shape + glyph(gk, gx, cy, b.sub ? 30 : 40, stroke, 1.8) + label + `</g>`);
  }
  parts.push(`</g></svg>`);
  return { svg: parts.join('\n'), viewBox: vb };
}

// ---------------------------------------------------------------- own renderer (n8n editor look, offline fallback)
const N8N = { bg: '#f5f5f5', dot: '#c9c9c9', node: '#ffffff', border: '#d6d6d6', text: '#27272a', muted: '#7a7a7a', link: '#9a9a9a', sticky: '#fdf6d8', stickyBorder: '#e9dc9f' };
const GLYPH_COLORS = { webhook: '#dc3a5f', respond: '#3f7ee8', code: '#f28c18', http: '#3a63d8', if: '#2f9e5b', db: '#3ecf8e', model: '#b4583a', schema: '#6b6b6b', ai: '#b4583a', split: '#2f7db5', noop: '#8a8a8a', set: '#3a78c8' };

function ownHtml(wf, w) {
  const g = geometry(w);
  const stickies = w.nodes.filter(isSticky);
  let { x0, y0, x1, y1 } = g.bbox;
  for (const s of stickies) { x0 = Math.min(x0, s.position[0]); y0 = Math.min(y0, s.position[1]); x1 = Math.max(x1, s.position[0] + (s.parameters.width || 240)); y1 = Math.max(y1, s.position[1] + (s.parameters.height || 160)); }
  const pad = 80;
  let W = x1 - x0 + 2 * pad, H = y1 - y0 + 2 * pad;
  const ratio = 16 / 9;
  if (W / H > ratio) H = W / ratio; else W = H * ratio;
  const cxm = (x0 + x1) / 2, cym = (y0 + y1) / 2;
  const vb = [cxm - W / 2, cym - H / 2, W, H];
  const parts = [];
  parts.push(`<defs><pattern id="dots" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="${N8N.dot}"/></pattern>` +
    `<marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M1 1.5 L9 5 L1 8.5 Z" fill="${N8N.link}"/></marker></defs>`);
  parts.push(`<rect x="${vb[0]}" y="${vb[1]}" width="${W}" height="${H}" fill="${N8N.bg}"/><rect x="${vb[0]}" y="${vb[1]}" width="${W}" height="${H}" fill="url(#dots)"/>`);
  for (const s of stickies) {
    const sw = s.parameters.width || 240, sh = s.parameters.height || 160;
    const text = String(s.parameters.content || '').replace(/[#*]/g, '').split('\n').filter(Boolean);
    parts.push(`<rect x="${s.position[0]}" y="${s.position[1]}" width="${sw}" height="${sh}" rx="6" fill="${N8N.sticky}" stroke="${N8N.stickyBorder}"/>`);
    parts.push(`<foreignObject x="${s.position[0] + 14}" y="${s.position[1] + 10}" width="${sw - 28}" height="${sh - 20}"><div xmlns="http://www.w3.org/1999/xhtml" style="font:13px/1.35 system-ui,sans-serif;color:#3a3a3a">${text.map((t, i) => i === 0 ? `<b style="font-size:15px">${esc(t)}</b>` : esc(t)).join('<br/>')}</div></foreignObject>`);
  }
  for (const l of g.links) {
    const dash = l.kind !== 'main' ? ' stroke-dasharray="6 5"' : ` marker-end="url(#arr)"`;
    parts.push(`<path d="${linkPath(l)}" fill="none" stroke="${N8N.link}" stroke-width="2"${dash}/>`);
    if (l.label && l.kind === 'main') parts.push(`<text x="${l.a.x + 9}" y="${l.a.y - 6}" font-size="11" fill="${N8N.muted}">${esc(l.label === 'success' ? 'Success' : l.label === 'error' ? 'Error' : l.label)}</text>`);
  }
  for (const n of g.nodes) {
    const b = g.box(n);
    const cx = b.x + b.w / 2, cy = b.y + b.h / 2;
    const gk = glyphKind(n);
    parts.push(shapeSvg(n, b, `fill="${N8N.node}" stroke="${N8N.border}" stroke-width="2"`));
    parts.push(glyph(gk, b.wide ? b.x + (b.sub ? 34 : 42) : cx, cy, b.sub ? 32 : 44, GLYPH_COLORS[gk] || N8N.muted, 2));
    // handles
    if (!b.sub) {
      if (!isTrigger(n)) parts.push(`<circle cx="${b.x}" cy="${cy}" r="5" fill="#fff" stroke="${N8N.link}" stroke-width="1.5"/>`);
      const k = g.outCount[n.name] || 1;
      if (!/respondToWebhook$/.test(n.type)) for (let i = 0; i < k; i++) parts.push(`<circle cx="${b.x + b.w}" cy="${b.y + (b.h * (i + 1)) / (k + 1)}" r="5" fill="#fff" stroke="${N8N.link}" stroke-width="1.5"/>`);
    }
    parts.push(labelSvg(wrapLabel(n.name, b.wide ? 17 : 22), b, cx, cy, `font-size="14" font-weight="500" fill="${N8N.text}"`));
  }
  return `<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;background:${N8N.bg};overflow:hidden}svg{display:block;width:100vw;height:100vh;font-family:system-ui,'Segoe UI',sans-serif}</style></head><body>` +
    `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${vb.join(' ')}" preserveAspectRatio="xMidYMid meet">${parts.join('')}</svg></body></html>`;
}

// ---------------------------------------------------------------- canvas renderers
function componentHtml(clean) {
  const json = JSON.stringify(clean).replace(/&/g, '&amp;').replace(/'/g, '&#39;');
  return `<!doctype html><html><head><meta charset="utf-8">
<script src="https://cdn.jsdelivr.net/npm/@webcomponents/webcomponentsjs@2.0.0/webcomponents-loader.js"></script>
<script type="module" src="https://cdn.jsdelivr.net/npm/@n8n_io/n8n-demo-component/n8n-demo.bundled.js"></script>
<style>html,body{margin:0;overflow:hidden;background:#f5f5f5}n8n-demo{position:absolute;left:4vw;top:4vh;width:92vw;height:92vh;--n8n-workflow-min-height:92vh}</style></head>
<body><n8n-demo workflow='${json}' frame="false" theme="light" hidecanvaserrors="true" disableinteractivity="true" collapseformobile="false"></n8n-demo></body></html>`;
}

async function renderComponent(browser, clean, pngPath, tmpDir, nn) {
  const page = await browser.newPage();
  try {
    await page.setViewport({ width: VIEW.width, height: VIEW.height, deviceScaleFactor: VIEW.dpr });
    const file = path.join(tmpDir, `component-${nn}.html`);
    fs.writeFileSync(file, componentHtml(clean), 'utf8');
    await page.goto(pathToFileURL(file).href, { waitUntil: 'networkidle2', timeout: 60000 });
    let frame = null;
    for (let t = 0; t < 60 && !frame; t++) { frame = page.frames().find(f => f.url().includes('n8n-preview-service')); if (!frame) await sleep(500); }
    if (!frame) throw new Error('preview iframe did not load');
    const expected = clean.nodes.length;
    await frame.waitForFunction(n => document.querySelectorAll('.vue-flow__node').length >= n, { timeout: 45000 }, expected);
    await sleep(1200);
    const unknown = await frame.evaluate(() => [...document.querySelectorAll('.vue-flow__node img')].filter(i => !(i.complete && i.naturalWidth > 0)).length);
    await frame.addStyleTag({ content: '.vue-flow__controls,[data-test-id="canvas-controls"],[data-test-id="canvas-background-striped-pattern"]{display:none!important}' });
    await frame.evaluate(() => {
      // hide the read-only stripes (keep the dotted grid)
      const pat = document.querySelector('[data-test-id="canvas-background-striped-pattern"]');
      if (pat && pat.id) for (const r of document.querySelectorAll(`[fill="url(#${pat.id})"]`)) r.style.display = 'none';
    });
    await sleep(1800); // let fit-view settle
    await page.screenshot({ path: pngPath });
    return { ok: true, unknown };
  } finally {
    await page.close();
  }
}

async function renderOwn(browser, wf, w, pngPath, tmpDir) {
  const page = await browser.newPage();
  try {
    await page.setViewport({ width: VIEW.width, height: VIEW.height, deviceScaleFactor: VIEW.dpr });
    const file = path.join(tmpDir, `own-${wf.nn}.html`);
    fs.writeFileSync(file, ownHtml(wf, w), 'utf8');
    await page.goto(pathToFileURL(file).href, { waitUntil: 'load' });
    await sleep(300);
    await page.screenshot({ path: pngPath });
    return { ok: true };
  } finally {
    await page.close();
  }
}

// ---------------------------------------------------------------- main
async function main() {
  fs.mkdirSync(OUT, { recursive: true });
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'render-n8n-'));
  const puppeteer = loadPuppeteer();
  const browser = await puppeteer.launch({ executablePath: CHROME, headless: true, args: ['--hide-scrollbars'] });
  const manifest = [];
  const nodeCount = {};
  try {
    for (const wf of WORKFLOWS) {
      const w = JSON.parse(fs.readFileSync(path.join(ROOT, wf.file), 'utf8'));
      nodeCount[wf.nn] = w.nodes.filter(n => !isSticky(n)).length;
      delete w.pinData; delete w.staticData;
      applyLayout(w, wf.nn);
      const clean = cleanWorkflow(w);
      const mp = mainPath(w);
      const png = `${wf.nn}-${wf.slug}.png`;
      const svgName = `${wf.nn}-${wf.slug}.paper.svg`;
      let renderer = MODE === 'own' ? 'own' : 'n8n-demo-component';
      if (MODE !== 'own') {
        try {
          const r = await renderComponent(browser, clean, path.join(OUT, png), tmpDir, wf.nn);
          console.log(`${wf.nn}: n8n demo component ok${r.unknown ? ` (${r.unknown} broken icons)` : ''}`);
        } catch (e) {
          console.log(`${wf.nn}: component failed (${e.message.slice(0, 120)})`);
          if (MODE === 'component') throw e;
          renderer = 'own';
        }
      }
      if (renderer === 'own') { await renderOwn(browser, wf, clean, path.join(OUT, png), tmpDir); console.log(`${wf.nn}: own renderer ok`); }
      const paper = paperSvg(wf, w, mp);
      fs.writeFileSync(path.join(OUT, svgName), paper.svg, 'utf8');
      manifest.push({
        file: png,
        paper_svg: svgName,
        workflow: path.basename(wf.file),
        n8n_name: w.name,
        title: wf.title,
        what_it_does: wf.what_it_does,
        trigger: wf.trigger,
        node_count: nodeCount[wf.nn],
        main_path: mp,
        renderer,
        png_size: [VIEW.width * VIEW.dpr, VIEW.height * VIEW.dpr],
        paper_viewbox: paper.viewBox,
      });
    }
  } finally {
    await browser.close();
    fs.rmSync(tmpDir, { recursive: true, force: true });
  }
  fs.writeFileSync(path.join(OUT, 'manifest.json'), JSON.stringify(manifest, null, 2) + '\n', 'utf8');
  console.log(`wrote ${manifest.length} workflows to ${path.relative(ROOT, OUT)}`);
}

main().catch(e => { console.error(e); process.exit(1); });
