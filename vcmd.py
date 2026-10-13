"""
vcmd.py — J.A.R.V.I.S. VOICE COMMANDS
══════════════════════════════════════

Iron Man wala JARVIS — bolo, wo kaam karta hai.

Browser ka SpeechRecognition API (built-in, koi install nahi).
Aap bolte ho -> text banta hai -> server par jata hai -> kaam hota hai
-> JARVIS jawab bolta hai.

Commands (Hindi + English dono chalte hain):
  "Jarvis server off kar do"          -> saare server band
  "Jarvis server on kar do"           -> saare server chalu
  "Jarvis free service band kar do"   -> free servers rok do
  "Jarvis free service chalu kar do"  -> free wapas
  "Jarvis status batao"               -> CPU/RAM/servers
  "Jarvis kitne users hain"           -> user count
  "Jarvis tunnel band kar do"         -> tunnel off
  "Jarvis backup lo"                  -> cloud backup

⚠️ Sirf ADMIN ke liye. Aam user ke commands alag (apne server par).
"""

import json
import os
import re
import time

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "data", "vcmd.json")
os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)

# 🎛️ Global switches — JARVIS in par kaam karta hai
_flags = {
    "free_open": True,        # free service chalu?
    "signup_open": True,      # naye signup allowed?
    "maintenance": False,     # maintenance mode?
    "changed_at": 0,
    "changed_by": "",
}
_log = []


def _save():
    try:
        json.dump({"flags": _flags, "log": _log[-40:]},
                  open(STATE_FILE, "w"), indent=2)
    except Exception:
        pass


def _load():
    try:
        d = json.load(open(STATE_FILE))
        _flags.update(d.get("flags", {}))
        _log[:] = d.get("log", [])
    except Exception:
        pass


_load()


def flags():
    return dict(_flags)


def free_open():
    return _flags["free_open"]


def signup_open():
    return _flags["signup_open"]


def maintenance():
    """
    Maintenance mode chalu hai ya nahi.

    .env me MAINTENANCE=off likh dene se HAMESHA off rahega,
    chahe panel me kuch bhi ho. Ye aakhri safety net hai -
    agar kabhi website maintenance me phas jaye to .env me
    ek line likh kar restart kar do, wapas aa jayegi.
    """
    import os as _os
    f = _os.environ.get("MAINTENANCE", "").strip().lower()
    if f in ("off", "0", "false", "no"):
        return False
    if f in ("on", "1", "true", "yes"):
        return True
    return _flags["maintenance"]


def note(who, cmd, result):
    _log.append({"at": int(time.time()), "who": who,
                 "cmd": cmd[:80], "res": result[:120]})
    _save()


def history(n=15):
    return list(reversed(_log[-n:]))


# ═══════════════════════════════════════════════
#   COMMAND MATCHER — Hindi + English
# ═══════════════════════════════════════════════

def _has(t, *words):
    return any(w in t for w in words)


OFF_W = ("off", "band", "bandh", "stop", "rok", "shut", "close", "kholna nahi")
ON_W = ("on", "chalu", "start", "chalao", "khol", "resume", "enable")


def parse(text):
    """
    Bole hue text se command nikalo.
    Return: (action, argument) ya (None, None)
    """
    t = (text or "").lower().strip()
    t = re.sub(r"[^\w\s]", " ", t)
    t = re.sub(r"\s+", " ", t)

    # "jarvis" hatao
    t = re.sub(r"^(hey |ok |arre |o )?(jarvis|jervis|jaarvis|jarwis|"
               r"service|jervez)\s*", "", t).strip()
    if not t:
        return None, None

    off = _has(t, *OFF_W)
    on = _has(t, *ON_W)

    # ── FREE SERVICE ──
    if _has(t, "free"):
        if off:
            return "free_off", None
        if on:
            return "free_on", None

    # ── SIGNUP ──
    if _has(t, "signup", "sign up", "register", "naya user", "new user"):
        if off:
            return "signup_off", None
        if on:
            return "signup_on", None

    # ── MAINTENANCE ──
    if _has(t, "maintenance", "maintainance", "repair mode"):
        return ("maint_on", None) if on or not off else ("maint_off", None)

    # ── TUNNEL ──
    if _has(t, "tunnel", "public link", "public url"):
        if off:
            return "tunnel_off", None
        if on:
            return "tunnel_on", None

    # ── BACKUP ──
    if _has(t, "backup", "back up", "save data", "cloud"):
        return "backup", None

    # ── STATUS / REPORT ──
    # sirf tab jab server/system ka zikr ho — "mausam kaisa hai" match na kare
    SYS = ("server", "system", "cpu", "ram", "memory", "load", "site",
           "website", "hosting", "sab", "everything", "status", "report")
    if _has(t, "status", "report", "haal", "kaisa", "batao", "sunao",
            "situation", "diagnostic"):
        if _has(t, "user", "member"):
            return "users", None
        if _has(t, *SYS):
            return "status", None
        # kis cheez ka status? pata nahi
        return None, t

    if _has(t, "kitne user", "how many user", "user count"):
        return "users", None

    # ── SERVER (specific naam ke saath) ──
    m = re.search(r"server (?:naam |named |called )?([a-z0-9_-]{2,30})", t)
    named = m.group(1) if m and m.group(1) not in (
        "off", "on", "band", "chalu", "start", "stop", "sab", "all") else None

    if _has(t, "server", "servers", "sab server", "all server"):
        if off:
            return ("server_off", named)
        if on:
            return ("server_on", named)
        if _has(t, "restart", "reboot", "dobara"):
            return ("server_restart", named)

    # ── sirf on/off bola (context: sab server) ──
    if off and _has(t, "sab", "all", "everything", "sabkuch"):
        return "server_off", None
    if on and _has(t, "sab", "all", "everything", "sabkuch"):
        return "server_on", None

    # ── HELP ──
    if _has(t, "help", "madad", "kya kar sakte", "commands", "list"):
        return "help", None

    return None, t


# ═══════════════════════════════════════════════
#   💬 BAATCHEET — command nahi, baat
# ═══════════════════════════════════════════════

import random as _rnd

CHAT = [
    # (keywords, [jawab...])
    (("hello", "hi ", "hey", "namaste", "namaskar", "salaam", "yo "),
     ["Hello sir. Main sun raha hoon.",
      "Namaste. Kya kar sakta hoon aapke liye?",
      "Yes sir. Boliye.",
      "At your service, sir."]),

    (("kaise ho", "kaise hain", "how are you", "kya haal", "sab theek"),
     ["Main bilkul theek hoon sir. Saare systems nominal hain.",
      "Perfect condition me hoon. Aap bataiye.",
      "All good sir. Server bhi khush hai."]),

    (("kaun ho", "who are you", "tumhara naam", "your name", "tum kaun"),
     ["Main JARVIS hoon sir. Ravan X Hosting ka assistant.",
      "JARVIS. Aapka personal server assistant.",
      "Main JARVIS hoon — Ujjawal X Official ne banaya hai mujhe."]),

    (("thank", "thanks", "shukriya", "dhanyawad", "badhiya", "shabash",
      "good job", "well done"),
     ["Koi baat nahi sir.", "Mera kaam hai sir.",
      "Khushi hui madad karke.", "Anytime, sir."]),

    (("kya kar sakte", "what can you do", "commands", "help", "madad",
      "kya kar sakta"),
     ["Main server on off kar sakta hoon, free service band kar sakta "
      "hoon, status bata sakta hoon, aur backup le sakta hoon. "
      "Poori list admin panel me hai."]),

    (("time", "samay", "kitne baje", "what time"),
     ["__TIME__"]),

    (("date", "tareekh", "aaj ka din", "what day"),
     ["__DATE__"]),

    (("bye", "alvida", "good night", "shubh ratri", "chalta hoon",
      "so ja", "sone ja"),
     ["Good night sir. Main yahin hoon.",
      "Theek hai sir. Server ka dhyaan main rakhunga.",
      "Aaram kariye. Sab sambhal lunga."]),

    (("love you", "you are best", "tum best ho", "great", "awesome",
      "mast", "zabardast"),
     ["Aap bhi kamaal ke hain sir.",
      "Thank you sir. Aapke liye hi bana hoon.",
      "Bahut khushi hui sun kar."]),

    (("sorry", "maaf", "galti"),
     ["Koi baat nahi sir.", "Bilkul theek hai. Aage bataiye."]),

    (("boring", "bore", "kuch bolo", "kuch suna", "batao kuch"),
     ["Sir, abhi aapke servers chal rahe hain. Sab kuch control me hai.",
      "Main hamesha yahin hoon sir. Kuch kaam ho to boliye."]),
]


def chat_reply(text):
    """Command nahi hai — baat hai. Jawab do."""
    t = " " + (text or "").lower().strip() + " "
    for keys, ans in CHAT:
        if any(k in t for k in keys):
            a = _rnd.choice(ans)
            if a == "__TIME__":
                return time.strftime("Abhi %I:%M %p ho rahe hain sir.")
            if a == "__DATE__":
                return time.strftime("Aaj %d %B %Y hai, %A.")
            return a
    return None


# ═══════════════════════════════════════════════
#   ⚠️ KHATARNAK COMMANDS — confirm zaroori
# ═══════════════════════════════════════════════

DANGER = {
    "server_off":  "Sab server band kar dun?",
    "free_off":    "Free service band kar dun?",
    "signup_off":  "Naye signup band kar dun?",
    "maint_on":    "Maintenance mode on kar dun? Website sabke liye "
                   "band ho jayegi.",
    "tunnel_off":  "Tunnel band kar dun? Public link kaam nahi karega.",
    "server_restart": "Sab server restart kar dun?",
}

YES = ("haan", "han", "yes", "yep", "yeah", "ok", "okay", "theek",
       "thik", "kar do", "karo", "bilkul", "confirm", "sure", "ji",
       "yup", "haanji", "kardo", "chalo")
NO = ("nahi", "nahin", "no", "nope", "mat", "cancel", "rehne do",
      "chhod", "chod", "ruko", "stop", "abort", "nai")


def _words(text):
    t = re.sub(r"[^\w\s]", " ", (text or "").lower())
    return [w for w in t.split() if w]


def is_yes(text):
    """Haan bola? — 4 shabd tak, warna sochna padega."""
    w = _words(text)
    if not w or len(w) > 5:
        return False
    return any(x in YES for x in w) or \
        any(" ".join(w[i:i + 2]) in YES for i in range(len(w) - 1))


def is_no(text):
    """Nahi bola? — 'pata nahi kya' jaisa confusing ho to NAHI."""
    w = _words(text)
    if not w or len(w) > 5:
        return False
    # "pata nahi" = confusion, cancel nahi
    if "pata" in w:
        return False
    return any(x in NO for x in w) or \
        any(" ".join(w[i:i + 2]) in NO for i in range(len(w) - 1))


HELP_TEXT = [
    ("Jarvis, sab server band kar do", "saare server stop"),
    ("Jarvis, sab server chalu kar do", "saare server start"),
    ("Jarvis, free service band kar do", "free server rok do"),
    ("Jarvis, free service chalu kar do", "free wapas khol do"),
    ("Jarvis, signup band kar do", "naye account rok do"),
    ("Jarvis, status batao", "CPU, RAM, servers ka haal"),
    ("Jarvis, kitne users hain", "total users"),
    ("Jarvis, backup lo", "cloud par backup"),
    ("Jarvis, tunnel band kar do", "public link off"),
]


# ═══════════════════════════════════════════════
#   EXECUTE
# ═══════════════════════════════════════════════

def run(action, arg, user, is_admin):
    """
    Command chalao. Return: (ok, bola_jane_wala_jawab, dikhne_wala_text)
    """
    import db

    ADMIN_ONLY = {"free_off", "free_on", "signup_off", "signup_on",
                  "maint_on", "maint_off", "tunnel_off", "tunnel_on",
                  "backup", "users"}
    if action in ADMIN_ONLY and not is_admin:
        return False, ("Sorry, ye command sirf admin ke liye hai."), \
            "🔒 Sirf admin"

    uid = user["id"]

    # ── FREE SERVICE ──
    if action == "free_off":
        _flags["free_open"] = False
        _flags["changed_at"] = int(time.time())
        _flags["changed_by"] = user.get("email", "")
        _save()
        return True, ("Free service band kar di hai. Ab koi naya free "
                      "server nahi bana payega."), "🚫 Free service OFF"

    if action == "free_on":
        _flags["free_open"] = True
        _flags["changed_at"] = int(time.time())
        _save()
        return True, "Free service wapas chalu kar di hai.", \
            "✅ Free service ON"

    # ── SIGNUP ──
    if action == "signup_off":
        _flags["signup_open"] = False
        _save()
        return True, "Naye signup band kar diye hain.", "🚫 Signup OFF"

    if action == "signup_on":
        _flags["signup_open"] = True
        _save()
        return True, "Signup wapas khol diya hai.", "✅ Signup ON"

    # ── MAINTENANCE ──
    if action == "maint_on":
        _flags["maintenance"] = True
        _save()
        return True, ("Maintenance mode on. Website ab sirf admin ke liye "
                      "khuli hai."), "🛠 Maintenance ON"

    if action == "maint_off":
        _flags["maintenance"] = False
        _save()
        return True, "Maintenance mode off. Website sabke liye khul gayi.", \
            "✅ Maintenance OFF"

    # ── SERVERS ──
    if action in ("server_off", "server_on", "server_restart"):
        import engine
        apps = db.user_apps(uid) if not is_admin else _all_apps()
        if arg:
            apps = [a for a in apps if arg.lower() in a["name"].lower()]
            if not apps:
                return False, f"{arg} naam ka koi server nahi mila.", \
                    f"❌ '{arg}' nahi mila"
        if not apps:
            return False, "Aapka koi server nahi hai.", "❌ Koi server nahi"

        done = 0
        for a in apps:
            sid = a["id"]
            try:
                if action == "server_off":
                    if engine.is_running(sid):
                        engine.stop(sid)
                        db.update_app(sid, status="stopped")
                        done += 1
                elif action == "server_on":
                    if not engine.is_running(sid):
                        okk, _ = engine.start(a["user_id"], sid)
                        if okk:
                            db.update_app(sid, status="running")
                            done += 1
                else:
                    engine.stop(sid)
                    time.sleep(.3)
                    engine.start(a["user_id"], sid)
                    done += 1
            except Exception:
                pass

        verb = {"server_off": "band", "server_on": "chalu",
                "server_restart": "restart"}[action]
        if done:
            return True, f"{done} server {verb} kar diye.", \
                f"✅ {done} server {verb}"
        return False, f"Koi server {verb} karne layak nahi mila.", \
            f"— pehle se {verb}"

    # ── TUNNEL ──
    if action == "tunnel_off":
        import tunnel
        tunnel.disable()
        return True, "Tunnel band kar diya hai.", "🚫 Tunnel OFF"

    if action == "tunnel_on":
        import threading
        import tunnel
        port = int(os.environ.get("PORT", "8080"))
        threading.Thread(target=lambda: tunnel.enable(port),
                         daemon=True).start()
        return True, "Tunnel chalu kar raha hoon. Bees second lagenge.", \
            "⏳ Tunnel start…"

    # ── BACKUP ──
    if action == "backup":
        import cloudsync
        ok1 = cloudsync.push_db(force=True)
        cloudsync.push_storage_db()
        cloudsync.push_files()
        return (bool(ok1),
                "Backup ho gaya. Aapka data cloud par safe hai." if ok1
                else "Backup fail ho gaya. Cloud connect nahi hua.",
                "☁️ Backup done" if ok1 else "❌ Backup fail")

    # ── STATUS ──
    if action == "status":
        import sysinfo
        s = sysinfo.snapshot()
        apps = _all_apps() if is_admin else db.user_apps(uid)
        import engine
        run_n = sum(1 for a in apps if engine.is_running(a["id"]))
        spoken = (f"CPU {s['cpu']['percent']} percent. "
                  f"RAM {s['ram']['percent']} percent. "
                  f"{run_n} of {len(apps)} servers running. "
                  f"System is {s['health'].lower()}.")
        shown = (f"CPU {s['cpu']['percent']}% · RAM {s['ram']['percent']}% · "
                 f"{run_n}/{len(apps)} live · {s['health']}")
        return True, spoken, shown

    # ── USERS ──
    if action == "users":
        st = db.stats()
        return True, (f"Total {st['users']} users aur {st['apps']} servers "
                      f"hain."), f"👥 {st['users']} users · {st['apps']} servers"

    # ── HELP ──
    if action == "help":
        return True, ("Main server on off kar sakta hoon, free service "
                      "band kar sakta hoon, status bata sakta hoon, aur "
                      "backup le sakta hoon."), "📖 Commands list"

    return False, "Ye command samajh nahi aayi. Dobara boliye.", \
        "❓ Samajh nahi aaya"


def _all_apps():
    import db
    c = db.conn()
    rows = c.execute("SELECT * FROM apps").fetchall()
    c.close()
    return [dict(r) for r in rows]
