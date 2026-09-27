#!/usr/bin/env python3
"""Make every audio clip of docs/launch/PRODUCTION.md section 3 (Ankommen launch kit).

Providers: Deepgram (aura-2 TTS, nova-3 STT) and ElevenLabs (TTS with timestamps, optional SFX/music).
Keys are read at runtime from services/voice-relay/.env (DEEPGRAM_API_KEY, ELEVENLABS_API_KEY) and are
never printed, logged or written anywhere.

Outputs (docs/launch/audio/):
  <id>.mp3               trimmed (<= 80 ms silence), ~-16 LUFS, 44.1 kHz mono mp3
  <id>_phone.mp3         receptionist lines only: telephone band (300-3400 Hz), light compression, ~-19 LUFS
  <id>.words.json        [{"w","start","end"}] in seconds on the final file
  call_full.mp3 / call_full.timeline.json      the nine call lines, receptionist in the phone version
  intake_full.mp3 / intake_full.timeline.json  the four Russian voice-intake lines
  manifest.json          one entry per file
  raw/                   API output + alignment + per-clip meta (lets you re-run post-processing without API calls)

Usage:
  python scripts/launch/make_audio.py              # make everything that is missing (idempotent)
  python scripts/launch/make_audio.py --force      # regenerate everything (costs API characters)
  python scripts/launch/make_audio.py --only call_02_a,nar_l6 [--force]
  python scripts/launch/make_audio.py --test       # one clip per provider
  python scripts/launch/make_audio.py --no-extras  # skip ElevenLabs SFX / music attempts
  python scripts/launch/make_audio.py --rebuild    # re-run post-processing from raw/ (no TTS calls)
Stdlib only (urllib, json, base64, subprocess, wave, difflib). Needs ffmpeg + ffprobe on PATH.
"""
import argparse
import base64
import difflib
import json
import random
import re
import subprocess
import sys
import threading
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import wave
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[2]
AUDIO = ROOT / "docs" / "launch" / "audio"
RAW = AUDIO / "raw"
ENV_FILE = ROOT / "services" / "voice-relay" / ".env"
UA = "ankommen-launch-audio/1.0"
SR = 44100
LOCK = threading.Lock()
EL_CHARS = {"n": 0}
WER_LIMIT = 0.25
STT_UNSUPPORTED = set()  # (model, lang) pairs Deepgram rejected

DG, EL = "deepgram", "elevenlabs"
SARAH = "EXAVITQu4vr4xnSDxMaL"
JESSICA, LAURA = "cgSgspJ2msm6clMCkdW9", "FGY2VhQYpPwHp6x1f3ZJ"
GEORGE, ALICE = "JBFqnCBsd6RMkjVDRZzb", "Xb7hH8MSUJpSbSDYk0k2"
VOICE_NAMES = {SARAH: "Sarah", JESSICA: "Jessica", LAURA: "Laura", GEORGE: "George", ALICE: "Alice"}


def log(*a):
    with LOCK:
        print(*a, flush=True)


def clip(cid, provider, voice, lang, text, subtitle=None, fallback=None, speaker=None, group=None, **kw):
    d = dict(id=cid, provider=provider, voice=voice, lang=lang, text=text, subtitle=subtitle,
             fallback=fallback, speaker=speaker, group=group)
    d.update(kw)
    return d


# ---------------------------------------------------------------- script (PRODUCTION.md section 3, verbatim)
# check_text = how the line is expected to sound (for the speech-to-text back-check only)
# wer_ignore = brand words the recogniser transliterates (not counted as errors)
BRAND_OLGA = ["Olgas", "Musikstudio"]
CLIPS = [
    # 3.1 problem beat
    clip("ivr_de", DG, "aura-2-aurelia-de", "de",
         "Herzlich willkommen im Musikstudio. Unsere Bürozeiten: Montag bis Donnerstag, neun bis zwölf Uhr. "
         "Für Anmeldungen drücken Sie die Eins. Für Fragen zu Kursgebühren drücken Sie die Zwei. "
         "Alle Leitungen sind zurzeit belegt.",
         speaker="ivr", group="problem", speed=1.1),
    # 3.2 voice intake
    clip("intake_ru_1", EL, SARAH, "ru",
         "Здравствуйте! Я позвоню за вас в Olgas Musikstudio. Что мне у них спросить?",
         speaker="assistant", group="intake", wer_ignore=BRAND_OLGA),
    clip("maria_ru_1", EL, JESSICA, "ru",
         "Здравствуйте! Я хочу записать дочку на музыку. Ей четыре года. Лучше во вторник или в четверг, после трёх.",
         fallback=LAURA, speaker="parent", group="intake"),
    clip("intake_ru_2", EL, SARAH, "ru",
         "Поняла. Я спрошу про свободное место или пробный урок во вторник или в четверг после 15:00. "
         "Позвонить им на немецком?",
         speaker="assistant", group="intake"),
    clip("maria_ru_2", EL, JESSICA, "ru", "Да, позвоните, пожалуйста.",
         fallback=LAURA, speaker="parent", group="intake"),
    # 3.3 the call
    clip("call_01_r", DG, "aura-2-julius-de", "de", "Musikstudio Olga, Böhme, guten Tag?",
         subtitle="«Музыкальная студия Ольги, Бёме, добрый день?»", speaker="receptionist", group="call"),
    clip("call_02_a", DG, "aura-2-viktoria-de", "de",
         "Guten Tag! Hier ist die KI-Assistentin von Maria Petrova. Ich rufe für sie an, weil ihr Deutsch noch "
         "nicht so gut ist, und wollte fragen, ob es in Ihrem Kurs für ein vierjähriges Kind noch einen Platz "
         "oder eine Probestunde gibt.",
         subtitle="«Добрый день! Это ИИ-ассистент Марии Петровой. Я звоню за неё, потому что она пока плохо "
                  "говорит по-немецки, и хотела спросить, есть ли место или пробный урок для ребёнка четырёх лет.»",
         speaker="assistant", group="call"),
    clip("call_03_r", DG, "aura-2-julius-de", "de",
         "Nu, da haben Sie Glück. Die Früherziehung für Vier- bis Sechsjährige ist dienstags und donnerstags um "
         "halb fünf. Ich könnte Ihnen aber auch Samstag früh um zehn anbieten.",
         subtitle="«Вам повезло. Занятия для детей 4–6 лет по вторникам и четвергам в 16:30. "
                  "Могу предложить и субботу в 10 утра.»",
         speaker="receptionist", group="call"),
    clip("call_04_a", DG, "aura-2-viktoria-de", "de",
         "Danke! Samstag passt leider nicht, Frau Petrova kann nur dienstags oder donnerstags ab fünfzehn Uhr. "
         "Geht eine Probestunde am Donnerstag um sechzehn Uhr dreißig?",
         subtitle="«Спасибо! Суббота, к сожалению, не подходит: госпожа Петрова может только во вторник или "
                  "четверг после 15:00. Можно пробный урок в четверг в 16:30?»",
         speaker="assistant", group="call"),
    clip("call_05_r", DG, "aura-2-julius-de", "de",
         "Donnerstag, halb fünf, das geht. Die Probestunde ist kostenlos. Bringen Sie bitte Hausschuhe mit.",
         subtitle="«Четверг, 16:30, подходит. Пробный урок бесплатный. Возьмите, пожалуйста, сменную обувь.»",
         speaker="receptionist", group="call"),
    clip("call_06_a", DG, "aura-2-viktoria-de", "de",
         "Ich wiederhole: Probestunde am Donnerstag, dem ersten Oktober, um sechzehn Uhr dreißig, kostenlos, "
         "bitte Hausschuhe mitbringen. Ist das richtig?",
         subtitle="«Повторяю: пробный урок в четверг, 1 октября, в 16:30, бесплатно, взять сменную обувь. Всё верно?»",
         speaker="assistant", group="call"),
    clip("call_07_r", DG, "aura-2-julius-de", "de", "Ja, genau so.",
         subtitle="«Да, именно так.»", speaker="receptionist", group="call"),
    clip("call_08_a", DG, "aura-2-viktoria-de", "de",
         "Wunderbar, ich notiere das. Vielen Dank, Herr Böhme, und auf Wiederhören!",
         subtitle="«Отлично, записываю. Большое спасибо, господин Бёме, до свидания!»",
         speaker="assistant", group="call"),
    clip("call_09_r", DG, "aura-2-julius-de", "de", "Gerne, auf Wiederhören.",
         subtitle="«Пожалуйста, до свидания.»", speaker="receptionist", group="call"),
    # 3.4 result
    clip("result_ru", EL, SARAH, "ru",
         "Готово! Пробный урок в Olgas Musikstudio: четверг, 1 октября, в 16:30. Урок бесплатный. "
         "Возьмите с собой сменную обувь.",
         speaker="assistant", group="result", wer_ignore=BRAND_OLGA),
    # 3.5 six languages
    clip("lang_en", DG, "aura-2-helena-en", "en",
         "I'll call them in German for you, and tell you the answer in English.", speaker="assistant", group="lang"),
    clip("lang_de", DG, "aura-2-viktoria-de", "de",
         "Ich rufe für Sie an und sage Ihnen gleich, was sie gesagt haben.", speaker="assistant", group="lang"),
    clip("lang_ru", EL, SARAH, "ru", "Я позвоню за вас на немецком и расскажу ответ по-русски.",
         speaker="assistant", group="lang"),
    clip("lang_uk", EL, SARAH, "uk", "Я зателефоную замість вас німецькою і розповім відповідь українською.",
         speaker="assistant", group="lang"),
    clip("lang_ar", EL, SARAH, "ar", "سأتصل بهم بالألمانية نيابةً عنك، وأخبرك بالجواب بالعربية.",
         speaker="assistant", group="lang"),
    clip("lang_tr", EL, SARAH, "tr", "Sizin yerinize Almanca arayacağım ve cevabı size Türkçe söyleyeceğim.",
         speaker="assistant", group="lang"),
    # alternate (not in the brief): English line in the ElevenLabs Sarah voice, in case the team drops Helena
    clip("lang_en_sarah", EL, SARAH, "en",
         "I'll call them in German for you, and tell you the answer in English.", speaker="assistant", group="lang-alt"),
    # 3.6 launch narration
    clip("nar_l1", EL, GEORGE, "en", "She found the right music course for her daughter.", fallback=ALICE,
         speaker="narrator", group="launch"),
    clip("nar_l2", EL, GEORGE, "en", "Then the page said: call us. In German.", fallback=ALICE,
         speaker="narrator", group="launch"),
    clip("nar_l3", EL, GEORGE, "en", "Ankommen. Your guide to starting in Germany.", fallback=ALICE,
         speaker="narrator", group="launch", wer_ignore=["Ankommen"]),
    clip("nar_l4", EL, GEORGE, "en", "Courses, events and help, in six languages.", fallback=ALICE,
         speaker="narrator", group="launch"),
    clip("nar_l5", EL, GEORGE, "en",
         "And when a call in German is needed: Call for me. It says it is an AI, makes the call, and brings the "
         "answer back in your language.", fallback=ALICE, speaker="narrator", group="launch"),
    clip("nar_l6", EL, GEORGE, "en", "ankommen-dresden.lovable.app", fallback=ALICE, speaker="narrator",
         group="launch", check_text="ankommen dresden dot lovable dot app", wer_ignore=["ankommen"]),
    # 3.7 demo narration
    clip("nar_d1", EL, GEORGE, "en", "This is Maria. She is new in Dresden, and she speaks Russian.", fallback=ALICE,
         speaker="narrator", group="demo"),
    clip("nar_d2", EL, GEORGE, "en", "Ankommen shows her courses, events and help in her own language.",
         fallback=ALICE, speaker="narrator", group="demo", wer_ignore=["Ankommen"]),
    clip("nar_d3", EL, GEORGE, "en", "She taps Call for me, and just says what she needs.", fallback=ALICE,
         speaker="narrator", group="demo"),
    clip("nar_d4", EL, GEORGE, "en",
         "Before anything happens, she sees what the assistant will say in German. She approves.", fallback=ALICE,
         speaker="narrator", group="demo"),
    clip("nar_d5", EL, GEORGE, "en", "Now the assistant calls. Listen to the first sentence.", fallback=ALICE,
         speaker="narrator", group="demo"),
    clip("nar_d6", EL, GEORGE, "en",
         "The answer comes back in Russian. No audio is stored, only text. And the course page now shows: "
         "checked by phone.", fallback=ALICE, speaker="narrator", group="demo"),
    clip("nar_d7", EL, GEORGE, "en",
         "Ankommen. Built this weekend in Dresden with Lovable, n8n, Supabase, Deepgram, ElevenLabs and Claude.",
         fallback=ALICE, speaker="narrator", group="demo", wer_ignore=["Ankommen", "Supabase"],
         check_text="Ankommen. Built this weekend in Dresden with Lovable, n eight n, Supabase, Deepgram, "
                    "Eleven Labs and Claude."),
]
BY_ID = {c["id"]: c for c in CLIPS}

CALL_SEQ = ["call_01_r", "call_02_a", "call_03_r", "call_04_a", "call_05_r",
            "call_06_a", "call_07_r", "call_08_a", "call_09_r"]
# pause BEFORE each line (s); a bit longer before replies that need thinking
CALL_GAPS = [0.0, 0.45, 0.6, 0.55, 0.5, 0.5, 0.4, 0.45, 0.35]
INTAKE_SEQ = ["intake_ru_1", "maria_ru_1", "intake_ru_2", "maria_ru_2"]
INTAKE_GAPS = [0.0, 0.6, 0.55, 0.5]

SFX = [
    ("phone_ring", "a modern German landline phone ringing twice, clean, close", 4.0),
    ("ui_click", "soft short UI tap, paper, subtle", 0.5),
    ("whoosh_soft", "very soft short air whoosh for a slide transition", 1.0),
    ("confirm_chime", "warm gentle two-note confirmation chime", 1.5),
]
MUSIC = [
    ("music_launch", "warm, hopeful, light acoustic guitar and soft piano, modern, 100 bpm, no vocals, clean ending", 26000),
    ("music_demo", "calm, warm, minimal piano and soft pads, gentle pulse, no vocals, suitable under dialogue", 110000),
]


# ---------------------------------------------------------------- keys + http
def load_keys():
    keys = {}
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("export "):
            line = line[7:]
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip(), v.strip().strip('"').strip("'")
        if k in ("DEEPGRAM_API_KEY", "ELEVENLABS_API_KEY") and v:
            keys[k] = v
    missing = {"DEEPGRAM_API_KEY", "ELEVENLABS_API_KEY"} - set(keys)
    if missing:
        sys.exit(f"missing in services/voice-relay/.env: {', '.join(sorted(missing))}")
    return keys


class ApiError(Exception):
    def __init__(self, status, body):
        self.status, self.body = status, body
        super().__init__(f"HTTP {status}: {body[:240]}")


def http_post(url, body, headers, timeout=240, tries=6):
    last = None
    for attempt in range(tries):
        req = urllib.request.Request(url, data=body, headers={"User-Agent": UA, **headers}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read(), r.headers.get("Content-Type", "")
        except urllib.error.HTTPError as e:
            data = e.read().decode("utf-8", "replace")
            if e.code == 429 or e.code >= 500:
                wait = min(40, 2 ** attempt) + random.random()
                ra = e.headers.get("Retry-After")
                if ra and ra.strip().isdigit():
                    wait = max(wait, float(ra))
                log(f"    HTTP {e.code}, retry in {wait:.1f}s")
                last = ApiError(e.code, data)
                time.sleep(wait)
                continue
            raise ApiError(e.code, data)
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:
            wait = min(40, 2 ** attempt) + random.random()
            log(f"    network {type(e).__name__}, retry in {wait:.1f}s")
            last = e
            time.sleep(wait)
    raise last


# ---------------------------------------------------------------- providers
def dg_speak(key, voice, text, speed=None):
    q = {"model": voice, "encoding": "linear16", "container": "wav", "sample_rate": "24000"}
    if speed:
        q["speed"] = str(speed)
    url = "https://api.deepgram.com/v1/speak?" + urllib.parse.urlencode(q)
    data, ct = http_post(url, json.dumps({"text": text}).encode("utf-8"),
                         {"Authorization": f"Token {key}", "Content-Type": "application/json"})
    if "json" in ct:
        raise ApiError(200, data.decode("utf-8", "replace"))
    return data


def dg_listen(key, path, lang, smart=False):
    """Returns (model, transcript, words) or None if no model supports the language."""
    for model in ("nova-3", "nova-2"):
        if (model, lang) in STT_UNSUPPORTED:
            continue
        q = {"model": model, "language": lang, "punctuate": "true"}
        if smart:
            q["smart_format"] = "true"
        url = "https://api.deepgram.com/v1/listen?" + urllib.parse.urlencode(q)
        try:
            data, _ = http_post(url, Path(path).read_bytes(),
                                {"Authorization": f"Token {key}", "Content-Type": "audio/mpeg"})
        except ApiError as e:
            if e.status in (400, 422):
                with LOCK:
                    STT_UNSUPPORTED.add((model, lang))
                continue
            raise
        alt = json.loads(data)["results"]["channels"][0]["alternatives"][0]
        words = [{"w": w.get("punctuated_word") or w["word"], "start": float(w["start"]), "end": float(w["end"])}
                 for w in alt.get("words", [])]
        return model, alt.get("transcript", ""), words
    return None


def el_request(key, voice_id, text, model, lang=None, timestamps=True):
    base = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    url = base + ("/with-timestamps" if timestamps else "") + "?output_format=mp3_44100_128"
    body = {"text": text, "model_id": model}
    if lang:
        body["language_code"] = lang
    if model == "eleven_multilingual_v2":
        body["voice_settings"] = {"stability": 0.45, "similarity_boost": 0.8, "style": 0.2, "use_speaker_boost": True}
    with LOCK:
        EL_CHARS["n"] += len(text)
    data, ct = http_post(url, json.dumps(body).encode("utf-8"),
                         {"xi-api-key": key, "Content-Type": "application/json",
                          "Accept": "application/json" if timestamps else "audio/mpeg"})
    if not timestamps:
        if "json" in ct:
            raise ApiError(200, data.decode("utf-8", "replace"))
        return data, None
    j = json.loads(data)
    return base64.b64decode(j["audio_base64"]), (j.get("alignment") or j.get("normalized_alignment"))


def el_generate(key, c, prefer="eleven_v3"):
    """Try preferred model (with/without language_code, with/without timestamps), then the other model,
    then the fallback voice. Returns (audio, alignment, info)."""
    voices = [c["voice"]] + ([c["fallback"]] if c.get("fallback") else [])
    models = [prefer] + [m for m in ("eleven_v3", "eleven_multilingual_v2") if m != prefer]
    errors = []
    for vid in voices:
        voice_missing = False
        for model in models:
            attempts = [(c["lang"], True), (None, True), (None, False)] if model == "eleven_v3" else [(None, True), (None, False)]
            for lc, ts in attempts:
                try:
                    audio, al = el_request(key, vid, c.get("tts_text", c["text"]), model, lc, ts)
                    return audio, al, {"voice": vid, "voice_name": VOICE_NAMES.get(vid, vid), "model": model,
                                       "language_code": lc, "timestamps": bool(al), "errors": errors}
                except ApiError as e:
                    errors.append(f"{VOICE_NAMES.get(vid, vid)}/{model}/lc={lc}/ts={ts}: {e.status} {e.body[:160]}")
                    b = e.body.lower()
                    if e.status == 401 and ("quota" in b or "credits" in b):
                        raise
                    if e.status == 404 and "voice" in b:
                        voice_missing = True
                        break
            if voice_missing:
                break
    raise RuntimeError("ElevenLabs failed: " + " | ".join(errors[-4:]))


# ---------------------------------------------------------------- text + timing helpers
ARABIC_FOLD = str.maketrans({"ة": "ه", "ى": "ي", "ٱ": "ا"})


def norm_tokens(text):
    t = unicodedata.normalize("NFD", unicodedata.normalize("NFKC", text).lower())
    t = "".join(ch for ch in t if unicodedata.category(ch) != "Mn").translate(ARABIC_FOLD)
    return re.findall(r"[^\W_]+", t)


def wer(ref, hyp, ignore=()):
    """Word error rate. `ignore` = brand words (e.g. Olgas Musikstudio) whose transliteration by the
    recogniser must not count as an error."""
    r, h = norm_tokens(ref), norm_tokens(hyp)
    if not r:
        return 0.0
    ign = {t for x in ignore for t in norm_tokens(x)}
    if ign:
        errs, real_total = 0, sum(1 for t in r if t not in ign)
        for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, r, h, autojunk=False).get_opcodes():
            span = r[i1:i2]
            real = [t for t in span if t not in ign]
            if tag == "insert":
                near = (i1 > 0 and r[i1 - 1] in ign) or (i1 < len(r) and r[i1] in ign)
                errs += 0 if near else j2 - j1
            elif tag == "delete":
                errs += len(real)
            elif tag == "replace":
                errs += max(len(span), j2 - j1) if len(real) == len(span) else len(real)
        return errs / max(1, real_total)
    prev = list(range(len(h) + 1))
    for i in range(1, len(r) + 1):
        cur = [i] + [0] * len(h)
        for j in range(1, len(h) + 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (r[i - 1] != h[j - 1]))
        prev = cur
    return prev[-1] / len(r)


def words_from_alignment(al):
    words, cur, s, e = [], "", 0.0, 0.0
    for ch, a, b in zip(al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]):
        if ch.isspace():
            if cur:
                words.append({"w": cur, "start": s, "end": e})
                cur = ""
            continue
        if not cur:
            s = a
        cur += ch
        e = b
    if cur:
        words.append({"w": cur, "start": s, "end": e})
    return words


def spread(tokens, t0, t1):
    """Distribute [t0, t1] over tokens by character length."""
    t1 = max(t1, t0)
    weights = [max(1, len(t)) for t in tokens]
    total, acc, out = sum(weights), 0, []
    for w in weights:
        a = t0 + (t1 - t0) * acc / total
        acc += w
        out.append((a, t0 + (t1 - t0) * acc / total))
    return out


def align_script(script, rec, length):
    """Script words (exact text for captions) with timings taken from recognised words."""
    toks = script.split()
    if not rec:
        return [{"w": t, "start": a, "end": b} for t, (a, b) in zip(toks, spread(toks, 0.0, length))]
    ns = [" ".join(norm_tokens(t)) for t in toks]
    nr = [" ".join(norm_tokens(w["w"])) for w in rec]
    out = [None] * len(toks)
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, ns, nr, autojunk=False).get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                out[i1 + k] = (rec[j1 + k]["start"], rec[j1 + k]["end"])
        elif tag == "replace":
            for k, ab in enumerate(spread(toks[i1:i2], rec[j1]["start"], rec[j2 - 1]["end"])):
                out[i1 + k] = ab
    i = 0
    while i < len(toks):
        if out[i] is not None:
            i += 1
            continue
        j = i
        while j < len(toks) and out[j] is None:
            j += 1
        t0 = out[i - 1][1] if i > 0 else max(0.0, rec[0]["start"] - 0.05 * (j - i))
        t1 = out[j][0] if j < len(toks) else min(length, rec[-1]["end"] + 0.25 * (j - i))
        for k, ab in enumerate(spread(toks[i:j], t0, t1)):
            out[i + k] = ab
        i = j
    res, last = [], 0.0
    for t, (a, b) in zip(toks, out):
        a = max(a, last)
        b = max(b, a + 0.02)
        res.append({"w": t, "start": round(min(a, length), 3), "end": round(min(b, length), 3)})
        last = a
    return res


# ---------------------------------------------------------------- ffmpeg
FF = ["ffmpeg", "-hide_banner", "-nostats", "-y"]


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode:
        raise RuntimeError(f"{cmd[0]} failed ({p.returncode}): {p.stderr[-1200:]}")
    return p


def probe_duration(path):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                      "-of", "default=nw=1:nk=1", str(path)]).stdout.strip())


def wav_len(path):
    with wave.open(str(path), "rb") as w:
        return w.getnframes() / w.getframerate()


_RUBBERBAND = {}


def has_rubberband():
    if "ok" not in _RUBBERBAND:
        out = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True,
                             encoding="utf-8", errors="replace").stdout
        _RUBBERBAND["ok"] = " rubberband " in out
    return _RUBBERBAND["ok"]


def to_prep_wav(src, dst, atempo=None):
    stretch = ""
    if atempo:
        stretch = (f"rubberband=tempo={atempo}:formant=preserved," if has_rubberband() else f"atempo={atempo},")
    chain = stretch + f"aresample={SR}"
    run(FF + ["-i", str(src), "-af", chain, "-ac", "1", "-c:a", "pcm_s16le", str(dst)])


def speech_bounds(wav, noise="-62dB", d=0.04):
    dur = wav_len(wav)
    err = run(FF + ["-i", str(wav), "-af", f"silencedetect=noise={noise}:d={d}", "-f", "null", "-"]).stderr
    # pair silence_start/silence_end in order; a silence running into EOF may have no end
    silences, cur = [], None
    for kind, val in re.findall(r"silence_(start|end): (-?[\d.]+)", err):
        if kind == "start":
            cur = max(0.0, float(val))
        elif cur is not None:
            silences.append((cur, float(val)))
            cur = None
    if cur is not None:
        silences.append((cur, dur))
    # sound = complement of silence; drop tiny codec blips (< 15 ms) so they do not count as speech
    sound, pos = [], 0.0
    for s, e in silences:
        if s > pos:
            sound.append((pos, s))
        pos = max(pos, e)
    if pos < dur:
        sound.append((pos, dur))
    # speech = first/last sound region of >= 80 ms; short regions right next to it (soft onsets, final
    # plosive releases, within 120 ms) are kept, isolated codec blips further away are dropped
    big = [i for i, (a, b) in enumerate(sound) if b - a >= 0.08]
    if not big:
        return 0.0, dur, dur
    i0, i1 = big[0], big[-1]
    while i0 > 0 and sound[i0][0] - sound[i0 - 1][1] <= 0.12:
        i0 -= 1
    while i1 < len(sound) - 1 and sound[i1 + 1][0] - sound[i1][1] <= 0.12:
        i1 += 1
    lead, tail = sound[i0][0], sound[i1][1]
    if tail - lead < 0.1:
        return 0.0, dur, dur
    return lead, tail, dur


def loudnorm_render(src, dst, chain, target, tp=-1.5, lra=11):
    """Loudness-normalise `src` (through `chain`) to `target` LUFS into a 44.1 kHz mono pcm wav.
    Pass 1 measures integrated loudness (EBU R128, same as loudnorm); pass 2 applies one static gain plus a
    delay-compensated peak limiter. Unlike loudnorm's dynamic mode this also hits the target on clips < 3 s
    and never changes timing."""
    pre = (chain + ",") if chain else ""
    err = run(FF + ["-i", str(src), "-af", f"{pre}loudnorm=I={target}:TP={tp}:LRA={lra}:print_format=json",
                    "-f", "null", "-"]).stderr
    gain = 0.0
    try:
        m = json.loads(re.findall(r"\{[^{}]*\}", err)[-1])
        if re.match(r"^-?\d", str(m["input_i"])):
            gain = max(-30.0, min(30.0, target - float(m["input_i"])))
    except (IndexError, ValueError, KeyError):
        pass
    limit = round(10 ** (tp / 20), 4)
    post = f"volume={gain:.2f}dB,alimiter=limit={limit}:attack=3:release=60:level=false:latency=true"
    run(FF + ["-i", str(src), "-af", f"{pre}{post},aresample={SR}", "-ac", "1", "-c:a", "pcm_s16le", str(dst)])


def encode_mp3(wav, mp3, bitrate="128k"):
    run(FF + ["-i", str(wav), "-c:a", "libmp3lame", "-b:a", bitrate, "-ar", str(SR), "-ac", "1", str(mp3)])


def trim_and_normalise(prep, final_wav, keep=0.07):
    lead, tail, dur = speech_bounds(prep)
    start, end = max(0.0, lead - keep), min(dur, tail + keep + 0.01)
    length = end - start
    chain = (f"atrim=start={start:.4f}:end={end:.4f},asetpts=PTS-STARTPTS,"
             f"afade=t=in:d=0.004,afade=t=out:st={max(0.0, length - 0.012):.4f}:d=0.012")
    loudnorm_render(prep, final_wav, chain, -16)
    return start, wav_len(final_wav)


def make_phone(final_wav, phone_wav, phone_mp3):
    chain = ("highpass=f=300,highpass=f=300,lowpass=f=3400,lowpass=f=3400,"
             "acompressor=threshold=0.125:ratio=3:attack=5:release=80:makeup=1")
    loudnorm_render(final_wav, phone_wav, chain, -19)
    encode_mp3(phone_wav, phone_mp3)


# ---------------------------------------------------------------- per clip
def paths(cid):
    return {
        "mp3": AUDIO / f"{cid}.mp3", "words": AUDIO / f"{cid}.words.json", "phone": AUDIO / f"{cid}_phone.mp3",
        "prep": RAW / f"{cid}.prep.wav", "final": RAW / f"{cid}.final.wav", "phone_wav": RAW / f"{cid}_phone.final.wav",
        "meta": RAW / f"{cid}.meta.json",
    }


def write_json(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def backcheck(dg_key, c, mp3):
    lang = c["lang"]
    res = dg_listen(dg_key, mp3, lang, smart=bool(re.search(r"\d", c["text"])))
    if res is None:
        return None
    model, transcript, words = res
    return {"stt_model": model, "wer": round(wer(c.get("check_text", c["text"]), transcript, c.get("wer_ignore", ())), 3),
            "transcript": transcript, "rec_words": words}


def build_from_raw(c, keys, src, alignment, atempo=None):
    """Post-process raw audio into the final files; returns meta fields (duration, words, backcheck)."""
    p = paths(c["id"])
    to_prep_wav(src, p["prep"], atempo)
    start, length = trim_and_normalise(p["prep"], p["final"])
    encode_mp3(p["final"], p["mp3"])
    if c.get("speaker") == "receptionist":
        make_phone(p["final"], p["phone_wav"], p["phone"])
    chk = backcheck(keys["DEEPGRAM_API_KEY"], c, p["mp3"])
    text = c.get("tts_text", c["text"])
    if alignment:
        words = []
        for w in words_from_alignment(alignment):
            a = min(max(0.0, w["start"] - start), length)
            b = min(max(a + 0.02, w["end"] - start), length)
            words.append({"w": w["w"], "start": round(a, 3), "end": round(b, 3)})
        timing_source = "elevenlabs-alignment"
    else:
        words = align_script(text, chk["rec_words"] if chk else [], length)
        timing_source = f"deepgram-{chk['stt_model']}" if chk else "even-spread"
    write_json(p["words"], words)
    if chk:
        chk.pop("rec_words", None)
    return {"duration_s": round(probe_duration(p["mp3"]), 3), "trim_start_s": round(start, 3),
            "timing_source": timing_source, "backcheck": chk, "word_count": len(words)}


def make_dg(c, keys, force):
    cid = c["id"]
    src, info_p = RAW / f"{cid}.src.wav", RAW / f"{cid}.src.json"
    if force or not src.exists() or not info_p.exists():
        speed_used, atempo = None, None
        if c.get("speed"):
            try:
                audio = dg_speak(keys["DEEPGRAM_API_KEY"], c["voice"], c["text"], c["speed"])
                speed_used = c["speed"]
            except ApiError as e:
                log(f"  {cid}: Deepgram speed param rejected ({e.status}); using ffmpeg atempo")
                audio = dg_speak(keys["DEEPGRAM_API_KEY"], c["voice"], c["text"])
                atempo = c["speed"]
        else:
            audio = dg_speak(keys["DEEPGRAM_API_KEY"], c["voice"], c["text"])
        src.write_bytes(audio)
        write_json(info_p, {"voice": c["voice"], "model": c["voice"], "speed_param": speed_used, "atempo": atempo})
    info = read_json(info_p)
    meta = build_from_raw(c, keys, src, None, info.get("atempo"))
    meta.update({"voice": c["voice"], "voice_name": c["voice"].split("-")[2].capitalize(), "model": c["voice"],
                 "speed_param": info.get("speed_param"), "atempo": info.get("atempo")})
    return meta


def make_el(c, keys, force, allow_retry=True):
    cid = c["id"]
    src, al_p, info_p = RAW / f"{cid}.src.mp3", RAW / f"{cid}.align.json", RAW / f"{cid}.src.json"
    if force or not src.exists() or not info_p.exists():
        audio, al, info = el_generate(keys["ELEVENLABS_API_KEY"], c)
        src.write_bytes(audio)
        write_json(al_p, al)
        write_json(info_p, info)
    info, al = read_json(info_p), read_json(al_p)
    meta = build_from_raw(c, keys, src, al)
    chk = meta.get("backcheck")
    if allow_retry and chk and chk["wer"] > WER_LIMIT and not info.get("retried"):
        other = "eleven_multilingual_v2" if info["model"] == "eleven_v3" else "eleven_v3"
        log(f"  {cid}: WER {chk['wer']:.2f} > {WER_LIMIT}; regenerating once with {other}")
        try:
            audio2, al2, info2 = el_generate(keys["ELEVENLABS_API_KEY"], c, prefer=other)
            alt_src, alt_al, alt_info = RAW / f"{cid}.alt.src.mp3", RAW / f"{cid}.alt.align.json", RAW / f"{cid}.alt.src.json"
            alt_src.write_bytes(audio2)
            write_json(alt_al, al2)
            meta2 = build_from_raw(c, keys, alt_src, al2)
            chk2 = meta2.get("backcheck") or {"wer": 9}
            if chk2["wer"] < chk["wer"]:
                log(f"  {cid}: kept {info2['model']} (WER {chk2['wer']:.2f})")
                info2["retried"] = True
                info2["replaced_wer"] = chk["wer"]
                src.write_bytes(audio2)
                write_json(al_p, al2)
                write_json(info_p, info2)
                write_json(alt_info, {"note": "promoted to src"})
                info, meta = info2, meta2
            else:
                log(f"  {cid}: kept first take (alt WER {chk2['wer']:.2f})")
                info["retried"] = True
                info["alt_wer"] = chk2["wer"]
                write_json(info_p, info)
                meta = build_from_raw(c, keys, src, al)
        except Exception as e:  # keep the first take
            log(f"  {cid}: retry failed: {str(e)[:200]}")
    meta.update({"voice": info["voice"], "voice_name": info.get("voice_name"), "model": info["model"],
                 "language_code": info.get("language_code"), "el_errors": info.get("errors") or None})
    return meta


def process(c, keys, force=False, rebuild=False):
    cid, p = c["id"], paths(c["id"])
    done = p["mp3"].exists() and p["words"].exists() and p["meta"].exists()
    if c.get("speaker") == "receptionist":
        done = done and p["phone"].exists()
    if done and not force and not rebuild:
        log(f"skip  {cid} (exists)")
        return read_json(p["meta"])
    t0 = time.time()
    try:
        meta = (make_dg if c["provider"] == DG else make_el)(c, keys, force and not rebuild)
    except Exception as e:
        log(f"FAIL  {cid}: {str(e)[:400]}")
        return None
    meta.update({k: c.get(k) for k in ("id", "provider", "lang", "text", "subtitle", "speaker", "group")})
    meta["file"] = f"{cid}.mp3"
    meta["words_file"] = f"{cid}.words.json"
    if c.get("speaker") == "receptionist":
        meta["phone_file"] = f"{cid}_phone.mp3"
    write_json(p["meta"], meta)
    chk = meta.get("backcheck")
    log(f"done  {cid}: {meta['duration_s']:.2f}s  {meta['model']}  "
        f"WER={'n/a' if not chk else format(chk['wer'], '.2f')}  ({time.time() - t0:.1f}s)")
    return meta


# ---------------------------------------------------------------- combined tracks
def final_wav(cid, phone=False):
    p = paths(cid)
    wavp = p["phone_wav"] if phone else p["final"]
    mp3 = p["phone"] if phone else p["mp3"]
    if not wavp.exists() or wavp.stat().st_mtime < mp3.stat().st_mtime - 5:
        run(FF + ["-i", str(mp3), "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le", str(wavp)])
    return wavp


def build_combined(name, seq, gaps, speaker_map, fields):
    frames = bytearray()
    timeline = []
    for i, cid in enumerate(seq):
        c = BY_ID[cid]
        if gaps[i]:
            frames += b"\x00\x00" * int(round(gaps[i] * SR))
        phone = c.get("speaker") == "receptionist"
        with wave.open(str(final_wav(cid, phone)), "rb") as w:
            assert w.getframerate() == SR and w.getnchannels() == 1 and w.getsampwidth() == 2
            data = w.readframes(w.getnframes())
        start = len(frames) / 2 / SR
        frames += data
        end = len(frames) / 2 / SR
        words = [{"w": w["w"], "start": round(start + w["start"], 3), "end": round(start + w["end"], 3)}
                 for w in read_json(paths(cid)["words"])]
        entry = {"id": cid, "speaker": speaker_map(c), "start": round(start, 3), "end": round(end, 3)}
        entry.update(fields(c))
        entry["words"] = words
        timeline.append(entry)
    frames += b"\x00\x00" * int(0.25 * SR)  # short tail so players do not clip the last word
    wav_out = RAW / f"{name}.wav"
    with wave.open(str(wav_out), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(bytes(frames))
    encode_mp3(wav_out, AUDIO / f"{name}.mp3", "160k")
    write_json(AUDIO / f"{name}.timeline.json", timeline)
    dur = probe_duration(AUDIO / f"{name}.mp3")
    log(f"built {name}.mp3: {dur:.2f}s, {len(timeline)} lines")
    return dur


# ---------------------------------------------------------------- extras (ElevenLabs SFX / music)
def make_extras(keys, force):
    key = keys["ELEVENLABS_API_KEY"]
    status_p = RAW / "extras.json"
    status = read_json(status_p) if status_p.exists() else {}
    blocked = {"sfx": False, "music": False}
    jobs = [("sfx", n, t, d) for n, t, d in SFX] + [("music", n, t, d) for n, t, d in MUSIC]
    for kind, name, prompt, dur in jobs:
        out = AUDIO / f"{name}.mp3"
        if out.exists() and not force and status.get(name, {}).get("ok"):
            log(f"skip  {name} (exists)")
            continue
        if blocked[kind]:
            status[name] = {"ok": False, "error": "skipped: no permission"}
            continue
        try:
            if kind == "sfx":
                url = "https://api.elevenlabs.io/v1/sound-generation?output_format=mp3_44100_128"
                body = {"text": prompt, "duration_seconds": dur, "prompt_influence": 0.45}
            else:
                url = "https://api.elevenlabs.io/v1/music?output_format=mp3_44100_128"
                body = {"prompt": prompt, "music_length_ms": dur, "model_id": "music_v1", "force_instrumental": True}
            data, ct = http_post(url, json.dumps(body).encode("utf-8"),
                                 {"xi-api-key": key, "Content-Type": "application/json", "Accept": "audio/mpeg"},
                                 timeout=400, tries=3)
            if "json" in ct:
                raise ApiError(200, data.decode("utf-8", "replace"))
            raw = RAW / f"{name}.src.mp3"
            raw.write_bytes(data)
            tmp = RAW / f"{name}.final.wav"
            target = -20 if kind == "sfx" else -18
            loudnorm_render(raw, tmp, "", target, tp=-1.5, lra=11 if kind == "sfx" else 15)
            encode_mp3(tmp, out, "160k" if kind == "music" else "128k")
            status[name] = {"ok": True, "kind": kind, "prompt": prompt, "duration_s": round(probe_duration(out), 3)}
            log(f"done  {name}: {status[name]['duration_s']:.2f}s")
        except ApiError as e:
            status[name] = {"ok": False, "kind": kind, "error": f"{e.status} {e.body[:200]}"}
            log(f"FAIL  {name}: HTTP {e.status} {e.body[:160]}")
            if e.status in (401, 403) or "permission" in e.body.lower():
                blocked[kind] = True
        except Exception as e:
            status[name] = {"ok": False, "kind": kind, "error": str(e)[:200]}
            log(f"FAIL  {name}: {str(e)[:160]}")
    write_json(status_p, status)
    return status


# ---------------------------------------------------------------- manifest + verify
def write_manifest(extras):
    entries = []
    for c in CLIPS:
        p = paths(c["id"])
        if not p["meta"].exists():
            continue
        m = read_json(p["meta"])
        base = {"id": c["id"], "file": m["file"], "provider": m["provider"], "voice": m.get("voice_name"),
                "voice_id": m.get("voice"), "model": m.get("model"), "lang": c["lang"], "text": c["text"],
                "subtitle": c.get("subtitle"), "speaker": c.get("speaker"), "group": c.get("group"),
                "duration_s": m["duration_s"], "words_file": m["words_file"],
                "timing_source": m.get("timing_source"), "backcheck_wer": (m.get("backcheck") or {}).get("wer")}
        entries.append(base)
        if m.get("phone_file") and (AUDIO / m["phone_file"]).exists():
            ph = dict(base, id=c["id"] + "_phone", file=m["phone_file"],
                      duration_s=round(probe_duration(AUDIO / m["phone_file"]), 3), variant="phone-line")
            entries.append(ph)
    for name, seq in (("call_full", CALL_SEQ), ("intake_full", INTAKE_SEQ)):
        f = AUDIO / f"{name}.mp3"
        if f.exists():
            entries.append({"id": name, "file": f.name, "provider": "mixed", "voice": None, "model": None,
                            "lang": "de" if name == "call_full" else "ru", "text": None, "subtitle": None,
                            "duration_s": round(probe_duration(f), 3), "words_file": None,
                            "timeline_file": f"{name}.timeline.json", "clips": seq})
    for name, st in (extras or {}).items():
        if st.get("ok") and (AUDIO / f"{name}.mp3").exists():
            entries.append({"id": name, "file": f"{name}.mp3", "provider": EL,
                            "voice": None, "model": "sound-generation" if st["kind"] == "sfx" else "music_v1",
                            "lang": None, "text": st["prompt"], "subtitle": None, "duration_s": st["duration_s"],
                            "words_file": None, "kind": st["kind"]})
    write_json(AUDIO / "manifest.json", entries)
    return entries


def verify():
    problems = []
    for c in CLIPS:
        p = paths(c["id"])
        files = [p["mp3"]] + ([p["phone"]] if c.get("speaker") == "receptionist" else [])
        for f in files:
            if not f.exists():
                problems.append(f"missing {f.name}")
            elif probe_duration(f) <= 0:
                problems.append(f"zero duration {f.name}")
        if not p["words"].exists() or not read_json(p["words"]):
            problems.append(f"empty/missing {c['id']}.words.json")
        if p["meta"].exists():
            chk = read_json(p["meta"]).get("backcheck")
            if chk and chk["wer"] > WER_LIMIT:
                problems.append(f"{c['id']}: back-check WER {chk['wer']:.2f} > {WER_LIMIT}")
    for name in ("call_full", "intake_full"):
        for f in (AUDIO / f"{name}.mp3", AUDIO / f"{name}.timeline.json"):
            if not f.exists():
                problems.append(f"missing {f.name}")
    return problems


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--force", action="store_true", help="regenerate even if files exist (new TTS calls)")
    ap.add_argument("--rebuild", action="store_true", help="redo post-processing from raw/ without TTS calls")
    ap.add_argument("--only", default="", help="comma-separated clip ids")
    ap.add_argument("--test", action="store_true", help="one clip per provider (lang_en, maria_ru_2)")
    ap.add_argument("--no-extras", action="store_true", help="skip ElevenLabs SFX/music")
    ap.add_argument("--workers", type=int, default=3)
    args = ap.parse_args()

    keys = load_keys()
    AUDIO.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    if args.test:
        sel = [BY_ID["lang_en"], BY_ID["maria_ru_2"]]
    elif args.only:
        ids = [x.strip() for x in args.only.split(",") if x.strip()]
        unknown = [x for x in ids if x not in BY_ID]
        if unknown:
            sys.exit(f"unknown clip ids: {unknown}")
        sel = [BY_ID[x] for x in ids]
    else:
        sel = CLIPS

    t0 = time.time()
    with ThreadPoolExecutor(max(1, args.workers)) as ex:
        results = list(ex.map(lambda c: process(c, keys, args.force, args.rebuild), sel))
    failed = [c["id"] for c, r in zip(sel, results) if r is None]

    for name, seq, gaps, spk, fields in (
        ("call_full", CALL_SEQ, CALL_GAPS, lambda c: c["speaker"], lambda c: {"de": c["text"], "ru": c["subtitle"].strip("«»")}),
        ("intake_full", INTAKE_SEQ, INTAKE_GAPS, lambda c: c["speaker"], lambda c: {"ru": c["text"], "text": c["text"]}),
    ):
        if all(paths(x)["mp3"].exists() and paths(x)["words"].exists() for x in seq):
            if any(c["id"] in seq for c in sel) or not (AUDIO / f"{name}.mp3").exists() or args.force or args.rebuild:
                build_combined(name, seq, gaps, spk, fields)

    extras = read_json(RAW / "extras.json") if (RAW / "extras.json").exists() else {}
    if not args.no_extras and not args.test and not args.only:
        extras = make_extras(keys, args.force)
    entries = write_manifest(extras)
    problems = verify() if not (args.test or args.only) else []
    log(f"\nmanifest: {len(entries)} entries; ElevenLabs characters this run: {EL_CHARS['n']}; "
        f"time {time.time() - t0:.0f}s")
    if failed:
        log("FAILED: " + ", ".join(failed))
    for pr in problems:
        log("PROBLEM: " + pr)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
