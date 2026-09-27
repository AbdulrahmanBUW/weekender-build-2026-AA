"""Build the demo walkthrough's audio mix and timing data.

Single source of truth for when things happen in the demo video.
Outputs:
  composition/data/timing.js          window.DEMO = {T, ivr, intake, call, nar_d7, total}
  composition/assets/audio/demo_mix.mp3  the full mix (speech + sfx; music off by default), about -16 LUFS
  build/demo_mix.wav                  same mix, lossless (used to remux the final mp4)
  composition/assets/screens/*.png    the screenshots the composition uses (+ crops)

Only standard library + numpy + Pillow. No keys needed (all audio already exists in docs/launch/audio).
Run from anywhere:  python build_demo.py
"""
import json
import os
import shutil
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LAUNCH = os.path.normpath(os.path.join(HERE, "..", ".."))
AUDIO = os.path.join(LAUNCH, "audio")
SCREENS = os.path.join(LAUNCH, "assets", "screens")
FONTS = os.path.join(LAUNCH, "assets", "fonts")
VENDOR = os.path.join(LAUNCH, "assets", "vendor")
REPO = os.path.normpath(os.path.join(LAUNCH, "..", ".."))
BRAG = os.path.join(REPO, ".claude", "skills", "brag", "assets")
COMP = os.path.join(HERE, "composition")
BUILD = os.path.join(HERE, "build")
SR = 48000

# ---------------------------------------------------------------- timeline (seconds, video time)
T = {}
T["ivr"] = 0.25            # ivr_de starts
T["ivr_fade"] = 7.0        # ivr fades out 7.0 -> 7.9
T["ivr_end"] = 7.9
T["maria"] = 7.4           # Maria card visual in
T["nar_d1"] = 7.9
T["home"] = 12.1           # home screen visual in
T["nar_d2"] = 12.5
T["courses"] = 15.3        # navigate to courses
T["provider"] = 17.9       # navigate to provider page
T["nar_d3"] = 18.6
T["lift"] = 19.9           # Call-for-me button lifts
T["press1"] = 20.7         # button press (click)
T["ask"] = 21.2            # ask page in
T["press_mic"] = 22.2      # mic press (click)
T["intake_screen"] = 22.55
T["intake"] = 22.9         # intake_full.mp3 starts
T["approval"] = 47.4       # approval card visual in
T["nar_d4"] = 47.8
T["tick"] = 52.4           # consent tick (click)
T["press2"] = 53.3         # "call now" press (click)
T["call_screen"] = 53.8    # live-call screen in
T["nar_d5"] = 54.2
T["ring"] = 58.0           # ringback tone 58.0 -> 59.0
T["pickup"] = 59.35
T["call"] = 59.6           # call_full.mp3 starts
CALL_CUT = 54.95           # play call_full up to here (after line 07 "Ja, genau so.")
T["call_end"] = T["call"] + CALL_CUT
T["result"] = T["call_end"] + 0.55   # result card in (chime)
T["nar_d6a"] = T["result"] + 0.6     # nar_d6 0.00-2.20 "The answer comes back in Russian."
NAR6_SPLIT = 2.20
T["result_ru"] = T["nar_d6a"] + NAR6_SPLIT + 0.4
T["addcal"] = T["result_ru"] + 9.52 - 0.1  # add-to-calendar press (click)
T["nar_d6b"] = T["result_ru"] + 9.52 + 0.45  # nar_d6 2.20-9.04
T["badge_page"] = T["nar_d6b"] + (5.22 - NAR6_SPLIT) - 0.2  # "And the course page now shows"
T["badge_hit"] = T["nar_d6b"] + (7.775 - NAR6_SPLIT)       # "checked by phone"
T["outro"] = T["nar_d6b"] + (9.04 - NAR6_SPLIT) + 0.35
T["nar_d7"] = T["outro"] + 0.3
T["endcard"] = T["nar_d7"] + 8.96 + 0.2
TOTAL = round(T["endcard"] + 4.2, 2)
T["total"] = TOTAL
IVR_SEGS = [(0.0, 1.70), (5.55, 7.40), (9.90, 11.77)]  # cut points sit in pauses (energy checked)
IVR_TEMPO = 1.1
IVR_WORDS = []
USE_MUSIC = False  # brief 2: all audio from Deepgram/ElevenLabs; the bundled brag track needs a licence check


def ffdecode(path, af=None):
    cmd = ["ffmpeg", "-v", "error", "-i", path]
    if af:
        cmd += ["-af", af]
    cmd += ["-f", "f32le", "-ac", "1", "-ar", str(SR), "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def db(x):
    return 10 ** (x / 20.0)


def place(bus, clip, t, gain=1.0):
    i = int(round(t * SR))
    j = min(len(bus), i + len(clip))
    bus[i:j] += clip[: j - i] * gain


def load_json(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def main():
    os.makedirs(BUILD, exist_ok=True)
    os.makedirs(os.path.join(COMP, "assets", "audio"), exist_ok=True)
    os.makedirs(os.path.join(COMP, "data"), exist_ok=True)
    n = int(TOTAL * SR) + SR
    speech = np.zeros(n, np.float32)
    sfx = np.zeros(n, np.float32)
    music = np.zeros(n, np.float32)

    # --- speech
    # phone menu: greeting + "press one" + "all lines are busy", spliced at pauses and sped up 1.1x (brief 3.1)
    ivr_src = ffdecode(os.path.join(AUDIO, "ivr_de.mp3"), "highpass=f=300,lowpass=f=3400")
    parts, off = [], 0.0
    ivr_words = load_json(os.path.join(AUDIO, "ivr_de.words.json"))
    for a0, a1 in IVR_SEGS:
        seg = ivr_src[int(a0 * SR): int(a1 * SR)].copy()
        e = int(0.012 * SR)
        seg[:e] *= np.linspace(0, 1, e, dtype=np.float32)
        seg[-e:] *= np.linspace(1, 0, e, dtype=np.float32)
        parts.append(seg)
        for w in ivr_words:
            if a0 - 0.1 <= w["start"] < a1 - 0.1:
                IVR_WORDS.append({"w": w["w"], "start": (off + max(0.0, w["start"] - a0)) / IVR_TEMPO,
                                  "end": (off + min(a1 - a0, w["end"] - a0)) / IVR_TEMPO})
        off += a1 - a0
    spliced = os.path.join(BUILD, "ivr_spliced.wav")
    write_wav(spliced, np.concatenate(parts))
    ivr = ffdecode(spliced, f"atempo={IVR_TEMPO}")
    place(speech, ivr, T["ivr"], db(1.5))
    ivr_stop = T["ivr"] + len(ivr) / SR
    # the line is busy: German busy tone (425 Hz, 480 ms on / 480 ms off), two beeps
    t = np.arange(int(0.48 * SR)) / SR
    beep = (np.sin(2 * np.pi * 425 * t) * np.minimum(1, np.minimum(t / 0.01, (0.48 - t) / 0.015))).astype(np.float32)
    for kb in range(2):
        place(sfx, beep, ivr_stop + 0.3 + kb * 0.96, db(-24))

    for k in ["nar_d1", "nar_d2", "nar_d3", "nar_d4", "nar_d5", "nar_d7"]:
        place(speech, ffdecode(os.path.join(AUDIO, k + ".mp3")), T[k])
    n6 = ffdecode(os.path.join(AUDIO, "nar_d6.mp3"))
    s = int(NAR6_SPLIT * SR)
    a = n6[:s].copy()
    a[-int(0.03 * SR):] *= np.linspace(1, 0, int(0.03 * SR), dtype=np.float32)
    b = n6[s:].copy()
    b[: int(0.02 * SR)] *= np.linspace(0, 1, int(0.02 * SR), dtype=np.float32)
    place(speech, a, T["nar_d6a"])
    place(speech, b, T["nar_d6b"])

    place(speech, ffdecode(os.path.join(AUDIO, "intake_full.mp3")), T["intake"])
    call = ffdecode(os.path.join(AUDIO, "call_full.mp3"))[: int(CALL_CUT * SR)]
    call[-int(0.08 * SR):] *= np.linspace(1, 0, int(0.08 * SR), dtype=np.float32)
    place(speech, call, T["call"])
    place(speech, ffdecode(os.path.join(AUDIO, "result_ru.mp3")), T["result_ru"])

    # --- sfx
    click_p = os.path.join(BRAG, "sfx", "ui", "click2.ogg")
    click = ffdecode(click_p) if os.path.exists(click_p) else np.zeros(10, np.float32)
    click = click / (np.abs(click).max() + 1e-9)
    for k in ["press1", "press_mic", "tick", "press2", "addcal"]:
        place(sfx, click, T[k], db(-16))
    # German ringback tone: 425 Hz, 1 s on
    t = np.arange(int(1.0 * SR)) / SR
    ring = np.sin(2 * np.pi * 425 * t).astype(np.float32)
    env = np.minimum(1, np.minimum(t / 0.02, (1.0 - t) / 0.03)).astype(np.float32)
    place(sfx, ring * env, T["ring"], db(-22))
    # pickup: short soft click
    place(sfx, click, T["pickup"], db(-20))
    # soft confirm chime (two sine notes with decay)
    t = np.arange(int(1.2 * SR)) / SR
    def note(f, d):
        e = np.exp(-t * d) * np.minimum(1, t / 0.005)
        return (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t)) * e
    chime = np.zeros(int(1.4 * SR), np.float32)
    chime[: len(t)] += note(784.0, 5.5).astype(np.float32)
    off = int(0.11 * SR)
    chime[off: off + len(t)] += note(1174.7, 4.5).astype(np.float32)
    chime /= np.abs(chime).max()
    place(sfx, chime, T["result"] + 0.05, db(-19))

    # --- music (calm bundled track, ducked hard under speech, off during the call)
    mpath = os.path.join(LAUNCH, "audio", "music_demo.mp3")
    if not os.path.exists(mpath):
        mpath = os.path.join(BRAG, "music", "happy-beats-business-moves-vol-12-by-ende-dot-app.mp3")
    mus = ffdecode(mpath, "lowpass=f=9000")
    seg_a = (T["nar_d1"] - 0.6, T["call_screen"] + 2.4)      # in after the hook, out before the ring
    seg_b = (T["result"] - 0.2, TOTAL)
    ma = mus[: int((seg_a[1] - seg_a[0]) * SR)].copy()
    place(music, ma, seg_a[0])
    lb = int((seg_b[1] - seg_b[0]) * SR)
    start_b = max(0, len(mus) - lb - int(1.0 * SR))
    place(music, mus[start_b: start_b + lb].copy(), seg_b[0])

    # music gain envelope: base level in gaps, ducked under speech (speech detector with attack/release)
    hop = int(0.01 * SR)
    frames = n // hop
    sp = speech[: frames * hop].reshape(frames, hop)
    rms = np.sqrt((sp ** 2).mean(axis=1) + 1e-12)
    active = (20 * np.log10(rms) > -45).astype(np.float32)
    # hold speech-active for 0.35 s and pre-open 0.15 s
    held = active.copy()
    for k in range(1, 36):
        held[k:] = np.maximum(held[k:], active[:-k])
    for k in range(1, 16):
        held[:-k] = np.maximum(held[:-k], active[k:])
    target_db = np.where(held > 0, -27.0, -17.0)  # music level relative to its own level
    ec = int((T["endcard"] + 0.3) * 100)
    target_db[ec:] = np.where(held[ec:] > 0, -27.0, -10.0)  # end card: music carries the last seconds
    g = np.zeros(frames)
    cur = target_db[0]
    for i in range(frames):
        tgt = target_db[i]
        rate = 0.35 if tgt < cur else 0.08  # dB per 10 ms: fast duck, slow release
        cur = max(tgt, cur - rate * 10) if tgt < cur else min(tgt, cur + rate * 3)
        g[i] = cur
    gain = np.repeat(db(g), hop)
    gain = np.concatenate([gain, np.full(n - len(gain), gain[-1])]).astype(np.float32)
    # segment fades
    def ramp(t0, t1, up):
        i0, i1 = int(t0 * SR), int(t1 * SR)
        r = np.linspace(0, 1, i1 - i0, dtype=np.float32)
        return i0, i1, (r if up else 1 - r)
    fadeenv = np.zeros(n, np.float32)
    for (s0, s1) in (seg_a, seg_b):
        i0, i1 = int(s0 * SR), min(n, int(s1 * SR))
        fadeenv[i0:i1] = 1
    for t0, t1, up in [(seg_a[0], seg_a[0] + 1.5, True), (seg_a[1] - 2.2, seg_a[1], False),
                       (seg_b[0], seg_b[0] + 1.2, True), (TOTAL - 2.5, TOTAL - 0.2, False)]:
        i0, i1, r = ramp(t0, t1, up)
        fadeenv[i0:i1] *= r
    fadeenv[int((TOTAL - 0.2) * SR):] = 0
    # a little lift on the end card (no speech there)
    music *= gain * fadeenv
    if not USE_MUSIC:
        music[:] = 0

    mix = speech + sfx + music
    raw_wav = os.path.join(BUILD, "mix_raw.wav")
    write_wav(raw_wav, mix[: int(TOTAL * SR)])

    # loudness: measure, gain to -16 LUFS, true-peak limit at -1.5 dBTP
    I = measure_lufs(raw_wav)
    gdb = -16.0 - I
    final_wav = os.path.join(BUILD, "demo_mix.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw_wav, "-af",
                    f"volume={gdb:.2f}dB,alimiter=limit=0.84:attack=3:release=60:level=disabled",
                    "-ac", "2", "-ar", str(SR), "-c:a", "pcm_s16le", final_wav], check=True)
    I2 = measure_lufs(final_wav)
    mp3 = os.path.join(COMP, "assets", "audio", "demo_mix.mp3")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", final_wav, "-c:a", "libmp3lame", "-b:a", "256k", mp3], check=True)
    print(f"mix: raw {I:.1f} LUFS -> gain {gdb:+.1f} dB -> {I2:.1f} LUFS; total {TOTAL:.2f}s")

    # speech envelope at 30 fps (0..1), drives the speaking bars / waveform
    fps = 30
    hopv = SR // fps
    fr = int(TOTAL * fps)
    sp = speech[: fr * hopv].reshape(fr, hopv)
    r = np.sqrt((sp ** 2).mean(axis=1) + 1e-12)
    d = 20 * np.log10(r)
    env = np.clip((d + 50) / 36.0, 0, 1)
    ENV[:] = [round(float(v), 2) for v in env]

    copy_assets()
    write_timing()


def write_wav(path, x):
    x = np.clip(x, -1, 1)
    pcm = (x * 32767).astype("<i2").tobytes()
    import wave
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm)


def measure_lufs(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    I = None
    for line in r.stderr.splitlines():
        line = line.strip()
        if line.startswith("I:") and "LUFS" in line:
            I = float(line.split()[1])
    return I


ENV = []
APPROVAL = {}


def write_timing():
    call = load_json(os.path.join(AUDIO, "call_full.timeline.json"))
    call = [c for c in call if c["start"] < CALL_CUT]
    intake = load_json(os.path.join(AUDIO, "intake_full.timeline.json"))
    ivr = IVR_WORDS
    d7 = load_json(os.path.join(AUDIO, "nar_d7.words.json"))
    def slim(words):
        return [{"w": w["w"], "s": round(w["start"], 3), "e": round(w["end"], 3)} for w in words]
    data = {
        "T": {k: round(v, 3) for k, v in T.items()},
        "ivr": slim(ivr),
        "intake": [{"id": e["id"], "speaker": e["speaker"], "s": e["start"], "e": e["end"], "ru": e["ru"],
                    "words": slim(e["words"])} for e in intake],
        "call": [{"id": e["id"], "speaker": e["speaker"], "s": e["start"], "e": e["end"], "de": e["de"], "ru": e["ru"],
                  "words": slim(e["words"])} for e in call],
        "nar_d7": slim(d7),
        "nar_d1": slim(load_json(os.path.join(AUDIO, "nar_d1.words.json"))),
        "nar_d4": slim(load_json(os.path.join(AUDIO, "nar_d4.words.json"))),
        "result_ru": slim(load_json(os.path.join(AUDIO, "result_ru.words.json"))),
        "env": ENV,
        "approval": APPROVAL,
    }
    with open(os.path.join(COMP, "data", "timing.js"), "w", encoding="utf-8") as f:
        f.write("// generated by ../build_demo.py - do not edit by hand\n")
        f.write("window.DEMO = " + json.dumps(data, ensure_ascii=False) + ";\n")


def copy_assets():
    from PIL import Image
    dst = os.path.join(COMP, "assets", "screens")
    os.makedirs(dst, exist_ok=True)
    for name in ["desktop-home-ru.png", "desktop-courses-ru.png", "desktop-provider-ru.png", "desktop-ask-ru.png",
                 "crop-approval-ru.png", "full-provider-ru.png"]:
        shutil.copy2(os.path.join(SCREENS, name), os.path.join(dst, name))
    # approval card: remove the app's keyboard-focus outline around the heading (pine 6 px frame)
    im = Image.open(os.path.join(SCREENS, "crop-approval-ru.png")).convert("RGB")
    px = im.load()
    W, H = im.size
    bg = px[40, 110]
    for y in range(60, 170):
        for x in range(60, W - 60):
            p = px[x, y]
            if abs(p[0] - 31) < 14 and abs(p[1] - 91) < 14 and abs(p[2] - 73) < 14:
                px[x, y] = bg
    def bbox(x0, y0, x1, y1, pred):
        xs, ys = [], []
        for y in range(y0, y1):
            for x in range(x0, x1):
                if pred(px[x, y]):
                    xs.append(x); ys.append(y)
        return [min(xs), min(ys), max(xs) + 1, max(ys) + 1] if xs else None
    APPROVAL["w"], APPROVAL["h"] = W, H
    APPROVAL["check"] = bbox(60, 2040, 180, 2180, lambda p: p == (255, 255, 255))
    APPROVAL["button"] = bbox(50, 2420, 480, 2620, lambda p: abs(p[0] - p[1]) > 12 and p[1] > 120 and p[1] < 190 and p[0] < 170)
    im.save(os.path.join(dst, "approval-ru-clean.png"))
    # header band (0-100 css px) of the ask page, reused on the recreated intake / call screens
    im = Image.open(os.path.join(SCREENS, "desktop-ask-ru.png"))
    im.crop((0, 0, 2880, 202)).save(os.path.join(dst, "header-ru.png"))
    fdst = os.path.join(COMP, "assets", "fonts")
    os.makedirs(fdst, exist_ok=True)
    for f in os.listdir(FONTS):
        if f.endswith(".woff2"):
            shutil.copy2(os.path.join(FONTS, f), os.path.join(fdst, f))
    vdst = os.path.join(COMP, "assets", "vendor")
    os.makedirs(vdst, exist_ok=True)
    shutil.copy2(os.path.join(VENDOR, "gsap.min.js"), os.path.join(vdst, "gsap.min.js"))


if __name__ == "__main__":
    main()
