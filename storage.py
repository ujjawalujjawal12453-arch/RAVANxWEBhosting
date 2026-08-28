"""
storage.py — RAVAN X STORAGE (website ke andar hi)
═══════════════════════════════════════════════════

Ye wahi storage server hai jo pehle alag chalta tha — ab website ke
andar hi ghus gaya hai. Alag process, alag port, alag command: kuch nahi.
Website chali = storage bhi chalu.

Kya karta hai:
  • Har website user ka account APNE AAP ban jata hai (signup par)
  • Token apne aap milta hai (dashboard par dikhta hai)
  • File kitni bhi BADI ho — chalegi (stream hoti hai, RAM me nahi aati)
  • Server ki saari files apne aap yahan mirror hoti hain
  • KV store (database backup ke liye)
  • Delete = trash, mitao mat
  • API bahar se bhi chalti hai (bot / script / curl)

Data:  data/storage/storage.db  +  data/storage/files/<acct>/…
"""

import hashlib
import json
import mimetypes
import os
import re
import secrets
import shutil
import sqlite3
import threading
import time

BASE = os.path.dirname(os.path.abspath(__file__))

# 📁 Kahan rakhna hai — env se badal sakte ho (persistent disk ke liye)
ROOT = os.environ.get("STORAGE_DIR") or os.path.join(BASE, "data", "storage")
FILES = os.path.join(ROOT, "files")
TRASH = os.path.join(ROOT, "trash")
TMP = os.path.join(ROOT, "tmp")
DB_PATH = os.path.join(ROOT, "storage.db")

for _d in (ROOT, FILES, TRASH, TMP):
    os.makedirs(_d, exist_ok=True)

# 📦 Jagah PLAN se aati hai (theme.STORAGE_GB).
#    Ek file kitni badi ho sakti hai — 0 = jitni jagah bachi hai utni.
MAX_FILE_MB = int(os.environ.get("STORAGE_MAX_FILE_MB", "0"))
#    Fallback (plan na mile to)
DEFAULT_GB = int(os.environ.get("STORAGE_DEFAULT_GB", "1"))

CHUNK = 1024 * 512          # 512 KB — stream ka tukda
VERSION = "1.0.0"

_lock = threading.RLock()
_stats = {"up": 0, "down": 0, "bytes_in": 0, "bytes_out": 0}


# ═══════════════════════════════════════════════
#   DATABASE
# ═══════════════════════════════════════════════

def conn():
    c = sqlite3.connect(DB_PATH, timeout=30)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")
    return c


def init():
    with conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS accounts (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            name      TEXT UNIQUE NOT NULL,
            token     TEXT UNIQUE NOT NULL,
            pw_hash   TEXT,
            web_user  INTEGER DEFAULT 0,
            quota_mb  INTEGER DEFAULT 0,
            created   INTEGER,
            last_seen INTEGER,
            note      TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS blobs (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            acct    INTEGER NOT NULL,
            path    TEXT NOT NULL,
            size    INTEGER,
            sha     TEXT,
            updated INTEGER,
            deleted INTEGER DEFAULT 0,
            UNIQUE(acct, path)
        );
        CREATE TABLE IF NOT EXISTS kv (
            acct    INTEGER NOT NULL,
            k       TEXT NOT NULL,
            v       TEXT,
            updated INTEGER,
            PRIMARY KEY (acct, k)
        );
        CREATE TABLE IF NOT EXISTS logs (
            id     INTEGER PRIMARY KEY AUTOINCREMENT,
            acct   INTEGER,
            action TEXT,
            detail TEXT,
            at     INTEGER
        );
        CREATE INDEX IF NOT EXISTS ix_blob ON blobs(acct, deleted);
        CREATE INDEX IF NOT EXISTS ix_log  ON logs(acct, at DESC);
        CREATE INDEX IF NOT EXISTS ix_web  ON accounts(web_user);
        """)


def log(acct, action, detail=""):
    try:
        with _lock, conn() as c:
            c.execute("INSERT INTO logs(acct,action,detail,at) VALUES(?,?,?,?)",
                      (acct, action, str(detail)[:300], int(time.time())))
            c.execute("DELETE FROM logs WHERE id NOT IN "
                      "(SELECT id FROM logs ORDER BY id DESC LIMIT 8000)")
    except Exception:
        pass


# ═══════════════════════════════════════════════
#   HELPERS
# ═══════════════════════════════════════════════

def new_token():
    return "rvx_" + secrets.token_urlsafe(32)


def human(b):
    b = float(b or 0)
    for u in ("B", "KB", "MB", "GB"):
        if b < 1024:
            return f"{int(b)} B" if u == "B" else f"{b:.1f} {u}"
        b /= 1024
    return f"{b:.2f} TB"


def ago(t):
    if not t:
        return "kabhi nahi"
    d = int(time.time() - t)
    if d < 60:
        return f"{d}s pehle"
    if d < 3600:
        return f"{d // 60}m pehle"
    if d < 86400:
        return f"{d // 3600}h pehle"
    return f"{d // 86400}d pehle"


def acct_dir(aid):
    p = os.path.join(FILES, str(aid))
    os.makedirs(p, exist_ok=True)
    return p


def clean_rel(rel):
    """Path saaf karo — '/etc/passwd' -> 'etc/passwd', '..' block."""
    rel = (rel or "").strip().replace("\\", "/").lstrip("/")
    parts = [p for p in rel.split("/") if p not in ("", ".")]
    if not parts or any(p == ".." for p in parts):
        return ""
    return "/".join(parts)


def safe_path(aid, rel):
    """Apne folder se bahar jaana mana hai."""
    rel = clean_rel(rel)
    if not rel:
        return None
    base = os.path.realpath(acct_dir(aid))
    full = os.path.realpath(os.path.join(base, rel))
    return full if full.startswith(base + os.sep) else None


def usage(aid):
    with conn() as c:
        r = c.execute("SELECT COALESCE(SUM(size),0) s, COUNT(*) n "
                      "FROM blobs WHERE acct=? AND deleted=0", (aid,)).fetchone()
    return r["s"], r["n"]


def account(aid):
    with conn() as c:
        r = c.execute("SELECT * FROM accounts WHERE id=?", (aid,)).fetchone()
    return dict(r) if r else None


def by_token(tok):
    if not tok:
        return None
    with conn() as c:
        r = c.execute("SELECT * FROM accounts WHERE token=?",
                      (tok.strip(),)).fetchone()
        if r:
            c.execute("UPDATE accounts SET last_seen=? WHERE id=?",
                      (int(time.time()), r["id"]))
    return dict(r) if r else None


def by_name(name):
    with conn() as c:
        r = c.execute("SELECT * FROM accounts WHERE name=?", (name,)).fetchone()
    return dict(r) if r else None


def by_web_user(uid):
    with conn() as c:
        r = c.execute("SELECT * FROM accounts WHERE web_user=?",
                      (int(uid),)).fetchone()
    return dict(r) if r else None


# ═══════════════════════════════════════════════
#   ACCOUNTS
# ═══════════════════════════════════════════════

def register(name, password="", web_user=0):
    name = str(name or "").strip()[:40]
    if not re.fullmatch(r"[A-Za-z0-9_.-]{3,40}", name):
        return None, "Naam 3-40 letters ka ho (a-z, 0-9, _ . -)"
    with _lock, conn() as c:
        if c.execute("SELECT 1 FROM accounts WHERE name=?", (name,)).fetchone():
            return None, "Ye naam pehle se hai"
        tok = new_token()
        ph = (hashlib.sha256((password + name).encode()).hexdigest()
              if password else None)
        now = int(time.time())
        cur = c.execute(
            "INSERT INTO accounts(name,token,pw_hash,web_user,created,last_seen)"
            " VALUES(?,?,?,?,?,?)", (name, tok, ph, int(web_user), now, now))
        aid = cur.lastrowid
    acct_dir(aid)
    log(aid, "register", name)
    return {"id": aid, "name": name, "token": tok}, ""


def recover(name, password):
    a = by_name(str(name or "").strip())
    if not a or not a.get("pw_hash"):
        return None, "Account nahi mila (ya password set nahi tha)"
    if hashlib.sha256((password + a["name"]).encode()).hexdigest() != a["pw_hash"]:
        return None, "Password galat"
    log(a["id"], "recover", "")
    return a, ""


def reset_token(aid):
    tok = new_token()
    with _lock, conn() as c:
        c.execute("UPDATE accounts SET token=? WHERE id=?", (tok, aid))
    log(aid, "token_reset", "")
    return tok


def ensure_for_user(user):
    """
    🔑 SAB AUTOMATIC.
    Website ka har user -> storage account apne aap.
    User ko kuch nahi karna, na signup, na token.
    """
    if not user:
        return None
    a = by_web_user(user["id"])
    if a:
        return a
    base = re.sub(r"[^A-Za-z0-9_.-]", "",
                  (user.get("email") or "").split("@")[0]) or "user"
    base = base[:28] or "user"
    if len(base) < 3:
        base = base + "usr"
    name = f"{base}-{user['id']}"
    n = 0
    while by_name(name):
        n += 1
        name = f"{base}-{user['id']}-{n}"
    acc, err = register(name, web_user=user["id"])
    if not acc:
        return None
    log(acc["id"], "auto_create", f"web user #{user['id']}")
    return by_web_user(user["id"])


# ═══════════════════════════════════════════════
#   FILES  (unlimited — streaming)
# ═══════════════════════════════════════════════

def _record(aid, rel, size, sha):
    with _lock, conn() as c:
        c.execute("INSERT INTO blobs(acct,path,size,sha,updated,deleted) "
                  "VALUES(?,?,?,?,?,0) ON CONFLICT(acct,path) DO UPDATE SET "
                  "size=excluded.size, sha=excluded.sha, "
                  "updated=excluded.updated, deleted=0",
                  (aid, rel, size, sha, int(time.time())))


def plan_of(aid):
    """Is storage account ke website user ka plan."""
    a = account(aid) or {}
    wu = a.get("web_user") or 0
    if not wu:
        return "starter"          # bahar wala account (bot/script)
    try:
        import db
        u = db.get_user(wu)
        return (u or {}).get("plan") or "free"
    except Exception:
        return "free"


def quota_bytes(aid):
    """Kitni jagah mili hai — bytes me."""
    a = account(aid) or {}
    if a.get("quota_mb"):                       # admin ne manually di
        return a["quota_mb"] * 1024 * 1024
    try:
        import theme
        return theme.storage_gb(plan_of(aid)) * 1024 * 1024 * 1024
    except Exception:
        return DEFAULT_GB * 1024 * 1024 * 1024


def quota_left(aid):
    """Bytes bache."""
    used, _ = usage(aid)
    return max(0, quota_bytes(aid) - used)


def quota_info(aid):
    cap = quota_bytes(aid)
    used, cnt = usage(aid)
    return {"cap": cap, "cap_h": human(cap), "used": used,
            "used_h": human(used), "left": max(0, cap - used),
            "left_h": human(max(0, cap - used)), "files": cnt,
            "pct": min(100, round(used / cap * 100, 1)) if cap else 0,
            "plan": plan_of(aid), "full": used >= cap}


def save_stream(aid, rel, reader, total=None):
    """
    Stream se seedha disk par. RAM me poori file kabhi nahi aati,
    isliye 5 GB ki file bhi chalegi.
      reader: .read(n) wala object (socket / file)
    """
    rel = clean_rel(rel)
    fp = safe_path(aid, rel)
    if not fp:
        return None, "Path galat hai"
    if MAX_FILE_MB and total and total > MAX_FILE_MB * 1024 * 1024:
        return None, f"File {MAX_FILE_MB}MB se badi hai"

    q = quota_info(aid)
    left = q["left"]
    # purani file replace ho rahi ho to uski jagah wapas mil jayegi
    old = None
    with conn() as c:
        old = c.execute("SELECT size FROM blobs WHERE acct=? AND path=? "
                        "AND deleted=0", (aid, rel)).fetchone()
    if old:
        left += old["size"]
    if total and total > left:
        try:
            import theme
            nx = theme.next_plan(q["plan"])
        except Exception:
            nx = None
        msg = (f"Jagah kam hai — {q['plan'].title()} plan me "
               f"{q['cap_h']} milta hai, {human(left)} bacha hai. "
               f"File {human(total)} ki hai.")
        if nx:
            msg += f" {nx.title()} plan lo ya purani files hatao."
        return None, msg

    os.makedirs(os.path.dirname(fp), exist_ok=True)
    tmp = os.path.join(TMP, f"{aid}_{secrets.token_hex(8)}.part")
    h = hashlib.sha256()
    n = 0
    try:
        with open(tmp, "wb") as f:
            while True:
                want = CHUNK if total is None else min(CHUNK, total - n)
                if want <= 0:
                    break
                b = reader.read(want)
                if not b:
                    break
                f.write(b)
                h.update(b)
                n += len(b)
                if MAX_FILE_MB and n > MAX_FILE_MB * 1024 * 1024:
                    raise ValueError(f"File {MAX_FILE_MB}MB se badi hai")
                if n > left:
                    raise ValueError(
                        f"Jagah khatam — {q['cap_h']} ki limit hai "
                        f"({q['plan'].title()} plan)")
            f.flush()
            os.fsync(f.fileno())
        shutil.move(tmp, fp)
    except Exception as e:
        try:
            os.remove(tmp)
        except Exception:
            pass
        return None, str(e)[:120]

    sha = h.hexdigest()[:16]
    _record(aid, rel, n, sha)
    _stats["up"] += 1
    _stats["bytes_in"] += n
    log(aid, "upload", f"{rel} ({human(n)})")
    return {"path": rel, "size": n, "sha": sha, "size_h": human(n)}, ""


def save_bytes(aid, rel, data):
    import io
    return save_stream(aid, rel, io.BytesIO(data), len(data))


def put_file(aid, rel, local_path):
    """Disk par ki file storage me daalo (copy, RAM me nahi)."""
    try:
        with open(local_path, "rb") as f:
            return save_stream(aid, rel, f, os.path.getsize(local_path))
    except Exception as e:
        return None, str(e)[:120]


def move(aid, src, dst):
    """File ka path badlo (folder field baad me mila to)."""
    src, dst = clean_rel(src), clean_rel(dst)
    if not src or not dst or src == dst:
        return False
    sp, dp = safe_path(aid, src), safe_path(aid, dst)
    if not sp or not dp or not os.path.isfile(sp):
        return False
    try:
        os.makedirs(os.path.dirname(dp), exist_ok=True)
        shutil.move(sp, dp)
    except Exception:
        return False
    with _lock, conn() as c:
        c.execute("DELETE FROM blobs WHERE acct=? AND path=?", (aid, dst))
        c.execute("UPDATE blobs SET path=? WHERE acct=? AND path=?",
                  (dst, aid, src))
    return True


def open_file(aid, rel):
    fp = safe_path(aid, rel)
    if not fp or not os.path.isfile(fp):
        return None, 0, ""
    ct = mimetypes.guess_type(fp)[0] or "application/octet-stream"
    return fp, os.path.getsize(fp), ct


def list_files(aid, prefix=""):
    with conn() as c:
        if prefix:
            rows = c.execute(
                "SELECT path,size,sha,updated FROM blobs WHERE acct=? AND "
                "deleted=0 AND path LIKE ? ORDER BY updated DESC",
                (aid, prefix + "%")).fetchall()
        else:
            rows = c.execute(
                "SELECT path,size,sha,updated FROM blobs WHERE acct=? AND "
                "deleted=0 ORDER BY updated DESC", (aid,)).fetchall()
    return [dict(r) for r in rows]


def delete(aid, rel):
    rel = clean_rel(rel)
    fp = safe_path(aid, rel)
    if not fp or not os.path.isfile(fp):
        return False, "File nahi mili"
    td = os.path.join(TRASH, str(aid))
    os.makedirs(td, exist_ok=True)
    try:
        shutil.move(fp, os.path.join(
            td, f"{int(time.time())}_{os.path.basename(fp)}"))
    except Exception as e:
        return False, str(e)[:80]
    with _lock, conn() as c:
        c.execute("UPDATE blobs SET deleted=1 WHERE acct=? AND path=?",
                  (aid, rel))
    log(aid, "delete", rel)
    return True, "Trash me chali gayi"


# ═══════════════════════════════════════════════
#   KV  (database backup)
# ═══════════════════════════════════════════════

def kv_set(aid, k, v):
    if not k or len(k) > 200:
        return False
    with _lock, conn() as c:
        c.execute("INSERT INTO kv(acct,k,v,updated) VALUES(?,?,?,?) "
                  "ON CONFLICT(acct,k) DO UPDATE SET v=excluded.v, "
                  "updated=excluded.updated", (aid, k, v, int(time.time())))
    log(aid, "kv_set", f"{k} ({human(len(v or ''))})")
    return True


def kv_get(aid, k):
    with conn() as c:
        r = c.execute("SELECT v,updated FROM kv WHERE acct=? AND k=?",
                      (aid, k)).fetchone()
    return dict(r) if r else None


def kv_list(aid):
    with conn() as c:
        rows = c.execute("SELECT k,LENGTH(v) sz,updated FROM kv WHERE acct=? "
                         "ORDER BY updated DESC", (aid,)).fetchall()
    return [dict(r) for r in rows]


def kv_del(aid, k):
    with _lock, conn() as c:
        c.execute("DELETE FROM kv WHERE acct=? AND k=?", (aid, k))
    log(aid, "kv_del", k)
    return True


def logs(aid, n=60):
    with conn() as c:
        rows = c.execute("SELECT action,detail,at FROM logs WHERE acct=? "
                         "ORDER BY id DESC LIMIT ?", (aid, n)).fetchall()
    return [dict(r) for r in rows]


def stats():
    with conn() as c:
        acc = c.execute("SELECT COUNT(*) n FROM accounts").fetchone()["n"]
        fl = c.execute("SELECT COUNT(*) n, COALESCE(SUM(size),0) s "
                       "FROM blobs WHERE deleted=0").fetchone()
        kvn = c.execute("SELECT COUNT(*) n FROM kv").fetchone()["n"]
    return {"accounts": acc, "files": fl["n"], "size": fl["s"],
            "size_h": human(fl["s"]), "keys": kvn, "version": VERSION,
            "root": ROOT, "up": _stats["up"], "down": _stats["down"],
            "disk": disk_free()}


def disk_free():
    """Server ki apni disk — kitni bachi hai."""
    try:
        st = os.statvfs(ROOT)
        free = st.f_bavail * st.f_frsize
        tot = st.f_blocks * st.f_frsize
        return {"free": free, "free_h": human(free), "total": tot,
                "total_h": human(tot),
                "pct": round((tot - free) / tot * 100, 1) if tot else 0}
    except Exception:
        return {"free": 0, "free_h": "?", "total": 0, "total_h": "?", "pct": 0}


# ═══════════════════════════════════════════════
#   AUTO-MIRROR — server files apne aap yahan
# ═══════════════════════════════════════════════

_mirror_state = {"last": 0, "files": 0, "bytes": 0, "running": False}

SKIP_DIRS = {"node_modules", "__pycache__", ".git", "venv", ".venv",
             ".cache", "dist", "build"}


def mirror_user_servers(web_uid):
    """Ek user ke saare server folders storage me copy."""
    import engine
    a = by_web_user(web_uid)
    if not a:
        return 0
    root = os.path.join(engine.SERVERS_DIR, str(web_uid))
    if not os.path.isdir(root):
        return 0
    done = 0
    for r, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            p = os.path.join(r, f)
            rel = "servers/" + os.path.relpath(p, root).replace("\\", "/")
            try:
                st = os.stat(p)
            except Exception:
                continue
            old = None
            with conn() as c:
                old = c.execute("SELECT size,updated FROM blobs WHERE acct=? "
                                "AND path=? AND deleted=0",
                                (a["id"], rel)).fetchone()
            if old and old["size"] == st.st_size and old["updated"] >= int(st.st_mtime):
                continue
            ok, _ = put_file(a["id"], rel, p)
            if ok:
                done += 1
    return done


def mirror_all():
    """Sab users ke server files -> storage."""
    import db
    n = 0
    try:
        c = db.conn()
        ids = [r["id"] for r in c.execute("SELECT id FROM users").fetchall()]
        c.close()
    except Exception:
        return 0
    for uid in ids:
        try:
            n += mirror_user_servers(uid)
        except Exception:
            pass
    _mirror_state["last"] = int(time.time())
    _mirror_state["files"] = n
    return n


def restore_user_servers(web_uid):
    """Storage se server files wapas disk par (restart ke baad)."""
    import engine
    a = by_web_user(web_uid)
    if not a:
        return 0
    root = os.path.join(engine.SERVERS_DIR, str(web_uid))
    n = 0
    for f in list_files(a["id"], "servers/"):
        rel = f["path"][len("servers/"):]
        dest = os.path.join(root, rel)
        if os.path.exists(dest) and os.path.getsize(dest) == f["size"]:
            continue
        src, sz, _ = open_file(a["id"], f["path"])
        if not src:
            continue
        try:
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copyfile(src, dest)
            n += 1
        except Exception:
            pass
    return n


def restore_all():
    import db
    n = 0
    try:
        c = db.conn()
        ids = [r["id"] for r in c.execute("SELECT id FROM users").fetchall()]
        c.close()
    except Exception:
        return 0
    for uid in ids:
        try:
            n += restore_user_servers(uid)
        except Exception:
            pass
    return n


def mirror_loop(every=180):
    """Background — har 3 min server files storage me."""
    _mirror_state["running"] = True
    while True:
        try:
            time.sleep(every)
            mirror_all()
        except Exception:
            time.sleep(30)


def mirror_status():
    return dict(_mirror_state)


def boot(quiet=False):
    """App start par: DB banao, purani files wapas lao, mirror chalu."""
    init()
    out = {"restored": 0}
    try:
        out["restored"] = restore_all()
    except Exception:
        pass
    threading.Thread(target=mirror_loop, daemon=True).start()
    if not quiet:
        s = stats()
        dk = s.get("disk", {})
        print(f"  🗄️  Storage : {s['accounts']} accounts • {s['files']} files"
              f" • {s['size_h']} — plan ke hisaab se quota"
              f"  (disk free: {dk.get('free_h','?')})")
        if out["restored"]:
            print(f"  ♻️  Storage se {out['restored']} files wapas aayi")
    return out
