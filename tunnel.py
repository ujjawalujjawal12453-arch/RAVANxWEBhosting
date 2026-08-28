"""
tunnel.py — 🌐 PUBLIC URL (localhost ko internet par lao)
══════════════════════════════════════════════════════════

PROBLEM: EarnLinks localhost accept nahi karta —
         "This domain is not allowed on our system"

SOLUTION: Tunnel se localhost ko asli public URL mil jata hai.
          Phir shortener bhi chal jata hai.

3 tareeke (jo mile wo use hoga):
  1. Cloudflare Tunnel — sabse stable, khud download ho jata hai
  2. localhost.run    — sirf SSH, kuch install nahi
  3. serveo.net       — SSH backup

⚠️ IMANDARI: free tunnel ka URL har restart par badalta hai.
   Permanent chahiye to Render/Railway par deploy karo.
"""

import json
import os
import re
import shutil
import subprocess
import threading
import sys
import time

BASE = os.path.dirname(os.path.abspath(__file__))
BIN = os.path.join(BASE, "bin")
os.makedirs(BIN, exist_ok=True)

URL_FILE = os.path.join(BASE, "data", "tunnel.json")
os.makedirs(os.path.dirname(URL_FILE), exist_ok=True)

_state = {"url": "", "kind": "", "proc": None, "log": [], "ok": False,
          "old": [], "changed_at": 0}
_listeners = []          # URL badle to inhe batao


def on_change(fn):
    """Callback register — URL badalte hi call hoga."""
    if fn not in _listeners:
        _listeners.append(fn)


def _save_url():
    """URL disk par — restart ke baad bhi yaad rahe."""
    try:
        json.dump({"url": _state["url"], "kind": _state["kind"],
                   "old": _state["old"][-25:],
                   "at": int(time.time())},
                  open(URL_FILE, "w"), indent=2)
    except Exception:
        pass


def _load_url():
    """
    Restart ke baad purana URL + history wapas.
    ⚠️ Pehle sirf 'old' load hota tha, 'url' nahi —
       isliye redirect kaam nahi karta tha. Ab dono.
    """
    try:
        d = json.load(open(URL_FILE))
        _state["old"] = list(d.get("old", []))
        u = (d.get("url") or "").rstrip("/")
        if u:
            # purana URL bhi history me — us par aaye to redirect ho
            if u not in _state["old"]:
                _state["old"].append(u)
                _state["old"] = _state["old"][-25:]
            _state["kind"] = d.get("kind", "")
            _state["changed_at"] = d.get("at", 0)
        return u
    except Exception:
        return ""


def _host_of(u):
    """URL se sirf hostname."""
    u = (u or "").strip()
    for p in ("https://", "http://"):
        if u.startswith(p):
            u = u[len(p):]
    return u.strip("/").split("/")[0].split(":")[0].lower()


def old_hosts():
    """
    Purane URL ke host — inse aaye to redirect.
    Disk se bhi padhta hai taaki restart ke baad bhi yaad rahe.
    """
    out = []
    seen = set()

    def add(u):
        h = _host_of(u)
        if h and h not in seen:
            seen.add(h)
            out.append(h)

    for u in _state["old"]:
        add(u)
    # disk par jo bacha ho (restart ke baad)
    try:
        d = json.load(open(URL_FILE))
        for u in d.get("old", []):
            add(u)
    except Exception:
        pass
    # current host list me nahi hona chahiye
    cur = _host_of(_state["url"])
    return [h for h in out if h and h != cur]




# ═══════════════════════════════════════════════════════
#   🌐 DOMAIN — website ke andar se hi set hota hai
#
#   Malik ka hukum: "domain daalne ka option sabse top par,
#   jahan RAVAN X ka logo aata hai wahin".
#
#   Isliye ab admin logo ke saath wale chip pe tap karke
#   seedha domain daal sakta hai. File me save hota hai —
#   restart pe bhi rehta hai.
# ═══════════════════════════════════════════════════════

_DOMFILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "data", "domain.txt")


def saved_domain():
    """File me save kiya hua domain"""
    try:
        return open(_DOMFILE, encoding="utf-8").read().strip()
    except Exception:
        return ""


def locked():
    """
    🔒 Domain PERMANENT ho chuka hai?

    Malik ka hukum: "jab main domain ek baar daal doon to
    wahi wala domain permanent ho jayega, phir aur koi
    domain kaam nahi karega".

    Isliye ek baar set hone ke baad taala lag jaata hai.
    """
    return bool(saved_domain())


def save_domain(v, force=False):
    """
    Domain save karo — SIRF EK BAAR.

    ⚠️ Ek baar set ho gaya to permanent. Dobara badalne ki
       koshish par mana kar dega. Ye jaan-boojh kar hai —
       malik ka hukum. Galti se badalne se poori website ke
       link tut jaate hain.

       Badalna hi ho to server ki `data/domain.txt` file
       haath se delete karni padegi.

    Return: (ok, domain_ya_wajah)
    """
    cur = saved_domain()
    if cur and not force:
        return False, ("LOCKED:" + cur)

    v = (v or "").strip().rstrip("/")
    # user https:// ya slash laga de to bhi chalega
    v = v.replace("https://", "").replace("http://", "").strip("/")
    if not v:
        return False, "khali"
    # theek se domain jaisa lag raha hai?
    if ("." not in v or " " in v or len(v) < 4
            or v.startswith(".") or v.endswith(".")):
        return False, "galat"
    try:
        os.makedirs(os.path.dirname(_DOMFILE), exist_ok=True)
        with open(_DOMFILE, "w", encoding="utf-8") as f:
            f.write(v)
    except Exception:
        return False, "save-fail"
    # turant lagu — restart ka intezaar nahi
    os.environ["DOMAIN"] = v
    return True, v


def domain():
    """
    Apna domain. Mil gaya to tunnel ki zarurat nahi.

    Priority:
      1. env (Render dashboard / .env)
      2. website me set kiya hua (data/domain.txt)
    """
    for k in ("DOMAIN", "PUBLIC_URL", "SITE_URL"):
        v = os.environ.get(k, "").strip()
        if v:
            v = v.rstrip("/")
            return v if v.startswith("http") else f"https://{v}"
    v = saved_domain()
    if v:
        return v if v.startswith("http") else f"https://{v}"
    return ""


def needed():
    """Tunnel chahiye bhi ya nahi?"""
    if domain():
        return False
    if os.environ.get("TUNNEL", "").lower() in ("0", "false", "no", "off"):
        return False
    return True


_stale_hits = {}


def hit_stale(host):
    """Kitne log purane link se aaye — count."""
    _stale_hits[host] = _stale_hits.get(host, 0) + 1
    n = _stale_hits[host]
    if n in (1, 5, 25, 100) or n % 250 == 0:
        log(f"purane link se {n} visit ({host}) -> naye par bheja")


def stale_hits():
    return dict(_stale_hits)


def set_url(new_url, kind=""):
    """
    Naya URL mila — purana history me daalo, sabko batao.
    """
    new_url = (new_url or "").rstrip("/")
    if not new_url or new_url == _state["url"]:
        return False

    prev = _state["url"]
    if prev and prev not in _state["old"]:
        _state["old"].append(prev)
    # naya URL history se nikaal do (warna khud pe redirect loop)
    _state["old"] = [x for x in _state["old"]
                     if _host_of(x) != _host_of(new_url)][-25:]

    _state["url"] = new_url
    _state["kind"] = kind or _state["kind"]
    _state["ok"] = True
    _state["changed_at"] = int(time.time())
    _save_url()

    if prev:
        log(f"URL badla: {prev} -> {new_url}")
        banner_change(prev, new_url)
    else:
        log(f"PUBLIC URL: {new_url}")
        banner_new(new_url)

    # sabko batao (shortener wagera update kar lein)
    for fn in list(_listeners):
        try:
            fn(new_url, prev)
        except Exception as e:
            log(f"listener fail: {str(e)[:50]}")
    return True


# ═══════════════ TERMUX LIVE DISPLAY ═══════════════

_TTY = sys.stdout.isatty() and not os.environ.get("NO_COLOR")
P  = "\033[38;5;141m" if _TTY else ""
P2 = "\033[38;5;99m"  if _TTY else ""
CY = "\033[38;5;51m"  if _TTY else ""
CY2= "\033[38;5;45m"  if _TTY else ""
PK = "\033[38;5;198m" if _TTY else ""
GR = "\033[38;5;83m"  if _TTY else ""
YL = "\033[38;5;221m" if _TTY else ""
WT = "\033[38;5;255m" if _TTY else ""
BD = "\033[1m"        if _TTY else ""
NC = "\033[0m"        if _TTY else ""
DM = "\033[2m"        if _TTY else ""


def _pulse(n=2, delay=.09):
    """Neon pulse animation."""
    if not _TTY:
        return
    cols = [CY, P, PK, P, CY]
    for _ in range(n):
        for c in cols:
            sys.stdout.write(f"\r  {c}{'━' * 56}{NC}")
            sys.stdout.flush()
            time.sleep(delay)
    sys.stdout.write(f"\r  {P}{'━' * 56}{NC}\n")
    sys.stdout.flush()


def banner_new(u):
    """Pehli baar URL mila."""
    print()
    _pulse(1)
    print(f"  {GR}{BD}◆  PUBLIC URL LIVE{NC}")
    print()
    print(f"  {CY}{BD}{u}{NC}")
    print()
    print(f"  {DM}Ye link duniya me kahin se bhi khulega{NC}")
    print(f"  {P}{'━' * 56}{NC}")
    print(f"  {DM}{time.strftime('%d %b %Y, %I:%M:%S %p')}{NC}")
    print(flush=True)


def banner_change(old, new):
    """
    🔄 URL badal gaya — Termux me BADA saaf dikhna chahiye.
    Purane link pe koi aaye to use naye pe bhej diya jayega.
    """
    print()
    _pulse(2)
    print(f"  {YL}{BD}⟳  T U N N E L   U R L   B A D A L   G A Y A{NC}")
    print()
    print(f"  {DM}Purana{NC}")
    print(f"    {DM}{old}{NC}")
    if _TTY:
        time.sleep(.18)
    print()
    print(f"  {PK}{BD}▼{NC}")
    if _TTY:
        time.sleep(.18)
    print()
    print(f"  {GR}Naya{NC}")
    print(f"    {CY}{BD}{new}{NC}")
    print()
    print(f"  {P}{'─' * 56}{NC}")
    print(f"  {GR}✔{NC}  Naya URL save ho gaya")
    print(f"  {GR}✔{NC}  Purane link se aane wale automatic yahan aayenge")
    print(f"  {GR}✔{NC}  Sab pending link dobara ban rahe hain")
    print(f"  {P}{'─' * 56}{NC}")
    print(f"  {DM}{time.strftime('%d %b %Y, %I:%M:%S %p')}"
          f"   ·   total {len(_state['old'])} baar badla{NC}")
    print(flush=True)


def log(m):
    _state["log"].append(f"{time.strftime('%H:%M:%S')}  {m}")
    if len(_state["log"]) > 60:
        _state["log"] = _state["log"][-60:]
    print(f"  {P}◈{NC} {DM}tunnel{NC}  {m}", flush=True)


def url():
    return _state["url"]


def status():
    return {"url": _state["url"], "kind": _state["kind"],
            "ok": _state["ok"], "log": list(_state["log"])[-14:],
            "old": list(_state["old"])[-8:],
            "changed_at": _state["changed_at"],
            "running": is_running()}


def is_running():
    p = _state["proc"]
    return bool(p and p.poll() is None)


# ─────────────────────────────────────────────────────────
#  CLOUDFLARED
# ─────────────────────────────────────────────────────────

def _arch():
    m = (os.uname().machine or "").lower()
    if "aarch64" in m or "arm64" in m:
        return "arm64"
    if "arm" in m:
        return "arm"
    if "x86_64" in m or "amd64" in m:
        return "amd64"
    return "amd64"


def cf_path():
    p = shutil.which("cloudflared")
    if p:
        return p
    p = os.path.join(BIN, "cloudflared")
    return p if os.path.exists(p) else ""


def cf_download():
    """Cloudflared khud download."""
    if cf_path():
        return True, "pehle se hai"
    import urllib.request
    u = ("https://github.com/cloudflare/cloudflared/releases/latest/"
         f"download/cloudflared-linux-{_arch()}")
    dest = os.path.join(BIN, "cloudflared")
    try:
        log(f"cloudflared download ({_arch()})…")
        req = urllib.request.Request(u, headers={"User-Agent": "RavanX"})
        with urllib.request.urlopen(req, timeout=180) as r, \
                open(dest, "wb") as f:
            shutil.copyfileobj(r, f)
        os.chmod(dest, 0o755)
        if os.path.getsize(dest) < 1_000_000:
            os.remove(dest)
            return False, "download adhoora"
        log("cloudflared ready ✅")
        return True, "downloaded"
    except Exception as e:
        return False, str(e)[:80]


URL_RE = re.compile(r"https://[a-z0-9\-]+\.trycloudflare\.com")
LHR_RE = re.compile(r"https://[a-z0-9\-]+\.lhr\.life")
SRV_RE = re.compile(r"https://[a-z0-9\-]+\.serveo\.net")


def _watch(proc, pats, name):
    """Output me se URL pakdo."""
    for line in iter(proc.stdout.readline, ""):
        if not line:
            break
        s = line.strip()
        if s and len(_state["log"]) < 200:
            low = s.lower()
            if any(k in low for k in ("error", "fail", "url", "http", "warn")):
                log(s[:120])
        for pat in pats:
            m = pat.search(s)
            if m:
                set_url(m.group(0), name)
                return


def start_cf(port=8080, wait=40):
    ok, msg = cf_download()
    if not ok:
        log(f"cloudflared nahi mila: {msg}")
        return False
    exe = cf_path()
    log("cloudflare tunnel start…")
    try:
        p = subprocess.Popen(
            [exe, "tunnel", "--no-autoupdate", "--url",
             f"http://localhost:{port}"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1, errors="ignore")
    except Exception as e:
        log(f"start fail: {e}")
        return False
    _state["proc"] = p
    threading.Thread(target=_watch, args=(p, [URL_RE], "cloudflare"),
                     daemon=True).start()
    for _ in range(wait * 2):
        if _state["url"]:
            return True
        if p.poll() is not None:
            log("cloudflared band ho gaya")
            return False
        time.sleep(0.5)
    log("cloudflare timeout")
    return False


def start_ssh(port=8080, host="nokey@localhost.run", wait=30):
    if not shutil.which("ssh"):
        log("ssh nahi hai (pkg install openssh)")
        return False
    log(f"SSH tunnel: {host}")
    try:
        p = subprocess.Popen(
            ["ssh", "-o", "StrictHostKeyChecking=no",
             "-o", "ServerAliveInterval=30", "-o", "ExitOnForwardFailure=yes",
             "-R", f"80:localhost:{port}", host],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL, text=True, bufsize=1, errors="ignore")
    except Exception as e:
        log(f"ssh fail: {e}")
        return False
    _state["proc"] = p
    threading.Thread(target=_watch, args=(p, [LHR_RE, SRV_RE], "ssh"),
                     daemon=True).start()
    for _ in range(wait * 2):
        if _state["url"]:
            return True
        if p.poll() is not None:
            return False
        time.sleep(0.5)
    return False


def start(port=8080):
    """Sab try karo — jo chale wo."""
    if _state["url"] and is_running():
        return _state["url"]

    if not _state["old"]:
        prev = _load_url()
        if prev and prev not in _state["old"]:
            _state["old"].append(prev)

    _state["ok"] = False
    for fn, nm in ((lambda: start_cf(port), "Cloudflare"),
                   (lambda: start_ssh(port, "nokey@localhost.run"), "localhost.run"),
                   (lambda: start_ssh(port, "serveo.net"), "serveo")):
        try:
            if fn():
                return _state["url"]
        except Exception as e:
            log(f"{nm}: {str(e)[:60]}")
        stop()
    log("❌ koi tunnel nahi chala")
    return ""


def stop():
    p = _state["proc"]
    if p and p.poll() is None:
        try:
            p.terminate()
            p.wait(timeout=5)
        except Exception:
            try:
                p.kill()
            except Exception:
                pass
    _state.update(proc=None, url="", ok=False)


def keepalive(port=8080):
    """
    Background — tunnel gir jaye to turant dobara.
    Naya URL mile to set_url() sabko khud bata dega.
    """
    fails = 0
    while True:
        try:
            time.sleep(15)
            if not _state.get("want"):
                continue
            if is_running() and _state["url"]:
                fails = 0
                continue
            fails += 1
            log(f"tunnel down — restart #{fails}")
            stop_proc_only()
            if start(port):
                fails = 0
            else:
                time.sleep(min(fails * 10, 90))
        except Exception:
            time.sleep(20)


def stop_proc_only():
    """Process band karo par URL history rakho."""
    p = _state["proc"]
    if p and p.poll() is None:
        try:
            p.terminate()
            p.wait(timeout=5)
        except Exception:
            try:
                p.kill()
            except Exception:
                pass
    _state["proc"] = None


def enable(port=8080):
    _state["want"] = True
    return start(port)


def disable():
    _state["want"] = False
    stop()
