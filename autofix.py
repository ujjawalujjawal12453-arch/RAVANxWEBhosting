"""
🔁 AUTO-FIX — khud theek karne wala doctor
════════════════════════════════════════════════════════════════

Kaam kya karta hai:
  1. Server crash hua?           →  pakad leta hai
  2. Error kaunsi file me hai?   →  traceback padh kar dhoondhta hai
  3. Us file ka code             →  padhta hai
  4. AI se fix                   →  maangta hai (Groq → NVIDIA → ...)
  5. Backup                      →  .bak me rakhta hai
  6. Naya code likhta hai        →  aur restart karta hai
  7. Phir crash?                 →  dobara koshish (max 3)
  8. 3 baar fail?                →  haath khada karke admin ko bulata hai

⚠️ SAFETY — ye sabse zaroori hissa hai:
  • max 3 koshish per crash  — infinite loop nahi
  • max 10 fix per din       — AI quota bacha ke
  • 20 sec cooldown          — crash-loop me paisa/quota nahi jalega
  • har fix ka .bak backup   — kuch bhi galat ho to wapas laa sakte ho
  • sirf usi server ki files — doosre user ko chhu nahi sakta
  • default OFF              — user khud ON kare tab hi chalega

Developer : Ujjawal X Official
Team      : RAVAN X HOSTING TEAM
"""

import json
import os
import re
import threading
import time

BASE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(BASE, "data", "autofix.json")
os.makedirs(os.path.dirname(STATE), exist_ok=True)

# ═══════════════ limits ═══════════════
MAX_TRIES = int(os.environ.get("AUTOFIX_TRIES", "3"))     # per crash
DAY_CAP = int(os.environ.get("AUTOFIX_DAY_CAP", "10"))    # per din
COOLDOWN = int(os.environ.get("AUTOFIX_COOLDOWN", "20"))  # second
WATCH_SEC = 5                                             # kitni der me check

_lock = threading.RLock()
_st = {"day": "", "fixes": 0, "on": {}, "hist": []}
_busy = set()          # jin sid pe abhi kaam chal raha hai
_last = {}             # sid -> last attempt time
_tries = {}            # sid -> kitni baar try kiya
_watch_on = False


# ═══════════════ state ═══════════════

def _load():
    try:
        d = json.load(open(STATE))
        _st.update(d)
        _st["on"] = {int(k): v for k, v in _st.get("on", {}).items()}
    except Exception:
        pass


def _save():
    try:
        json.dump(_st, open(STATE, "w"), indent=2)
    except Exception:
        pass


def _today():
    return time.strftime("%Y-%m-%d")


def _roll():
    if _st["day"] != _today():
        _st.update(day=_today(), fixes=0)
        _save()


def left():
    _roll()
    return max(0, DAY_CAP - _st["fixes"])


_load()


# ═══════════════ on / off ═══════════════

def is_on(sid):
    return bool(_st.get("on", {}).get(int(sid)))


def set_on(sid, val=True):
    with _lock:
        _st.setdefault("on", {})[int(sid)] = bool(val)
        if not val:
            _tries.pop(int(sid), None)
        _save()
    return is_on(sid)


def enabled_list():
    return [s for s, v in _st.get("on", {}).items() if v]


# ═══════════════ traceback padhna ═══════════════

_PY = re.compile(r'File "([^"]+)", line (\d+)')
_JS = re.compile(r'at .*?\(?([\w./\\-]+\.(?:js|ts|mjs|cjs)):(\d+)')
_MOD = re.compile(r"No module named '([^']+)'")
_REQ = re.compile(r"Cannot find module '([^']+)'")


def guess_file(logtext, folder=""):
    """
    Traceback padh kar batao: kaunsi file, kaunsi line.
    Sabse AAKHRI match lete hain — wahi asli galti hoti hai.
    (upar wali lines library ki hoti hain, humari nahi)
    Return: (filename, line_no) ya ("", 0)
    """
    hits = _PY.findall(logtext or "") + _JS.findall(logtext or "")
    if not hits:
        return "", 0
    # peeche se chalo, pehli file jo HUMARE folder me ho
    for path, ln in reversed(hits):
        p = path.replace("\\", "/")
        # library/system files skip karo
        if ("/site-packages/" in p or "/lib/python" in p
                or "/node_modules/" in p or p.startswith("<")):
            continue
        name = os.path.basename(p)
        if folder:
            # folder ke andar hai kya?
            rel = p.split(folder.rstrip("/") + "/")[-1] if folder in p else name
            return rel, int(ln)
        return name, int(ln)
    return "", 0


def missing_module(logtext):
    """Sirf package missing hai? To AI ki zaroorat hi nahi."""
    m = _MOD.search(logtext or "") or _REQ.search(logtext or "")
    return m.group(1) if m else ""


def crashed(logtext):
    """Log dekhkar batao crash hua ya normal band hua."""
    t = (logtext or "").lower()
    if "traceback (most recent call last)" in t:
        return True
    if re.search(r"exit [1-9]\d*\)", t):
        return True
    for w in ("syntaxerror", "indentationerror", "modulenotfounderror",
              "importerror", "nameerror", "typeerror", "attributeerror",
              "keyerror", "indexerror", "valueerror",
              "referenceerror", "cannot find module"):
        if w in t:
            return True
    return False


# ═══════════════ ek round ═══════════════

def _log(sid, msg, lv="out"):
    try:
        import engine
        engine.log(sid, msg, lv)
    except Exception:
        pass


def _hist(sid, ok, what, fname="", eng=""):
    with _lock:
        _st.setdefault("hist", []).insert(0, {
            "t": time.time(), "sid": sid, "ok": bool(ok),
            "what": str(what)[:160], "file": fname, "engine": eng})
        _st["hist"] = _st["hist"][:60]
        _save()


def history(n=20):
    return _st.get("hist", [])[:n]


def attempt(uid, sid, force=False):
    """
    Ek baar theek karne ki koshish.
    Return dict: {ok, step, msg, file, engine}
    """
    import engine
    sid = int(sid)

    # ── guards ──
    if sid in _busy:
        return {"ok": False, "step": "busy", "msg": "Pehle se chal raha hai"}
    if not force and not is_on(sid):
        return {"ok": False, "step": "off", "msg": "Auto-fix band hai"}
    _roll()
    if left() <= 0:
        return {"ok": False, "step": "cap",
                "msg": f"Aaj ki {DAY_CAP} fix limit khatam"}
    ago = time.time() - _last.get(sid, 0)
    if not force and ago < COOLDOWN:
        return {"ok": False, "step": "cool",
                "msg": f"{int(COOLDOWN - ago)} sec ruko"}
    if _tries.get(sid, 0) >= MAX_TRIES:
        return {"ok": False, "step": "give-up",
                "msg": f"{MAX_TRIES} baar try kiya, nahi hua — "
                       f"admin dekhe"}

    _busy.add(sid)
    _last[sid] = time.time()
    try:
        return _do(uid, sid, engine)
    finally:
        _busy.discard(sid)


def _do(uid, sid, engine):
    import coder

    folder = engine.server_dir(uid, sid)
    lines = engine.console(sid, 0) or []
    # engine format: {"t":..., "l":..., "x": text}
    logtext = "\n".join(str(x.get("x", "")) for x in lines[-90:])

    if not crashed(logtext):
        return {"ok": False, "step": "no-crash",
                "msg": "Koi error nahi mila"}

    _tries[sid] = _tries.get(sid, 0) + 1
    n = _tries[sid]
    _log(sid, f"🔁 Auto-fix koshish {n}/{MAX_TRIES}…", "warn")

    # ═══ CASE 1: sirf package missing — AI ki zaroorat nahi ═══
    mod = missing_module(logtext)
    if mod:
        _log(sid, f"📦 '{mod}' missing hai — install kar raha hoon", "warn")
        try:
            engine.install_deps(uid, sid)
            time.sleep(1)
            mark = time.time()
            engine.restart(uid, sid)
            with _lock:
                _st["fixes"] += 1
                _save()
            _hist(sid, True, f"'{mod}' install kiya", "", "install")
            _log(sid, f"✅ '{mod}' install karke restart kiya", "ok")
            return {"ok": True, "step": "install", "engine": "install",
                    "msg": f"'{mod}' install karke restart kiya",
                    "since": mark}
        except Exception as e:
            _hist(sid, False, f"install fail: {e}")
            return {"ok": False, "step": "install",
                    "msg": f"install fail: {str(e)[:90]}"}

    # ═══ CASE 2: code me bug — AI se fix mangao ═══
    fname, lno = guess_file(logtext, folder)
    if not fname:
        info = engine.detect(folder)
        fname = info.get("entry") or ""
    if not fname:
        _hist(sid, False, "file nahi mili")
        return {"ok": False, "step": "find",
                "msg": "Error kaunsi file me hai — pata nahi chala"}

    code = engine.read_file(uid, sid, fname, 60000) or ""
    if not code.strip():
        _hist(sid, False, f"{fname} khali", fname)
        return {"ok": False, "step": "read",
                "msg": f"{fname} padh nahi paya"}

    _log(sid, f"🔍 Galti mili: {fname}"
              + (f" line {lno}" if lno else ""), "warn")

    r = coder.diagnose(logtext[-3500:], code=code[:22000],
                       filename=fname)
    newcode = (r.get("code") or "").strip()
    eng = r.get("engine", "")

    if not newcode:
        _hist(sid, False, "AI ne fix nahi diya", fname, eng)
        return {"ok": False, "step": "ai",
                "msg": "AI fix nahi de paya", "file": fname}

    # ── safety: naya code bahut chhota to shak hai ──
    if len(newcode) < len(code) * 0.35 and len(code) > 400:
        _hist(sid, False, "AI ne aadha code kaat diya", fname, eng)
        _log(sid, "⚠️ AI ne bahut zyada code kaat diya — nahi lagaya",
             "err")
        return {"ok": False, "step": "guard", "file": fname,
                "msg": "AI ka fix shaqi laga — nahi lagaya"}

    # ── safety: Python hai to syntax check karo LAGANE SE PEHLE ──
    if fname.endswith(".py"):
        try:
            import ast
            ast.parse(newcode)
        except SyntaxError as se:
            _hist(sid, False, f"AI ka code hi toota: {se.msg}", fname, eng)
            _log(sid, f"⚠️ AI ka naya code hi galat tha ({se.msg}) — "
                      f"nahi lagaya", "err")
            return {"ok": False, "step": "syntax", "file": fname,
                    "msg": f"AI ka code hi toota hua tha: {se.msg}"}

    # ── backup ──
    engine.write_file(uid, sid, fname + ".bak", code)
    okw = engine.write_file(uid, sid, fname, newcode)
    if not okw:
        _hist(sid, False, "likh nahi paya", fname, eng)
        return {"ok": False, "step": "write", "file": fname,
                "msg": "File likh nahi paya"}

    with _lock:
        _st["fixes"] += 1
        _save()

    prob = str(r.get("problem", ""))[:140]
    _log(sid, f"🔧 {fname} theek kiya — {prob}", "ok")
    _log(sid, f"💾 Purana code {fname}.bak me safe hai", "out")

    # ── restart ──
    time.sleep(0.5)
    mark = time.time()          # is waqt ke BAAD ki lines hi dekhni hain
    engine.restart(uid, sid)
    _log(sid, "🔄 Restart kar diya — dekhte hain chalta hai ya nahi",
         "warn")

    _hist(sid, True, prob or "fix lagaya", fname, eng)
    return {"ok": True, "step": "fixed", "file": fname, "engine": eng,
            "line": lno, "msg": prob or "Fix lagakar restart kiya",
            "try": n, "max": MAX_TRIES, "since": mark}


def verify(uid, sid, wait=8, since=0):
    """
    Fix ke baad: sach me theek hua kya?

    ⚠️ Do baatein jo bina test kiye pata nahi chaltin:

    1. Console me PURANA crash bhi pada hota hai. Agar poora
       console padh liya to hamesha "error hai" lagega — chahe
       fix perfect ho. Isliye `since` ke BAAD wali lines hi dekhte hain.

    2. Har script server nahi hoti. Kuch kaam karke exit 0 se
       band ho jaati hain — WO KAAMYAABI HAI, failure nahi.

    Return: (True, wajah) ya (False, wajah)
    """
    import engine
    sid = int(sid)
    time.sleep(wait)
    lines = engine.console(sid, 0) or []
    if since:
        lines = [x for x in lines if float(x.get("t", 0)) >= since - 0.5]
    tail = "\n".join(str(x.get("x", "")) for x in lines[-40:])

    # 1. naya error aaya? — pakka fail
    if crashed(tail):
        return False, "phir error aa raha hai"

    # 2. abhi chal raha hai — server hai, sahi hai
    if engine.is_running(sid):
        _tries.pop(sid, None)
        return True, "chal raha hai"

    # 3. exit 0 — script ne kaam poora kiya
    if re.search(r"exit 0\)", tail):
        _tries.pop(sid, None)
        return True, "kaam poora karke band hua (exit 0)"

    # 4. kuch log hi nahi mila — shak ka fayda, chal gaya maano
    if not tail.strip():
        return False, "koi output nahi aaya"

    return False, "band ho gaya"


def reset(sid):
    _tries.pop(int(sid), None)
    _last.pop(int(sid), None)


# ═══════════════ watcher — background nazar ═══════════════

def _watcher():
    import engine
    import db
    while True:
        try:
            time.sleep(WATCH_SEC)
            for sid in list(enabled_list()):
                try:
                    if sid in _busy or engine.is_running(sid):
                        continue
                    if time.time() - _last.get(sid, 0) < COOLDOWN:
                        continue
                    if _tries.get(sid, 0) >= MAX_TRIES:
                        continue
                    app = db.get_app(sid)
                    uid = (app or {}).get("user_id")
                    if not uid:
                        continue
                    lines = engine.console(sid, 0) or []
                    tail = "\n".join(str(x.get("x", ""))
                                     for x in lines[-40:])
                    if not crashed(tail):
                        continue
                    res = attempt(uid, sid)
                    if res.get("ok"):
                        good, why = verify(uid, sid,
                                           since=res.get("since", 0))
                        if good:
                            _log(sid, "✅ Auto-fix kaamyaab — "
                                      "server chal raha hai", "ok")
                            reset(sid)
                        else:
                            _log(sid, f"⚠️ {why} — dobara dekhta hoon",
                                 "warn")
                    elif res.get("step") == "give-up":
                        _log(sid, f"🚨 {MAX_TRIES} baar try kiya, nahi hua. "
                                  f"Admin ko dekhna padega.", "err")
                except Exception:
                    continue
        except Exception:
            time.sleep(10)


def start_watcher():
    global _watch_on
    if _watch_on:
        return False
    _watch_on = True
    threading.Thread(target=_watcher, daemon=True).start()
    return True


# ═══════════════ status ═══════════════

def status(sid=None):
    _roll()
    d = {
        "cap": DAY_CAP,
        "used": _st.get("fixes", 0),
        "left": left(),
        "tries_max": MAX_TRIES,
        "cooldown": COOLDOWN,
        "watching": _watch_on,
        "on_count": len(enabled_list()),
    }
    if sid is not None:
        sid = int(sid)
        d.update(on=is_on(sid), tries=_tries.get(sid, 0),
                 busy=sid in _busy)
    return d
