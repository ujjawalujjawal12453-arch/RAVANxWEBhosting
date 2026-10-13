"""
botlink.py — WEBSITE ⟷ BOT ka pul
═══════════════════════════════════

Problem jo ye solve karta hai:
  Tunnel ka URL badalta rehta hai. Bot ke paas purana URL rehta hai.
  User bot se website par aata hai — link toota hua, khali haath.

Hal:
  Website apna current URL har baar cloud (Upstash) par likh deti hai.
  Bot wahan se padh leta hai. Domain badle, bot ko turant pata chal jaata.

Aur ulta bhi:
  Bot ka username / channel yahan aata hai, website par dikhta hai.

Cloud keys:
  ravanx:link:web     -> website ka live URL + info
  ravanx:link:bot     -> bot ka username + info
  ravanx:link:handoff -> bot se aane wale users ke token
"""

import json
import os
import secrets
import threading
import time

BASE = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE, "data", "botlink.json")
os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)

KEY_WEB = "ravanx:link:web"
KEY_BOT = "ravanx:link:bot"
KEY_HAND = "ravanx:link:handoff"

PUB_EVERY = 45          # har 45 sec publish
_state = {
    "url": "",
    "published_at": 0,
    "bot": {},           # bot ki info (cloud se)
    "bot_seen": 0,
    "pushes": 0,
    "fails": 0,
    "last_err": "",
}


# ═══════════════ helpers ═══════════════

def _cmd(args, timeout=15):
    try:
        import cloudsync
        return cloudsync._cmd(args, timeout=timeout)
    except Exception:
        return None


def ready():
    try:
        import cloudsync
        return cloudsync.configured()
    except Exception:
        return False


def _save():
    try:
        json.dump(_state, open(STATE_FILE, "w"), indent=2, default=str)
    except Exception:
        pass


def _load():
    try:
        d = json.load(open(STATE_FILE))
        _state.update({k: d.get(k, _state[k]) for k in _state})
    except Exception:
        pass


# ═══════════════ WEBSITE -> CLOUD ═══════════════

def publish(url=None, force=False):
    """
    Website ka live URL cloud par likho — bot padh lega.
    Tunnel badla ki turant call hota hai.
    """
    if not ready():
        return False
    if url is None:
        try:
            import tunnel
            url = tunnel.url()
        except Exception:
            url = ""
    url = (url or "").rstrip("/")
    if not url:
        return False
    if not force and url == _state["url"] and \
            time.time() - _state["published_at"] < PUB_EVERY:
        return False

    try:
        import db
        import theme
        st = db.stats()
    except Exception:
        st = {}
        theme = None

    payload = {
        "url": url,
        "name": getattr(theme, "BRAND", "RAVAN X HOSTING"),
        "tagline": getattr(theme, "TAGLINE", ""),
        "signup": url + "/signup",
        "login": url + "/login",
        "free": url + "/free",
        "pricing": url + "/#pricing",
        "status": url + "/status",
        "users": st.get("users", 0),
        "servers": st.get("apps", 0),
        "plans": [
            {"key": p[0], "name": p[1], "price": p[2], "ram": p[3],
             "storage_gb": getattr(theme, "STORAGE_GB", {}).get(p[0], 0)}
            for p in getattr(theme, "PLANS", [])
        ],
        "at": int(time.time()),
        "v": 2,
    }
    r = _cmd(["SET", KEY_WEB, json.dumps(payload)], timeout=20)
    if r and "result" in r:
        _state["url"] = url
        _state["published_at"] = int(time.time())
        _state["pushes"] += 1
        _state["last_err"] = ""
        _save()
        return True
    _state["fails"] += 1
    _state["last_err"] = "publish fail"
    return False


# ═══════════════ CLOUD -> WEBSITE ═══════════════

def fetch_bot():
    """Bot ki info cloud se — website par dikhane ke liye."""
    if not ready():
        return {}
    r = _cmd(["GET", KEY_BOT], timeout=15)
    if not r or not r.get("result"):
        return {}
    try:
        d = json.loads(r["result"])
        _state["bot"] = d
        _state["bot_seen"] = int(time.time())
        _save()
        return d
    except Exception:
        return {}


def bot_info():
    """Cached bot info."""
    return dict(_state.get("bot") or {})


def bot_link():
    """Bot ka t.me link."""
    b = bot_info()
    u = (b.get("username") or "").lstrip("@")
    return f"https://t.me/{u}" if u else ""


def bot_online():
    b = bot_info()
    if not b:
        return False
    return (time.time() - b.get("at", 0)) < 600


# ═══════════════ HANDOFF — bot se aane wale user ═══════════════

def make_handoff(tg_id, name="", extra=None):
    """
    Bot ye call karta hai: user ko website bhejne se pehle token banao.
    Token wala link khulte hi website ko pata chal jaata hai
    ki ye banda bot se aaya hai — khali haath nahi jayega.
    """
    if not ready():
        return ""
    tok = secrets.token_urlsafe(16)
    payload = {"tg": tg_id, "name": name, "at": int(time.time()),
               **(extra or {})}
    r = _cmd(["SET", f"{KEY_HAND}:{tok}", json.dumps(payload), "EX", "3600"],
             timeout=15)
    return tok if (r and "result" in r) else ""


def read_handoff(tok):
    """Website: token se bot-user ki info nikalo."""
    if not ready() or not tok:
        return {}
    r = _cmd(["GET", f"{KEY_HAND}:{tok}"], timeout=15)
    if not r or not r.get("result"):
        return {}
    try:
        return json.loads(r["result"])
    except Exception:
        return {}


def burn_handoff(tok):
    if ready() and tok:
        _cmd(["DEL", f"{KEY_HAND}:{tok}"], timeout=10)


# ═══════════════ STATUS + LOOP ═══════════════

def status():
    b = bot_info()
    return {
        "ready": ready(),
        "url": _state["url"],
        "published_at": _state["published_at"],
        "pushes": _state["pushes"],
        "fails": _state["fails"],
        "error": _state["last_err"],
        "bot": b,
        "bot_username": b.get("username", ""),
        "bot_link": bot_link(),
        "bot_online": bot_online(),
        "bot_users": b.get("users", 0),
        "bot_seen": _state["bot_seen"],
    }


def on_tunnel_change(new_url, old_url=None):
    """Tunnel badla -> turant cloud par naya URL."""
    ok = publish(new_url, force=True)
    if ok:
        try:
            import tunnel
            tunnel.log(f"bot ko naya URL bata diya: {new_url}")
        except Exception:
            pass
    return ok


def loop(every=PUB_EVERY):
    """Background — URL publish + bot info fetch."""
    time.sleep(12)
    n = 0
    while True:
        try:
            publish()
            if n % 4 == 0:
                fetch_bot()
            n += 1
            time.sleep(every)
        except Exception:
            time.sleep(30)


def boot():
    _load()
    threading.Thread(target=loop, daemon=True).start()
