# -*- coding: utf-8 -*-
"""make_people.py - builds public/pixel/people.png (384x288) for the Ankommen site.

12 newcomers, each a 96x96 block = 3 rows (down, up, right) x 3 walk frames of 32x32.
Base sprites: Pixel Agents (https://github.com/pixel-agents-hq/pixel-agents),
Copyright (c) 2026 Pablo De Lucca, MIT License. Based on MetroCity by JIK-A-4 (CC0).
Recoloured to the Ankommen palette, hair redrawn, overlays and props drawn here.
Run: python scripts/pixel/make_people.py
"""
import os
from PIL import Image

BASE_DIR = 'C:/Users/a_rahman/AppData/Local/npm-cache/_npx/5a59f5d4e775a394/node_modules/pixel-agents/dist/assets/characters/'
OUT = 'C:/Users/a_rahman/Desktop/Automation/hallotermin-paper/public/pixel/people.png'
TS_OUT = 'C:/Users/a_rahman/Desktop/Automation/hallotermin-paper/src/components/pixel/people.data.ts'
PREV = 'C:/Users/a_rahman/Desktop/Automation/Weekender Build/docs/pixel/previews/'


def hx(s):
    s = s.lstrip('#')
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), 255)


INK, INK2 = hx('1C2420'), hx('3A3F3A')
WHITE, PAPER, CREAM = hx('FFFFFF'), hx('F7F4EC'), hx('EFE4CF')
SAND = [hx(c) for c in ('F1E4C6', 'D9C49A', 'B59D73', '8C7453', '5E4C38')]
GREY = [hx(c) for c in ('D3CDBF', 'A8A296', '77736A')]
GOLD = hx('E0B04A')
STEEL = [hx('6E97C9'), hx('3F66A0')]
ROOF = [hx('C9704F'), hx('93493A')]
WATER = [hx('B7D1D6'), hx('8DB2BD'), hx('638D9B')]
APO = hx('B4202A')
EXTRA_ROSE_SH = hx('A86E6E')  # extra colour 1: dusty rose shadow

SKIN = {
    's1': [hx('F7DCC8'), hx('E4B9A0'), hx('A56E48')],
    's2': [hx('EDC29E'), hx('CF9C77'), hx('835530')],
    's3': [hx('C98E62'), hx('A56E48'), hx('5E3822')],
    's4': [hx('A8703F'), hx('835530'), hx('5E3822')],
    's5': [hx('7F4E31'), hx('5E3822'), hx('3D2417')],
    's6': [hx('573522'), hx('3D2417'), hx('231F1C')],
}
HAIR = {
    'black': [hx('4A4E52'), hx('3A3F3A'), hx('231F1C'), INK],
    'dbrown': [hx('7A5234'), hx('4A3326'), hx('231F1C'), INK],
    'brown': [hx('8C7453'), hx('7A5234'), hx('4A3326'), INK],
    'red': [hx('C9704F'), hx('B5532E'), hx('93493A'), hx('4A3326')],
    'blonde': [hx('F1E4C6'), hx('D9B26A'), hx('B59D73'), hx('5E4C38')],
    'grey': [hx('D3CDBF'), hx('B3ADA3'), hx('77736A'), INK2],
}
CL = {
    'sage': [hx('A9CDBB'), hx('8FA888'), hx('4E7E6B'), INK2],
    'mustard': [hx('E0B04A'), hx('D9A441'), hx('8C7453'), hx('5E4C38')],
    'terracotta': [hx('C9704F'), hx('C4674A'), hx('93493A'), hx('5E3822')],
    'navy': [hx('3F66A0'), hx('34496B'), INK2, INK],
    'teal': [hx('74A590'), hx('3E7F7F'), hx('1F5C4A'), hx('174A3B')],
    'denim': [hx('6E97C9'), hx('5C7BA6'), hx('3F66A0'), hx('34496B')],
    'charcoal': [hx('77736A'), hx('4A4E52'), INK2, INK],
    'rose': [hx('C98B8B'), hx('C98B8B'), EXTRA_ROSE_SH, hx('5E4C38')],
    'white': [WHITE, PAPER, hx('D3CDBF'), hx('A8A296')],
    'cream': [PAPER, CREAM, hx('D9C49A'), hx('8C7453')],
}

# colour roles of the base sprites (H hair, S skin, O skin outline, E eye dark, W white(eye/shirt), T top, B bottom, K shoes/black)
ROLES = {
    0: dict(H='32191d 6d4726 b18649 8f6439 341f20 6f4a2a', S='ffd8b2 fbbf97 e9a384 c5896e e29878 84523a 352c27', O='493e38',
            E='4f4f4f 191919', T='1164a9 114978 071c2e 0f406a 9f9f9f 403632', X='040605', K='000000 595959 1a1a1a 353535'),
    1: dict(H='f1c084 e39f5a 7e4b29 be7743', S='ffd8b2 e29878 bd8068 fbbf97 e9a384 c5896e', O='493e38',
            E='4f4f4f 191919 595959', T='1a1a1a 252525 2b2b2b 101010 5e514c', K='000000'),
    2: dict(H='2b2827 252120 181616 282423 221e1e 1b1a19', S='865e4c 75503d 5f4132 593b2c 84523a 493227 352c27', O='231e1d',
            E='4f4f4f 191919', T='741713 a91d18 e1721d 8b1a16 56110e e8741b f67d20 e87218 ff8b31 592700 403632',
            B='23294d 343d5a 49557e 111528', K='000000 595959 d0d0d0 120308 fff2ec'),
    3: dict(H='fff1ef e9d7d4 b0a6a3 f0e1de daccc9 bfb6b3', S='ffa77c e08d64 352c27 ac6847 84523a b67352 8c583f', O='423732',
            E='4f4f4f 191919', T='bdbdbd eeeeee d4d4d4 4c4c4c 403632', B='796064 d2b48e ac9082 3c314f', K='000000 595959 fff2ec'),
    4: dict(H='69451b 57351a 2f160f 432415 421b19 442414', S='ffd8b2 fbbf97 e9a384 352c27 e29878 c5896e bd8068', O='493e38',
            E='4f4f4f 191919', T='bdbdbd eeeeee d4d4d4 4c4c4c 5e514c', B='0b100c 071c2e 0f406a 114978', K='000000 595959 1a1a1a 353535'),
    5: dict(H='131313 202020 373737 282828 0e0e0e 414141 303030', S='ffede5 fff6f2 ba917e cf9d86 fcd6c4 e1aa91 c4a68e b0886c ad8572 cab3a9 b48d7c c1a496 ffe0d2 5f4f3f',
            O='705e56 594b45 564842', E='4f4f4f 191919 454545', T='9f3f31 e16451 b24737 640026 403632', B='1d1718 332c23 2a2320 0f0c13',
            K='000000 595959 fff2ec'),
}


def lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def build_map(base, skin, hair, top, bottom, flat=False):
    r = ROLES[base]
    m = {}

    def ramp(keys, target):
        cols = sorted([hx(k) for k in keys.split()], key=lum, reverse=True)
        n = len(cols)
        for i, c in enumerate(cols):
            idx = 0 if n == 1 else round(i * (len(target) - 1) / (n - 1))
            m[c[:3]] = target[idx]
    hr = HAIR[hair] if isinstance(hair, str) else hair
    if flat:
        cols = sorted([hx(k) for k in r['H'].split()], key=lum, reverse=True)
        for i, c in enumerate(cols):
            m[c[:3]] = hr[3] if i == len(cols) - 1 else (hr[2] if (i == len(cols) - 2 and c[:3] != (0x13, 0x13, 0x13)) else hr[1])
    else:
        ramp(r['H'], hr)
    # skin: light, light, shadow, shadow
    ramp(r['S'], [skin[0], skin[0], skin[1], skin[1]])
    for k in r['O'].split():
        m[hx(k)[:3]] = skin[2]
    for k in r['E'].split():
        m[hx(k)[:3]] = INK
    ramp(r['T'], CL[top])
    if 'B' in r:
        ramp(r['B'], CL[bottom])
    if 'X' in r:
        for k in r['X'].split():
            m[hx(k)[:3]] = CL[bottom][2]
    for k in r['K'].split():
        c = hx(k)[:3]
        m[c] = INK if lum(c) < 70 else (GREY[2] if lum(c) < 150 else GREY[0])
    return m


def load_base(i):
    return Image.open(BASE_DIR + 'char_%d.png' % i).convert('RGBA')


def person(base, skin, hair, top, bottom, white_top=False, flat=False):
    """returns frames[dir][f] -> 16x32 RGBA recoloured and role layer (dict (x,y)->role)"""
    im = load_base(base)
    m = build_map(base, skin, hair, top, bottom, flat)
    hairset = set(hx(k)[:3] for k in ROLES[base]['H'].split())
    skinset = set(hx(k)[:3] for k in ROLES[base]['S'].split())
    out = []
    for d in range(3):
        row = []
        for f in range(3):
            c = Image.new('RGBA', (16, 32), (0, 0, 0, 0))
            roles = {}
            for y in range(32):
                for x in range(16):
                    p = im.getpixel((f * 16 + x, d * 32 + y))
                    if p[3] == 0:
                        continue
                    k = p[:3]
                    if k == (255, 255, 255):
                        # eye white in head area, else shirt
                        if y <= 18 and d != 1:
                            col = WHITE; roles[(x, y)] = 'eye'
                        else:
                            col = CL[top][0] if not white_top else WHITE; roles[(x, y)] = 'top'
                    else:
                        col = m.get(k)
                        if col is None:
                            col = nearest(p)
                        if k in hairset:
                            roles[(x, y)] = 'hair'
                        elif k in skinset:
                            roles[(x, y)] = 'skin'
                        else:
                            roles[(x, y)] = 'other'
                    c.putpixel((x, y), col)
            if flat:
                hr = HAIR[hair] if isinstance(hair, str) else hair
                for (x, y), rr in list(roles.items()):
                    if rr == 'hair' and c.getpixel((x, y)) == hr[3] and all(
                            roles.get((x + dx, y + dy)) == 'hair' for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                        c.putpixel((x, y), hr[1])
                hb = bbox(roles, {'hair'})
                cxm = (hb[0] + hb[2]) / 2 if hb else 8
                for (x, y), rr in list(roles.items()):
                    if rr == 'hair' and c.getpixel((x, y)) == hr[1] and y > 0:
                        up = c.getpixel((x, y - 1))
                        if up == hr[3] and x < cxm + (1 if d == 1 else 0):
                            c.putpixel((x, y), hr[0])
            row.append((c, roles))
        out.append(row)
    return out


def all_palette():
    cols = [INK, INK2, WHITE, PAPER, CREAM, GOLD, APO, EXTRA_ROSE_SH] + SAND + GREY + STEEL + ROOF + WATER
    for v in list(SKIN.values()) + list(HAIR.values()) + list(CL.values()):
        cols += v
    return cols


def nearest(p):
    best = None
    for c in all_palette():
        d = sum((a - b) ** 2 for a, b in zip(p[:3], c[:3]))
        if best is None or d < best[0]:
            best = (d, c)
    return best[1]


# ---------------------------------------------------------------- drawing helpers
def px(img, x, y, c):
    if 0 <= x < img.width and 0 <= y < img.height and c is not None:
        img.putpixel((x, y), c)


def rect(img, x0, y0, x1, y1, c):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            px(img, x, y, c)


def grid(img, ox, oy, rows, cmap):
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch in cmap:
                px(img, ox + i, oy + j, cmap[ch])


def bbox(roles, want):
    pts = [p for p, r in roles.items() if r in want]
    if not pts:
        return None
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def lowest(img):
    for y in range(img.height - 1, -1, -1):
        for x in range(img.width):
            if img.getpixel((x, y))[3]:
                return y
    return 0


def eyes(roles):
    return sorted([p for p, r in roles.items() if r == 'eye'])


# ---------------------------------------------------------------- hair / face modifiers (operate on 16x32 person)
def recolor_role(img, roles, role, ramp_from, ramp_to):
    for (x, y), r in roles.items():
        if r == role:
            c = img.getpixel((x, y))
            if c in ramp_from:
                img.putpixel((x, y), ramp_to[ramp_from.index(c)])


D_CUR = [0]


def make_bald(img, roles, skin, fringe):
    """hair -> skin dome, keep a grey fringe at the sides (down/right)."""
    hb = bbox(roles, {'hair'})
    if not hb:
        return
    x0, y0, x1, y1 = hb
    # rebuild the skull as a rounded dome inside the hair area
    d = D_CUR[0]
    cx = (x0 + x1) / 2 + (0.5 if d == 2 else 0)
    rx = (x1 - x0) / 2 + 0.4
    cy = y1 - 1
    ry = (y1 - y0) - 0.4
    keep = set()
    for (x, y), r in list(roles.items()):
        if r != 'hair':
            continue
        if (abs(x - cx) / rx) ** 2.3 + (abs(y - cy) / ry) ** 2.3 <= 1.0 or y >= y1 - 1:
            keep.add((x, y))
        else:
            img.putpixel((x, y), (0, 0, 0, 0)); del roles[(x, y)]
    for (x, y) in keep:
        edge = any((x + dx, y + dy) not in roles for dx, dy in ((1, 0), (-1, 0), (0, -1), (0, 1)))
        fr = (d == 0 and y >= y1 - 4 and (x <= x0 + 1 or x >= x1 - 1)) or (d == 1 and y >= y1 - 2) or              (d == 2 and y >= y1 - 4 and x <= x0 + 3)
        if edge:
            img.putpixel((x, y), INK2 if not fr else fringe[2])
        elif fr:
            img.putpixel((x, y), fringe[1] if (x + y) % 3 else fringe[0])
        else:
            rel = (x - x0) / max(1, (x1 - x0))
            img.putpixel((x, y), skin[1] if (rel > 0.72 or (d == 1 and rel > 0.6)) else skin[0])
        roles[(x, y)] = 'skin' if not fr else 'hair'
    hb2 = bbox(roles, {'skin'})
    top = min(y for (x, y) in keep)
    row = sorted(x for (x, y) in keep if y == top + 1)
    if row and d != 1:
        px(img, row[0] + 2, top + 2, skin[0] if skin is not SKIN['s4'] else hx('C98E62'))
        px(img, row[0] + 3, top + 2, hx('C98E62'))
        px(img, row[0] + 2, top + 3, hx('C98E62'))
    return
    # shine
    px(img, x0 + 4, y0 + 2, WHITE if skin is SKIN['s1'] else skin[0])


def add_bun(img, roles, d, ramp):
    hb = bbox(roles, {'hair'})
    x0, y0, x1, y1 = hb
    cx = (x0 + x1) // 2
    if d == 2:
        cx = x0 + 3
    rows = [' oooo ', 'o1122o', 'o1223o', ' o33o ']
    cmap = {'o': ramp[3], '1': ramp[0], '2': ramp[1], '3': ramp[2]}
    grid(img, cx - 3, max(0, y0 - 3), rows, cmap)


def add_hijab(img, roles, d, ramp):
    """hair already recoloured to the scarf ramp; extend a drape over neck and shoulders."""
    hb = bbox(roles, {'hair'})
    x0, y0, x1, y1 = hb
    fb = bbox(roles, {'skin', 'eye'})
    # neck / chin wrap: rows just below the face down to shoulders
    if d == 0:
        # frame the face: columns next to face get scarf, and a band under the chin
        ey = [p for p in eyes(roles)]
        top_face = min(p[1] for p in ey) - 2 if ey else y1 - 4
        for y in range(top_face, y1 + 5):
            for x in range(x0 + 1, x1):
                r = roles.get((x, y))
                if r == 'skin' and (x <= x0 + 2 or x >= x1 - 2):
                    img.putpixel((x, y), ramp[2]); roles[(x, y)] = 'hair'
        # chin band + shoulder drape
        chin = y1 + 3
        for y in range(chin, chin + 3):
            for x in range(x0 + 2, x1 - 1):
                if (x, y) in roles:
                    img.putpixel((x, y), ramp[1] if y < chin + 2 else ramp[2]); roles[(x, y)] = 'hair'
    elif d == 1:
        for y in range(y1, y1 + 5):
            for x in range(x0 + 2, x1 - 1):
                if (x, y) in roles and roles[(x, y)] != 'other' or ((x, y) in roles and y < y1 + 4):
                    img.putpixel((x, y), ramp[1] if x < (x0 + x1) // 2 else ramp[2]); roles[(x, y)] = 'hair'
    else:
        # side: cover neck, back of head down to shoulder
        ey = eyes(roles)
        exx = min(p[0] for p in ey) if ey else x1
        for y in range(y1 - 2, y1 + 5):
            for x in range(x0, x1 + 1):
                r = roles.get((x, y))
                if r == 'skin' and y > y1 and x <= exx - 2:
                    img.putpixel((x, y), ramp[1]); roles[(x, y)] = 'hair'


def add_beard(img, roles, d, col, col2):
    if d == 1:
        return
    ey = eyes(roles)
    if not ey:
        return
    ex0 = min(p[0] for p in ey); ex1 = max(p[0] for p in ey); eyy = max(p[1] for p in ey)
    for (x, y), r in list(roles.items()):
        if r == 'skin' and eyy + 1 <= y <= eyy + 4:
            if d == 0 and ex0 - 1 <= x <= ex1 + 1:
                # leave mouth line as darker, beard around
                img.putpixel((x, y), col if (y > eyy + 1 or x in (ex0 - 1, ex1 + 1)) else img.getpixel((x, y)))
            if d == 2 and x >= ex0 - 3:
                if y > eyy + 1 or x <= ex0 - 2:
                    img.putpixel((x, y), col)
    # moustache hint
    if d == 0:
        cx = (ex0 + ex1) // 2
        px(img, cx, eyy + 2, col2); px(img, cx + 1, eyy + 2, col2)


def add_glasses(img, roles, d, col):
    if d == 1:
        return
    ey = eyes(roles)
    if not ey:
        return
    ys = sorted(set(p[1] for p in ey)); y = ys[0]
    xs = sorted(set(p[0] for p in ey))
    if d == 0:
        # eyes groups
        g1 = [x for x in xs if x < 8]; g2 = [x for x in xs if x >= 8]
        for g in (g1, g2):
            if g:
                px(img, min(g) - 1, y, col); px(img, max(g) + 2, y, col)
                for x in range(min(g) - 1, max(g) + 3):
                    px(img, x, y - 1, col)
        if g1 and g2:
            for x in range(max(g1) + 2, min(g2) - 1 + 1):
                px(img, x, y, col)
    else:
        x0 = min(xs)
        for x in range(x0 - 1, x0 + 3):
            px(img, x, y - 1, col)
        px(img, x0 - 1, y, col); px(img, x0 + 2, y, col)
        for x in range(x0 - 4, x0 - 1):
            px(img, x, y - 1, col)


def add_wrap_top(img, roles, d, ramp):
    hb = bbox(roles, {'hair'})
    x0, y0, x1, y1 = hb
    cx = (x0 + x1) // 2
    if d == 2:
        rows = ['  oooo  ', ' o1122o ', 'o112223o']
        grid(img, x0 + 2, max(0, y0 - 2), rows[1:] if False else [], {'o': ramp[3], '1': ramp[0], '2': ramp[1], '3': ramp[2]})
    else:
        rows = ['  oooo  ', ' o1122o ', 'o112223o']
        grid(img, cx - 4, max(0, y0 - 2), [], {'o': ramp[3], '1': ramp[0], '2': ramp[1], '3': ramp[2]})
    # diagonal folds across the wrap
    for (x, y), r in roles.items():
        if r == 'hair' and img.getpixel((x, y)) == ramp[1] and (x + y) % 6 == 0 and y0 + 2 < y < y1 - 2:
            img.putpixel((x, y), ramp[2])


def add_ponytail(img, roles, d, ramp):
    hb = bbox(roles, {'hair'})
    x0, y0, x1, y1 = hb
    if d == 1:
        cx = (x0 + x1) // 2
        for y in range(y1 - 1, y1 + 4):
            px(img, cx, y, ramp[2]); px(img, cx + 1, y, ramp[1])
        px(img, cx, y1 - 2, GOLD if False else ramp[3]); px(img, cx + 1, y1 - 2, ramp[3])
    elif d == 2:
        bx = x0
        rows = ['o1', 'o12o', ' o2o', ' o2o', '  oo']
        grid(img, bx - 2, y0 + 6, rows, {'o': ramp[3], '1': ramp[1], '2': ramp[2]})


def add_braids(img, roles, d, ramp):
    """long hair -> braids: add a highlight pattern on the hanging strands."""
    hb = bbox(roles, {'hair'})
    x0, y0, x1, y1 = hb
    for (x, y), r in roles.items():
        if r == 'hair' and y > y0 + 6:
            c = img.getpixel((x, y))
            if c not in (ramp[3],):
                img.putpixel((x, y), ramp[0] if (y + (x // 2)) % 3 == 0 else ramp[2])


# ---------------------------------------------------------------- props
def suitcase(c, x, y, d, f):
    # body 7x9 at (x,y) top-left, handle up from top
    s = [hx('74A590'), hx('3E7F7F'), hx('1F5C4A')]
    rows = ['ooooooo', 'o11122o', 'o12222o', 'o12222o', 'o3333ko', 'o12222o', 'o12222o', 'o22223o', 'ooooooo']
    grid(c, x, y, rows, {'o': INK, '1': s[0], '2': s[1], '3': s[2], 'k': GOLD})
    px(c, x + 1, y + 9, INK); px(c, x + 5, y + 9, INK)
    px(c, x + 1 + (f % 2), y + 9, INK2)


def stroller(c, d, f, ox):
    can = [hx('74A590'), hx('3E7F7F'), hx('1F5C4A')]
    if d == 2:
        x = ox
        rows = [
            '    oooo    ',
            '  oo1122o   ',
            ' o11222233o ',
            'o1122223333o',
            'o1222o......',
            'oooooooooooo',
            'o4444444444o',
            ' o55555555o ',
            '  oooooooo  ',
        ]
        grid(c, x, 18, rows, {'o': INK, '1': can[0], '2': can[1], '3': can[2], '4': GREY[1], '5': GREY[2]})
        # frame and wheels
        px(c, x + 3, 27, INK2); px(c, x + 8, 27, INK2)
        for wx in (x + 1, x + 8):
            grid(c, wx, 28, [' oo ', 'o' + ('g' if f != 1 else 'o') + 'go', 'oggo' if f == 1 else 'o' + 'o' + 'go', ' oo '][:4],
                 {'o': INK, 'g': GREY[1]})
        # handle bar back to the hands
        for i in range(4):
            px(c, x - 1 - i, 21 - (i // 2), INK2)
    elif d == 0:
        x = 10
        rows = [
            '   oooooo   ',
            ' oo111222oo ',
            'o1111222223o',
            'o1122222333o',
            'o1o......o3o',
            'oooooooooooo',
            'o4444444444o',
            'o5555555555o',
            ' oooooooooo ',
        ]
        grid(c, x, 20, rows, {'o': INK, '1': can[0], '2': can[1], '3': can[2], '4': GREY[1], '5': GREY[2]})
        # baby face peeking under the hood
        grid(c, x + 4, 24, ['ssss'], {'s': SKIN['s6'][0]})
        px(c, x + 5, 24, INK); px(c, x + 7, 24, INK)
        for wx in (x, x + 9):
            grid(c, wx, 29, ['ooo', 'ogo' if f != 1 else 'oog', ' o '], {'o': INK, 'g': GREY[1]})
    else:
        # up: stroller ahead, behind the body: hood peeks at the sides, handle bar at the hands
        x = 8
        rows = [
            '  oooooooooooo  ',
            ' o111122222233o ',
            'o11112222223333o',
            'o11222222223333o',
            'o12222222223333o',
            'oooooooooooooooo',
        ]
        grid(c, x, 14, rows, {'o': INK, '1': can[0], '2': can[1], '3': can[2]})


def wheelchair_back(c, d, f):
    if d == 1:
        # backrest + bag (drawn over the lower back), wheels at the sides
        pass


def wheel_side(c, cx, cy, f):
    # 11px wheel
    rows = [
        '   ooooo   ',
        '  o11111o  ',
        ' o1o...o1o ',
        'o1o.....o1o',
        'o1.......1o',
        'o1...h...1o',
        'o1.......1o',
        'o1o.....o1o',
        ' o1o...o1o ',
        '  o11111o  ',
        '   ooooo   ',
    ]
    grid(c, cx - 5, cy - 5, rows, {'o': INK, '1': GREY[1], 'h': GREY[0]})
    # spokes rotate by frame
    sp = [((0, -3), (0, 3), (-3, 0), (3, 0)), ((-2, -2), (2, 2), (-2, 2), (2, -2)), ((0, -3), (0, 3), (-3, 0), (3, 0))][f]
    for dx, dy in sp:
        px(c, cx + dx, cy + dy, GREY[2])
        px(c, cx + dx // 2 if dx else cx, cy + dy // 2 if dy else cy, GREY[2])


# ---------------------------------------------------------------- child sprite (10 px wide, 15 tall)
KID = {
    0: [  # down
        '  oooooo  ',
        ' ohhhhhho ',
        'ohhhhhhhho',
        'ohHhhhhHho',
        'ossssssss o'[:10],
        'osEssssEso',
        'osssssssso',
        ' oss..sso '.replace('.', 's'),
        '  ottttO  '.replace('O', 'o'),
        ' ottttttgo',
        'ottttttttS',
        'Sottttttto',
        ' oppppppo ',
    ],
    1: [  # up (back)
        '  oooooo  ',
        ' ohhhhhho ',
        'ohhhhhhhho',
        'ohhhhhhhho',
        'ohhhhhhhho',
        'ohhhhhhhho',
        'oshhhhhhso',
        ' ossssso  '.replace('ossssso ', 'osssssso'),
        '  ottttO  '.replace('O', 'o'),
        ' obbbbbbto',
        'obbbbbbbtS',
        'Sobbbbbbto',
        ' oppppppo ',
    ],
    2: [  # right
        '  ooooo   ',
        ' ohhhhhoo ',
        'ohhhhhhhho',
        'ohhhhhHsso',
        'ohhhhsssso',
        'ohhhsssEso',
        ' ohssssso ',
        '  osssso  ',
        '  otttto  ',
        '  ottttSo ',
        '  otttto  ',
        '  ottttSo '[:10].replace('S', 't'),
        '  oppppo  ',
    ],
}
KID_LEGS = {
    0: [[' op  po   ', ' ok  po   ', ' oo  ko   '], [' op  po   ', ' op  ko   ', ' ko  oo   ']],
    1: [[' op  po   ', ' ok  po   ', ' oo  ko   '], [' op  po   ', ' op  ko   ', ' ko  oo   ']],
    2: [['  op po   ', ' ok  po   ', ' oo   ko  '], ['  oppo    ', '  opko    ', '  ko      ']],
}


def draw_kid(c, x, y_feet, d, f, skin, hair, top, bag=None, flip=False):
    rows = KID[d]
    legs = KID_LEGS[d][f % 2]
    allrows = rows + legs
    top_y = y_feet - len(allrows) + 1
    cmap = {'o': INK, 'h': hair[1], 'H': hair[0], 's': skin[0], 'S': skin[0], 'E': INK, 't': top[1], 'g': top[0],
            'p': CL['denim'][1], 'k': INK2, 'b': (bag or top)[1]}
    if bag is None:
        cmap['b'] = top[1]
    for j, r in enumerate(allrows):
        for i, ch in enumerate(r):
            if ch in cmap:
                xx = x + (9 - i if flip else i)
                px(c, xx, top_y + j, cmap[ch])
    return top_y


def hand_link(c, pts, col):
    # joined hands: fill only transparent pixels so no outline is overwritten
    for (x, y) in pts:
        if c.getpixel((x, y))[3] == 0:
            px(c, x, y, col)


# ---------------------------------------------------------------- composition
def cellimg():
    return Image.new('RGBA', (32, 32), (0, 0, 0, 0))


def paste_person(c, img, ox, drop=0):
    oy = 31 - lowest(img) - drop
    c.alpha_composite(img, (ox, oy))
    return oy


def build():
    sheet = Image.new('RGBA', (384, 288), (0, 0, 0, 0))
    chars = []

    def block(idx, cells):
        bx = (idx % 4) * 96; by = (idx // 4) * 96
        for d in range(3):
            for f in range(3):
                sheet.alpha_composite(cells[d][f], (bx + f * 32, by + d * 32))

    # ---- 1 woman s3, sage hijab, suitcase
    P = person(5, SKIN['s3'], [hx('A9CDBB'), hx('8FA888'), hx('4E7E6B'), INK2], 'navy', 'charcoal', flat=True)
    cells = []
    for d in range(3):
        row = []
        for f in range(3):
            img, roles = P[d][f][0].copy(), dict(P[d][f][1])
            add_hijab(img, roles, d, CL['sage'])
            c = cellimg()
            if d == 0:
                suitcase(c, 22, 21, d, f); rect(c, 23, 18, 23, 20, INK2); rect(c, 26, 18, 26, 20, INK2); rect(c, 23, 18, 26, 18, INK2)
                paste_person(c, img, 8)
            elif d == 1:
                paste_person(c, img, 8)
                suitcase(c, 3, 21, d, f); rect(c, 4, 18, 4, 20, INK2); rect(c, 7, 18, 7, 20, INK2); rect(c, 4, 18, 7, 18, INK2)
            else:
                suitcase(c, 1, 21, d, f)
                for i in range(5):
                    px(c, 6 + i, 20 - i // 2 + 0, INK2)
                paste_person(c, img, 10)
            row.append(c)
        cells.append(row)
    block(0, cells); chars.append(('hijab-suitcase', 'Woman in a sage hijab with a rolling suitcase'))

    # ---- 2 man s6, short afro, stroller
    P = person(2, SKIN['s6'], 'black', 'mustard', 'denim')
    cells = []
    for d in range(3):
        row = []
        for f in range(3):
            img, roles = P[d][f]
            c = cellimg()
            if d == 0:
                paste_person(c, img, 8); stroller(c, d, f, 0)
            elif d == 1:
                stroller(c, d, f, 0); paste_person(c, img, 8)
            else:
                paste_person(c, img, 2); stroller(c, d, f, 19)
            row.append(c)
        cells.append(row)
    block(1, cells); chars.append(('afro-stroller', 'Man with a short afro pushing a stroller'))

    # ---- 3 grandmother s1, grey bun, holds a child's hand (child with a Kita bag)
    P = person(3, SKIN['s1'], 'grey', 'rose', 'charcoal')
    cells = []
    for d in range(3):
        row = []
        for f in range(3):
            img, roles = P[d][f][0].copy(), dict(P[d][f][1])
            add_bun(img, roles, d, HAIR['grey'])
            c = cellimg()
            if d == 0:
                paste_person(c, img, 4)
                draw_kid(c, 21, 31, 0, f, SKIN['s1'], HAIR['blonde'], CL['teal'])
                hand_link(c, [(18, 25), (19, 26), (20, 27)], SKIN['s1'][0])
            elif d == 1:
                draw_kid(c, 1, 31, 1, f, SKIN['s1'], HAIR['blonde'], CL['teal'], bag=CL['mustard'])
                paste_person(c, img, 12)
                hand_link(c, [(11, 27), (12, 26), (13, 25)], SKIN['s1'][0])
            else:
                draw_kid(c, 18, 31, 2, f, SKIN['s1'], HAIR['blonde'], CL['teal'])
                paste_person(c, img, 5)
            row.append(c)
        cells.append(row)
    block(2, cells); chars.append(('grandma-child', 'Grandmother with a grey bun holding a small child by the hand'))

    # ---- 4 young man s4, curly hair, wheelchair with backpack
    P = person(4, SKIN['s4'], 'black', 'teal', 'denim')
    cells = []
    for d in range(3):
        row = []
        for f in range(3):
            img, roles = P[d][1]  # neutral pose, upper body
            up = img.copy()
            # cut legs: keep rows above the waist (lowest - 6)
            lo = lowest(up)
            waist = lo - 5
            rect(up, 0, waist + 1, 15, 31, (0, 0, 0, 0))
            c = cellimg()
            if d == 0:
                # wheels behind at the sides
                for wx in (6, 23):
                    rect(c, wx, 19, wx + 2, 30, INK); rect(c, wx + 1, 20, wx + 1, 29, GREY[1])
                    px(c, wx + 1, 21 + (f * 3) % 8, GREY[0])
                oy = 31 - waist - 5
                c.alpha_composite(up, (8, oy))
                # lap / legs / feet
                rect(c, 11, oy + waist - 1, 20, oy + waist + 1, CL['denim'][1]); rect(c, 11, oy + waist + 2, 20, oy + waist + 2, INK2)
                rect(c, 12, oy + waist + 3, 14, 28, CL['denim'][1]); rect(c, 17, oy + waist + 3, 19, 28, CL['denim'][1]); px(c, 12, oy + waist + 3, CL['denim'][0]); px(c, 17, oy + waist + 3, CL['denim'][0])
                rect(c, 12, 29, 14, 29, INK); rect(c, 17, 29, 19, 29, INK)
                rect(c, 10, 30, 21, 30, GREY[2]); rect(c, 10, 31, 21, 31, INK)
                px(c, 7 + (f % 2), 31, INK); px(c, 24 - (f % 2), 31, INK)
            elif d == 1:
                oy = 31 - waist - 5
                c.alpha_composite(up, (8, oy))
                # backrest + backpack hanging on it
                rect(c, 10, 19, 21, 27, INK2); rect(c, 11, 20, 20, 26, CL['charcoal'][1])
                bp = CL['terracotta']
                rect(c, 12, 21, 19, 27, INK); rect(c, 13, 22, 18, 26, bp[1]); rect(c, 13, 22, 18, 22, bp[0]); rect(c, 13, 24, 18, 24, bp[2])
                px(c, 10, 17, INK2); px(c, 10, 18, INK2); px(c, 21, 17, INK2); px(c, 21, 18, INK2)
                for wx in (6, 23):
                    rect(c, wx, 20, wx + 2, 31, INK); rect(c, wx + 1, 21, wx + 1, 30, GREY[1])
                    px(c, wx + 1, 22 + (f * 3) % 8, GREY[0])
            else:
                oy = 31 - waist - 8
                # backpack on the backrest (behind)
                bp = CL['terracotta']
                rect(c, 5, 15, 9, 22, INK); rect(c, 6, 16, 8, 21, bp[1]); rect(c, 6, 16, 8, 16, bp[0]); rect(c, 6, 19, 8, 19, bp[2])
                rect(c, 9, 12, 9, 24, INK2); px(c, 8, 12, INK2)  # push handle / backrest post
                c.alpha_composite(up, (7, oy))
                # thighs and shins
                sy = oy + waist + 1
                pn = CL['denim']
                rect(c, 9, sy + 1, 19, sy + 1, INK2)  # seat rail
                wheel_side(c, 13, 25, f)
                # thigh (outlined), shin, shoe, footrest - drawn over the wheel's near side
                rect(c, 12, sy - 3, 22, sy + 1, INK); rect(c, 13, sy - 2, 21, sy, pn[1]); rect(c, 13, sy - 2, 21, sy - 2, pn[0])
                rect(c, 18, sy, 22, 29, INK); rect(c, 19, sy, 21, 28, pn[1]); rect(c, 19, sy, 19, 28, pn[0])
                rect(c, 19, 28, 24, 29, INK); px(c, 23, 28, INK2)
                rect(c, 18, 30, 25, 30, GREY[2])
                px(c, 23, 31, INK); px(c, 22, 31, INK2)
            row.append(c)
        cells.append(row)
    block(3, cells); chars.append(('wheelchair', 'Young man with curly hair in a wheelchair with a backpack'))

    # ---- 5 man s2, trimmed beard, glasses, document folder
    P = person(0, SKIN['s2'], 'dbrown', 'navy', 'navy')
    cells = []
    for d in range(3):
        row = []
        for f in range(3):
            img, roles = P[d][f][0].copy(), dict(P[d][f][1])
            add_beard(img, roles, d, HAIR['dbrown'][1], HAIR['dbrown'][2])
            add_glasses(img, roles, d, INK)
            c = cellimg()
            oy = paste_person(c, img, 8)
            fo = [hx('C9704F'), hx('93493A')]
            if d == 0:
                rect(c, 20, oy + 18, 23, oy + 23, INK); rect(c, 21, oy + 19, 22, oy + 22, fo[0]); px(c, 22, oy + 22, fo[1])
            elif d == 1:
                rect(c, 8, oy + 18, 11, oy + 23, INK); rect(c, 9, oy + 19, 10, oy + 22, fo[0])
            else:
                rect(c, 17, oy + 18, 22, oy + 21, INK); rect(c, 18, oy + 19, 21, oy + 20, fo[0]); px(c, 21, oy + 20, fo[1])
            row.append(c)
        cells.append(row)
    block(4, cells); chars.append(('beard-folder', 'Man with a trimmed beard and glasses carrying a document folder'))

    # ---- 6 teen s5, braids, violin case
    P = person(1, SKIN['s5'], 'black', 'terracotta', 'charcoal')
    cells = []
    vc = [hx('7A5234'), hx('4A3326')]
    for d in range(3):
        row = []
        for f in range(3):
            img, roles = P[d][f][0].copy(), dict(P[d][f][1])
            add_braids(img, roles, d, HAIR['black'])
            c = cellimg()
            if d == 0:
                # case neck peeks over the left shoulder
                rect(c, 20, 10, 22, 17, INK); rect(c, 21, 11, 21, 16, vc[0])
                oy = paste_person(c, img, 8)
            elif d == 1:
                oy = paste_person(c, img, 8)
                grid(c, 11, 11, [' ooo ', ' o1o ', ' o1o ', 'oo1oo', 'o112o', 'o112o', 'oo12oo'[:5], 'o1122o'[:5], 'o1122o'[:5], 'o1122o'[:5], 'o1122o'[:5], ' ooo '],
                     {'o': INK, '1': vc[0], '2': vc[1]})
                rect(c, 12, 22, 14, 22, GOLD)
            else:
                grid(c, 5, 12, [' oo ', 'o12o', 'o12o', 'o12o', 'o12o', 'o112o'[:4], 'o12o', 'o12o', 'ok2o', 'o12o', 'o12o', 'o12o', ' oo '],
                     {'o': INK, '1': vc[0], '2': vc[1], 'k': GOLD})
                oy = paste_person(c, img, 8)
            row.append(c)
        cells.append(row)
    block(5, cells); chars.append(('braids-violin', 'Teenager with braids and a violin case on the back'))

    # ---- 7 woman s1, short black bob, toddler in a sling
    P = person(5, SKIN['s1'], 'black', 'sage', 'denim', flat=True)
    cells = []
    sl = CL['mustard']
    for d in range(3):
        row = []
        for f in range(3):
            img, roles = P[d][f]
            c = cellimg()
            oy = paste_person(c, img, 8)
            if d == 0:
                # sling strap diagonal + toddler head on the chest
                for i in range(7):
                    px(c, 11 + i, oy + 16 + i // 2 + 0, sl[1])
                grid(c, 13, oy + 18, [' oooo ', 'ohhhho', 'ohsssо'.replace('о', 'o'), ' oooo ', 'o1111o', ' o11o '],
                     {'o': INK, 'h': HAIR['brown'][1], 's': SKIN['s1'][0], '1': sl[1]})
            elif d == 1:
                for i in range(8):
                    px(c, 11 + i, oy + 17 + i // 2, sl[1]); px(c, 19 - i, oy + 17 + i // 2, sl[2])
                rect(c, 14, oy + 16, 17, oy + 16, sl[1])
            else:
                grid(c, 17, oy + 17, [' ooo ', 'ohhso', 'ohsso', 'o111o', 'o11o', ' oo'],
                     {'o': INK, 'h': HAIR['brown'][1], 's': SKIN['s1'][0], '1': sl[1]})
                for i in range(5):
                    px(c, 12 + i, oy + 17 + i // 2, sl[2])
            row.append(c)
        cells.append(row)
    block(6, cells); chars.append(('bob-sling', 'Woman with a short black bob carrying a toddler in a sling'))

    # ---- 8 older man s4, bald, grey beard, white cane
    P = person(0, SKIN['s4'], 'grey', 'teal', 'charcoal')
    cells = []
    for d in range(3):
        row = []
        for f in range(3):
            img, roles = P[d][f][0].copy(), dict(P[d][f][1])
            D_CUR[0] = d
            make_bald(img, roles, SKIN['s4'], HAIR['grey'])
            add_beard(img, roles, d, HAIR['grey'][0], HAIR['grey'][2])
            c = cellimg()
            oy = paste_person(c, img, 8)
            tip = [0, 2, 1][f]
            if d == 0:
                # cane from right hand down and forward (towards viewer), tip taps
                hxp, hyp = 21, oy + 21
                for i in range(31 - hyp + 1):
                    px(c, hxp + (i * (3 + tip)) // 10, hyp + i, WHITE)
                px(c, hxp + ((31 - hyp) * (3 + tip)) // 10, 31, APO)
            elif d == 1:
                hxp, hyp = 10, oy + 21
                for i in range(6):
                    px(c, hxp - i // 3, hyp + i, WHITE)
            else:
                hxp, hyp = 18, oy + 21
                n = 31 - hyp
                ex = 26 + tip
                for i in range(n + 1):
                    px(c, hxp + (ex - hxp) * i // n, hyp + i, WHITE)
                px(c, ex, 31, APO)
            row.append(c)
        cells.append(row)
    block(7, cells); chars.append(('cane', 'Older man with a grey beard and a white cane'))

    # ---- 9 young woman s1, long red hair, backpack + book
    P = person(1, SKIN['s1'], 'red', 'denim', 'charcoal', flat=False)
    cells = []
    bp = CL['teal']
    for d in range(3):
        row = []
        for f in range(3):
            img, roles = P[d][f]
            c = cellimg()
            if d == 2:
                rect(c, 5, 16, 9, 24, INK); rect(c, 6, 17, 8, 23, bp[1]); rect(c, 6, 17, 8, 17, bp[0]); rect(c, 6, 20, 8, 20, bp[2])
            oy = paste_person(c, img, 8)
            if d == 0:
                px(c, 11, oy + 17, bp[2]); px(c, 11, oy + 18, bp[2]); px(c, 20, oy + 17, bp[2]); px(c, 20, oy + 18, bp[2])
                rect(c, 8, oy + 19, 11, oy + 23, INK); rect(c, 9, oy + 20, 10, oy + 22, APO); px(c, 10, oy + 20, WHITE)
            elif d == 1:
                rect(c, 11, oy + 16, 20, oy + 24, INK); rect(c, 12, oy + 17, 19, oy + 23, bp[1]); rect(c, 12, oy + 17, 19, oy + 17, bp[0])
                rect(c, 12, oy + 20, 19, oy + 20, bp[2]); px(c, 15, oy + 21, GOLD)
            else:
                rect(c, 17, oy + 19, 20, oy + 22, INK); rect(c, 18, oy + 20, 19, oy + 21, APO)
            row.append(c)
        cells.append(row)
    block(8, cells); chars.append(('red-backpack', 'Young woman with long red hair, a backpack and a book'))

    # ---- 10 parent s3, dark hair, child holding hands
    P = person(4, SKIN['s3'], 'dbrown', 'sage', 'denim')
    cells = []
    for d in range(3):
        row = []
        for f in range(3):
            img, roles = P[d][f]
            c = cellimg()
            if d == 0:
                oy = paste_person(c, img, 4)
                draw_kid(c, 21, 31, 0, f, SKIN['s3'], HAIR['black'], CL['mustard'])
                hand_link(c, [(18, 25), (19, 26), (20, 27)], SKIN['s3'][0])
            elif d == 1:
                draw_kid(c, 1, 31, 1, f, SKIN['s3'], HAIR['black'], CL['mustard'])
                oy = paste_person(c, img, 12)
                hand_link(c, [(11, 27), (12, 26), (13, 25)], SKIN['s3'][0])
            else:
                draw_kid(c, 18, 31, 2, f, SKIN['s3'], HAIR['black'], CL['mustard'])
                oy = paste_person(c, img, 5)
            row.append(c)
        cells.append(row)
    block(9, cells); chars.append(('parent-child', 'Parent walking hand in hand with a child'))

    # ---- 11 woman s6, mustard head wrap, bag with a pretzel
    P = person(0, SKIN['s6'], [hx('E0B04A'), hx('D9A441'), hx('8C7453'), hx('5E4C38')], 'teal', 'charcoal', flat=True)
    cells = []
    for d in range(3):
        row = []
        for f in range(3):
            img, roles = P[d][f][0].copy(), dict(P[d][f][1])
            add_wrap_top(img, roles, d, CL['mustard'])
            c = cellimg()
            oy = paste_person(c, img, 8)
            bag = [hx('D9C49A'), hx('B59D73'), hx('8C7453')]
            if d == 0:
                bx, by = 20, oy + 20
            elif d == 1:
                bx, by = 7, oy + 20
            else:
                bx, by = 16, oy + 20
            grid(c, bx, by - 2, [' gg ', 'gbgg', 'oooooo'[:5], 'o111o', 'o122o', 'o122o', 'ooooo'],
                 {'o': INK, '1': bag[0], '2': bag[1], 'g': hx('93493A'), 'b': GOLD})
            row.append(c)
        cells.append(row)
    block(10, cells); chars.append(('wrap-pretzel', 'Woman in a mustard head wrap with a bakery bag'))

    # ---- 12 man s3, ponytail, looks at a phone
    P = person(4, SKIN['s3'], 'black', 'white', 'charcoal', white_top=False)
    cells = []
    for d in range(3):
        row = []
        for f in range(3):
            img, roles = P[d][f][0].copy(), dict(P[d][f][1])
            add_ponytail(img, roles, d, HAIR['black'])
            c = cellimg()
            oy = paste_person(c, img, 8)
            if d == 0:
                rect(c, 14, oy + 19, 17, oy + 21, INK); rect(c, 15, oy + 19, 16, oy + 19, WATER[0])
                px(c, 13, oy + 20, SKIN['s3'][0]); px(c, 18, oy + 20, SKIN['s3'][0])
            elif d == 2:
                rect(c, 19, oy + 18, 20, oy + 21, INK); px(c, 20, oy + 18, WATER[0]); px(c, 21, oy + 17, WATER[0])
                px(c, 18, oy + 20, SKIN['s3'][0])
            row.append(c)
        cells.append(row)
    block(11, cells); chars.append(('ponytail-phone', 'Man with a ponytail looking at his phone'))

    return sheet, chars


def quantize_to_palette(img):
    pal = all_palette()
    keys = set(c[:3] for c in pal)
    out = img.copy()
    for y in range(img.height):
        for x in range(img.width):
            p = img.getpixel((x, y))
            if p[3] == 0:
                out.putpixel((x, y), (0, 0, 0, 0))
            elif p[:3] not in keys:
                out.putpixel((x, y), nearest(p))
            else:
                out.putpixel((x, y), p[:3] + (255,))
    return out


def save_indexed(img, path):
    # palette PNG with transparency index 0
    cols = []
    for p in img.getdata():
        if p[3] and p[:3] not in cols:
            cols.append(p[:3])
    pimg = Image.new('P', img.size, 0)
    flat = [0, 0, 0]
    for c in cols:
        flat += list(c)
    flat += [0] * (768 - len(flat))
    pimg.putpalette(flat)
    idx = {c: i + 1 for i, c in enumerate(cols)}
    w, h = img.size
    data = [idx[p[:3]] if p[3] else 0 for p in img.getdata()]
    pimg.putdata(data)
    pimg.save(path, optimize=True, transparency=0)
    return len(cols)


def previews(sheet):
    os.makedirs(PREV, exist_ok=True)
    bg = Image.new('RGBA', sheet.size, hx('F7F4EC'))
    # light guide grid
    g = Image.new('RGBA', sheet.size, (0, 0, 0, 0))
    for x in range(0, 384, 32):
        for y in range(288):
            g.putpixel((x, y), (0, 0, 0, 25))
    for y in range(0, 288, 32):
        for x in range(384):
            g.putpixel((x, y), (0, 0, 0, 25))
    bg.alpha_composite(g)
    bg.alpha_composite(sheet)
    bg.resize((384 * 6, 288 * 6), Image.NEAREST).convert('RGB').save(PREV + 'people_sheet_6x.png')
    for half in range(2):
        crop = bg.crop((0, half * 144, 384, half * 144 + 144))
        crop.resize((384 * 5, 144 * 5), Image.NEAREST).convert('RGB').save(PREV + 'people_part%d_5x.png' % half)


if __name__ == '__main__':
    sheet, chars = build()
    sheet = quantize_to_palette(sheet)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    n = save_indexed(sheet, OUT)
    previews(sheet)
    print('colours', n, 'bytes', os.path.getsize(OUT))
    lines = ['// Generated by scripts/pixel/make_people.py (team repo). Do not edit by hand.',
             '// Character sprites based on Pixel Agents (https://github.com/pixel-agents-hq/pixel-agents),',
             '// Copyright (c) 2026 Pablo De Lucca, MIT License. Based on MetroCity by JIK-A-4 (CC0).',
             'import type { PeopleDef } from "./types";', '',
             'export const PEOPLE: PeopleDef = {',
             '  src: "/pixel/people.png",', '  cell: 32,', '  frames: 3,', '  rows: { down: 0, up: 1, right: 2 },',
             '  // frame 1 = standing pose (used when a walker pauses), 0 and 2 = steps',
             '  cycle: [1, 0, 1, 2],', '  speed: 14,', '  chars: [']
    for i, (cid, label) in enumerate(chars):
        print(i, cid, label, 'col', i % 4, 'row', i // 4)
        lines.append('    { id: "%s", label: "%s", col: %d, row: %d },' % (cid, label, i % 4, i // 4))
    lines += ['  ],', '};', '']
    with open(TS_OUT, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('\n'.join(lines))
