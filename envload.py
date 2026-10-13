"""
envload.py — 🔑 .env FILE PADHNE WALA
══════════════════════════════════════

Malik ka hukum: "sirf ek env banao, usme main Render ka domain
daalunga — baaki sab andar hi rehna chahiye".

Isliye:
  • Saari API keys CODE KE ANDAR bhari hain (BUILTIN_*)
  • .env me sirf 2-4 line — jo aapko badalni pad sakti hain
  • .env na ho to bhi sab chalta hai (default se)

⚠️ ZAROORI: ye sabse PEHLE chalna chahiye — kisi bhi module ke
   import se pehle. Kyunki module import hote hi os.environ
   padh lete hain. Isliye app.py ki pehli line me hai.

Dhoondhta hai (jo pehle mile):
  1. RAVANX_ENV se bataya hua path
  2. website folder me .env
  3. uske upar wale folder me .env
  4. jahan se chalaya hai wahan .env
"""

import os

BASE = os.path.dirname(os.path.abspath(__file__))
_loaded = []


def _parse(path):
    """
    .env padho. Aasan format:
        KEY=value
        KEY = "value"     <- quote bhi chalega
        # comment
    """
    out = {}
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                if line.lower().startswith("export "):
                    line = line[7:].strip()
                if "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip()
                # quote hata do
                if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
                    v = v[1:-1]
                # line ke aakhir me comment
                elif " #" in v:
                    v = v.split(" #")[0].strip()
                if k:
                    out[k] = v
    except Exception:
        pass
    return out


def load(verbose=True):
    """
    .env dhoondho aur environment me daalo.

    ⚠️ Jo cheez PEHLE SE environment me hai (Render ke dashboard
       se aayi) usko OVERWRITE nahi karte — Render ki setting
       hamesha upar rahegi.
    """
    global _loaded
    paths = []
    custom = os.environ.get("RAVANX_ENV", "").strip()
    if custom:
        paths.append(custom)
    paths += [
        os.path.join(BASE, ".env"),
        os.path.join(os.path.dirname(BASE), ".env"),
        os.path.join(os.getcwd(), ".env"),
    ]

    seen = set()
    n = 0
    for p in paths:
        p = os.path.abspath(p)
        if p in seen or not os.path.isfile(p):
            continue
        seen.add(p)
        d = _parse(p)
        got = 0
        for k, v in d.items():
            # Render/Railway ka env hamesha jeetega
            if os.environ.get(k, "").strip():
                continue
            os.environ[k] = v
            got += 1
        if got:
            _loaded.append((p, got))
            n += got
        if verbose and d:
            print(f"  🔑 .env padha: {p}  ({got} setting)")

    if verbose and not _loaded:
        print("  ℹ️  .env nahi mila — built-in setting se chalega")
    return n


def loaded():
    return list(_loaded)


# ─────────────────────────────────────────────────────────
#  Naya .env bana do — pehli baar chalane par
# ─────────────────────────────────────────────────────────

TEMPLATE = """# ╔═════════════════════════════════════════════════════╗
# ║                                                     ║
# ║   🌐  A P N A   D O M A I N   Y A H A N   👇        ║
# ║                                                     ║
# ╚═════════════════════════════════════════════════════╝
#
#  Render pe deploy karne ke baad wahan se jo link milta
#  hai, wo neeche paste karo. Bas itna hi.
#
#     DOMAIN=ravanx-hosting.onrender.com
#
#  Apna khud ka domain ho to wo bhi:
#     DOMAIN=ravanxhosting.com
#
#  ⚠️ https:// mat likhna, sirf naam.
#  Khali chhoda to temporary link banega (har restart pe
#  badalta hai).

DOMAIN=

# ═════════════════════════════════════════════════════
#  ⬆️ BAS YAHI EK LINE. Neeche ka sab optional hai —
#     haath na lagao to bhi sab chalta hai.
# ═════════════════════════════════════════════════════


# ── 🔐 ADMIN PASSWORD ───────────────────────────────────
#  /admin panel kholne ke liye

ADMIN_PASS=ravanx2026


# ── 🛠 MAINTENANCE MODE ─────────────────────────────────
#
#  Website galti se maintenance me phas jaye to yahan
#  "off" likh kar restart kar do — turant wapas aa jayegi.
#
#     MAINTENANCE=off    <- hamesha LIVE (panel ignore)
#     MAINTENANCE=on     <- hamesha band
#     MAINTENANCE=       <- panel wala switch chalega
#
#  Ya bina restart ke, browser me ye kholo:
#     /maintenance-off?pass=ravanx2026

MAINTENANCE=


# ── 📧 EMAIL (signup + login ka OTP) ────────────────────
#  Khali chhoda to code screen pe dikh jayega — login
#  phir bhi chalega.
#
#  Free key 2 minute me:  brevo.com -> Sign up ->
#  SMTP & API -> API Keys -> Generate  (300 email/din)

BREVO_API_KEY=
MAIL_FROM=ontopujjala@gmail.com


# ── 🎁 FREE SERVER KE NIYAM ─────────────────────────────

FREE_STOCK=10          # kitne free server available
WEEKLY_CREDITS=10      # har baar kitne credit muft
WEEKLY_DAYS=7          # kitne din me ek baar
SERVER_LOCK_DAYS=30    # credit lene par server kitne din band
FREE_SERVER_HOURS=24   # free server kitne ghante chalega
"""


def make_template(path=None, force=False):
    """
    .env na ho to bana do — taaki user ko pata chale kya
    badal sakta hai.
    """
    p = path or os.path.join(BASE, ".env")
    if os.path.exists(p) and not force:
        return False, p
    try:
        with open(p, "w", encoding="utf-8") as f:
            f.write(TEMPLATE)
        return True, p
    except Exception as e:
        return False, str(e)
