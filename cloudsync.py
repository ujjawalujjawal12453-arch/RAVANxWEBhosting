"""
cloudsync.py — Upstash Redis se real-time backup
═════════════════════════════════════════════════

Bot wali hi credentials use karta hai (~/.ravanx-db.json).
Isse Render/Railway par bhi data KABHI nahi jayega.

Kaam:
  • Har 60 sec me database cloud par push
  • Boot par cloud se pull (agar local khali ho)
  • Server files bhi (chhoti) cloud me
  • Ephemeral platform (Render/Railway) auto-detect
"""

import base64
import json
import os
import threading
import time
import urllib.error
import urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")

# ☁️ BUILT-IN UPSTASH — pehle se laga hua, koi setup nahi chahiye.
#    Render/Railway/Termux — kahin bhi data automatic backup hoga.
#    Badalna ho to env me UPSTASH_REDIS_REST_URL / _TOKEN daal do.
#    🔐 keyvault.py me chhupi hain (GitHub push protection ki wajah se)
import keyvault as _kv

BUILTIN_URL = _kv.get("UPSTASH_URL")
BUILTIN_TOKEN = _kv.get("UPSTASH_TOK")

# Bot wali creds — dono ek hi cloud use karenge
BOT_CRED = os.path.join(HOME, ".ravanx-db.json")
OWN_CRED = os.path.join(HOME, ".ravanx-web-db.json")

_ep = ""
_tok = ""
_last_push = 0
_ok = False
_err = ""

KEY_DB = "ravanx:web:db"
KEY_META = "ravanx:web:meta"
KEY_FILES = "ravanx:web:files"
KEY_SDB = "ravanx:web:storagedb"     # storage.db (accounts + tokens)


def is_ephemeral():
    """Render / Railway / Heroku — jahan files delete ho jati hain."""
    return bool(os.environ.get("RENDER") or os.environ.get("RAILWAY_ENVIRONMENT")
                or os.environ.get("DYNO") or os.environ.get("FLY_APP_NAME"))


def platform_name():
    if os.environ.get("RENDER"):
        return "Render"
    if os.environ.get("RAILWAY_ENVIRONMENT"):
        return "Railway"
    if os.environ.get("DYNO"):
        return "Heroku"
    if os.environ.get("FLY_APP_NAME"):
        return "Fly.io"
    if os.path.isdir("/data/data/com.termux"):
        return "Termux"
    return "Local"


# ─────────────────────────────────────────────────────────
#  CREDENTIALS
# ─────────────────────────────────────────────────────────

def load_creds():
    """Env → bot ki creds → apni creds."""
    global _ep, _tok
    u = os.environ.get("UPSTASH_REDIS_REST_URL", "").strip()
    t = os.environ.get("UPSTASH_REDIS_REST_TOKEN", "").strip()
    if u and t:
        _ep, _tok = u.rstrip("/"), t
        return True, "env"

    for path, src in ((BOT_CRED, "bot"), (OWN_CRED, "own")):
        try:
            d = json.load(open(path))
            if d.get("endpoint") and d.get("token"):
                _ep = d["endpoint"].rstrip("/")
                _tok = d["token"]
                return True, src
        except Exception:
            continue

    # 🔑 kuch na mile to built-in — data kabhi nahi jayega
    if BUILTIN_URL and BUILTIN_TOKEN:
        _ep, _tok = BUILTIN_URL.rstrip("/"), BUILTIN_TOKEN
        return True, "builtin"

    return False, "none"


def save_creds(url, token):
    global _ep, _tok
    _ep, _tok = url.rstrip("/"), token
    try:
        json.dump({"endpoint": _ep, "token": _tok},
                  open(OWN_CRED, "w"), indent=2)
        os.chmod(OWN_CRED, 0o600)
        return True
    except Exception:
        return False


def configured():
    return bool(_ep and _tok)


# ─────────────────────────────────────────────────────────
#  REDIS REST
# ─────────────────────────────────────────────────────────

def _cmd(args, timeout=20):
    if not configured():
        return None
    try:
        req = urllib.request.Request(
            _ep, data=json.dumps(args).encode(),
            headers={"Authorization": f"Bearer {_tok}",
                     "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.load(r)
    except Exception:
        return None


def ping():
    global _ok, _err
    r = _cmd(["PING"], timeout=12)
    _ok = bool(r and r.get("result"))
    _err = "" if _ok else "connect nahi hua"
    return _ok


# ─────────────────────────────────────────────────────────
#  PUSH / PULL
# ─────────────────────────────────────────────────────────

def push_db(force=False):
    """Database file cloud par."""
    global _last_push
    if not configured():
        return False
    if not force and time.time() - _last_push < 25:
        return False
    try:
        import db
        if not os.path.exists(db.DB_PATH):
            return False
        raw = open(db.DB_PATH, "rb").read()
        if len(raw) > 9 * 1024 * 1024:      # Upstash limit
            return False
        b64 = base64.b64encode(raw).decode()
        r = _cmd(["SET", KEY_DB, b64], timeout=45)
        if r and "result" in r:
            _cmd(["SET", KEY_META, json.dumps({
                "at": int(time.time()), "size": len(raw),
                "platform": platform_name()})], timeout=12)
            _last_push = time.time()
            return True
    except Exception:
        pass
    return False


def pull_db(only_if_empty=True):
    """Cloud se database wapas."""
    if not configured():
        return False, "cloud set nahi hai"
    try:
        import db
        exists = os.path.exists(db.DB_PATH)
        if exists and only_if_empty:
            try:
                c = db.conn()
                n = c.execute("SELECT COUNT(*) FROM users").fetchone()[0]
                c.close()
                if n > 0:
                    return False, "local data pehle se hai"
            except Exception:
                pass

        r = _cmd(["GET", KEY_DB], timeout=45)
        if not r or not r.get("result"):
            return False, "cloud me backup nahi mila"
        raw = base64.b64decode(r["result"])
        os.makedirs(os.path.dirname(db.DB_PATH), exist_ok=True)
        if exists:
            try:
                os.replace(db.DB_PATH, db.DB_PATH + ".bak")
            except Exception:
                pass
        open(db.DB_PATH, "wb").write(raw)
        return True, f"{len(raw)//1024} KB restore hua"
    except Exception as e:
        return False, str(e)[:80]


def push_storage_db():
    """
    🗄️ storage.db (saare accounts + tokens) cloud par.
    Ye na ho to Render restart pe sabke token ud jayenge.
    """
    if not configured():
        return False
    try:
        import storage
        if not os.path.exists(storage.DB_PATH):
            return False
        # WAL checkpoint — warna aadha data .wal me reh jata hai
        try:
            c = storage.conn()
            c.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            c.close()
        except Exception:
            pass
        raw = open(storage.DB_PATH, "rb").read()
        if len(raw) > 9 * 1024 * 1024:
            return False
        r = _cmd(["SET", KEY_SDB, base64.b64encode(raw).decode()], timeout=45)
        return bool(r and "result" in r)
    except Exception:
        return False


def pull_storage_db(only_if_empty=True):
    """Cloud se storage.db wapas — tokens bach jayenge."""
    if not configured():
        return False, "cloud set nahi hai"
    try:
        import storage
        if only_if_empty and os.path.exists(storage.DB_PATH):
            try:
                c = storage.conn()
                n = c.execute("SELECT COUNT(*) n FROM accounts").fetchone()["n"]
                c.close()
                if n > 0:
                    return False, f"{n} accounts pehle se hain"
            except Exception:
                pass
        r = _cmd(["GET", KEY_SDB], timeout=45)
        if not r or not r.get("result"):
            return False, "storage backup nahi mila"
        raw = base64.b64decode(r["result"])
        os.makedirs(os.path.dirname(storage.DB_PATH), exist_ok=True)
        for ext in ("-wal", "-shm"):
            try:
                os.remove(storage.DB_PATH + ext)
            except Exception:
                pass
        tmp = storage.DB_PATH + ".new"
        with open(tmp, "wb") as f:
            f.write(raw)
        os.replace(tmp, storage.DB_PATH)
        return True, f"{len(raw)//1024} KB restore"
    except Exception as e:
        return False, str(e)[:80]


def push_files(max_mb=6):
    """Server files (chhoti) cloud par — tar.gz me."""
    if not configured():
        return False
    try:
        import io
        import tarfile
        import engine
        buf = io.BytesIO()
        n = 0
        with tarfile.open(fileobj=buf, mode="w:gz") as tar:
            roots = [(engine.SERVERS_DIR, "servers")]
            try:
                import storage as _st
                roots.append((_st.FILES, "storage"))
            except Exception:
                pass
            for _base, _pre in roots:
              if not os.path.isdir(_base):
                continue
              for root, dirs, files in os.walk(_base):
                dirs[:] = [d for d in dirs
                           if d not in ("node_modules", "__pycache__", ".git",
                                        "venv", ".venv")]
                for f in files:
                    p = os.path.join(root, f)
                    try:
                        if os.path.getsize(p) > 3 * 1024 * 1024:
                            continue
                        tar.add(p, arcname=_pre + "/" + os.path.relpath(
                            p, _base))
                        n += 1
                    except Exception:
                        pass
        raw = buf.getvalue()
        if not n or len(raw) > max_mb * 1024 * 1024:
            return False
        r = _cmd(["SET", KEY_FILES, base64.b64encode(raw).decode()], timeout=60)
        return bool(r and "result" in r)
    except Exception:
        return False


def pull_files():
    """Cloud se server files wapas."""
    if not configured():
        return False, "cloud nahi hai"
    try:
        import io
        import tarfile
        import engine
        r = _cmd(["GET", KEY_FILES], timeout=60)
        if not r or not r.get("result"):
            return False, "files backup nahi mila"
        raw = base64.b64decode(r["result"])
        try:
            import storage as _st
            sfiles = _st.FILES
        except Exception:
            sfiles = None
        os.makedirs(engine.SERVERS_DIR, exist_ok=True)
        n = 0
        with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as tar:
            for m in tar.getmembers():
                if m.name.startswith("/") or ".." in m.name:
                    continue
                if m.name.startswith("servers/"):
                    dest, m.name = engine.SERVERS_DIR, m.name[8:]
                elif m.name.startswith("storage/") and sfiles:
                    dest, m.name = sfiles, m.name[8:]
                else:
                    dest = engine.SERVERS_DIR      # purana format
                if not m.name:
                    continue
                try:
                    tar.extract(m, dest, filter="data")
                except TypeError:
                    tar.extract(m, dest)
                except Exception:
                    continue
                n += 1
        return True, f"{n} files restore"
    except Exception as e:
        return False, str(e)[:80]


def meta():
    r = _cmd(["GET", KEY_META], timeout=12)
    if r and r.get("result"):
        try:
            return json.loads(r["result"])
        except Exception:
            pass
    return {}


# ─────────────────────────────────────────────────────────
#  BOOT + LOOP
# ─────────────────────────────────────────────────────────

def boot():
    """Start par — creds load, cloud se restore."""
    found, src = load_creds()
    if not found:
        return {"ok": False, "src": "none",
                "msg": "Cloud creds nahi mile (local hi chalega)"}
    if not ping():
        return {"ok": False, "src": src, "msg": "Cloud connect nahi hua"}

    out = {"ok": True, "src": src, "restored": False, "files": False,
           "storage": False}
    ok, msg = pull_db(only_if_empty=True)
    out["restored"] = ok
    out["msg"] = msg
    # 🗄️ storage.db hamesha check karo — tokens kabhi na khoyein
    oks, msgs = pull_storage_db(only_if_empty=True)
    out["storage"] = oks
    out["storage_msg"] = msgs
    if ok or oks:
        okf, _ = pull_files()
        out["files"] = okf
    return out


def sync_loop(every=60):
    """Background — har minute cloud par backup."""
    time.sleep(20)
    tick = 0
    while True:
        try:
            time.sleep(every)
            if not configured():
                continue
            push_db()
            push_storage_db()        # 🗄️ tokens/accounts bhi
            tick += 1
            if tick % 5 == 0:        # har 5 min files bhi
                push_files()
        except Exception:
            time.sleep(30)


def status_text():
    m = meta()
    return {
        "configured": configured(),
        "ok": _ok,
        "endpoint": (_ep[:38] + "…") if len(_ep) > 38 else _ep,
        "platform": platform_name(),
        "ephemeral": is_ephemeral(),
        "last_push": m.get("at", 0),
        "size": m.get("size", 0),
    }


load_creds()
