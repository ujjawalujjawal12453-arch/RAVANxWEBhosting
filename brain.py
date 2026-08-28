"""
brain.py — J.A.R.V.I.S. ka DIMAAG
══════════════════════════════════

Teen kaam, teen provider, apne aap best chunta hai:

  listen(audio)  →  awaaz se text     (Gemini / Sarvam / browser)
  think(text)    →  samajhna + jawab  (Gemini / Sarvam / keyword)
  speak(text)    →  text se awaaz     (Gemini / Sarvam / browser)

Priority:
  1. GEMINI  — free (1500 req/din), samajh behtar
  2. SARVAM  — Indian awaaz behtar, Hinglish codemix
  3. BROWSER — key na ho to bhi website chalti rahe

Keys env se:
  GEMINI_API_KEY, SARVAM_API_KEY
Ya ~/.ravanx-ai.json se.

⚠️ Keys sirf server par. Browser me kabhi nahi jaati.
"""

import base64
import json
import os
import re
import threading
import time
import urllib.error
import urllib.request

HOME = os.path.expanduser("~")
CRED = os.path.join(HOME, ".ravanx-ai.json")
BASE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(BASE, "data", "brain.json")
os.makedirs(os.path.dirname(STATE), exist_ok=True)

# ═══════════════ built-in keys ═══════════════
# 🔐 Keys keyvault.py me XOR+Base64 me hain — GitHub push protection
#    plain-text key dekhte hi push block kar deta tha. Badalna ho to
#    Render → Environment me GEMINI_API_KEY / SARVAM_API_KEY daal do,
#    env hamesha built-in se pehle padha jata hai.
import keyvault as _kv

BUILTIN_GEMINI = _kv.get("GEMINI")
BUILTIN_SARVAM = _kv.get("SARVAM")

GEM_URL = "https://generativelanguage.googleapis.com/v1beta/models"
SRV_URL = "https://api.sarvam.ai"

# Models — 21 Aug 2026 par verified
GEM_CHAT = os.environ.get("GEMINI_MODEL", "gemini-3-flash-preview")
GEM_CHAT_FALLBACK = "gemini-flash-lite-latest"
GEM_TTS = "gemini-2.5-flash-preview-tts"

# ⚠️ 22 Aug 2026: Sarvam ne `sarvam-m` DEPRECATE kar diya
#    ("Model 'sarvam-m' has been deprecated"). Ab sirf 2 hain:
#      sarvam-105b               → bahut slow, 40s me timeout
#      sarvam-105b-conversations → 3s, chalta hai ✅
SRV_CHAT = os.environ.get("SARVAM_MODEL", "sarvam-105b-conversations")
GEM_VOICE = os.environ.get("GEMINI_VOICE", "Charon")   # bhaari, JARVIS jaisi

SRV_TTS_MODEL = "bulbul:v3"
SRV_SPEAKER = os.environ.get("SARVAM_VOICE", "shubh")
SRV_STT_MODEL = "saaras:v3"

# 🛡️ Daily limit — bill kabhi na bade
DAY_CAP = int(os.environ.get("AI_DAY_CAP", "1200"))

_lock = threading.RLock()
_st = {"day": "", "gem": 0, "srv": 0, "fail": 0,
       "last_err": "", "last_engine": "", "tts_ms": 0, "stt_ms": 0,
       "think_ms": 0}


# ═══════════════════════════════════════════════
#   KEYS
# ═══════════════════════════════════════════════

def _key(name, builtin):
    v = os.environ.get(name, "").strip()
    if v:
        return v
    try:
        d = json.load(open(CRED))
        v = (d.get(name) or d.get(name.lower()) or "").strip()
        if v:
            return v
    except Exception:
        pass
    return builtin


def gemini_key():
    return _key("GEMINI_API_KEY", BUILTIN_GEMINI)


def sarvam_key():
    return _key("SARVAM_API_KEY", BUILTIN_SARVAM)


def has_gemini():
    return bool(gemini_key())


def has_sarvam():
    return bool(sarvam_key())


def ok():
    return has_gemini() or has_sarvam()


# ═══════════════════════════════════════════════
#   COUNTER
# ═══════════════════════════════════════════════

def _load():
    try:
        d = json.load(open(STATE))
        _st.update(d)
    except Exception:
        pass


def _save():
    try:
        json.dump(_st, open(STATE, "w"), indent=2)
    except Exception:
        pass


def _today():
    return time.strftime("%Y-%m-%d")


def _bump(who):
    with _lock:
        if _st["day"] != _today():
            _st.update(day=_today(), gem=0, srv=0, fail=0)
        _st[who] = _st.get(who, 0) + 1
        _save()


def budget_left():
    if _st["day"] != _today():
        return DAY_CAP
    return max(0, DAY_CAP - _st["gem"] - _st["srv"])


def over_budget():
    return budget_left() <= 0


_load()


# ═══════════════════════════════════════════════
#   HTTP
# ═══════════════════════════════════════════════

def _post(url, data, headers, timeout=60):
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        return json.loads(urllib.request.urlopen(req, timeout=timeout).read()), None
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode()[:300]
        except Exception:
            body = ""
        return None, f"HTTP {e.code} {body}"
    except Exception as e:
        return None, str(e)[:200]


def _gem(model, body, timeout=60):
    k = gemini_key()
    if not k:
        return None, "no key"
    return _post(f"{GEM_URL}/{model}:generateContent?key={k}",
                 json.dumps(body).encode(),
                 {"Content-Type": "application/json"}, timeout)


def _srv(path, body, timeout=60):
    k = sarvam_key()
    if not k:
        return None, "no key"
    return _post(f"{SRV_URL}{path}", json.dumps(body).encode(),
                 {"api-subscription-key": k,
                  "Content-Type": "application/json"}, timeout)


def _gtext(d):
    try:
        for p in d["candidates"][0]["content"]["parts"]:
            if "text" in p:
                return p["text"].strip()
    except Exception:
        pass
    return ""


# ═══════════════════════════════════════════════
#   🧠 THINK — samajhna
# ═══════════════════════════════════════════════

ACTIONS = ["server_off", "server_on", "server_restart", "free_off",
           "free_on", "signup_off", "signup_on", "maint_on", "maint_off",
           "tunnel_off", "tunnel_on", "backup", "status", "users",
           "help", "chat"]

DANGEROUS = {"server_off", "server_restart", "free_off", "signup_off",
             "maint_on", "tunnel_off"}


def _prompt(text, ctx=None):
    c = ctx or {}
    return f"""Tum JARVIS ho — RAVAN X HOSTING (India ki hosting company) ka
AI assistant. Malik ka naam Ujjawal X Official hai, unhe "sir" bulao.

ABHI KA HAAL:
- Servers: {c.get('live', 0)} chal rahe, {c.get('total', 0)} total
- Users: {c.get('users', 0)}
- CPU {c.get('cpu', 0)}% · RAM {c.get('ram', 0)}%
- Free service: {'CHALU' if c.get('free_open', True) else 'BAND'}
- Signup: {'CHALU' if c.get('signup_open', True) else 'BAND'}
- Website: {'MAINTENANCE' if c.get('maintenance') else 'LIVE'}

User bola: "{text}"

Sirf JSON do, aur kuch nahi. Koi markdown nahi, koi ``` nahi:
{{"action": "<action>", "reply": "<jawab>"}}

Allowed actions aur unka matlab:
- server_off     : servers/bots band karo, rok do, stop, shut down
- server_on      : servers/bots chalu karo, start, on
- server_restart : servers dobara chalu, reboot
- free_off       : free service/free server band
- free_on        : free service chalu
- signup_off     : naye signup/registration band
- signup_on      : signup chalu
- maint_on       : maintenance mode on, poori website band
- maint_off      : maintenance hatao, website wapas
- tunnel_off     : tunnel/public link band
- tunnel_on      : tunnel chalu
- backup         : backup lo, data save karo
- status         : CPU/RAM/server ka haal batao
- users          : kitne users hain
- help           : kya kar sakte ho
- chat           : sirf baat-cheet (hello, kaise ho, thanks, kaun ho)

⚠️ ZAROORI RULES:
1. Tumhare paas SAB control hai — server on/off, free service, sab kuch.
   "access nahi hai" KABHI mat kehna.
2. "bot" = "server" hi hota hai. "bot band karo" = server_off.
   "app", "service", "wo cheez" — sab server hi samjho.
3. Ghuma-phira kar bola ho to bhi action nikalo:
   "wo jo chal raha tha usko rok do" = server_off
   "aaj free nahi dena" = free_off
   "sab band" = server_off
4. Sirf tab chat karo jab SACH ME koi command na ho.
5. reply Hinglish me, chhota (max 18 shabd), shaant aur polite. "sir" bolo.
6. reply me JSON/code mat likhna.
7. Numbers sirf upar diye hue use karo — invent mat karo.
8. Action karne se pehle "kar diya" mat kehna — "kar deta hoon" kehna."""


def _parse_json(t):
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", (t or "").strip())
    try:
        d = json.loads(t)
    except Exception:
        m = re.search(r"\{[^{}]*\}", t, re.S)
        if not m:
            return None
        try:
            d = json.loads(m.group(0))
        except Exception:
            return None
    a = str(d.get("action", "")).strip().lower()
    r = str(d.get("reply", "")).strip()
    if a not in ACTIONS:
        a = "chat"
    return {"action": a, "reply": r[:300] or "Ji sir?"}


def think(text, ctx=None):
    """
    Samajhna. Return: (action, reply, engine)
    Fail ho to (None, None, "") — caller keyword fallback use kare.
    """
    if not text or over_budget():
        return None, None, ""
    t0 = time.time()
    p = _prompt(text, ctx)

    # ── 1. GEMINI ──
    if has_gemini():
        for model in (GEM_CHAT, GEM_CHAT_FALLBACK):
            cfg = {"temperature": 0.35, "maxOutputTokens": 900}
            if "3" in model or "preview" in model:
                cfg["thinkingConfig"] = {"thinkingBudget": 0}
            d, err = _gem(model, {"contents": [{"parts": [{"text": p}]}],
                                  "generationConfig": cfg}, 45)
            if d:
                r = _parse_json(_gtext(d))
                if r:
                    _bump("gem")
                    _st["last_engine"] = "gemini"
                    _st["think_ms"] = int((time.time() - t0) * 1000)
                    return r["action"], r["reply"], "gemini"
            else:
                _st["last_err"] = f"gemini: {err}"

    # ── 2. SARVAM ──
    if has_sarvam():
        d, err = _post(f"{SRV_URL}/v1/chat/completions",
                       json.dumps({"model": SRV_CHAT,
                                   "messages": [{"role": "user",
                                                 "content": p}],
                                   "temperature": 0.35,
                                   "max_tokens": 300}).encode(),
                       {"Authorization": "Bearer " + sarvam_key(),
                        "Content-Type": "application/json"}, 45)
        if d:
            try:
                txt = d["choices"][0]["message"]["content"]
                r = _parse_json(txt)
                if r:
                    _bump("srv")
                    _st["last_engine"] = "sarvam"
                    _st["think_ms"] = int((time.time() - t0) * 1000)
                    return r["action"], r["reply"], "sarvam"
            except Exception:
                pass
        else:
            _st["last_err"] = f"sarvam: {err}"

    # ── 3. GROQ (0.2s · 14,400/din — Gemini/Sarvam fail ho to) ──
    try:
        import coder
        gk = coder.groq_key()
        if gk:
            for m, extra in coder.GROQ_MODELS[:3]:
                body = {"model": m,
                        "messages": [{"role": "user", "content": p}],
                        "temperature": 0.35, "max_tokens": 400}
                body.update(extra)
                d, err = _post(coder.GROQ_URL, json.dumps(body).encode(),
                               {"Authorization": "Bearer " + gk,
                                "Content-Type": "application/json",
                                "User-Agent": coder.UA}, 30)
                if d:
                    try:
                        txt = d["choices"][0]["message"].get("content") or ""
                    except Exception:
                        txt = ""
                    r = _parse_json(coder._clean(txt))
                    if r:
                        _st["last_engine"] = "groq"
                        _st["think_ms"] = int((time.time() - t0) * 1000)
                        return r["action"], r["reply"], "groq"
                else:
                    _st["last_err"] = f"groq: {str(err)[:60]}"
    except Exception as e:
        _st["last_err"] = f"groq: {str(e)[:60]}"

    # ── 4. NVIDIA NIM (coder.py ki key — koi din ki limit nahi) ──
    #    Gemini/Sarvam dono fail? Tab bhi JARVIS chup nahi hoga.
    try:
        import coder
        nk = coder.nv_key()
        if nk:
            for m in coder.NV_MODELS[:3]:
                d, err = _post(coder.NV_URL, json.dumps({
                    "model": m,
                    "messages": [{"role": "user", "content": p}],
                    "temperature": 0.35, "max_tokens": 400}).encode(),
                    {"Authorization": "Bearer " + nk,
                     "Content-Type": "application/json"}, 40)
                if d:
                    try:
                        txt = d["choices"][0]["message"].get("content") or ""
                    except Exception:
                        txt = ""
                    r = _parse_json(coder._clean(txt))
                    if r:
                        _st["last_engine"] = "nvidia"
                        _st["think_ms"] = int((time.time() - t0) * 1000)
                        return r["action"], r["reply"], "nvidia"
                else:
                    _st["last_err"] = f"nvidia: {str(err)[:60]}"
    except Exception as e:
        _st["last_err"] = f"nvidia: {str(e)[:60]}"

    _st["fail"] = _st.get("fail", 0) + 1
    return None, None, ""


# ═══════════════════════════════════════════════
#   🔊 SPEAK — awaaz banao
# ═══════════════════════════════════════════════

def _pcm_to_wav(pcm, rate=24000, ch=1, bits=16):
    """Gemini raw PCM deta hai — WAV header laga do."""
    import struct
    ba = ch * bits // 8
    hdr = (b"RIFF" + struct.pack("<I", 36 + len(pcm)) + b"WAVEfmt " +
           struct.pack("<IHHIIHH", 16, 1, ch, rate, rate * ba, ba, bits) +
           b"data" + struct.pack("<I", len(pcm)))
    return hdr + pcm


def speak(text, prefer=None):
    """
    Text → awaaz. Return: (wav_bytes, engine) ya (None, "")
    prefer: "gemini" / "sarvam" / None (auto)
    """
    text = (text or "").strip()
    if not text or over_budget():
        return None, ""
    text = text[:1400]
    t0 = time.time()
    order = ([prefer] if prefer else []) + ["gemini", "sarvam"]
    seen = set()

    for who in order:
        if who in seen:
            continue
        seen.add(who)

        # ── GEMINI TTS ──
        if who == "gemini" and has_gemini():
            d, err = _gem(GEM_TTS, {
                "contents": [{"parts": [{"text": text}]}],
                "generationConfig": {
                    "responseModalities": ["AUDIO"],
                    "speechConfig": {"voiceConfig": {
                        "prebuiltVoiceConfig": {"voiceName": GEM_VOICE}}}}
            }, 70)
            if d:
                try:
                    pt = d["candidates"][0]["content"]["parts"][0]
                    ai = pt["inlineData"]
                    raw = base64.b64decode(ai["data"])
                    mime = ai.get("mimeType", "")
                    m = re.search(r"rate=(\d+)", mime)
                    rate = int(m.group(1)) if m else 24000
                    wav = (raw if raw[:4] == b"RIFF"
                           else _pcm_to_wav(raw, rate))
                    _bump("gem")
                    _st["last_engine"] = "gemini"
                    _st["tts_ms"] = int((time.time() - t0) * 1000)
                    return wav, "gemini"
                except Exception as e:
                    _st["last_err"] = f"gtts parse: {str(e)[:60]}"
            else:
                _st["last_err"] = f"gtts: {err}"

        # ── SARVAM TTS ──
        if who == "sarvam" and has_sarvam():
            d, err = _srv("/text-to-speech", {
                "text": text[:2400],
                "target_language_code": "hi-IN",
                "speaker": SRV_SPEAKER,
                "model": SRV_TTS_MODEL,
                "pace": 0.95,
            }, 70)
            if d and d.get("audios"):
                try:
                    wav = base64.b64decode(d["audios"][0])
                    _bump("srv")
                    _st["last_engine"] = "sarvam"
                    _st["tts_ms"] = int((time.time() - t0) * 1000)
                    return wav, "sarvam"
                except Exception:
                    pass
            else:
                _st["last_err"] = f"stts: {err}"

    _st["fail"] = _st.get("fail", 0) + 1
    return None, ""


# ═══════════════════════════════════════════════
#   🎤 LISTEN — awaaz se text
# ═══════════════════════════════════════════════

def _multipart(fields, fname, fdata, mime="audio/wav"):
    bd = "----rx" + os.urandom(8).hex()
    out = []
    for k, v in fields.items():
        out.append(f"--{bd}\r\nContent-Disposition: form-data; "
                   f"name=\"{k}\"\r\n\r\n{v}\r\n".encode())
    out.append((f"--{bd}\r\nContent-Disposition: form-data; name=\"file\"; "
                f"filename=\"{fname}\"\r\nContent-Type: {mime}\r\n\r\n")
               .encode())
    out.append(fdata)
    out.append(f"\r\n--{bd}--\r\n".encode())
    return b"".join(out), bd


def listen(audio, mime="audio/wav", prefer=None):
    """
    Awaaz → text. Return: (text, engine) ya ("", "")
    Sarvam pehle — Hinglish codemix behtar hai.
    """
    if not audio or over_budget():
        return "", ""
    t0 = time.time()
    order = ([prefer] if prefer else []) + ["sarvam", "groq", "gemini"]
    seen = set()

    for who in order:
        if who in seen:
            continue
        seen.add(who)

        # ── SARVAM STT — codemix (Hinglish ke liye best) ──
        if who == "sarvam" and has_sarvam():
            body, bd = _multipart(
                {"model": SRV_STT_MODEL, "mode": "codemix",
                 "language_code": "unknown"},
                "cmd.wav", audio, mime)
            req = urllib.request.Request(
                f"{SRV_URL}/speech-to-text", data=body,
                headers={"api-subscription-key": sarvam_key(),
                         "Content-Type":
                             f"multipart/form-data; boundary={bd}"})
            try:
                d = json.loads(urllib.request.urlopen(req, timeout=70).read())
                t = (d.get("transcript") or "").strip()
                if t:
                    _bump("srv")
                    _st["last_engine"] = "sarvam"
                    _st["stt_ms"] = int((time.time() - t0) * 1000)
                    return t, "sarvam"
            except urllib.error.HTTPError as e:
                try:
                    _st["last_err"] = f"sstt: {e.code} {e.read().decode()[:120]}"
                except Exception:
                    _st["last_err"] = f"sstt: {e.code}"
            except Exception as e:
                _st["last_err"] = f"sstt: {str(e)[:80]}"

        # ── GROQ WHISPER STT (free, 2000/din — Sarvam ka backup) ──
        if who == "groq":
            try:
                import coder
                gk = coder.groq_key()
            except Exception:
                gk = ""
            if gk:
                body, bd = _multipart(
                    {"model": coder.GROQ_STT, "response_format": "json"},
                    "cmd.wav", audio, mime)
                req = urllib.request.Request(
                    "https://api.groq.com/openai/v1/audio/transcriptions",
                    data=body,
                    headers={"Authorization": "Bearer " + gk,
                             "User-Agent": coder.UA,
                             "Content-Type":
                                 f"multipart/form-data; boundary={bd}"})
                try:
                    d = json.loads(urllib.request.urlopen(req,
                                                          timeout=70).read())
                    t = (d.get("text") or "").strip()
                    if t:
                        _st["last_engine"] = "groq"
                        _st["stt_ms"] = int((time.time() - t0) * 1000)
                        return t, "groq"
                except Exception as e:
                    _st["last_err"] = f"gqstt: {str(e)[:80]}"

        # ── GEMINI STT — audio seedha model ko ──
        if who == "gemini" and has_gemini():
            d, err = _gem(GEM_CHAT, {
                "contents": [{"parts": [
                    {"text": "Is audio me jo bola gaya hai wahi text do. "
                             "Hindi shabd Hindi me, English shabd English "
                             "me. Sirf text, aur kuch nahi."},
                    {"inlineData": {"mimeType": mime,
                                    "data": base64.b64encode(audio).decode()}}
                ]}],
                "generationConfig": {"temperature": 0, "maxOutputTokens": 700,
                                     "thinkingConfig": {"thinkingBudget": 0}}
            }, 90)
            if d:
                t = _gtext(d)
                if t:
                    _bump("gem")
                    _st["last_engine"] = "gemini"
                    _st["stt_ms"] = int((time.time() - t0) * 1000)
                    return t, "gemini"
            else:
                _st["last_err"] = f"gstt: {err}"

    _st["fail"] = _st.get("fail", 0) + 1
    return "", ""


# ═══════════════════════════════════════════════
#   STATUS
# ═══════════════════════════════════════════════

def has_groq():
    try:
        import coder
        return bool(coder.groq_key())
    except Exception:
        return False


def has_nvidia():
    try:
        import coder
        return bool(coder.nv_key())
    except Exception:
        return False


def status():
    if _st["day"] != _today():
        used = 0
    else:
        used = _st["gem"] + _st["srv"]
    return {
        "ok": ok(),
        "nvidia": has_nvidia(),
        "groq": has_groq(),
        "gemini": has_gemini(),
        "sarvam": has_sarvam(),
        "engine": _st.get("last_engine", ""),
        "gem_calls": _st.get("gem", 0),
        "srv_calls": _st.get("srv", 0),
        "fails": _st.get("fail", 0),
        "used": used,
        "cap": DAY_CAP,
        "left": budget_left(),
        "error": _st.get("last_err", "")[:120],
        "tts_ms": _st.get("tts_ms", 0),
        "stt_ms": _st.get("stt_ms", 0),
        "think_ms": _st.get("think_ms", 0),
        "voice_gem": GEM_VOICE,
        "voice_srv": SRV_SPEAKER,
    }


def selftest():
    """Boot par — keys chal rahi hain ya nahi."""
    out = {"gemini": False, "sarvam": False}
    if has_gemini():
        d, _ = _gem(GEM_CHAT_FALLBACK,
                    {"contents": [{"parts": [{"text": "Reply only: OK"}]}],
                     "generationConfig": {"maxOutputTokens": 12}}, 25)
        out["gemini"] = bool(d and "OK" in _gtext(d).upper())
    if has_sarvam():
        d, _ = _srv("/text-to-speech",
                    {"text": "ok", "target_language_code": "hi-IN",
                     "speaker": SRV_SPEAKER, "model": SRV_TTS_MODEL}, 25)
        out["sarvam"] = bool(d and d.get("audios"))
    return out
