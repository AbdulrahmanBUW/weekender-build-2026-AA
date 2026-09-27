# -*- coding: utf-8 -*-
"""Home band (960x128) + tram strip (2 x 64x20) for the Ankommen site.

Original pixel art drawn as code with the palette from docs/pixel/BRIEF.md.
Run:  python scripts/pixel/make_home.py
Writes public/pixel/home.png + tram.png in the Lovable repo and 6x previews to docs/pixel/previews/.
"""
import os
import random
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
TEAM = os.path.abspath(os.path.join(HERE, "..", ".."))
APP = os.path.abspath(os.path.join(TEAM, "..", "hallotermin-paper"))
OUT_DIR = os.path.join(APP, "public", "pixel")
PREV_DIR = os.path.join(TEAM, "docs", "pixel", "previews")

W, H = 960, 128


def hx(s):
    s = s.lstrip("#")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), 255)


INK, INK2, PAPER, CREAM, WHITE = map(hx, ["1C2420", "3A3F3A", "F7F4EC", "EFE4CF", "FFFFFF"])
SS1, SS2, SS3, SS4, SS5 = map(hx, ["F1E4C6", "D9C49A", "B59D73", "8C7453", "5E4C38"])
CU1, CU2, CU3 = map(hx, ["A9CDBB", "74A590", "4E7E6B"])
PINE1, PINE2 = map(hx, ["1F5C4A", "174A3B"])
W1, W2, W3 = map(hx, ["B7D1D6", "8DB2BD", "638D9B"])
G1, G2, G3, G4 = map(hx, ["BCD08F", "8FB068", "638A48", "3F6233"])
RR1, RR2 = map(hx, ["C9704F", "93493A"])
ST1, ST2, ST3 = map(hx, ["D3CDBF", "A8A296", "77736A"])
TY1, TY2 = map(hx, ["FFD541", "D9A21B"])
APO, GOLD = hx("B4202A"), hx("E0B04A")
SB1, SB2 = hx("6E97C9"), hx("3F66A0")
CLEAR = (0, 0, 0, 0)


class Layer:
    def __init__(self, w=W, h=H):
        self.w, self.ht = w, h
        self.im = Image.new("RGBA", (w, h), CLEAR)
        self.p = self.im.load()

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.ht:
            self.p[x, y] = c

    def rect(self, x0, y0, x1, y1, c):
        for y in range(max(0, y0), min(self.ht - 1, y1) + 1):
            for x in range(max(0, x0), min(self.w - 1, x1) + 1):
                self.p[x, y] = c

    def h(self, x0, x1, y, c):
        self.rect(x0, y, x1, y, c)

    def v(self, x, y0, y1, c):
        self.rect(x, y0, x, y1, c)

    def get(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.ht:
            return self.p[x, y]
        return CLEAR

    def on(self, x, y):
        return self.get(x, y)[3] > 0

    def sprite(self, x0, y0, rows, cmap):
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch in cmap:
                    self.px(x0 + i, y0 + j, cmap[ch])

    def outline(self, light, dark, box=None):
        """1px outline outside the silhouette; right/bottom sides get the darker colour."""
        x0, y0, x1, y1 = box or (0, 0, self.w - 1, self.ht - 1)
        pts = []
        for y in range(max(0, y0 - 1), min(self.ht, y1 + 2)):
            for x in range(max(0, x0 - 1), min(self.w, x1 + 2)):
                if self.p[x, y][3]:
                    continue
                if self.on(x - 1, y) or self.on(x, y - 1):
                    pts.append((x, y, dark))
                elif self.on(x + 1, y) or self.on(x, y + 1):
                    pts.append((x, y, light))
        for x, y, c in pts:
            self.p[x, y] = c

    def paste(self, other, dx=0, dy=0):
        self.im.alpha_composite(other.im, (dx, dy))
        self.p = self.im.load()


def shade_row(L, cx, y, w, cols, cuts):
    """Fill row y from cx-w..cx+w; cols[i] used while t < cuts[i] (t = 0..1 left to right)."""
    for x in range(cx - w, cx + w + 1):
        t = (x - (cx - w) + 0.5) / (2 * w + 1)
        for c, cut in zip(cols, cuts):
            if t <= cut:
                L.px(x, y, c)
                break


# ----------------------------------------------------------------------------------------------
# layout constants
TERR = 64          # top of Brühl's Terrace wall = ground line of the Altstadt skyline
RIV0, RIV1 = 74, 99
BANK0 = 100        # Neustadt meadow
WALK0, WALK1 = 112, 125
FEET = 122
BX0, ARCH, PIER, NARCH = 380, 24, 6, 7
BX1 = BX0 + NARCH * ARCH + (NARCH + 1) * PIER - 1   # 601
DECK = 84          # bridge deck surface (tram wheels stand here)
FK_CX = 300        # Frauenkirche centre
KA_CX = 392        # Kunstakademie dome
HM_CX = 462        # Hausmannsturm
HK_CX = 572        # Hofkirche tower
SO_CX = 664        # Semperoper centre

BENCHES = [232, 424, 612, 738]
LAMPS = [176, 336, 518, 682, 792]
TREES = [(58, 1.0), (96, 0.8), (206, 1.0), (764, 1.0), (806, 0.85)]
KIOSK_X = 848      # centre
STOP_X = 898       # centre of shelter


# ----------------------------------------------------------------------------------------------
def hills(img):
    far = Layer()
    import math
    for x in range(36, 926):
        # stepped hill profile: high on the left (Loschwitz slopes), low to the right
        hgt = 10 + 12 * math.exp(-((x - 130) / 90.0) ** 2) + 4 * math.sin(x / 37.0) + 3 * math.sin(x / 13.0 + 1)
        hgt += 6 * math.exp(-((x - 860) / 60.0) ** 2)
        edge = min(x - 36, 925 - x)
        if edge < 40:
            hgt *= edge / 40.0
        top = TERR - int(round(hgt / 2.0) * 2 / 2)  # keep steps calm
        top = TERR - int(hgt)
        far.v(x, top, TERR + 2, W1)
    img.paste(far)
    # nearer green slope only at the far left and far right of the far bank
    near = Layer()
    for x in range(36, 190):
        hgt = 8 + 5 * math.sin((x - 36) / 30.0) + 2 * math.sin(x / 7.0)
        edge = x - 36
        if edge < 30:
            hgt *= edge / 30.0
        near.v(x, TERR - int(hgt) + 4, TERR + 4, CU1)
    for x in range(760, 925):
        hgt = 7 + 4 * math.sin((x - 760) / 26.0) + 2 * math.sin(x / 6.0)
        edge = 925 - x
        if edge < 30:
            hgt *= edge / 30.0
        near.v(x, TERR - int(hgt) + 4, TERR + 4, CU1)
    img.paste(near)
    # Fernsehturm (far, faint): slim shaft, cabin near top, red/white tip
    fx, fb = 128, 44
    t = Layer()
    t.v(fx, fb - 24, fb, ST1)
    t.v(fx + 1, fb - 24, fb, ST2)
    t.h(fx - 1, fx + 2, fb, ST2)
    t.rect(fx - 1, fb - 22, fx + 2, fb - 20, ST2)   # cabin
    t.h(fx - 1, fx + 2, fb - 22, ST1)
    t.v(fx, fb - 30, fb - 25, WHITE)
    t.px(fx, fb - 30, RR1)
    t.px(fx, fb - 28, RR1)
    t.px(fx, fb - 26, RR1)
    img.paste(t)


def far_bank_greens(img):
    """Tree rows on the Brühl's Terrace and the far bank (faded)."""
    L = Layer()
    rnd = random.Random(7)
    def crown(cx, cy, r, base, hi, lo):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r - 1, cx + r + 2):
                d = ((x - cx) / (r + 0.6)) ** 2 + ((y - cy) / (r + 0.2)) ** 2
                if d <= 1.0:
                    L.px(x, y, base)
    for cx in list(range(44, 170, 9)) + list(range(772, 922, 9)):
        cy = TERR + 1 - rnd.choice([0, 1, 2])
        crown(cx, cy, 3 + rnd.choice([0, 1]), CU1, W1, CU2)
    # terrace trees (lindens) between the buildings
    for cx in list(range(182, 262, 8)) + list(range(342, 354, 8)) + list(range(716, 768, 8)):
        crown(cx, TERR - 4 - (cx // 8) % 2, 4, CU1, G1, CU2)
    # shade only the lower rim of the whole tree mass (calm, no stripes)
    rim = [(x, y) for y in range(L.ht) for x in range(L.w) if L.on(x, y) and not L.on(x, y + 1)]
    rim += [(x, y) for y in range(L.ht) for x in range(L.w) if L.on(x, y) and not L.on(x + 1, y) and L.on(x, y + 2)]
    for (x, y) in rim:
        L.px(x, y, CU2)
    img.paste(L)


def low_blocks(img):
    """Faded background buildings (Albertinum side, Residenzschloss, Taschenberg/Zwinger side)."""
    L = Layer()
    def block(x0, x1, top, roof_h, fac, roof, win):
        L.rect(x0, top + roof_h, x1, TERR - 1, fac)
        for i in range(roof_h):
            L.h(x0 + (roof_h - i) - 1, x1 - (roof_h - i) + 1, top + i, roof)
        for y in range(top + roof_h + 2, TERR - 2, 4):
            for x in range(x0 + 2, x1 - 1, 4):
                L.v(x, y, y + 1, win)
    block(196, 252, 44, 3, SS1, CU1, SS2)      # Albertinum-like block
    block(420, 530, 46, 4, SS1, ST1, SS2)      # Residenzschloss / Ständehaus
    block(700, 758, 48, 3, SS1, CU1, SS2)      # Taschenbergpalais side
    L.outline(SS2, SS3)
    img.paste(L)


# ----------------------------------------------------------------------------------------------
def frauenkirche(img):
    cx = FK_CX
    L = Layer()
    base = TERR - 1
    # body
    bx0, bx1 = cx - 25, cx + 25
    L.rect(bx0, 41, bx1, base, SS1)
    L.rect(cx + 8, 41, bx1, base, SS2)
    L.rect(bx1 - 3, 41, bx1, base, SS3)
    L.h(bx0, bx1, 41, CREAM)          # cornice highlight
    L.h(bx0, bx1, 42, SS3)            # cornice shadow
    # arched windows, two rows
    for x in range(bx0 + 5, bx1 - 3, 7):
        if abs(x + 1 - cx) < 5:
            continue
        for (y0, y1) in ((45, 51), (54, 59)):
            L.rect(x, y0 + 1, x + 2, y1, SS4)
            L.px(x + 1, y0, SS4)
            L.h(x, x + 2, y1, SS3)
            L.px(x, y0 + 1, SS3)
    # central portal with pediment
    L.rect(cx - 3, 53, cx + 3, base, SS4)
    L.rect(cx - 2, 52, cx + 2, 52, SS4)
    L.v(cx - 3, 53, base, SS5)
    L.h(cx - 6, cx + 6, 50, SS3)
    L.h(cx - 5, cx + 5, 49, CREAM)
    L.h(cx - 3, cx + 3, 48, CREAM)
    L.h(cx - 1, cx + 1, 47, CREAM)
    # drum
    L.rect(cx - 21, 35, cx + 21, 40, SS1)
    L.rect(cx + 8, 35, cx + 21, 40, SS2)
    L.h(cx - 21, cx + 21, 40, SS3)
    for x in range(cx - 18, cx + 19, 4):
        L.v(x, 37, 38, SS3)
    # the stone bell dome
    half = {13: 4, 14: 7, 15: 9, 16: 10, 17: 11, 18: 12, 19: 12, 20: 13, 21: 13, 22: 13, 23: 13, 24: 13,
            25: 13, 26: 14, 27: 14, 28: 15, 29: 16, 30: 17, 31: 18, 32: 19, 33: 20, 34: 21}
    for y, w in half.items():
        shade_row(L, cx, y, w, [SS1, SS2, SS3], [0.55, 0.86, 1.0])
    for y in range(15, 26):
        L.px(cx - 7, y, CREAM)                   # highlight streak on the crown
    for y in range(26, 33):
        L.px(cx - 8 - (y - 26) // 2, y, CREAM)
    L.h(cx - 21, cx + 21, 34, SS3)               # dome foot ring
    # lantern
    L.h(cx - 4, cx + 4, 12, SS2)
    L.rect(cx - 3, 6, cx + 3, 11, SS1)
    L.rect(cx + 1, 6, cx + 3, 11, SS2)
    L.v(cx - 1, 8, 10, SS4)
    L.v(cx + 2, 8, 10, SS4)
    L.h(cx - 4, cx + 4, 5, SS2)
    L.h(cx - 2, cx + 2, 4, SS1)
    L.h(cx - 1, cx + 1, 3, SS2)
    # four corner towers (two visible on the front, two peeking behind)
    for tx, back in ((cx - 26, False), (cx + 26, False), (cx - 17, True), (cx + 17, True)):
        top = 32 if back else 27
        if back:
            L.rect(tx - 3, top + 3, tx + 3, 40, SS2)
        else:
            L.rect(tx - 4, top + 3, tx + 4, base, SS1 if tx < cx else SS2)
            L.v(tx + 4, top + 3, base, SS3)
            for y in range(top + 6, base - 3, 7):
                L.v(tx - 1, y, y + 2, SS4)
                L.v(tx + 1, y, y + 2, SS4)
        # little bell cap + spire
        L.h(tx - 3, tx + 3, top + 2, SS2)
        L.h(tx - 2, tx + 2, top + 1, SS1)
        L.h(tx - 1, tx + 1, top, SS1)
        L.v(tx, top - 4, top - 1, SS2)
    # dark patina patches (old stones), tidy stone-sized blocks
    rnd = random.Random(1743)
    cells = []
    for _ in range(70):
        x = rnd.randint(cx - 28, cx + 26)
        y = rnd.choice([rnd.randint(22, 33), rnd.randint(43, base - 2), rnd.randint(43, base - 2)])
        cells.append((x & ~1, y))
    def near_dark(x, y):
        return any(L.get(xx, yy) in (SS4, SS5) for xx in range(x - 1, x + 3) for yy in range(y - 1, y + 3))
    for (x, y) in cells:
        if not L.on(x, y) or not L.on(x + 1, y) or near_dark(x, y):
            continue
        cur = L.get(x, y)
        if cur in (SS4, SS5):
            continue
        L.px(x, y, SS4)
        L.px(x + 1, y, SS4)
        if rnd.random() < 0.45 and L.on(x, y + 1) and L.get(x, y + 1) not in (SS4, SS5):
            L.px(x, y + 1, SS5 if rnd.random() < 0.3 else SS4)
    L.outline(SS3, SS4)
    img.paste(L)
    # golden orb + cross (drawn on top, no outline)
    img.px(cx, 2, GOLD)
    img.v(cx, 0, 1, GOLD)
    img.px(cx - 1, 0, GOLD)
    img.px(cx + 1, 0, GOLD)


def kunstakademie(img):
    cx = KA_CX
    L = Layer()
    base = TERR - 1
    x0, x1 = cx - 34, cx + 30
    L.rect(x0, 50, x1, base, SS1)
    L.rect(x1 - 3, 50, x1, base, SS2)
    L.h(x0, x1, 50, CREAM)
    L.h(x0, x1, 51, SS3)
    for i in range(3):   # roof band seen from above
        L.h(x0 + 2 - i, x1 - 2 + i, 47 + i, CU1 if i < 2 else CU2)
    for x in range(x0 + 3, x1 - 2, 5):
        L.rect(x, 54, x + 1, 58, SS3)
        L.px(x, 54, SS2)
    L.h(x0, x1, 60, SS2)
    # drum
    L.rect(cx - 9, 41, cx + 9, 46, SS1)
    L.rect(cx + 4, 41, cx + 9, 46, SS2)
    for x in range(cx - 7, cx + 8, 3):
        L.v(x, 43, 44, SS3)
    # "lemon squeezer": ribbed glass dome
    rows = [11, 11, 10, 10, 9, 9, 8, 8, 7, 6, 5, 4, 3, 2, 1]
    for i, w in enumerate(rows):
        y = 40 - i
        shade_row(L, cx, y, w, [W1, W1, W2], [0.2, 0.62, 1.0])
        for k in (-3, -2, -1, 0, 1, 2, 3):
            xr = cx + int(round(k * w / 3.5))
            if abs(k * w / 3.5) <= w:
                L.px(xr, y, ST2 if k < 1 else W3)
    L.h(cx - 12, cx + 12, 40, ST2)
    L.outline(SS3, SS4)
    img.paste(L)
    # small golden figure (Fama) on top
    img.v(cx, 21, 24, GOLD)
    img.px(cx - 1, 22, GOLD)
    img.px(cx + 1, 21, GOLD)
    img.px(cx + 2, 20, GOLD)


def hausmannsturm(img):
    cx = HM_CX
    L = Layer()
    L.rect(cx - 4, 28, cx + 4, TERR - 1, SS1)
    L.rect(cx + 2, 28, cx + 4, TERR - 1, SS2)
    for y in range(33, 46, 5):
        L.v(cx - 1, y, y + 2, SS3)
        L.v(cx + 1, y, y + 2, SS3)
    L.h(cx - 5, cx + 5, 30, SS2)    # gallery
    L.h(cx - 5, cx + 5, 31, SS3)
    # copper helm: flared roof, neck, open lantern, bulb, spire
    helm = [(29, 5), (28, 4), (27, 3), (26, 3), (25, 2), (24, 2), (23, 2), (22, 3), (21, 3), (20, 2),
            (19, 1), (18, 1), (17, 1), (16, 0), (15, 0), (14, 0)]
    for y, w in helm:
        shade_row(L, cx, y, w, [CU1, CU2, CU3], [0.34, 0.75, 1.0])
    L.px(cx, 24, CU3)   # lantern opening
    L.outline(CU2, CU3, box=(cx - 6, 12, cx + 6, 31))
    L.outline(SS3, SS4, box=(cx - 6, 32, cx + 6, TERR))
    img.paste(L)
    img.v(cx, 11, 13, GOLD)


def hofkirche(img):
    cx = HK_CX
    L = Layer()
    base = TERR - 1
    # nave: lower aisle + clerestory, both with balustrades and statues
    nx0, nx1 = cx - 78, cx - 8
    L.rect(nx0, 51, nx1, base, SS1)
    L.h(nx0, nx1, 51, CREAM)
    L.h(nx0, nx1, 52, SS3)
    for x in range(nx0 + 3, nx1 - 2, 6):
        L.rect(x, 55, x + 1, 60, SS3)
        L.px(x, 55, SS2)
    L.rect(nx0 + 6, 41, nx1 - 4, 50, SS1)
    L.rect(nx1 - 10, 41, nx1 - 4, 50, SS2)
    L.h(nx0 + 6, nx1 - 4, 41, CREAM)
    L.h(nx0 + 6, nx1 - 4, 42, SS3)
    for x in range(nx0 + 9, nx1 - 6, 6):
        L.rect(x, 44, x + 1, 48, SS3)
    # copper roof seen from above
    for i in range(5):
        L.h(nx0 + 10 + (4 - i), nx1 - 7 - (4 - i), 36 + i, CU1 if i < 3 else CU2)
    L.outline(SS3, SS4)
    # statues on both balustrades (tiny figures)
    for x in range(nx0 + 1, nx1, 6):
        L.v(x, 48, 50, SS3)
        L.px(x, 47, SS2)
    for x in range(nx0 + 8, nx1 - 4, 6):
        L.v(x, 38, 40, SS3)
        L.px(x, 37, SS2)
    img.paste(L)
    # tower: tall, slender, tiered
    T = Layer()
    tiers = [(38, base, 8), (28, 37, 6), (19, 27, 4), (13, 18, 3)]
    for (y0, y1, w) in tiers:
        T.rect(cx - w, y0, cx + w, y1, SS1)
        T.rect(cx + w // 2 + 1, y0, cx + w, y1, SS2)
        T.h(cx - w - 1, cx + w + 1, y0, CREAM)
        T.h(cx - w, cx + w, y0 + 1, SS3)
    # openings per tier
    T.rect(cx - 2, 43, cx + 2, 54, SS3)
    T.h(cx - 1, cx + 1, 42, SS3)
    T.rect(cx - 1, 31, cx + 1, 36, SS4)
    T.px(cx, 30, SS4)
    T.rect(cx - 5, 31, cx - 4, 36, SS2)
    T.rect(cx + 4, 31, cx + 5, 36, SS3)
    T.rect(cx - 1, 21, cx + 1, 25, SS4)
    T.v(cx, 15, 17, SS4)
    # copper cap + lantern
    for y, w in ((12, 3), (11, 2), (10, 2), (9, 1), (8, 1), (7, 0), (6, 0)):
        shade_row(T, cx, y, w, [CU1, CU2, CU3], [0.34, 0.75, 1.0])
    T.outline(SS3, SS4)
    img.paste(T)
    # corner statues on the tier cornices + cross
    for (x, y) in ((cx - 7, 36), (cx + 7, 36), (cx - 5, 26), (cx + 5, 26)):
        img.v(x, y - 2, y, SS3)
    img.v(cx, 3, 5, GOLD)
    img.px(cx - 1, 4, GOLD)
    img.px(cx + 1, 4, GOLD)


def semperoper(img):
    cx = SO_CX
    L = Layer()
    hw = 50
    # stage house + auditorium roof behind the curved front
    L.rect(cx - 22, 28, cx + 24, 44, SS1)
    L.rect(cx + 12, 28, cx + 24, 44, SS2)
    for i in range(6):
        L.h(cx - 22 + i, cx + 24 - i, 27 - i, CU1 if i > 0 else CU2)
    for x in range(cx - 18, cx + 22, 5):
        L.v(x, 31, 33, SS3)
    # curved auditorium roof (half ellipse)
    for y in range(33, 46):
        t = (45 - y) / 12.0
        w = int(round(hw * (1 - t * t) ** 0.5 * 0.92))
        shade_row(L, cx, y, w, [CU1, CU1, CU2], [0.3, 0.72, 1.0])
    # curved front: cornice + base bow towards the viewer in the middle (3/4 view of a half-circle)
    for x in range(cx - hw, cx + hw + 1):
        u = (x - cx) / float(hw)
        bow = int(round(3 * (1 - u * u)))
        top = 44 + bow
        bot = TERR - 4 + bow
        col = SS1 if u < 0.35 else SS2
        if u > 0.8:
            col = SS3
        L.v(x, top, bot, col)
        L.px(x, top, CREAM if u < 0.5 else SS1)
        L.px(x, top - 1, CU2)
        L.px(x, top + 1, SS3)
        # two rows of arches, 6 px rhythm
        k = (x - (cx - hw)) % 6
        if 2 <= k <= 4 and abs(x - cx) > 13:
            ac = SS4 if u < 0.8 else SS5
            for (a0, a1) in ((top + 4, top + 8), (top + 11, top + 15)):
                if k == 3:
                    L.v(x, a0, a1, ac)
                else:
                    L.v(x, a0 + 1, a1, ac)
        L.px(x, top + 9, SS3 if u > 0 else SS2)
    # central portal niche, taller block
    L.rect(cx - 12, 36, cx + 12, TERR - 1, SS1)
    L.rect(cx + 6, 36, cx + 12, TERR - 1, SS2)
    L.h(cx - 12, cx + 12, 36, CREAM)
    L.h(cx - 12, cx + 12, 37, SS3)
    niche = {41: 3, 42: 5, 43: 6, 44: 6}
    for y in range(41, 60):
        w = niche.get(y, 7)
        L.h(cx - w, cx + w, y, SS4 if y < 50 else SS3)
        L.px(cx - w, y, SS5)
    for x in range(cx - 6, cx + 7, 3):
        L.v(x, 52, 59, SS2)
    L.h(cx - 8, cx + 8, 60, SS2)
    L.h(cx - 12, cx + 12, TERR - 1, SS3)
    L.outline(SS3, SS4)
    img.paste(L)
    # quadriga on the portal (dark bronze silhouette, 4 horses + driver)
    q = [
        "......#......",
        ".....###.....",
        ".#.#.#.#.#...",
        "#############",
        ".#.#.#.#.#.#.",
    ]
    L2 = Layer()
    L2.sprite(cx - 6, 31, q, {"#": SS5})
    img.paste(L2)


def terrace_wall(img):
    L = Layer()
    x0, x1 = 168, 772
    L.rect(x0, TERR, x1, RIV0 - 1, SS2)
    L.h(x0, x1, TERR, SS1)
    L.h(x0, x1, TERR + 1, SS3)
    for y in (TERR + 4, TERR + 7):
        L.h(x0, x1, y, SS3)
    for x in range(x0 + 4, x1, 12):
        L.v(x, TERR + 2, TERR + 3, SS3)
        L.v(x + 6, TERR + 5, TERR + 6, SS3)
    L.h(x0, x1, RIV0 - 1, SS4)
    # small steps down at both ends
    for i in range(4):
        L.rect(x0 - 3 - 3 * i, TERR + 2 + 2 * i, x0 - 1 - 3 * i, RIV0 - 1, SS2)
        L.px(x0 - 3 - 3 * i, TERR + 2 + 2 * i, SS1)
        L.rect(x1 + 1 + 3 * i, TERR + 2 + 2 * i, x1 + 3 + 3 * i, RIV0 - 1, SS2)
    L.outline(SS3, SS4)
    # far bank meadow strips outside the wall (under the steps)
    B = Layer()
    for x in list(range(30, x0 - 2)) + list(range(x1 + 3, 930)):
        B.v(x, TERR + 3 + (x // 5) % 2, RIV0 - 1, G1)
        B.px(x, RIV0 - 1, G2)
    img.paste(B)
    img.paste(L)


def river(img):
    L = Layer()
    L.rect(0, RIV0, W - 1, RIV1, W2)
    L.h(0, W - 1, RIV0, W3)
    L.h(0, W - 1, RIV0 + 1, W3)
    for x in range(0, W, 4):
        L.px(x, RIV0 + 2, W3)
    rnd = random.Random(99)
    for _ in range(95):
        y = rnd.randint(RIV0 + 4, RIV1 - 2)
        x = rnd.randint(0, W - 10)
        ln = rnd.choice([3, 4, 5, 6, 8])
        c = W1 if rnd.random() < 0.7 else W3
        L.h(x, x + ln - 1, y, c)
    img.paste(L)


def bridge(img):
    L = Layer()
    y_top = DECK
    x0, x1 = BX0, BX1
    # far parapet (behind the tram)
    L.h(x0, x1, y_top - 3, SS1)
    for x in range(x0, x1 + 1, 3):
        L.v(x, y_top - 2, y_top - 1, SS2)
    # deck face (spandrel) + cornice
    L.h(x0 - 2, x1 + 2, y_top, SS3)
    L.rect(x0, y_top + 1, x1, RIV1 - 3, SS1)
    L.h(x0 - 2, x1 + 2, y_top + 1, CREAM)
    L.h(x0 - 2, x1 + 2, y_top + 2, SS3)
    # arches
    for i in range(NARCH):
        ax0 = x0 + PIER + i * (ARCH + PIER)
        ax1 = ax0 + ARCH - 1
        acx = (ax0 + ax1) / 2.0
        for x in range(ax0, ax1 + 1):
            u = (x - acx) / (ARCH / 2.0)
            crown = y_top + 5 + int(round(5 * (u * u)))
            for y in range(crown, RIV1 - 2):
                c = W3 if y < crown + 3 else W2
                L.px(x, y, c)
            L.px(x, crown - 1, SS3)          # arch ring shadow
        # pier: lit left face, darker right, cutwater
        px0 = x0 + i * (ARCH + PIER)
        L.v(px0, y_top + 3, RIV1 - 3, SS1)
        L.v(px0 + PIER - 1, y_top + 3, RIV1 - 3, SS2)
    last = x0 + NARCH * (ARCH + PIER)
    L.v(last + PIER - 1, y_top + 3, RIV1 - 3, SS2)
    # right side shading of piers
    for i in range(NARCH + 1):
        px0 = x0 + i * (ARCH + PIER)
        L.v(px0 + PIER - 2, y_top + 6, RIV1 - 3, SS2)
    # solid abutments at both ends (stepped, widening towards the water)
    for j, y in enumerate(range(y_top + 3, RIV1 - 2)):
        ext = 2 + j // 2
        L.h(x0 - ext, x0 - 1, y, SS2)
        L.px(x0 - ext, y, SS1)
        L.h(x1 + 1, x1 + ext, y, SS3)
    L.outline(SS3, SS4)
    img.paste(L)
    # waterline foam + pier reflections
    R = Layer()
    for i in range(NARCH + 1):
        px0 = x0 + i * (ARCH + PIER)
        R.h(px0 - 1, px0 + PIER, RIV1 - 2, W1)
        R.h(px0, px0 + PIER - 1, RIV1 - 1, W3)
        R.h(px0 + 1, px0 + PIER - 2, RIV1, W3)
    img.paste(R)


def near_bank(img):
    L = Layer()
    L.rect(0, BANK0, W - 1, WALK0 - 1, G1)
    L.h(0, W - 1, BANK0, G3)
    L.h(0, W - 1, BANK0 + 1, G2)
    for x in range(0, W, 3):
        L.px(x, BANK0 + 2, G2 if (x // 3) % 2 else G1)
    rnd = random.Random(5)
    for _ in range(150):
        x = rnd.randint(0, W - 3)
        y = rnd.randint(BANK0 + 4, WALK0 - 3)
        L.px(x, y, G2)
        L.px(x + 1, y - 1, G2)
    for _ in range(26):   # a few meadow flowers
        x = rnd.randint(0, W - 1)
        y = rnd.randint(BANK0 + 4, WALK0 - 3)
        L.px(x, y, CREAM if rnd.random() < 0.6 else GOLD)
    # walkway (paved), feet line FEET inside the lower slab course
    L.h(0, W - 1, WALK0 - 1, ST2)
    L.rect(0, WALK0, W - 1, WALK1, ST1)
    L.h(0, W - 1, WALK0, PAPER if False else CREAM)
    L.h(0, W - 1, 118, ST2)
    for x in range(0, W, 16):
        L.v(x, WALK0 + 1, 117, ST2)
        L.v(x + 8, 119, WALK1, ST2)
    L.h(0, W - 1, WALK1 + 1, ST2)
    L.h(0, W - 1, WALK1 + 2, G2)
    img.paste(L)


def tree(img, cx, s):
    L = Layer()
    r = int(round(10 * s))
    cy = WALK0 - 4 - int(round(16 * s)) - r // 2
    # trunk
    L.rect(cx - 1, cy + r - 2, cx + 1, WALK0 - 2, SS4)
    L.v(cx - 1, cy + r - 2, WALK0 - 2, SS3)
    L.v(cx + 1, cy + r - 2, WALK0 - 2, SS5)
    # crown made of three lobes
    for (ox, oy, rr) in ((0, 0, r), (-int(r * 0.6), int(r * 0.35), int(r * 0.7)), (int(r * 0.6), int(r * 0.4), int(r * 0.7))):
        ccx, ccy = cx + ox, cy + oy
        for y in range(ccy - rr, ccy + rr + 1):
            for x in range(ccx - rr - 1, ccx + rr + 2):
                d = ((x - ccx) / (rr + 0.7)) ** 2 + ((y - ccy) / (rr + 0.3)) ** 2
                if d <= 1.0:
                    dd = (x - cx) * 0.7 + (y - cy)
                    c = G2
                    if dd < -r * 0.45:
                        c = G1
                    elif dd > r * 0.55:
                        c = G3
                    L.px(x, y, c)
    # leaf clusters texture
    rnd = random.Random(cx)
    for _ in range(int(14 * s)):
        x = rnd.randint(cx - r, cx + r)
        y = rnd.randint(cy - r, cy + r)
        if L.get(x, y) == G2 and L.get(x + 1, y) == G2:
            L.px(x, y, G1 if (x - cx) + (y - cy) < 0 else G3)
    L.outline(G3, G4)
    # shadow on the grass
    S = Layer()
    S.h(cx - r + 2, cx + r - 2, WALK0 - 2, G2)
    S.h(cx - r + 4, cx + r - 4, WALK0 - 3, G2)
    img.paste(S)
    img.paste(L)


def lamp(img, x):
    L = Layer()
    L.v(x, WALK0 - 20, WALK0 - 1, INK2)
    L.h(x - 1, x + 1, WALK0 - 1, INK)
    L.h(x - 1, x + 1, WALK0 - 2, INK2)
    L.px(x, WALK0 - 8, INK)
    # lantern
    L.h(x - 1, x + 1, WALK0 - 21, INK2)
    L.rect(x - 1, WALK0 - 25, x + 1, WALK0 - 22, CREAM)
    L.px(x - 1, WALK0 - 25, WHITE)
    L.v(x + 1, WALK0 - 25, WALK0 - 22, GOLD)
    L.h(x - 2, x + 2, WALK0 - 26, INK)
    L.px(x, WALK0 - 27, INK)
    img.paste(L)


def bench(img, cx):
    L = Layer()
    x0, x1 = cx - 6, cx + 6
    y = WALK0 - 1
    L.h(x0, x1, y - 4, SS3)        # seat
    L.h(x0, x1, y - 3, SS4)
    L.h(x0, x1, y - 8, SS3)        # backrest slats
    L.h(x0, x1, y - 6, SS3)
    L.h(x0, x1, y - 7, SS4)
    L.h(x0, x1, y - 5, SS4)
    for x in (x0 + 1, x1 - 1):
        L.v(x, y - 2, y, INK2)
        L.v(x, y - 9, y - 8, INK2)
    L.outline(SS5, SS5)
    img.paste(L)


def kiosk(img, cx):
    L = Layer()
    x0, x1 = cx - 13, cx + 13
    gy = WALK0 - 1
    # body
    L.rect(x0, gy - 15, x1, gy, CREAM)
    L.rect(x1 - 3, gy - 15, x1, gy, SS2)
    L.rect(x0, gy - 5, x1, gy, RR2)
    L.h(x0, x1, gy - 5, RR1)
    # counter window with bread
    L.rect(x0 + 3, gy - 13, x1 - 5, gy - 7, SS5)
    L.h(x0 + 3, x1 - 5, gy - 7, SS3)
    for x in range(x0 + 4, x1 - 5, 3):
        L.px(x, gy - 8, GOLD)
        L.px(x + 1, gy - 8, SS3)
    L.h(x0 + 2, x1 - 4, gy - 6, SS3)
    # side door
    L.rect(x1 - 3, gy - 12, x1 - 1, gy - 1, SS3)
    # striped awning
    for x in range(x0 - 2, x1 + 3):
        c = RR1 if ((x - x0) // 3) % 2 == 0 else WHITE
        L.v(x, gy - 18, gy - 16, c)
        if ((x - x0) % 3) == 1:
            L.px(x, gy - 15, c)
    L.h(x0 - 1, x1 + 1, gy - 19, RR2)
    L.outline(SS4, SS5)
    img.paste(L)
    # pretzel sign on a small post
    P = Layer()
    P.v(cx, gy - 24, gy - 20, INK2)
    pretzel = [
        ".aaa.aaa.",
        "a...a...a",
        "a..a.a..a",
        "a.a...a.a",
        "ab.....ba",
        ".bbbbbbb.",
        "..ccccc..",
    ]
    P.sprite(cx - 4, gy - 31, pretzel, {"a": RR1, "b": RR1, "c": RR2})
    for (sx, sy) in ((-2, 5), (1, 5), (3, 4)):
        P.px(cx + sx, gy - 31 + sy, WHITE)

    img.paste(P)


def tram_stop(img, cx):
    L = Layer()
    x0, x1 = cx - 14, cx + 14
    gy = WALK0 - 1
    # glass back wall
    L.rect(x0 + 1, gy - 16, x1 - 1, gy - 2, W1)
    for i in range(4):
        L.px(x0 + 4 + i, gy - 13 + i, WHITE)
        L.px(x0 + 14 + i, gy - 13 + i, WHITE)
    L.h(x0 + 1, x1 - 1, gy - 9, W2)
    # bench inside
    L.h(x0 + 4, x1 - 4, gy - 5, SS3)
    L.v(x0 + 5, gy - 4, gy, INK2)
    L.v(x1 - 5, gy - 4, gy, INK2)
    # frame posts + roof
    for x in (x0, x1):
        L.v(x, gy - 17, gy, INK2)
    L.rect(x0 - 2, gy - 19, x1 + 2, gy - 18, ST3)
    L.h(x0 - 2, x1 + 2, gy - 20, ST2)
    img.paste(L)
    # stop sign pole: yellow disc with green ring (symbol only)
    S = Layer()
    px = x1 + 5
    S.v(px, gy - 22, gy, ST3)
    S.h(px - 1, px + 1, gy, INK2)
    disc = [
        ".ggg.",
        "gyyyg",
        "gyGyg",
        "gyyyg",
        ".ggg.",
    ]
    S.sprite(px - 2, gy - 27, disc, {"g": G3, "y": TY1, "G": G3})
    img.paste(S)


def taper(img):
    """Outer ~32 px on each side end in stepped edges into the paper."""
    for y in range(H):
        # higher rows end earlier; lower rows reach further out
        k = max(0, y - 60)
        cut = 34 - (k // 4) * 2
        cut += 2 if (y // 4) % 3 == 1 else 0
        cut = max(2, min(40, cut))
        for x in range(0, cut):
            img.px(x, y, CLEAR)
            img.px(W - 1 - x, y, CLEAR)


def build_home():
    img = Layer()
    hills(img)
    far_bank_greens(img)
    low_blocks(img)
    kunstakademie(img)
    frauenkirche(img)
    hausmannsturm(img)
    hofkirche(img)
    semperoper(img)
    terrace_wall(img)
    river(img)
    bridge(img)
    near_bank(img)
    for (x, s) in TREES:
        tree(img, x, s)
    for x in BENCHES:
        bench(img, x)
    for x in LAMPS:
        lamp(img, x)
    kiosk(img, KIOSK_X)
    tram_stop(img, STOP_X)
    taper(img)
    return img.im


# ----------------------------------------------------------------------------------------------
def tram_frame(f):
    L = Layer(64, 20)
    # body: rear car 0..30, bellows 31..32, front car 33..63 (cab on the right)
    top, bot = 5, 16
    L.rect(1, top, 30, bot, TY1)
    L.rect(33, top, 61, bot, TY1)
    L.rect(0, top + 1, 0, bot - 1, TY1)
    # front cab slope
    for i, y in enumerate(range(top, bot + 1)):
        xe = 62 if y > top + 3 else 58 + i
        L.h(33, xe, y, TY1)
    L.v(63, top + 5, bot - 1, TY1)
    # lower band + skirt
    for x0, x1 in ((0, 30), (33, 63)):
        L.h(x0, x1, bot - 2, TY2)
        L.h(x0, x1, bot - 1, TY2)
        L.h(x0, x1, bot, TY2)
    L.h(1, 30, top, TY1)
    # windows band
    for x0, x1 in ((2, 29), (34, 57)):
        L.rect(x0, top + 2, x1, top + 6, W2)
        L.h(x0, x1, top + 2, W1)
    # windshield
    for i, y in enumerate(range(top + 2, top + 7)):
        L.h(58, min(62, 58 + i + 1), y, W2)
    L.px(58, top + 2, W1)
    # doors (low floor: down to the floor), window pillars
    for dx in (8, 22, 40, 51):
        L.rect(dx, top + 2, dx + 3, bot - 1, W3)
        L.v(dx + 1, top + 3, bot - 2, W2)
        L.v(dx - 1, top + 2, bot - 1, TY2)
        L.v(dx + 4, top + 2, bot - 1, TY2)
    for px in (5, 15, 19, 27, 37, 45, 48, 55):
        L.v(px, top + 2, top + 6, TY2)
    # bellows
    for y in range(top + 1, bot):
        L.px(31, y, INK2 if y % 2 else ST3)
        L.px(32, y, ST3 if y % 2 else INK2)
    # roof + equipment
    L.h(2, 29, top - 1, ST1)
    L.h(34, 60, top - 1, ST1)
    L.rect(10, top - 2, 18, top - 1, ST2)
    L.rect(50, top - 2, 56, top - 1, ST2)
    # lights
    L.px(62, bot - 3, WHITE)
    L.px(0, bot - 3, RR1)
    L.outline(INK, INK)
    # bogies with wheels
    for wx in (5, 23, 39, 56):
        L.rect(wx - 2, bot + 1, wx + 3, bot + 2, INK2)
        for k in (0, 3):
            L.px(wx - 1 + k, 19, INK)
            L.px(wx - 1 + k, 18, ST2 if (f == 0) else INK)
            L.px(wx + k, 19, INK)
            L.px(wx + k, 18, INK if (f == 0) else ST2)
    # pantograph on the front car (tiny bounce between frames)
    if f == 0:
        L.h(37, 42, 0, INK2)
        L.px(38, 1, INK2)
        L.px(41, 1, INK2)
        L.px(39, 2, INK2)
        L.px(40, 2, INK2)
    else:
        L.h(37, 42, 1, INK2)
        L.px(39, 2, INK2)
        L.px(40, 2, INK2)
    return L.im


def build_tram():
    strip = Image.new("RGBA", (128, 20), CLEAR)
    for f in range(2):
        strip.alpha_composite(tram_frame(f), (f * 64, 0))
    return strip


def save_indexed(im, path):
    q = im.convert("RGBA")
    flat = q.get_flattened_data() if hasattr(q, "get_flattened_data") else q.getdata()
    data = [c if c[3] else CLEAR for c in flat]
    uniq = [CLEAR] + sorted(set(c for c in data if c[3]))
    assert len(uniq) <= 256
    idx = {c: i for i, c in enumerate(uniq)}
    out = Image.new("P", q.size)
    out.putdata([idx[c] for c in data])
    pal = []
    for c in uniq:
        pal += list(c[:3])
    out.putpalette(pal)
    out.info["transparency"] = 0
    out.save(path, optimize=True, transparency=0)
    return os.path.getsize(path), len(uniq) - 1


def preview(im, name, scale=6, bg=PAPER):
    base = Image.new("RGBA", im.size, bg)
    base.alpha_composite(im)
    big = base.resize((im.width * scale, im.height * scale), Image.NEAREST)
    big.convert("RGB").save(os.path.join(PREV_DIR, name))


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(PREV_DIR, exist_ok=True)
    home = build_home()
    tram = build_tram()
    n1, c1 = save_indexed(home, os.path.join(OUT_DIR, "home.png"))
    n2, c2 = save_indexed(tram, os.path.join(OUT_DIR, "tram.png"))
    print("home.png", n1, "bytes", c1, "colours")
    print("tram.png", n2, "bytes", c2, "colours")
    # previews: full band at 2x (site size), crops at 6x
    preview(home, "home_2x.png", 2)
    for i, (x0, x1) in enumerate(((0, 320), (240, 560), (480, 800), (640, 960))):
        preview(home.crop((x0, 0, x1, H)), "home_6x_%d.png" % i, 6)
    # composite check: tram on the deck + walkers' feet line marker
    chk = home.copy()
    chk.alpha_composite(tram.crop((0, 0, 64, 20)), (BX0 + 70, DECK - 20))
    preview(chk.crop((330, 0, 650, H)), "home_tram_check_6x.png", 6)
    preview(tram, "tram_6x.png", 6)
    print("focusX", FK_CX, "bridge", BX0, BX1, "tram y", DECK - 20)


if __name__ == "__main__":
    main()
