"""
coder.py — 🔧 CODE DOCTOR
══════════════════════════

User ka bot crash ho gaya? JARVIS error padh kar batayega ki kya
galat hai, aur sudhra hua code de dega. User ek click me apply kare.

Engines (jo chale wo):
  1. OpenRouter  — free coding models (poolside, cohere north-mini-code)
  2. Groq        — agar key ho, sabse tez
  3. Gemini      — brain.py se, pehle se laga hua

Kaam:
  diagnose(error, code, lang)  →  problem + fix + sudhra code
  review(code, lang)           →  deploy se pehle scan
  requirements(code)           →  requirements.txt bana do
"""

import json
import os
import re
import threading
import time
import urllib.error
import urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(BASE, "data", "coder.json")
os.makedirs(os.path.dirname(STATE), exist_ok=True)
HOME = os.path.expanduser("~")
CRED = os.path.join(HOME, ".ravanx-ai.json")

# ═══════════════ keys ═══════════════
# 🔐 keyvault.py me XOR+Base64 me — GitHub plain-text key pe push rokta hai
import keyvault as _kv

BUILTIN_OR = _kv.get("OPENROUTER")

# NVIDIA NIM — 22 Aug 2026 verified live. 102 models, 40 req/min,
# koi din ki limit NAHI (NVIDIA ne 2026 me credit cap hata diya).
BUILTIN_NV = _kv.get("NVIDIA")

OR_URL = "https://openrouter.ai/api/v1/chat/completions"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
NV_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

# 22 Aug 2026 — maine 18 NVIDIA models test kiye, ye 11 chale.
# Order: pehle wo jo SAAF jawab dete hain (soch-vichar leak nahi karte).
NV_MODELS = [
    "minimaxai/minimax-m3",                    # 0.7s · saaf · sabse tez
    "moonshotai/kimi-k3",                      # 2.8s · saaf · Hinglish achhi
    "nvidia/nemotron-3-ultra-550b-a55b",       # 1.6s · saaf · 550B
    "poolside/laguna-xs-2.1",                  # 1.8s · saaf · coding agent
    "google/gemma-4-31b-it",                   # 2.7s · saaf
    "nvidia/nemotron-3-nano-30b-a3b",          # 1.8s
    "nvidia/nemotron-3.5-lightning-30b-a3b",   # 4.1s
    "nvidia/nemotron-3-super-120b-a12b",       # 5.0s
    "stepfun-ai/step-3.7-flash",               # 8.4s
    "nvidia/llama-3.3-nemotron-super-49b-v1.5",  # 11.1s
    "openai/gpt-oss-20b",                      # 2.8s
]
# NVIDIA pe FAIL hue:
#   404 (account ko allowed nahi): kimi-k2.6, codestral-22b,
#       mistral-large-2, nemotron-ultra-253b, gemma-3-12b,
#       granite-8b-code, starcoder2-15b, yi-large
#   410 (band): qwen3-coder-480b
#   timeout 180s+: deepseek-v4-flash, llama-3.3-70b, mistral-nemotron
#   gpt-oss-120b chalta hai par 112s leta hai — aakhir me rakha

# 21 Aug 2026 — maine SAARE 22 free models test kiye.
# Ye 9 chal rahe the. Priority order me lagaye hain.
OR_MODELS = [
    # ── CODING ke liye best (verified) ──
    "poolside/laguna-s-2.1:free",              # 1.2s · coding agent
    "cohere/north-mini-code:free",             # 1.0s · code + terminal
    "stealth/ox-alpha",                        # 1.3s · 1M context
    # ── backup (tez, general) ──
    "nvidia/nemotron-3.5-lightning:free",      # 0.6s · sabse tez
    "nvidia/nemotron-3-nano-30b-a3b:free",     # 0.5s
    "nvidia/nemotron-3-super-120b-a12b:free",  # 0.7s
    "nvidia/nemotron-3-ultra-550b-a55b:free",  # 0.8s · 1M context
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
    "liquid/lfm-2.5-2.6b:free",                # 0.9s · halka
]

# Ye test me FAIL hue — rate limit ya band hain:
#   403: thinkingmachines/inkling, inkling-small
#   429: poolside/laguna-xs, google/gemma-4-*, z-ai/glm-5.2
#   502: google/lyria-3-* (ye TTS ke liye hain, chat ke liye nahi)
#   khali jawab: dots-3-note, openrouter/free, nemotron-nano-9b,
#                nemotron-3.5-content-safety
# ═══ GROQ — 22 Aug 2026 LIVE verified ═══
# key: keyvault GROQ  · 30 req/min · 14,400 req/DIN · card nahi
# ⚠️ Groq Cloudflare ke peeche hai — User-Agent header ke BINA 403 (code 1010)
BUILTIN_GROQ = _kv.get("GROQ")
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

# Maine 13 models ki list nikali aur 7 chat models test kiye.
# Har model ko ALAG reasoning param chahiye — warna soch content
# me leak hoti hai (gpt-oss) ya jawab hi khali aata hai.
GROQ_MODELS = [
    ("qwen/qwen3.6-27b", {"reasoning_effort": "none"}),      # 0.17s
    ("openai/gpt-oss-120b", {"reasoning_effort": "low"}),    # 0.29s
    ("openai/gpt-oss-20b", {"reasoning_effort": "low"}),     # 0.25s
    ("groq/compound", {}),                                   # 3.2s
    ("groq/compound-mini", {}),
    ("openai/gpt-oss-safeguard-20b", {"reasoning_effort": "low"}),
]
GROQ_STT = "whisper-large-v3-turbo"      # free STT — Sarvam ka backup

# Groq pe ye NAHI hain (purani guide galat thi — maine list nikali):
#   llama-3.3-70b, llama-3.1-8b, llama-4-scout, kimi-k2, deepseek-r1
#   → sab 404 "model does not exist". Groq ne inhe hata diya.
# allam-2-7b chalta hai par sirf Arabic bolta hai — nahi lagaya.

# Z.AI (GLM) — Flash models hamesha free, ~1 req/sec
ZAI_URL = "https://api.z.ai/api/paas/v4/chat/completions"
ZAI_MODELS = [
    "glm-4.7-flash",                     # 203K ctx · coding strong
    "glm-4.5-flash",                     # 128K ctx
]

DAY_CAP = int(os.environ.get("CODER_DAY_CAP", "45"))   # OR free = 50/din

_lock = threading.RLock()
_st = {"day": "", "calls": 0, "fail": 0, "last_err": "",
       "last_engine": "", "last_model": "", "ms": 0, "fixed": 0}


def _key(name, builtin=""):
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


def or_key():
    return _key("OPENROUTER_API_KEY", BUILTIN_OR)


def nv_key():
    return _key("NVIDIA_API_KEY", BUILTIN_NV)


def groq_key():
    return _key("GROQ_API_KEY", BUILTIN_GROQ)


def zai_key():
    return _key("ZAI_API_KEY", "")


def ok():
    return bool(nv_key() or or_key() or groq_key()
                or zai_key()) or _gemini_ok()


def _gemini_ok():
    try:
        import brain
        return brain.has_gemini()
    except Exception:
        return False


# ═══════════════ counter ═══════════════

def _load():
    try:
        _st.update(json.load(open(STATE)))
    except Exception:
        pass


def _save():
    try:
        json.dump(_st, open(STATE, "w"), indent=2)
    except Exception:
        pass


def _today():
    return time.strftime("%Y-%m-%d")


def _bump(engine=""):
    with _lock:
        if _st["day"] != _today():
            _st.update(day=_today(), calls=0, fail=0, by={})
        _st["calls"] += 1
        if engine:
            b = _st.setdefault("by", {})
            b[engine] = b.get(engine, 0) + 1
        _save()


def left():
    """Kitni CAPPED call bachi (NVIDIA unlimited hai, wo nahi ginte)."""
    if _st["day"] != _today():
        return DAY_CAP
    b = _st.get("by", {})
    free = b.get("nvidia", 0) + b.get("groq", 0) + b.get("zai", 0)
    used = _st["calls"] - free
    return max(0, DAY_CAP - used)


def used_by():
    if _st["day"] != _today():
        return {}
    return dict(_st.get("by", {}))


_load()


# ═══════════════ HTTP ═══════════════

def _post(url, body, hdr, timeout=120):
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers=hdr)
    try:
        return json.loads(urllib.request.urlopen(req, timeout=timeout)
                          .read()), None
    except urllib.error.HTTPError as e:
        try:
            b = e.read().decode()[:200]
        except Exception:
            b = ""
        return None, f"HTTP {e.code} {b}"
    except Exception as e:
        return None, str(e)[:150]


_LEAK = ("we need to", "the user asks", "the user wrote", "user asks:",
         "okay, let's", "got it, let's", "here's a thinking process",
         "let's tackle", "we should", "i need to", "first, the problem",
         "the user is asking", "let me", "so they want", "we must")


def _clean(t):
    """Kuch models apni soch leak kar dete hain — usko kaat do."""
    if not t:
        return ""
    t = t.strip()
    # <think>...</think> block
    for a, b in (("<think>", "</think>"), ("<thinking>", "</thinking>"),
                 ("<reasoning>", "</reasoning>")):
        if b in t:
            t = t.split(b, 1)[1].strip()
        elif t.lower().startswith(a):
            t = t[len(a):].strip()
    lines = t.split("\n")
    # shuru ki soch-wali lines girao, jab tak asli jawab na mile
    while lines:
        low = lines[0].strip().lower()
        if not low:
            lines.pop(0)
            continue
        if any(low.startswith(p) for p in _LEAK):
            lines.pop(0)
            continue
        break
    out = "\n".join(lines).strip()
    return out or t


def _msg(d):
    try:
        c = d["choices"][0]["message"]
        return (c.get("content") or "").strip()
    except Exception:
        return ""


def _ask(prompt, max_tok=1400):
    """
    Sabse achhe available engine se poocho.
    Return: (text, engine, model) ya ("", "", "")
    """
    if left() <= 0:
        return "", "", ""
    t0 = time.time()

    # ── 1. GROQ (0.2s · 14,400/din — sabse tez, isliye pehle) ──
    gk = groq_key()
    if gk:
        hdr = {"Authorization": "Bearer " + gk,
               "Content-Type": "application/json",
               "User-Agent": UA}          # ⚠️ ye zaroori hai warna 403
        for m, extra in GROQ_MODELS:
            body = {"model": m,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tok, "temperature": 0.15}
            body.update(extra)
            d, err = _post(GROQ_URL, body, hdr, 60)
            if d:
                t = _clean(_msg(d))
                if t:
                    _bump("groq")
                    _st.update(last_engine="groq", last_model=m,
                               ms=int((time.time() - t0) * 1000))
                    _save()
                    return t, "groq", m
            else:
                _st["last_err"] = f"groq/{m.split('/')[-1]}: {err[:60]}"

    # ── 2. NVIDIA NIM (koi din ki limit nahi · 11 model) ──
    nk = nv_key()
    if nk:
        hdr = {"Authorization": "Bearer " + nk,
               "Content-Type": "application/json"}
        for m in NV_MODELS:
            d, err = _post(NV_URL, {
                "model": m,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tok, "temperature": 0.15}, hdr, 25)
            if d:
                t = _clean(_msg(d))
                if t:
                    _bump("nvidia")
                    _st.update(last_engine="nvidia", last_model=m,
                               ms=int((time.time() - t0) * 1000))
                    _save()
                    return t, "nvidia", m
            else:
                _st["last_err"] = f"nv/{m.split('/')[-1]}: {err[:70]}"

    # ── 3. Z.AI GLM Flash (free, ~1 req/sec) ──
    zk = zai_key()
    if zk:
        hdr = {"Authorization": "Bearer " + zk,
               "Content-Type": "application/json"}
        for m in ZAI_MODELS:
            d, err = _post(ZAI_URL, {
                "model": m,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tok, "temperature": 0.15}, hdr, 60)
            if d:
                t = _clean(_msg(d))
                if t:
                    _bump("zai")
                    _st.update(last_engine="zai", last_model=m,
                               ms=int((time.time() - t0) * 1000))
                    _save()
                    return t, "zai", m
            else:
                _st["last_err"] = f"zai/{m}: {err[:60]}"

    # ── 4. OPENROUTER (free coding models) ──
    k = or_key()
    if k:
        hdr = {"Authorization": "Bearer " + k,
               "Content-Type": "application/json",
               "HTTP-Referer": "https://ravanx.hosting",
               "X-Title": "RAVAN X HOSTING"}
        for m in OR_MODELS:
            d, err = _post(OR_URL, {
                "model": m,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tok, "temperature": 0.15}, hdr, 120)
            if d:
                t = _clean(_msg(d))
                if t:
                    _bump("openrouter")
                    _st.update(last_engine="openrouter", last_model=m,
                               ms=int((time.time() - t0) * 1000))
                    _save()
                    return t, "openrouter", m
            else:
                _st["last_err"] = f"or/{m.split('/')[-1]}: {err[:70]}"

    # ── 5. GEMINI (brain.py) ──
    try:
        import brain
        if brain.has_gemini():
            d, err = brain._gem(brain.GEM_CHAT, {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.15,
                                     "maxOutputTokens": max_tok,
                                     "thinkingConfig": {"thinkingBudget": 0}}
            }, 90)
            if d:
                t = _clean(brain._gtext(d))
                if t:
                    _bump("gemini")
                    _st.update(last_engine="gemini",
                               last_model=brain.GEM_CHAT,
                               ms=int((time.time() - t0) * 1000))
                    _save()
                    return t, "gemini", brain.GEM_CHAT
    except Exception as e:
        _st["last_err"] = f"gemini: {str(e)[:60]}"

    _st["fail"] = _st.get("fail", 0) + 1
    _save()
    return "", "", ""


def _json(t):
    """LLM ke jawab se JSON nikalo."""
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", (t or "").strip())
    try:
        return json.loads(t)
    except Exception:
        pass
    # nested braces handle
    depth, start = 0, -1
    for i, ch in enumerate(t):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start >= 0:
                try:
                    return json.loads(t[start:i + 1])
                except Exception:
                    start = -1
    return None


# ═══════════════════════════════════════════
#   🩺 DIAGNOSE — crash ka ilaj
# ═══════════════════════════════════════════

def diagnose(error_log, code="", lang="Python", filename="main.py"):
    """
    Error padho, batao kya galat hai + sudhra code do.
    Return: dict ya None
    """
    err = (error_log or "").strip()[-2500:]
    src = (code or "").strip()[:6000]
    if not err and not src:
        return None

    p = f"""Tum RAVAN X HOSTING ke Code Doctor ho. Ek user ka {lang} program
crash ho gaya hai. Usko theek karna hai.

ERROR / CONSOLE OUTPUT:
```
{err}
```
"""
    if src:
        p += f"""
CODE ({filename}):
```
{src}
```
"""
    p += """
Sirf JSON do, koi markdown nahi, koi ``` nahi:
{"problem":"kya galat hai — Hinglish, 1 line, simple",
 "why":"aisa kyun hua — Hinglish, 1 line",
 "fix":"user ko kya karna hai — Hinglish, 1-2 line",
 "code":"poora sudhra hua code, ya khali string agar code change nahi chahiye",
 "severity":"low|medium|high",
 "confidence":"low|medium|high"}

Rules:
- Hinglish me likho (Hindi Latin script me), simple shabd
- "code" me POORA file dena, aadha nahi
- Agar sirf env variable ya command ki galti hai to code khali chhodo
- Kuch invent mat karo — jo error me hai wahi dekho"""

    t, eng, model = _ask(p, 2200)
    if not t:
        return None
    d = _json(t)
    if not d:
        return {"problem": t[:200], "why": "", "fix": "",
                "code": "", "severity": "medium", "confidence": "low",
                "engine": eng, "model": model, "raw": True}
    out = {
        "problem": str(d.get("problem", ""))[:400],
        "why": str(d.get("why", ""))[:400],
        "fix": str(d.get("fix", ""))[:600],
        "code": str(d.get("code", ""))[:20000],
        "severity": str(d.get("severity", "medium")).lower(),
        "confidence": str(d.get("confidence", "medium")).lower(),
        "engine": eng, "model": model,
    }
    if out["severity"] not in ("low", "medium", "high"):
        out["severity"] = "medium"
    if out["code"].strip() in ("", "null", "none", "-"):
        out["code"] = ""
    _st["fixed"] = _st.get("fixed", 0) + 1
    _save()
    return out


# ═══════════════════════════════════════════
#   🔍 REVIEW — deploy se pehle scan
# ═══════════════════════════════════════════

def review(code, lang="Python", filename="main.py"):
    """Deploy se pehle — bug, security, missing deps."""
    src = (code or "").strip()[:9000]
    if not src:
        return None
    p = f"""Tum RAVAN X HOSTING ke Code Doctor ho. Ye {lang} code hosting par
deploy hone wala hai. Deploy se PEHLE check karo.

CODE ({filename}):
```
{src}
```

Sirf JSON do, koi markdown nahi:
{{"safe": true/false,
 "score": 0-100,
 "issues": [
   {{"type":"bug|security|missing|style","msg":"Hinglish 1 line",
     "line":"line number ya khali","bad":"low|medium|high"}}
 ],
 "deps": ["package1","package2"],
 "verdict":"Hinglish me 1 line — deploy karein ya nahi"}}

Rules:
- Max 6 issues, sabse zaroori pehle
- Hardcoded token/password mile to security issue (bad=high)
- import se deps nikalo (sirf pip wale, builtin nahi)
- Hinglish me likho, simple
- safe=false sirf tab jab sach me crash hoga ya token leak hai"""

    t, eng, model = _ask(p, 1600)
    if not t:
        return None
    d = _json(t)
    if not d:
        return None
    iss = []
    for x in (d.get("issues") or [])[:6]:
        if isinstance(x, dict):
            iss.append({
                "type": str(x.get("type", "bug"))[:12],
                "msg": str(x.get("msg", ""))[:220],
                "line": str(x.get("line", ""))[:8],
                "bad": str(x.get("bad", "medium")).lower()[:6]})
    try:
        sc = max(0, min(100, int(d.get("score", 70))))
    except Exception:
        sc = 70
    return {"safe": bool(d.get("safe", True)), "score": sc, "issues": iss,
            "deps": [str(x)[:40] for x in (d.get("deps") or [])[:20]],
            "verdict": str(d.get("verdict", ""))[:300],
            "engine": eng, "model": model}


# ═══════════════════════════════════════════
#   📦 REQUIREMENTS
# ═══════════════════════════════════════════

def requirements(code, lang="Python"):
    """requirements.txt / package.json bana do."""
    src = (code or "").strip()[:9000]
    if not src:
        return ""
    fn = "requirements.txt" if lang == "Python" else "package.json"
    p = f"""Is {lang} code ke liye {fn} banao.

```
{src}
```

Sirf file ka content do — koi explanation nahi, koi markdown nahi,
koi ``` nahi. Sirf wo packages jo pip/npm se install hote hain.
Built-in modules (os, sys, json, time) mat daalna.
Version mat likhna, sirf naam."""
    t, eng, model = _ask(p, 500)
    if not t:
        return ""
    t = re.sub(r"^```[a-z]*\s*|\s*```$", "", t.strip())
    return t[:2000]


# ═══════════════════════════════════════════
#   STATUS
# ═══════════════════════════════════════════

def status():
    return {
        "ok": ok(),
        "nvidia": bool(nv_key()),
        "zai": bool(zai_key()),
        "openrouter": bool(or_key()),
        "groq": bool(groq_key()),
        "gemini": _gemini_ok(),
        "calls": _st.get("calls", 0) if _st["day"] == _today() else 0,
        "cap": DAY_CAP,
        "left": left(),
        "fixed": _st.get("fixed", 0),
        "fails": _st.get("fail", 0),
        "engine": _st.get("last_engine", ""),
        "model": _st.get("last_model", ""),
        "ms": _st.get("ms", 0),
        "error": _st.get("last_err", "")[:110],
        "models": (len(NV_MODELS) + len(OR_MODELS)
                   + (len(GROQ_MODELS) if groq_key() else 0)
                   + (len(ZAI_MODELS) if zai_key() else 0)),
        "nv_models": len(NV_MODELS),
        "or_models": len(OR_MODELS),
        "by": used_by(),
        "unlimited": bool(nv_key() or groq_key()),
    }


def selftest():
    t, eng, m = _ask("Reply with only: OK", 40)
    return {"ok": "OK" in t.upper(), "engine": eng, "model": m}
