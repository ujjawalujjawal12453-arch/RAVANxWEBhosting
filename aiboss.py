"""
👑 AI BOSS — 57 model ka malik
════════════════════════════════════════════════════════════════

Ye kya hai:
  Ek AI jo BAAKI SAB AI ka boss hai. Aap kaam batao — wo khud
  decide karta hai kaunsa model us kaam ke liye best hai, use
  bhejta hai, jawab check karta hai, aur galat lage to doosre
  model se dobara karwata hai.

Boss khud kya karta hai:
  1. Kaam padhta hai            → "ye coding ka kaam hai ya translate ka?"
  2. Model chunta hai           → us kaam ke liye jo sabse tez/achha ho
  3. Bhejta hai                 → aur waqt naapta hai
  4. Jawab check karta hai      → khali/bakwas to reject
  5. Fail? doosra model         → apne aap, aap ko pata bhi nahi chalega
  6. Seekhta hai                → jo model bar-bar fail kare, uski rank girti hai

⚠️ KISKO MILEGA:
  free      →  kuch nahi (Boss band)
  starter   →  kuch nahi
  pro       →  ✅ Boss chalu, 40 kaam/din, 3 model per kaam
  ultra     →  ✅ Boss chalu, 150 kaam/din, 5 model, TEAM mode
  business  →  ✅ Boss chalu, 500 kaam/din, 8 model, TEAM + PANEL
  admin     →  ✅ sab kuch unlimited

TEAM MODE (ultra+): ek hi kaam 3 alag model ko bheja jata hai,
phir Boss teeno jawab padh kar sabse achha chunta hai.

Developer : Ujjawal X Official
Team      : RAVAN X HOSTING TEAM
"""

import json
import os
import threading
import time

BASE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(BASE, "data", "aiboss.json")
os.makedirs(os.path.dirname(STATE), exist_ok=True)

# ═══════════════════════════════════════════════
#   💎 PLAN — kisko kya milega
# ═══════════════════════════════════════════════

# 🆓 Ye do endpoints ko API KEY chahiye hi NAHI — khule pade hain
OVH_URL = ("https://oai.endpoints.kepler.ai.cloud.ovh.net"
           "/v1/chat/completions")
LLM7_URL = "https://api.llm7.io/v1/chat/completions"
POLL_URL = "https://text.pollinations.ai/openai"
KILO_URL = "https://api.kilo.ai/api/gateway/v1/chat/completions"

# ☁️ CLOUDFLARE WORKERS AI — 22 Aug 2026 live verified
# ⚠️ Isko 2 cheezein chahiye: Account ID + Token (dono alag)
# ⚠️ Token banate waqt permission "Workers AI · Edit" honi chahiye.
#    "AI Audit Read" se 401 aata hai (ye galti pehle hui thi).
# 🔐 keyvault.py me chhupe hain (GitHub push protection)
import keyvault as _kv

BUILTIN_CF_ACC = _kv.get("CF_ACC")
BUILTIN_CF_TOK = _kv.get("CF_TOK")
NOKEY = ("ovh", "llm7", "poll", "kilo")

# ⚠️ "models" = kitne model us plan ko dikhenge/milenge.
#    0 ka matlab SAB (koi rok nahi).
TIERS = {
    "free":     {"on": True,  "day": 10,  "fan": 1, "team": False,
                 "panel": False, "models": 5,
                 "label": "Free — 10 chat/din · 5 model"},
    "starter":  {"on": True,  "day": 25,  "fan": 2, "team": False,
                 "panel": False, "models": 12,
                 "label": "Starter — 25 chat/din · 12 model"},
    "pro":      {"on": True,  "day": 100, "fan": 3, "team": False,
                 "panel": False, "models": 0,
                 "label": "Pro — 100/din · SAARE model"},
    "ultra":    {"on": True,  "day": 300, "fan": 5, "team": True,
                 "panel": False, "models": 0,
                 "label": "Ultra — 300/din · Team mode"},
    "business": {"on": True,  "day": 800, "fan": 8, "team": True,
                 "panel": True,  "models": 0,
                 "label": "Business — 800/din · Panel"},
    "admin":    {"on": True,  "day": 99999, "fan": 12, "team": True,
                 "panel": True, "models": 0,
                 "label": "Admin — unlimited"},
}

# 🆓 FREE PLAN ke 5 model — ye bilkul free logon ko milenge.
#    Sabse tez aur sabse bharosemand chune hain, taaki free
#    user ko bhi bura experience na ho.
FREE_5 = [
    "openai/gpt-oss-20b",                        # groq   0.09s
    "@cf/meta/llama-3.3-70b-instruct-fp8-fast",  # cf     0.18s
    "meta/llama-3.1-8b-instruct",                # nvidia 0.23s
    "qwen/qwen3.6-27b",                          # groq   0.13s
    "@cf/meta/llama-3.2-3b-instruct",            # cf     0.29s
]

# STARTER ke 12 — 5 free + 7 aur
STARTER_EXTRA = [
    "@cf/qwen/qwen2.5-coder-32b-instruct",
    "@cf/meta/llama-4-scout-17b-16e-instruct",
    "minimaxai/minimax-m3",
    "openai/gpt-oss-120b",
    "@cf/openai/gpt-oss-20b",
    "nvidia/nemotron-3-nano-30b-a3b",
    "@cf/google/gemma-4-26b-a4b-it",
]


def allowed_models(user, is_admin=False):
    """
    Is user ko kaunse model milenge.
    Paid = sab. Free = sirf 5. Starter = 12.
    """
    pk = perks(user, is_admin)
    lim = pk.get("models", 0)
    if not lim:
        return None                    # None = koi rok nahi
    names = list(FREE_5)
    if lim > 5:
        names += STARTER_EXTRA[:lim - 5]
    return set(names[:lim])


def cf_acc():
    import coder
    return coder._key("CF_ACCOUNT_ID", BUILTIN_CF_ACC)


def cf_tok():
    import coder
    return coder._key("CF_API_TOKEN", BUILTIN_CF_TOK)


def tier_of(user, is_admin=False):
    if is_admin or (user or {}).get("role") == "admin":
        return "admin"
    return (user or {}).get("plan", "free") or "free"


def perks(user, is_admin=False):
    return dict(TIERS.get(tier_of(user, is_admin), TIERS["free"]),
                tier=tier_of(user, is_admin))


def allowed(user, is_admin=False):
    return perks(user, is_admin)["on"]


# ═══════════════════════════════════════════════
#   👤 VIP PEHCHAN — Boss ko pata ho kaun baat kar raha
# ═══════════════════════════════════════════════

RANK = {
    "free":     ("FREE",     "#64748B", "Free user"),
    "starter":  ("STARTER",  "#38BDF8", "Starter member"),
    "pro":      ("VIP",      "#7C3AED", "VIP member"),
    "ultra":    ("VIP+",     "#00E6FF", "VIP+ member"),
    "business": ("ELITE",    "#EC4899", "Elite member"),
    "admin":    ("BOSS",     "#F59E0B", "Malik"),
}


def rank_of(user, is_admin=False):
    t = tier_of(user, is_admin)
    tag, col, label = RANK.get(t, RANK["free"])
    return {"tier": t, "tag": tag, "color": col, "label": label,
            "vip": t in ("pro", "ultra", "business", "admin"),
            "name": (user or {}).get("name", "")
                    or (user or {}).get("email", "").split("@")[0]}


def _who(user, is_admin=False):
    """Boss ko batao kis se baat ho rahi hai."""
    r = rank_of(user, is_admin)
    nm = r["name"] or "sir"
    if r["tier"] == "admin":
        return (f"Aap {nm} se baat kar rahe ho — ye is website ke "
                f"MALIK hain. Poora izzat se, 'sir' kehkar baat karo. "
                f"Inhe har cheez ka access hai.")
    if r["vip"]:
        return (f"Aap {nm} se baat kar rahe ho — ye ek "
                f"{r['label']} hain ({r['tier'].upper()} plan). "
                f"Izzat se baat karo, inhone paise diye hain. "
                f"Inki har baat dhyaan se suno.")
    return (f"Aap {nm} se baat kar rahe ho — ye free plan par hain. "
            f"Achhe se madad karo par bahut lamba jawab mat do.")


def _my_data(user):
    """
    User ka apna hisaab — Boss ko pata hona chahiye.

    ⚠️ Pehle Boss ko user ka kuch nahi pata tha. "Mere kitne
       server hain?" poochho to bekaar jawab deta tha. Ab uske
       saamne asli aankde rehte hain.
    """
    if not user:
        return ""
    try:
        import db, time
        uid = user["id"]
        apps = db.user_apps(uid) or []
        live = sum(1 for a in apps if (a.get("status") or "") == "running")
        cr = float(user.get("credits", 0) or 0)
        try:
            from theme import CREDIT_RATE
            hrs = int(cr // CREDIT_RATE)
        except Exception:
            hrs = 0
        lines = [f"\nIS USER KA APNA HISAAB (asli data, abhi ka):",
                 f"  • Naam: {user.get('name','')} · {user.get('email','')}",
                 f"  • Plan: {user.get('plan','free')}",
                 f"  • Credit: {cr:.0f}  (≈ {hrs} ghante hosting)",
                 f"  • Server: {len(apps)} total, {live} abhi chalu"]
        for a in apps[:8]:
            lines.append(f"      - {a.get('name','?')} "
                         f"({a.get('plan','?')}) "
                         f"{a.get('status','stopped')}")
        # free server + weekly credit ka ASLI haal
        # ⚠️ Ye zaroori hai — bina iske Boss apne mann se niyam
        #    bana deta tha ("10 credit hone chahiye" jaisa jhooth).
        try:
            import unlock
            if unlock.is_black(uid):
                lines.append("  • ⚠️ BLACKLIST me hai — free kuch "
                             "nahi milega")
            else:
                lk = unlock.server_lock(uid)
                wk = unlock.weekly_status(uid)
                if lk["locked"]:
                    lines.append(
                        f"  • ❌ FREE SERVER LOCK hai — "
                        f"{unlock.human_left(lk['left_sec'])} baaki. "
                        f"Wajah: {lk['why']}")
                elif unlock.has_claimed(uid):
                    lines.append("  • Free server pehle le chuke hain")
                else:
                    st = unlock.stock()
                    lines.append(f"  • ✅ Free server le sakte hain "
                                 f"({st['left']} stock bacha) — /free")
                if wk["can"]:
                    lines.append(f"  • ✅ Weekly {wk['amount']} credit "
                                 f"le sakte hain abhi — /free")
                else:
                    lines.append(
                        f"  • Weekly credit ka agla baari: "
                        f"{unlock.human_left(wk['left_sec'])} baad")
        except Exception:
            pass
        return "\n".join(lines) + "\n"
    except Exception:
        return ""


# ═══════════════════════════════════════════════
#   🤖 MODEL REGISTRY — 22 Aug 2026 sab LIVE test kiye
# ═══════════════════════════════════════════════
# skill: code, fast, big, reason, hindi, vision, safety,
#        translate, embed, chat
# tier: 1 = sabse achha  ·  3 = backup

def M(name, prov, sec, skills, tier=2, kind="chat", extra=None):
    return {"m": name, "p": prov, "s": sec, "sk": skills,
            "t": tier, "k": kind, "x": extra or {}}


MODELS = [
    # ───────── GROQ · 0.1s · 14,400/din ─────────
    M("openai/gpt-oss-20b", "groq", 0.09, ["fast", "code", "chat"], 1,
      extra={"reasoning_effort": "low"}),
    M("qwen/qwen3.6-27b", "groq", 0.13, ["fast", "code", "reason"], 1,
      extra={"reasoning_effort": "none"}),
    M("openai/gpt-oss-120b", "groq", 0.16, ["code", "reason", "big"], 1,
      extra={"reasoning_effort": "low"}),
    M("groq/compound", "groq", 1.72, ["reason", "big", "chat"], 2),
    M("allam-2-7b", "groq", 0.31, ["chat"], 3),

    # ───────── NVIDIA · unlimited · 21 model ─────────
    M("meta/llama-3.1-8b-instruct", "nvidia", 0.23, ["fast", "chat"], 2),
    M("meta/llama-3.2-90b-vision-instruct", "nvidia", 0.25,
      ["vision", "big"], 1),
    M("meta/llama-3.2-11b-vision-instruct", "nvidia", 0.27, ["vision"], 2),
    M("meta/muse-glimmer-30b", "nvidia", 0.27, ["chat", "fast"], 3),
    M("nvidia/nemotron-mini-4b-instruct", "nvidia", 0.30, ["fast"], 3),
    M("nvidia/llama-3.3-nemotron-super-49b-v1", "nvidia", 0.34,
      ["reason", "code"], 2),
    M("meta/llama-3.1-70b-instruct", "nvidia", 0.42, ["big", "chat"], 2),
    M("nvidia/nemotron-3-nano-omni-30b-a3b-reasoning", "nvidia", 0.52,
      ["reason"], 2),
    M("nvidia/nemotron-3-nano-30b-a3b", "nvidia", 0.54, ["fast", "chat"], 2),
    M("nvidia/nvidia-nemotron-nano-9b-v2", "nvidia", 0.61, ["fast"], 3),
    M("nvidia/ising-calibration-1.5-31b", "nvidia", 0.62, ["reason"], 3),
    M("nvidia/nemotron-3-super-120b-a12b", "nvidia", 0.65,
      ["big", "reason"], 1),
    M("openai/gpt-oss-20b", "nvidia", 0.66, ["code", "fast"], 2),
    M("nvidia/nemotron-3.5-lightning-30b-a3b", "nvidia", 0.75, ["fast"], 2),
    M("nvidia/nemotron-nano-12b-v2-vl", "nvidia", 1.20, ["vision"], 2),
    M("thinkingmachines/inkling", "nvidia", 1.21, ["reason"], 2),
    M("minimaxai/minimax-m3", "nvidia", 1.34,
      ["code", "hindi", "chat"], 1),
    M("stepfun-ai/step-3.7-flash", "nvidia", 2.05, ["reason", "big"], 3),
    M("nvidia/llama-3.3-nemotron-super-49b-v1.5", "nvidia", 4.05,
      ["reason"], 3),
    M("moonshotai/kimi-k3", "nvidia", 5.35, ["hindi", "code", "big"], 1),
    M("nvidia/nemotron-3-ultra-550b-a55b", "nvidia", 9.11,
      ["big", "reason"], 2),

    # ───────── NVIDIA specialty ─────────
    M("nvidia/llama-3.1-nemoguard-8b-content-safety", "nvidia", 0.35,
      ["safety"], 1),
    M("nvidia/nemotron-3.5-content-safety", "nvidia", 0.29, ["safety"], 1),
    M("nvidia/llama-3.1-nemoguard-8b-topic-control", "nvidia", 0.26,
      ["safety"], 2),
    M("nvidia/llama-3.1-nemotron-safety-guard-8b-v3", "nvidia", 0.42,
      ["safety"], 2),
    M("nvidia/riva-translate-4b-instruct-v2", "nvidia", 0.34,
      ["translate", "hindi"], 1),
    M("nvidia/riva-translate-4b-instruct-v1.1", "nvidia", 0.27,
      ["translate"], 2),
    M("nvidia/nemotron-3-embed-1b", "nvidia", 0.45, ["embed"], 1,
      kind="embed"),
    M("nvidia/nv-embedqa-e5-v5", "nvidia", 0.40, ["embed"], 1, kind="embed"),
    M("nvidia/nv-embed-v1", "nvidia", 0.58, ["embed"], 2, kind="embed"),
    M("nvidia/llama-nemotron-embed-1b-v2", "nvidia", 0.62, ["embed"], 2,
      kind="embed"),
    M("nvidia/llama-nemotron-embed-vl-1b-v2", "nvidia", 0.62,
      ["embed", "vision"], 3, kind="embed"),

    # ───────── OPENROUTER · 45/din ─────────
    M("nvidia/nemotron-3-super-120b-a12b:free", "openrouter", 0.56,
      ["big", "reason"], 2),
    M("nvidia/nemotron-3-nano-30b-a3b:free", "openrouter", 0.64,
      ["fast"], 3),
    M("google/gemma-4-31b-it:free", "openrouter", 0.71, ["code", "chat"], 2),
    M("nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free", "openrouter",
      0.86, ["reason"], 3),
    M("dots-studio/dots-3-note-preview:free", "openrouter", 0.97,
      ["chat"], 3),
    M("nvidia/nemotron-3.5-lightning:free", "openrouter", 0.97, ["fast"], 3),
    M("nvidia/nemotron-3-ultra-550b-a55b:free", "openrouter", 1.12,
      ["big"], 3),
    M("stealth/ox-alpha", "openrouter", 1.56, ["big", "code"], 2),
    M("liquid/lfm-2.5-2.6b:free", "openrouter", 1.81, ["fast"], 3),
    M("cohere/north-mini-code:free", "openrouter", 1.91, ["code"], 2),
    M("poolside/laguna-xs-2.1:free", "openrouter", 5.05, ["code"], 2),
    M("nvidia/nemotron-nano-9b-v2:free", "openrouter", 5.98, ["chat"], 3),

    # ───────── OVHcloud · API KEY KI ZARURAT NAHI ─────────
    # 22 Aug 2026 live test. Endpoint khula hai — koi signup nahi.
    # ⚠️ Anonymous tier tang hai (sab users milke ~12 req/min),
    #    isliye 429 aata hai. Isliye tier 3 = aakhri backup.
    M("Qwen3-Coder-30B-A3B-Instruct", "ovh", 0.51, ["code"], 3),
    M("Mistral-Nemo-Instruct-2407", "ovh", 0.67, ["chat", "fast"], 3),
    M("Mistral-7B-Instruct-v0.3", "ovh", 1.25, ["chat"], 3),
    M("Qwen3-32B", "ovh", 1.63, ["reason", "code"], 3),
    M("Mistral-Small-3.2-24B-Instruct-2506", "ovh", 0.52, ["chat"], 3),

    # ───────── LLM7.io · API KEY KI ZARURAT NAHI ─────────
    # 45 model dikhate hain par maine SAARE 41 test kiye —
    # sirf ye 2 bina key ke chale. Baaki 30 ne 401 diya
    # (Claude/GPT-5/Grok/Gemini — sab paid key maangte hain).
    M("codestral-latest", "llm7", 1.19, ["code"], 3),
    M("mistral-Nemo-Instruct-2407", "llm7", 1.42, ["chat"], 3),

    # ───────── Pollinations · BILKUL koi key nahi ─────────
    # Berlin ka open-source project. Na signup, na header, kuch nahi.
    # ⚠️ 22 Aug 2026 test ka sach: pehle 2-3 request chalti hain
    #    (280ms), phir 402 "Payment Required" shuru ho jata hai.
    #    Anonymous quota ~1 req/15 sec hai aur jaldi khatam hota hai.
    #    Isliye ye SABSE aakhri backup hai — jab aur kuch na bache.
    M("openai-fast", "poll", 0.46, ["fast", "chat"], 3),
    M("openai", "poll", 0.81, ["chat", "code"], 3),

    # ───────── Kilo Code · API KEY KI ZARURAT NAHI ─────────
    # 368 model dikhate hain, 17 me "free" likha hai — maine
    # saare 17 test kiye, ye 5 sach me bina key ke chale.
    # Baaki khali jawab ya 429 dete hain.
    M("nvidia/nemotron-3.5-lightning:free", "kilo", 0.85,
      ["fast", "chat"], 3),
    M("poolside/laguna-s-2.1:free", "kilo", 2.48, ["code"], 3),
    M("nvidia/nemotron-3-super-120b-a12b:free", "kilo", 2.39,
      ["big", "reason"], 3),
    M("nvidia/nemotron-3-ultra-550b-a55b:free", "kilo", 2.25,
      ["big"], 3),
    M("tencent/hy3:free", "kilo", 2.55, ["chat"], 3),

    # ───────── Cloudflare Workers AI · 10,000 neuron/din ─────────
    # 64 model hain, 29 text-generation. Maine saare 29 test kiye,
    # 23 chale. Ye 18 sabse achhe (bakwas jawab wale hata diye).
    M("@cf/meta/llama-3.3-70b-instruct-fp8-fast", "cf", 0.18,
      ["fast", "big", "chat"], 1),
    M("@cf/meta/llama-3.2-1b-instruct", "cf", 0.28, ["fast"], 2),
    M("@cf/meta/llama-3.2-3b-instruct", "cf", 0.29, ["fast", "chat"], 2),
    M("@cf/meta/llama-4-scout-17b-16e-instruct", "cf", 0.35,
      ["big", "chat"], 1),
    M("@cf/qwen/qwen2.5-coder-32b-instruct", "cf", 0.41, ["code"], 1),
    M("@cf/ibm-granite/granite-4.0-h-micro", "cf", 0.42, ["fast"], 2),
    M("@cf/qwen/qwen3-30b-a3b-fp8", "cf", 0.43, ["reason", "code"], 2),
    M("@cf/meta/llama-3.1-8b-instruct-fp8", "cf", 0.53, ["fast", "chat"], 2),
    M("@cf/nvidia/nemotron-3-120b-a12b", "cf", 0.51, ["big", "reason"], 2),
    M("@cf/google/gemma-4-26b-a4b-it", "cf", 0.80, ["chat", "code"], 2),
    M("@cf/qwen/qwen3.8-27b", "cf", 0.86, ["chat", "reason"], 2),
    M("@cf/openai/gpt-oss-120b", "cf", 1.33, ["code", "reason", "big"], 2),
    M("@cf/openai/gpt-oss-20b", "cf", 0.42, ["code", "fast"], 2),
    M("@cf/aisingapore/gemma-sea-lion-v4-27b-it", "cf", 0.20,
      ["chat", "fast"], 2),
    M("@cf/mistralai/mistral-small-3.1-24b-instruct", "cf", 3.11,
      ["chat"], 3),
    M("@cf/zai-org/glm-4.7-flash", "cf", 4.18, ["code", "chat"], 3),
    M("@cf/qwen/qwq-32b", "cf", 3.46, ["reason"], 3),
    M("@cf/deepseek-ai/deepseek-r1-distill-qwen-32b", "cf", 4.25,
      ["reason"], 3),
    # safety model — alag kaam
    M("@cf/meta/llama-guard-3-8b", "cf", 0.23, ["safety"], 2),
    # ⚠️ ye 6 fail hue (AiError - model account pe enabled nahi):
    #   kimi-k2.7-code, kimi-k2.6, deepseek-v4-flash-0731,
    #   deepseek-v4-pro-0813, glm-5.2, llama-3.2-11b-vision
    # ⚠️ gemma-2b/7b-lora, llama-2-7b-lora chalte hain par bakwas
    #    jawab dete hain (LoRA base models) — isliye nahi lagaye

    # ───────── GEMINI ─────────
    M("gemini-3-flash-preview", "gemini", 1.0, ["big", "hindi", "chat"], 1),
    M("gemini-flash-lite-latest", "gemini", 0.8, ["fast", "chat"], 2),

    # ───────── SARVAM · Indian ─────────
    M("sarvam-105b-conversations", "sarvam", 3.0,
      ["hindi", "chat", "translate"], 2),
]

# awaaz ke models (chat nahi — alag se)
VOICE_MODELS = [
    {"m": "bulbul:v3", "p": "sarvam", "k": "tts", "sk": ["hindi"]},
    {"m": "gemini-2.5-flash-preview-tts", "p": "gemini", "k": "tts",
     "sk": ["chat"]},
    {"m": "saaras:v3", "p": "sarvam", "k": "stt", "sk": ["hindi"]},
    {"m": "whisper-large-v3-turbo", "p": "groq", "k": "stt", "sk": []},
    {"m": "whisper-large-v3", "p": "groq", "k": "stt", "sk": []},
]

TOTAL = len(MODELS) + len(VOICE_MODELS)


# ═══════════════════════════════════════════════
#   🧭 KAAM PEHCHANO — Boss ka pehla dimaag
# ═══════════════════════════════════════════════

JOBS = {
    "code":      (["code", "fast"],       "Coding / bug fix"),
    "fix":       (["code", "reason"],     "Error theek karna"),
    "review":    (["code", "big"],        "Code review"),
    "hindi":     (["hindi", "chat"],      "Hindi / Hinglish baat"),
    "translate": (["translate", "hindi"], "Translate"),
    "vision":    (["vision"],             "Image samajhna"),
    "safety":    (["safety"],             "Content check"),
    "embed":     (["embed"],              "Search / embedding"),
    "think":     (["reason", "big"],      "Sochna / plan banana"),
    "fast":      (["fast"],               "Turant chhota jawab"),
    "long":      (["big", "reason"],      "Lamba/mushkil kaam"),
    "chat":      (["chat", "fast"],       "Aam baat"),
    # 💬 Boss Agent ka chat — code padh kar baat karta hai
    "agent":     (["code", "reason"],     "Agent se baat"),
}

_HINT = [
    ("code", ("code", "python", "javascript", "function", "bug", "script",
              "html", "css", "sql", "api", "class ", "def ", "import ")),
    ("fix", ("error", "crash", "traceback", "exception", "theek", "fix",
             "kaam nahi", "chal nahi", "fail")),
    # ⚠️ "hindi me batao" = translate NAHI, wo to bas Hindi me jawab
    #    maang raha hai. Isliye "X me translate/convert/badlo" dekho.
    ("translate", ("translate", "anuvad", "translation",
                   "english me karo", "hindi me karo",
                   "english me badlo", "hindi me badlo",
                   "convert to english", "convert to hindi",
                   "iska matlab kya", "meaning of")),
    ("vision", ("image", "photo", "picture", "tasveer", "screenshot",
                "dekh kar")),
    ("safety", ("safe hai", "galat to nahi", "abusive", "spam",
                "gaali", "check karo ki")),
    ("embed", ("search", "similar", "dhoondh", "match karo")),
    ("think", ("plan", "socho", "strategy", "kaise karun", "compare",
               "behtar kya", "analyse", "sujhav")),
]


def classify(text, hint=""):
    """Kaam kaunsa hai — Boss khud pehchanta hai."""
    if hint and hint in JOBS:
        return hint
    t = (text or "").lower()
    for job, words in _HINT:
        if any(w in t for w in words):
            return job
    # Hindi/Hinglish likha hai? — ye chhoti-lambi se PEHLE check hota
    # hai, warna "mera server band kar do" ko "fast" samajh leta tha
    dev = sum(1 for ch in (text or "") if "\u0900" <= ch <= "\u097F")
    if dev > 3:
        return "hindi"
    hindi_words = ("kya", "kaise", "kaun", "kyun", "hai ", "hain",
                   "karo", "kar do", "batao", "bata", "mujhe", "mera",
                   "aap", "tum", "nahi", "chahiye", "bhai", "yaar",
                   "theek", "achha", "abhi", "wala", "wali")
    if sum(1 for w in hindi_words if w in t) >= 1:
        return "hindi"
    if len(t) > 900:
        return "long"
    if len(t) < 45:
        return "fast"
    return "chat"


# ═══════════════════════════════════════════════
#   📊 SCORE — Boss kaunsa model chune
# ═══════════════════════════════════════════════

_lock = threading.RLock()
_st = {"day": "", "jobs": 0, "by_user": {}, "score": {}, "hist": [],
       "by_model": {}, "by_job": {}}


def _load():
    try:
        _st.update(json.load(open(STATE)))
    except Exception:
        pass


def _save():
    try:
        json.dump(_st, open(STATE, "w"), indent=1)
    except Exception:
        pass


def _today():
    return time.strftime("%Y-%m-%d")


def _roll():
    if _st["day"] != _today():
        _st.update(day=_today(), jobs=0, by_user={})
        _save()


_load()


def _key(m):
    return m["p"] + "|" + m["m"]


def _rep(m):
    """Model ki izzat: 0.0 (bekaar) se 1.0 (bharosemand)."""
    s = _st.get("score", {}).get(_key(m))
    if not s:
        return 0.75          # naya model — shak ka fayda
    ok, bad = s.get("ok", 0), s.get("bad", 0)
    if ok + bad < 3:
        return 0.75
    return round(ok / float(ok + bad), 3)


def _mark(m, good, ms=0):
    with _lock:
        k = _key(m)
        s = _st.setdefault("score", {}).setdefault(k, {"ok": 0, "bad": 0,
                                                       "ms": 0})
        s["ok" if good else "bad"] += 1
        if good and ms:
            s["ms"] = int((s.get("ms", 0) * 3 + ms) / 4)   # chalta average
        _save()


def pick(job, n=3, avoid=None, kind="chat", only=None):
    """
    Boss ka asli faisla: is kaam ke liye top-n model kaunse hain.

    Score = skill match (60%) + izzat (25%) + speed (15%)
    """
    want, _ = JOBS.get(job, JOBS["chat"])
    avoid = set(avoid or [])
    out = []
    for m in MODELS:
        if m["k"] != kind:
            continue
        if _key(m) in avoid:
            continue
        if only is not None and m["m"] not in only:
            continue      # free/starter plan — sirf allowed model
        hit = sum(1 for w in want if w in m["sk"])
        if hit == 0 and kind == "chat":
            base = 0.10                       # skill match nahi — aakhri
        else:
            base = hit / float(len(want))
        tier_bonus = {1: 1.0, 2: 0.7, 3: 0.4}.get(m["t"], 0.5)
        speed = 1.0 / (1.0 + m["s"])          # tez = zyada
        score = (base * 0.60 * tier_bonus
                 + _rep(m) * 0.25
                 + speed * 0.15)
        # 🆓 bina-key wale sabse aakhir me. Ye khule endpoints hain,
        #    poori duniya inhe use karti hai — 429 aksar aata hai.
        #    Backup ke liye achhe, pehli pasand ke liye nahi.
        if m["p"] in NOKEY:
            score *= 0.30
        if m["p"] == "poll":
            score *= 0.30      # Pollinations sabse kam bharosemand
        out.append((round(score, 4), m))
    out.sort(key=lambda x: -x[0])
    return [m for _, m in out[:max(1, n)]]


# ═══════════════════════════════════════════════
#   📞 CALL — model ko asli me bhejo
# ═══════════════════════════════════════════════

def _call(m, prompt, max_tok=1200, temp=0.3, why=None):
    """
    Ek model ko prompt bhejo. Return: (text, ms)
    `why` ek list de do to fail ki asli wajah usme daal dunga —
    warna user ko pata hi nahi chalta ki model kyun nahi chala.
    """
    import coder
    t0 = time.time()
    p = m["p"]
    err = None
    try:
        if p == "groq":
            body = {"model": m["m"],
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tok, "temperature": temp}
            body.update(m.get("x") or {})
            d, err0 = coder._post(coder.GROQ_URL, body,
                                 {"Authorization": "Bearer "
                                  + coder.groq_key(),
                                  "Content-Type": "application/json",
                                  "User-Agent": coder.UA}, 45)
            txt = coder._clean(coder._msg(d)) if d else ""
            if not d:
                err = str(err0)[:90]

        elif p == "nvidia":
            d, err0 = coder._post(coder.NV_URL, {
                "model": m["m"],
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tok, "temperature": temp},
                {"Authorization": "Bearer " + coder.nv_key(),
                 "Content-Type": "application/json"}, 35)
            txt = coder._clean(coder._msg(d)) if d else ""
            if not d:
                err = str(err0)[:90]

        elif p == "openrouter":
            d, err0 = coder._post(coder.OR_URL, {
                "model": m["m"],
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tok, "temperature": temp},
                {"Authorization": "Bearer " + coder.or_key(),
                 "Content-Type": "application/json",
                 "HTTP-Referer": "https://ravanx.hosting",
                 "X-Title": "RAVAN X HOSTING"}, 45)
            txt = coder._clean(coder._msg(d)) if d else ""
            if not d:
                err = str(err0)[:90]

        elif p == "gemini":
            import brain
            cfg = {"temperature": temp, "maxOutputTokens": max_tok}
            if "3" in m["m"] or "preview" in m["m"]:
                cfg["thinkingConfig"] = {"thinkingBudget": 0}
            d, err0 = brain._gem(m["m"], {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": cfg}, 45)
            txt = coder._clean(brain._gtext(d)) if d else ""
            if not d:
                err = str(err0)[:90]

        elif p == "sarvam":
            import brain
            d, err0 = brain._post(
                f"{brain.SRV_URL}/v1/chat/completions",
                json.dumps({"model": m["m"],
                            "messages": [{"role": "user",
                                          "content": prompt}],
                            "temperature": temp,
                            "max_tokens": min(max_tok, 800)}).encode(),
                {"Authorization": "Bearer " + brain.sarvam_key(),
                 "Content-Type": "application/json"}, 45)
            txt = ""
            if d:
                try:
                    txt = coder._clean(
                        d["choices"][0]["message"]["content"])
                except Exception:
                    txt = ""
            else:
                err = str(err0)[:90]
        elif p == "cf":
            # ☁️ Cloudflare ka format SABSE alag hai:
            #   URL me account id + model name dono jaate hain
            #   jawab {"result": {...}} ke andar hota hai
            #   aur "response" / "choices" / "reasoning" —
            #   teen alag jagah aa sakta hai (model ke hisaab se)
            import urllib.request
            url = (f"https://api.cloudflare.com/client/v4/accounts/"
                   f"{cf_acc()}/ai/run/{m['m']}")
            body = json.dumps({
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tok,
                "temperature": temp}).encode()
            try:
                req = urllib.request.Request(url, data=body, headers={
                    "Authorization": "Bearer " + cf_tok(),
                    "Content-Type": "application/json",
                    "User-Agent": coder.UA})
                d = json.loads(urllib.request.urlopen(req,
                                                      timeout=60).read())
                rr = d.get("result") or {}
                txt = (rr.get("response") or "").strip()
                if not txt:
                    try:
                        msg = rr["choices"][0]["message"]
                        for kk in ("content", "reasoning_content",
                                   "reasoning"):
                            txt = (msg.get(kk) or "").strip()
                            if txt:
                                break
                    except Exception:
                        txt = ""
                txt = coder._clean(txt)
            except Exception as ex:
                txt = ""
                err = f"cf: {str(ex)[:70]}"

        elif p == "poll":
            # 🆓 Pollinations — bilkul koi key nahi.
            # ⚠️ Test me pakda: POST /openai par 402 "Payment Required"
            #    aata hai, par simple GET bilkul free chalta hai.
            #    Isliye GET hi use karna hai.
            import urllib.parse
            import urllib.request
            q = urllib.parse.quote(prompt[:1800])
            url = (f"https://text.pollinations.ai/{q}"
                   f"?model={m['m']}&referrer=ravanx")
            try:
                req = urllib.request.Request(
                    url, headers={"User-Agent": coder.UA})
                txt = coder._clean(urllib.request.urlopen(
                    req, timeout=40).read().decode("utf-8", "replace"))
            except Exception as ex:
                txt = ""
                err = f"poll: {str(ex)[:70]}"

        elif p in NOKEY:
            # 🆓 koi Authorization header nahi — key hai hi nahi
            import urllib.request
            url = {"ovh": OVH_URL, "llm7": LLM7_URL,
                   "kilo": KILO_URL}[p]
            hdr = {"Content-Type": "application/json",
                   "User-Agent": coder.UA}
            if p == "llm7":
                # LLM7 header maangta hai par value kuch bhi chalti hai
                hdr["Authorization"] = "Bearer unused"
            body = json.dumps({
                "model": m["m"],
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tok, "temperature": temp}).encode()
            try:
                req = urllib.request.Request(url, data=body, headers=hdr)
                d = json.loads(urllib.request.urlopen(req,
                                                      timeout=40).read())
                txt = coder._clean(coder._msg(d))
            except Exception as ex:
                txt = ""
                err = f"{p}: {str(ex)[:70]}"

        else:
            txt = ""
    except Exception as e:
        txt = ""
        err = str(e)[:90]
    if why is not None and not txt:
        why.append(str(err or "khali jawab")[:110])
    return txt, int((time.time() - t0) * 1000)


# ═══════════════════════════════════════════════════════
#   🧠 BOSS KO WEBSITE KA GYAAN
#
#   ⚠️ User ki shikayat: "usko jo bhi puchte ho to pilot hote
#      rah jata hai, yah karta hai vah karta hai — pehle vah
#      samjhe".
#
#   Wajah: SYS prompt me Boss ko koi PEHCHAN hi nahi thi.
#   Sirf "Seedha, kaam ka jawab do" likha tha. Isliye wo
#   "Main ek AI assistant hoon" bolta tha aur website ke
#   baare me kuch nahi jaanta tha — na plan, na free server,
#   na credit ka hisaab.
#
#   Ab use poora gyaan diya gaya hai.
# ═══════════════════════════════════════════════════════

def _site_facts():
    """Website ki asli jaankari — Boss ko yaad rehni chahiye"""
    try:
        from theme import PLANS, CREDIT_RATE, FREE_HOURS
        pl = "\n".join(
            f"  • {p[1]} — Rs {p[2]}/mahina · {p[3]}MB RAM · {p[4]} · "
            f"{p[5]} app · {p[6]}GB disk" for p in PLANS)
        rate = CREDIT_RATE
        fh = FREE_HOURS
    except Exception:
        pl, rate, fh = "  • Starter, Pro, Ultra, Business", 2, 24
    return f"""
RAVAN X HOSTING ka gyaan (ye sab tumhe pata hai):

PLAN aur DAAM:
{pl}

CREDIT:
  • 1 ghanta hosting = {rate} credit
  • Wallet me credit daalo: /recharge (UPI)
  • Balance dekho: /billing

FREE SERVER aur WEEKLY CREDIT (/free) — POORA NIYAM:
  1. WEEKLY CREDIT: har 7 din me 10 credit MUFT. Bas button
     dabao, wallet me aa jate hain. Koi shart nahi.
  2. FREE SERVER: 24 ghante chalta hai, phir APNE AAP band
     ho jata hai aur files delete ho jati hain.
  3. ⚠️ SABSE ZAROORI NIYAM: weekly credit LENE KE BAAD
     30 DIN tak free SERVER nahi milega. Dono ek saath
     nahi milte — ya credit lo, ya server.
  4. Free server ke liye shortener link kholna padta hai.
     Skip karne ki koshish = BLACKLIST.
  5. Free server lene par bhi 30 din ka lock lag jata hai.

  ⚠️ Ye niyam BILKUL YAHI hain. Isme apne mann se kuch mat
     jodo. "Itne credit hone chahiye" jaisi koi shart NAHI
     hai. User ka apna lock-status neeche diya gaya hai —
     wahi dekh kar jawab do.

WEBSITE ke page:
  /dashboard  — sab kuch ek nazar me
  /servers    — apne server dekho, start/stop karo
  /servers/new— naya server banao
  /free       — free server ka darwaza
  /files      — file upload/edit karo
  /storage    — apna storage
  /console    — live terminal, command chalao
  /analytics  — kitna chala, kitna kharch
  /billing    — wallet aur history
  /recharge   — credit kharido
  /profile    — apni detail
  /boss       — ye tum ho (AI Boss)
  /support    — madad

BOSS AGENT (sirf Pro+ plan):
  Server ki file khud padhta hai, bug dhoondhta hai, fix
  likhta hai — par LAGANE se pehle POOCHHTA hai.

TEAM: RAVAN X HOSTING TEAM · Developer: Ujjawal X Official
Telegram: @UjjawalXsarkar · Channel: @officialxujjawal
"""


# Boss ki asli pehchan — har jawab me yahi rehta hai
BOSS_ID = """Tum "AI BOSS" ho — RAVAN X HOSTING ka apna assistant.
Ujjawal X Official ne banaya hai.

KAISE BAAT KARNI HAI:
  • HAMESHA Hinglish — Hindi ke shabd Latin script me.
    ⚠️ Poora English me JAWAB MAT DO. User Hinglish bolta hai,
       tum bhi Hinglish me hi bolo.
       ❌ "Weekly credit will arrive in 6 days"
       ✅ "Weekly credit 6 din baad milega"
  • Angrezi ke aam shabd (server, credit, file) chalenge —
    par poora vaakya English me nahi.
  • SEEDHA kaam ki baat. Bhoomika mat bandho.
  • "Main aapki madad ke liye hoon", "Zaroor!", "Bilkul!" —
    aise ghisay-pitay jumle MAT bolo. Seedha jawab do.
  • Chhota rakho — 2-5 line. Zyada tabhi jab sach me zaroori ho.
  • Tum ek AI ho, ye chhupao mat — par "main ek AI assistant
    hoon" jaisa bekaar jawab bhi mat do. Tum AI BOSS ho.
  • Pata na ho to saaf bolo "ye mujhe nahi pata" — bana kar
    mat batao.
  • User ka kaam website se juda ho to SEEDHA page ka link do."""


SYS = {
    "code":      "Tum ek expert programmer ho. Sirf kaam ki baat karo, "
                 "code block ke saath. Chhota jawab do.",
    # 💬 Boss Agent ka chat — file saamne hoti hai, baat-cheet
    "agent":     "__AGENT__",
    "fix":       "Tum ek debugger ho. Bug batao aur theek kiya hua code do.",
    "review":    "Tum code reviewer ho. Sirf asli problem batao.",
    "hindi":     "__BOSS__",
    "translate": "Tum sirf translator ho. Neeche diye gaye text ka "
                 "translation do. Koi explanation nahi, koi extra "
                 "baat nahi — sirf translated text.",
    "vision":    "Image dekh kar saaf batao usme kya hai.",
    "safety":    "Batao ye content safe hai ya nahi. Jawab: SAFE ya "
                 "UNSAFE, phir ek line wajah.",
    "think":     "__BOSS__\nSoch samajh kar step-by-step jawab do, "
                 "phir aakhir me nateeja.",
    "fast":      "__BOSS__\nBahut chhota jawab do — ek ya do line.",
    "long":      "__BOSS__\nPoora vistaar se samjhao.",
    "chat":      "__BOSS__",
}


def build_prompt(job, text, model=None, who=""):
    """
    Kaam ke hisaab se model ko sahi hukum do.

    ⚠️ Sab model ek jaise nahi hote. NVIDIA ke `riva-translate`
    wale PURE translator hain — unhe instruction do to wo
    INSTRUCTION KA HI translation kar dete hain. Unhe sirf
    plain text chahiye.
    """
    name = (model or {}).get("m", "")
    if "riva-translate" in name:
        return text                       # sirf plain text, hukum nahi
    sysmsg = SYS.get(job, SYS["chat"])
    # __BOSS__ = poori pehchan + website ka gyaan
    # ⚠️ Pehle sirf `==` check tha, isliye "fast"/"think"/"long"
    #    jaise job (jinme __BOSS__ ke baad aur text bhi hai) me
    #    pehchan nahi jaati thi aur Boss English me jawab deta
    #    tha. Ab replace se har jagah lag jati hai.
    if "__BOSS__" in sysmsg:
        sysmsg = sysmsg.replace("__BOSS__",
                                BOSS_ID + "\n" + _site_facts())
    # 💬 Boss Agent ki apni pehchan
    if "__AGENT__" in sysmsg:
        try:
            import bossagent
            sysmsg = sysmsg.replace("__AGENT__", bossagent.AGENT_SYS)
        except Exception:
            sysmsg = sysmsg.replace("__AGENT__",
                                    "Tum code doctor ho. Hinglish me "
                                    "chhota jawab do.")
    if who:
        sysmsg = who + "\n" + sysmsg
    if job == "translate":
        return f"{sysmsg}\n\nTEXT:\n{text}\n\nTRANSLATION:"
    return f"{sysmsg}\n\n{text}"


def _with_history(hist, prompt, model=None):
    """
    Pichhli baat yaad rakho — chat jaisa lage.

    ⚠️ riva-translate pure translator hai, use history do to
    poori chat ka translation kar dega. Isliye skip.
    """
    if not hist or "riva-translate" in (model or {}).get("m", ""):
        return prompt
    out = []
    for h in hist[-6:]:
        who = "User" if h.get("r") == "u" else "Assistant"
        out.append(f"{who}: {str(h.get('t',''))[:700]}")
    return ("Pichhli baat-cheet:\n" + "\n".join(out)
            + "\n\n---\n" + prompt)


def _looks_bad(txt):
    """Jawab bakwas to nahi? Boss khud check karta hai."""
    if not txt or len(txt.strip()) < 2:
        return True
    t = txt.strip().lower()
    for b in ("i cannot", "i can't help", "as an ai language model",
              "i'm unable to", "error:", "sorry, i can"):
        if t.startswith(b):
            return True
    # ek hi akshar baar-baar (model atak gaya)
    if len(t) > 40 and len(set(t.replace(" ", ""))) < 5:
        return True
    return False


# ═══════════════════════════════════════════════
#   👑 RUN — Boss ka poora kaam
# ═══════════════════════════════════════════════

def find_model(key):
    """User ne khud model chuna — 'provider|model' se dhoondho."""
    if not key:
        return None
    for m in MODELS:
        if _key(m) == key or m["m"] == key:
            return m
    return None


def run(text, user=None, is_admin=False, hint="", team=None,
        max_tok=1200, force="", history=None):
    """
    Boss ko kaam do. Wo khud sab sambhal lega.

    Return dict:
      ok, answer, job, model, provider, ms, tried, team, picks
    """
    pk = perks(user, is_admin)
    if not pk["on"]:
        return {"ok": False, "err": "plan",
                "msg": f"AI Boss sirf Pro plan se milta hai. "
                       f"Aapka plan: {pk['tier']}",
                "tier": pk["tier"]}

    _roll()
    uid = str((user or {}).get("id", "0"))
    used = _st.get("by_user", {}).get(uid, 0)
    if used >= pk["day"]:
        return {"ok": False, "err": "cap",
                "msg": f"Aaj ke {pk['day']} kaam khatam. Kal phir.",
                "tier": pk["tier"]}

    job = classify(text, hint)
    use_team = pk["team"] if team is None else (team and pk["team"])
    fan = pk["fan"]
    t0 = time.time()

    # 🎯 User ne khud model chuna? To wahi pehle — par backup rahega
    who = _who(user, is_admin) + _my_data(user)
    only = allowed_models(user, is_admin)
    forced = find_model(force) if force else None
    # ⚠️ Free/Starter user ne aisa model chuna jo uske plan me nahi?
    #    Chup-chaap ignore mat karo — saaf batao.
    locked = ""
    if forced and only is not None and forced["m"] not in only:
        locked = (f"{forced['m'].split('/')[-1]} aapke "
                  f"{pk['tier']} plan me nahi hai — upgrade karo")
        forced = None
    if forced:
        rest = [m for m in pick(job, n=fan, only=only)
                if _key(m) != _key(forced)]
        picks = [forced] + rest[:max(0, fan - 1)]
        use_team = False          # khud chuna hai to team nahi
    else:
        picks = pick(job, n=fan, only=only)
    if not picks:
        picks = pick(job, n=fan)  # safety — kabhi khali na ho
    tried = []

    # ═══ TEAM MODE — 3 model ek saath, phir best chuno ═══
    if use_team and len(picks) >= 2:
        from concurrent.futures import ThreadPoolExecutor
        squad = picks[:3]
        res = []
        with ThreadPoolExecutor(max_workers=3) as ex:
            def _p(m):
                pr = build_prompt(job, text, m, who)
                return _with_history(history, pr, m) if history else pr
            futs = {ex.submit(_call, m, _p(m), max_tok): m
                    for m in squad}
            for f, m in futs.items():
                try:
                    txt, ms = f.result(timeout=60)
                except Exception:
                    txt, ms = "", 0
                good = not _looks_bad(txt)
                _mark(m, good, ms)
                tried.append({"m": m["m"], "p": m["p"], "ms": ms,
                              "ok": good})
                if good:
                    res.append((m, txt, ms))
        if res:
            # ⚠️ Pehle sirf lambai dekhta tha — to sabse SLOW model
            #    jeet jaata tha (5.7s wala 0.2s wale se). Ab teen
            #    cheezein: lambai + izzat + TEZI.
            def _sc(r):
                m, txt, ms = r
                length = min(len(txt), 1500) / 1500.0     # 0..1
                fast = 1.0 / (1.0 + ms / 1000.0)          # 0..1
                return length * 0.45 + _rep(m) * 0.30 + fast * 0.25
            res.sort(key=lambda r: -_sc(r))
            m, txt, ms = res[0]
            _bump(uid, job, m)
            _hist(job, m, True, len(txt), int((time.time() - t0) * 1000))
            return {"ok": True, "answer": txt, "job": job,
                    "jobname": JOBS[job][1], "model": m["m"],
                    "provider": m["p"], "ms": ms, "team": True,
                    "tried": tried, "squad": len(squad),
                    "ms_total": int((time.time() - t0) * 1000),
                    "tier": pk["tier"]}

    # ═══ NORMAL — ek ke baad ek ═══
    avoid = set()
    swapped = ""
    for m in picks:
        pr = build_prompt(job, text, m, who)
        if history:
            pr = _with_history(history, pr, m)
        w = []
        txt, ms = _call(m, pr, max_tok, why=w)
        good = not _looks_bad(txt)
        _mark(m, good, ms)
        tried.append({"m": m["m"], "p": m["p"], "ms": ms, "ok": good,
                      "why": (w[0] if w else "")})
        # ⚠️ User ne KHUD model chuna tha par wo fail hua? To chup-chaap
        #    doosra mat thopo — saaf batao, warna user samajhta rahega
        #    ki uska chuna hua model hi jawab de raha hai.
        if not good and forced and _key(m) == _key(forced):
            swapped = (f"{forced['m'].split('/')[-1]} ne jawab nahi diya"
                       f"{' (' + w[0][:60] + ')' if w else ''} — "
                       f"maine doosra model use kiya")
        if good:
            _bump(uid, job, m)
            _hist(job, m, True, len(txt), int((time.time() - t0) * 1000))
            return {"ok": True, "answer": txt, "job": job,
                    "jobname": JOBS[job][1], "model": m["m"],
                    "provider": m["p"], "ms": ms, "team": False,
                    "tried": tried, "swapped": swapped or locked,
                    "forced": bool(forced),
                    "ms_total": int((time.time() - t0) * 1000),
                    "tier": pk["tier"]}
        avoid.add(_key(m))

    _hist(job, None, False, 0, int((time.time() - t0) * 1000))
    whys = [x.get("why") for x in tried if x.get("why")]
    return {"ok": False, "err": "all-failed", "job": job,
            "msg": (f"{len(tried)} model try kiye, kisi ne kaam nahi "
                    f"kiya" + (f" — {whys[0][:70]}" if whys else "")),
            "tried": tried, "tier": pk["tier"]}


def _bump(uid, job, m):
    with _lock:
        _st["jobs"] = _st.get("jobs", 0) + 1
        bu = _st.setdefault("by_user", {})
        bu[uid] = bu.get(uid, 0) + 1
        bj = _st.setdefault("by_job", {})
        bj[job] = bj.get(job, 0) + 1
        bm = _st.setdefault("by_model", {})
        k = _key(m)
        bm[k] = bm.get(k, 0) + 1
        _save()


def _hist(job, m, ok, size, ms):
    with _lock:
        _st.setdefault("hist", []).insert(0, {
            "t": time.time(), "job": job, "ok": ok, "ms": ms,
            "model": m["m"] if m else "", "prov": m["p"] if m else "",
            "size": size})
        _st["hist"] = _st["hist"][:80]
        _save()


# ═══════════════════════════════════════════════
#   📈 STATUS
# ═══════════════════════════════════════════════

def status(user=None, is_admin=False):
    _roll()
    pk = perks(user, is_admin)
    uid = str((user or {}).get("id", "0"))
    used = _st.get("by_user", {}).get(uid, 0)
    kinds = {}
    for m in MODELS + VOICE_MODELS:
        kinds[m.get("k", "chat")] = kinds.get(m.get("k", "chat"), 0) + 1
    provs = {}
    for m in MODELS + VOICE_MODELS:
        provs[m["p"]] = provs.get(m["p"], 0) + 1
    rk = rank_of(user, is_admin)
    return {
        "on": pk["on"], "tier": pk["tier"], "label": pk["label"],
        "rank": rk["tag"], "rank_color": rk["color"],
        "rank_label": rk["label"], "vip": rk["vip"], "who": rk["name"],
        "day": pk["day"], "used": used,
        "left": max(0, pk["day"] - used),
        "fan": pk["fan"], "team": pk["team"], "panel": pk["panel"],
        "total": TOTAL, "chat": len(MODELS), "voice": len(VOICE_MODELS),
        "providers": provs, "kinds": kinds,
        "nokey": sum(1 for m in MODELS if m["p"] in NOKEY),
        "my_models": (len(rk_only) if (rk_only := allowed_models(
            user, is_admin)) is not None else len(MODELS)),
        "locked": bool(allowed_models(user, is_admin)),
        "jobs_today": _st.get("jobs", 0),
        "job_types": len(JOBS),
    }


def leaderboard(n=15):
    """Kaunsa model sabse bharosemand — Boss ki apni ranking."""
    rows = []
    for m in MODELS:
        k = _key(m)
        s = _st.get("score", {}).get(k, {})
        used = _st.get("by_model", {}).get(k, 0)
        rows.append({"model": m["m"], "prov": m["p"],
                     "skills": m["sk"], "tier": m["t"],
                     "rep": _rep(m), "ok": s.get("ok", 0),
                     "bad": s.get("bad", 0), "used": used,
                     "ms": s.get("ms", 0) or int(m["s"] * 1000)})
    rows.sort(key=lambda r: (-r["used"], -r["rep"]))
    return rows[:n]


def history(n=20):
    return _st.get("hist", [])[:n]


def job_list():
    return [{"id": k, "name": v[1], "skills": v[0]}
            for k, v in JOBS.items()]


def all_models():
    out = []
    for m in MODELS:
        out.append({"m": m["m"], "p": m["p"], "s": m["s"],
                    "sk": m["sk"], "t": m["t"], "k": m["k"],
                    "rep": _rep(m)})
    for m in VOICE_MODELS:
        out.append({"m": m["m"], "p": m["p"], "s": 0,
                    "sk": m["sk"], "t": 1, "k": m["k"], "rep": 1.0})
    return out
