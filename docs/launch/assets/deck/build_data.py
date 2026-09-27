"""Build assets/deck/data.js for presentation.html.

Chrome blocks fetch() on file:// pages, so everything the deck needs at run time
(word timings, timelines, manifests, paper SVGs, waveform peaks, the QR code) is
inlined here into one script file. Run from anywhere:

    python docs/launch/assets/deck/build_data.py

Only the Python standard library + ffmpeg on PATH. No keys are read or written.
"""
import json
import os
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LAUNCH = os.path.abspath(os.path.join(HERE, "..", ".."))
AUDIO = os.path.join(LAUNCH, "audio")
ASSETS = os.path.join(LAUNCH, "assets")
URL = "https://ankommen-dresden.lovable.app"


def load_json(path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:  # missing asset -> degrade gracefully
        print("warn: could not read", os.path.relpath(path, LAUNCH), "-", type(e).__name__)
        return default


def read_text(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None


# ---------------------------------------------------------------- waveform
def waveform(mp3, bins=160):
    try:
        raw = subprocess.run(
            ["ffmpeg", "-v", "error", "-i", mp3, "-ac", "1", "-ar", "8000", "-f", "s16le", "-"],
            capture_output=True, check=True).stdout
    except Exception:
        return []
    n = len(raw) // 2
    if n == 0:
        return []
    samples = struct.unpack("<%dh" % n, raw[: n * 2])
    size = max(1, n // bins)
    peaks = []
    for i in range(bins):
        chunk = samples[i * size:(i + 1) * size]
        if not chunk:
            peaks.append(0.0)
            continue
        rms = (sum(s * s for s in chunk) / len(chunk)) ** 0.5
        peaks.append(rms)
    top = max(peaks) or 1.0
    return [round(min(1.0, p / top), 3) for p in peaks]


# ---------------------------------------------------------------- QR code (byte mode, ECC level M)
# Follows the structure of Project Nayuki's reference QR generator (MIT), reduced to what we need.
ECC_PER_BLOCK_M = [-1, 10, 16, 26, 18, 24, 16, 18, 22, 22, 26]
NUM_BLOCKS_M = [-1, 1, 1, 1, 2, 2, 4, 4, 4, 5, 5]
FORMAT_BITS_M = 0  # L=1, M=0, Q=3, H=2


def gf_mul(x, y):
    z = 0
    for i in reversed(range(8)):
        z = (z << 1) ^ ((z >> 7) * 0x11D)
        z ^= ((y >> i) & 1) * x
    return z & 0xFF


def rs_divisor(degree):
    result = [0] * (degree - 1) + [1]
    root = 1
    for _ in range(degree):
        for j in range(degree):
            result[j] = gf_mul(result[j], root)
            if j + 1 < degree:
                result[j] ^= result[j + 1]
        root = gf_mul(root, 0x02)
    return result


def rs_remainder(data, divisor):
    result = [0] * len(divisor)
    for b in data:
        factor = b ^ result.pop(0)
        result.append(0)
        for i, coef in enumerate(divisor):
            result[i] ^= gf_mul(coef, factor)
    return result


def raw_modules(ver):
    result = (16 * ver + 128) * ver + 64
    if ver >= 2:
        na = ver // 7 + 2
        result -= (25 * na - 10) * na - 55
        if ver >= 7:
            result -= 36
    return result


def data_codewords(ver):
    return raw_modules(ver) // 8 - ECC_PER_BLOCK_M[ver] * NUM_BLOCKS_M[ver]


def align_positions(ver, size):
    if ver == 1:
        return []
    na = ver // 7 + 2
    step = (ver * 8 + na * 3 + 5) // (na * 4 - 4) * 2
    result = [size - 7 - i * step for i in range(na - 1)] + [6]
    return list(reversed(result))


class QR:
    def __init__(self, text):
        data = text.encode("utf-8")
        for ver in range(1, 11):
            if len(data) * 8 + 12 <= data_codewords(ver) * 8:
                break
        else:
            raise ValueError("too long")
        self.ver = ver
        self.size = ver * 4 + 17
        bits = []

        def put(val, n):
            for i in reversed(range(n)):
                bits.append((val >> i) & 1)
        put(0b0100, 4)
        put(len(data), 8)
        for b in data:
            put(b, 8)
        cap = data_codewords(ver) * 8
        put(0, min(4, cap - len(bits)))
        put(0, (-len(bits)) % 8)
        pad = 0xEC
        while len(bits) < cap:
            put(pad, 8)
            pad ^= 0xEC ^ 0x11
        codewords = [int("".join(map(str, bits[i:i + 8])), 2) for i in range(0, len(bits), 8)]
        self.data_cw = codewords
        allcw = self._ecc_interleave(codewords)
        n = self.size
        self.mod = [[False] * n for _ in range(n)]
        self.fn = [[False] * n for _ in range(n)]
        self._function_patterns()
        self._draw_codewords(allcw)
        best, best_pen = 0, None
        for m in range(8):
            self._apply_mask(m)
            self._format_bits(m)
            pen = self._penalty()
            if best_pen is None or pen < best_pen:
                best, best_pen = m, pen
            self._apply_mask(m)
        self.mask = best
        self._apply_mask(best)
        self._format_bits(best)

    def _set_fn(self, x, y, dark):
        self.mod[y][x] = dark
        self.fn[y][x] = True

    def _function_patterns(self):
        n = self.size
        for i in range(n):
            self._set_fn(6, i, i % 2 == 0)
            self._set_fn(i, 6, i % 2 == 0)
        for (cx, cy) in ((3, 3), (n - 4, 3), (3, n - 4)):
            for dy in range(-4, 5):
                for dx in range(-4, 5):
                    xx, yy = cx + dx, cy + dy
                    if 0 <= xx < n and 0 <= yy < n:
                        self._set_fn(xx, yy, max(abs(dx), abs(dy)) not in (2, 4))
        pos = align_positions(self.ver, n)
        last = len(pos) - 1
        for i, a in enumerate(pos):
            for j, b in enumerate(pos):
                if (i == 0 and j == 0) or (i == 0 and j == last) or (i == last and j == 0):
                    continue
                for dy in range(-2, 3):
                    for dx in range(-2, 3):
                        self._set_fn(a + dx, b + dy, max(abs(dx), abs(dy)) != 1)
        self._format_bits(0)

    def _format_bits(self, mask):
        data = FORMAT_BITS_M << 3 | mask
        rem = data
        for _ in range(10):
            rem = (rem << 1) ^ ((rem >> 9) * 0x537)
        bits = (data << 10 | rem) ^ 0x5412
        g = lambda i: ((bits >> i) & 1) != 0
        n = self.size
        for i in range(0, 6):
            self._set_fn(8, i, g(i))
        self._set_fn(8, 7, g(6))
        self._set_fn(8, 8, g(7))
        self._set_fn(7, 8, g(8))
        for i in range(9, 15):
            self._set_fn(14 - i, 8, g(i))
        for i in range(0, 8):
            self._set_fn(n - 1 - i, 8, g(i))
        for i in range(8, 15):
            self._set_fn(8, n - 15 + i, g(i))
        self._set_fn(8, n - 8, True)

    def _ecc_interleave(self, data):
        ver = self.ver
        nb = NUM_BLOCKS_M[ver]
        ecl = ECC_PER_BLOCK_M[ver]
        raw = raw_modules(ver) // 8
        nshort = nb - raw % nb
        shortlen = raw // nb
        div = rs_divisor(ecl)
        blocks, k = [], 0
        for i in range(nb):
            dat = data[k:k + shortlen - ecl + (0 if i < nshort else 1)]
            k += len(dat)
            ecc = rs_remainder(dat, div)
            if i < nshort:
                dat = dat + [0]
            blocks.append(dat + ecc)
        out = []
        for i in range(len(blocks[0])):
            for j, blk in enumerate(blocks):
                if i != shortlen - ecl or j >= nshort:
                    out.append(blk[i])
        return out

    def _draw_codewords(self, cw):
        n = self.size
        i = 0
        right = n - 1
        while right >= 1:
            if right == 6:
                right = 5
            for vert in range(n):
                for j in range(2):
                    x = right - j
                    upward = ((right + 1) & 2) == 0
                    y = (n - 1 - vert) if upward else vert
                    if not self.fn[y][x] and i < len(cw) * 8:
                        self.mod[y][x] = ((cw[i >> 3] >> (7 - (i & 7))) & 1) != 0
                        i += 1
            right -= 2

    @staticmethod
    def mask_fn(m, x, y):
        return [
            (x + y) % 2 == 0, y % 2 == 0, x % 3 == 0, (x + y) % 3 == 0,
            (x // 3 + y // 2) % 2 == 0, x * y % 2 + x * y % 3 == 0,
            (x * y % 2 + x * y % 3) % 2 == 0, ((x + y) % 2 + x * y % 3) % 2 == 0][m]

    def _apply_mask(self, m):
        n = self.size
        for y in range(n):
            for x in range(n):
                if not self.fn[y][x] and self.mask_fn(m, x, y):
                    self.mod[y][x] = not self.mod[y][x]

    def _penalty(self):
        n, M = self.size, self.mod
        pen = 0
        for lines in (M, [list(c) for c in zip(*M)]):
            for row in lines:
                run, prev = 0, None
                for v in row:
                    if v == prev:
                        run += 1
                    else:
                        if run >= 5:
                            pen += 3 + run - 5
                        run, prev = 1, v
                if run >= 5:
                    pen += 3 + run - 5
                s = "".join("1" if v else "0" for v in row)
                pen += 40 * (s.count("10111010000") + s.count("00001011101"))
        for y in range(n - 1):
            for x in range(n - 1):
                c = M[y][x]
                if c == M[y][x + 1] == M[y + 1][x] == M[y + 1][x + 1]:
                    pen += 3
        dark = sum(v for row in M for v in row)
        k = (abs(dark * 20 - n * n * 10) + n * n - 1) // (n * n) - 1
        pen += max(0, k) * 10
        return pen

    def svg(self, border=4, px=10, dark="#1C2420", light="#FFFDF8"):
        n = self.size
        dim = (n + border * 2)
        parts = []
        for y in range(n):
            for x in range(n):
                if self.mod[y][x]:
                    parts.append("M%d %dh1v1h-1z" % (x + border, y + border))
        return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" shape-rendering="crispEdges" '
                'role="img" aria-label="QR code for %s">'
                '<rect width="100%%" height="100%%" fill="%s"/><path d="%s" fill="%s"/></svg>'
                % (dim, dim, URL, light, "".join(parts), dark))


def qr_readback(q):
    """Independent read-back: decode format info from the matrix, unmask, collect codewords
    in placement order, de-interleave, check Reed-Solomon syndromes, parse the byte segment."""
    n = q.size
    M = q.mod
    bits = 0
    seq = [(8, i) for i in range(6)] + [(8, 7), (8, 8), (7, 8)] + [(14 - i, 8) for i in range(9, 15)]
    for i, (x, y) in enumerate(seq):
        if M[y][x]:
            bits |= 1 << i
    found = None
    for ecl_bits in range(4):
        for mask in range(8):
            data = ecl_bits << 3 | mask
            rem = data
            for _ in range(10):
                rem = (rem << 1) ^ ((rem >> 9) * 0x537)
            if ((data << 10 | rem) ^ 0x5412) == bits:
                found = (ecl_bits, mask)
    assert found, "format info unreadable"
    assert found[0] == FORMAT_BITS_M
    mask = found[1]
    # second copy must agree
    bits2 = 0
    seq2 = [(n - 1 - i, 8) for i in range(8)] + [(8, n - 15 + i) for i in range(8, 15)]
    for i, (x, y) in enumerate(seq2):
        if M[y][x]:
            bits2 |= 1 << i
    assert bits2 == bits, "format copies differ"
    stream = []
    right = n - 1
    while right >= 1:
        if right == 6:
            right = 5
        for vert in range(n):
            for j in range(2):
                x = right - j
                upward = ((right + 1) & 2) == 0
                y = (n - 1 - vert) if upward else vert
                if not q.fn[y][x]:
                    v = M[y][x] ^ QR.mask_fn(mask, x, y)
                    stream.append(1 if v else 0)
        right -= 2
    total = raw_modules(q.ver) // 8
    cws = [int("".join(map(str, stream[i * 8:i * 8 + 8])), 2) for i in range(total)]
    nb = NUM_BLOCKS_M[q.ver]
    ecl = ECC_PER_BLOCK_M[q.ver]
    nshort = nb - total % nb
    shortlen = total // nb
    lens = [shortlen + (0 if i < nshort else 1) for i in range(nb)]
    blocks = [[] for _ in range(nb)]
    k = 0
    for i in range(max(lens)):
        for j in range(nb):
            if i < lens[j]:
                blocks[j].append(cws[k])
                k += 1
    # move EC bytes: for short blocks the EC part starts at shortlen-ecl
    data_bytes = []
    for j, blk in enumerate(blocks):
        dlen = lens[j] - ecl
        # syndrome check: evaluate polynomial at alpha^i
        for i in range(ecl):
            a = 1
            for _ in range(i):
                a = gf_mul(a, 2)
            s = 0
            for c in blk:
                s = gf_mul(s, a) ^ c
            assert s == 0, "RS syndrome non-zero"
        data_bytes += blk[:dlen]
    bitstr = "".join(format(b, "08b") for b in data_bytes)
    assert bitstr[:4] == "0100", "not byte mode"
    count = int(bitstr[4:12], 2)
    payload = bytes(int(bitstr[12 + 8 * i:20 + 8 * i], 2) for i in range(count))
    return payload.decode("utf-8"), q.ver, mask


def main():
    out = {}
    manifest = load_json(os.path.join(AUDIO, "manifest.json"), []) or []
    out["audio"] = {}
    for entry in manifest:
        cid = entry.get("id")
        words = load_json(os.path.join(AUDIO, entry.get("words_file") or (cid + ".words.json")), []) if cid else []
        out["audio"][cid] = {
            "file": entry.get("file"), "text": entry.get("text"), "lang": entry.get("lang"),
            "speaker": entry.get("speaker"), "duration": entry.get("duration_s"), "words": words or [],
            "voice": entry.get("voice"), "provider": entry.get("provider"),
        }
    out["callTimeline"] = load_json(os.path.join(AUDIO, "call_full.timeline.json"), []) or []
    out["intakeTimeline"] = load_json(os.path.join(AUDIO, "intake_full.timeline.json"), []) or []
    out["ivrWave"] = waveform(os.path.join(AUDIO, "ivr_de.mp3"), 150)
    out["callWave"] = waveform(os.path.join(AUDIO, "call_full.mp3"), 200)
    out["screens"] = load_json(os.path.join(ASSETS, "screens", "manifest.json"), []) or []
    n8n = load_json(os.path.join(ASSETS, "n8n", "manifest.json"), []) or []
    for wf in n8n:
        svg = read_text(os.path.join(ASSETS, "n8n", wf.get("paper_svg") or "")) if wf.get("paper_svg") else None
        if svg and svg.lstrip().startswith("<?xml"):
            svg = svg[svg.index("?>") + 2:]
        wf["svg"] = svg
    out["n8n"] = n8n
    out["arch"] = load_json(os.path.join(ASSETS, "diagrams", "nodes.json"), None)
    q = QR(URL)
    decoded, ver, mask = qr_readback(q)
    assert decoded == URL, decoded
    out["qr"] = {"svg": q.svg(), "version": q.ver, "mask": q.mask, "ecc": "M", "text": URL,
                 "modules": q.size}
    js = "/* generated by build_data.py - do not edit by hand */\nwindow.DECK_DATA = " + \
        json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";\n"
    with open(os.path.join(HERE, "data.js"), "w", encoding="utf-8", newline="\n") as f:
        f.write(js)
    with open(os.path.join(HERE, "qr.svg"), "w", encoding="utf-8", newline="\n") as f:
        f.write(q.svg())
    print("data.js written: %d clips, %d call lines, %d screens, %d workflows, arch=%s, qr v%d mask %d readback=%s"
          % (len(out["audio"]), len(out["callTimeline"]), len(out["screens"]), len(n8n),
             bool(out["arch"]), ver, mask, decoded == URL))


if __name__ == "__main__":
    sys.exit(main())
