"""
🕵️ BOSS AGENT — Boss ka haath-paanv
════════════════════════════════════════════════════════════════

Boss ab sirf jawab nahi deta — KAAM KARTA HAI.

Aap sirf bolo: "mera server theek karo"
Agent khud:
  1. 📂 Server ki SAARI files khud uthata hai (khud dhoondhta hai)
  2. 🔍 Har file padhta hai — syntax check, error dhoondhna
  3. 📜 Console ka crash log padhta hai
  4. 🧠 Boss se poochta hai kaunsa model is kaam ke liye best hai
  5. ✍️ Fix likhwata hai
  6. 🛡️ Fix ko CHECK karta hai (syntax + size guard)
  7. ⏸️ RUKTA HAI — "Sir, 3 file me 5 galti mili, theek kar dun?"
  8. ✅ Aap HAAN bolo → tabhi file badalta hai
  9. ⏸️ Phir RUKTA HAI — "Ab deploy kar dun?"
 10. ✅ Aap HAAN bolo → restart/deploy kar deta hai

⚠️ SABSE ZAROORI: Agent apne aap kuch nahi badalta.
   Har badi cheez se pehle AAP se poochta hai.

Plan gating (aiboss.py se):
   free/starter → agent milta hi nahi
   pro          → 5 file scan, deploy NAHI
   ultra        → 20 file, deploy HAAN
   business     → 60 file, deploy + auto-approve option
   admin        → sab unlimited

Developer : Ujjawal X Official
Team      : RAVAN X HOSTING TEAM
"""

import ast
import json
import os
import re
import threading
import time

BASE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(BASE, "data", "bossagent.json")
os.makedirs(os.path.dirname(STATE), exist_ok=True)

# ═══════════════════════════════════════════════
#   💎 PLAN — agent kisko kitna milega
# ═══════════════════════════════════════════════

# ═══════════════════════════════════════════════════════
#   PLAN aur HADD
#
#   Malik ka hukum:
#     "ek din me 5 se 10 baar use kar sakte hain, bas usse
#      zyada nahi. Admin ke liye koi rok nahi. VIP ke liye
#      bhi rakhna."
#
#   Isliye:
#     free/starter  -> milta hi nahi
#     pro           ->  5 baar/din
#     ultra         -> 10 baar/din
#     business      -> UNLIMITED (VIP)
#     admin         -> UNLIMITED
#
#   runs = -1 ka matlab koi hadd nahi.
# ═══════════════════════════════════════════════════════
AGENT_TIERS = {
    "free":     {"on": False, "files": 0,  "deploy": False,
                 "runs": 0,  "auto": False},
    "starter":  {"on": False, "files": 0,  "deploy": False,
                 "runs": 0,  "auto": False},
    "pro":      {"on": True,  "files": 8,  "deploy": False,
                 "runs": 5,  "auto": False},
    "ultra":    {"on": True,  "files": 25, "deploy": True,
                 "runs": 10, "auto": False},
    "business": {"on": True,  "files": 80, "deploy": True,
                 "runs": -1, "auto": True},
    "admin":    {"on": True,  "files": 300, "deploy": True,
                 "runs": -1, "auto": True},
}


def unlimited(pk):
    """VIP aur admin — koi ginti nahi"""
    return pk.get("runs", 0) < 0


def aperks(user, is_admin=False):
    import aiboss
    t = aiboss.tier_of(user, is_admin)
    return dict(AGENT_TIERS.get(t, AGENT_TIERS["free"]), tier=t)


# ═══════════════════════════════════════════════
#   📂 FILE DHOONDHNA
# ═══════════════════════════════════════════════

CODE_EXT = (".py", ".js", ".ts", ".mjs", ".cjs", ".php", ".go",
            ".rb", ".java", ".sh", ".json", ".html", ".css")

SKIP_DIR = ("node_modules", "__pycache__", ".git", "venv", ".venv",
            "dist", "build", "vendor", ".cache", "site-packages")

SKIP_FILE = (".bak", ".pyc", ".lock", ".min.js", ".min.css",
             ".map", ".log")

MAX_FILE = 60000          # 60 KB se badi file skip


def scan(uid, sid, limit=20):
    """
    Server ki saari code files khud dhoondho.
    Return: [{path, size, ext}]
    """
    import engine
    folder = engine.server_dir(uid, sid)
    if not os.path.isdir(folder):
        return []
    out = []
    for root, dirs, files in os.walk(folder):
        dirs[:] = [d for d in dirs
                   if d not in SKIP_DIR and not d.startswith(".")]
        for f in sorted(files):
            if f.endswith(SKIP_FILE) or f.startswith("."):
                continue
            ext = os.path.splitext(f)[1].lower()
            if ext not in CODE_EXT:
                continue
            p = os.path.join(root, f)
            try:
                sz = os.path.getsize(p)
            except Exception:
                continue
            if sz == 0 or sz > MAX_FILE:
                continue
            out.append({"path": os.path.relpath(p, folder),
                        "size": sz, "ext": ext})
        if len(out) > limit * 4:
            break
    # entry file sabse pehle, phir chhoti file pehle
    info = engine.detect(folder)
    entry = (info or {}).get("entry", "")
    out.sort(key=lambda x: (x["path"] != entry, x["size"]))
    return out[:limit]


# ═══════════════════════════════════════════════
#   🔍 GALTI DHOONDHNA — bina AI ke pehle
# ═══════════════════════════════════════════════

def quick_check(path, code):
    """
    AI se poochhne se PEHLE khud dekho.
    Sasta hai aur pakka hai — AI quota bachta hai.
    Return: list of {line, kind, msg}
    """
    bad = []
    ext = os.path.splitext(path)[1].lower()

    if ext == ".py":
        try:
            ast.parse(code)
        except SyntaxError as e:
            bad.append({"line": e.lineno or 0, "kind": "syntax",
                        "msg": f"Python syntax galat: {e.msg}"})
    elif ext == ".json":
        try:
            json.loads(code)
        except Exception as e:
            bad.append({"line": 0, "kind": "syntax",
                        "msg": f"JSON galat: {str(e)[:70]}"})

    # bracket ginti (har language)
    for o, c, nm in (("(", ")", "bracket"), ("[", "]", "square"),
                     ("{", "}", "curly")):
        # string ke andar wale mat gino — motamoti check
        plain = re.sub(r'"[^"\n]*"|\'[^\'\n]*\'', "", code)
        if plain.count(o) != plain.count(c):
            bad.append({"line": 0, "kind": "bracket",
                        "msg": f"{nm} match nahi: {plain.count(o)} "
                               f"'{o}' par {plain.count(c)} '{c}'"})

    # khatarnak cheezein
    danger = [
        (r"\beval\s*\(", "eval() — hacker code chala sakta hai"),
        (r"\bexec\s*\(", "exec() — khatarnak"),
        (r"shell\s*=\s*True", "shell=True — command injection"),
        (r"verify\s*=\s*False", "SSL verify off"),
        (r"DEBUG\s*=\s*True", "DEBUG on — production me mat rakho"),
        (r"0\.0\.0\.0.{0,20}debug", "debug server public pe"),
    ]
    for rx, msg in danger:
        m = re.search(rx, code)
        if m:
            bad.append({"line": code[:m.start()].count("\n") + 1,
                        "kind": "risk", "msg": msg})

    # secret leak
    for rx, msg in ((r"['\"](sk-[A-Za-z0-9_\-]{20,})['\"]",
                     "OpenAI/OpenRouter key code me padi hai"),
                    (r"['\"](gsk_[A-Za-z0-9]{20,})['\"]",
                     "Groq key code me padi hai"),
                    (r"['\"](nvapi-[A-Za-z0-9_\-]{20,})['\"]",
                     "NVIDIA key code me padi hai"),
                    (r"['\"]([0-9]{8,10}:AA[A-Za-z0-9_\-]{30,})['\"]",
                     "Telegram bot token code me pada hai")):
        m = re.search(rx, code)
        if m:
            bad.append({"line": code[:m.start()].count("\n") + 1,
                        "kind": "secret", "msg": msg})
    return bad


def crash_info(sid):
    """Console se crash ka log nikalo."""
    import engine
    import autofix
    lines = engine.console(sid, 0) or []
    txt = "\n".join(str(x.get("x", "")) for x in lines[-90:])
    if not autofix.crashed(txt):
        return "", "", 0
    f, ln = autofix.guess_file(txt)
    return txt[-3000:], f, ln


# ═══════════════════════════════════════════════
#   💼 PLAN — agent ka kaam ka naksha
# ═══════════════════════════════════════════════

_lock = threading.RLock()
_st = {"plans": {}, "day": "", "runs": {}}


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


_load()


def _newid():
    return "p" + str(int(time.time() * 1000))[-9:]


def _roll():
    if _st.get("day") != _today():
        _st["day"] = _today()
        _st["runs"] = {}
        # 2 ghante purane plan hata do
        cut = time.time() - 7200
        _st["plans"] = {k: v for k, v in _st.get("plans", {}).items()
                        if v.get("t", 0) > cut}
        _save()


def get_plan(pid):
    return _st.get("plans", {}).get(pid)


def _put(plan):
    with _lock:
        _st.setdefault("plans", {})[plan["id"]] = plan
        _save()


# ═══════════════════════════════════════════════
#   STEP 1 — DEKHO (scan + diagnose)
# ═══════════════════════════════════════════════

def investigate(uid, sid, user=None, is_admin=False, note=""):
    """
    Agent ka pehla kaam: file uthao, padho, galti dhoondho,
    AI se fix likhwao — par LAGAO MAT. Sirf plan banao.

    Return: plan dict — user ko dikhane ke liye
    """
    import aiboss
    import db
    import engine

    pk = aperks(user, is_admin)
    if not pk["on"]:
        return {"ok": False, "err": "plan",
                "msg": f"Boss Agent {pk['tier']} plan me nahi hai. "
                       f"Pro se milta hai."}

    _roll()
    ukey = str((user or {}).get("id", 0))
    used = _st.get("runs", {}).get(ukey, 0)
    # VIP (business) aur admin — koi ginti nahi
    if not unlimited(pk) and used >= pk["runs"]:
        return {"ok": False, "err": "cap",
                "msg": f"Aaj ke {pk['runs']} agent-run khatam. "
                       f"Kal phir — ya Business plan lo "
                       f"(unlimited)."}

    if not db.get_app(sid, uid):
        return {"ok": False, "err": "404", "msg": "Server nahi mila"}

    t0 = time.time()
    files = scan(uid, sid, pk["files"])
    if not files:
        return {"ok": False, "err": "empty",
                "msg": "Is server me koi code file nahi mili. "
                       "Pehle file upload karo."}

    log, cfile, cline = crash_info(sid)

    # ⚠️ Doosra sabak asli test se: console memory me hota hai.
    #    Restart ke baad purana crash gayab ho jata hai, to
    #    crash_info() khali laut aati hai aur agent samajhta hai
    #    "sab theek" — jabki server band pada hai.
    #    Isliye: agar server CHAL HI NAHI RAHA, to use crash maano.
    down = False
    try:
        down = not engine.is_running(sid)
    except Exception:
        pass
    crashed_now = bool(log) or down
    entry = (engine.detect(engine.server_dir(uid, sid)) or {}).get(
        "entry", "")
    steps = []
    fixes = []
    checked = 0

    # ── har file khud padho ──
    for f in files:
        code = engine.read_file(uid, sid, f["path"], MAX_FILE) or ""
        if not code.strip():
            continue
        checked += 1
        probs = quick_check(f["path"], code)
        is_crash = bool(cfile and f["path"].endswith(cfile))

        # ⚠️ Ye sabak asli test se mila: pehle sirf quick_check aur
        #    crash-file dekhte the. helper.py ka syntax theek hone ke
        #    baad main.py ka CHHUPA IndexError nikla — kyunki runtime
        #    galti static check kabhi nahi pakadta.
        #    Ab: server crash hua hai to ENTRY file bhi hamesha AI ko
        #    dikhao, chahe upar se saaf lage.
        is_entry = bool(entry and f["path"] == entry)
        deep = crashed_now and (is_crash or is_entry)

        if not probs and not deep:
            steps.append({"file": f["path"], "st": "clean",
                          "msg": "sab theek"})
            continue

        why = []
        if is_crash:
            why.append(f"crash isi file me (line {cline})")
        elif deep:
            why.append("server chal nahi raha — ye main file hai, "
                       "runtime galti dhoondho (index, None, "
                       "type mismatch)")
        for p in probs:
            why.append(p["msg"])

        # ── AI se fix mangao ──
        job = "fix" if (deep or any(p["kind"] == "syntax"
                                    for p in probs)) else "review"
        ask = (f"File: {f['path']}\n"
               f"Problem:\n- " + "\n- ".join(why[:6]) + "\n")
        if is_crash and log:
            ask += f"\nCrash log:\n{log[-1500:]}\n"
        if note:
            ask += f"\nUser ne bola: {note}\n"
        ask += (f"\nPOORA CODE:\n{code[:20000]}\n\n"
                f"Dhyaan se dekho — SYNTAX ke saath RUNTIME galti "
                f"bhi dhoondho: list index range se bahar, variable "
                f"jo define hi nahi, int+str jodna, None pe method, "
                f"key jo dict me hai hi nahi.\n"
                f"Theek kiya hua POORA code do. Sirf code, koi "
                f"explanation nahi. Code block me do.")

        r = aiboss.run(ask, user, is_admin, hint=job, max_tok=4000)
        if not r.get("ok"):
            steps.append({"file": f["path"], "st": "aifail",
                          "msg": r.get("msg", "AI ne jawab nahi diya"),
                          "why": why})
            continue

        new = _extract_code(r["answer"])
        v = _verify(f["path"], code, new)
        if not v["ok"]:
            steps.append({"file": f["path"], "st": "reject",
                          "msg": v["why"], "why": why,
                          "model": r.get("model", "")})
            continue

        fixes.append({"file": f["path"], "old": code, "new": new,
                      "why": why, "model": r.get("model", ""),
                      "prov": r.get("provider", ""),
                      "crash": is_crash,
                      "kinds": sorted({p["kind"] for p in probs}),
                      "d_old": len(code), "d_new": len(new)})
        steps.append({"file": f["path"], "st": "fix",
                      "msg": why[0] if why else "sudhar",
                      "why": why, "model": r.get("model", ""),
                      "prov": r.get("provider", "")})

    with _lock:
        _st.setdefault("runs", {})[ukey] = used + 1
        _save()

    plan = {
        "id": _newid(), "t": time.time(), "uid": uid, "sid": sid,
        "tier": pk["tier"], "can_deploy": pk["deploy"],
        "scanned": checked, "found": len(fixes),
        "steps": steps, "fixes": fixes,
        "crash": crashed_now, "crash_file": cfile,
        "down": down,
        "ms": int((time.time() - t0) * 1000),
        "applied": False, "deployed": False,
        "note": note[:200],
    }
    _put(plan)

    # ── Agent kya bolega ──
    if not fixes:
        plan["say"] = (f"Sir, maine {checked} file poori padhi. "
                       f"Koi galti nahi mili — sab theek hai.")
        plan["ask"] = ""
    else:
        n = len(fixes)
        names = ", ".join(x["file"] for x in fixes[:3])
        if n > 3:
            names += f" +{n - 3} aur"
        plan["say"] = (f"Sir, maine {checked} file padhi. "
                       f"{n} file me galti mili: {names}. "
                       f"Fix taiyaar hai.")
        plan["ask"] = "apply"
    plan["ok"] = True
    _put(plan)
    return plan


def _extract_code(ans):
    """AI ke jawab se sirf code nikalo."""
    if not ans:
        return ""
    m = re.findall(r"```[a-zA-Z0-9]*\n(.*?)```", ans, re.S)
    if m:
        return max(m, key=len).strip()
    # bina fence ke — pehli line agar prose hai to hata do
    lines = ans.strip().split("\n")
    while lines and not lines[0].strip():
        lines.pop(0)
    return "\n".join(lines).strip()


def _verify(path, old, new):
    """
    ⚠️ Ye sabse zaroori guard hai. AI ka code lagane se PEHLE
    check — warna AI ki galti aapki file kha jayegi.
    """
    if not new or len(new.strip()) < 5:
        return {"ok": False, "why": "AI ne khali code diya"}
    if new.strip() == old.strip():
        return {"ok": False, "why": "koi badlav nahi"}
    if len(old) > 400 and len(new) < len(old) * 0.35:
        return {"ok": False,
                "why": f"AI ne {100 - int(len(new) * 100 / len(old))}% "
                       f"code kaat diya — shaqi"}
    if len(new) > len(old) * 4 and len(old) > 200:
        return {"ok": False, "why": "AI ne 4 guna code bana diya — shaqi"}
    ext = os.path.splitext(path)[1].lower()
    if ext == ".py":
        try:
            ast.parse(new)
        except SyntaxError as e:
            return {"ok": False,
                    "why": f"AI ka naya code hi toota: {e.msg}"}
    if ext == ".json":
        try:
            json.loads(new)
        except Exception as e:
            return {"ok": False,
                    "why": f"AI ka JSON hi galat: {str(e)[:50]}"}
    return {"ok": True, "why": ""}


# ═══════════════════════════════════════════════
#   STEP 2 — LAGAO (user ne HAAN bola tab)
# ═══════════════════════════════════════════════

def apply(pid, uid, user=None, is_admin=False):
    """User ne 'haan' bola — ab file badlo. Backup ke saath."""
    import engine
    p = get_plan(pid)
    if not p:
        return {"ok": False, "msg": "Plan expire ho gaya. Dobara scan karo."}
    if p["uid"] != uid:
        return {"ok": False, "msg": "Ye aapka plan nahi hai"}
    if p.get("applied"):
        return {"ok": False, "msg": "Pehle hi laga chuka hoon"}
    if not p["fixes"]:
        return {"ok": False, "msg": "Lagane ko kuch nahi hai"}

    sid = p["sid"]
    done, fail = [], []
    for f in p["fixes"]:
        try:
            engine.write_file(uid, sid, f["file"] + ".bak", f["old"])
            if engine.write_file(uid, sid, f["file"], f["new"]):
                done.append(f["file"])
                engine.log(sid, f"🕵️ Agent ne {f['file']} theek kiya "
                                f"({f['why'][0][:60] if f['why'] else ''})",
                           "ok")
            else:
                fail.append(f["file"])
        except Exception as e:
            fail.append(f"{f['file']}: {str(e)[:40]}")

    p["applied"] = True
    p["done"] = done
    p["failed"] = fail
    p["ask"] = "deploy" if (done and p["can_deploy"]) else ""
    _put(p)

    engine.log(sid, f"💾 Purani files .bak me safe hain "
                    f"({len(done)} file badli)", "out")

    msg = f"Ho gaya sir — {len(done)} file theek kar di."
    if fail:
        msg += f" {len(fail)} me dikkat aayi."
    if p["can_deploy"] and done:
        msg += " Ab deploy kar dun?"
    elif done:
        msg += (f" Deploy {p['tier']} plan me nahi hai — "
                f"Ultra se milta hai.")
    return {"ok": True, "msg": msg, "done": done, "failed": fail,
            "ask": p["ask"], "id": pid}


# ═══════════════════════════════════════════════
#   STEP 3 — DEPLOY (user ne phir HAAN bola)
# ═══════════════════════════════════════════════

def deploy(pid, uid, user=None, is_admin=False):
    """User ne deploy ko haan bola — restart karo aur dekho chala ya nahi."""
    import autofix
    import engine
    p = get_plan(pid)
    if not p:
        return {"ok": False, "msg": "Plan expire ho gaya"}
    if p["uid"] != uid:
        return {"ok": False, "msg": "Ye aapka plan nahi"}
    if not p.get("applied"):
        return {"ok": False, "msg": "Pehle fix apply karo"}
    if not p["can_deploy"]:
        return {"ok": False, "err": "plan",
                "msg": f"Deploy {p['tier']} plan me nahi hai. "
                       f"Ultra ya Business chahiye."}
    if p.get("deployed"):
        return {"ok": False, "msg": "Deploy ho chuka hai"}

    sid = p["sid"]
    engine.log(sid, "🚀 Agent deploy kar raha hai…", "warn")

    # naye package chahiye to install karo
    try:
        engine.install_deps(uid, sid)
    except Exception:
        pass

    mark = time.time()
    engine.restart(uid, sid)
    good, why = autofix.verify(uid, sid, wait=7, since=mark)

    p["deployed"] = True
    p["deploy_ok"] = good
    p["ask"] = ""
    _put(p)

    if good:
        engine.log(sid, f"✅ Deploy kaamyaab — {why}", "ok")
        return {"ok": True, "worked": True,
                "msg": f"Deploy ho gaya sir — {why}"}
    engine.log(sid, f"⚠️ Deploy hua par {why}", "warn")
    p["ask"] = "retry"
    _put(p)
    return {"ok": True, "worked": False,
            "msg": f"Deploy to kar diya, par {why}. Lagta hai koi "
                   f"aur galti chhupi hai — dobara dhoondh loon? "
                   f"(Purana code .bak me safe hai)",
            "rollback": True, "ask": "retry", "id": pid}


# ═══════════════════════════════════════════════
#   ↩️ ROLLBACK — galat ho gaya to wapas
# ═══════════════════════════════════════════════

def rollback(pid, uid):
    """.bak se purana code wapas laao."""
    import engine
    p = get_plan(pid)
    if not p or p["uid"] != uid:
        return {"ok": False, "msg": "Plan nahi mila"}
    if not p.get("applied"):
        return {"ok": False, "msg": "Kuch badla hi nahi tha"}
    back = []
    for f in p["fixes"]:
        try:
            if engine.write_file(uid, p["sid"], f["file"], f["old"]):
                back.append(f["file"])
        except Exception:
            pass
    p["applied"] = False
    p["deployed"] = False
    _put(p)
    engine.log(p["sid"], f"↩️ Agent ne {len(back)} file wapas "
                         f"purani kar di", "warn")
    return {"ok": True, "msg": f"{len(back)} file wapas purani kar di",
            "files": back}


# ═══════════════════════════════════════════════
#   📊 STATUS
# ═══════════════════════════════════════════════

def status(user=None, is_admin=False):
    _roll()
    pk = aperks(user, is_admin)
    ukey = str((user or {}).get("id", 0))
    used = _st.get("runs", {}).get(ukey, 0)
    unl = unlimited(pk)
    return {"on": pk["on"], "tier": pk["tier"], "files": pk["files"],
            "deploy": pk["deploy"], "runs": pk["runs"],
            "used": used,
            "left": (-1 if unl else max(0, pk["runs"] - used)),
            "unlimited": unl,
            "left_txt": ("unlimited" if unl
                         else f"{max(0, pk['runs'] - used)} baaki"),
            "auto": pk["auto"]}


# ═══════════════════════════════════════════════════════
#   💬 AGENT SE BAAT-CHEET  (chat mode)
#
#   Malik ka hukum:
#     "chat board jaisa rahega, usse hum baat kar sake.
#      Aisa na ki 'ye dhoondho vo dhoondho'. Jaise AI Boss
#      banaya hai vaise."
#
#   Isliye ab do tareeke hain:
#     • investigate()  — purana: ek button, poora scan
#     • chat()         — naya: baat karo, wo file dekh kar
#                        jawab de, aur zaroorat pade to
#                        khud fix likh de
#
#   Agent ke paas SACH ME file hoti hai — wo padh kar
#   bolta hai, andaza nahi lagata.
# ═══════════════════════════════════════════════════════

AGENT_SYS = """Tum "BOSS AGENT" ho — RAVAN X HOSTING ka code doctor.
Ujjawal X Official ne banaya hai.

TUM KYA HO:
  User ke server ki files SACH ME tumhare saamne hain. Tum
  unhe padh kar baat karte ho — andaza nahi lagate.

KAISE BAAT KARNI HAI:
  • Hinglish (Hindi shabd Latin script me). Poora English
    me jawab MAT do.
  • Seedha kaam ki baat. "Zaroor!", "Bilkul!", "Main aapki
    madad ke liye hoon" — aise ghisay-pitay jumle MAT bolo.
  • Chhota jawab — 3-6 line. Zyada tabhi jab code dena ho.
  • Dost ki tarah baat karo, robot ki tarah nahi.

CODE KE BAARE ME:
  • Bug dikhe to SAAF batao: kaunsi file, kaunsi line, kya
    galat hai.
  • Fix dena ho to POORI file do, aadhi nahi:
        ```python
        # poora naya code yahan
        ```
  • Pehle samjhao 1-2 line me ki kya badla, phir code.
  • Pata na ho to saaf bolo "ye file mere paas nahi hai" ya
    "ye mujhe nahi pata" — bana kar mat batao.

  • User sirf baat kar raha ho (jaise "hi", "kaise ho",
    "ye kya karta hai") to bas jawab do — code mat thoko."""


def _files_for_chat(uid, sid, limit=10, want=""):
    """
    Chat ke liye files padho.

    Agar user ne kisi file ka naam liya hai to wo pehle.
    Warna sabse zaroori (main.py, app.py, index.js...) pehle.
    """
    import engine
    files = scan(uid, sid, limit=60)
    if not files:
        return [], ""

    w = (want or "").lower()
    def score(f):
        nm = os.path.basename(f["path"]).lower()
        sc = 0
        if w and nm in w:
            sc -= 100          # user ne naam liya = sabse upar
        if nm in ("main.py", "app.py", "bot.py", "index.js",
                  "server.js", "run.py", "start.py"):
            sc -= 50
        if nm in ("requirements.txt", "package.json"):
            sc -= 20
        return (sc, f.get("size", 0))

    files.sort(key=score)
    folder = engine.server_dir(uid, sid)
    out = []
    total = 0
    for f in files[:limit]:
        try:
            full = os.path.join(folder, f["path"])
            code = open(full, encoding="utf-8",
                        errors="replace").read()
        except Exception:
            continue
        if len(code) > 6000:
            code = code[:6000] + "\n... (file aur lambi hai)"
        total += len(code)
        out.append({"path": f["path"], "code": code})
        if total > 26000:
            break
    return out, folder


def chat(uid, sid, text, user=None, is_admin=False, history=None):
    """
    Agent se baat karo.

    Wo file padh kar jawab deta hai. Fix likhe to code block
    me — aur agar wo poori file ka code hai to hum plan bana
    dete hain (user ek tap me laga sakta hai).

    Return: {ok, answer, plan_id?, file?, files_read, model}
    """
    import aiboss
    import db

    pk = aperks(user, is_admin)
    if not pk["on"]:
        return {"ok": False, "err": "plan",
                "msg": f"Boss Agent {pk['tier']} plan me nahi hai. "
                       f"Pro se milta hai."}

    _roll()
    ukey = str((user or {}).get("id", 0))
    used = _st.get("runs", {}).get(ukey, 0)
    if not unlimited(pk) and used >= pk["runs"]:
        return {"ok": False, "err": "cap",
                "msg": f"Aaj ke {pk['runs']} agent-run khatam. "
                       f"Kal phir — ya Business plan lo "
                       f"(unlimited)."}

    text = (text or "").strip()[:4000]
    if not text:
        return {"ok": False, "err": "khali", "msg": "Kuch to boliye"}

    app = db.get_app(sid, uid)
    if not app:
        return {"ok": False, "err": "404", "msg": "Server nahi mila"}

    # ── file padho ──
    files, folder = _files_for_chat(uid, sid, pk["files"], text)
    crash, cfile, cline = crash_info(sid)

    ctx = [f"SERVER: {app.get('name','?')} "
           f"({app.get('lang','?')} · {app.get('plan','?')})"]
    if crash:
        ctx.append(f"\n⚠️ SERVER CRASH HUA HAI:\n{crash[-1500:]}")
        if cfile:
            ctx.append(f"Crash yahan lagta hai: {cfile}"
                       + (f" line {cline}" if cline else ""))
    if files:
        ctx.append(f"\nSERVER KI FILES ({len(files)}):")
        for f in files:
            ctx.append(f"\n----- {f['path']} -----\n{f['code']}")
    else:
        ctx.append("\n(is server par abhi koi code file nahi hai)")

    prompt = ("\n".join(ctx) + "\n\n"
              "=====================\n"
              f"USER BOLA: {text}")

    r = aiboss.run(prompt, user, is_admin, hint="agent",
                   max_tok=2200, history=history or [])
    if not r.get("ok"):
        return {"ok": False, "err": r.get("err", "ai"),
                "msg": r.get("msg", "AI se jawab nahi aaya")}

    ans = r.get("answer", "")

    # ── AI ne poori file ka code diya? to plan bana do ──
    plan_id = ""
    target = ""
    no_fix_why = ""
    code = _extract_code(ans)
    if code and len(code) > 60 and files:
        # kaunsi file? user ke shabd ya AI ke jawab se
        low = (text + " " + ans[:600]).lower()
        for f in files:
            nm = os.path.basename(f["path"]).lower()
            if nm in low:
                target = f["path"]
                break
        if not target:
            target = files[0]["path"]

        old = ""
        for f in files:
            if f["path"] == target:
                old = f["code"]
                break
        # ⚠️⚠️ YAHAN BUG THA ⚠️⚠️
        #
        #    Maine plan me "items" / "path" likh diya tha, par
        #    apply() "fixes" / "file" dhoondhta hai. Isliye
        #    "File me laga do" dabane par
        #    "Lagane ko kuch nahi hai" aata tha aur code
        #    file me kabhi replace hi nahi hota tha.
        #
        #    Ab bilkul wahi dhancha jo investigate() banata hai.
        v = _verify(target, old, code)
        if v.get("ok"):
            plan_id = _newid()
            _put({
                "id": plan_id, "t": time.time(),
                "uid": uid, "sid": sid,
                "tier": pk["tier"], "can_deploy": pk["deploy"],
                "scanned": len(files), "found": 1,
                "from": "chat",
                "steps": [{"file": target, "st": "fix",
                           "msg": text[:120], "why": [text[:120]],
                           "model": r.get("model", ""),
                           "prov": r.get("provider", "")}],
                "fixes": [{"file": target, "old": old, "new": code,
                           "why": [text[:200]],
                           "model": r.get("model", ""),
                           "prov": r.get("provider", ""),
                           "crash": bool(crash), "kinds": ["chat"],
                           "d_old": len(old), "d_new": len(code)}],
                "crash": bool(crash), "crash_file": cfile,
                "down": False,
                "ms": r.get("ms", 0),
                "applied": False, "deployed": False,
                "note": text[:200],
            })
        else:
            # kyun nahi laga — user ko batao, chup mat raho
            no_fix_why = v.get("why", "")

    with _lock:
        _st.setdefault("runs", {})[ukey] = used + 1
        _save()

    return {"ok": True, "answer": ans, "plan_id": plan_id,
            "file": target, "files_read": len(files),
            "no_fix": no_fix_why,
            "crashed": bool(crash),
            "model": r.get("model", ""), "ms": r.get("ms", 0),
            "left": (-1 if unlimited(pk)
                     else max(0, pk["runs"] - used - 1))}
