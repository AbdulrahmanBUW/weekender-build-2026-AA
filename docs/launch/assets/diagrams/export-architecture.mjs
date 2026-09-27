// Exports the delivered archify architecture diagram as deck PNGs (2x, light + dark) in the
// "Bilingual paper v3" palette (CSS variable override at capture time only; the HTML is not modified),
// plus nodes.json with each primary node's box in light-PNG pixel coordinates.
import { createRequire } from 'node:module';
import fs from 'node:fs';
const require = createRequire('C:/Users/a_rahman/AppData/Local/Temp/claude/C--Users-a-rahman-Desktop-Automation-Weekender-Build/bc0649a2-1b68-40fd-bce5-cd66ad9c3d51/scratchpad/tools/package.json');
const puppeteer = require('puppeteer-core');
const OUT = 'C:/Users/a_rahman/Desktop/Automation/Weekender Build/docs/launch/assets/diagrams';
const URL = 'file:///C:/Users/a_rahman/Desktop/Automation/Weekender%20Build/docs/launch/assets/diagrams/architecture.html';
const DSF = 2;
const PAL = {
  light: {
    '--bg': '#F7F4EC', '--grid': 'transparent', '--panel': '#F7F4EC', '--panel-border': '#D9D2C3', '--mask': '#F7F4EC',
    '--text': '#1C2420', '--text-muted': '#5B635E', '--text-dim': '#5B635E', '--text-faint': '#5B635E',
    '--arrow': '#5B635E', '--arrow-emphasis': '#1F5C4A',
    '--frontend-fill': '#E6EEE9', '--frontend-stroke': '#1F5C4A',
    '--backend-fill': '#FFFDF8', '--backend-stroke': '#1F5C4A',
    '--database-fill': '#F2E6D3', '--database-stroke': '#5B635E',
    '--cloud-fill': '#EFE9DC', '--cloud-stroke': '#1C2420',
    '--external-fill': '#FFFDF8', '--external-stroke': '#5B635E',
    '--messagebus-fill': '#EFE9DC', '--messagebus-stroke': '#5B635E',
    '--security-fill': '#FFFDF8', '--security-stroke': '#1C2420',
  },
  dark: {
    '--bg': '#1C2420', '--grid': 'transparent', '--panel': '#1C2420', '--panel-border': '#3A443F', '--mask': '#1C2420',
    '--text': '#F7F4EC', '--text-muted': '#C9C3B6', '--text-dim': '#A7AFA9', '--text-faint': '#A7AFA9',
    '--arrow': '#A7AFA9', '--arrow-emphasis': '#7FC0A6',
    '--frontend-fill': '#24453A', '--frontend-stroke': '#9CCFBA',
    '--backend-fill': '#232C27', '--backend-stroke': '#7FC0A6',
    '--database-fill': '#3A342A', '--database-stroke': '#D9D2C3',
    '--cloud-fill': '#2B302B', '--cloud-stroke': '#EFE9DC',
    '--external-fill': '#232C27', '--external-stroke': '#A7AFA9',
    '--messagebus-fill': '#2B302B', '--messagebus-stroke': '#A7AFA9',
    '--security-fill': '#232C27', '--security-stroke': '#EFE9DC',
  },
};
const MAIN_PATH = ['app', 'requests', 'brief', 'relay-call', 'agent', 'receptionist', 'store', 'result', 'app'];
const b = await puppeteer.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: 'new' });
let nodesOut = null;
for (const theme of ['light', 'dark']) {
  const p = await b.newPage();
  await p.emulateMediaFeatures([{ name: 'prefers-reduced-motion', value: 'reduce' }, { name: 'prefers-color-scheme', value: theme }]);
  await p.setViewport({ width: 1600, height: 1000, deviceScaleFactor: DSF });
  await p.goto(URL, { waitUntil: 'load' });
  await new Promise(r => setTimeout(r, 600));
  const vars = Object.entries(PAL[theme]).map(([k, v]) => `${k}: ${v} !important;`).join(' ');
  await p.evaluate((theme, vars) => {
    document.documentElement.setAttribute('data-theme', theme);
    const st = document.createElement('style');
    st.textContent = `html, html *, svg, svg * { ${vars} } svg[viewBox="0 0 1360 580"] { background: var(--bg) !important; }`;
    document.head.appendChild(st);
  }, theme, vars);
  await new Promise(r => setTimeout(r, 700));
  const box = await p.evaluate(() => { const r = document.querySelector('svg[viewBox="0 0 1360 580"]').getBoundingClientRect(); return { x: r.left + window.scrollX, y: r.top + window.scrollY, width: r.width, height: r.height }; });
  await p.screenshot({ path: `${OUT}/architecture-${theme}.png`, clip: box, captureBeyondViewport: false });
  if (theme === 'light') {
    nodesOut = await p.evaluate((DSF) => {
      const s = document.querySelector('svg[viewBox="0 0 1360 580"]').getBoundingClientRect();
      return [...document.querySelectorAll('svg g[data-node-id]')].map(g => {
        const shape = g.querySelector('rect') || g;
        const r = shape.getBoundingClientRect();
        return { id: g.dataset.nodeId, label: g.dataset.nodeLabel, x: Math.round((r.left - s.left) * DSF), y: Math.round((r.top - s.top) * DSF), w: Math.round(r.width * DSF), h: Math.round(r.height * DSF) };
      }).concat([{ _png: { w: Math.round(s.width * DSF), h: Math.round(s.height * DSF) } }]);
    }, DSF);
  }
  await p.close();
}
await b.close();
const png = nodesOut.pop()._png;
fs.writeFileSync(`${OUT}/nodes.json`, JSON.stringify({ png: `architecture-light.png`, width: png.w, height: png.h, scale: DSF, nodes: nodesOut, main_path: MAIN_PATH }, null, 2) + '\n', 'utf8');
console.log('ok', png, nodesOut.length);
