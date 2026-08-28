"""
unlock.py — 🎁 FREE SERVER TOKEN SYSTEM
════════════════════════════════════════

Flow (jaisa aapne bataya):
  1. User "Free Server" dabata hai
  2. Bot STOCK check karta hai — slots bache hain ya nahi
  3. Stock hai → user ko HAMARI website ka link milta hai
  4. Us page par neeche "GENERATE" button hota hai
  5. Generate dabao → shortener link banti hai
  6. Shortener complete karo → TOKEN milta hai
  7. Token daalo → free server mil jata hai

🚫 CHEATING BLOCK:
   Agar koi shortener skip karke seedha /verify endpoint hit karta hai,
   ya fake token daalta hai → BLACKLIST.

   Blacklist ka matlab:
     • Free server KABHI nahi milega
     • Kuch bhi buy nahi kar sakta
     • Har page par blacklist notice
     • 10 minute ka temporary block bhi
"""

import hashlib
import hmac
import json
import os
import random
import secrets
import string
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
os.makedirs(DATA, exist_ok=True)

STATE_FILE = os.path.join(DATA, "unlock.json")
SECRET = os.environ.get("UNLOCK_SECRET", "ravanx-unlock-2026-secret")

# ── SETTINGS ──
FREE_STOCK = int(os.environ.get("FREE_STOCK", "10"))    # kitne free servers

# ═══════════════════════════════════════════════════════
#   🎁 WEEKLY CREDIT + FREE SERVER KA NAYA NIYAM
#
#   Malik ka faisla:
#     • Har 7 din me 10 credit MUFT
#     • Free server 24 ghante chalta hai, phir APNE AAP band
#     • ⚠️ Ek baar weekly CREDIT le liya to 30 din tak
#       free SERVER nahi milega (dono ek saath nahi)
#
#   Ye isliye taaki log dono cheezein ek saath na le lein.
# ═══════════════════════════════════════════════════════
WEEKLY_CREDITS = int(os.environ.get("WEEKLY_CREDITS", "10"))
WEEKLY_DAYS = int(os.environ.get("WEEKLY_DAYS", "7"))
SERVER_LOCK_DAYS = int(os.environ.get("SERVER_LOCK_DAYS", "30"))
FREE_SERVER_HOURS = int(os.environ.get("FREE_SERVER_HOURS", "24"))
STEP_MIN_SEC = int(os.environ.get("STEP_MIN_SEC", "8"))   # shortener ka min time
TOKEN_TTL = 1800          # 30 min me token expire
TEMP_BLOCK_MIN = 10       # cheating par temporary block

# ─────────────────────────────────────────────────────────
#  🔗 SHORTENER — EarnLinks.in
# ─────────────────────────────────────────────────────────
#  Verified: https://earnlinks.in/api?api=KEY&url=ENCODED&alias=XX
#  Response: {"status":"success","shortenedUrl":"https://earnlinks.in/xxxx"}

import keyvault as _kv

SHORTENER = {
    "name": os.environ.get("SHORT_NAME", "EarnLinks"),
    "api": os.environ.get("SHORT_API", "") or _kv.get("SHORT_API"),
    "base": os.environ.get("SHORT_BASE", "https://earnlinks.in/api"),
    "domain": os.environ.get("SHORT_DOMAIN", "earnlinks.in"),
}
SHORTENER["enabled"] = bool(SHORTENER["api"])

# fail hone par kya karein: "block" = server nahi milega, "allow" = direct link
SHORT_FALLBACK = os.environ.get("SHORT_FALLBACK", "block")

_S = None


def _load():
    global _S
    if _S is not None:
        return _S
    try:
        _S = json.load(open(STATE_FILE))
    except Exception:
        _S = {}
    _S.setdefault("pending", {})     # code -> {uid, at, step, ip}
    _S.setdefault("used", {})        # code -> uid
    _S.setdefault("black", {})       # uid -> {at, reason}
    _S.setdefault("tempblock", {})   # uid -> until
    _S.setdefault("claimed", [])     # uid list jinhe free mila
    _S.setdefault("weekly", {})      # uid -> last weekly credit ka time
    _S.setdefault("srvlock", {})     # uid -> kab tak server band
    return _S


def _save():
    try:
        tmp = STATE_FILE + ".tmp"
        with open(tmp, "w") as f:
            json.dump(_load(), f)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, STATE_FILE)
    except Exception:
        pass


# ─────────────────────────────────────────────────────────
#  STOCK
# ─────────────────────────────────────────────────────────

def stock():
    s = _load()
    used = len(s["claimed"])
    left = max(0, FREE_STOCK - used)
    return {"total": FREE_STOCK, "used": used, "left": left,
            "available": left > 0,
            "percent": int(used / FREE_STOCK * 100) if FREE_STOCK else 100}


def has_claimed(uid):
    return str(uid) in _load()["claimed"]


# ─────────────────────────────────────────────────────────
#  🎁 WEEKLY 10 CREDIT
# ─────────────────────────────────────────────────────────

def weekly_status(uid):
    """
    Weekly credit ka haal.

    Return: dict(can, left_sec, next_at, last_at, amount, days)
    """
    s = _load()
    last = float(s["weekly"].get(str(uid), 0) or 0)
    gap = WEEKLY_DAYS * 86400
    now = time.time()
    nxt = last + gap if last else 0
    left = max(0, int(nxt - now)) if last else 0
    return {"can": left <= 0, "left_sec": left, "next_at": nxt,
            "last_at": last, "amount": WEEKLY_CREDITS,
            "days": WEEKLY_DAYS, "lock_days": SERVER_LOCK_DAYS}


def claim_weekly(uid):
    """
    10 credit do — aur 30 din ke liye free SERVER band kar do.

    ⚠️ Yahi malik ka asli niyam hai: credit liya to server nahi.
    Return: (ok, msg, kitne_credit)
    """
    if is_black(uid):
        return False, "Aap blacklist me hain — free kuch nahi milega", 0
    w = weekly_status(uid)
    if not w["can"]:
        return False, f"Abhi nahi — {human_left(w['left_sec'])} baad", 0

    s = _load()
    now = time.time()
    s["weekly"][str(uid)] = now
    # 🔒 30 din ka server lock
    s["srvlock"][str(uid)] = now + SERVER_LOCK_DAYS * 86400
    _save()

    try:
        import db
        db.add_credits(uid, WEEKLY_CREDITS, "Weekly free credit")
    except Exception:
        pass
    return True, (f"{WEEKLY_CREDITS} credit mil gaye! "
                  f"Ab {SERVER_LOCK_DAYS} din tak free server "
                  f"nahi milega."), WEEKLY_CREDITS


def server_lock(uid):
    """
    Free server pe lock hai ya nahi.

    Return: dict(locked, left_sec, until, why)
    """
    s = _load()
    until = float(s["srvlock"].get(str(uid), 0) or 0)
    left = max(0, int(until - time.time()))
    return {"locked": left > 0, "left_sec": left, "until": until,
            "why": (f"Aapne weekly {WEEKLY_CREDITS} credit liye the — "
                    f"isliye {SERVER_LOCK_DAYS} din free server band")
                   if left > 0 else ""}


def lock_server(uid, days=None):
    """Free server lene ke baad bhi lock lagao"""
    s = _load()
    d = SERVER_LOCK_DAYS if days is None else days
    s["srvlock"][str(uid)] = time.time() + d * 86400
    _save()


def human_left(sec):
    """350000 -> '4 din 1 ghanta'"""
    sec = max(0, int(sec))
    d, r = divmod(sec, 86400)
    h, r = divmod(r, 3600)
    m = r // 60
    if d:
        return f"{d} din {h} ghanta" if h else f"{d} din"
    if h:
        return f"{h} ghanta {m} min" if m else f"{h} ghanta"
    return f"{m} minute" if m else "thodi der"


def mark_claimed(uid):
    s = _load()
    if str(uid) not in s["claimed"]:
        s["claimed"].append(str(uid))
        _save()


# ─────────────────────────────────────────────────────────
#  BLACKLIST
# ─────────────────────────────────────────────────────────

def is_black(uid):
    return str(uid) in _load()["black"]


def black_info(uid):
    return _load()["black"].get(str(uid))


def blacklist(uid, reason="Cheating detect hua"):
    s = _load()
    s["black"][str(uid)] = {"at": int(time.time()), "reason": reason}
    s["tempblock"][str(uid)] = time.time() + TEMP_BLOCK_MIN * 60
    # uske pending codes bhi mar do
    for c in [k for k, v in s["pending"].items() if str(v.get("uid")) == str(uid)]:
        s["pending"].pop(c, None)
    _save()
    return True


def unblacklist(uid):
    s = _load()
    s["black"].pop(str(uid), None)
    s["tempblock"].pop(str(uid), None)
    _save()
    return True


def temp_blocked(uid):
    s = _load()
    u = s["tempblock"].get(str(uid), 0)
    if u > time.time():
        return int(u - time.time())
    return 0


def all_black():
    s = _load()
    return [{"uid": k, **v} for k, v in s["black"].items()]


# ─────────────────────────────────────────────────────────
#  TOKEN FLOW
# ─────────────────────────────────────────────────────────

def _sign(code, uid):
    return hmac.new(SECRET.encode(), f"{code}:{uid}".encode(),
                    hashlib.sha256).hexdigest()[:16]


def start(uid, ip=""):
    """Step 1 — code banao (abhi shortener nahi bheja)."""
    s = _load()
    # purane pending saaf
    now = time.time()
    for c in [k for k, v in s["pending"].items()
              if now - v.get("at", 0) > TOKEN_TTL]:
        s["pending"].pop(c, None)

    code = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
    s["pending"][code] = {"uid": str(uid), "at": now, "step": 1, "ip": ip,
                          "gen_at": 0}
    _save()
    return code


def mark_generated(code, uid):
    """Step 2 — user ne GENERATE dabaya, ab shortener par bheja."""
    s = _load()
    p = s["pending"].get(code)
    if not p or str(p["uid"]) != str(uid):
        return False
    p["step"] = 2
    p["gen_at"] = time.time()
    _save()
    return True


def token_for(code, uid):
    """Shortener ke baad jo token milega."""
    return f"{code}-{_sign(code, uid)}"


def short_url(code, uid, site_url):
    """
    EarnLinks.in se asli short link banao.
    Return: (link, is_short, error)
    """
    dest = f"{site_url}/free/done?t={token_for(code, uid)}"

    if not SHORTENER["enabled"]:
        return dest, False, "API key set nahi hai"

    # 🏠 Localhost/private IP — shortener aise domain accept nahi karta.
    #    Local testing me direct link, asli domain par asli shortener.
    low_site = site_url.lower()
    is_local = any(x in low_site for x in (
        "localhost", "127.0.0.1", "0.0.0.0", "192.168.", "10.0.",
        "169.254.", ".local", "172.16.", "172.17.", "172.18."))
    if is_local:
        return dest, False, "local"

    alias = f"RX{code[:8]}"
    api = SHORTENER["base"]
    url = (f"{api}?api={SHORTENER['api']}"
           f"&url={urllib.parse.quote(dest, safe='')}"
           f"&alias={alias}")

    last = ""
    for attempt in range(3):
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "Mozilla/5.0 (RavanX)"})
            with urllib.request.urlopen(req, timeout=20) as r:
                raw = r.read().decode("utf-8", "ignore")
            try:
                d = json.loads(raw)
            except json.JSONDecodeError:
                if raw.strip().startswith("http"):
                    return raw.strip(), True, ""
                last = f"galat response: {raw[:60]}"
                continue

            if str(d.get("status", "")).lower() == "success":
                link = (d.get("shortenedUrl") or d.get("short")
                        or d.get("url") or "")
                if link:
                    _log_short(code, uid, link)
                    return link, True, ""
                last = "link khali aaya"
            else:
                # ⚠️ API kabhi string, kabhi list bhejti hai
                msg = d.get("message")
                if isinstance(msg, (list, tuple)):
                    msg = " ".join(str(x) for x in msg)
                elif isinstance(msg, dict):
                    msg = json.dumps(msg)
                last = str(msg or "").strip() or "API ne mana kar diya"
                low = last.lower()
                # alias busy -> bina alias
                if "alias" in low or "exist" in low or "taken" in low:
                    url = (f"{api}?api={SHORTENER['api']}"
                           f"&url={urllib.parse.quote(dest, safe='')}")
                    continue
                if "invalid api" in low or "invalid token" in low:
                    break
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}"
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:70]}"
        time.sleep(0.7)

    if SHORT_FALLBACK == "allow":
        return dest, False, last
    return "", False, last or "Shortener respond nahi kar raha"


def _log_short(code, uid, link):
    s = _load()
    p = s["pending"].get(code)
    if p:
        p["short"] = link
        p["short_at"] = time.time()
        _save()


def short_test():
    """Admin panel ke liye — API live hai ya nahi."""
    if not SHORTENER["enabled"]:
        return False, "API key nahi hai"
    try:
        u = (f"{SHORTENER['base']}?api={SHORTENER['api']}"
             f"&url={urllib.parse.quote('https://example.com/ping', safe='')}")
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            d = json.loads(r.read().decode())
        if str(d.get("status", "")).lower() == "success":
            return True, d.get("shortenedUrl", "ok")
        return False, d.get("message", "unknown")
    except Exception as e:
        return False, f"{type(e).__name__}: {str(e)[:60]}"


def verify(token, uid, ip=""):
    """
    Step 3 — token check.
    Return: (ok, reason)

    🚫 Cheating -> blacklist:
       • fake/galat token
       • doosre ka token
       • generate hi nahi kiya (direct endpoint hit)
       • bahut jaldi wapas aa gaya (shortener skip)
       • ek token dobara
    """
    s = _load()

    if is_black(uid):
        return False, "blacklisted"
    tb = temp_blocked(uid)
    if tb:
        return False, f"temp:{tb}"

    if not token or "-" not in token:
        blacklist(uid, "Galat token format — cheating ki koshish")
        return False, "bad_token"

    code, sig = token.rsplit("-", 1)

    if code in s["used"]:
        blacklist(uid, "Ek hi token dobara use karne ki koshish")
        return False, "already_used"

    p = s["pending"].get(code)
    if not p:
        blacklist(uid, "Bina generate kiye seedha endpoint hit kiya")
        return False, "no_pending"

    if str(p["uid"]) != str(uid):
        blacklist(uid, "Doosre user ka token use karne ki koshish")
        return False, "wrong_user"

    if not hmac.compare_digest(sig, _sign(code, p["uid"])):
        blacklist(uid, "Token ki signature galat — fake token")
        return False, "bad_sig"

    if p.get("step", 1) < 2:
        blacklist(uid, "GENERATE dabaye bina token laane ki koshish")
        return False, "skipped_generate"

    gap = time.time() - p.get("gen_at", 0)
    if gap < STEP_MIN_SEC:
        blacklist(uid, f"Shortener skip kiya (sirf {gap:.0f}s me wapas)")
        return False, "too_fast"

    if time.time() - p["at"] > TOKEN_TTL:
        s["pending"].pop(code, None)
        _save()
        return False, "expired"

    # ✅ sab sahi
    s["used"][code] = str(uid)
    s["pending"].pop(code, None)
    _save()
    return True, "ok"


def reason_text(code):
    return {
        "bad_token": "Token ka format galat hai",
        "already_used": "Ye token pehle use ho chuka hai",
        "no_pending": "Aapne process shuru hi nahi ki thi",
        "wrong_user": "Ye token kisi aur ka hai",
        "bad_sig": "Token nakli hai",
        "skipped_generate": "Aapne GENERATE button dabaya hi nahi",
        "too_fast": "Shortener complete nahi kiya",
        "expired": "Token expire ho gaya (30 min)",
        "blacklisted": "Aap blacklist me ho",
    }.get(code, "Verify nahi hua")


def rebuild_pending(new_base, old_base=""):
    """
    🔄 Tunnel URL badal gaya — jo tokens pending hain unki
    short link naye URL se dobara banao. Purani bekaar ho gayi.
    """
    st = _load()
    done, fail = 0, 0
    for code, p in list(st["pending"].items()):
        if p.get("step", 1) < 2:
            continue                      # generate hi nahi kiya
        if time.time() - p.get("at", 0) > TOKEN_TTL:
            continue                      # waise bhi expire
        try:
            link, is_short, err = short_url(code, p["uid"], new_base)
            if link:
                p["short"] = link
                p["rebuilt"] = int(time.time())
                done += 1
            else:
                fail += 1
        except Exception:
            fail += 1
    if done or fail:
        _save()
    return done, fail


def pending_for(uid):
    """Us user ka abhi active pending (naya link dikhane ke liye)."""
    st = _load()
    now = time.time()
    for code, p in st["pending"].items():
        if str(p.get("uid")) == str(uid) and \
                now - p.get("at", 0) < TOKEN_TTL:
            return code, p
    return None, None


def stats():
    s = _load()
    return {"pending": len(s["pending"]), "used": len(s["used"]),
            "black": len(s["black"]), "claimed": len(s["claimed"]),
            **stock()}
