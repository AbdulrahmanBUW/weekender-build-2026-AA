# -*- coding: utf-8 -*-
"""Pixel Dresden pillar scenes (320x96, transparent sky, walkway feet at y=90).

Run:  python scripts/pixel/make_scenes.py
Writes 1x PNGs to the Lovable repo (public/pixel/scene-<id>.png) and 6x previews to docs/pixel/previews/.
Palette: docs/pixel/BRIEF.md (no extra colours). Light from the top-left. No text in images.
"""
import os
import sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.environ.get("PIXEL_OUT", r"C:/Users/a_rahman/Desktop/Automation/hallotermin-paper/public/pixel")
PREV = os.path.join(ROOT, "docs", "pixel", "previews")

W, H = 320, 96
BASE = 81      # last facade row; pavement starts at 82
FEET = 90

# ---------------------------------------------------------------- palette (BRIEF.md)
INK = "#1C2420"; INK2 = "#3A3F3A"; PAPER = "#F7F4EC"; CREAM = "#EFE4CF"; WHITE = "#FFFFFF"
SAND = ["#F1E4C6", "#D9C49A", "#B59D73", "#8C7453", "#5E4C38"]
COP = ["#A9CDBB", "#74A590", "#4E7E6B"]; PINE = ["#1F5C4A", "#174A3B"]
WATER = ["#B7D1D6", "#8DB2BD", "#638D9B"]
GRASS = ["#BCD08F", "#8FB068", "#638A48", "#3F6233"]
RRED = ["#C9704F", "#93493A"]
GREY = ["#D3CDBF", "#A8A296", "#77736A"]
TRAM = ["#FFD541", "#D9A21B"]; APO = "#B4202A"; GOLD = "#E0B04A"; STEEL = ["#6E97C9", "#3F66A0"]
SAGE = "#8FA888"; MUST = "#D9A441"; TERRA = "#C4674A"; NAVY = "#34496B"; TEAL = "#3E7F7F"
DENIM = "#5C7BA6"; CHAR = "#4A4E52"; ROSE = "#C98B8B"

# facade ramps: (highlight, base, shade, dark)
F_SAND = (SAND[0], SAND[1], SAND[2], SAND[3])
F_CREAM = (WHITE, CREAM, SAND[1], SAND[2])
F_GREY = (WHITE, GREY[0], GREY[1], GREY[2])
F_BLUE = (WATER[0], STEEL[0], STEEL[1], NAVY)
F_YEL = (TRAM[0], MUST, TRAM[1], SAND[3])
F_ROSE = (SAND[0], ROSE, TERRA, RRED[1])
F_SAGE = (GRASS[0], SAGE, GRASS[2], PINE[0])
R_COP = (COP[0], COP[1], COP[2])
R_RED = (RRED[0], RRED[1], SAND[4])
R_GREY = (GREY[0], GREY[1], GREY[2])
R_SLATE = (GREY[1], GREY[2], INK2)


def hx(h):
    return (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16), 255)


class C:
    def __init__(s, w=W, h=H):
        s.w, s.h = w, h
        s.im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        s.p = s.im.load()

    def px(s, x, y, c):
        x, y = int(x), int(y)
        if c and 0 <= x < s.w and 0 <= y < s.h:
            s.p[x, y] = hx(c)

    def clear(s, x, y):
        if 0 <= x < s.w and 0 <= y < s.h:
            s.p[x, y] = (0, 0, 0, 0)

    def get(s, x, y):
        if 0 <= x < s.w and 0 <= y < s.h:
            return s.p[x, y]
        return (0, 0, 0, 0)

    def rect(s, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                s.px(xx, yy, c)

    def hl(s, x0, x1, y, c):
        for x in range(x0, x1 + 1):
            s.px(x, y, c)

    def vl(s, x, y0, y1, c):
        for y in range(y0, y1 + 1):
            s.px(x, y, c)

    def box(s, x, y, w, h, fill, ol=INK):
        s.rect(x, y, w, h, fill)
        s.hl(x, x + w - 1, y, ol); s.hl(x, x + w - 1, y + h - 1, ol)
        s.vl(x, y, y + h - 1, ol); s.vl(x + w - 1, y, y + h - 1, ol)

    def outline(s, c=INK):
        pts = []
        for y in range(s.h):
            for x in range(s.w):
                if s.p[x, y][3] == 0:
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        if s.get(x + dx, y + dy)[3] > 0:
                            pts.append((x, y)); break
        for x, y in pts:
            s.px(x, y, c)

    def comp(s, other):
        s.im.alpha_composite(other.im)


# ---------------------------------------------------------------- ground
def pavement(c, x0=0, x1=W - 1):
    for y in range(82, 96):
        for x in range(x0, x1 + 1):
            # stepped soft ends
            e = min(x - x0, x1 - x)
            if (y >= 94 and e < 3) or (y >= 92 and e < 1):
                continue
            col = GREY[0]
            if y == 82:
                col = GREY[1]                       # foot shadow along the facades
            elif y in (87,):
                col = GREY[1]                       # slab joint
            elif y == 94:
                col = GREY[1]                       # kerb top
            elif y == 95:
                col = GREY[2]
            else:
                band = 0 if y < 87 else 1
                if (x + band * 8) % 16 == 0:
                    col = GREY[1]
                elif (x + band * 8) % 16 == 1 and y in (83, 88):
                    col = WHITE if False else CREAM
            c.px(x, y, col)


def ground_shadow(c, cx, y, rw):
    for x in range(cx - rw, cx + rw + 1):
        for yy in (y, y + 1):
            if yy == y + 1 and abs(x - cx) > rw - 2:
                continue
            p = c.get(x, yy)
            if p[3] and p[:3] in (hx(GREY[0])[:3], hx(CREAM)[:3]):
                c.px(x, yy, GREY[1])


# ---------------------------------------------------------------- building parts
def facade(c, x, y, w, h, f, eave=True):
    c.box(x, y, w, h, f[1])
    c.vl(x + 1, y + 1, y + h - 2, f[0])
    c.vl(x + w - 2, y + 1, y + h - 2, f[2])
    if eave:
        c.hl(x + 1, x + w - 2, y + 1, f[3])
        c.hl(x + 1, x + w - 2, y + 2, f[2])


def band(c, x, y, w, f):
    """string course across a facade (interior columns)."""
    c.hl(x + 1, x + w - 2, y, f[0])
    c.hl(x + 1, x + w - 2, y + 1, f[2])


def cornice(c, x, y, w, f):
    c.hl(x - 1, x + w, y, INK)
    c.hl(x - 1, x + w, y + 1, f[0])
    c.hl(x - 1, x + w, y + 2, f[2])
    c.hl(x - 1, x + w, y + 3, INK)
    c.vl(x - 1, y, y + 3, INK); c.vl(x + w, y, y + 3, INK)


def rustic(c, x, y, w, h, f):
    for yy in range(y, y + h):
        if (yy - y) % 3 == 2:
            c.hl(x + 1, x + w - 2, yy, f[2])


def plinth(c, x, w, f, top=BASE - 2):
    c.hl(x + 1, x + w - 2, top, f[2])
    c.hl(x + 1, x + w - 2, top + 1, f[3])


def window(c, x, y, w, h, frame, shadow, arch=False, cross=True, sill=True, hood=None, lit=False):
    fr = frame
    c.rect(x - 1, y - 1, w + 2, h + 2, fr)
    glass = CREAM if lit else STEEL[1]
    c.rect(x, y, w, h, glass)
    c.hl(x, x + w - 1, y, NAVY if not lit else SAND[1])
    if not lit:
        c.px(x + 1, y + 2, STEEL[0]); c.px(x + 1, y + 3, STEEL[0]); c.px(x + 2, y + 2, STEEL[0])
        if h > 7:
            c.px(x + w - 2, y + h - 2, STEEL[0])
    if cross and w >= 5:
        c.vl(x + w // 2, y, y + h - 1, fr)
        if h >= 8:
            c.hl(x, x + w - 1, y + h // 3, fr)
    if arch:
        c.clear(x - 1, y - 1); c.clear(x + w, y - 1)
        c.px(x - 1, y - 1, None)
        c.px(x, y, fr); c.px(x + w - 1, y, fr)
    if sill:
        c.hl(x - 2, x + w + 1, y + h + 1, fr)
        c.hl(x - 2, x + w + 1, y + h + 2, shadow)
    if hood:
        c.hl(x - 2, x + w + 1, y - 3, hood[0])
        c.hl(x - 2, x + w + 1, y - 2, hood[1])


def arch_window(c, x, y, w, h, frame, shadow, bg, cross=True, sill=True):
    """round-arched window; bg = facade colour for the cut corners."""
    window(c, x, y, w, h, frame, shadow, cross=cross, sill=sill)
    c.px(x - 1, y - 1, bg); c.px(x + w, y - 1, bg)
    c.px(x, y - 1, bg if w <= 4 else frame); c.px(x + w - 1, y - 1, bg if w <= 4 else frame)
    if w > 4:
        c.px(x - 1, y - 1, bg); c.px(x + w, y - 1, bg)
        c.px(x - 1, y, frame); c.px(x + w, y, frame)
        c.px(x, y - 1, bg); c.px(x + w - 1, y - 1, bg)
        c.hl(x + 1, x + w - 2, y - 2, frame)
        c.px(x, y, frame); c.px(x + w - 1, y, frame)
        c.hl(x + 1, x + w - 2, y - 1, frame)
        c.hl(x + 1, x + w - 2, y, NAVY)


def door(c, x, w, h, leaf, frame, glassrow=True, double=False, knob=GOLD, bottom=BASE):
    y = bottom - h + 1
    c.rect(x - 1, y - 1, w + 2, h + 1, frame)
    c.rect(x, y, w, h, leaf[1])
    c.vl(x, y, bottom, leaf[0])
    c.hl(x, x + w - 1, y, leaf[2])
    if double:
        c.vl(x + w // 2, y + 1, bottom, leaf[2])
    if glassrow and h > 8:
        gy = y + 2
        if double:
            c.rect(x + 1, gy, w // 2 - 2, 4, STEEL[1]); c.rect(x + w // 2 + 1, gy, w - w // 2 - 2, 4, STEEL[1])
            c.px(x + 1, gy, STEEL[0]); c.px(x + w // 2 + 1, gy, STEEL[0])
        else:
            c.rect(x + 1, gy, w - 2, 4, STEEL[1]); c.px(x + 1, gy, STEEL[0])
    if knob:
        kx = x + w // 2 - 1 if double else x + w - 2
        c.px(kx, bottom - h // 2 + 1, knob)
        if double:
            c.px(kx + 2, bottom - h // 2 + 1, knob)
    # step
    c.hl(x - 2, x + w + 1, bottom + 1, WHITE)
    c.hl(x - 2, x + w + 1, bottom + 2, GREY[1])


def roof(c, x, y, w, rh, r, inset=1, seams=None, courses=3, top_inset=None):
    """3/4 view roof sitting on facade top row y (roof rows y-rh..y-1). r=(light, base, dark)."""
    L = C()
    for i in range(rh):
        yy = y - 1 - i
        ins = inset if top_inset is None or i < rh - 3 else top_inset
        x0 = x - 1 + i * inset
        x1 = x + w - i * inset
        if x1 - x0 < 1:
            break
        for xx in range(x0, x1 + 1):
            col = r[1]
            if seams and (xx - x) % seams == 0:
                col = r[0]
            if courses and i % courses == courses - 1:
                col = r[2] if not seams else col
            L.px(xx, yy, col)
        L.px(x0, yy, r[0]); L.px(x1, yy, r[2])
        if i == rh - 1:
            L.hl(x0, x1, yy, r[0])
    L.hl(x - 1, x + w, y - 1, r[2])
    L.outline(INK)
    c.comp(L)


def dormer(c, x, y, r, f):
    """small dormer, bottom row y, 7 wide."""
    L = C()
    L.rect(x, y - 5, 7, 6, f[1])
    L.vl(x, y - 5, y, f[0]); L.vl(x + 6, y - 5, y, f[2])
    L.rect(x + 2, y - 3, 3, 4, STEEL[1]); L.px(x + 2, y - 3, STEEL[0])
    for i in range(4):
        L.hl(x - 1 + i, x + 7 - i, y - 6 - i, r[1] if i < 3 else r[0])
        L.px(x - 1 + i, y - 6 - i, r[0]); L.px(x + 7 - i, y - 6 - i, r[2])
    L.outline(INK)
    c.comp(L)


def chimney(c, x, y, h=6):
    L = C()
    L.rect(x, y - h + 1, 4, h, RRED[0])
    L.vl(x + 3, y - h + 1, y, RRED[1])
    L.hl(x, x + 3, y - h + 1, SAND[1])
    L.outline(INK)
    c.comp(L)


# ---------------------------------------------------------------- props
def tree(c, cx, base, r=9, trunk=6, shadow=True):
    if shadow:
        ground_shadow(c, cx + 1, base + 1, r - 1)
    L = C()
    top = base - trunk
    L.rect(cx - 1, top, 3, trunk + 1, SAND[3])
    L.vl(cx - 1, top, base, SAND[2]); L.vl(cx + 1, top, base, SAND[4])
    L.px(cx - 2, base, SAND[3]); L.px(cx + 2, base, SAND[4])
    cy = top - r + 3
    blobs = [(cx, cy, r), (cx - r * 0.55, cy + r * 0.35, r * 0.62), (cx + r * 0.6, cy + r * 0.3, r * 0.6),
             (cx - r * 0.25, cy - r * 0.45, r * 0.58), (cx + r * 0.3, cy + r * 0.55, r * 0.5)]
    for bx, by, br in blobs:
        for y in range(int(by - br) - 1, int(by + br) + 2):
            for x in range(int(bx - br) - 1, int(bx + br) + 2):
                dx, dy = x + 0.5 - bx, y + 0.5 - by
                if dx * dx + dy * dy <= br * br:
                    t = (-dx * 0.8 - dy) / (br * 1.3)
                    col = GRASS[0] if t > 0.42 else GRASS[1] if t > -0.02 else GRASS[2] if t > -0.5 else GRASS[3]
                    L.px(x, y, col)
    L.outline(INK)
    c.comp(L)


def lamp(c, x, base, h=24):
    ground_shadow(c, x + 1, base + 1, 2)
    L = C()
    L.vl(x, base - h + 4, base, INK2)
    L.hl(x - 1, x + 1, base, INK2); L.hl(x - 1, x + 1, base - 1, CHAR)
    top = base - h
    L.rect(x - 2, top + 1, 5, 3, CREAM)
    L.px(x - 1, top + 2, TRAM[0]); L.px(x, top + 2, WHITE)
    L.hl(x - 2, x + 2, top, INK2); L.hl(x - 1, x + 1, top - 1, INK2)
    L.hl(x - 2, x + 2, top + 4, INK2)
    L.outline(INK)
    c.comp(L)


def bench(c, x, base, w=14):
    ground_shadow(c, x + w // 2 + 1, base + 1, w // 2)
    L = C()
    L.hl(x, x + w - 1, base - 6, SAND[1]); L.hl(x, x + w - 1, base - 5, SAND[2])      # backrest
    L.hl(x, x + w - 1, base - 3, SAND[1]); L.hl(x, x + w - 1, base - 2, SAND[3])      # seat
    for lx in (x + 1, x + w - 2):
        L.vl(lx, base - 7, base, PINE[0])
    L.outline(INK)
    c.comp(L)


def bush(c, x, base, w=10, h=6):
    L = C()
    for y in range(base - h + 1, base + 1):
        for xx in range(x, x + w):
            dx = (xx - x - (w - 1) / 2) / (w / 2)
            dy = (y - base) / h
            if dx * dx + (dy + 0.1) ** 2 * 1.2 <= 1.05:
                t = -dx * 0.6 - (y - (base - h / 2)) / h
                L.px(xx, y, GRASS[1] if t > 0.15 else GRASS[2] if t > -0.35 else GRASS[3])
    L.outline(INK)
    c.comp(L)


def planter(c, x, base, flower=TERRA):
    L = C()
    L.rect(x, base - 3, 6, 4, TERRA); L.vl(x + 5, base - 3, base, RRED[1]); L.hl(x, x + 5, base - 3, RRED[0])
    for i, col in enumerate([GRASS[2], GRASS[1], flower, GRASS[2], flower, GRASS[1]]):
        L.px(x + i, base - 4 - (i % 2), col)
        L.px(x + i, base - 4, GRASS[2] if i % 2 else GRASS[1])
    L.outline(INK)
    c.comp(L)



# ---------------------------------------------------------------- far Dresden silhouettes (atmospheric, no outline)
FAR = (WATER[0], WATER[1])


def _prof_fill(c, cx, ybot, h, pts, col=FAR):
    for i in range(h):
        t = i / max(1, h - 1)
        f = pts[-1][1]
        for (a, fa), (b, fb) in zip(pts, pts[1:]):
            if a <= t <= b:
                f = fa + (fb - fa) * (t - a) / (b - a)
                break
        half = max(0.5, f)
        x0 = int(round(cx - half)); x1 = int(round(cx + half)) - 1
        c.hl(x0, x1, ybot - i, col[0])
        if x1 - x0 >= 3:
            c.px(x1, ybot - i, col[1])


def far_frauenkirche(c, cx, base):
    """Frauenkirche: square body, four corner towers, bell dome, lantern, golden cross."""
    c.rect(cx - 14, base - 14, 28, 15, FAR[0]); c.vl(cx + 13, base - 14, base, FAR[1])
    for tx in (cx - 16, cx + 12):
        c.rect(tx, base - 21, 4, 22, FAR[0]); c.vl(tx + 3, base - 21, base, FAR[1])
        c.hl(tx, tx + 3, base - 22, FAR[0]); c.hl(tx + 1, tx + 2, base - 23, FAR[0]); c.px(tx + 2, base - 23, FAR[1])
        c.vl(tx + 1, base - 25, base - 24, FAR[0])
    c.rect(cx - 8, base - 17, 16, 3, FAR[0])
    _prof_fill(c, cx, base - 17, 16, [(0, 10), (0.25, 9.2), (0.5, 8), (0.7, 6), (0.85, 4), (1.0, 2)])
    c.rect(cx - 2, base - 37, 4, 5, FAR[0]); c.vl(cx + 1, base - 37, base - 33, FAR[1])
    c.px(cx - 1, base - 38, FAR[0]); c.px(cx, base - 38, FAR[0])
    c.vl(cx - 1, base - 42, base - 39, GOLD); c.hl(cx - 2, cx, base - 41, GOLD)


def far_hofkirche_tower(c, cx, base):
    """slim tiered baroque tower of the Hofkirche."""
    c.rect(cx - 5, base - 16, 10, 17, FAR[0]); c.vl(cx + 4, base - 16, base, FAR[1])
    c.rect(cx - 4, base - 26, 8, 10, FAR[0]); c.vl(cx + 3, base - 26, base - 16, FAR[1])
    c.rect(cx - 3, base - 33, 6, 7, FAR[0]); c.vl(cx + 2, base - 33, base - 26, FAR[1])
    c.rect(cx - 2, base - 38, 4, 5, FAR[0]); c.vl(cx + 1, base - 38, base - 33, FAR[1])
    for k, (w_, y_) in enumerate(((10, 16), (8, 26), (6, 33))):
        c.hl(cx - w_ // 2 - 1, cx + w_ // 2, base - y_, FAR[1])
    c.vl(cx - 1, base - 43, base - 39, FAR[0]); c.vl(cx, base - 43, base - 39, FAR[1])
    c.px(cx - 1, base - 44, GOLD)


def far_tv_tower(c, cx, base, h=52):
    """Fernsehturm on its hill: slim shaft, cabin near the top, red/white antenna."""
    c.vl(cx, base - h + 12, base, FAR[0]); c.vl(cx + 1, base - h + 12, base, FAR[1])
    c.rect(cx - 2, base - h + 8, 6, 4, FAR[0]); c.vl(cx + 3, base - h + 8, base - h + 11, FAR[1])
    c.vl(cx, base - h + 1, base - h + 7, FAR[0])
    c.px(cx, base - h, APO); c.px(cx, base - h + 2, APO); c.px(cx, base - h + 1, WHITE)


# ---------------------------------------------------------------- scenes
def scene_services():
    c = C()
    far_frauenkirche(c, 268, 54)
    pavement(c, 2, 317)
    # --- Apotheke: Gruenderzeit corner house
    ax, aw, ay = 14, 82, 26
    roof(c, ax, ay, aw, 10, R_RED, inset=1)
    dormer(c, ax + 18, ay - 2, R_RED, F_CREAM); dormer(c, ax + 56, ay - 2, R_RED, F_CREAM)
    chimney(c, ax + 38, ay - 9, 5)
    facade(c, ax, ay, aw, BASE - ay + 1, F_CREAM)
    band(c, ax, 42, aw, F_CREAM)
    band(c, ax, 57, aw, F_CREAM)
    rustic(c, ax, 59, aw, 20, F_CREAM)
    for fy in (31, 46):
        for i in range(5):
            if fy == 46 and i == 3:
                continue
            window(c, ax + 7 + i * 15, fy, 6, 8, WHITE, SAND[2], hood=(WHITE, SAND[2]))
    # shop window with shelves of bottles
    sx, sy, sw, sh = ax + 6, 63, 34, 15
    c.rect(sx - 1, sy - 1, sw + 2, sh + 2, PINE[0])
    c.rect(sx, sy, sw, sh, CREAM)
    for shelf in (sy + 4, sy + 9):
        c.hl(sx, sx + sw - 1, shelf, SAND[2])
        for k in range(2, sw - 1, 3):
            col = [WHITE, STEEL[0], TERRA, SAGE, GOLD][(k // 3 + shelf) % 5]
            c.vl(sx + k, shelf - 3, shelf - 1, col)
            c.px(sx + k, shelf - 3, INK2 if col == WHITE else col)
    c.hl(sx, sx + sw - 1, sy + sh - 1, SAND[1])
    c.vl(sx + sw // 2, sy, sy + sh - 1, PINE[0])
    c.px(sx + 1, sy + 1, WHITE); c.px(sx + sw // 2 + 2, sy + 1, WHITE)
    door(c, ax + 50, 10, 18, (COP[1], PINE[0], PINE[1]), PINE[1])
    window(c, ax + 67, 64, 8, 10, PINE[0], SAND[2], cross=True)
    # red A sign on a bracket, sticks out at the corner above the door
    kx = ax + 45
    c.hl(kx - 1, kx + 13, 58, INK2)
    L = C()
    L.rect(kx + 2, 49, 11, 12, APO)
    L.vl(kx + 2, 49, 60, "#C9704F"); L.vl(kx + 12, 49, 60, RRED[1]); L.hl(kx + 2, kx + 12, 60, RRED[1])
    Apix = ["..#..", ".#.#.", ".#.#.", "#####", "#...#", "#...#"]
    for j, row in enumerate(Apix):
        for i, ch in enumerate(row):
            if ch == "#":
                L.px(kx + 5 + i, 51 + j, WHITE)
    L.outline(INK)
    c.comp(L)
    plinth(c, ax, aw, F_CREAM)
    # --- tree between
    tree(c, 104, 84, r=9, trunk=7)
    # --- Buergeramt: calm official building, clock in the pediment, copper roof
    bx, bw, by = 114, 98, 30
    roof(c, bx, by, bw, 9, R_COP, inset=1, seams=4)
    # central risalit with pediment
    rx, rw = bx + 33, 32
    facade(c, bx, by, bw, BASE - by + 1, F_SAND)
    cornice(c, bx, by, bw, F_SAND)
    # pediment triangle
    L = C()
    ph = 12
    for i in range(ph):
        y = by - 1 - i
        x0 = rx - 1 + int(i * 1.45); x1 = rx + rw - int(i * 1.45)
        if x1 < x0:
            break
        L.hl(x0, x1, y, SAND[1])
        L.px(x0, y, SAND[0]); L.px(x1, y, SAND[2])
    L.outline(INK)
    c.comp(L)
    # clock
    ccx, ccy = rx + rw // 2, by - 5
    L = C()
    for y in range(ccy - 4, ccy + 5):
        for x in range(ccx - 4, ccx + 5):
            d = (x - ccx) ** 2 + (y - ccy) ** 2
            if d <= 16:
                L.px(x, y, WHITE if d <= 9 else GOLD)
    L.px(ccx, ccy, INK); L.vl(ccx, ccy - 3, ccy, INK); L.hl(ccx, ccx + 2, ccy, INK)
    L.px(ccx - 2, ccy - 2, CREAM)
    c.comp(L)
    band(c, bx, 55, bw, F_SAND)
    rustic(c, bx, 57, bw, 22, F_SAND)
    c.box(rx, by + 3, rw, BASE - by - 2, SAND[1])
    c.vl(rx + 1, by + 4, BASE - 1, SAND[0]); c.vl(rx + rw - 2, by + 4, BASE - 1, SAND[2])
    band(c, rx, 55, rw, F_SAND)
    rustic(c, rx, 57, rw, 22, F_SAND)
    for i in range(3):
        for wx in (bx + 5 + i * 9, rx + rw + 3 + i * 9):
            window(c, wx, 38, 5, 11, WHITE, SAND[3], hood=(SAND[0], SAND[3]))
            arch_window(c, wx, 63, 5, 10, WHITE, SAND[3], SAND[1])
    # central: pilasters, tall windows, door with steps
    for px_ in (rx + 3, rx + rw - 4):
        c.vl(px_, by + 5, 54, SAND[0]); c.vl(px_ + 1, by + 5, 54, SAND[2])
    window(c, rx + 8, 37, 5, 12, WHITE, SAND[3], hood=(SAND[0], SAND[3]))
    window(c, rx + 19, 37, 5, 12, WHITE, SAND[3], hood=(SAND[0], SAND[3]))
    door(c, rx + 10, 12, 19, (STEEL[0], NAVY, INK2), SAND[3], double=True)
    c.hl(rx + 7, rx + 24, 60, SAND[0]); c.hl(rx + 7, rx + 24, 61, SAND[3])
    plinth(c, bx, bw, F_SAND)
    c.rect(rx + 8, BASE - 1, 16, 2, SAND[3])
    door(c, rx + 10, 12, 19, (STEEL[0], NAVY, INK2), SAND[3], double=True)
    # --- tree
    tree(c, 219, 84, r=8, trunk=6)
    # --- Kita: low colourful building, sun sign, fence and slide
    kx0, kw, ky = 229, 62, 54
    facade(c, kx0, ky, kw, BASE - ky + 1, F_CREAM, eave=False)
    # flat roof edge
    c.box(kx0 - 2, ky - 3, kw + 4, 4, TEAL)
    c.hl(kx0 - 1, kx0 + kw, ky - 2, COP[1]); c.hl(kx0 - 1, kx0 + kw, ky - 1, PINE[0])
    c.hl(kx0 + 1, kx0 + kw - 2, ky + 1, SAND[2])
    panels = [MUST, TERRA, TEAL, SAGE, MUST]
    for i, col in enumerate(panels):
        px0 = kx0 + 2 + i * 12
        c.rect(px0, ky + 3, 4, BASE - ky - 4, col)
        c.vl(px0 + 3, ky + 3, BASE - 2, INK2 if col in (TEAL,) else SAND[3])
        c.vl(px0, ky + 3, BASE - 2, WHITE if col in (MUST, SAGE) else CREAM)
    for i in range(4):
        wx = kx0 + 8 + i * 12
        if i == 1:
            continue
        window(c, wx, ky + 9, 6, 11, WHITE, SAND[2], cross=True)
    door(c, kx0 + 20, 6, 15, (TRAM[0], MUST, TRAM[1]), WHITE, glassrow=True, knob=INK2)
    # sun sign on the roof edge
    sx0, sy0 = kx0 + 21, ky - 9
    L = C()
    for y in range(sy0 - 5, sy0 + 6):
        for x in range(sx0 - 5, sx0 + 6):
            d = (x - sx0) ** 2 + (y - sy0) ** 2
            if d <= 7:
                L.px(x, y, TRAM[0] if (x - sx0) + (y - sy0) < 1 else TRAM[1])
    for dx, dy in ((0, -5), (0, 5), (-5, 0), (5, 0), (-4, -4), (4, -4), (-4, 4), (4, 4)):
        L.px(sx0 + dx, sy0 + dy, GOLD)
        L.px(sx0 + (dx * 4) // 5, sy0 + (dy * 4) // 5, GOLD)
    L.outline(INK)
    c.comp(L)
    c.vl(sx0, sy0 + 6, ky - 4, INK2)
    plinth(c, kx0, kw, F_CREAM)
    # slide in the yard
    yx = 296
    # ladder: two rails + rungs, platform with a little roof
    c.vl(yx, 58, BASE, INK); c.vl(yx + 5, 58, BASE, INK)
    for yy in range(61, BASE, 4):
        c.hl(yx + 1, yx + 4, yy, GREY[2])
    c.box(yx - 1, 57, 8, 3, TERRA)
    c.hl(yx, yx + 5, 58, RRED[0])
    for i in range(3):
        c.hl(yx + i, yx + 5 - i, 51 + i + 2, TERRA if i < 2 else RRED[1])
    c.hl(yx + 1, yx + 4, 52, INK); c.px(yx - 1, 55, INK); c.px(yx + 6, 55, INK)
    c.px(yx, 54, INK); c.px(yx + 5, 54, INK)
    c.vl(yx, 55, 57, INK); c.vl(yx + 5, 55, 57, INK)
    # chute
    for i in range(16):
        sx_ = yx + 7 + (i * 3) // 4
        c.px(sx_, 58 + i, TRAM[0]); c.px(sx_ + 1, 58 + i, TRAM[0])
        c.px(sx_, 59 + i, TRAM[1]); c.px(sx_ + 1, 59 + i, TRAM[1])
        c.px(sx_, 57 + i, INK); c.px(sx_ + 2, 58 + i, INK); c.px(sx_, 60 + i, INK) if i == 15 else None
    # low picket fence in front of the yard
    for fx in range(293, 317, 3):
        c.vl(fx, 73, 82, WHITE); c.vl(fx + 1, 73, 82, GREY[0])
        c.px(fx, 72, INK); c.px(fx + 1, 72, INK); c.px(fx - 1, 73, INK)
        c.vl(fx + 2, 73, 82, INK) if fx + 2 < 317 else None
    c.hl(293, 316, 76, WHITE); c.hl(293, 316, 79, WHITE)
    c.hl(293, 316, 77, GREY[1]); c.hl(293, 316, 80, GREY[1])
    c.hl(293, 316, 83, GREY[1])
    bush(c, 226, 84, 7, 5)
    stops = [ax + 55, rx + 16, kx0 + 23]
    return c, dict(focusX=rx + 16, lanes=[dict(y=FEET, x0=8, x1=312, stops=stops)], walkers=2)


def scene_courses():
    c = C()
    far_hofkirche_tower(c, 150, 70)
    pavement(c, 2, 317)
    # --- music school: tall Gruenderzeit house with a gable
    mx, mw, my = 12, 108, 24
    roof(c, mx, my, mw, 11, R_SLATE, inset=1, courses=3)
    # central gable (Zwerchhaus)
    gx, gw = mx + 38, 32
    L = C()
    for i in range(16):
        y = my - 1 - i
        x0 = gx + i; x1 = gx + gw - 1 - i
        if x1 < x0:
            break
        L.hl(x0, x1, y, F_ROSE[1]); L.px(x0, y, F_ROSE[0]); L.px(x1, y, F_ROSE[2])
    L.outline(INK)
    c.comp(L)
    window(c, gx + 13, my - 9, 6, 7, WHITE, RRED[1], cross=True, sill=True)
    dormer(c, mx + 12, my - 2, R_SLATE, F_ROSE); dormer(c, mx + 88, my - 2, R_SLATE, F_ROSE)
    facade(c, mx, my, mw, BASE - my + 1, F_ROSE)
    band(c, mx, 39, mw, F_ROSE)
    band(c, mx, 53, mw, F_ROSE)
    for fy in (29, 43):
        for i in range(6):
            if fy == 43 and i == 4:
                continue
            window(c, mx + 7 + i * 17, fy, 6, 8, WHITE, RRED[1], hood=(SAND[0], RRED[1]))
    rustic(c, mx, 56, mw, 23, (SAND[0], SAND[1], SAND[2], SAND[3]))
    c.rect(mx + 1, 56, mw - 2, BASE - 57, SAND[1])
    c.vl(mx + 1, 56, BASE - 1, SAND[0]); c.vl(mx + mw - 2, 56, BASE - 1, SAND[2])
    rustic(c, mx, 56, mw, 23, F_SAND)
    c.hl(mx + 1, mx + mw - 2, 56, SAND[0])
    # studio window with a grand piano
    sx, sy, sw, sh = mx + 8, 60, 44, 18
    c.rect(sx - 2, sy - 2, sw + 4, sh + 3, WHITE)
    c.rect(sx, sy, sw, sh, CREAM)
    c.hl(sx, sx + sw - 1, sy, SAND[1]); c.hl(sx, sx + sw - 1, sy + 1, SAND[0])
    c.hl(sx, sx + sw - 1, sy + sh - 1, SAND[2])
    for k in range(1, 4):
        c.vl(sx + k * sw // 4, sy, sy + sh - 1, WHITE)
    c.hl(sx, sx + sw - 1, sy + 5, WHITE)
    # piano (side view, lid open)
    P = C()
    pxl, pyl = sx + 9, sy + 8
    P.rect(pxl, pyl, 22, 4, INK)                 # case
    P.hl(pxl, pxl + 21, pyl, INK2)
    for i in range(7):
        P.hl(pxl + 8 + i, pxl + 21, pyl - 1 - i, INK if i < 6 else INK2)   # open lid
    P.vl(pxl + 8, pyl - 7, pyl, INK2)
    P.hl(pxl, pxl + 7, pyl + 1, WHITE); P.hl(pxl, pxl + 7, pyl + 2, INK2)   # keys
    for kx in range(pxl + 1, pxl + 7, 2):
        P.px(kx, pyl + 1, INK)
    P.vl(pxl + 1, pyl + 4, pyl + 8, INK); P.vl(pxl + 20, pyl + 4, pyl + 8, INK)
    P.rect(pxl - 5, pyl + 3, 4, 2, INK2); P.vl(pxl - 4, pyl + 5, pyl + 8, INK2)   # stool
    c.comp(P)
    c.hl(sx, sx + sw - 1, sy + sh - 1, SAND[2])
    # door + note sign
    door(c, mx + 62, 10, 19, (RRED[0], RRED[1], SAND[4]), SAND[3])
    window(c, mx + 82, 62, 8, 11, WHITE, SAND[3])
    window(c, mx + 97, 62, 6, 11, WHITE, SAND[3])
    nx = mx + 74
    c.hl(nx, nx + 4, 55, INK2)
    L = C()
    L.rect(nx + 3, 48, 10, 11, GOLD)
    L.vl(nx + 3, 48, 58, TRAM[0]); L.vl(nx + 12, 48, 58, TRAM[1]); L.hl(nx + 3, nx + 12, 58, TRAM[1])
    note = ["..##", "..#.#", "..#..", "..#..", ".##..", "###..", ".#..."]
    for j, row in enumerate(note):
        for i, ch in enumerate(row):
            if ch == "#":
                L.px(nx + 5 + i, 49 + j, INK)
    L.outline(INK)
    c.comp(L)
    plinth(c, mx, mw, F_SAND)
    # --- tree + bench
    tree(c, 136, 84, r=10, trunk=8)
    bench(c, 145, 86, 14)
    # --- small sports hall
    hx0, hw, hy = 170, 132, 46
    # shallow barrel roof
    L = C()
    for i in range(6):
        ins = [0, 0, 1, 3, 6, 11][i]
        y = hy - 1 - i
        L.hl(hx0 - 1 + ins, hx0 + hw - ins, y, R_GREY[1] if i < 4 else R_GREY[0])
        L.px(hx0 - 1 + ins, y, R_GREY[0]); L.px(hx0 + hw - ins, y, R_GREY[2])
    for sx_ in range(hx0 + 4, hx0 + hw - 3, 6):
        for i in range(4):
            L.px(sx_, hy - 1 - i, R_GREY[0])
    L.hl(hx0 - 1, hx0 + hw, hy - 1, R_GREY[2])
    L.outline(INK)
    c.comp(L)
    facade(c, hx0, hy, hw, BASE - hy + 1, F_GREY)
    # clerestory window band
    c.rect(hx0 + 4, hy + 5, hw - 8, 8, STEEL[1])
    c.hl(hx0 + 4, hx0 + hw - 5, hy + 5, NAVY)
    for k in range(hx0 + 4, hx0 + hw - 4, 8):
        c.vl(k, hy + 5, hy + 12, WHITE)
        c.px(k + 2, hy + 7, STEEL[0]); c.px(k + 3, hy + 7, STEEL[0]); c.px(k + 2, hy + 8, STEEL[0])
    c.hl(hx0 + 3, hx0 + hw - 4, hy + 13, WHITE); c.hl(hx0 + 3, hx0 + hw - 4, hy + 14, GREY[1])
    # lower wall: terracotta brick band
    c.rect(hx0 + 1, hy + 16, hw - 2, BASE - hy - 16, TERRA)
    for yy in range(hy + 16, BASE, 3):
        c.hl(hx0 + 1, hx0 + hw - 2, yy, RRED[1] if yy != hy + 16 else RRED[0])
    c.vl(hx0 + 1, hy + 16, BASE - 1, RRED[0]); c.vl(hx0 + hw - 2, hy + 16, BASE - 1, RRED[1])
    # entrance with canopy
    ex = hx0 + 44
    door(c, ex, 14, 17, (STEEL[0], STEEL[1], NAVY), WHITE, double=True, knob=WHITE)
    c.box(ex - 5, 61, 24, 3, WHITE)
    c.hl(ex - 4, ex + 17, 62, GREY[0])
    # ball sign
    L = C()
    bcx, bcy = hx0 + 100, hy + 22
    L.rect(bcx - 7, bcy - 7, 15, 15, WHITE)
    L.hl(bcx - 7, bcx + 7, bcy + 7, GREY[1]); L.vl(bcx + 7, bcy - 7, bcy + 7, GREY[1])
    for y in range(bcy - 5, bcy + 6):
        for x in range(bcx - 5, bcx + 6):
            d = (x - bcx) ** 2 + (y - bcy) ** 2
            if d <= 26:
                L.px(x, y, TRAM[0] if (x - bcx) + (y - bcy) < -3 else MUST if (x - bcx) + (y - bcy) < 4 else TRAM[1])
            if 26 < d <= 38:
                L.px(x, y, INK)
    for k in range(-5, 6):
        L.px(bcx, bcy + k, INK); L.px(bcx + k, bcy, INK)
    for k in (-2, -1, 0, 1, 2):
        L.px(bcx - 3 - (1 if abs(k) < 2 else 0), bcy + k, INK); L.px(bcx + 3 + (1 if abs(k) < 2 else 0), bcy + k, INK)
    L.outline(INK)
    c.comp(L)
    window(c, hx0 + 10, 66, 10, 9, WHITE, GREY[2])
    window(c, hx0 + 72, 66, 10, 9, WHITE, GREY[2])
    plinth(c, hx0, hw, F_GREY)
    bush(c, hx0 + 22, 84, 12, 6)
    bush(c, hx0 + 116, 84, 12, 6)
    lamp(c, 162, 86)
    stops = [mx + 67, 152, ex + 7]
    return c, dict(focusX=mx + 68, lanes=[dict(y=FEET, x0=8, x1=312, stops=stops)], walkers=2)


def onion(L, cx, ybot, w, h, r=R_COP):
    """baroque onion dome: short neck, big bulb, pointed tip. Shaded from the top-left, with ribs."""
    pts = [(0.0, 0.62), (0.08, 0.74), (0.22, 0.98), (0.36, 1.0), (0.5, 0.86), (0.64, 0.56), (0.76, 0.3), (0.88, 0.16), (1.0, 0.08)]
    def prof(t):
        for (a, fa), (b, fb) in zip(pts, pts[1:]):
            if a <= t <= b:
                return fa + (fb - fa) * (t - a) / (b - a)
        return 0.08
    for i in range(h):
        y = ybot - i
        t = i / (h - 1)
        half = max(0.5, w / 2 * prof(t))
        x0 = int(round(cx - half)); x1 = int(round(cx + half)) - 1
        for x in range(x0, x1 + 1):
            u = (x + 0.5 - cx) / max(half, 1)
            s_ = -u + (t - 0.45) * 0.6
            col = r[0] if s_ > 0.45 else r[1] if s_ > -0.3 else r[2]
            if abs(u) < 0.08 and 0.12 < t < 0.8:
                col = r[0] if col != r[0] else r[1]
            if abs(abs(u) - 0.55) < 0.12 and 0.1 < t < 0.7 and x1 - x0 > 8:
                col = r[2] if u > 0 else r[1]
            L.px(x, y, col)
    # neck ring (gold band)
    L.hl(int(cx - w * 0.31), int(cx + w * 0.31) - 1, ybot, GOLD)
    L.hl(int(cx - w * 0.31), int(cx + w * 0.31) - 1, ybot - 1, TRAM[1])


def scene_events():
    import math
    c = C()
    pavement(c, 2, 317)
    # --- Zwinger galleries (arcaded wings, copper mansard roofs, balustrade)
    def wing(x, w):
        wy = 56
        roof(c, x, wy - 3, w, 7, R_COP, inset=1, seams=4)
        facade(c, x, wy, w, BASE - wy + 1, F_SAND, eave=False)
        # balustrade on top
        c.hl(x - 1, x + w, wy - 3, INK)
        c.hl(x - 1, x + w, wy - 2, SAND[0]); c.hl(x - 1, x + w, wy - 1, SAND[2])
        for k in range(x + 2, x + w - 1, 8):   # vases / statues on the balustrade
            c.vl(k, wy - 7, wy - 4, SAND[0]); c.vl(k + 1, wy - 7, wy - 4, SAND[2]); c.px(k, wy - 8, INK); c.px(k + 1, wy - 8, INK)
            c.px(k - 1, wy - 7, INK); c.px(k + 2, wy - 7, INK); c.px(k - 1, wy - 5, INK); c.px(k + 2, wy - 5, INK)
            c.hl(k - 1, k + 2, wy - 4, INK); c.hl(k, k + 1, wy - 4, SAND[1])
        for k in range(x + 4, x + w - 8, 10):
            arch_window(c, k + 1, wy + 7, 6, 16, WHITE, SAND[3], SAND[1])
            c.vl(k - 1, wy + 2, BASE - 3, SAND[0]); c.vl(k, wy + 2, BASE - 3, SAND[2])  # pilasters
        plinth(c, x, w, F_SAND)
    wing(6, 64)
    wing(126, 60)
    # --- Kronentor
    gx, gw = 70, 56
    cx = gx + gw // 2
    gy = 47
    L = C()
    # lower storey
    L.rect(gx, gy, gw, BASE - gy + 1, SAND[1])
    c.comp(L)
    facade(c, gx, gy, gw, BASE - gy + 1, F_SAND, eave=False)
    for px_ in (gx + 5, gx + 13, gx + gw - 15, gx + gw - 7):   # paired columns
        c.vl(px_, gy + 4, BASE - 3, SAND[0]); c.vl(px_ + 1, gy + 4, BASE - 3, SAND[1]); c.vl(px_ + 2, gy + 4, BASE - 3, SAND[3])
    # gate arch passage
    aw_, ah = 16, 26
    ax0 = cx - aw_ // 2
    for y in range(BASE - ah + 1, BASE + 1):
        for x in range(ax0, ax0 + aw_):
            dy = y - (BASE - ah + 1 + aw_ // 2)
            dx = x + 0.5 - cx
            if dy >= 0 or dx * dx + dy * dy <= (aw_ / 2) ** 2:
                c.px(x, y, INK2 if y < BASE - 6 else CHAR)
    # view through the arch: courtyard green + fountain hint
    c.rect(ax0 + 1, BASE - 8, aw_ - 2, 6, GRASS[2])
    c.hl(ax0 + 1, ax0 + aw_ - 2, BASE - 8, GRASS[1])
    c.rect(ax0 + 1, BASE - 2, aw_ - 2, 2, GREY[0])
    # arch voussoir ring
    for a in range(0, 181, 6):
        x = cx + (aw_ / 2 + 0.5) * math.cos(math.radians(a)) - 0.5
        y = BASE - ah + 1 + aw_ // 2 - (aw_ / 2 + 0.5) * math.sin(math.radians(a))
        c.px(round(x), round(y), SAND[0] if a > 90 else SAND[3])
    c.px(cx - 1, BASE - ah - 1, GOLD); c.px(cx, BASE - ah - 1, GOLD)       # keystone
    cornice(c, gx, gy - 2, gw, F_SAND)
    # upper storey (narrower pavilion with open arch)
    ux, uw, uy = gx + 11, gw - 22, 31
    facade(c, ux, uy, uw, gy - uy - 2, F_SAND, eave=False)
    for px_ in (ux + 3, ux + uw - 6):
        c.vl(px_, uy + 3, gy - 4, SAND[0]); c.vl(px_ + 1, uy + 3, gy - 4, SAND[1]); c.vl(px_ + 2, uy + 3, gy - 4, SAND[3])
    for y in range(uy + 3, gy - 3):
        for x in range(cx - 5, cx + 5):
            dy = y - (uy + 8)
            dx = x + 0.5 - cx
            if dy >= 0 or dx * dx + dy * dy <= 25:
                c.px(x, y, INK2)
    c.hl(cx - 4, cx + 3, gy - 4, SAND[3])
    # scrolls (volutes) left and right of the upper storey
    for vx in (gx + 1, gx + gw - 3):      # vases on the lower cornice corners
        c.rect(vx, gy - 7, 2, 4, SAND[0]); c.vl(vx + 1, gy - 7, gy - 4, SAND[2])
        c.hl(vx, vx + 1, gy - 8, INK); c.vl(vx - 1, gy - 7, gy - 4, INK); c.vl(vx + 2, gy - 7, gy - 4, INK)
        c.hl(vx - 1, vx + 2, gy - 3, INK)
    cornice(c, ux, uy - 3, uw, F_SAND)
    # onion dome
    L = C()
    onion(L, cx, uy - 4, 26, 17)
    L.outline(INK)
    c.comp(L)
    # golden crown on the tip
    L = C()
    cy0 = uy - 21
    crown = ["....G....", "...GYG...", "....G....", "G...G...G", "GG.GYG.GG", "GYGGGGGYG", "YRYSYRYSY", "DDDDDDDDD"]
    cmap = {"G": GOLD, "Y": TRAM[0], "D": TRAM[1], "R": APO, "S": STEEL[0]}
    for j, row in enumerate(crown):
        for i, ch in enumerate(row):
            if ch in cmap:
                L.px(cx - 4 + i, cy0 - 7 + j, cmap[ch])
    L.outline(INK)
    c.comp(L)
    plinth(c, gx, gw, F_SAND)
    c.rect(ax0, BASE - 1, aw_, 2, GREY[0])
    # --- Elbe meadows: river, grass bank, market stall
    mx0, mx1 = 192, 316
    for y in range(58, 82):
        for x in range(mx0, mx1 + 1):
            e = min(x - mx0, mx1 - x)
            if y < 58 + max(0, 4 - e):
                continue
            if y < 63:
                col = WATER[1]
                if y == 58:
                    col = WATER[2]
                if y in (60, 62) and (x + y * 5) % 14 < 3:
                    col = WATER[0]
            elif y == 63:
                col = GRASS[2]
            else:
                col = GRASS[1]
                if y == 64:
                    col = GRASS[0]
                tx, ty = (x + (y // 6) * 5) % 11, y % 6
                if ty == 3 and tx in (0, 2):
                    col = GRASS[2]
                if ty == 2 and tx == 1:
                    col = GRASS[2]
            c.px(x, y, col)
    # far bank: Neustadt meadow line
    for x in range(mx0 + 5, mx1 - 4):
        c.px(x, 57, GRASS[2]); c.px(x, 56, GRASS[1]); c.px(x, 55, INK)
    c.hl(mx0, mx1, 81, GRASS[3])
    # market stall
    L = C()
    stx, stw = 228, 40
    for pxx in (stx + 1, stx + stw - 2):
        L.vl(pxx, 58, 83, SAND[3])
    # awning: stripes terracotta / cream, 3/4 view slope
    for i in range(7):
        y = 52 + i
        for x in range(stx - 2 + (6 - i) // 3, stx + stw + 2 - (6 - i) // 3):
            L.px(x, y, TERRA if ((x - stx) // 4) % 2 == 0 else CREAM)
        L.px(stx - 2 + (6 - i) // 3, y, RRED[0] if ((0) // 4) % 2 == 0 else WHITE)
    for x in range(stx - 2, stx + stw + 2):     # scalloped edge
        col = RRED[1] if ((x - stx) // 4) % 2 == 0 else SAND[1]
        L.px(x, 59, col)
        if (x - stx) % 4 in (1, 2):
            L.px(x, 60, col)
    # counter with goods
    L.rect(stx, 71, stw, 12, SAND[2])
    L.hl(stx, stx + stw - 1, 71, SAND[1]); L.hl(stx, stx + stw - 1, 72, SAND[1])
    for x in range(stx, stx + stw):
        if x % 5 == 0:
            L.vl(x, 73, 82, SAND[3])
    L.hl(stx, stx + stw - 1, 82, SAND[3])
    goods = [(TERRA, RRED[1]), (TRAM[0], TRAM[1]), (GRASS[1], GRASS[2]), (RRED[0], RRED[1]), (MUST, SAND[3]), (GRASS[0], GRASS[2])]
    for i in range(6):
        gx0 = stx + 2 + i * 6
        a, b = goods[i]
        L.rect(gx0, 68, 5, 3, SAND[3])
        L.hl(gx0 + 1, gx0 + 3, 67, a); L.hl(gx0, gx0 + 4, 68, a); L.px(gx0 + 3, 68, b); L.px(gx0 + 1, 67, WHITE if i % 2 else a)
    L.outline(INK)
    c.comp(L)
    tree(c, 304, 82, r=9, trunk=7)
    tree(c, 208, 80, r=7, trunk=5, shadow=False)
    lamp(c, 186, 86)
    stops = [cx, stx + stw // 2]
    return c, dict(focusX=cx, lanes=[dict(y=FEET, x0=8, x1=312, stops=stops)], walkers=2)


def scene_communities():
    c = C()
    far_tv_tower(c, 262, 70, 54)
    pavement(c, 2, 317)
    # --- Hof der Elemente: blue facade with funnel drain pipes
    bx, bw, by = 10, 104, 14
    roof(c, bx, by, bw, 9, R_SLATE, inset=1)
    dormer(c, bx + 20, by - 1, R_SLATE, F_BLUE); dormer(c, bx + 72, by - 1, R_SLATE, F_BLUE)
    facade(c, bx, by, bw, BASE - by + 1, F_BLUE)
    for fy in (22, 38, 54):
        for i in range(5):
            wx = bx + 6 + i * 20
            c.rect(wx - 1, fy - 1, 9, 11, NAVY)
            c.rect(wx, fy, 7, 9, STEEL[1] if (i + fy) % 3 else CREAM)
            c.vl(wx + 3, fy, fy + 8, NAVY)
            c.px(wx + 1, fy + 1, WATER[0]); c.px(wx + 1, fy + 2, STEEL[0])
            c.hl(wx - 2, wx + 8, fy + 10, WATER[0]); c.hl(wx - 2, wx + 8, fy + 11, NAVY)
    # the pipes (gold) with funnels
    def pipe_v(x, y0, y1):
        c.vl(x, y0, y1, GOLD); c.vl(x + 1, y0, y1, TRAM[1])
        for yy in range(y0 + 3, y1, 7):
            c.hl(x - 1, x + 2, yy, TRAM[1])

    def funnel(x, y):
        # trumpet-shaped bowl opening upwards, 7 wide at top
        rows = [(-3, 4), (-2, 3), (-1, 2), (0, 1)]
        for j, (a, b) in enumerate(rows):
            c.hl(x + a, x + b, y + j, GOLD)
            c.px(x + a, y + j, TRAM[0]); c.px(x + b, y + j, TRAM[1])
        c.hl(x - 3, x + 4, y - 1, INK); c.px(x - 4, y, INK); c.px(x + 5, y, INK)
        c.hl(x - 2, x + 3, y, INK2)
    for (px_, top, bot, fun) in ((bx + 16, by + 3, 62, [36, 52]), (bx + 56, by + 3, 78, [30, 50, 66]), (bx + 95, by + 3, 70, [44])):
        pipe_v(px_, top, bot)
        for fy in fun:
            funnel(px_, fy)
    # zig-zag connectors
    for i in range(10):
        c.px(bx + 17 + i * 2, 62 + i, GOLD); c.px(bx + 18 + i * 2, 62 + i, TRAM[1])
    for i in range(8):
        c.px(bx + 94 - i * 2, 70 + i, GOLD); c.px(bx + 95 - i * 2, 70 + i, TRAM[1])
    # passage arch (entrance to the courtyards)
    ax0 = bx + 34
    for y in range(64, BASE + 1):
        for x in range(ax0, ax0 + 14):
            dy = y - 71; dx = x + 0.5 - (ax0 + 7)
            if dy >= 0 or dx * dx + dy * dy <= 49:
                c.px(x, y, INK2)
    c.rect(ax0 + 1, BASE - 5, 12, 6, CHAR)
    c.px(ax0 + 6, 73, TRAM[0]); c.px(ax0 + 7, 73, TRAM[0])
    plinth(c, bx, bw, F_BLUE)
    # --- Hof der Tiere: yellow facade with teal windows
    yx, yw, yy = 116, 92, 20
    roof(c, yx, yy, yw, 9, R_RED, inset=1)
    dormer(c, yx + 40, yy - 1, R_RED, F_YEL)
    chimney(c, yx + 12, yy - 7, 5)
    facade(c, yx, yy, yw, BASE - yy + 1, F_YEL)
    for fy in (28, 44):
        for i in range(4):
            wx = yx + 8 + i * 22
            c.rect(wx - 3, fy - 1, 2, 12, TEAL); c.rect(wx + 8, fy - 1, 2, 12, TEAL)   # shutters
            c.vl(wx - 3, fy - 1, fy + 10, COP[1]); c.vl(wx + 9, fy - 1, fy + 10, PINE[0])
            window(c, wx, fy, 6, 10, WHITE, TRAM[1], cross=True, sill=True)
    # little giraffe relief symbols (light shapes) between windows
    band(c, yx, 57, yw, F_YEL)
    # shop / cafe front on the ground floor
    c.rect(yx + 36, 62, 22, 14, STEEL[1]); c.rect(yx + 35, 61, 24, 1, TEAL)
    c.hl(yx + 36, yx + 57, 62, NAVY)
    c.vl(yx + 47, 62, 75, TEAL)
    c.px(yx + 37, 64, STEEL[0]); c.px(yx + 38, 64, STEEL[0]); c.px(yx + 37, 65, STEEL[0])
    # awning
    L = C()
    for i in range(4):
        for x in range(yx + 33 + i, yx + 61 - i):
            L.px(x, 57 + i, SAGE if ((x - yx) // 3) % 2 == 0 else CREAM)
    L.outline(INK)
    c.comp(L)
    door(c, yx + 12, 9, 17, (COP[1], TEAL, PINE[0]), TRAM[1])
    door(c, yx + 70, 9, 17, (COP[1], TEAL, PINE[0]), TRAM[1])
    plinth(c, yx, yw, F_YEL)
    # --- cafe tables with parasols
    def table(x, base, cloth):
        # parasol
        L = C()
        for i in range(4):
            L.hl(x - 8 + i * 2, x + 8 - i * 2, base - 24 - i, cloth[0] if i < 3 else cloth[0])
        L.hl(x - 9, x + 9, base - 23, cloth[1])
        for k in range(x - 8, x + 9, 4):
            L.px(k, base - 22, cloth[1])
        L.px(x - 5, base - 25, WHITE); L.px(x - 4, base - 26, WHITE)
        L.vl(x, base - 22, base - 7, INK2)
        # table
        L.hl(x - 5, x + 5, base - 7, WHITE); L.hl(x - 5, x + 5, base - 6, GREY[1])
        L.vl(x, base - 5, base, INK2); L.hl(x - 2, x + 2, base, INK2)
        L.px(x - 3, base - 8, WHITE); L.px(x + 2, base - 8, TERRA)       # cups
        L.outline(INK)
        ground_shadow(c, x + 1, base + 1, 9)
        c.comp(L)
        # bistro chairs (thin, no outline)
        for sx, d in ((x - 9, 1), (x + 9, -1)):
            c.vl(sx, base - 9, base, INK2)
            c.hl(sx, sx + d * 3, base - 4, SAND[2]); c.hl(sx, sx + d * 3, base - 5, SAND[1])
            c.vl(sx + d * 3, base - 3, base, INK2)
            c.px(sx, base - 10, INK)
    table(236, 86, (SAGE, GRASS[2]))
    table(270, 86, (TERRA, RRED[1]))
    planter(c, 216, 84, TRAM[0])
    tree(c, 300, 84, r=9, trunk=7)
    bush(c, 250, 82, 8, 5)
    stops = [ax0 + 7, yx + 16, 236, 270]
    return c, dict(focusX=110, lanes=[dict(y=FEET, x0=8, x1=312, stops=stops)], walkers=2)


def scene_library():
    c = C()
    far_frauenkirche(c, 204, 66)
    pavement(c, 2, 317)
    # --- library: tall round-arched windows, copper roof, portal with steps
    lx, lw, ly = 12, 150, 26
    roof(c, lx, ly, lw, 10, R_COP, inset=1, seams=4)
    facade(c, lx, ly, lw, BASE - ly + 1, F_SAND)
    cornice(c, lx, ly, lw, F_SAND)
    # attic statues / vases
    dormer(c, lx + 22, ly - 2, R_COP, F_SAND); dormer(c, lx + lw - 29, ly - 2, R_COP, F_SAND)
    cxp = lx + lw // 2
    # central portal risalit with pediment
    L = C()
    for i in range(9):
        y = ly - 1 - i
        x0 = cxp - 18 + 2 * i; x1 = cxp + 17 - 2 * i
        if x1 < x0:
            break
        L.hl(x0, x1, y, SAND[1]); L.px(x0, y, SAND[0]); L.px(x1, y, SAND[2])
    L.outline(INK)
    c.comp(L)
    c.px(cxp - 1, ly - 4, GOLD); c.px(cxp, ly - 4, GOLD); c.px(cxp - 1, ly - 3, TRAM[1]); c.px(cxp, ly - 3, TRAM[1])
    rustic(c, lx, 66, lw, 14, F_SAND)
    # tall arched windows (two storeys)
    for i in range(10):
        wx = lx + 7 + i * 14
        if abs(wx + 3 - cxp) < 12:
            continue
        arch_window(c, wx, 36, 7, 24, WHITE, SAND[3], SAND[1], cross=True)
        c.hl(wx, wx + 6, 48, WHITE)
        for yy in range(49, 60, 3):
            pass
    # portal
    c.rect(cxp - 12, ly + 4, 24, BASE - ly - 4, SAND[0])
    c.vl(cxp - 12, ly + 4, BASE, SAND[0]); c.vl(cxp + 11, ly + 4, BASE, SAND[2])
    for px_ in (cxp - 10, cxp - 5, cxp + 3, cxp + 8):
        c.vl(px_, ly + 6, BASE - 5, WHITE); c.vl(px_ + 1, ly + 6, BASE - 5, SAND[1]); c.vl(px_ + 2, ly + 6, BASE - 5, SAND[2])
    arch_window(c, cxp - 3, 36, 6, 14, WHITE, SAND[3], SAND[0], cross=True)
    # open book symbol above the door
    bkx, bky = cxp - 6, 54
    c.box(bkx, bky, 12, 8, TEAL)
    book = [".WWW..WWW.", "WWWWWSWWWW", "WWWWWSWWWW", "WWWWWSWWWW", ".DDDDSDDD."]
    for j, row in enumerate(book):
        for i, ch in enumerate(row):
            if ch != ".":
                c.px(bkx + 1 + i, bky + 1 + j, {"W": WHITE, "S": SAND[3], "D": SAND[1]}[ch])
    door(c, cxp - 5, 10, 18, (SAND[2], SAND[3], SAND[4]), SAND[4], double=True)
    plinth(c, lx, lw, F_SAND)
    # --- trees with a reading bench
    tree(c, 180, 84, r=11, trunk=9)
    tree(c, 222, 84, r=10, trunk=8)
    bench(c, 194, 86, 16)
    # --- book kiosk
    kx, kw, ky = 246, 50, 52
    L = C()
    L.rect(kx, ky, kw, BASE - ky + 1, TEAL)
    L.vl(kx, ky, BASE, COP[1]); L.vl(kx + kw - 1, ky, BASE, PINE[0])
    # open front with shelves
    L.rect(kx + 3, ky + 6, kw - 6, 18, SAND[3])
    for sh in range(2):
        yb = ky + 6 + sh * 9
        L.hl(kx + 3, kx + kw - 4, yb + 8, SAND[4])
        x = kx + 4
        k = 0
        cols = [TERRA, NAVY, MUST, SAGE, ROSE, STEEL[0], APO, CREAM, TEAL, GOLD]
        while x < kx + kw - 4:
            wbk = 1 + (k * 7 + sh) % 2
            hb = 5 + (k * 3 + sh * 2) % 3
            col = cols[(k * 3 + sh * 5) % len(cols)]
            L.rect(x, yb + 8 - hb, wbk, hb, col)
            x += wbk + (1 if k % 4 == 3 else 0)
            k += 1
    # counter
    L.rect(kx + 1, ky + 24, kw - 2, BASE - ky - 23, TEAL)
    L.hl(kx + 1, kx + kw - 2, ky + 24, COP[0])
    L.hl(kx + 1, kx + kw - 2, ky + 25, COP[1])
    for i in range(5):     # books lying on the counter
        L.rect(kx + 5 + i * 9, ky + 22, 6, 2, [TERRA, STEEL[0], MUST, CREAM, SAGE][i])
        L.px(kx + 5 + i * 9, ky + 22, WHITE)
    # awning
    for i in range(6):
        for x in range(kx - 4 + (5 - i) // 2, kx + kw + 4 - (5 - i) // 2):
            st = ((x - kx + 40) // 4) % 2
            L.px(x, ky - 6 + i, (CREAM if i < 5 else SAND[1]) if st else (TEAL if i < 5 else PINE[0]))
    for x in range(kx - 4, kx + kw + 4):
        st = ((x - kx + 40) // 4) % 2
        if (x - kx + 40) % 4 in (1, 2):
            L.px(x, ky, SAND[1] if st else PINE[0])
    L.outline(INK)
    c.comp(L)
    # book cart in front
    L = C()
    L.rect(kx + 12, 76, 16, 6, SAND[2]); L.hl(kx + 12, kx + 27, 76, SAND[1])
    for i in range(7):
        L.rect(kx + 13 + i * 2, 72 + (i % 3), 2, 4 - (i % 3), [NAVY, TERRA, MUST, SAGE, ROSE, TEAL, CREAM][i])
    L.px(kx + 13, 83, INK2); L.px(kx + 26, 83, INK2)
    L.vl(kx + 13, 82, 83, INK2); L.vl(kx + 26, 82, 83, INK2)
    L.outline(INK)
    c.comp(L)
    lamp(c, 238, 86)
    bush(c, 168, 83, 8, 5)
    stops = [cxp, 202, kx + 20]
    return c, dict(focusX=cxp, lanes=[dict(y=FEET, x0=8, x1=312, stops=stops)], walkers=2)


def scene_notfound():
    c = C()
    pavement(c, 70, 250)
    # rails in the street hint (below the kerb is the scene edge, so just the kerb)
    # shelter: steel frame, glass, roof
    sx, sw, sy = 132, 52, 50
    ground_shadow(c, sx + sw // 2 + 2, 84, sw // 2)
    L = C()
    # roof
    L.rect(sx - 3, sy - 4, sw + 6, 4, GREY[1])
    L.hl(sx - 3, sx + sw + 2, sy - 4, GREY[0])
    L.hl(sx - 3, sx + sw + 2, sy - 1, GREY[2])
    # glass back wall
    L.rect(sx, sy, sw, BASE - sy - 1, WATER[0])
    for x in range(sx, sx + sw):
        for y in range(sy, BASE - 1):
            if (x - sx + (y - sy)) % 13 == 0 or (x - sx + (y - sy)) % 13 == 1:
                L.px(x, y, WHITE)
    L.hl(sx, sx + sw - 1, sy, WATER[1])
    # frame posts
    for px_ in (sx, sx + sw // 2, sx + sw - 1):
        L.vl(px_, sy - 1, BASE + 2, STEEL[1])
    L.vl(sx + 1, sy - 1, BASE + 2, STEEL[0])
    # map/timetable panel (no text: just a blank panel with a line)
    L.rect(sx + 6, sy + 6, 12, 16, WHITE); L.hl(sx + 6, sx + 17, sy + 6, TRAM[0]); L.hl(sx + 6, sx + 17, sy + 7, TRAM[0])
    for yy in range(sy + 10, sy + 20, 3):
        L.hl(sx + 8, sx + 15, yy, GREY[1])
    # bench inside
    L.hl(sx + 30, sx + sw - 5, 72, SAND[1]); L.hl(sx + 30, sx + sw - 5, 73, SAND[3])
    L.vl(sx + 32, 74, 78, INK2); L.vl(sx + sw - 7, 74, 78, INK2)
    L.hl(sx, sx + sw - 1, BASE - 1, GREY[2])
    L.outline(INK)
    c.comp(L)
    # stop sign pole: a yellow disc with a small tram symbol
    L = C()
    px0 = 118
    L.vl(px0, 50, 84, GREY[2]); L.vl(px0 + 1, 50, 84, GREY[1])
    for y in range(38, 49):
        for x in range(px0 - 5, px0 + 7):
            d = (x - px0 - 0.5) ** 2 + (y - 43) ** 2
            if d <= 30:
                L.px(x, y, TRAM[0] if (x - px0) + (y - 43) < 2 else TRAM[1])
    for y in range(38, 49):
        for x in range(px0 - 5, px0 + 7):
            d = (x - px0 - 0.5) ** 2 + (y - 43) ** 2
            if 8 <= d <= 16:
                L.px(x, y, GRASS[2])
            elif d < 8:
                L.px(x, y, TRAM[0])
    L.outline(INK)
    c.comp(L)
    lamp(c, 204, 86, h=38)
    # waste bin
    L = C()
    L.rect(214, 76, 6, 8, GREY[2]); L.hl(214, 219, 76, GREY[1]); L.vl(214, 76, 83, GREY[1])
    L.outline(INK)
    c.comp(L)
    return c, dict(focusX=160, lanes=[dict(y=FEET, x0=80, x1=240, stops=[158])], walkers=0)


SCENES = [("services", scene_services), ("courses", scene_courses), ("events", scene_events),
          ("communities", scene_communities), ("library", scene_library), ("notfound", scene_notfound)]


def to_indexed(im):
    """RGBA -> palette PNG with a transparent index (exact colours only)."""
    cols = {}
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            p = px[x, y]
            if p[3]:
                cols.setdefault(p[:3], len(cols) + 1)
    if len(cols) > 255:
        return None
    pal = [0, 0, 0]
    for rgb, _ in sorted(cols.items(), key=lambda kv: kv[1]):
        pal += list(rgb)
    out = Image.new("P", im.size, 0)
    op = out.load()
    for y in range(im.height):
        for x in range(im.width):
            p = px[x, y]
            op[x, y] = cols[p[:3]] if p[3] else 0
    out.putpalette(pal + [0] * (768 - len(pal)))
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(PREV, exist_ok=True)
    only = sys.argv[1:]
    meta = {}
    for sid, fn in SCENES:
        if only and sid not in only:
            continue
        c, m = fn()
        meta[sid] = m
        path = os.path.join(OUT, "scene-%s.png" % sid)
        ix = to_indexed(c.im)
        if ix is not None:
            ix.save(path, optimize=True, transparency=0)
        else:
            c.im.save(path, optimize=True)
        prev = Image.new("RGBA", (W, H), hx(PAPER))
        prev.alpha_composite(c.im)
        prev.resize((W * 6, H * 6), Image.NEAREST).save(os.path.join(PREV, "scene-%s.png" % sid))
        print(sid, os.path.getsize(path), "bytes", m)
    import json
    with open(os.path.join(PREV, "scenes-meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=1)
    write_ts(meta)


TS = os.environ.get("PIXEL_TS", r"C:/Users/a_rahman/Desktop/Automation/hallotermin-paper/src/components/pixel/scenes.data.ts")


def write_ts(meta):
    """Replace ONLY our marker blocks (// <id> ... // </id>) in scenes.data.ts."""
    if not os.path.exists(TS):
        print("scenes.data.ts not found, skipped")
        return
    src = open(TS, encoding="utf-8").read()
    for sid, m in meta.items():
        a, b = "// <%s>" % sid, "// </%s>" % sid
        if a not in src or b not in src:
            print("markers missing for", sid)
            continue
        lanes = ", ".join("{ y: %d, x0: %d, x1: %d, stops: [%s] }" % (l["y"], l["x0"], l["x1"], ", ".join(str(v) for v in l["stops"]))
                          for l in m["lanes"])
        block = "\n".join([
            a,
            "export const %s: SceneDef | null = {" % sid.upper(),
            '  id: "%s",' % sid,
            '  src: "/pixel/scene-%s.png",' % sid,
            "  w: %d," % W,
            "  h: %d," % H,
            "  focusX: %d," % m["focusX"],
            "  lanes: [%s]," % lanes,
            "  walkers: %d," % m["walkers"],
            "};",
            b,
        ])
        i0 = src.index(a); i1 = src.index(b) + len(b)
        src = src[:i0] + block + src[i1:]
    with open(TS, "w", encoding="utf-8", newline="\n") as f:
        f.write(src)
    print("scenes.data.ts updated:", ", ".join(meta))


if __name__ == "__main__":
    main()
