"""
db.py — RAVAN X CLOUD ka database
══════════════════════════════════

Bilkul ALAG database (bot se koi connection nahi).
SQLite — koi install nahi, file hi database hai.
"""

import hashlib
import os
import secrets
import sqlite3
import time

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE, "data")
DB_PATH = os.path.join(DATA_DIR, "cloud.db")

os.makedirs(DATA_DIR, exist_ok=True)


def _migrate(c):
    """Purane DB me naye column jodo."""
    try:
        cols = [r[1] for r in c.execute("PRAGMA table_info(payments)")]
        if cols and "shot" not in cols:
            c.execute("ALTER TABLE payments ADD COLUMN shot TEXT DEFAULT ''")
            c.commit()
        # FamGateway: remember provider order/metadata on existing DBs.
        cols = [r[1] for r in c.execute("PRAGMA table_info(payments)")]
        for name, spec in (("provider", "TEXT DEFAULT ''"),
                           ("gateway_order", "TEXT DEFAULT ''"),
                           ("sender_name", "TEXT DEFAULT ''"),
                           ("qr_url", "TEXT DEFAULT ''"),
                           ("checkout_url", "TEXT DEFAULT ''")):
            if cols and name not in cols:
                c.execute(f"ALTER TABLE payments ADD COLUMN {name} {spec}")
        c.commit()
    except Exception:
        pass
    # 📧 Email verify ka nishaan
    #
    # ⚠️ `verified` column pehle se maujood tha par sab 0 pe pada
    #    tha (kabhi use hi nahi hua). Ab OTP chalu ho raha hai —
    #    par PURANE users ko dobara verify karne ko bolna galat
    #    hoga, unka account to pehle se chal raha hai. Isliye
    #    ek baar sabko verified kar dete hain. Naye users OTP
    #    se hi guzrenge.
    try:
        cols = [r[1] for r in c.execute("PRAGMA table_info(users)")]
        if cols and "verified" not in cols:
            c.execute("ALTER TABLE users ADD COLUMN "
                      "verified INTEGER DEFAULT 0")
        # ═══ 🔄 VERIFICATION RESET ═══
        #
        # Malik ka hukum:
        #   "ab sabke liye verification completely kar do.
        #    jitne verification pehle hue the un sab ko hata
        #    kar ab naya verification hoga. Admin ko chhod kar
        #    baaki sab verification se hi aayenge."
        #
        # Isliye ek baar SABKA verified=0 kar dete hain (admin
        # chhod kar). Login karte hi unhe email pe code aayega.
        #
        # ⚠️ Nishaan file isliye taaki ye har restart pe na
        #    chale — warna log baar-baar verify karte rahenge.
        import os as _os
        _mark = _os.path.join(_os.path.dirname(DB_PATH),
                              ".verify-reset-v2")
        if not _os.path.exists(_mark):
            c.execute("UPDATE users SET verified=0 "
                      "WHERE role != 'admin'")
            c.execute("UPDATE users SET verified=1 "
                      "WHERE role = 'admin'")
            c.commit()
            try:
                open(_mark, "w").write("1")
            except Exception:
                pass
            # purana nishaan hata do
            try:
                _old = _os.path.join(_os.path.dirname(DB_PATH),
                                     ".verified-migrated")
                if _os.path.exists(_old):
                    _os.remove(_old)
            except Exception:
                pass
    except Exception:
        pass
    # ⏳ Free server 24 ghante me apne aap expire — uske liye
    #    do naye column. Purane DB me bhi jud jayenge.
    try:
        cols = [r[1] for r in c.execute("PRAGMA table_info(apps)")]
        if cols:
            if "expires_at" not in cols:
                c.execute("ALTER TABLE apps ADD COLUMN "
                          "expires_at INTEGER DEFAULT 0")
            if "is_free" not in cols:
                c.execute("ALTER TABLE apps ADD COLUMN "
                          "is_free INTEGER DEFAULT 0")
            c.commit()
    except Exception:
        pass


# ═══════════════════════════════════════════════
#   ⏳ FREE SERVER — 24 ghante ka hisaab
# ═══════════════════════════════════════════════

def set_expiry(app_id, hours, free=True):
    """Server pe expiry ki mohar lagao"""
    c = conn()
    c.execute("UPDATE apps SET expires_at=?, is_free=? WHERE id=?",
              (int(time.time() + hours * 3600), 1 if free else 0,
               app_id))
    c.commit()
    c.close()


def expired_apps():
    """Jinka waqt poora ho gaya — abhi tak zinda hain"""
    c = conn()
    r = c.execute(
        "SELECT * FROM apps WHERE is_free=1 AND expires_at>0 "
        "AND expires_at<=?", (int(time.time()),)).fetchall()
    c.close()
    return [dict(x) for x in r]


def expiry_left(app):
    """Kitna waqt bacha — second me. 0 = expire ya free nahi"""
    try:
        e = int(app.get("expires_at") or 0)
    except Exception:
        return 0
    if not e:
        return 0
    return max(0, e - int(time.time()))


def conn():
    c = sqlite3.connect(DB_PATH, timeout=20)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")
    return c


def init():
    c = conn()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        email         TEXT UNIQUE NOT NULL,
        name          TEXT NOT NULL,
        phone         TEXT DEFAULT '',
        pass_hash     TEXT NOT NULL,
        salt          TEXT NOT NULL,
        credits       INTEGER DEFAULT 0,
        plan          TEXT DEFAULT 'free',
        role          TEXT DEFAULT 'user',
        verified      INTEGER DEFAULT 0,
        banned        INTEGER DEFAULT 0,
        created_at    INTEGER,
        last_login    INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS sessions (
        token      TEXT PRIMARY KEY,
        user_id    INTEGER NOT NULL,
        created_at INTEGER,
        expires_at INTEGER,
        ip         TEXT DEFAULT ''
    );

    CREATE TABLE IF NOT EXISTS apps (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id     INTEGER NOT NULL,
        name        TEXT NOT NULL,
        lang        TEXT DEFAULT 'Python',
        plan        TEXT DEFAULT 'starter',
        status      TEXT DEFAULT 'stopped',
        ram_mb      INTEGER DEFAULT 0,
        cpu_pct     REAL DEFAULT 0,
        disk_mb     REAL DEFAULT 0,
        domain      TEXT DEFAULT '',
        repo        TEXT DEFAULT '',
        created_at  INTEGER,
        started_at  INTEGER DEFAULT 0,
        restarts    INTEGER DEFAULT 0,
        expires_at  INTEGER DEFAULT 0,
        is_free     INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS logs (
        id      INTEGER PRIMARY KEY AUTOINCREMENT,
        app_id  INTEGER NOT NULL,
        ts      INTEGER,
        level   TEXT DEFAULT 'info',
        line    TEXT
    );

    CREATE TABLE IF NOT EXISTS txns (
        id      INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        amount  INTEGER,
        note    TEXT,
        ts      INTEGER
    );

    CREATE TABLE IF NOT EXISTS payments (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id  INTEGER NOT NULL,
        ref      TEXT UNIQUE,
        rupees   REAL,
        credits  INTEGER,
        utr      TEXT DEFAULT '',
        shot     TEXT DEFAULT '',
        status   TEXT DEFAULT 'pending',
        ts       INTEGER,
        done_at  INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS app_settings (
        key        TEXT PRIMARY KEY,
        value      TEXT NOT NULL DEFAULT '',
        updated_at INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS tickets (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id  INTEGER NOT NULL,
        subject  TEXT,
        message  TEXT,
        reply    TEXT DEFAULT '',
        status   TEXT DEFAULT 'open',
        ts       INTEGER
    );

    CREATE INDEX IF NOT EXISTS ix_apps_user ON apps(user_id);
    CREATE INDEX IF NOT EXISTS ix_logs_app  ON logs(app_id);
    CREATE INDEX IF NOT EXISTS ix_sess_user ON sessions(user_id);
    """)
    c.commit()
    _migrate(c)
    c.close()


# ───────── PASSWORD ─────────

def hash_pw(password, salt=None):
    salt = salt or secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120_000)
    return h.hex(), salt


def check_pw(password, stored_hash, salt):
    h, _ = hash_pw(password, salt)
    return secrets.compare_digest(h, stored_hash)


# ───────── USERS ─────────

def create_user(email, name, password, phone=""):
    email = email.strip().lower()
    h, salt = hash_pw(password)
    c = conn()
    try:
        # 💡 Koi signup bonus NAHI — seedha ek free starter server milega
        cur = c.execute(
            "INSERT INTO users (email,name,phone,pass_hash,salt,credits,created_at)"
            " VALUES (?,?,?,?,?,?,?)",
            (email, name.strip(), phone.strip(), h, salt, 0, int(time.time())))
        uid = cur.lastrowid
        c.commit()
        return uid, None
    except sqlite3.IntegrityError:
        return None, "Ye email pehle se registered hai"
    finally:
        c.close()


def user_count():
    c = conn()
    n = c.execute("SELECT COUNT(*) n FROM users").fetchone()["n"]
    c.close()
    return n


def get_user(uid):
    c = conn()
    r = c.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    c.close()
    return dict(r) if r else None


def get_by_email(email):
    c = conn()
    r = c.execute("SELECT * FROM users WHERE email=?",
                  (email.strip().lower(),)).fetchone()
    c.close()
    return dict(r) if r else None


def update_user(uid, **kw):
    if not kw:
        return
    sets = ", ".join(f"{k}=?" for k in kw)
    c = conn()
    c.execute(f"UPDATE users SET {sets} WHERE id=?", (*kw.values(), uid))
    c.commit()
    c.close()


def kill_sessions(uid):
    """
    Is user ke saare session kaat do — turant bahar.

    ⚠️ Ban karte waqt zaroori hai. Warna user ka cookie
       chalta rehta hai aur wo 30 din tak andar ghusa
       rehta hai — ban bekaar ho jata hai.
    """
    c = conn()
    c.execute("DELETE FROM sessions WHERE user_id=?", (uid,))
    c.commit()
    c.close()


def all_users(limit=200):
    c = conn()
    rows = c.execute("SELECT * FROM users ORDER BY id DESC LIMIT ?",
                     (limit,)).fetchall()
    c.close()
    return [dict(r) for r in rows]


# ───────── SESSIONS ─────────

def new_session(uid, ip="", days=30):
    tok = secrets.token_urlsafe(32)
    now = int(time.time())
    c = conn()
    c.execute("INSERT INTO sessions (token,user_id,created_at,expires_at,ip)"
              " VALUES (?,?,?,?,?)", (tok, uid, now, now + days * 86400, ip))
    c.execute("UPDATE users SET last_login=? WHERE id=?", (now, uid))
    c.commit()
    c.close()
    return tok


def session_user(token):
    if not token:
        return None
    c = conn()
    r = c.execute(
        "SELECT u.* FROM sessions s JOIN users u ON u.id=s.user_id"
        " WHERE s.token=? AND s.expires_at>?",
        (token, int(time.time()))).fetchone()
    c.close()
    return dict(r) if r else None


def kill_session(token):
    c = conn()
    c.execute("DELETE FROM sessions WHERE token=?", (token,))
    c.commit()
    c.close()


# ───────── APPS ─────────

def create_app(uid, name, lang="Python", plan="starter", repo=""):
    c = conn()
    cur = c.execute(
        "INSERT INTO apps (user_id,name,lang,plan,repo,created_at)"
        " VALUES (?,?,?,?,?,?)",
        (uid, name, lang, plan, repo, int(time.time())))
    aid = cur.lastrowid
    c.execute("INSERT INTO logs (app_id,ts,level,line) VALUES (?,?,?,?)",
              (aid, int(time.time()), "info", f"App '{name}' created"))
    c.commit()
    c.close()
    return aid


def user_apps(uid):
    c = conn()
    rows = c.execute("SELECT * FROM apps WHERE user_id=? ORDER BY id DESC",
                     (uid,)).fetchall()
    c.close()
    return [dict(r) for r in rows]


def get_app(aid, uid=None):
    c = conn()
    if uid is None:
        r = c.execute("SELECT * FROM apps WHERE id=?", (aid,)).fetchone()
    else:
        r = c.execute("SELECT * FROM apps WHERE id=? AND user_id=?",
                      (aid, uid)).fetchone()
    c.close()
    return dict(r) if r else None


def update_app(aid, **kw):
    if not kw:
        return
    sets = ", ".join(f"{k}=?" for k in kw)
    c = conn()
    c.execute(f"UPDATE apps SET {sets} WHERE id=?", (*kw.values(), aid))
    c.commit()
    c.close()


def delete_app(aid):
    c = conn()
    c.execute("DELETE FROM logs WHERE app_id=?", (aid,))
    c.execute("DELETE FROM apps WHERE id=?", (aid,))
    c.commit()
    c.close()


def add_log(aid, line, level="info"):
    c = conn()
    c.execute("INSERT INTO logs (app_id,ts,level,line) VALUES (?,?,?,?)",
              (aid, int(time.time()), level, line[:500]))
    c.execute("DELETE FROM logs WHERE app_id=? AND id NOT IN"
              " (SELECT id FROM logs WHERE app_id=? ORDER BY id DESC LIMIT 200)",
              (aid, aid))
    c.commit()
    c.close()


def app_logs(aid, limit=60):
    c = conn()
    rows = c.execute("SELECT * FROM logs WHERE app_id=? ORDER BY id DESC LIMIT ?",
                     (aid, limit)).fetchall()
    c.close()
    return [dict(r) for r in reversed(rows)]


# ───────── MONEY ─────────

def add_credits(uid, amount, note=""):
    c = conn()
    c.execute("UPDATE users SET credits=credits+? WHERE id=?", (amount, uid))
    c.execute("INSERT INTO txns (user_id,amount,note,ts) VALUES (?,?,?,?)",
              (uid, amount, note, int(time.time())))
    r = c.execute("SELECT credits FROM users WHERE id=?", (uid,)).fetchone()
    c.commit()
    c.close()
    return r["credits"] if r else 0


def user_txns(uid, limit=30):
    c = conn()
    rows = c.execute("SELECT * FROM txns WHERE user_id=? ORDER BY id DESC LIMIT ?",
                     (uid, limit)).fetchall()
    c.close()
    return [dict(r) for r in rows]


def create_payment(uid, ref, rupees, credits):
    c = conn()
    c.execute("INSERT INTO payments (user_id,ref,rupees,credits,ts)"
              " VALUES (?,?,?,?,?)", (uid, ref, rupees, credits, int(time.time())))
    c.commit()
    c.close()


def get_setting(key, default=""):
    c = conn()
    try:
        r = c.execute("SELECT value FROM app_settings WHERE key=?", (str(key),)).fetchone()
        return r["value"] if r else default
    finally:
        c.close()


def set_setting(key, value):
    c = conn()
    try:
        c.execute("INSERT INTO app_settings(key,value,updated_at) VALUES(?,?,?) "
                  "ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=excluded.updated_at",
                  (str(key), str(value), int(time.time())))
        c.commit()
    finally:
        c.close()


def set_payment(ref, **kw):
    if not kw:
        return
    sets = ", ".join(f"{k}=?" for k in kw)
    c = conn()
    c.execute(f"UPDATE payments SET {sets} WHERE ref=?", (*kw.values(), ref))
    c.commit()
    c.close()


def get_payment(ref):
    c = conn()
    r = c.execute("SELECT * FROM payments WHERE ref=?", (ref,)).fetchone()
    c.close()
    return dict(r) if r else None


def complete_gateway_payment(ref, utr, sender_name=""):
    """Atomic idempotent website credit fulfillment for a verified gateway order."""
    c = conn()
    try:
        c.execute("BEGIN IMMEDIATE")
        p = c.execute("SELECT * FROM payments WHERE ref=?", (ref,)).fetchone()
        if not p:
            c.rollback(); return False, "order_missing", 0
        p = dict(p)
        if p.get("status") == "approved":
            row = c.execute("SELECT credits FROM users WHERE id=?", (p["user_id"],)).fetchone()
            c.commit(); return True, "already_paid", int(row["credits"] if row else 0)
        if p.get("status") != "pending" or p.get("provider") != "famgateway":
            c.rollback(); return False, "wrong_state", 0
        dup = c.execute("SELECT ref FROM payments WHERE utr=? AND status='approved' AND ref<>?", (utr, ref)).fetchone()
        if dup:
            c.rollback(); return False, "duplicate_utr", 0
        updated = c.execute("UPDATE payments SET status='approved',utr=?,sender_name=?,done_at=? WHERE ref=? AND status='pending'",
                            (str(utr), str(sender_name)[:120], int(time.time()), ref)).rowcount
        if updated != 1:
            c.rollback(); return False, "race", 0
        c.execute("UPDATE users SET credits=credits+? WHERE id=?", (int(p["credits"]), int(p["user_id"])))
        c.execute("INSERT INTO txns (user_id,amount,note,ts) VALUES (?,?,?,?)",
                  (int(p["user_id"]), int(p["credits"]), f"FamGateway {ref}", int(time.time())))
        row = c.execute("SELECT credits FROM users WHERE id=?", (int(p["user_id"]),)).fetchone()
        c.commit()
        return True, "credited", int(row["credits"] if row else 0)
    except Exception:
        c.rollback()
        raise
    finally:
        c.close()


def utr_exists(utr):
    if not utr:
        return None
    c = conn()
    r = c.execute("SELECT ref,user_id FROM payments WHERE utr=?"
                  " AND status IN ('pending','approved')", (utr,)).fetchone()
    c.close()
    return dict(r) if r else None


def user_payments(uid, limit=20):
    c = conn()
    rows = c.execute("SELECT * FROM payments WHERE user_id=?"
                     " ORDER BY id DESC LIMIT ?", (uid, limit)).fetchall()
    c.close()
    return [dict(r) for r in rows]


def pending_payments():
    c = conn()
    rows = c.execute(
        "SELECT p.*, u.email, u.name FROM payments p JOIN users u ON u.id=p.user_id"
        " WHERE p.status='pending' ORDER BY p.id DESC").fetchall()
    c.close()
    return [dict(r) for r in rows]


# ───────── TICKETS ─────────

def create_ticket(uid, subject, message):
    c = conn()
    c.execute("INSERT INTO tickets (user_id,subject,message,ts) VALUES (?,?,?,?)",
              (uid, subject[:120], message[:2000], int(time.time())))
    c.commit()
    c.close()


def user_tickets(uid):
    c = conn()
    rows = c.execute("SELECT * FROM tickets WHERE user_id=? ORDER BY id DESC",
                     (uid,)).fetchall()
    c.close()
    return [dict(r) for r in rows]


def all_tickets():
    c = conn()
    rows = c.execute(
        "SELECT t.*, u.email, u.name FROM tickets t JOIN users u ON u.id=t.user_id"
        " ORDER BY t.id DESC LIMIT 100").fetchall()
    c.close()
    return [dict(r) for r in rows]


# ───────── STATS ─────────

def stats():
    c = conn()
    g = lambda q: c.execute(q).fetchone()[0]
    s = {
        "users": g("SELECT COUNT(*) FROM users"),
        "apps": g("SELECT COUNT(*) FROM apps"),
        "running": g("SELECT COUNT(*) FROM apps WHERE status='running'"),
        "credits": g("SELECT COALESCE(SUM(credits),0) FROM users"),
        "revenue": g("SELECT COALESCE(SUM(rupees),0) FROM payments"
                     " WHERE status='approved'"),
        "pending": g("SELECT COUNT(*) FROM payments WHERE status='pending'"),
        "tickets": g("SELECT COUNT(*) FROM tickets WHERE status='open'"),
    }
    c.close()
    return s


init()
