"""
engine.py — ASLI HOSTING ENGINE
════════════════════════════════

Ye sach me processes chalata hai — dikhawa nahi.

  • File upload  -> disk par save
  • ZIP extract  -> project banega
  • Language detect -> Python / Node / PHP / Go / Ruby / Bash
  • pip/npm install -> ASLI install, live output ke saath
  • Process start -> subprocess.Popen, PID milta hai
  • Live console -> stdout/stderr line by line
  • RAM/CPU      -> /proc se asli numbers

⚠️ Har server ka apna folder: data/servers/<user>/<server>/
"""

import json
import os
import re
import shutil
import signal
import subprocess
import sys
import threading
import time
import zipfile

BASE = os.path.dirname(os.path.abspath(__file__))
SERVERS_DIR = os.path.join(BASE, "data", "servers")
os.makedirs(SERVERS_DIR, exist_ok=True)

# server_id -> {"proc":Popen, "lines":[], "started":ts, "installing":bool}
LIVE = {}
_LOCK = threading.Lock()

MAX_LINES = 400


# ─────────────────────────────────────────────────────────
#  LANGUAGE DETECT
# ─────────────────────────────────────────────────────────

LANGS = {
    ".py":  {"name": "Python", "icon": "🐍", "run": [sys.executable, "-u", "{f}"],
             "install": [sys.executable, "-m", "pip", "install", "-r",
                         "requirements.txt", "--no-input", "-q"],
             "reqfile": "requirements.txt"},
    ".js":  {"name": "Node.js", "icon": "🟢", "run": ["node", "{f}"],
             "install": ["npm", "install", "--no-audit", "--no-fund"],
             "reqfile": "package.json"},
    ".php": {"name": "PHP", "icon": "🐘", "run": ["php", "{f}"],
             "install": None, "reqfile": None},
    ".rb":  {"name": "Ruby", "icon": "💎", "run": ["ruby", "{f}"],
             "install": None, "reqfile": "Gemfile"},
    ".go":  {"name": "Go", "icon": "🐹", "run": ["go", "run", "{f}"],
             "install": None, "reqfile": "go.mod"},
    ".sh":  {"name": "Bash", "icon": "📜", "run": ["bash", "{f}"],
             "install": None, "reqfile": None},
}

ENTRY_NAMES = ["main.py", "bot.py", "app.py", "run.py", "start.py", "index.py",
               "index.js", "main.js", "bot.js", "app.js", "server.js",
               "index.php", "main.go", "main.rb", "start.sh", "run.sh"]


def server_dir(uid, sid):
    p = os.path.join(SERVERS_DIR, str(uid), str(sid))
    os.makedirs(p, exist_ok=True)
    return p


def detect(folder):
    """Project scan — entry file, language, deps."""
    entry, lang, ext = None, None, None

    # 1) jaane-pehchane naam
    for nm in ENTRY_NAMES:
        p = os.path.join(folder, nm)
        if os.path.exists(p):
            entry = nm
            ext = os.path.splitext(nm)[1]
            break

    # 2) nahi mila to koi bhi code file
    if not entry:
        for root, dirs, files in os.walk(folder):
            dirs[:] = [d for d in dirs if d not in
                       ("node_modules", "__pycache__", ".git", "venv")]
            for f in sorted(files):
                e = os.path.splitext(f)[1].lower()
                if e in LANGS:
                    entry = os.path.relpath(os.path.join(root, f), folder)
                    ext = e
                    break
            if entry:
                break

    if ext and ext in LANGS:
        lang = LANGS[ext]

    files_n, size = 0, 0
    for root, dirs, files in os.walk(folder):
        dirs[:] = [d for d in dirs if d not in ("node_modules", "__pycache__")]
        for f in files:
            files_n += 1
            try:
                size += os.path.getsize(os.path.join(root, f))
            except Exception:
                pass

    has_req = bool(lang and lang["reqfile"] and
                   os.path.exists(os.path.join(folder, lang["reqfile"])))

    return {
        "entry": entry,
        "lang": lang["name"] if lang else None,
        "icon": lang["icon"] if lang else "❔",
        "ext": ext,
        "files": files_n,
        "size_mb": round(size / 1048576, 2),
        "has_deps": has_req,
        "reqfile": lang["reqfile"] if lang else None,
    }


def scan_secrets(folder):
    """Token/key expose to nahi hai?"""
    pats = [r"[0-9]{8,10}:AA[\w-]{30,}", r"sk-[A-Za-z0-9]{20,}",
            r"AKIA[0-9A-Z]{16}", r"mongodb(\+srv)?://[^\s\"']+"]
    hits = []
    for root, dirs, files in os.walk(folder):
        dirs[:] = [d for d in dirs if d not in
                   ("node_modules", "__pycache__", ".git")]
        for f in files:
            if os.path.splitext(f)[1].lower() not in \
                    (".py", ".js", ".php", ".rb", ".go", ".sh", ".env", ".json", ".txt"):
                continue
            try:
                txt = open(os.path.join(root, f), encoding="utf-8",
                           errors="ignore").read(60000)
            except Exception:
                continue
            for p in pats:
                if re.search(p, txt):
                    hits.append(f)
                    break
    return hits


# ─────────────────────────────────────────────────────────
#  CONSOLE
# ─────────────────────────────────────────────────────────

def _slot(sid):
    with _LOCK:
        if sid not in LIVE:
            LIVE[sid] = {"proc": None, "lines": [], "started": 0,
                         "installing": False}
        return LIVE[sid]


def log(sid, line, level="out"):
    s = _slot(sid)
    s["lines"].append({"t": time.time(), "l": level, "x": str(line)[:600]})
    if len(s["lines"]) > MAX_LINES:
        s["lines"] = s["lines"][-MAX_LINES:]


def console(sid, since=0):
    """Console ki lines — since ke baad wali."""
    s = _slot(sid)
    return s["lines"][since:]


def clear_console(sid):
    _slot(sid)["lines"] = []


def is_running(sid):
    s = LIVE.get(sid)
    if not s or not s["proc"]:
        return False
    return s["proc"].poll() is None


def is_busy(sid):
    return _slot(sid)["installing"]


# ─────────────────────────────────────────────────────────
#  UPLOAD / EXTRACT
# ─────────────────────────────────────────────────────────

def quota_check(uid, size=0):
    """Plan ke hisaab se jagah bachi hai ya nahi."""
    try:
        import storage
        a = storage.by_web_user(uid)
        if not a:
            return True, None
        q = storage.quota_info(a["id"])
        if size and size > q["left"]:
            return False, q
        if q["full"]:
            return False, q
        return True, q
    except Exception:
        return True, None


def save_upload_stream(uid, sid, filename, reader, total=None):
    """
    File stream hoke seedha disk par — RAM me poori kabhi nahi aati.
    Plan ki limit check hoti hai. Saath hi storage server pe bhi jaati hai.
    """
    ok, q = quota_check(uid, total or 0)
    if not ok and q:
        import theme
        nx = theme.next_plan(q["plan"])
        m = (f"Jagah kam hai — {q['plan'].title()} plan me {q['cap_h']} "
             f"milta hai, {q['left_h']} bacha hai.")
        if nx:
            m += f" {nx.title()} plan lo ya purani files hatao."
        log(sid, f"❌ {m}", "err")
        return False, m

    folder = server_dir(uid, sid)
    fn = re.sub(r"[^A-Za-z0-9._-]", "_", filename)[:120] or "file.txt"
    path = os.path.join(folder, fn)

    n = 0
    try:
        with open(path, "wb") as f:
            while True:
                b = reader.read(524288)
                if not b:
                    break
                f.write(b)
                n += len(b)
            f.flush()
            os.fsync(f.fileno())
    except Exception as e:
        try:
            os.remove(path)
        except Exception:
            pass
        log(sid, f"❌ Upload fail: {e}", "err")
        return False, str(e)[:120]

    if n == 0:
        try:
            os.remove(path)
        except Exception:
            pass
        return False, "File khali hai"

    log(sid, f"📥 Upload: {fn} ({_hsz(n)})", "ok")
    r = _after_upload(uid, sid, fn, path, folder)
    _to_storage(uid, sid)
    return r


def _hsz(b):
    b = float(b)
    for u in ("B", "KB", "MB", "GB"):
        if b < 1024:
            return f"{int(b)} {u}"
        b /= 1024
    return f"{b:.1f} TB"


def save_upload(uid, sid, filename, data):
    """File save karo (bytes se). ZIP ho to extract."""
    folder = server_dir(uid, sid)
    fn = re.sub(r"[^A-Za-z0-9._-]", "_", filename)[:120] or "file.txt"
    path = os.path.join(folder, fn)

    with open(path, "wb") as f:
        f.write(data)
    log(sid, f"📥 Upload: {fn} ({len(data)//1024} KB)", "ok")
    r = _after_upload(uid, sid, fn, path, folder)
    _to_storage(uid, sid)
    return r


def _to_storage(uid, sid=None):
    """🗄️ Server ki files apne storage server par — background me."""
    def w():
        try:
            import storage
            storage.mirror_user_servers(uid)
        except Exception:
            pass
    threading.Thread(target=w, daemon=True).start()


def _after_upload(uid, sid, fn, path, folder):

    if fn.lower().endswith(".zip"):
        log(sid, "📦 ZIP extract ho rahi hai…")
        try:
            with zipfile.ZipFile(path) as z:
                bad = [n for n in z.namelist()
                       if n.startswith("/") or ".." in n]
                if bad:
                    log(sid, "❌ ZIP me galat path hai", "err")
                    os.remove(path)
                    return False, "ZIP surakshit nahi hai"
                # ♾️ ZIP kitni bhi badi ho — chalegi
                z.extractall(folder)
                n = len(z.namelist())
            os.remove(path)
            log(sid, f"✅ {n} files nikal gayi", "ok")

            # agar sab kuch ek hi folder me hai to upar le aao
            items = [i for i in os.listdir(folder) if not i.startswith(".")]
            if len(items) == 1:
                inner = os.path.join(folder, items[0])
                if os.path.isdir(inner):
                    for it in os.listdir(inner):
                        shutil.move(os.path.join(inner, it),
                                    os.path.join(folder, it))
                    shutil.rmtree(inner, ignore_errors=True)
                    log(sid, f"📂 '{items[0]}' folder khol diya")
        except zipfile.BadZipFile:
            os.remove(path)
            log(sid, "❌ ZIP kharab hai", "err")
            return False, "ZIP file kharab hai"

    info = detect(folder)
    if info["entry"]:
        log(sid, f"🔍 Mila: {info['icon']} {info['lang']} — {info['entry']}", "ok")
        if info["has_deps"]:
            log(sid, f"📋 {info['reqfile']} mila — install kar sakte ho")
    else:
        log(sid, "⚠️ Main file nahi mili (main.py / index.js…)", "warn")

    sec = scan_secrets(folder)
    if sec:
        log(sid, f"🔐 Dhyan do: {len(sec)} file me token dikha", "warn")

    return True, info


def list_files(uid, sid, sub=""):
    folder = server_dir(uid, sid)
    target = os.path.normpath(os.path.join(folder, sub))
    if not target.startswith(folder):
        return []
    if not os.path.isdir(target):
        return []
    out = []
    for n in sorted(os.listdir(target)):
        p = os.path.join(target, n)
        isd = os.path.isdir(p)
        try:
            sz = 0 if isd else os.path.getsize(p)
        except Exception:
            sz = 0
        out.append({"name": n, "dir": isd, "size": sz,
                    "path": os.path.relpath(p, folder)})
    return sorted(out, key=lambda x: (not x["dir"], x["name"].lower()))


def delete_path(uid, sid, rel):
    folder = server_dir(uid, sid)
    p = os.path.normpath(os.path.join(folder, rel))
    if not p.startswith(folder) or p == folder:
        return False
    try:
        shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
        log(sid, f"🗑 Delete: {rel}", "warn")
        return True
    except Exception:
        return False


def read_file(uid, sid, rel, limit=100000):
    folder = server_dir(uid, sid)
    p = os.path.normpath(os.path.join(folder, rel))
    if not p.startswith(folder) or not os.path.isfile(p):
        return None
    try:
        return open(p, encoding="utf-8", errors="ignore").read(limit)
    except Exception:
        return None


def write_file(uid, sid, rel, content):
    folder = server_dir(uid, sid)
    p = os.path.normpath(os.path.join(folder, rel))
    if not p.startswith(folder):
        return False
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w", encoding="utf-8").write(content)
        log(sid, f"✏️ Saved: {rel}", "ok")
        return True
    except Exception:
        return False


def disk_mb(uid, sid):
    folder = server_dir(uid, sid)
    total = 0
    for root, dirs, files in os.walk(folder):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except Exception:
                pass
    return round(total / 1048576, 2)


# ─────────────────────────────────────────────────────────
#  INSTALL  (asli pip / npm)
# ─────────────────────────────────────────────────────────

def install_deps(uid, sid, on_done=None):
    """Background me deps install — live output console me."""
    folder = server_dir(uid, sid)
    info = detect(folder)
    s = _slot(sid)

    if not info["ext"] or info["ext"] not in LANGS:
        log(sid, "❌ Language pata nahi chali", "err")
        return False
    cfg = LANGS[info["ext"]]
    if not cfg["install"]:
        log(sid, f"ℹ️ {info['lang']} me install ki zarurat nahi", "ok")
        return True
    if cfg["reqfile"] and not os.path.exists(os.path.join(folder, cfg["reqfile"])):
        log(sid, f"ℹ️ {cfg['reqfile']} nahi hai — skip", "warn")
        return True
    if s["installing"]:
        log(sid, "⚠️ Install pehle se chal raha hai", "warn")
        return False

    def worker():
        s["installing"] = True
        log(sid, "━" * 40)
        log(sid, f"📦 Dependencies install ho rahi hain ({cfg['reqfile']})…")
        t0 = time.time()
        try:
            p = subprocess.Popen(cfg["install"], cwd=folder,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,
                                 text=True, bufsize=1,
                                 errors="ignore")
            for line in p.stdout:
                ln = line.rstrip()
                if ln:
                    low = ln.lower()
                    lv = "err" if ("error" in low or "failed" in low) else (
                        "warn" if "warn" in low else "out")
                    log(sid, ln, lv)
            p.wait(timeout=900)
            took = time.time() - t0
            if p.returncode == 0:
                log(sid, f"✅ Install ho gaya ({took:.0f}s)", "ok")
            else:
                log(sid, f"❌ Install fail (exit {p.returncode})", "err")
        except FileNotFoundError:
            log(sid, f"❌ '{cfg['install'][0]}' install nahi hai server par", "err")
        except subprocess.TimeoutExpired:
            log(sid, "❌ Install me 15 min se zyada lag gaya", "err")
        except Exception as e:
            log(sid, f"❌ {e}", "err")
        finally:
            s["installing"] = False
            log(sid, "━" * 40)
            if on_done:
                try:
                    on_done()
                except Exception:
                    pass

    threading.Thread(target=worker, daemon=True).start()
    return True


# ─────────────────────────────────────────────────────────
#  START / STOP  (asli process)
# ─────────────────────────────────────────────────────────

def start(uid, sid, env=None):
    folder = server_dir(uid, sid)
    s = _slot(sid)

    if is_running(sid):
        log(sid, "⚠️ Pehle se chal raha hai", "warn")
        return False, "Already running"
    if s["installing"]:
        return False, "Install chal raha hai, ruko"

    info = detect(folder)
    if not info["entry"]:
        log(sid, "❌ Main file nahi mili — pehle file upload karo", "err")
        return False, "Main file nahi mili"
    if not info["ext"] or info["ext"] not in LANGS:
        log(sid, f"❌ '{info['ext']}' support nahi hai", "err")
        return False, "Language support nahi"

    cfg = LANGS[info["ext"]]
    cmd = [c.replace("{f}", info["entry"]) for c in cfg["run"]]

    e = dict(os.environ)
    e["PYTHONUNBUFFERED"] = "1"
    e["NODE_NO_WARNINGS"] = "1"
    if env:
        e.update({str(k): str(v) for k, v in env.items()})

    log(sid, "━" * 40)
    log(sid, f"🚀 Start: {info['icon']} {' '.join(cmd)}", "ok")
    try:
        p = subprocess.Popen(cmd, cwd=folder, env=e,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             text=True, bufsize=1, errors="ignore",
                             start_new_session=True)
    except FileNotFoundError:
        log(sid, f"❌ '{cmd[0]}' server par install nahi hai", "err")
        return False, f"{cmd[0]} nahi mila"
    except Exception as ex:
        log(sid, f"❌ Start fail: {ex}", "err")
        return False, str(ex)

    s["proc"] = p
    s["started"] = time.time()
    log(sid, f"✅ Chal raha hai — PID {p.pid}", "ok")

    def reader():
        try:
            for line in p.stdout:
                ln = line.rstrip()
                if ln:
                    low = ln.lower()
                    lv = "err" if ("error" in low or "traceback" in low
                                   or "exception" in low) else (
                        "warn" if "warn" in low else "out")
                    log(sid, ln, lv)
        except Exception:
            pass
        code = p.poll()
        if code is not None:
            log(sid, "━" * 40)
            log(sid, f"⏹ Process band ho gaya (exit {code})",
                "err" if code else "warn")

    threading.Thread(target=reader, daemon=True).start()
    return True, p.pid


def stop(sid):
    s = LIVE.get(sid)
    if not s or not s["proc"] or s["proc"].poll() is not None:
        return False
    p = s["proc"]
    log(sid, "⏹ Stop kar raha hoon…", "warn")
    try:
        os.killpg(os.getpgid(p.pid), signal.SIGTERM)
    except Exception:
        try:
            p.terminate()
        except Exception:
            pass
    try:
        p.wait(timeout=8)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        except Exception:
            p.kill()
    log(sid, "✅ Band ho gaya", "ok")
    s["proc"] = None
    s["started"] = 0
    return True


def restart(uid, sid, env=None):
    stop(sid)
    time.sleep(0.6)
    return start(uid, sid, env)


def usage(sid):
    """Asli RAM/CPU /proc se."""
    s = LIVE.get(sid)
    if not s or not s["proc"] or s["proc"].poll() is not None:
        return {"ram": 0.0, "cpu": 0.0, "pid": None, "uptime": 0}
    pid = s["proc"].pid
    ram = 0.0
    try:
        with open(f"/proc/{pid}/status") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    ram = round(int(line.split()[1]) / 1024, 1)
                    break
    except Exception:
        pass
    cpu = 0.0
    try:
        with open(f"/proc/{pid}/stat") as f:
            parts = f.read().split()
        ticks = int(parts[13]) + int(parts[14])
        up = max(1, time.time() - s["started"])
        cpu = round(ticks / os.sysconf("SC_CLK_TCK") / up * 100, 1)
    except Exception:
        pass
    return {"ram": ram, "cpu": min(cpu, 100.0), "pid": pid,
            "uptime": int(time.time() - s["started"])}


def run_cmd(uid, sid, cmd, timeout=60):
    """Console se command — surakshit tareeke se."""
    folder = server_dir(uid, sid)
    banned = ["rm -rf /", "mkfs", "dd if=", ":(){", "shutdown", "reboot",
              "> /dev/sda", "chmod -R 777 /"]
    low = cmd.lower()
    if any(b in low for b in banned):
        log(sid, f"🚫 Ye command allowed nahi: {cmd[:50]}", "err")
        return
    log(sid, f"$ {cmd}", "cmd")
    try:
        r = subprocess.run(cmd, shell=True, cwd=folder, capture_output=True,
                           text=True, timeout=timeout, errors="ignore")
        out = (r.stdout or "") + (r.stderr or "")
        for line in out.splitlines()[-120:]:
            if line.strip():
                log(sid, line)
        if not out.strip():
            log(sid, f"(koi output nahi, exit {r.returncode})", "warn")
    except subprocess.TimeoutExpired:
        log(sid, f"⏱ {timeout}s me pura nahi hua", "err")
    except Exception as e:
        log(sid, f"❌ {e}", "err")


def destroy(uid, sid):
    stop(sid)
    with _LOCK:
        LIVE.pop(sid, None)
    shutil.rmtree(server_dir(uid, sid), ignore_errors=True)
    return True
