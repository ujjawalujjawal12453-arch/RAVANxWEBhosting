"""
mailer.py — 📧 EMAIL BHEJNE WALA
════════════════════════════════════

Signup pe OTP bhejta hai. Teen raste — jo bhi key mile, wahi
chalta hai:

  1. BREVO      (300 email/din free)  → BREVO_API_KEY
  2. RESEND     (3000/mahina free)    → RESEND_API_KEY
  3. GMAIL SMTP (500/din)             → SMTP_USER + SMTP_PASS

⚠️ Koi key na ho to bhi kaam nahi rukta — OTP console me
   print ho jata hai aur admin panel me dikh jata hai. Isse
   website chalti rehti hai, sirf email nahi jata.

KEY KAHAN SE LEIN — 2 minute ka kaam:

  BREVO (sabse aasan, card nahi mangta):
    1. brevo.com → Sign up free
    2. email verify karo
    3. SMTP & API → API Keys → Generate
    4. Render → Environment → BREVO_API_KEY = xkeysib-...

  RESEND:
    1. resend.com → Sign up (GitHub se ho jata hai)
    2. API Keys → Create
    3. RESEND_API_KEY = re_...
    ⚠️ Apna domain verify kiye bina sirf apne hi email pe
       bhej paoge. Domain hai to add kar lena.

  GMAIL:
    1. Google Account → Security → 2-Step ON
    2. App Passwords → Mail → 16 akshar ka password
    3. SMTP_USER = aapka@gmail.com
       SMTP_PASS = wo 16 akshar
"""

import json
import os
import random
import re
import smtplib
import time
import urllib.error
import urllib.parse
import urllib.request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

BRAND = "RAVAN X HOSTING"
FROM_NAME = os.environ.get("MAIL_FROM_NAME", BRAND)
FROM_ADDR = os.environ.get("MAIL_FROM", "ontopujjala@gmail.com")

BREVO_KEY = os.environ.get("BREVO_API_KEY", "").strip()
RESEND_KEY = os.environ.get("RESEND_API_KEY", "").strip()
SMTP_USER = os.environ.get("SMTP_USER", "").strip()
SMTP_PASS = os.environ.get("SMTP_PASS", "").strip()
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))

# 📮 FormSubmit — bina signup. Sirf activate kiye hue pate pe.
FORMSUBMIT_TO = os.environ.get("FORMSUBMIT_TO", FROM_ADDR).strip()
SITE_REF = os.environ.get("SITE_REF",
                          "https://ravanx-hosting.onrender.com")

# OTP ka hisaab
OTP_TTL = int(os.environ.get("OTP_TTL", "600"))        # 10 minute
OTP_RESEND_SEC = int(os.environ.get("OTP_RESEND", "60"))
OTP_MAX_TRY = 5

_last_err = ""


# ─────────────────────────────────────────────────────────
#  Kaunsa rasta chalu hai
# ─────────────────────────────────────────────────────────

def ready():
    return bool(BREVO_KEY or RESEND_KEY
                or (SMTP_USER and SMTP_PASS) or FORMSUBMIT_TO)


def which():
    if BREVO_KEY:
        return "Brevo"
    if RESEND_KEY:
        return "Resend"
    if SMTP_USER and SMTP_PASS:
        return "Gmail SMTP"
    if FORMSUBMIT_TO:
        return "FormSubmit (bina signup)"
    return ""


def status():
    return {"ok": ready(), "via": which() or "koi nahi",
            "from": FROM_ADDR, "err": _last_err}


# ─────────────────────────────────────────────────────────
#  Bhejne wale
# ─────────────────────────────────────────────────────────

def _post(url, body, headers, timeout=15):
    req = urllib.request.Request(
        url, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", **headers})
    r = urllib.request.urlopen(req, timeout=timeout)
    return r.status, r.read().decode("utf-8", "replace")


def _brevo(to, subject, html, text):
    st, _ = _post(
        "https://api.brevo.com/v3/smtp/email",
        {"sender": {"name": FROM_NAME, "email": FROM_ADDR},
         "to": [{"email": to}],
         "subject": subject,
         "htmlContent": html,
         "textContent": text},
        {"api-key": BREVO_KEY, "accept": "application/json"})
    return 200 <= st < 300


def _resend(to, subject, html, text):
    st, _ = _post(
        "https://api.resend.com/emails",
        {"from": f"{FROM_NAME} <{FROM_ADDR}>", "to": [to],
         "subject": subject, "html": html, "text": text},
        {"Authorization": "Bearer " + RESEND_KEY})
    return 200 <= st < 300


def _formsubmit(to, subject, html, text):
    """
    📮 FormSubmit — BINA SIGNUP wala rasta.

    ⚠️ Malik ka hukum: "email ka free me kuch dekho, jahan bina
       sign-up ke sab kuch kar sako".

    FormSubmit.co ko koi account nahi chahiye. Bas ek baar
    activate karna padta hai:
      1. Pehli baar bhejne pe wo aapke email pe
         "Activate Form" ka link bhejta hai
      2. Wo link click karo — bas, hamesha ke liye chalu
      3. Koi API key nahi, koi dashboard nahi, koi limit nahi

    ⚠️ Ye SIRF EK email pe bhej sakta hai — wahi jo activate
       kiya hai (FORMSUBMIT_TO). Isliye ye admin ke apne code
       ke liye theek hai. Doosre users ko bhejne ke liye
       Brevo/SMTP chahiye.

    Isliye ladder me sabse NEECHE hai — pehle asli service,
    na ho to ye.
    """
    if not FORMSUBMIT_TO:
        return False
    if to.strip().lower() != FORMSUBMIT_TO.strip().lower():
        return False          # sirf activate kiye hue pate pe
    body = json.dumps({
        "name": FROM_NAME,
        "_subject": subject,
        "message": text[:3000],
        "_template": "box",
        "_captcha": "false",
    }).encode()
    req = urllib.request.Request(
        "https://formsubmit.co/ajax/" + urllib.parse.quote(to),
        data=body,
        headers={"Content-Type": "application/json",
                 "Accept": "application/json",
                 "Referer": SITE_REF, "Origin": SITE_REF,
                 "User-Agent": "Mozilla/5.0"})
    r = urllib.request.urlopen(req, timeout=20)
    d = json.loads(r.read().decode("utf-8", "replace") or "{}")
    if str(d.get("success")).lower() == "true":
        return True
    msg = str(d.get("message", ""))
    if "Activation" in msg or "Activate" in msg:
        raise RuntimeError(
            "FormSubmit ko ek baar activate karna hai — "
            f"{to} pe 'Activate Form' wala email aaya hai, "
            "usme link click kar dijiye")
    raise RuntimeError(msg[:120] or "formsubmit fail")


def _smtp(to, subject, html, text):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{FROM_NAME} <{SMTP_USER}>"
    msg["To"] = to
    msg.attach(MIMEText(text, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))
    s = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20)
    try:
        s.starttls()
        s.login(SMTP_USER, SMTP_PASS)
        s.sendmail(SMTP_USER, [to], msg.as_string())
    finally:
        try:
            s.quit()
        except Exception:
            pass
    return True


def send(to, subject, html, text=""):
    """
    Email bhejo. Jo rasta mile, use karo.
    Return: (ok, kaise/kyun)
    """
    global _last_err
    to = (to or "").strip()
    if not to or "@" not in to:
        return False, "email sahi nahi"
    text = text or re.sub(r"<[^>]+>", " ", html)

    for name, fn, on in (("Brevo", _brevo, bool(BREVO_KEY)),
                         ("Resend", _resend, bool(RESEND_KEY)),
                         ("SMTP", _smtp, bool(SMTP_USER and SMTP_PASS)),
                         ("FormSubmit", _formsubmit,
                          bool(FORMSUBMIT_TO))):
        if not on:
            continue
        try:
            if fn(to, subject, html, text):
                _last_err = ""
                return True, name
        except urllib.error.HTTPError as e:
            try:
                body = e.read().decode()[:150]
            except Exception:
                body = ""
            _last_err = f"{name} HTTP {e.code} {body}"
        except Exception as e:
            _last_err = f"{name}: {str(e)[:120]}"

    return False, _last_err or "koi email service set nahi hai"


# ─────────────────────────────────────────────────────────
#  🔢 OTP
# ─────────────────────────────────────────────────────────

BASE = os.path.dirname(os.path.abspath(__file__))
OTP_FILE = os.path.join(BASE, "data", "otp.json")
_O = None


def _load():
    global _O
    if _O is not None:
        return _O
    try:
        _O = json.load(open(OTP_FILE))
    except Exception:
        _O = {}
    return _O


def _save():
    try:
        os.makedirs(os.path.dirname(OTP_FILE), exist_ok=True)
        tmp = OTP_FILE + ".tmp"
        with open(tmp, "w") as f:
            json.dump(_load(), f)
        os.replace(tmp, OTP_FILE)
    except Exception:
        pass


def _clean():
    o = _load()
    now = time.time()
    for k in [k for k, v in o.items()
              if now - v.get("at", 0) > OTP_TTL * 3]:
        o.pop(k, None)


def otp_html(code, name=""):
    hi = f"Namaste {name}," if name else "Namaste,"
    return f"""<!DOCTYPE html><html><body style="margin:0;padding:0;
background:#070B14;font-family:-apple-system,Segoe UI,Roboto,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center"
style="padding:32px 16px">
<table width="100%" style="max-width:440px" cellpadding="0" cellspacing="0">
<tr><td style="background:linear-gradient(135deg,#7C3AED,#EC4899);
padding:26px;border-radius:16px 16px 0 0;text-align:center">
<div style="color:#fff;font-size:21px;font-weight:800;letter-spacing:1px">
RAVAN <span style="color:#00E6FF">X</span> HOSTING</div>
<div style="color:rgba(255,255,255,.82);font-size:12px;margin-top:4px">
Power · Speed · Uptime</div></td></tr>
<tr><td style="background:#0F172A;padding:32px 26px;
border-radius:0 0 16px 16px;border:1px solid #1E293B;border-top:0">
<p style="color:#F8FAFC;font-size:16px;margin:0 0 6px">{hi}</p>
<p style="color:#94A3B8;font-size:14px;margin:0 0 22px;line-height:1.6">
Aapka verification code neeche hai. Ye {OTP_TTL // 60} minute me
expire ho jayega.</p>
<div style="background:#070B14;border:1px solid #7C3AED;border-radius:12px;
padding:20px;text-align:center;margin-bottom:22px">
<div style="color:#00E6FF;font-size:36px;font-weight:800;
letter-spacing:9px;font-family:monospace">{code}</div></div>
<p style="color:#64748B;font-size:12.5px;margin:0;line-height:1.6">
Ye code kisi ko mat batana — hum kabhi nahi poochhenge.<br>
Aapne signup nahi kiya? Is email ko ignore kar dijiye.</p>
<div style="border-top:1px solid #1E293B;margin-top:24px;padding-top:16px">
<p style="color:#475569;font-size:11.5px;margin:0">
RAVAN X HOSTING TEAM · Ujjawal X Official<br>
Telegram: @UjjawalXsarkar</p></div>
</td></tr></table></td></tr></table></body></html>"""


def send_otp(email, name=""):
    """
    OTP banao aur bhejo.
    Return: (ok, msg, dev_code)
      dev_code sirf tab jab koi email service na ho — taaki
      website tab bhi chalti rahe.
    """
    _clean()
    email = (email or "").strip().lower()
    o = _load()
    old = o.get(email)
    now = time.time()

    # bahut jaldi-jaldi mat maango
    if old and now - old.get("at", 0) < OTP_RESEND_SEC:
        wait = int(OTP_RESEND_SEC - (now - old["at"]))
        return False, f"{wait} second ruk kar dobara maango", ""

    code = f"{random.randint(0, 999999):06d}"
    o[email] = {"code": code, "at": now, "try": 0, "name": name}
    _save()

    if not ready():
        # ⚠️ Key nahi hai — website rukni nahi chahiye.
        #    Code console me chhap do, admin dekh lega.
        print(f"  📧 [EMAIL SERVICE NAHI] OTP for {email} = {code}")
        return True, "dev", code

    ok, via = send(email, f"{code} — aapka {BRAND} code",
                   otp_html(code, name),
                   f"Aapka code: {code}\n"
                   f"{OTP_TTL // 60} minute me expire.\n\n{BRAND}")
    if ok:
        return True, via, ""

    # ⚠️ Email fail ho gaya — par user ko atkana GALAT hai.
    #    Code screen pe dikha do, signup/login chalta rahe.
    #    (Pehle yahan False lautaya jata tha aur user phas
    #     jata tha — wo bada bug tha.)
    print(f"  ⚠️  Email fail ({via}) — {email} ka code = {code}")
    return True, "screen", code


def check_otp(email, code):
    """
    Code sahi hai? Return: (ok, msg)
    """
    email = (email or "").strip().lower()
    code = re.sub(r"\D", "", str(code or ""))
    o = _load()
    d = o.get(email)
    if not d:
        return False, "Pehle code mangwaiye"
    if time.time() - d.get("at", 0) > OTP_TTL:
        o.pop(email, None)
        _save()
        return False, "Code expire ho gaya — naya mangwaiye"
    if d.get("try", 0) >= OTP_MAX_TRY:
        o.pop(email, None)
        _save()
        return False, f"{OTP_MAX_TRY} baar galat — naya code lijiye"
    if code != d.get("code"):
        d["try"] = d.get("try", 0) + 1
        _save()
        left = OTP_MAX_TRY - d["try"]
        return False, f"Code galat hai — {left} koshish bachi"
    o.pop(email, None)
    _save()
    return True, "ok"


def pending(email):
    """Is email pe code bheja hua hai?"""
    d = _load().get((email or "").strip().lower())
    if not d:
        return False
    return time.time() - d.get("at", 0) <= OTP_TTL


# ─────────────────────────────────────────────────────────
#  Swagat email — signup ho jane ke baad
# ─────────────────────────────────────────────────────────

def welcome(email, name=""):
    if not ready():
        return False, "service nahi"
    html = f"""<!DOCTYPE html><html><body style="margin:0;padding:0;
background:#070B14;font-family:-apple-system,Segoe UI,Roboto,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center"
style="padding:32px 16px">
<table width="100%" style="max-width:440px" cellpadding="0" cellspacing="0">
<tr><td style="background:linear-gradient(135deg,#7C3AED,#EC4899);
padding:26px;border-radius:16px 16px 0 0;text-align:center">
<div style="color:#fff;font-size:21px;font-weight:800;letter-spacing:1px">
RAVAN <span style="color:#00E6FF">X</span> HOSTING</div></td></tr>
<tr><td style="background:#0F172A;padding:30px 26px;
border-radius:0 0 16px 16px;border:1px solid #1E293B;border-top:0">
<p style="color:#F8FAFC;font-size:17px;margin:0 0 14px">
Swagat hai{(", " + name) if name else ""}! 🎉</p>
<p style="color:#94A3B8;font-size:14px;line-height:1.7;margin:0 0 18px">
Aapka account ban gaya. Ab aap apne bots aur apps 24/7 online
rakh sakte hain.</p>
<div style="background:#070B14;border:1px solid #1E293B;
border-radius:12px;padding:16px;margin-bottom:18px">
<p style="color:#00E6FF;font-size:13px;font-weight:700;margin:0 0 10px">
🎁 SHURUAAT KE LIYE</p>
<p style="color:#94A3B8;font-size:13px;line-height:1.8;margin:0">
• Har 7 din me <b style="color:#F8FAFC">10 credit muft</b><br>
• Ya free server — <b style="color:#F8FAFC">24 ghante</b> ke liye<br>
• AI Boss se poochho — kuch bhi</p></div>
<p style="color:#64748B;font-size:12px;margin:0">
Madad chahiye? Telegram: @UjjawalXsarkar</p>
</td></tr></table></td></tr></table></body></html>"""
    return send(email, f"Swagat hai {BRAND} me! 🎉", html)
