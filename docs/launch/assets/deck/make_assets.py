"""Derived deck assets (run from anywhere: python docs/launch/assets/deck/make_assets.py).

1. approval-consent-ru.png: copy of screens/crop-approval-ru.png with the consent box ticked and the
   "Call now" button enabled (pine), for the last pan stop on slide 6. The tick is copied from the ticked
   "Alter des Kindes" checkbox in the same screenshot; the button is recoloured per pixel (keeps anti-aliasing).
2. architecture-paper.html: copy of diagrams/architecture.html forced to the light theme with the
   "Bilingual paper v3" palette (same overrides as diagrams/export-architecture.mjs), no glow filters.
   Open it with ?theme=light&embed=1 to hide the archify toolbar.
Re-run after the screenshot or the diagram changes. The source files are not modified.
"""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.dirname(HERE)

# ---------------------------------------------------------------- 1. consent overlay
src = os.path.join(ASSETS, 'screens', 'crop-approval-ru.png')
im = np.array(Image.open(src).convert('RGB')).astype(float)
H, W, _ = im.shape
assert (W, H) == (1408, 2644), (W, H)  # coordinates below are for this capture

# ticked checkbox (x 82..121, y 1502..1541) -> unticked one (x 82..121, y 2090..2129), 3 px margin
m = 3
im[2090 - m:2130 + m, 82 - m:122 + m] = im[1502 - m:1542 + m, 82 - m:122 + m]

# disabled button (x 82..417, y 2474..2561) -> pine with white text
BTN = np.array([135, 162, 147.])
WHITE = np.array([255, 255, 255.])
CARD = im[2440, 60].copy()
PINE = np.array([31, 92, 74.])
x0, y0, x1, y1 = 80, 2472, 420, 2564
reg = im[y0:y1, x0:x1]
A = np.stack([WHITE - BTN, CARD - BTN], axis=1)  # 3x2
coef, *_ = np.linalg.lstsq(A, (reg.reshape(-1, 3) - BTN).T, rcond=None)  # 2xN
a = np.clip(coef[0], 0, 1)[:, None]
b = np.clip(coef[1], 0, 1)[:, None]
new = PINE + a * (WHITE - PINE) + b * (CARD - PINE)
im[y0:y1, x0:x1] = new.reshape(reg.shape)

out = os.path.join(HERE, 'approval-consent-ru.png')
Image.fromarray(np.clip(im, 0, 255).astype(np.uint8)).save(out, optimize=True)
print('wrote', os.path.relpath(out, ASSETS))

# ---------------------------------------------------------------- 2. paper diagram copy
PAL = {
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
    '--toolbar-bg': '#FFFDF8', '--toolbar-border': '#D9D2C3', '--toolbar-text': '#1C2420',
    '--toolbar-hover': '#EFE9DC', '--toolbar-menu-bg': '#FFFDF8',
}
vars_css = ' '.join('%s: %s !important;' % kv for kv in PAL.items())
style = ('<style id="ankommen-paper">html, html *, svg, svg * { %s }\n'
         'html, body { background: #F7F4EC !important; background-image: none !important; }\n'
         'svg *, .toolbar, .header, .cards { filter: none !important; text-shadow: none !important; box-shadow: none !important; }\n'
         '</style>\n' % vars_css)
dsrc = os.path.join(ASSETS, 'diagrams', 'architecture.html')
with open(dsrc, encoding='utf-8') as f:
    html = f.read()
html = html.replace('data-theme="dark"', 'data-theme="light"', 1)
# force light theme even if the viewer's system or a stored choice says dark
html = html.replace("document.documentElement.setAttribute('data-theme', theme);",
                    "theme = 'light'; document.documentElement.setAttribute('data-theme', theme);", 1)
i = html.rfind('</head>')
assert i > 0
html = html[:i] + style + html[i:]
dout = os.path.join(HERE, 'architecture-paper.html')
with open(dout, 'w', encoding='utf-8') as f:
    f.write(html)
print('wrote', os.path.relpath(dout, ASSETS))
