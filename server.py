"""
server.py — RAVAN X CLOUD
══════════════════════════
Poora hosting company website: landing + login/signup + dashboard + admin.

Chalao:  python3 server.py
Kholo :  http://localhost:8080

Sirf Python stdlib — koi pip install nahi.
"""

import html
import http.cookies
import hashlib
import hmac
import json
import os
import random
import re
import secrets
import socket
import sys
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import db
import engine
import famgateway_pay
import brain
import botlink
import cloudsync
import coder
import freeserver
import jarvispage
import landing
import live
import pages
import storage
import storagepage
import sysinfo
import theme
import tunnel
import unlock
import vcmd
import voice
from brand import ico, logo, sparkline, minibars, donut, gauge
from theme import BRAND, PLANS, PACKS, CREDIT_RATE, ADMIN_PASS, FREE_PLAN, FREE_HOURS, esc, page, footer, dash_page

PORT = int(os.environ.get("PORT", "8080"))
HOST = os.environ.get("HOST", "0.0.0.0")


# ══════════════════════════════════════════════
#   HELPERS
# ══════════════════════════════════════════════

def money(n):
    return f"₹{n:,.0f}" if float(n) == int(n) else f"₹{n:,.2f}"


def ago(ts):
    if not ts:
        return "—"
    d = int(time.time()) - int(ts)
    if d < 60:
        return "abhi"
    if d < 3600:
        return f"{d // 60}m pehle"
    if d < 86400:
        return f"{d // 3600}h pehle"
    return f"{d // 86400}d pehle"


def uptime(ts):
    if not ts:
        return "—"
    d = int(time.time()) - int(ts)
    h, m = divmod(d // 60, 60)
    if h >= 24:
        return f"{h // 24}d {h % 24}h"
    return f"{h}h {m}m" if h else f"{m}m"


def plan_of(key):
    for p in PLANS:
        if p[0] == key:
            return p
    return PLANS[0]


def bar(pct, cls=""):
    pct = max(0, min(100, pct))
    c = "r" if pct >= 90 else ("y" if pct >= 70 else "")
    return f'<div class="bar {c}"><i style="width:{pct}%"></i></div>'


# ══════════════════════════════════════════════
#   LANDING
# ══════════════════════════════════════════════

# ══════════════════════════════════════════════
#   AUTH
# ══════════════════════════════════════════════

# ══════════════════════════════════════════════
#   ✨ AUTH ANIMATION — login/signup ka jaan
# ══════════════════════════════════════════════

def _authfx(lines):
    """
    Typing animation + floating particles + scan line.
    `lines` = jo text ek-ek karke type hoga.
    """
    import json as _j
    return f'''<div class="afx">
<div class="afxgrid"></div>
<span class="afxp p1"></span><span class="afxp p2"></span>
<span class="afxp p3"></span><span class="afxp p4"></span>
<span class="afxp p5"></span><span class="afxp p6"></span>
<div class="afxscan"></div></div>
<div class="afxtype"><span id="afxt"></span><i class="afxcur"></i></div>
<script>
(function(){{
  var L = {_j.dumps(lines)}, li = 0, ci = 0, del = false;
  var el = document.getElementById('afxt');
  if (!el) return;
  function tick(){{
    var w = L[li];
    if (!del) {{
      el.textContent = w.slice(0, ++ci);
      if (ci === w.length) {{ del = true; setTimeout(tick, 1400); return; }}
      setTimeout(tick, 45);
    }} else {{
      el.textContent = w.slice(0, --ci);
      if (ci === 0) {{ del = false; li = (li + 1) % L.length; }}
      setTimeout(tick, 22);
    }}
  }}
  tick();
}})();
function afxGo(f){{
  var b = document.getElementById('afxbtn');
  if (b) {{
    b.classList.add('load');
    var sp = b.querySelector('span');
    if (sp) sp.textContent = 'Ruko\\u2026';
    b.disabled = true;
    setTimeout(function(){{ b.disabled = false; }}, 8000);
  }}
  var bx = document.querySelector('.authin');
  if (bx) bx.classList.add('go');
  return true;
}}
</script>'''


# 📧 Jo log OTP ka intezaar kar rahe hain (account abhi nahi bana)
PENDING_SIGNUP = {}
# 📧 Purane user jo login pe verify kar rahe hain
PENDING_LOGIN = {}
PENDING_TTL = 1800          # 30 minute


def _clean_pending():
    """Purane adhoore signup hata do — memory saaf rahe"""
    now = time.time()
    for k in [k for k, v in PENDING_SIGNUP.items()
              if now - v.get("at", 0) > PENDING_TTL]:
        PENDING_SIGNUP.pop(k, None)
    for k in [k for k, v in PENDING_LOGIN.items()
              if now - v.get("at", 0) > PENDING_TTL]:
        PENDING_LOGIN.pop(k, None)


def p_otp(email, err="", ok="", dev="", login=False):
    """
    📧 OTP daalne ka page.

    ⚠️ Signup ab do kadam ka hai: pehle email verify, phir
       account. Isse fake email se account nahi banega.
    """
    e = (f'<div class="msg err">{ico("x",15)}<div>{esc(err)}</div></div>'
         if err else "")
    o = (f'<div class="msg on">{ico("check",15)}<div>{esc(ok)}</div></div>'
         if ok else "")
    # koi email service na ho to code screen pe — website rukni nahi chahiye
    d = (f'<div class="msg warn">{ico("info",15)}<div>'
         f'<b>Email service abhi set nahi hai.</b><br>'
         f'Aapka code: <b style="font-size:19px;letter-spacing:3px;'
         f'color:var(--acc3)">{esc(dev)}</b></div></div>' if dev else "")
    fx = _authfx(["Email verify kar rahe hain.",
                  "6 number ka code bheja hai.",
                  "10 minute me expire ho jayega.",
                  "Inbox nahi mila? Spam dekho."])
    body = f"""<div class="auth">{fx}<div class="box authin">
<div class="bh">{logo(40, text=False)}
<h2>Email verify karo</h2>
<p class="s">Code bheja hai — <b>{esc(email)}</b></p>
{'<p class="dim2 xs mt2">Ek baar ka kaam hai — iske baad seedha '
 'login ho jayega.</p>' if login else ''}</div>
{d}{o}{e}
<form method="POST" action="/verify-email">
<input type="hidden" name="email" value="{esc(email)}">
<div class="fld"><label>6 number ka code</label>
<input name="code" required inputmode="numeric" pattern="[0-9]*"
maxlength="6" autofocus autocomplete="one-time-code"
placeholder="000000" style="font-size:26px;letter-spacing:11px;
text-align:center;font-family:monospace"></div>
<button class="btn btn-p btn-b btn-lg">
{ico("check",16)} <span>Verify karo</span></button>
</form>
<form method="POST" action="/resend-otp" style="margin-top:10px">
<input type="hidden" name="email" value="{esc(email)}">
<button class="btn btn-g btn-b">{ico("refresh",14)} Dobara bhejo</button>
</form>
<p class="dim2 xs tc mt2">Inbox me na mile to <b>Spam</b> folder
dekhiye.<br>Galat email? <a href="/signup">Wapas jao</a></p>
</div></div>"""
    return page("Email verify", body)


def p_signup(err="", vals=None, bot=None, btok=""):
    v = vals or {}
    e = (f'<div class="msg err">{ico("x",15)}<div>{esc(err)}</div></div>'
         if err else "")
    # 🤖 Bot se aaya banda — swagat karo
    welcome = ""
    hidden = ""
    if bot:
        nm = esc(str(bot.get("name") or "dost"))
        welcome = f'''<div class="botwel">
<div class="bwi">{ico("bolt",20)}</div>
<div><b>Namaste {nm}!</b>
<span>Aap bot se aaye hain — sab kuch taiyaar hai</span></div></div>'''
        hidden = f'<input type="hidden" name="btok" value="{esc(btok)}">'
        if bot.get("name") and not v.get("name"):
            v = dict(v, name=bot["name"])
    fx = _authfx(["Naya account bana rahe hain?",
                  "25 credits bilkul free.",
                  "Card ki zarurat nahi.",
                  "30 second me ho jayega."])
    body = f"""<div class="auth">{fx}<div class="box authin">
<div class="bh">{logo(40, text=False)}
<h2>Account banao</h2>
<p class="s">25 credits free — card ki zarurat nahi</p></div>
{welcome}{e}
<form method="POST" action="/signup" onsubmit="return afxGo(this)">{hidden}
<div class="fld"><label>Poora naam</label>
<input name="name" required value="{esc(v.get('name',''))}"
placeholder="Aapka naam" maxlength="60" autofocus></div>
<div class="fld"><label>Email</label>
<input name="email" type="email" required value="{esc(v.get('email',''))}"
placeholder="aap@gmail.com"></div>
<div class="fld"><label>Phone <span class="dim2">(optional)</span></label>
<input name="phone" value="{esc(v.get('phone',''))}"
placeholder="9876543210" maxlength="15"></div>
<div class="fld"><label>Password</label>
<input name="password" type="password" required minlength="8"
placeholder="Kam se kam 8 character">
<div class="hint">{ico("lock",12)} PBKDF2 se encrypt hoga</div></div>
<button class="btn btn-p btn-b btn-lg" id="afxbtn">
{ico("rocket",16)} <span>Account Banao</span></button>
</form>
<div class="flex mt" style="justify-content:center;gap:22px">
<span class="dim2 xs">{ico("check",12)} 25 credits</span>
<span class="dim2 xs">{ico("check",12)} No card</span>
<span class="dim2 xs">{ico("check",12)} 30 sec</span></div>
<p class="tc dim mt" style="font-size:14px">Pehle se account hai?
<a href="/login" style="color:var(--acc3);font-weight:600">Login karo</a></p>
</div></div>"""
    return page("Sign Up", body)


def p_login(err="", ok=""):
    m = ""
    if err:
        m = f'<div class="msg err">{ico("x",15)}<div>{esc(err)}</div></div>'
    elif ok:
        m = f'<div class="msg ok">{ico("check",15)}<div>{esc(ok)}</div></div>'
    fx = _authfx(["Wapas aa gaye, sir.",
                  "Aapke servers chal rahe hain.",
                  "57 AI model taiyaar hain.",
                  "Boss Agent intezaar kar raha hai."])
    body = f"""<div class="auth">{fx}<div class="box authin">
<div class="bh">{logo(40, text=False)}
<h2>Wapas aa gaye</h2><p class="s">Apne dashboard me login karo</p></div>{m}
<form method="POST" action="/login" onsubmit="return afxGo(this)">
<div class="fld"><label>Email</label>
<input name="email" type="email" required placeholder="aap@gmail.com" autofocus>
</div>
<div class="fld"><label>Password</label>
<input name="password" type="password" required placeholder="••••••••"></div>
<button class="btn btn-p btn-b btn-lg" id="afxbtn">
{ico("logout",16)} <span>Login</span></button></form>
<p class="tc dim mt" style="font-size:14px">Account nahi hai?
<a href="/signup" style="color:var(--acc3);font-weight:600">Free me banao</a></p>
</div></div>"""
    return page("Login", body)


# ══════════════════════════════════════════════
#   DASHBOARD
# ══════════════════════════════════════════════

def p_dashboard(u):
    apps = db.user_apps(u["id"])
    run = sum(1 for a in apps if engine.is_running(a["id"]))
    ram = sum(engine.usage(a["id"])["ram"] for a in apps)
    disk = sum(engine.disk_mb(u["id"], a["id"]) for a in apps)
    hrs = int(u["credits"] // CREDIT_RATE)
    burn = run * CREDIT_RATE
    left = int(u["credits"] // burn) if burn else 0

    warn = ""
    if u["credits"] < CREDIT_RATE * 4:
        warn = f"""<div class="msg warn">{ico("bell",15)}<div>
<b>Credits kam hain</b> — {u['credits']:.0f} bache
({hrs} ghante). Servers band ho sakte hain.
<a href="/recharge" style="color:#A78BFA;text-decoration:underline">
Abhi recharge karo →</a></div></div>"""

    cards = f"""<div class="grid g4 mb">
<div class="stat"><div class="top"><span class="lbl">Credits</span>
<span class="ib">{ico("wallet",15)}</span></div>
<div class="val">{u['credits']:.0f}</div>
<div class="sub">{ico("clock",12)} {hrs} ghante hosting</div>
<div class="chart">{sparkline([u['credits']*.6,u['credits']*.8,
u['credits']*.7,u['credits']*.9,u['credits']] if u['credits'] else [0,0],
110,28,"#00E6FF",sid="d1")}</div></div>

<div class="stat"><div class="top"><span class="lbl">Servers</span>
<span class="ib p">{ico("server",15)}</span></div>
<div class="val">{len(apps)}</div>
<div class="sub"><span class="up">{ico("bolt",12)} {run} live</span></div>
<div class="chart">{minibars([1,2,2,3,len(apps) or 1],110,28,"#8B5CF6")}</div>
</div>

<div class="stat"><div class="top"><span class="lbl">RAM Used</span>
<span class="ib c">{ico("ram",15)}</span></div>
<div class="val">{ram:.0f}<small style="font-size:15px"> MB</small></div>
<div class="sub">{disk:.0f} MB disk</div>
<div class="chart">{sparkline([ram*.4,ram*.7,ram*.5,ram*.9,ram] if ram
else [0,0],110,28,"#22D3EE",sid="d2")}</div></div>

<div class="stat"><div class="top"><span class="lbl">Burn Rate</span>
<span class="ib y">{ico("bolt",15)}</span></div>
<div class="val">{burn}<small style="font-size:15px">/hr</small></div>
<div class="sub">{f"{left}h bache" if burn else "koi server live nahi"}</div>
<div class="chart">{minibars([burn or 1]*5,110,28,"#F59E0B")}</div></div>
</div>"""

    if apps:
        rows = ""
        for a in apps[:6]:
            sid = a["id"]
            r = engine.is_running(sid)
            us = engine.usage(sid)
            pl = plan_of(a["plan"])
            rp = min(100, int(us["ram"] / pl[3] * 100)) if pl[3] else 0
            rows += f"""<tr>
<td><div class="flex" style="gap:10px">
<span class="ib" style="width:32px;height:32px;border-radius:9px;
background:rgba(47,129,247,.1);color:var(--acc3);display:grid;
place-items:center">{ico("server",15)}</span>
<div><b>{esc(a['name'])}</b>
<div class="dim2 xs">{esc(a['lang'])} · {pl[1]}</div></div></div></td>
<td><span class="bdg {'on' if r else 'off'}">{'Live' if r else 'Stopped'}</span></td>
<td style="min-width:110px">{us['ram']} MB{bar(rp)}</td>
<td>{us['cpu']}%</td>
<td class="dim">{uptime(us['uptime']) if r else '—'}</td>
<td><div class="flex" style="gap:6px">
<a href="/server/{sid}" class="btn btn-g btn-sm">{ico("edit",13)}</a>
<a href="/console?s={sid}" class="btn btn-g btn-sm">{ico("term",13)}</a>
<a href="/server/{sid}/{'stop' if r else 'start'}"
class="btn {'btn-d' if r else 'btn-ok'} btn-sm">
{ico('stop' if r else 'play',13)}</a></div></td></tr>"""
        table = f"""<div class="tbl"><div class="th">
<h3>{ico("server",17)} Aapke Servers</h3>
<a href="/servers" class="btn btn-g btn-sm">Sab dekho {ico("up",13)}</a></div>
<table><thead><tr><th>Server</th><th>Status</th><th>RAM</th><th>CPU</th>
<th>Uptime</th><th>Actions</th></tr></thead><tbody>{rows}</tbody></table></div>"""
    else:
        table = f"""<div class="card empty">
<div class="ei">{ico("server",30)}</div>
<h3>Abhi koi server nahi</h3>
<p>Apna pehla server banao — 30 second me live ho jayega</p>
<a href="/servers/new" class="btn btn-p">{ico("rocket",16)} Server Banao</a>
</div>"""

    quick = f"""<div class="grid g4 mt">
<a href="/servers/new" class="feat" style="text-decoration:none">
<div class="fi">{ico("plus",20)}</div><h3>Naya Server</h3>
<p>30 second me deploy</p></a>
<a href="/console" class="feat" style="text-decoration:none">
<div class="fi">{ico("term",20)}</div><h3>Live Console</h3>
<p>Asli terminal dekho</p></a>
<a href="/analytics" class="feat" style="text-decoration:none">
<div class="fi">{ico("chart",20)}</div><h3>Analytics</h3>
<p>Usage aur burn rate</p></a>
<a href="/recharge" class="feat" style="text-decoration:none">
<div class="fi">{ico("card",20)}</div><h3>Add Credits</h3>
<p>UPI se turant</p></a></div>"""

    return dash_page(f"Namaste, {esc(u['name'].split()[0])}",
                     "Aapke servers ka live status", warn + cards + table + quick,
                     u, "dashboard",
                     f'<a href="/servers/new" class="btn btn-p">{ico("plus",15)} Naya Server</a>')


def p_billing(u):
    tx = db.user_txns(u["id"], 20)
    pays = db.user_payments(u["id"], 10)
    spent = sum(abs(t["amount"]) for t in tx if t["amount"] < 0)
    added = sum(t["amount"] for t in tx if t["amount"] > 0)
    hrs = int(u["credits"] // CREDIT_RATE)

    trows = "".join(f"""<tr><td>{esc(t['note'])}</td>
<td><b style="color:{'#22C55E' if t['amount']>0 else '#FF6B8A'}">
{'+' if t['amount']>0 else ''}{t['amount']:.1f}</b></td>
<td class="dim">{ago(t['ts'])}</td></tr>""" for t in tx) or \
        '<tr><td colspan="3" class="dim tc" style="padding:26px">Koi transaction nahi</td></tr>'

    prows = "".join(f"""<tr><td><code>{esc(p['ref'])}</code></td>
<td><b>{money(p['rupees'])}</b></td><td>{p['credits']} cr</td>
<td><span class="bdg {'on' if p['status']=='approved' else
('wait' if p['status']=='pending' else 'err')}">{p['status']}</span></td>
<td class="dim">{ago(p['ts'])}</td></tr>""" for p in pays) or \
        '<tr><td colspan="5" class="dim tc" style="padding:26px">Koi payment nahi</td></tr>'

    content = f"""<div class="grid g4 mb">
<div class="stat"><div class="top"><span class="lbl">Balance</span>
<span class="ib">{ico("wallet",15)}</span></div>
<div class="val">{u['credits']:.0f}</div>
<div class="sub">{hrs} ghante hosting</div></div>
<div class="stat"><div class="top"><span class="lbl">Total Added</span>
<span class="ib g">{ico("up2",15)}</span></div>
<div class="val">{added:.0f}</div></div>
<div class="stat"><div class="top"><span class="lbl">Total Used</span>
<span class="ib y">{ico("bolt",15)}</span></div>
<div class="val">{spent:.0f}</div></div>
<div class="stat" style="display:grid;place-items:center">
<a href="/recharge" class="btn btn-p">{ico("plus",15)} Add Credits</a></div>
</div>
<div class="grid g2">
<div class="tbl"><div class="th"><h3>{ico("clock",17)} Transactions</h3></div>
<table><thead><tr><th>Note</th><th>Credits</th><th>When</th></tr></thead>
<tbody>{trows}</tbody></table></div>
<div class="tbl"><div class="th"><h3>{ico("card",17)} Payments</h3></div>
<table><thead><tr><th>Ref</th><th>Amount</th><th>Credits</th><th>Status</th>
<th>When</th></tr></thead><tbody>{prows}</tbody></table></div></div>"""
    return dash_page("Wallet", "Credits aur payment history", content, u, "billing")


def p_paid(u, ref, rs, cr):
    """
    🎉 PAYMENT SUBMIT HO GAYA — jashn wala page

    User ne kaha: "jab bhi payment vagaira successful hota hai to
    uske aakhiri mein ek emoji ya FIR emoji vagaira to aana hi
    chahie"

    Pehle sirf ek patli si line aati thi "Payment submit ho gaya".
    User ko pata hi nahi chalta tha ki sach me hua ya nahi — aur
    itne bade kaam (paisa bhejna) ke baad wo bahut sookha lagta
    tha.

    ⚠️ Saaf likha hai "SUBMIT ho gaya", "credits mil gaye" NAHI.
       Admin ke verify karne tak credit nahi milte. Jhooth bol
       kar khush karna galat hota.
    """
    content = f"""
<div class="card" style="text-align:center;padding:38px 22px;
position:relative;overflow:hidden">

  <div class="cfx" id="cfx"></div>

  <div class="paid-emo">🎉</div>
  <div class="paid-ring"></div>

  <h2 style="margin:16px 0 6px;font-size:25px">
    Payment submit ho gaya! 🥳</h2>
  <p class="dim" style="max-width:430px;margin:0 auto 20px">
    Shukriya sir 🙏 &nbsp;Aapki payment humein mil gayi hai.
    Verify hote hi credits aapke account me aa jayenge.</p>

  <div class="grid g3" style="max-width:440px;margin:0 auto 22px">
    <div class="card flat"><div class="dim2 xs">BHEJA</div>
      <div class="big" style="font-size:22px">{money(rs)}</div></div>
    <div class="card flat"><div class="dim2 xs">MILENGE</div>
      <div class="big" style="font-size:22px;color:var(--acc3)">
        {cr}</div></div>
    <div class="card flat"><div class="dim2 xs">REF</div>
      <code style="font-size:13px">{esc(ref)}</code></div>
  </div>

  <div class="steps" style="max-width:420px;margin:0 auto;
  text-align:left">
    <div class="step done"><div class="n">✓</div><div class="sc">
      <b>Payment mili</b><p>UTR aur screenshot dono aa gaye</p>
    </div></div>
    <div class="step now"><div class="n">⏳</div><div class="sc">
      <b>Verify ho rahi hai</b>
      <p>Aam taur pe 5–30 minute lagte hain</p></div></div>
    <div class="step"><div class="n">🎁</div><div class="sc">
      <b>Credits milenge</b>
      <p>Account me apne aap jud jayenge</p></div></div>
  </div>

  <div class="flex mt" style="justify-content:center;gap:10px">
    <a href="/dashboard" class="btn btn-p btn-b">
      {ico("home",15)} Dashboard</a>
    <a href="/recharge" class="btn btn-g">
      {ico("card",15)} Aur credits</a>
  </div>

  <p class="dim2 xs mt2">
    Ref number sambhal kar rakhiye — poochhne par kaam aayega ✨</p>
</div>

<style>
.paid-emo{{font-size:76px;line-height:1;
  animation:pop .7s cubic-bezier(.2,1.6,.4,1) both}}
.paid-ring{{width:104px;height:104px;border-radius:50%;
  border:2px solid var(--ok);margin:-88px auto 0;opacity:0;
  animation:ring 1.5s ease-out .25s infinite}}
@keyframes pop{{0%{{transform:scale(0) rotate(-25deg);opacity:0}}
  60%{{transform:scale(1.25) rotate(8deg)}}
  100%{{transform:scale(1) rotate(0);opacity:1}}}}
@keyframes ring{{0%{{transform:scale(.7);opacity:.8}}
  100%{{transform:scale(2.1);opacity:0}}}}
.cfx{{position:absolute;inset:0;pointer-events:none;overflow:hidden}}
.cfp{{position:absolute;width:9px;height:9px;top:-14px;
  animation:fall linear forwards}}
@keyframes fall{{to{{transform:translateY(560px) rotate(760deg);
  opacity:0}}}}
</style>
<script>
/* 🎊 confetti — bina kisi library ke, sirf 34 div */
(function(){{
  var box=document.getElementById('cfx');
  if(!box) return;
  var col=['#00E6FF','#7C3AED','#EC4899','#22C55E','#F59E0B'];
  for(var i=0;i<34;i++){{
    var d=document.createElement('i');
    d.className='cfp';
    d.style.left=(Math.random()*100)+'%';
    d.style.background=col[i%col.length];
    d.style.animationDuration=(2+Math.random()*1.8)+'s';
    d.style.animationDelay=(Math.random()*.7)+'s';
    d.style.borderRadius=(i%3?'50%':'2px');
    box.appendChild(d);
  }}
  /* 7 second baad hata do — warna page bhari rehta hai */
  setTimeout(function(){{ box.innerHTML=''; }}, 7000);
}})();
</script>"""
    return dash_page("Payment", "Ho gaya 🎉", content, u, "recharge")


def create_famgateway_web_order(u, pack_idx, webhook_url=""):
    """Create or reuse a pending website checkout order. Returns (order, ref, rupees, credits, error)."""
    try:
        rs, cr = PACKS[int(pack_idx)]
    except Exception:
        return None, "", 0, 0, "Recharge pack sahi nahi hai."
    if not famgateway_pay.configured():
        return None, "", rs, cr, "FamGateway API key website ke private environment me set nahi hai."
    # Reuse this user's recent unpaid gateway order to avoid duplicate QR orders.
    for old in db.user_payments(u["id"], 10):
        if old.get("provider") == "famgateway" and old.get("status") == "pending" and int(time.time()) - int(old.get("ts", 0)) < 285 and old.get("qr_url"):
            order = {"order_id": old.get("gateway_order") or old["ref"], "amount": old["rupees"],
                     "qr_url": old.get("qr_url", ""), "checkout_url": old.get("checkout_url", ""), "upi_intent": ""}
            return order, old["ref"], float(old["rupees"]), int(old["credits"]), ""
    order, err = famgateway_pay.create_order(rs, u, webhook_url=webhook_url)
    if not order:
        return None, "", rs, cr, err
    ref = order["order_id"]
    try:
        db.create_payment(u["id"], ref, rs, cr)
        db.set_payment(ref, provider="famgateway", gateway_order=ref,
                       qr_url=order.get("qr_url", ""), checkout_url=order.get("checkout_url", ""))
    except Exception as exc:
        return None, "", rs, cr, "Order database me save nahi hua. Dobara try karein."
    return order, ref, rs, cr, ""


def p_famgateway_checkout(u, order, ref, rs, cr, pack_idx):
    """Website payment page: dynamic FamGateway QR + live Check Payment button."""
    import html as _html
    qr = _html.escape(order.get("qr_url", ""), quote=True)
    checkout = _html.escape(order.get("checkout_url", ""), quote=True)
    oid = _html.escape(order.get("order_id", ""), quote=True)
    amount = money(rs)
    intent = _html.escape(order.get("upi_intent", ""), quote=True)
    content = f"""<div class="card tc" style="max-width:580px;margin:auto">
<h2>💳 FamGateway UPI Payment</h2>
<p class="dim">Scan this live QR or open secure checkout. FamGateway payment verify karega; confirmation ke baad credits automatic add honge.</p>
<div class="msg mt2" style="text-align:left"><b>Payment kaise karein</b><br>• FamPay, PhonePe, GPay, BHIM ya kisi bhi supported UPI app se isi page ka QR/checkout use karein.<br>• <b>QR me dikhaya exact amount aur recipient UPI hi pay karein</b>; kisi doosri UPI ID par transfer na karein. Payer ka UPI app/bank alag ho sakta hai.<br>• Payment receive hone wali merchant FamPay account aur uska linked Gmail/IMAP integration FamGateway me active hona chahiye.<br>• Page khula rehne dein—status automatic check hoga; verified payment par credits wallet me aa jayenge. Screenshot/UTR manually submit nahi karna hota.</div>
<div class="card flat" style="background:#fff;display:inline-block;padding:12px;margin:14px auto">
<img src="{qr}" alt="FamGateway payment QR" style="width:min(260px,70vw);height:auto;display:block">
</div>
<div class="grid g2 mt2">
<div class="card flat"><div class="dim2 xs">PAYABLE</div><div class="big">{amount}</div></div>
<div class="card flat"><div class="dim2 xs">CREDITS AFTER VERIFIED PAYMENT</div><div class="big" style="color:var(--acc3)">{int(cr)}</div></div>
</div>
<div class="dim sm mt2">Order ID: <code>{oid}</code> · Expires in <b id="fgTimer">05:00</b></div>
<a class="btn btn-p mt2" style="display:block" href="{checkout}" target="_blank" rel="noopener">📲 Open secure checkout / UPI</a>
<button class="btn btn-g mt2" id="fgCheck" type="button" onclick="checkFamPayment(true)">🔄 Check Payment</button>
<div id="fgStatus" class="msg mt2" style="display:block">⏳ Payment ka intezaar hai. Bank confirmation ke baad credits auto-add honge.</div>
<a href="/dashboard" class="btn btn-d mt2" style="display:block">← Dashboard</a>
<script>
(function(){{
 let remain=300, busy=false, done=false;
 const timer=document.getElementById('fgTimer'), box=document.getElementById('fgStatus'), btn=document.getElementById('fgCheck');
 function tick(){{ if(done)return; let m=Math.floor(remain/60),s=remain%60; timer.textContent=String(m).padStart(2,'0')+':'+String(s).padStart(2,'0'); if(remain<=0){{box.className='msg err mt2';box.textContent='⌛ Payment order expire ho gaya. Naya order bana kar pay karein.';btn.disabled=true;return;}} remain--; }}
 tick(); setInterval(tick,1000);
 window.checkFamPayment=function(manual){{ if(busy||done)return; busy=true; btn.disabled=true; if(manual)box.textContent='🔎 FamGateway se live payment status check ho raha hai...'; fetch('/api/famgateway-status?order_id='+encodeURIComponent('{oid}'),{{cache:'no-store'}}).then(r=>r.json()).then(d=>{{
  if(d.status==='success'){{done=true;box.className='msg ok mt2';box.textContent='✅ Payment verified! '+d.credits+' credits wallet me add hue.';btn.textContent='✅ Verified';setTimeout(()=>location.href='/dashboard',2200);}}
  else if(d.status==='expired'){{done=true;box.className='msg err mt2';box.textContent='⌛ Order expire ho gaya. Naya payment order banayein.';btn.disabled=true;}}
  else if(d.status==='review'){{box.className='msg err mt2';box.textContent=d.message||'Payment manual review me bheji gayi hai.';btn.disabled=false;}}
  else {{if(manual){{box.className='msg mt2';box.textContent='⏳ Abhi payment confirm nahi hui. Payment ke baad phir Check Payment dabayein.';}}btn.disabled=false;}}
 }}).catch(()=>{{if(manual)box.textContent='⚠️ Status connection error; auto-check dobara koshish karega.';btn.disabled=false;}}).finally(()=>{{busy=false;}});}};
 setInterval(()=>window.checkFamPayment(false),4000);
}})();
</script>"""
    return dash_page("FamGateway Payment", "Live QR · auto verification", content, u, "recharge")


def p_recharge(u, msg="", err=""):
    # 📱 UPI QR — user ki shikayat thi "QR code aata hi nahin hai"
    #
    # ⚠️ Amount JAANBUJH KAR nahi daala. User pehle pack chunta
    #    hai, phir alag-alag amount ho sakta hai. Fix amount ka
    #    QR banate to galat pack pe galat paisa chala jata.
    #    Khali QR me user khud amount daalta hai — safe hai.
    try:
        import qr as _qr
        _qr_svg = _qr.upi_svg(theme.UPI_ID, theme.UPI_NAME, px=6)
    except Exception:
        _qr_svg = ""
    if not _qr_svg:
        _qr_svg = ('<div class="dim sm" style="padding:26px">'
                   'QR nahi bana — neeche UPI ID use karo</div>')
    m = ""
    if msg:
        m = f'<div class="msg ok">{ico("check",15)}<div>{msg}</div></div>'
    elif err:
        m = f'<div class="msg err">{ico("x",15)}<div>{esc(err)}</div></div>'

    packs = ""
    for i, (rs, cr) in enumerate(PACKS):
        bonus = cr - rs
        hot = " glow" if i == 2 else ""
        packs += f"""<div class="card{hot}" style="text-align:center">
{f'<div class="stag" style="margin-bottom:8px">+{bonus} BONUS</div>'
  if bonus>0 else '<div style="height:29px"></div>'}
<div class="big" style="color:var(--acc3)">{cr}</div>
<div class="dim2 xs" style="letter-spacing:1px">CREDITS</div>
<div style="font-size:21px;font-weight:800;margin:11px 0">{money(rs)}</div>
<div class="dim2 xs mb2">≈ {int(cr//CREDIT_RATE)} ghante</div>
<a href="/recharge?pack={i}" class="btn btn-p btn-sm btn-b">Select</a></div>"""

    opts = "".join(f'<option value="{i}">{money(rs)} → {cr} credits</option>'
                   for i, (rs, cr) in enumerate(PACKS))

    content = f"""{m}<div class="grid g" style="grid-template-columns:
repeat(auto-fit,minmax(160px,1fr))">{packs}</div>

<div class="split mt">
<div><h3 class="mb2">{ico("card",18)} Payment kaise karein</h3>
<div class="steps">
<div class="step done"><div class="n">1</div><div class="sc">
<b>Pack chuno</b><p>Upar se koi bhi pack select karo</p></div></div>
<div class="step done"><div class="n">2</div><div class="sc">
<b>UPI se bhejo</b><p>Neeche wali UPI ID par exact amount</p></div></div>
<div class="step done"><div class="n">3</div><div class="sc">
<b>UTR copy karo</b><p>Receipt me 12 digit ka number hota hai</p></div></div>
<div class="step now"><div class="n">4</div><div class="sc">
<b>Form bharo</b><p>Verify hote hi credits mil jayenge</p></div></div></div>
<div class="card flat mt2" style="background:var(--bg2);
text-align:center">
<div class="dim2 xs" style="letter-spacing:1px;margin-bottom:10px">
{ico("card",12)} QR SCAN KARO</div>
<div style="background:#fff;padding:10px;border-radius:14px;
display:inline-block;line-height:0">{_qr_svg}</div>
<div class="dim2 xs mt2">Koi bhi UPI app se scan karo</div>
<div style="height:12px"></div>
<div class="dim2 xs" style="letter-spacing:1px">YA UPI ID</div>
<code style="font-size:15px;display:inline-block;margin:6px 0">
{theme.UPI_ID}</code>
<div class="dim sm">{ico("user",13)} {theme.UPI_NAME}</div>
<button type="button" class="btn btn-g btn-sm mt2"
onclick="navigator.clipboard.writeText('{theme.UPI_ID}');
this.textContent='Copy ho gaya'">UPI ID copy karo</button>
</div></div>

<div><h3 class="mb2">{ico("check",18)} Payment submit karo</h3>
<form method="POST" action="/recharge" enctype="multipart/form-data"
id="payf" onsubmit="return payGo()">
<div class="fld"><label>Kitna bheja?</label>
<select name="pack">{opts}</select></div>
<div class="fld"><label>UTR / Reference number</label>
<input name="utr" required pattern="[0-9]{{12}}" maxlength="12"
placeholder="129812103075" style="font-family:monospace;font-size:16px">
<div class="hint">{ico("shield",12)} Ek UTR sirf ek baar use hota hai</div>
</div>

<div class="fld"><label>Payment screenshot {ico("shield",12)}
<span style="color:var(--pk2)">zaroori</span></label>
<div class="drop" id="drop" onclick="document.getElementById('shot').click()">
<input type="file" name="shot" id="shot" accept="image/*" required
onchange="shotPick(this)" style="display:none">
<div id="dtxt">
<div class="dicon">{ico("up",26)}</div>
<b>Screenshot yahan daalo</b>
<span class="dim xs">PhonePe / GPay / Paytm ki receipt — JPG ya PNG</span>
</div>
<img id="prev" style="display:none">
</div>
<div class="hint">{ico("eye",12)} UTR aur amount saaf dikhna chahiye</div>
</div>

<button class="btn btn-p btn-b btn-lg" id="paybtn">
{ico("check",16)} Submit karo</button>
</form>

<div class="ovl" id="ovl"><div class="obox">
<div class="oring"><i></i><i></i><i></i></div>
<h3 id="ottl">Payment check ho rahi hai</h3>
<div class="osteps">
<div class="ost" id="os0">{ico("up",14)} Screenshot upload</div>
<div class="ost" id="os1">{ico("search",14)} UTR verify</div>
<div class="ost" id="os2">{ico("shield",14)} Duplicate check</div>
<div class="ost" id="os3">{ico("check",14)} Admin ko bheja</div>
</div></div></div>

<style>
.drop{{border:2px dashed rgba(124,58,237,.4);border-radius:14px;
padding:26px 18px;text-align:center;cursor:pointer;
background:linear-gradient(160deg,rgba(124,58,237,.06),rgba(0,230,255,.03));
transition:.3s var(--ease)}}
.drop:hover{{border-color:var(--acc);background:rgba(124,58,237,.1);
box-shadow:0 0 30px var(--glow)}}
.drop.has{{border-style:solid;border-color:var(--ok);padding:10px}}
.dicon{{color:var(--acc3);margin-bottom:8px;animation:fl 2.6s ease-in-out infinite}}
@keyframes fl{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-6px)}}}}
.drop b{{display:block;font-size:14px;margin-bottom:3px}}
#prev{{max-width:100%;max-height:230px;border-radius:10px;display:block;
margin:0 auto;box-shadow:0 6px 26px rgba(0,0,0,.5)}}
.ovl{{position:fixed;inset:0;z-index:900;display:none;place-items:center;
background:rgba(7,11,20,.86);backdrop-filter:blur(9px);animation:fin .3s}}
.ovl.on{{display:grid}}
@keyframes fin{{from{{opacity:0}}}}
.obox{{text-align:center;padding:34px 30px;max-width:340px}}
.oring{{width:76px;height:76px;margin:0 auto 20px;position:relative}}
.oring i{{position:absolute;inset:0;border:2.5px solid transparent;
border-radius:50%;animation:spn 1.4s linear infinite}}
.oring i:nth-child(1){{border-top-color:#7C3AED}}
.oring i:nth-child(2){{border-right-color:#00E6FF;inset:9px;
animation-duration:1.9s;animation-direction:reverse}}
.oring i:nth-child(3){{border-bottom-color:#FF0080;inset:18px;
animation-duration:1.1s}}
@keyframes spn{{to{{transform:rotate(360deg)}}}}
.obox h3{{font-size:17px;margin-bottom:18px}}
.osteps{{display:flex;flex-direction:column;gap:9px;text-align:left}}
.ost{{display:flex;align-items:center;gap:9px;font-size:13px;
color:var(--dim3);padding:8px 13px;border-radius:9px;
background:rgba(255,255,255,.03);transition:.35s var(--ease)}}
.ost.on{{color:var(--txt);background:rgba(124,58,237,.16);
box-shadow:inset 0 0 0 1px rgba(124,58,237,.35)}}
.ost.done{{color:var(--ok);background:rgba(34,197,94,.1)}}
</style>
<script>
function shotPick(el){{
  var f=el.files[0]; if(!f) return;
  var d=document.getElementById('drop');
  var r=new FileReader();
  r.onload=function(e){{
    document.getElementById('dtxt').style.display='none';
    var p=document.getElementById('prev');
    p.src=e.target.result; p.style.display='block';
    d.classList.add('has');
  }};
  r.readAsDataURL(f);
}}
function payGo(){{
  document.getElementById('ovl').classList.add('on');
  document.getElementById('paybtn').disabled=true;
  var n=0;
  var t=setInterval(function(){{
    if(n>0) document.getElementById('os'+(n-1)).className='ost done';
    if(n<4) document.getElementById('os'+n).className='ost on';
    n++;
    if(n>4) clearInterval(t);
  }},520);
  return true;
}}
</script>
<div class="msg info mt">{ico("clock",15)}<div>
Verify hone me 5-30 minute lagte hain. Turant chahiye to
<a href="https://t.me/{theme.SUPPORT.lstrip('@')}"
style="color:var(--acc4);text-decoration:underline">Telegram par bolo</a>.
</div></div></div></div>"""
    return dash_page("Add Credits", f"1 ghanta = {CREDIT_RATE} credits",
                     content, u, "recharge")


def _vbadge(u):
    """✅ Email verify ho chuka hai ya nahi"""
    if u.get("verified"):
        return (f'<span class="bdg on" style="margin-left:7px;'
                f'font-size:10px">{ico("check",10)} VERIFIED</span>')
    return (f'<span class="bdg warn" style="margin-left:7px;'
            f'font-size:10px">{ico("info",10)} UNVERIFIED</span>')


def p_profile(u, msg=""):
    m = f'<div class="msg ok">{ico("check",15)}<div>{esc(msg)}</div></div>' if msg else ""
    pl = plan_of(u.get("plan") if u.get("plan") in
                 [p[0] for p in PLANS] else "starter")
    apps = db.user_apps(u["id"])
    content = f"""{m}<div class="grid g2">
<div class="card"><h3 class="mb2">{ico("user",18)} Details</h3>
<form method="POST" action="/profile">
<div class="fld"><label>Naam</label>
<input name="name" value="{esc(u['name'])}" required></div>
<div class="fld"><label>Email {_vbadge(u)}</label>
<input value="{esc(u['email'])}" disabled style="opacity:.55">
<div class="hint">Email badalne ke liye support se bolo</div></div>
<div class="fld"><label>Phone</label>
<input name="phone" value="{esc(u['phone'])}" placeholder="9876543210"></div>
<button class="btn btn-p">{ico("check",15)} Save karo</button></form></div>

<div class="card"><h3 class="mb2">{ico("key",18)} Password badlo</h3>
<form method="POST" action="/password">
<div class="fld"><label>Purana password</label>
<input name="old" type="password" required></div>
<div class="fld"><label>Naya password</label>
<input name="new" type="password" required minlength="8">
<div class="hint">{ico("lock",12)} Kam se kam 8 character</div></div>
<button class="btn btn-p">{ico("shield",15)} Update karo</button></form></div>
</div>

<div class="grid g4 mt">
<div class="stat"><div class="top"><span class="lbl">Plan</span>
<span class="ib p">{ico("star",15)}</span></div>
<div class="val" style="font-size:22px">{pl[1]}</div></div>
<div class="stat"><div class="top"><span class="lbl">Role</span>
<span class="ib y">{ico("crown",15)}</span></div>
<div class="val" style="font-size:22px">{u['role'].title()}</div></div>
<div class="stat"><div class="top"><span class="lbl">Servers</span>
<span class="ib">{ico("server",15)}</span></div>
<div class="val" style="font-size:22px">{len(apps)}</div></div>
<div class="stat"><div class="top"><span class="lbl">Member since</span>
<span class="ib c">{ico("clock",15)}</span></div>
<div class="val" style="font-size:22px">{ago(u['created_at'])}</div></div>
</div>"""
    return dash_page("Profile", "Apni details manage karo", content, u, "profile")


def p_support(u, msg=""):
    m = f'<div class="msg ok">{ico("check",15)}<div>{esc(msg)}</div></div>' if msg else ""
    ts = db.user_tickets(u["id"])
    rows = "".join(f"""<tr><td><b>{esc(t['subject'])}</b>
<div class="dim2 xs">{esc(t['message'][:60])}…</div></td>
<td><span class="bdg {'on' if t['status']=='closed' else 'wait'}">
{t['status']}</span></td><td class="dim">{ago(t['ts'])}</td>
<td class="dim">{esc(t['reply']) or '—'}</td></tr>"""
        for t in ts) or \
        '<tr><td colspan="4" class="dim tc" style="padding:26px">Koi ticket nahi</td></tr>'

    content = f"""{m}<div class="grid g32">
<div class="card"><h3 class="mb2">{ico("bolt",18)} Turant help</h3>
<p class="dim sm mb2">Telegram par seedha baat karo — 10 minute me jawab</p>
<a href="https://t.me/{theme.SUPPORT.lstrip('@')}" class="btn btn-p btn-b">
{ico("help",15)} Telegram Support</a>
<a href="https://t.me/{theme.CHANNEL}" class="btn btn-g btn-b mt2">
{ico("bell",15)} Updates Channel</a>
<div class="card flat mt2" style="background:var(--bg2)">
<div class="dim2 xs">RESPONSE TIME</div>
<div class="flex between mt2"><span class="sm">Telegram</span>
<b class="sm" style="color:#22C55E">~10 min</b></div>
<div class="flex between mt2"><span class="sm">Ticket</span>
<b class="sm" style="color:#8B5CF6">~2 hours</b></div></div></div>

<div class="card"><h3 class="mb2">{ico("ticket",18)} Naya ticket</h3>
<form method="POST" action="/support">
<div class="fld"><label>Subject</label>
<input name="subject" required maxlength="100"
placeholder="Server start nahi ho raha"></div>
<div class="fld"><label>Problem detail me batao</label>
<textarea name="message" required maxlength="2000"
placeholder="Kya problem aa rahi hai, kab se, kya try kiya…"></textarea></div>
<button class="btn btn-p">{ico("check",15)} Ticket bhejo</button></form></div>
</div>
<div class="tbl mt"><div class="th"><h3>{ico("ticket",17)} Mere tickets</h3></div>
<table><thead><tr><th>Subject</th><th>Status</th><th>When</th>
<th>Reply</th></tr></thead><tbody>{rows}</tbody></table></div>"""
    return dash_page("Support", "Help chahiye? Hum yahan hain", content, u, "support")


def p_admin(u, msg=""):
    # 🔐 Guard = ADMIN_PASS (route par check hota hai), role nahi
    s = db.stats()
    m = f'<div class="msg ok">{ico("check",15)}<div>{esc(msg)}</div></div>' if msg else ""
    try:
        _fgs = famgateway_pay.admin_state()
    except Exception:
        _fgs = {"enabled": False, "key_configured": False}
    _fgbadge = ("🟢 ON" if _fgs["enabled"] else "🔴 OFF")
    _fgkey = ("✅ API key set" if _fgs["key_configured"] else "⚠️ API key missing")
    _fgcard = f"""<div class="card mb" style="border-color:rgba(56,189,248,.35)">
<div class="flex between mb2"><h3>🏦 FamGateway Auto Payment</h3>
<span class="bdg {'on' if _fgs['enabled'] and _fgs['key_configured'] else 'wait'}">{_fgbadge}</span></div>
<p class="dim sm">Status: {_fgkey}. API key server-side store hoti hai; page/browser me wapas display nahi hoti.</p>
<form method="POST" action="/admin/famgateway">
<div class="fld"><label>FamGateway Merchant API Key (nayi key paste karein; blank = existing key rakhein)</label>
<input type="password" name="famgateway_api_key" autocomplete="new-password" placeholder="API key yahan paste karein"></div>
<div class="fld"><label>Auto-pay mode</label><select name="famgateway_enabled">
<option value="1" {'selected' if _fgs['enabled'] else ''}>ON — dynamic QR + automatic verification</option>
<option value="0" {'selected' if not _fgs['enabled'] else ''}>OFF — existing manual payment flow</option></select></div>
<button class="btn btn-p btn-sm" type="submit">💾 Save & Apply Now</button>
</form></div>"""
    users = db.all_users(30)
    pend = db.pending_payments()
    tickets = db.all_tickets()[:8]

    # ⚠️ data-l = mobile pe card banane ke liye (table kat jati thi)
    def _urow(x):
        ban = bool(x.get("banned"))
        ver = bool(x.get("verified"))
        adm = x["role"] == "admin"
        tags = [f'<span class="bdg {"vip" if adm else "info"}">'
                f'{x["role"]}</span>']
        if ban:
            tags.append('<span class="bdg err">BANNED</span>')
        elif not ver:
            tags.append('<span class="bdg warn">unverified</span>')
        acts = (f'<a href="/admin/credit/{x["id"]}" '
                f'class="btn btn-g btn-sm">{ico("plus",13)} 100</a>')
        if not adm:
            if ban:
                acts += (f'<a href="/admin/unban/{x["id"]}" '
                         f'class="btn btn-g btn-sm">'
                         f'{ico("check",13)} Unban</a>')
            else:
                acts += (f'<a href="/admin/ban/{x["id"]}" '
                         f'class="btn btn-d btn-sm" '
                         f'onclick="return confirm('
                         f'\'{esc(x["email"])} ko ban karna hai? '
                         f'Wo login nahi kar payega.\')">'
                         f'{ico("x",13)} Ban</a>')
        return (f'<tr><td data-l="User"><b>{esc(x["name"])}</b>'
                f'<div class="dim2 xs">{esc(x["email"])}</div></td>'
                f'<td data-l="Credits"><b>{x["credits"]:.0f}</b></td>'
                f'<td data-l="Status">{"".join(tags)}</td>'
                f'<td data-l="Joined" class="dim">'
                f'{ago(x["created_at"])}</td>'
                f'<td data-l="Kaam"><div class="flex" '
                f'style="gap:6px;flex-wrap:wrap">{acts}</div></td></tr>')

    urows = "".join(_urow(x) for x in users)

    def _shotcell(p):
        sh = p.get("shot") or ""
        if not sh:
            return f'<span class="bdg err nd">{ico("x",11)} nahi</span>'
        return (f'<a href="/admin/shot/{esc(p["ref"])}" target="_blank" '
                f'class="shotlnk" title="Bada karke dekho">'
                f'<img src="/admin/shot/{esc(p["ref"])}" loading="lazy">'
                f'<span>{ico("eye",12)} dekho</span></a>')

    prows = "".join(f"""<tr><td><code>{esc(p['ref'])}</code></td>
<td><b>{esc(p['name'])}</b><div class="dim2 xs">{esc(p['email'])}</div></td>
<td><b>{money(p['rupees'])}</b></td><td>{p['credits']} cr</td>
<td><code>{esc(p['utr'])}</code></td>
<td>{_shotcell(p)}</td>
<td><div class="flex" style="gap:6px">
<a href="/admin/pay/{esc(p['ref'])}/ok" class="btn btn-ok btn-sm">
{ico("check",13)}</a>
<a href="/admin/pay/{esc(p['ref'])}/no" class="btn btn-d btn-sm">
{ico("x",13)}</a></div></td></tr>""" for p in pend) or \
        f'<tr><td colspan="6" class="dim tc" style="padding:26px">{ico("check",15)} Koi pending nahi</td></tr>'

    trows = "".join(f"""<tr><td><b>{esc(t['name'])}</b></td>
<td>{esc(t['subject'])}</td>
<td><span class="bdg {'on' if t['status']=='closed' else 'wait'}">
{t['status']}</span></td><td class="dim">{ago(t['ts'])}</td></tr>"""
        for t in tickets) or \
        '<tr><td colspan="4" class="dim tc" style="padding:26px">Koi ticket nahi</td></tr>'

    # 🔗 shortener + free server status
    sok, smsg = unlock.short_test()
    ust = unlock.stats()
    blk = unlock.all_black()
    brows = "".join(f"""<tr><td><code>#{b['uid']}</code></td>
<td class="dim">{esc(b.get('reason','')[:52])}</td>
<td class="dim2 xs">{ago(b.get('at',0))}</td>
<td><a href="/admin/unblack/{b['uid']}" class="btn btn-ok btn-sm">
{ico("check",13)} Free</a></td></tr>""" for b in blk[:10]) or \
        '<tr><td colspan="4" class="dim tc" style="padding:22px">Koi blacklist nahi ✅</td></tr>'

    # ⚠️ PYTHON 3.11 FIX — f-string ke ANDAR dobara f-string nahi likh sakte
    #    (PEP 701 sirf 3.12+ me hai). Render 3.11 pe SyntaxError deta tha:
    #        SyntaxError: invalid character '—' (U+2014)
    #    Isliye ye do nested block yahan bahar nikaal diye hain.
    _oldu = ""
    if tunnel.old_hosts():
        _rows = "".join(f'<div class="oldu">{esc(o[:52])}'
                        f'<span>{tunnel.stale_hits().get(o, 0)} hits</span>'
                        f'</div>'
                        for o in tunnel.old_hosts()[-4:])
        _oldu = (f'<div class="mt2"><div class="dim2 xs">'
                 f'{ico("refresh", 11)} PURANE URL — inse aane wale '
                 f'auto-redirect honge ({len(tunnel.old_hosts())})</div>'
                 f'{_rows}</div>')

    _bl = botlink.status()
    if _bl['bot_username']:
        _bot = (f'<table>'
                f'<tr><td class="dim">Bot</td>'
                f'<td><b>@{esc(_bl["bot_username"])}</b></td></tr>'
                f'<tr><td class="dim">Bot users</td>'
                f'<td>{_bl["bot_users"]}</td></tr>'
                f'<tr><td class="dim">Aakhri baar</td>'
                f'<td class="dim2">{ago(_bl["bot"]["at"])}</td></tr>'
                f'</table>')
    else:
        _bot = ('<p class="dim sm">Bot abhi connect nahi hua. '
                'Bot chalte hi yahan dikhega.</p>')

    extra = f"""<div class="grid g2 mb">
<div class="card"><div class="flex between mb2">
<h3>{ico("globe",17)} {unlock.SHORTENER['name']}</h3>
<span class="bdg {'on' if sok else 'err'}">{'LIVE' if sok else 'DOWN'}</span>
</div>
<table><tr><td class="dim">Domain</td>
<td><code>{unlock.SHORTENER['domain']}</code></td></tr>
<tr><td class="dim">API key</td>
<td><code>{unlock.SHORTENER['api'][:10]}…{unlock.SHORTENER['api'][-4:]}</code></td></tr>
<tr><td class="dim">Test</td><td class="{'dim' if sok else ''}"
style="{'color:#FF6B8A' if not sok else ''}">{esc(str(smsg)[:44])}</td></tr>
<tr><td class="dim">Min wait</td><td>{unlock.STEP_MIN_SEC}s</td></tr>
</table>
<a href="/admin/shorttest" class="btn btn-g btn-sm mt2">
{ico("refresh",13)} Dobara test</a></div>

<div class="card"><div class="flex between mb2">
<h3>{ico("globe",17)} Public Tunnel</h3>
<span class="bdg {'on' if tunnel.url() else 'off'}">
{'LIVE' if tunnel.url() else 'OFF'}</span></div>
{f'<div class="linkbox2">{esc(tunnel.url())}</div>' if tunnel.url() else
 '<p class="dim sm">Localhost par shortener nahi chalta. Tunnel on karo — '
 'ek public URL milega, phir EarnLinks bhi chalegi.</p>'}
<div class="flex mt2">
<a href="/admin/tunnel/{'off' if tunnel.url() else 'on'}"
class="btn {'btn-d' if tunnel.url() else 'btn-p'} btn-sm">
{ico('stop' if tunnel.url() else 'play',13)}
{'Band karo' if tunnel.url() else 'Chalu karo'}</a>
<a href="/admin" class="btn btn-g btn-sm">{ico("refresh",13)}</a></div>
<p class="dim2 xs mt2">{esc(tunnel.status()['kind'] or 'cloudflare / ssh')}
— auto-restart on, URL badle to sab khud update</p>
{_oldu}</div>

<div class="card" style="border-color:rgba(0,230,255,.3)">
<div class="flex between mb2">
<h3>{ico("bell",17)} JARVIS Voice Control</h3>
<span class="bdg on">READY</span></div>
<p class="s">Mic dabao (ya <b>Ctrl+Space</b>) aur bolo — JARVIS kaam
kar dega.</p>
<div class="jvsw mt2">
<div class="jvs {'on' if vcmd.free_open() else 'off'}">
<b>Free service</b><span>{'CHALU' if vcmd.free_open() else 'BAND'}</span>
<a href="/admin/flag/free/{'0' if vcmd.free_open() else '1'}"
class="btn btn-g btn-sm">{'Band karo' if vcmd.free_open() else 'Chalu karo'}</a>
</div>
<div class="jvs {'on' if vcmd.signup_open() else 'off'}">
<b>Naye signup</b><span>{'CHALU' if vcmd.signup_open() else 'BAND'}</span>
<a href="/admin/flag/signup/{'0' if vcmd.signup_open() else '1'}"
class="btn btn-g btn-sm">{'Band karo' if vcmd.signup_open() else 'Chalu karo'}</a>
</div>
<div class="jvs {'off' if vcmd.maintenance() else 'on'}">
<b>Maintenance</b><span>{'ON' if vcmd.maintenance() else 'OFF'}</span>
<a href="/admin/flag/maint/{'0' if vcmd.maintenance() else '1'}"
class="btn btn-g btn-sm">{'Hatao' if vcmd.maintenance() else 'Lagao'}</a>
</div></div>
<div class="mt2"><div class="dim2 xs">BOL KAR TRY KARO</div>
{"".join(f'<div class="jvc"><b>{esc(c)}</b><span>{esc(d)}</span></div>'
         for c, d in vcmd.HELP_TEXT[:6])}</div>
{f'''<div class="mt2"><div class="dim2 xs">PICHHLE COMMANDS</div>
{"".join(f"<div class=jvl><span>{esc(x['cmd'])}</span>"
         f"<i>{esc(x['res'])}</i></div>" for x in vcmd.history(5))}</div>'''
 if vcmd.history(1) else ""}
<style>
.jvsw{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
gap:8px}}
.jvs{{padding:10px 12px;border-radius:10px;background:rgba(255,255,255,.03);
border:1px solid var(--line)}}
.jvs.on{{border-color:rgba(34,197,94,.35)}}
.jvs.off{{border-color:rgba(239,68,68,.35)}}
.jvs b{{display:block;font-size:12.5px;margin-bottom:2px}}
.jvs span{{display:block;font-size:10.5px;letter-spacing:1px;
font-weight:700;margin-bottom:7px}}
.jvs.on span{{color:var(--ok)}}
.jvs.off span{{color:var(--err)}}
.jvc{{display:flex;flex-direction:column;padding:6px 10px;margin-top:4px;
border-radius:8px;background:rgba(0,230,255,.05);
border-left:2px solid rgba(0,230,255,.4)}}
.jvc b{{font-size:12px;color:var(--cy);font-weight:600}}
.jvc span{{font-size:10.5px;color:var(--dim2)}}
.jvl{{display:flex;justify-content:space-between;gap:9px;font-size:11px;
padding:4px 8px;margin-top:3px;border-radius:6px;
background:rgba(255,255,255,.025)}}
.jvl span{{color:var(--dim);overflow:hidden;text-overflow:ellipsis;
white-space:nowrap}}
.jvl i{{font-style:normal;color:var(--acc4);white-space:nowrap}}
</style></div>

<div class="card"><div class="flex between mb2">
<h3>{ico("bolt",17)} Bot Link</h3>
<span class="bdg {'on' if botlink.bot_online() else ('wait' if botlink.status()['url'] else 'off')}">
{'LIVE' if botlink.bot_online() else ('PUBLISHED' if botlink.status()['url'] else 'OFF')}</span></div>
{_bot}
<div class="mt2"><div class="dim2 xs">WEBSITE URL (bot ise padhta hai)</div>
{f'<div class="linkbox2">{esc(botlink.status()["url"])}</div>'
 if botlink.status()["url"] else
 '<p class="dim sm">Tunnel on karo — URL apne aap publish ho jayega.</p>'}
</div>
<p class="dim2 xs mt2">{ico("check",11)} URL badalte hi bot ko turant pata
chal jata hai — {botlink.status()['pushes']} baar bheja gaya
{f"· {botlink.status()['fails']} fail" if botlink.status()['fails'] else ""}
</p>
<a href="/admin/botpush" class="btn btn-g btn-sm mt2">
{ico("refresh",13)} Abhi bhejo</a></div>

<div class="card"><div class="flex between mb2">
<h3>{ico("db",17)} Cloud Backup</h3>
<span class="bdg {'on' if cloudsync.configured() and cloudsync._ok else 'err'}">
{'LIVE' if cloudsync.configured() and cloudsync._ok else 'OFF'}</span></div>
{_cloud_rows()}
<div class="flex mt2">
<a href="/admin/cloudpush" class="btn btn-p btn-sm">
{ico("up2",13)} Abhi backup</a>
<a href="/admin/cloudtest" class="btn btn-g btn-sm">
{ico("refresh",13)} Test</a></div></div>

<div class="card"><h3 class="mb2">{ico("gift",17)} Free Server Stock</h3>
<div class="flex between"><span class="dim sm">Bache hain</span>
<b style="color:{'#22C55E' if ust['left'] else '#FF6B8A'}">
{ust['left']} / {ust['total']}</b></div>
{bar(ust['percent'])}
<div class="grid g3 mt2" style="gap:8px">
<div><div class="dim2 xs">CLAIMED</div><b>{ust['claimed']}</b></div>
<div><div class="dim2 xs">PENDING</div><b>{ust['pending']}</b></div>
<div><div class="dim2 xs">BLACKLIST</div>
<b style="color:#FF6B8A">{ust['black']}</b></div></div>
<form method="POST" action="/admin/stock" class="flex mt2">
<input name="n" type="number" min="0" max="9999" value="{ust['total']}"
style="flex:1;padding:8px 11px;background:var(--bg2);
border:1px solid var(--line2);border-radius:8px;color:var(--txt)">
<button class="btn btn-p btn-sm">Set</button></form></div></div>

<div class="tbl mb"><div class="th">
<h3>{ico("shield",17)} Blacklist</h3>
<span class="bdg {'err' if blk else 'on'}">{len(blk)}</span></div>
<table><thead><tr><th>User</th><th>Wajah</th><th>Kab</th>
<th>Action</th></tr></thead><tbody>{brows}</tbody></table></div>"""

    content = f"""{m}{_fgcard}{extra}<div class="grid g4 mb">
<div class="stat"><div class="top"><span class="lbl">Users</span>
<span class="ib">{ico("user",15)}</span></div>
<div class="val">{s['users']}</div>
<div class="chart">{minibars([2,4,3,6,5,8,s['users'] or 1],110,28,"#00E6FF")}</div>
</div>
<div class="stat"><div class="top"><span class="lbl">Servers</span>
<span class="ib p">{ico("server",15)}</span></div>
<div class="val">{s['apps']}</div>
<div class="sub"><span class="up">{s['running']} running</span></div></div>
<div class="stat"><div class="top"><span class="lbl">Revenue</span>
<span class="ib g">{ico("up2",15)}</span></div>
<div class="val" style="font-size:25px">{money(s['revenue'])}</div>
<div class="chart">{sparkline([100,240,180,420,380,600,s['revenue'] or 1],
110,28,"#22C55E",sid="a1")}</div></div>
<div class="stat"><div class="top"><span class="lbl">Pending</span>
<span class="ib y">{ico("clock",15)}</span></div>
<div class="val" style="color:{'#8B5CF6' if s['pending'] else 'inherit'}">
{s['pending']}</div>
<div class="sub">{s['tickets']} open tickets</div></div></div>

<div class="tbl mb"><div class="th">
<h3>{ico("card",17)} Pending Payments</h3>
<span class="bdg wait">{len(pend)} waiting</span></div>
<table><thead><tr><th>Ref</th><th>User</th><th>Amount</th><th>Credits</th>
<th>UTR</th><th>Screenshot</th><th>Action</th></tr></thead>
<tbody>{prows}</tbody></table></div>
<style>
.shotlnk{{display:inline-flex;align-items:center;gap:7px;padding:3px;
border-radius:8px;border:1px solid rgba(124,58,237,.3);
transition:.25s var(--ease)}}
.shotlnk:hover{{border-color:var(--acc);box-shadow:0 0 18px var(--glow);
transform:scale(1.04)}}
.shotlnk img{{width:42px;height:42px;object-fit:cover;border-radius:6px;
display:block}}
.shotlnk span{{font-size:11.5px;color:var(--acc4);padding-right:7px}}
</style>

<div class="grid g2">
<div class="tbl"><div class="th"><h3>{ico("user",17)} Users</h3></div>
<table><thead><tr><th>User</th><th>Credits</th><th>Role</th><th>Joined</th>
<th></th></tr></thead><tbody>{urows}</tbody></table></div>
<div class="tbl"><div class="th"><h3>{ico("ticket",17)} Tickets</h3></div>
<table><thead><tr><th>User</th><th>Subject</th><th>Status</th>
<th>When</th></tr></thead><tbody>{trows}</tbody></table></div></div>"""
    return dash_page("Admin Panel", "Sab kuch ek jagah", content, u, "admin")


def on_tunnel_change(new_url, old_url):
    """
    🔄 Tunnel ka URL badla — sab kuch auto-update:
      1. Pending short links naye URL se dobara
      2. Purana host redirect list me (server.py khud handle karta hai)
      3. Cloud par save
    """
    print(f"\n  🔄 TUNNEL URL BADLA", flush=True)
    if old_url:
        print(f"     purana: {old_url}", flush=True)
    print(f"     naya  : {new_url}", flush=True)
    try:
        done, fail = unlock.rebuild_pending(new_url, old_url)
        if done or fail:
            print(f"     🔗 {done} link naye se bane"
                  f"{f', {fail} fail' if fail else ''}", flush=True)
    except Exception as e:
        print(f"     rebuild fail: {e}", flush=True)
    try:
        cloudsync.push_db(force=True)
    except Exception:
        pass
    # 🤖 BOT ko naya URL batao — bot ka link kabhi na toote
    try:
        if botlink.on_tunnel_change(new_url, old_url):
            print("     🤖 bot ko naya URL bata diya", flush=True)
    except Exception as e:
        print(f"     bot sync fail: {str(e)[:50]}", flush=True)
    print(f"     ✅ purane URL wale users apne aap naye par jayenge\n",
          flush=True)


def _cloud_rows():
    st = cloudsync.status_text()
    m = cloudsync.meta()
    last = m.get("at", 0)
    ago_s = "kabhi nahi"
    if last:
        d = int(time.time()) - last
        ago_s = f"{d}s pehle" if d < 60 else f"{d//60}m pehle"
    return (f'<table>'
            f'<tr><td class="dim">Server</td>'
            f'<td><code>{esc(st["endpoint"][:34])}</code></td></tr>'
            f'<tr><td class="dim">Platform</td><td>{st["platform"]}'
            f'{" (ephemeral)" if st["ephemeral"] else ""}</td></tr>'
            f'<tr><td class="dim">Last backup</td><td>{ago_s}</td></tr>'
            f'<tr><td class="dim">Size</td>'
            f'<td>{m.get("size",0)//1024} KB</td></tr>'
            f'<tr><td class="dim">Auto</td><td>DB 60s · files 5min</td></tr>'
            f'</table>')


def _closed_page(u, title, msg):
    body = f"""<div class="auth"><div class="box tc">
<div style="font-size:52px">🚫</div>
<h2>{esc(title)}</h2>
<p class="s">{esc(msg)}</p>
<div class="flex mt" style="justify-content:center;gap:9px">
<a href="/dashboard" class="btn btn-g">Dashboard</a>
<a href="/recharge" class="btn btn-p">Credits lo</a></div>
</div></div>"""
    return page(esc(title), body, u)


BANNED_HTML = ('<div class="auth"><div class="box tc">'
               '<div style="font-size:52px">&#128683;</div>'
               '<h2>Account band kar diya gaya</h2>'
               '<p class="s">Niyam todne par aapka account band '
               'kar diya gaya hai. Ab aap login nahi kar sakte.</p>'
               '<p class="dim2 xs" style="margin-top:16px">'
               'Galti se hua lagta hai? Telegram par baat karo: '
               '@UjjawalXsarkar</p>'
               '<a href="/logout" class="btn btn-g mt">Logout</a>'
               '</div></div>')

MAINT_DENY_HTML = ('<div class="auth"><div class="box tc"><div style="font-size:48px">LOCK</div><h2>Galat password</h2><p class="s">Sahi tareeka: /maintenance-off?pass=AAPKA_PASSWORD</p></div></div>')

MAINT_OK_HTML = ('<div class="auth"><div class="box tc"><div style="font-size:56px">&#9989;</div><h2>Website wapas LIVE hai</h2><p class="s">Maintenance mode hata diya gaya.</p><a href="/" class="btn btn-p mt">Website kholo</a><a href="/admin" class="btn btn-g btn-sm mt2">Admin panel</a></div></div>')


def _maint_page():
    """
    Maintenance ka page.

    Neeche ADMIN ka link ZAROORI hai. Ek baar aisa hua ki
    maintenance on karke website "phas gayi" lagi, kyunki page
    pe nikalne ka koi raasta hi nahi dikh raha tha. (Asal me
    /admin tab bhi khulta tha - bas pata nahi chalta tha.)
    Ab link saamne hai.
    """
    return page("Maintenance", f"""<div class="auth"><div class="box tc">
<div style="font-size:56px">🛠</div>
<h2>Thodi der ka break</h2>
<p class="s">Hum kuch sudhaar kar rahe hain. Bahut jaldi wapas aayenge.</p>
<div class="mt2"><span class="bdg wait">MAINTENANCE MODE</span></div>
<p class="dim2 xs mt2">— RAVAN X HOSTING TEAM</p>
<div style="margin-top:26px;padding-top:18px;
border-top:1px solid var(--line)">
<a href="/admin" class="btn btn-g btn-sm">{ico("crown",14)}
Admin - maintenance hatao</a>
<p class="dim2 xs mt2">Malik ho? Yahan se andar aa jao.</p>
</div>
</div></div>""")


def public_base(handler):
    """
    Asli public URL — priority:
      1. DOMAIN / PUBLIC_URL env  (aapka apna domain — sabse upar)
      2. Tunnel (agar domain nahi hai)
      3. Render/Railway ka apna domain
      4. Host header
    """
    # 🌐 Apna domain mil gaya? Tunnel ki zarurat hi nahi
    for k in ("DOMAIN", "PUBLIC_URL", "SITE_URL"):
        v = os.environ.get(k, "").strip()
        if v:
            v = v.rstrip("/")
            return v if v.startswith("http") else f"https://{v}"
    t = tunnel.url()
    if t:
        return t.rstrip("/")
    # Render/Railway apna domain dete hain
    for k in ("RENDER_EXTERNAL_URL", "RAILWAY_PUBLIC_DOMAIN"):
        v = os.environ.get(k, "").strip()
        if v:
            return v if v.startswith("http") else f"https://{v}"
    host = handler.headers.get("Host", f"localhost:{PORT}")
    proto = "https" if handler.headers.get(
        "X-Forwarded-Proto") == "https" else "http"
    return f"{proto}://{host}"


# ══════════════════════════════════════════════
#   ADMIN LOCK
# ══════════════════════════════════════════════

ADMIN_OK = {}        # token -> expires
ADMIN_TRY = {}       # ip -> [count, until]


def admin_unlocked(tok):
    return bool(tok) and ADMIN_OK.get(tok, 0) > time.time()


def admin_unlock(tok, hours=6):
    ADMIN_OK[tok] = time.time() + hours * 3600


def admin_blocked(ip):
    c, until = ADMIN_TRY.get(ip, (0, 0))
    return until > time.time()


def admin_fail(ip):
    c, until = ADMIN_TRY.get(ip, (0, 0))
    c += 1
    if c >= 5:
        ADMIN_TRY[ip] = (0, time.time() + 600)
        return True
    ADMIN_TRY[ip] = (c, 0)
    return False


# ══════════════════════════════════════════════
#   MULTIPART UPLOAD (bina library ke)
# ══════════════════════════════════════════════

class MultipartStream:
    """
    ♾️ Multipart body ko STREAM karke padhta hai — poori file kabhi
    RAM me nahi aati. Isliye 5 GB ki file bhi upload ho jayegi.

    Ek hi buffer poore body ke liye, isliye text fields + file
    kisi bhi order me ho, sab sahi padha jayega.
    """

    def __init__(self, rf, headers):
        ctype = headers.get("Content-Type", "")
        m = re.search(r'boundary=(?:"([^"]+)"|([^;\s]+))', ctype)
        self.ok = bool(m)
        self.rf = rf
        self.b = ((m.group(1) or m.group(2)).encode() if m else b"--none--")
        self.sep = b"--" + self.b
        self.term = b"\r\n" + self.sep
        self.left = int(headers.get("Content-Length", 0) or 0)
        self.buf = b""
        self.eof = False
        self.fields = {}

    # ── low level ──
    def _pull(self, n=65536):
        if self.eof:
            return False
        want = min(n, self.left) if self.left else 0
        if want <= 0:
            self.eof = True
            return False
        d = self.rf.read(want)
        if not d:
            self.eof = True
            return False
        self.left -= len(d)
        self.buf += d
        return True

    def _line(self):
        while b"\r\n" not in self.buf:
            if not self._pull():
                ln, self.buf = self.buf, b""
                return ln
        i = self.buf.index(b"\r\n")
        ln, self.buf = self.buf[:i], self.buf[i + 2:]
        return ln

    def _seek_boundary(self):
        for _ in range(4000):
            ln = self._line()
            if ln.startswith(self.sep):
                return not ln.startswith(self.sep + b"--")
            if not ln and self.eof:
                return False
        return False

    def _part_headers(self):
        """(name, filename) — part khatam ho to (None, None)."""
        head = []
        for _ in range(50):
            ln = self._line()
            if ln == b"":
                break
            head.append(ln.decode("utf-8", "ignore"))
            if self.eof and not self.buf:
                break
        if not head:
            return None, None
        h = "\n".join(head)
        nm = re.search(r'name="([^"]*)"', h)
        fm = re.search(r'filename="([^"]*)"', h)
        return (nm.group(1) if nm else ""), (fm.group(1) if fm else "")

    # ── part body ──
    def read(self, n=65536):
        """Chalu part ka agla tukda. Part khatam = b''."""
        if getattr(self, "_pdone", True):
            return b""
        n = max(1, int(n))
        keep = len(self.term) + 2
        while True:
            i = self.buf.find(self.term)
            if i >= 0:
                out = self.buf[:i]
                self.buf = self.buf[i + 2:]      # \r\n hata, sep chhoda
                self._pdone = True
                return out
            if len(self.buf) > keep + n:
                out, self.buf = self.buf[:n], self.buf[n:]
                return out
            if not self._pull(max(65536, n)):
                out, self.buf = self.buf, b""
                self._pdone = True
                return out

    def _drain_text(self, limit=200000):
        v = b""
        while True:
            c = self.read(65536)
            if not c:
                break
            if len(v) < limit:
                v += c
        return v.decode("utf-8", "ignore").strip()

    def finish(self, limit=60):
        """File ke baad ke text fields bhi padh lo (folder wagaira)."""
        if not self.ok:
            return self.fields
        for _ in range(limit):
            if not self._pdone:
                self._drain_text(0)
            ln = self._line()
            if not ln or ln.startswith(self.sep + b"--"):
                break
            name, fname = self._part_headers()
            if name is None:
                break
            self._pdone = False
            if fname:
                self._drain_text(0)
            else:
                self.fields[name] = self._drain_text()
        return self.fields

    def next_file(self, want="file"):
        """
        Aage badhte raho jab tak file part na mile.
        Text fields raste me self.fields me bharte jao.
        Return: filename ya None (phir self.read() se data lo).
        """
        if not self.ok:
            return None
        if not self._seek_boundary():
            return None
        for _ in range(60):
            name, fname = self._part_headers()
            if name is None:
                return None
            self._pdone = False
            if fname:
                if want in (None, "", name):
                    return os.path.basename(fname)
                self._drain_text(0)
            else:
                self.fields[name] = self._drain_text()
            # is part ke baad boundary line nigal jao
            ln = self._line()
            if ln.startswith(self.sep + b"--"):
                return None
        return None


def parse_multipart(headers, body):
    """(filename, data) — simple multipart/form-data parser."""
    ctype = headers.get("Content-Type", "")
    m = re.search(r'boundary=(?:"([^"]+)"|([^;\s]+))', ctype)
    if not m:
        return None, None
    b = (m.group(1) or m.group(2)).encode()
    parts = body.split(b"--" + b)
    for part in parts:
        if b'name="file"' not in part:
            continue
        hi = part.find(b"\r\n\r\n")
        if hi < 0:
            continue
        head = part[:hi].decode("utf-8", "ignore")
        data = part[hi + 4:]
        if data.endswith(b"\r\n"):
            data = data[:-2]
        fm = re.search(r'filename="([^"]*)"', head)
        fn = fm.group(1) if fm else ""
        if not fn:
            return None, None
        return os.path.basename(fn), data
    return None, None


# ══════════════════════════════════════════════
#   BILLING LOOP — har ghante credits kaato
# ══════════════════════════════════════════════

def billing_loop():
    """Har live server ke CREDIT_RATE credits/ghanta."""
    import threading
    while True:
        try:
            time.sleep(300)          # har 5 min
            c = db.conn()
            rows = c.execute("SELECT * FROM apps WHERE status='running'").fetchall()
            c.close()
            for a in rows:
                sid = a["id"]
                if not engine.is_running(sid):
                    db.update_app(sid, status="stopped")
                    continue
                usr = db.get_user(a["user_id"])
                if not usr:
                    continue
                # 5 min = 1/12 ghanta
                cost = CREDIT_RATE / 12.0
                if usr["credits"] < cost:
                    engine.stop(sid)
                    engine.log(sid, "💸 Credits khatam — server band", "err")
                    db.update_app(sid, status="stopped")
                    continue
                db.add_credits(a["user_id"], -cost, f"Hosting: {a['name']}")
        except Exception:
            time.sleep(60)


# ══════════════════════════════════════════════
#   HTTP HANDLER
# ══════════════════════════════════════════════

class App(BaseHTTPRequestHandler):
    server_version = "RavanX/1.0"

    def log_message(self, fmt, *args):
        pass    # chup raho

    # ── helpers ──
    def _user(self):
        ck = http.cookies.SimpleCookie(self.headers.get("Cookie", ""))
        tok = ck["rx_session"].value if "rx_session" in ck else None
        return db.session_user(tok)

    def _send(self, body, code=200, ctype="text/html; charset=utf-8",
              cookie=None, redirect=None):
        data = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        if redirect:
            self.send_header("Location", redirect)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()
        try:
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _go(self, url):
        self._send("", 302, redirect=url)

    def _form(self):
        n = int(self.headers.get("Content-Length", 0) or 0)
        if n <= 0 or n > 1_000_000:
            return {}
        raw = self.rfile.read(n).decode("utf-8", "ignore")
        return {k: v[0] for k, v in urllib.parse.parse_qs(raw).items()}

    def _ip(self):
        return self.client_address[0] if self.client_address else ""

    # ══════════ STORAGE API ══════════
    def _sj(self, obj, code=200):
        return self._send(json.dumps(obj, ensure_ascii=False), code,
                          ctype="application/json")

    def _storage_api(self, method, path, q):
        """
        Token wali API — bot, script, curl, kahin se bhi.
        Auth: Authorization: Bearer <token>  ya  ?token=<token>
        """
        p = path[len("/api/storage"):].rstrip("/") or "/"

        if p == "/register" and method == "POST":
            n = int(self.headers.get("Content-Length", 0) or 0)
            try:
                d = json.loads(self.rfile.read(min(n, 4096)) or b"{}")
            except Exception:
                d = {}
            acc, err = storage.register(d.get("name", ""),
                                        d.get("password", ""))
            if not acc:
                return self._sj({"ok": False, "error": err}, 400)
            return self._sj({"ok": True, **acc})

        if p == "/stats":
            return self._sj({"ok": True, **storage.stats()})

        tok = self.headers.get("Authorization", "")
        if tok.lower().startswith("bearer "):
            tok = tok[7:]
        tok = tok.strip() or q.get("token", "")
        a = storage.by_token(tok)
        if not a:
            return self._sj({"ok": False, "error": "Galat token"}, 401)
        aid = a["id"]

        if p == "/me":
            q = storage.quota_info(aid)
            return self._sj({"ok": True, "name": a["name"],
                             "created": a["created"],
                             "last_seen": a["last_seen"], **q})

        if p == "/files":
            fl = storage.list_files(aid, q.get("prefix", ""))
            return self._sj({"ok": True, "count": len(fl), "files": fl})

        if p == "/logs":
            return self._sj({"ok": True, "logs": storage.logs(aid, 80)})

        if p == "/upload" and method == "POST":
            rel = q.get("path", "")
            if not rel:
                self._drain(50 * 1024 * 1024)
                return self._sj({"ok": False, "error": "?path= chahiye"}, 400)
            total = int(self.headers.get("Content-Length", 0) or 0)
            # 📏 Plan quota — body padhne se PEHLE hi mana kar do
            qq = storage.quota_info(aid)
            if total and total > qq["left"]:
                old = 0
                try:
                    cc = storage.conn()
                    r0 = cc.execute("SELECT size FROM blobs WHERE acct=? AND "
                                    "path=? AND deleted=0",
                                    (aid, storage.clean_rel(rel))).fetchone()
                    cc.close()
                    old = r0["size"] if r0 else 0
                except Exception:
                    pass
                if total > qq["left"] + old:
                    nx = theme.next_plan(qq["plan"])
                    em = (f"Jagah kam hai — {qq['plan'].title()} plan me "
                          f"{qq['cap_h']} milta hai, {qq['left_h']} bacha "
                          f"hai. File {storage.human(total)} ki hai.")
                    if nx:
                        em += (f" {nx.title()} plan lo "
                               f"({theme.storage_gb(nx)} GB) ya purani "
                               f"files hatao.")
                    self._drain(50 * 1024 * 1024)
                    return self._sj({"ok": False, "error": em,
                                     "quota": qq}, 413)
            ct = self.headers.get("Content-Type", "")
            if "multipart/form-data" in ct:
                mp = MultipartStream(self.rfile, self.headers)
                if not mp.next_file("file"):
                    return self._sj({"ok": False, "error": "File nahi mili"}, 400)
                res, err = storage.save_stream(aid, rel, mp)
            else:
                res, err = storage.save_stream(aid, rel, self.rfile, total)
            if not res:
                return self._sj({"ok": False, "error": err}, 400)
            return self._sj({"ok": True, **res})

        if p == "/file":
            fp, sz, ct = storage.open_file(aid, q.get("path", ""))
            if not fp:
                return self._sj({"ok": False, "error": "File nahi mili"}, 404)
            storage._stats["down"] += 1
            return self._stream_file(fp, sz, ct)

        if p == "/kv":
            k = q.get("key", "")
            if method == "POST":
                if not k:
                    return self._sj({"ok": False, "error": "?key= chahiye"}, 400)
                n = int(self.headers.get("Content-Length", 0) or 0)
                v = self.rfile.read(n).decode("utf-8", "ignore") if n else ""
                storage.kv_set(aid, k, v)
                return self._sj({"ok": True, "key": k, "size": len(v)})
            if k:
                r = storage.kv_get(aid, k)
                if not r:
                    return self._sj({"ok": False, "error": "Key nahi mili"}, 404)
                return self._sj({"ok": True, "key": k, "value": r["v"],
                                 "updated": r["updated"]})
            return self._sj({"ok": True, "keys": storage.kv_list(aid)})

        return self._sj({"ok": False, "error": "Route nahi mila"}, 404)

    def do_PUT(self):
        """curl -T … — PUT bhi upload hai."""
        pu = urllib.parse.urlparse(self.path)
        path = pu.path.rstrip("/") or "/"
        q = {k: v[0] for k, v in urllib.parse.parse_qs(pu.query).items()}
        if not path.startswith("/api/storage"):
            return self._sj({"ok": False, "error": "Route nahi mila"}, 404)
        return self._storage_api("POST", path, q)

    def do_DELETE(self):
        pu = urllib.parse.urlparse(self.path)
        path = pu.path.rstrip("/") or "/"
        q = {k: v[0] for k, v in urllib.parse.parse_qs(pu.query).items()}
        if not path.startswith("/api/storage"):
            return self._sj({"ok": False, "error": "Route nahi mila"}, 404)
        tok = self.headers.get("Authorization", "")
        if tok.lower().startswith("bearer "):
            tok = tok[7:]
        a = storage.by_token(tok.strip() or q.get("token", ""))
        if not a:
            return self._sj({"ok": False, "error": "Galat token"}, 401)
        p = path[len("/api/storage"):].rstrip("/")
        if p == "/file":
            ok, m = storage.delete(a["id"], q.get("path", ""))
            return self._sj({"ok": ok, "msg": m}, 200 if ok else 404)
        if p == "/kv":
            storage.kv_del(a["id"], q.get("key", ""))
            return self._sj({"ok": True})
        return self._sj({"ok": False, "error": "Route nahi mila"}, 404)

    def _drain(self, limit=None):
        """
        Reject karne se pehle client ka body padh ke phenk do.
        Warna curl/browser ko 'connection reset' milta hai, error nahi.
        """
        n = int(self.headers.get("Content-Length", 0) or 0)
        if limit and n > limit:
            self.close_connection = True
            return
        left = n
        try:
            while left > 0:
                b = self.rfile.read(min(262144, left))
                if not b:
                    break
                left -= len(b)
        except Exception:
            self.close_connection = True

    def _stream_file(self, fp, size, ctype):
        """Badi file bhi — 512 KB ke tukdon me, RAM safe."""
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(size))
        self.send_header("Content-Disposition",
                         f'attachment; filename="{os.path.basename(fp)}"')
        self.end_headers()
        try:
            with open(fp, "rb") as f:
                while True:
                    b = f.read(524288)
                    if not b:
                        break
                    self.wfile.write(b)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _stale_redirect(self):
        """
        🔄 Purane tunnel URL se aaya request?
        Turant naye URL par bhej do — user ko pata bhi nahi chalega.

        Host kahan se milta hai (priority):
          1. X-Forwarded-Host  (cloudflare/proxy)
          2. Host header
        """
        try:
            cur = tunnel.url()
            if not cur:
                return False

            raw = (self.headers.get("X-Forwarded-Host")
                   or self.headers.get("Host") or "")
            host = raw.split(",")[0].strip().split(":")[0].lower()
            if not host or host in ("localhost", "127.0.0.1", "0.0.0.0"):
                return False

            cur_host = tunnel._host_of(cur)
            if host == cur_host:
                return False
            if host not in tunnel.old_hosts():
                return False

            # purana tunnel host -> naye par 301 (permanent)
            new = cur.rstrip("/") + self.path
            body = (f'<!DOCTYPE html><meta charset="utf-8">'
                    f'<meta http-equiv="refresh" content="0;url={new}">'
                    f'<title>Naye link par ja rahe hain…</title>'
                    f'<body style="background:#070B14;color:#F8FAFC;'
                    f'font-family:system-ui;display:grid;place-items:center;'
                    f'height:100vh;margin:0;text-align:center">'
                    f'<div><div style="font-size:34px">🔄</div>'
                    f'<h2 style="margin:12px 0 6px">Link badal gaya hai</h2>'
                    f'<p style="color:#94A3B8">Naye address par bhej rahe '
                    f'hain…</p><a href="{new}" style="color:#00E6FF">{new}'
                    f'</a></div></body>').encode()
            self.send_response(301)
            self.send_header("Location", new)
            self.send_header("Cache-Control", "no-store, must-revalidate")
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            try:
                self.wfile.write(body)
            except Exception:
                pass
            tunnel.hit_stale(host)
            return True
        except Exception:
            return False

    # ── GET ──
    def do_GET(self):
        if self._stale_redirect():
            return
        p = urllib.parse.urlparse(self.path)
        path = p.path.rstrip("/") or "/"
        q = {k: v[0] for k, v in urllib.parse.parse_qs(p.query).items()}
        u = self._user()

        try:
            # 🛠 Maintenance mode — sirf admin andar
            # /maintenance-off KHUD block na ho jaye - warna
            # emergency switch bekaar hai
            if vcmd.maintenance() and path not in (
                    "/health", "/admin", "/admin/unlock", "/login",
                    "/logout", "/api/jarvis", "/maintenance-off"):
                ck = http.cookies.SimpleCookie(
                    self.headers.get("Cookie", ""))
                st = ck["rx_session"].value if "rx_session" in ck else ""
                if not admin_unlocked(st):
                    return self._send(_maint_page(), 503)

            # 🚫 BANNED — har page par rok. Session bhi kaat do.
            #
            # ⚠️ Pehle sirf LOGIN par check tha. Jo pehle se
            #    logged-in tha wo ban hone ke baad bhi 30 din
            #    tak andar ghusa rehta tha — ban bekaar tha.
            if u and u.get("banned") and path not in (
                    "/logout", "/health"):
                try:
                    db.kill_sessions(u["id"])
                except Exception:
                    pass
                return self._send(page("Band", BANNED_HTML), 403)

            if path == "/":
                return self._send(landing.p_home())
            if path in ("/terms", "/privacy", "/refund", "/sla"):
                return self._send(landing.p_legal(path[1:]))
            if path == "/status":
                return self._send(landing.p_status())
            # EMERGENCY - maintenance seedha OFF
            #
            # Agar kabhi admin panel me na ghus pao (cookie kho
            # gayi, ya kuch aur), to browser me ye kholo:
            #   /maintenance-off?pass=<ADMIN_PASS>
            # Bas. Website turant wapas aa jayegi.
            if path == "/maintenance-off":
                if (q.get("pass") or "") != ADMIN_PASS:
                    return self._send(
                        page("Nahi", MAINT_DENY_HTML), 403)
                vcmd._flags["maintenance"] = False
                vcmd._flags["changed_at"] = int(time.time())
                vcmd._flags["changed_by"] = "emergency-url"
                vcmd._save()
                vcmd.note("emergency", "maintenance=off",
                          "URL se hataya")
                return self._send(page("Wapas", MAINT_OK_HTML))

            if path == "/health":
                return self._send(json.dumps({"ok": True, "ts": int(time.time())}),
                                  ctype="application/json")

            # 🏦 FamGateway: secure status check. API secret stays server-side.
            if path == "/api/famgateway-status":
                if not u:
                    return self._send(json.dumps({"status": "error", "message": "Login required"}), 401, "application/json; charset=utf-8")
                order_id = (q.get("order_id") or "").strip()
                pay = db.get_payment(order_id)
                if not pay or int(pay.get("user_id", 0)) != int(u["id"]) or pay.get("provider") != "famgateway":
                    return self._send(json.dumps({"status": "error", "message": "Order not found"}), 404, "application/json; charset=utf-8")
                if pay.get("status") == "approved":
                    fresh = db.get_user(u["id"])
                    return self._send(json.dumps({"status": "success", "credits": pay.get("credits", 0), "balance": fresh.get("credits", 0)}), 200, "application/json; charset=utf-8")
                if pay.get("status") == "expired":
                    return self._send(json.dumps({"status": "expired"}), 200, "application/json; charset=utf-8")
                if pay.get("status") == "review":
                    return self._send(json.dumps({"status": "review", "message": "Payment admin review me hai."}), 200, "application/json; charset=utf-8")
                gw = famgateway_pay.verify_order(order_id)
                gw_status = str(gw.get("status", "error")).lower()
                details = gw.get("data") or gw
                if gw_status == "success":
                    try:
                        actual = float(details.get("amount") or details.get("payable_amount") or 0)
                    except Exception:
                        actual = 0
                    expected = float(pay.get("rupees") or 0)
                    utr = str(details.get("utr") or "").strip()
                    if actual <= 0 or not utr:
                        db.set_payment(order_id, status="review")
                        return self._send(json.dumps({"status": "review", "message": "Verified response me amount/UTR missing; admin review karega."}), 200, "application/json; charset=utf-8")
                    if abs(actual - expected) > 0.01:
                        db.set_payment(order_id, status="review")
                        return self._send(json.dumps({"status": "review", "message": "Payment amount mismatch; admin review karega."}), 200, "application/json; charset=utf-8")
                    ok, result, balance = db.complete_gateway_payment(order_id, utr, details.get("sender_name", ""))
                    if ok:
                        return self._send(json.dumps({"status": "success", "credits": pay.get("credits", 0), "balance": balance}), 200, "application/json; charset=utf-8")
                    if result == "duplicate_utr":
                        db.set_payment(order_id, status="review")
                        return self._send(json.dumps({"status": "review", "message": "Duplicate UTR; admin review karega."}), 200, "application/json; charset=utf-8")
                    return self._send(json.dumps({"status": "review", "message": "Auto-credit nahi hua; admin review karega."}), 200, "application/json; charset=utf-8")
                if gw_status == "expired":
                    db.set_payment(order_id, status="expired")
                    return self._send(json.dumps({"status": "expired"}), 200, "application/json; charset=utf-8")
                return self._send(json.dumps({"status": "pending"}), 200, "application/json; charset=utf-8")

            # 🗄️ STORAGE API — token se, login ki zarurat nahi
            if path.startswith("/api/storage"):
                return self._storage_api("GET", path, q)

            # 🤖 Bot se aaya banda — khali haath nahi jayega
            if path == "/b" or path == "/from-bot":
                tk = q.get("t", "")
                info = botlink.read_handoff(tk) if tk else {}
                return self._send(landing.p_frombot(info, tk))

            if path == "/signup" and not vcmd.signup_open():
                return self._send(page("Signup band", f'''
<div class="auth"><div class="box tc">
<div style="font-size:52px">🚧</div>
<h2>Naye signup band hain</h2>
<p class="s">Abhi hum naye accounts nahi le rahe.
Thodi der baad try kariye.</p>
<a href="/" class="btn btn-p mt">Home</a></div></div>'''))
            if path == "/signup":
                if q.get("b"):
                    info = botlink.read_handoff(q["b"])
                    if info:
                        return self._send(p_signup(bot=info, btok=q["b"]))
                return self._go("/dashboard") if u else self._send(p_signup())
            if path == "/login":
                return self._go("/dashboard") if u else \
                    self._send(p_login(ok=q.get("ok", "")))
            if path == "/logout":
                ck = http.cookies.SimpleCookie(self.headers.get("Cookie", ""))
                if "rx_session" in ck:
                    db.kill_session(ck["rx_session"].value)
                return self._send("", 302, redirect="/",
                                  cookie="rx_session=; Path=/; Max-Age=0")

            # ── login zaroori ──
            if not u:
                return self._go("/login")

            # 🔌 Console API (live polling)
            m = re.match(r"^/api/console/(\d+)$", path)
            if m:
                sid = int(m.group(1))
                if not db.get_app(sid, u["id"]):
                    return self._send('{"lines":[],"total":0}',
                                      ctype="application/json")
                since = int(q.get("since", "0") or 0)
                lines = engine.console(sid, since)
                total = since + len(lines)
                return self._send(json.dumps({"lines": lines, "total": total,
                                              "run": engine.is_running(sid),
                                              "busy": engine.is_busy(sid)}),
                                  ctype="application/json")

            # ⚡ Halka live endpoint — har page ka livebar isko poochta hai
            if path == "/api/live":
                sn = sysinfo.snapshot()
                return self._send(json.dumps({
                    "cpu": sn["cpu"]["percent"],
                    "ram": sn["ram"]["percent"],
                    "disk": sn["disk"]["percent"],
                    "dn": sn["net"]["down_kbs"],
                    "up": sn["net"]["up_kbs"],
                    "ramu": sn["ram"]["used"],
                    "load": sn["cpu"]["load1"],
                    "procs": sn["procs"],
                    "health": sn["health"], "hcls": sn["hcls"],
                    "uptime": sn["uptime_h"],
                    "ts": sn["ts"]}), ctype="application/json")

            if path == "/api/system":
                sn = sysinfo.snapshot()
                srv = []
                for a in db.user_apps(u["id"]):
                    us = engine.usage(a["id"])
                    srv.append({"id": a["id"], "ram": us["ram"],
                                "cpu": us["cpu"],
                                "up": sysinfo.human_time(us["uptime"])
                                if engine.is_running(a["id"]) else "—"})
                sn["servers"] = srv
                from brand import bargraph, stackbars
                H = sn["hist"]
                sn["charts"] = [
                    minibars(H["cpu"] or [0], 110, 30, "#7C3AED"),
                    minibars(H["ram"] or [0], 110, 30, "#00E6FF"),
                    sparkline(H["net"] or [0, 0], 110, 30, "#22C55E", sid="nt"),
                    stackbars([("CPU", H["cpu"] or [0], "#7C3AED"),
                               ("RAM", H["ram"] or [0], "#00E6FF"),
                               ("DISK", H["disk"] or [0], "#8B5CF6")],
                              560, 215, "mc"),
                    bargraph(H["cpu"] or [0], 520, 180, "#7C3AED", "c1", "%", 100),
                    bargraph(H["ram"] or [0], 520, 180, "#00E6FF", "r1", "%", 100),
                    bargraph(H["disk"] or [0], 520, 175, "#8B5CF6", "d1", "%", 100),
                    bargraph(H["net"] or [0], 520, 175, "#22C55E", "n1", " KB/s"),
                ]
                sn.pop("hist", None)
                return self._send(json.dumps(sn), ctype="application/json")

            # 🎁 FREE SERVER
            if path == "/free":
                if not vcmd.free_open():
                    return self._send(_closed_page(
                        u, "Free service abhi band hai",
                        "Admin ne free servers temporary rok diye hain. "
                        "Thodi der baad try kariye — ya paid plan lijiye."))
                pg = freeserver.p_free(u)
                if q.get("hi"):
                    nm = (u.get("name") or "").split()[0] if u.get("name") \
                        else "there"
                    pg += voice.speak(
                        f"Account created. Welcome to Ravan X Hosting, {nm}. "
                        f"Let's get your first server online.", 800)
                return self._send(pg)
            if path in ("/free/enter", "/free/done") and \
                    not vcmd.free_open():
                return self._send(_closed_page(
                    u, "Free service abhi band hai",
                    "Admin ne free servers temporary rok diye hain."))
            if path == "/free/enter":
                return self._send(freeserver.p_enter(u))
            if path == "/free/done":
                tk = q.get("t", "")
                if not tk:
                    return self._send(freeserver.p_enter(u, "Token nahi mila"))
                return self._send(freeserver.p_token(u, tk))
            if path == "/blacklisted":
                return self._send(freeserver.p_blacklisted(u))

            # 🧾 Payment screenshot — sirf admin ya khud ka
            m = re.match(r"^/admin/shot/([A-Za-z0-9]+)$", path)
            if m:
                ref = m.group(1)
                pay = db.get_payment(ref)
                if not pay:
                    return self._go("/admin")
                mine = pay["user_id"] == u["id"]
                ck = http.cookies.SimpleCookie(
                    self.headers.get("Cookie", ""))
                stok = (ck["rx_session"].value
                        if "rx_session" in ck else "")
                if not mine and not admin_unlocked(stok):
                    return self._go("/admin")
                sh = pay.get("shot") or ""
                if not sh:
                    return self._go("/admin")
                try:
                    owner = storage.by_web_user(pay["user_id"])
                    fp, sz, ct = storage.open_file(owner["id"], sh)
                except Exception:
                    fp = None
                if not fp:
                    return self._go("/admin")
                self.send_response(200)
                self.send_header("Content-Type", ct)
                self.send_header("Content-Length", str(sz))
                self.send_header("Cache-Control", "private, max-age=600")
                self.end_headers()
                try:
                    with open(fp, "rb") as fh:
                        while True:
                            b = fh.read(262144)
                            if not b:
                                break
                            self.wfile.write(b)
                except Exception:
                    pass
                return

            # 🗄️ STORAGE (website ke andar hi)
            if path == "/storage":
                return self._send(storagepage.p_storage(
                    u, msg=q.get("msg", ""), err=q.get("err", "")))
            if path == "/storage/get":
                a = storage.ensure_for_user(u)
                fp, sz, ct = storage.open_file(a["id"], q.get("path", ""))
                if not fp:
                    return self._go("/storage?err=File+nahi+mili")
                return self._stream_file(fp, sz, ct)
            if path == "/storage/del":
                a = storage.ensure_for_user(u)
                ok, m2 = storage.delete(a["id"], q.get("path", ""))
                return self._go("/storage?" + ("msg=" if ok else "err=") +
                                urllib.parse.quote(m2))

            if path == "/system":
                return self._send(live.p_system(u))

            m = re.match(r"^/api/stats/(\d+)$", path)
            if m:
                sid = int(m.group(1))
                if not db.get_app(sid, u["id"]):
                    return self._send("{}", ctype="application/json")
                us = engine.usage(sid)
                us["run"] = engine.is_running(sid)
                us["disk"] = engine.disk_mb(u["id"], sid)
                return self._send(json.dumps(us), ctype="application/json")

            if path == "/dashboard":
                pg = p_dashboard(u)
                if q.get("hi"):
                    nm = (u.get("name") or "").split()[0] if u.get("name") \
                        else "there"
                    pg += voice.speak(
                        f"Welcome back {nm}. All systems nominal. "
                        f"Your dashboard is ready.", 700)
                return self._send(pg)

            # 🖥 SERVERS
            if path in ("/servers", "/apps"):
                return self._send(pages.p_servers(u))
            if path in ("/servers/new", "/apps/new"):
                return self._send(pages.p_new_server(u))
            if path == "/files":
                if q.get("del"):
                    engine.delete_path(u["id"], int(q.get("s", 0)), q["del"])
                    return self._go(f"/files?s={q.get('s','')}")
                if q.get("edit"):
                    return self._send(pages.p_edit(u, int(q.get("s", 0)),
                                                   q["edit"]))
                return self._send(pages.p_files(u,
                    int(q["s"]) if q.get("s") else None, q.get("d", "")))
            if path == "/console":
                sid = int(q["s"]) if q.get("s") else None
                if q.get("clear") and sid:
                    engine.clear_console(sid)
                    return self._go(f"/console?s={sid}")
                return self._send(pages.p_console(u, sid))
            if path == "/analytics":
                return self._send(pages.p_analytics(u))
            if path == "/billing":
                return self._send(p_billing(u))
            if path == "/recharge":
                pack_idx = q.get("pack")
                if u and pack_idx is not None and famgateway_pay.configured():
                    proto = self.headers.get("X-Forwarded-Proto", "https").split(",")[0].strip()
                    host = self.headers.get("X-Forwarded-Host") or self.headers.get("Host", "")
                    hook = f"{proto}://{host}/api/famgateway-webhook" if host else ""
                    order, ref, rs, cr, err = create_famgateway_web_order(u, pack_idx, webhook_url=hook)
                    if order:
                        return self._send(p_famgateway_checkout(u, order, ref, rs, cr, int(pack_idx)))
                    return self._send(p_recharge(u, err=err))
                return self._send(p_recharge(u, msg=q.get("ok", "")))
            if path == "/profile":
                return self._send(p_profile(u, msg=q.get("ok", "")))
            if path == "/support":
                return self._send(p_support(u, msg=q.get("ok", "")))
            if path == "/admin":
                ck = http.cookies.SimpleCookie(self.headers.get("Cookie", ""))
                tok = ck["rx_session"].value if "rx_session" in ck else ""
                if not admin_unlocked(tok):
                    return self._send(live.p_admin_lock(u))
                return self._send(p_admin(u, msg=q.get("ok", "")))

            # 👑 AI BOSS — Pro+ plan aur admin
            if path == "/boss":
                ck = http.cookies.SimpleCookie(
                    self.headers.get("Cookie", ""))
                tk = ck["rx_session"].value if "rx_session" in ck else ""
                adm = admin_unlocked(tk) or u.get("role") == "admin"
                import bosspage
                try:
                    srv = db.user_apps(u["id"])
                except Exception:
                    srv = []
                return self._send(bosspage.p_boss(u, adm, srv))

            # 🤖 JARVIS CONTROL ROOM — sirf admin
            if path == "/admin/jarvis":
                ck = http.cookies.SimpleCookie(
                    self.headers.get("Cookie", ""))
                tk = ck["rx_session"].value if "rx_session" in ck else ""
                if not admin_unlocked(tk):
                    return self._send(live.p_admin_lock(u))
                return self._send(jarvispage.p_jarvis(u))

            m = re.match(r"^/admin/jarvis/srv/(\d+)/(start|stop)$", path)
            if m:
                ck = http.cookies.SimpleCookie(
                    self.headers.get("Cookie", ""))
                tk = ck["rx_session"].value if "rx_session" in ck else ""
                if not admin_unlocked(tk):
                    return self._go("/admin")
                sid = int(m.group(1))
                a = db.get_app(sid)
                if a:
                    if m.group(2) == "stop":
                        engine.stop(sid)
                        db.update_app(sid, status="stopped")
                    else:
                        engine.start(a["user_id"], sid)
                        db.update_app(sid, status="running")
                return self._go("/admin/jarvis")

            if path == "/admin/welcome":
                ck = http.cookies.SimpleCookie(self.headers.get("Cookie", ""))
                tok = ck["rx_session"].value if "rx_session" in ck else ""
                if not admin_unlocked(tok):
                    return self._go("/admin")
                return self._send(live.p_admin_welcome(u))

            # /server/<id>/<action>
            m = re.match(r"^/(?:server|app)/(\d+)(?:/(\w+))?$", path)
            if m:
                sid, act = int(m.group(1)), m.group(2)
                a = db.get_app(sid, u["id"])
                if not a:
                    return self._go("/servers")

                if act == "start":
                    if u["credits"] < CREDIT_RATE:
                        return self._send(pages.p_server(
                            u, sid, err=f"Credits kam hain! {CREDIT_RATE} "
                            f"credits/ghanta lagta hai. Recharge karo."))
                    okk, res = engine.start(u["id"], sid)
                    if okk:
                        db.update_app(sid, status="running",
                                      started_at=int(time.time()))
                        return self._send(pages.p_server(
                            u, sid, msg=f"Server chalu ho gaya (PID {res})"))
                    return self._send(pages.p_server(u, sid, err=str(res)))

                if act == "stop":
                    engine.stop(sid)
                    db.update_app(sid, status="stopped")
                    return self._send(pages.p_server(u, sid, msg="Server band"))

                if act == "restart":
                    okk, res = engine.restart(u["id"], sid)
                    db.update_app(sid, status="running" if okk else "stopped",
                                  started_at=int(time.time()) if okk else 0,
                                  restarts=a["restarts"] + 1)
                    return self._send(pages.p_server(
                        u, sid, msg="Restart ho gaya" if okk else "",
                        err="" if okk else str(res)))

                if act == "install":
                    engine.install_deps(u["id"], sid)
                    return self._send(pages.p_server(
                        u, sid, msg="Install chalu — console me dekho"))

                if act == "delete":
                    engine.destroy(u["id"], sid)
                    db.delete_app(sid)
                    return self._go("/servers")

                return self._send(pages.p_server(u, sid))

            # admin actions — lock ke peeche
            _ck = http.cookies.SimpleCookie(self.headers.get("Cookie", ""))
            _tok = _ck["rx_session"].value if "rx_session" in _ck else ""
            if path.startswith("/admin/") and admin_unlocked(_tok):
                m = re.match(r"^/admin/pay/([\w-]+)/(ok|no)$", path)
                if m:
                    ref, act = m.group(1), m.group(2)
                    pay = db.get_payment(ref)
                    if pay and pay["status"] == "pending":
                        if act == "ok":
                            db.set_payment(ref, status="approved",
                                           done_at=int(time.time()))
                            db.add_credits(pay["user_id"], pay["credits"],
                                           f"Recharge {ref}")
                            return self._go("/admin?ok=Payment+approved")
                        db.set_payment(ref, status="rejected",
                                       done_at=int(time.time()))
                        return self._go("/admin?ok=Payment+rejected")
                    return self._go("/admin?ok=Already+processed")

                m = re.match(r"^/admin/tunnel/(on|off)$", path)
                if m:
                    if m.group(1) == "on":
                        tunnel.on_change(on_tunnel_change)
                        threading.Thread(
                            target=lambda: (tunnel.enable(PORT),
                                            tunnel.keepalive(PORT)),
                            daemon=True).start()
                        return self._go("/admin?ok=Tunnel+start+ho+raha+hai+"
                                        "(20-40+sec)")
                    tunnel.disable()
                    return self._go("/admin?ok=Tunnel+band")

                m = re.match(r"^/admin/flag/(free|signup|maint)/([01])$",
                             path)
                if m:
                    key, val = m.group(1), m.group(2) == "1"
                    if key == "free":
                        vcmd._flags["free_open"] = val
                    elif key == "signup":
                        vcmd._flags["signup_open"] = val
                    else:
                        vcmd._flags["maintenance"] = val
                    vcmd._flags["changed_at"] = int(time.time())
                    vcmd._flags["changed_by"] = u.get("email", "")
                    vcmd._save()
                    vcmd.note(u.get("email", ""), f"button:{key}={val}",
                              "manual toggle")
                    return self._go("/admin?ok=Setting+badal+gayi")

                if path == "/admin/botpush":
                    okb = botlink.publish(force=True)
                    botlink.fetch_bot()
                    return self._go("/admin?ok=" + (
                        "URL+bot+ko+bhej+diya" if okb
                        else "Cloud+ya+URL+ready+nahi"))

                if path == "/admin/seturl":
                    nu = (q.get("u") or "").strip()
                    if nu.startswith("http"):
                        tunnel.set_url(nu, "manual")
                        return self._go("/admin?ok=URL+set+ho+gaya")
                    return self._go("/admin?ok=Galat+URL")

                if path == "/admin/cloudpush":
                    ok1 = cloudsync.push_db(force=True)
                    ok2 = cloudsync.push_files()
                    return self._go(f"/admin?ok=Backup+"
                                    f"{'ho+gaya' if ok1 else 'fail'}"
                                    f"{'+(files+bhi)' if ok2 else ''}")

                if path == "/admin/cloudtest":
                    cloudsync.ping()
                    return self._go("/admin?ok=Cloud+test+"
                                    + ("LIVE" if cloudsync._ok else "FAIL"))

                if path == "/admin/shorttest":
                    return self._go("/admin?ok=Test+ho+gaya")

                m = re.match(r"^/admin/unblack/(\d+)$", path)
                if m:
                    unlock.unblacklist(int(m.group(1)))
                    return self._go("/admin?ok=Blacklist+se+hata+diya")
            # 🚫 BAN / UNBAN — sakht niyam
            mb = re.match(r"^/admin/(ban|unban)/(\d+)$", path)
            if mb:
                ck3 = http.cookies.SimpleCookie(
                    self.headers.get("Cookie", ""))
                tk3 = (ck3["rx_session"].value
                       if "rx_session" in ck3 else "")
                if u.get("role") != "admin" and not admin_unlocked(tk3):
                    return self._go("/dashboard")
                act3, tid = mb.group(1), int(mb.group(2))
                tu = db.get_user(tid)
                if not tu:
                    return self._go("/admin?err=User+nahi+mila")
                # ⚠️ Admin ko ban nahi kar sakte — warna website
                #    hi lock ho jayegi
                if tu.get("role") == "admin":
                    return self._go("/admin?err="
                                    + urllib.parse.quote(
                                        "Admin ko ban nahi kar sakte"))
                if act3 == "ban":
                    db.update_user(tid, banned=1)
                    # sab session kaat do — turant bahar
                    try:
                        db.kill_sessions(tid)
                    except Exception:
                        pass
                    m3 = f"{tu['email']} ban ho gaya"
                else:
                    db.update_user(tid, banned=0)
                    m3 = f"{tu['email']} wapas allow"
                return self._go("/admin?ok=" + urllib.parse.quote(m3))


                m = re.match(r"^/admin/credit/(\d+)$", path)
                if m:
                    db.add_credits(int(m.group(1)), 100, "Admin bonus")
                    return self._go("/admin?ok=100+credits+added")

            return self._send(page("404", f"""<div class="auth"><div class="box tc">
<div style="font-size:56px">🔍</div><h2>404</h2>
<p class="s">Ye page nahi mila</p>
<a href="/dashboard" class="btn btn-p">Dashboard</a></div></div>""", u), 404)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return self._send(page("Error", f"""<div class="auth"><div class="box tc">
<div style="font-size:56px">⚠️</div><h2>Kuch gadbad ho gayi</h2>
<p class="s">{esc(str(e)[:120])}</p>
<a href="/" class="btn btn-p">Home</a></div></div>"""), 500)

    # ── POST ──
    def do_POST(self):
        if self._stale_redirect():
            return
        pu = urllib.parse.urlparse(self.path)
        path = pu.path.rstrip("/") or "/"
        u = self._user()

        # FamGateway signed webhook: fulfills a browser-closed order too.
        if path == "/api/famgateway-webhook":
            key = os.environ.get("FAMGATEWAY_API_KEY", "").strip()
            if not key:
                return self._send("Gateway not configured", 503, "text/plain; charset=utf-8")
            try:
                size = int(self.headers.get("Content-Length", "0") or 0)
                if size <= 0 or size > 65536:
                    return self._send("Invalid body size", 400, "text/plain; charset=utf-8")
                raw = self.rfile.read(size)
                signature = (self.headers.get("X-FamGateway-Signature") or "").strip().lower()
                expected = hmac.new(key.encode("utf-8"), raw, hashlib.sha256).hexdigest()
                if not signature or not hmac.compare_digest(signature, expected):
                    return self._send("Invalid signature", 401, "text/plain; charset=utf-8")
                event = json.loads(raw.decode("utf-8"))
                if str(event.get("status", "")).lower() != "success" and event.get("event") != "payment.success":
                    return self._send(json.dumps({"status": "ignored"}), 200, "application/json; charset=utf-8")
                order_id = str(event.get("order_id") or "").strip()
                pay = db.get_payment(order_id)
                if not pay or pay.get("provider") != "famgateway":
                    return self._send("Order not found", 404, "text/plain; charset=utf-8")
                try:
                    paid_amount = float(event.get("amount") or event.get("payable_amount") or 0)
                except Exception:
                    paid_amount = 0
                expected_amount = float(pay.get("rupees") or 0)
                utr = str(event.get("utr") or "").strip()
                if not utr or paid_amount <= 0 or abs(paid_amount - expected_amount) > 0.01:
                    return self._send("Payment data mismatch", 422, "text/plain; charset=utf-8")
                ok, result, balance = db.complete_gateway_payment(order_id, utr, event.get("sender_name", ""))
                if ok:
                    return self._send(json.dumps({"status": "received", "order_id": order_id}), 200, "application/json; charset=utf-8")
                return self._send(json.dumps({"status": "review", "reason": result}), 200, "application/json; charset=utf-8")
            except Exception:
                return self._send("Webhook processing error", 500, "text/plain; charset=utf-8")

        # 🗄️ STORAGE API (token) — login ki zarurat nahi
        if path.startswith("/api/storage"): 
            q = {k: v[0] for k, v in urllib.parse.parse_qs(pu.query).items()}
            return self._storage_api("POST", path, q)

        # 🔧 CODE DOCTOR — crash theek karo
        if path == "/api/doctor":
            if not u:
                return self._sj({"ok": False, "err": "login"}, 401)
            n = int(self.headers.get("Content-Length", 0) or 0)
            try:
                d = json.loads(self.rfile.read(min(n, 64000)) or b"{}")
            except Exception:
                d = {}
            sid = int(d.get("sid") or 0)
            a = db.get_app(sid, u["id"])
            if not a:
                return self._sj({"ok": False, "err": "server nahi mila"}, 404)
            mode = d.get("mode", "fix")

            folder = engine.server_dir(u["id"], sid)
            info = engine.detect(folder)
            fn = info.get("entry") or "main.py"
            src = engine.read_file(u["id"], sid, fn, 9000) or ""
            lang = info.get("lang") or "Python"

            if mode == "fix":
                lines = engine.console(sid, 0)
                log = "\n".join(
                    str(x.get("x", "")) if isinstance(x, dict) else str(x)
                    for x in lines[-70:])
                if not log.strip() and not src:
                    return self._sj({"ok": False,
                                     "err": "Console khali hai — "
                                            "pehle server chalao"})
                r = coder.diagnose(log, src, lang, fn)
            elif mode == "review":
                if not src:
                    return self._sj({"ok": False,
                                     "err": "Koi code nahi mila"})
                r = coder.review(src, lang, fn)
            elif mode == "deps":
                if not src:
                    return self._sj({"ok": False, "err": "Koi code nahi"})
                txt = coder.requirements(src, lang)
                if txt:
                    rf = ("requirements.txt" if lang == "Python"
                          else "package.json")
                    engine.write_file(u["id"], sid, rf, txt)
                    return self._sj({"ok": True, "mode": "deps",
                                     "file": rf, "text": txt})
                return self._sj({"ok": False, "err": "bana nahi paya"})
            else:
                return self._sj({"ok": False, "err": "galat mode"}, 400)

            if not r:
                return self._sj({"ok": False,
                                 "err": coder.status().get("error")
                                 or "AI se jawab nahi mila"})
            r["ok"] = True
            r["mode"] = mode
            r["file"] = fn
            return self._sj(r)

        # 🔧 FIX APPLY — sudhra code save karo
        if path == "/api/doctor/apply":
            if not u:
                return self._sj({"ok": False}, 401)
            n = int(self.headers.get("Content-Length", 0) or 0)
            try:
                d = json.loads(self.rfile.read(min(n, 200000)) or b"{}")
            except Exception:
                d = {}
            sid = int(d.get("sid") or 0)
            code = str(d.get("code") or "")
            fname = re.sub(r"[^A-Za-z0-9._/-]", "",
                           str(d.get("file") or "main.py"))[:80]
            if not db.get_app(sid, u["id"]) or not code.strip():
                return self._sj({"ok": False, "err": "galat data"}, 400)
            old = engine.read_file(u["id"], sid, fname, 200000) or ""
            if old:
                engine.write_file(u["id"], sid, fname + ".bak", old)
            okw = engine.write_file(u["id"], sid, fname, code)
            if okw:
                engine.log(sid, f"🔧 Code Doctor ne {fname} theek kiya "
                                f"(purana {fname}.bak me hai)", "ok")
            return self._sj({"ok": bool(okw), "file": fname,
                             "backup": fname + ".bak" if old else ""})

        # 👑 AI BOSS — 57 model ka malik (Pro+ only)
        if path == "/api/boss":
            if not u:
                return self._sj({"ok": False, "err": "login"}, 401)
            n = int(self.headers.get("Content-Length", 0) or 0)
            try:
                d = json.loads(self.rfile.read(min(n, 60000)) or b"{}")
            except Exception:
                d = {}
            ck = http.cookies.SimpleCookie(self.headers.get("Cookie", ""))
            stok = ck["rx_session"].value if "rx_session" in ck else ""
            adm = admin_unlocked(stok) or u.get("role") == "admin"
            try:
                import aiboss
            except Exception as e:
                return self._sj({"ok": False, "err": str(e)[:90]}, 500)

            act = str(d.get("act") or "ask")[:12]
            if act == "status":
                return self._sj({"ok": True, **aiboss.status(u, adm)})
            if act == "models":
                if not aiboss.perks(u, adm)["on"]:
                    return self._sj({"ok": False, "err": "plan"}, 403)
                only = aiboss.allowed_models(u, adm)
                ms = aiboss.all_models()
                # free/starter — batao kaunsa locked hai
                for x in ms:
                    x["lock"] = bool(only is not None
                                     and x["m"] not in only)
                return self._sj({"ok": True, "models": ms,
                                 "jobs": aiboss.job_list(),
                                 "limited": only is not None,
                                 "mine": len(only) if only else len(ms)})
            if act == "board":
                if not aiboss.perks(u, adm)["panel"] and not adm:
                    return self._sj({"ok": False, "err": "plan"}, 403)
                return self._sj({"ok": True,
                                 "board": aiboss.leaderboard(20),
                                 "hist": aiboss.history(20)})
            # ── asli kaam ──
            txt = str(d.get("text", ""))[:12000]
            if not txt.strip():
                return self._sj({"ok": False, "err": "khali"}, 400)
            hist = d.get("hist") or []
            if not isinstance(hist, list):
                hist = []
            hist = [{"r": str(x.get("r", "u"))[:1],
                     "t": str(x.get("t", ""))[:900]}
                    for x in hist[-8:] if isinstance(x, dict)]
            r = aiboss.run(txt, u, adm,
                           hint=str(d.get("job") or "")[:12],
                           team=d.get("team"),
                           force=str(d.get("force") or "")[:90],
                           history=hist)
            return self._sj(r)

        # 🕵️ BOSS AGENT — khud file uthaye, theek kare, poochhe
        if path == "/api/agent":
            if not u:
                return self._sj({"ok": False, "err": "login"}, 401)
            n = int(self.headers.get("Content-Length", 0) or 0)
            try:
                d = json.loads(self.rfile.read(min(n, 8000)) or b"{}")
            except Exception:
                d = {}
            ck = http.cookies.SimpleCookie(self.headers.get("Cookie", ""))
            stok = ck["rx_session"].value if "rx_session" in ck else ""
            adm = admin_unlocked(stok) or u.get("role") == "admin"
            try:
                import bossagent
            except Exception as e:
                return self._sj({"ok": False, "err": str(e)[:90]}, 500)

            act = str(d.get("act") or "status")[:10]
            if act == "status":
                return self._sj({"ok": True,
                                 **bossagent.status(u, adm)})
            sid = int(d.get("sid") or 0)
            pid = str(d.get("id") or "")[:20]

            # 💬 AGENT SE BAAT — chat mode
            if act == "chat":
                if not db.get_app(sid, u["id"]):
                    return self._sj({"ok": False,
                                     "msg": "server nahi mila"}, 404)
                hs = d.get("hist") or []
                if not isinstance(hs, list):
                    hs = []
                hs = [{"r": str(x.get("r", "u"))[:1],
                       "t": str(x.get("t", ""))[:1200]}
                      for x in hs[-6:] if isinstance(x, dict)]
                return self._sj(bossagent.chat(
                    u["id"], sid, str(d.get("text") or "")[:4000],
                    u, adm, history=hs))

            if act == "scan":
                if not db.get_app(sid, u["id"]):
                    return self._sj({"ok": False,
                                     "msg": "server nahi mila"}, 404)
                r = bossagent.investigate(
                    u["id"], sid, u, adm,
                    note=str(d.get("note") or "")[:300])
                return self._sj(r)
            if act == "apply":
                return self._sj(bossagent.apply(pid, u["id"], u, adm))
            if act == "deploy":
                return self._sj(bossagent.deploy(pid, u["id"], u, adm))
            if act == "undo":
                return self._sj(bossagent.rollback(pid, u["id"]))
            return self._sj({"ok": False, "err": "act"}, 400)

        # 🔁 AUTO-FIX — khud theek karo
        if path == "/api/autofix":
            if not u:
                return self._sj({"ok": False}, 401)
            n = int(self.headers.get("Content-Length", 0) or 0)
            try:
                d = json.loads(self.rfile.read(min(n, 4096)) or b"{}")
            except Exception:
                d = {}
            sid = int(d.get("sid") or 0)
            act = str(d.get("act") or "status")[:12]
            if not db.get_app(sid, u["id"]):
                return self._sj({"ok": False, "err": "server nahi mila"}, 404)
            try:
                import autofix
            except Exception as e:
                return self._sj({"ok": False, "err": str(e)[:80]}, 500)

            if act == "on":
                autofix.set_on(sid, True)
                autofix.start_watcher()
                engine.log(sid, "🔁 Auto-fix CHALU — crash hote hi khud "
                                "theek karunga", "ok")
                return self._sj({"ok": True, "on": True,
                                 **autofix.status(sid)})
            if act == "off":
                autofix.set_on(sid, False)
                engine.log(sid, "🔁 Auto-fix BAND", "warn")
                return self._sj({"ok": True, "on": False,
                                 **autofix.status(sid)})
            if act == "now":
                autofix.reset(sid)
                r = autofix.attempt(u["id"], sid, force=True)
                if r.get("ok"):
                    good, why = autofix.verify(u["id"], sid, wait=6,
                                               since=r.get("since", 0))
                    r["worked"] = good
                    r["after"] = why
                    engine.log(sid, ("✅ Auto-fix kaamyaab — " + why)
                               if good else ("⚠️ Fix laga par " + why),
                               "ok" if good else "warn")
                return self._sj({**r, **autofix.status(sid)})
            return self._sj({"ok": True, **autofix.status(sid),
                             "hist": autofix.history(12)})

        # 🎤 JARVIS VOICE — baat + command + confirm
        if path == "/api/jarvis":
            if not u:
                return self._sj({"ok": False, "say": "Pehle login kariye.",
                                 "shown": "🔒 Login zaroori"}, 401)
            n = int(self.headers.get("Content-Length", 0) or 0)
            try:
                d = json.loads(self.rfile.read(min(n, 4096)) or b"{}")
            except Exception:
                d = {}
            txt = str(d.get("text", ""))[:220]
            pend = str(d.get("pending", ""))[:40]   # confirm ka intezaar
            ck = http.cookies.SimpleCookie(self.headers.get("Cookie", ""))
            stok = ck["rx_session"].value if "rx_session" in ck else ""
            is_admin = admin_unlocked(stok) or u.get("role") == "admin"

            # ── 1. Pehle se koi confirm pending hai? ──
            if pend:
                if vcmd.is_no(txt):
                    return self._sj({
                        "ok": True, "say": "Theek hai sir, rehne diya.",
                        "shown": "✋ Cancel kiya", "chat": True})
                if vcmd.is_yes(txt):
                    try:
                        okc, say, shown = vcmd.run(pend, None, u, is_admin)
                    except Exception as e:
                        okc, say, shown = (False, "Kuch gadbad ho gayi.",
                                           f"❌ {str(e)[:50]}")
                    vcmd.note(u.get("email", ""), f"[confirm] {pend}", shown)
                    return self._sj({
                        "ok": okc, "say": say, "shown": shown,
                        "action": pend,
                        "reload": pend in ("server_off", "server_on",
                                           "server_restart", "free_off",
                                           "free_on", "maint_on",
                                           "maint_off")})
                return self._sj({
                    "ok": False,
                    "say": "Samajh nahi aaya sir. Haan ya nahi boliye.",
                    "shown": "❓ Haan ya nahi?", "pending": pend})

            # ── 2. AI se samajhne ki koshish ──
            act, arg, ai_reply, eng = None, None, "", ""
            try:
                import db as _db
                import sysinfo as _si
                _sn = _si.snapshot(push_hist=False)
                _f = vcmd.flags()
                _apps = vcmd._all_apps()
                _live = sum(1 for a in _apps if engine.is_running(a["id"]))
                _ctx = {"live": _live, "total": len(_apps),
                        "users": _db.stats().get("users", 0),
                        "cpu": _sn["cpu"]["percent"],
                        "ram": _sn["ram"]["percent"],
                        "free_open": _f["free_open"],
                        "signup_open": _f["signup_open"],
                        "maintenance": _f["maintenance"]}
                a2, r2, e2 = brain.think(txt, _ctx)
                if a2 and a2 != "chat":
                    act, ai_reply, eng = a2, r2, e2
                elif a2 == "chat" and r2:
                    vcmd.note(u.get("email", ""), txt, "💬 " + r2[:50])
                    return self._sj({"ok": True, "say": r2,
                                     "shown": "💬 " + r2[:70],
                                     "chat": True, "engine": e2})
            except Exception:
                pass

            # ── 2b. AI fail? keyword se ──
            if not act:
                act, arg = vcmd.parse(txt)
            if act:
                # khatarnak? -> pehle poocho
                if act in vcmd.DANGER and not d.get("skip_confirm"):
                    q2 = vcmd.DANGER[act]
                    return self._sj({
                        "ok": True, "confirm": True, "pending": act,
                        "say": q2, "shown": "⚠️ " + q2, "engine": eng})
                try:
                    okc, say, shown = vcmd.run(act, arg, u, is_admin)
                except Exception as e:
                    okc, say, shown = (False, "Kuch gadbad ho gayi.",
                                       f"❌ {str(e)[:50]}")
                vcmd.note(u.get("email", ""), txt, shown)
                if ai_reply:
                    say = ai_reply + (" " + say if okc else "")
                return self._sj({
                    "ok": okc, "say": say[:400], "shown": shown,
                    "action": act, "engine": eng,
                    "reload": act in ("server_on", "free_on", "maint_off")})

            # ── 3. Command nahi — baat hai? ──
            rep = vcmd.chat_reply(txt)
            if rep:
                return self._sj({"ok": True, "say": rep,
                                 "shown": "💬 " + rep[:70], "chat": True})

            # ── 4. Kuch samajh nahi aaya ──
            return self._sj({
                "ok": False,
                "say": "Sorry sir, ye samajh nahi aaya. Dobara boliye.",
                "shown": f"❓ {esc(txt[:60])}", "chat": True})

        # 🔊 JARVIS ki ASLI AWAAZ
        if path == "/api/jarvis/tts":
            if not u:
                return self._sj({"ok": False}, 401)
            n = int(self.headers.get("Content-Length", 0) or 0)
            try:
                d = json.loads(self.rfile.read(min(n, 4096)) or b"{}")
            except Exception:
                d = {}
            txt = str(d.get("text", ""))[:900]
            if not txt:
                return self._sj({"ok": False, "err": "no text"}, 400)
            wav, eng = brain.speak(txt, prefer=d.get("engine"))
            if not wav:
                return self._sj({"ok": False, "err": "tts fail"}, 503)
            self.send_response(200)
            self.send_header("Content-Type", "audio/wav")
            self.send_header("Content-Length", str(len(wav)))
            self.send_header("X-Engine", eng)
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            try:
                self.wfile.write(wav)
            except Exception:
                pass
            return

        # 🎤 JARVIS SUNTA HAI — audio upload
        if path == "/api/jarvis/stt":
            if not u:
                return self._sj({"ok": False}, 401)
            n = int(self.headers.get("Content-Length", 0) or 0)
            if n > 12 * 1024 * 1024:
                self._drain(20 * 1024 * 1024)
                return self._sj({"ok": False, "err": "bahut badi"}, 413)
            raw = self.rfile.read(n) if n else b""
            if not raw:
                return self._sj({"ok": False, "err": "no audio"}, 400)
            mime = self.headers.get("X-Audio-Mime", "audio/webm")
            txt, eng = brain.listen(raw, mime=mime)
            if not txt:
                return self._sj({"ok": False, "err": "sunayi nahi diya",
                                 "detail": brain.status().get("error", "")})
            return self._sj({"ok": True, "text": txt, "engine": eng})

        # 💳 RECHARGE — screenshot ke saath (multipart)
        if path == "/recharge" and "multipart" in self.headers.get(
                "Content-Type", ""):
            if not u:
                return self._go("/login")
            if unlock.is_black(u["id"]):
                self._drain(20 * 1024 * 1024)
                return self._send(freeserver.p_blacklisted(u))
            n = int(self.headers.get("Content-Length", 0) or 0)
            if n > 12 * 1024 * 1024:
                self._drain(20 * 1024 * 1024)
                return self._send(p_recharge(
                    u, err="Screenshot 12MB se badi hai"))
            mp = MultipartStream(self.rfile, self.headers)
            fn = mp.next_file("shot")
            shot_data = b""
            if fn:
                while True:
                    ch = mp.read(262144)
                    if not ch:
                        break
                    shot_data += ch
            mp.finish()
            ff = mp.fields
            try:
                rs, cr = PACKS[int(ff.get("pack") or 0)]
            except Exception:
                return self._send(p_recharge(u, err="Pack sahi nahi"))
            utr = re.sub(r"\D", "", ff.get("utr") or "")
            if len(utr) != 12:
                return self._send(p_recharge(
                    u, err="UTR 12 digit ka hota hai"))
            if not shot_data:
                return self._send(p_recharge(
                    u, err="Payment screenshot zaroori hai"))
            if len(shot_data) < 2000:
                return self._send(p_recharge(
                    u, err="Screenshot theek nahi — dobara daalo"))
            dup = db.utr_exists(utr)
            if dup:
                return self._send(p_recharge(
                    u, err=f"Ye UTR pehle use ho chuka hai ({dup['ref']})"))
            ref = f"RX{u['id']}{int(time.time()) % 100000}"
            # screenshot storage server par
            ext = os.path.splitext(fn or "")[1].lower()
            if ext not in (".jpg", ".jpeg", ".png", ".webp"):
                ext = ".jpg"
            rel = f"payments/{ref}{ext}"
            try:
                a = storage.ensure_for_user(u)
                storage.save_bytes(a["id"], rel, shot_data)
            except Exception:
                rel = ""
            db.create_payment(u["id"], ref, rs, cr)
            db.set_payment(ref, utr=utr, shot=rel)
            # 🎉 sookhi line ki jagah jashn wala page
            return self._send(p_paid(u, ref, rs, cr))

        # 🗄️ STORAGE UPLOAD — koi size limit nahi (stream)
        if path == "/storage/upload":
            if not u:
                return self._go("/login")
            a = storage.ensure_for_user(u)
            clen = int(self.headers.get("Content-Length", 0) or 0)
            q = storage.quota_info(a["id"])
            if clen and clen > q["left"] + 4096:
                nx = theme.next_plan(q["plan"])
                em = (f"Jagah kam hai — {q['plan'].title()} plan me "
                      f"{q['cap_h']}, sirf {q['left_h']} bacha hai.")
                if nx:
                    em += f" {nx.title()} plan lo ({theme.storage_gb(nx)} GB)."
                self._drain(50 * 1024 * 1024)
                return self._go("/storage?err=" + urllib.parse.quote(em))
            mp = MultipartStream(self.rfile, self.headers)
            fn = mp.next_file("file")
            if not fn:
                return self._go("/storage?err=File+nahi+mili")
            safe = re.sub(r"[^A-Za-z0-9._-]", "_", fn)[:120] or "file"
            folder = re.sub(r"[^A-Za-z0-9_./-]", "",
                            mp.fields.get("folder", "")).strip("/")
            rel = f"{folder}/{safe}" if folder else safe
            res, err2 = storage.save_stream(a["id"], rel, mp)
            if not res:
                return self._go("/storage?err=" + urllib.parse.quote(err2))
            # folder field file ke BAAD aaya ho to ab path theek karo
            try:
                mp.finish()
                f2 = re.sub(r"[^A-Za-z0-9_./-]", "",
                            mp.fields.get("folder", "")).strip("/")
                if f2 and not folder:
                    if storage.move(a["id"], rel, f"{f2}/{safe}"):
                        rel = f"{f2}/{safe}"
            except Exception:
                pass
            return self._go("/storage?msg=" + urllib.parse.quote(
                f"{safe} upload ho gayi ({res['size_h']})"))

        if path == "/storage/token/reset":
            if not u:
                return self._go("/login")
            a = storage.ensure_for_user(u)
            storage.reset_token(a["id"])
            return self._go("/storage?msg=Naya+token+ban+gaya")

        # 📤 SERVER FILE UPLOAD — ♾️ koi size limit nahi (stream to disk)
        m = re.match(r"^/(?:server|app)/(\d+)/upload$", path)
        if m:
            if not u:
                return self._go("/login")
            sid = int(m.group(1))
            app_row = db.get_app(sid, u["id"])
            if not app_row:
                return self._go("/servers")

            # ⚠️⚠️ v1.2 — UPLOAD SE PEHLE SERVER CHECK ⚠️⚠️
            #
            # User ki shikayat: "upload button pe jaate hain to
            # vah dekhta hi nahin ki server hai ya nahin"
            #
            # Pehle sirf `db.get_app()` dekha jata tha — yaani
            # "database me row hai kya". Par row to expire hone
            # ke baad bhi rehti hai! Natija: user 50 MB file
            # upload karta tha, wo chali bhi jaati thi, aur baad
            # me pata chalta tha ki server to kab ka mar chuka.
            #
            # Ab asli haalat dekhte hain — expire/suspend to nahi.
            _dead = ""
            try:
                _st = (app_row.get("status") or "").lower()
                _exp = float(app_row.get("expires_at") or 0)
                if _st in ("expired", "deleted", "suspended"):
                    _dead = f"Ye server ab {_st} hai."
                elif _exp and _exp < time.time():
                    _dead = "Is server ka time khatam ho gaya hai."
            except Exception:
                pass
            if _dead:
                self._drain(50 * 1024 * 1024)
                return self._send(pages.p_server(
                    u, sid, err=_dead + " Pehle naya server "
                    "banaiye ya plan lijiye — tabhi file "
                    "upload hogi."))

            # 📏 Plan quota — upload shuru karne se pehle hi
            clen = int(self.headers.get("Content-Length", 0) or 0)
            okq, q = engine.quota_check(u["id"], clen)
            if not okq and q:
                nx = theme.next_plan(q["plan"])
                em = (f"Jagah kam hai — {q['plan'].title()} plan me "
                      f"{q['cap_h']} milta hai, {q['left_h']} bacha hai.")
                if nx:
                    em += (f" {nx.title()} plan lo "
                           f"({theme.storage_gb(nx)} GB) ya purani files "
                           f"hatao.")
                self._drain(50 * 1024 * 1024)
                return self._send(pages.p_server(u, sid, err=em))
            mp = MultipartStream(self.rfile, self.headers)
            fn = mp.next_file("file")
            if not fn:
                return self._send(pages.p_server(u, sid, err="File nahi mili"))
            okk, info = engine.save_upload_stream(u["id"], sid, fn, mp, clen)
            if not okk:
                return self._send(pages.p_server(u, sid, err=str(info)))
            if isinstance(info, dict) and info.get("lang"):
                db.update_app(sid, lang=info["lang"])
            # storage me bhi turant mirror
            try:
                threading.Thread(
                    target=storage.mirror_user_servers,
                    args=(u["id"],), daemon=True).start()
            except Exception:
                pass
            return self._send(pages.p_server(
                u, sid, msg=f"{fn} upload ho gaya"))

        f = self._form()

        # Admin-only FamGateway keyswitch: changes apply immediately without a restart.
        if path == "/admin/famgateway":
            ck = http.cookies.SimpleCookie(self.headers.get("Cookie", ""))
            tok = ck["rx_session"].value if "rx_session" in ck else ""
            if not (admin_unlocked(tok) or (u and u.get("role") == "admin")):
                return self._send("Admin authentication required", 403, "text/plain; charset=utf-8")
            new_key = (f.get("famgateway_api_key") or "").strip()
            enabled_value = "1" if (f.get("famgateway_enabled") or "0") == "1" else "0"
            if new_key:
                if len(new_key) < 20 or len(new_key) > 256 or any(ch.isspace() for ch in new_key):
                    return self._go("/admin?err=FamGateway+API+key+format+galat")
                db.set_setting("famgateway_api_key", new_key)
            db.set_setting("famgateway_enabled", enabled_value)
            return self._go("/admin?ok=FamGateway+settings+real-time+apply+ho+gayi")

        try:
            if path == "/signup":
                name = (f.get("name") or "").strip()
                email = (f.get("email") or "").strip().lower()
                pw = f.get("password") or ""
                phone = (f.get("phone") or "").strip()
                if len(name) < 2:
                    return self._send(p_signup("Naam chhota hai", f))
                if "@" not in email or "." not in email.split("@")[-1]:
                    return self._send(p_signup("Email sahi nahi hai", f))
                if len(pw) < 8:
                    return self._send(p_signup("Password 8 character ka ho", f))
                if db.get_by_email(email):
                    return self._send(p_signup(
                        "Ye email pehle se registered hai", f))

                # ═══ 📧 EMAIL VERIFY — pehla kadam ═══
                # Account ABHI NAHI banega. Pehle code sahi daalo,
                # tab banega. Isse fake email se signup nahi hoga.
                import mailer
                okm, via, dev = mailer.send_otp(email, name)
                if not okm:
                    return self._send(p_signup(
                        f"Code nahi bhej paye — {via}", f))
                PENDING_SIGNUP[email] = {
                    "name": name, "pw": pw, "phone": phone,
                    "btok": f.get("btok") or "", "at": time.time()}
                _clean_pending()
                return self._send(p_otp(email, dev=dev))

            # ═══ 📧 OTP CHECK — doosra kadam, account yahan banta hai ═══
            if path == "/verify-email":
                email = (f.get("email") or "").strip().lower()
                code = (f.get("code") or "").strip()

                # ── purana user login pe verify kar raha hai ──
                lp = PENDING_LOGIN.get(email)
                if lp:
                    import mailer
                    okc, msg = mailer.check_otp(email, code)
                    if not okc:
                        return self._send(p_otp(email, err=msg,
                                                login=True))
                    PENDING_LOGIN.pop(email, None)
                    db.update_user(lp["uid"], verified=1)
                    tok = db.new_session(lp["uid"], self._ip())
                    return self._send(
                        "", 302, redirect="/dashboard?hi=1",
                        cookie=f"rx_session={tok}; Path=/; HttpOnly; "
                               f"SameSite=Lax; Max-Age=2592000")

                pend = PENDING_SIGNUP.get(email)
                if not pend:
                    return self._send(p_signup(
                        "Session khatam ho gaya — dobara bhariye"))
                import mailer
                okc, msg = mailer.check_otp(email, code)
                if not okc:
                    return self._send(p_otp(email, err=msg))

                uid, err = db.create_user(email, pend["name"],
                                          pend["pw"], pend["phone"])
                if err:
                    PENDING_SIGNUP.pop(email, None)
                    return self._send(p_signup(err))
                PENDING_SIGNUP.pop(email, None)
                try:
                    db.update_user(uid, verified=1)
                except Exception:
                    pass
                try:
                    storage.ensure_for_user({"id": uid, "email": email})
                except Exception:
                    pass
                # swagat email — background me, signup rukna nahi chahiye
                try:
                    threading.Thread(
                        target=mailer.welcome,
                        args=(email, pend["name"]), daemon=True).start()
                except Exception:
                    pass
                tok = db.new_session(uid, self._ip())
                return self._send("", 302, redirect="/free?hi=1",
                    cookie=f"rx_session={tok}; Path=/; HttpOnly; "
                           f"SameSite=Lax; Max-Age=2592000")

            if path == "/resend-otp":
                email = (f.get("email") or "").strip().lower()
                lg = email in PENDING_LOGIN
                if email not in PENDING_SIGNUP and not lg:
                    return self._send(p_signup("Dobara bhariye"))
                import mailer
                nm = (PENDING_SIGNUP.get(email) or {}).get("name", "")
                okm, via, dev = mailer.send_otp(email, nm)
                if okm:
                    return self._send(p_otp(
                        email, ok="Naya code bhej diya", dev=dev,
                        login=lg))
                return self._send(p_otp(email, err=via, login=lg))

            if path == "/login":
                email = (f.get("email") or "").strip().lower()
                pw = f.get("password") or ""
                usr = db.get_by_email(email)
                if not usr or not db.check_pw(pw, usr["pass_hash"], usr["salt"]):
                    return self._send(p_login("Email ya password galat hai"))
                if usr["banned"]:
                    return self._send(p_login("Aapka account band hai"))

                # ═══ 📧 EMAIL VERIFY ZAROORI ═══
                #
                # Malik ka hukum: "ab sab verification se hi
                # aayenge, admin ko chhod kar".
                #
                # Purane users ka verified reset kar diya gaya
                # hai — unhe ek baar code daalna hoga. Uske
                # baad hamesha ke liye ho jayega.
                if not usr.get("verified") and usr.get("role") != "admin":
                    import mailer
                    okm, via, dev = mailer.send_otp(
                        email, usr.get("name", ""))
                    if not okm and "ruk" not in str(via).lower():
                        return self._send(p_login(
                            f"Code nahi bhej paye — {via}"))
                    PENDING_LOGIN[email] = {"uid": usr["id"],
                                            "at": time.time()}
                    _clean_pending()
                    return self._send(p_otp(email, dev=dev,
                                            login=True))

                tok = db.new_session(usr["id"], self._ip())
                return self._send("", 302, redirect="/dashboard?hi=1",
                    cookie=f"rx_session={tok}; Path=/; HttpOnly; "
                           f"SameSite=Lax; Max-Age=2592000")

            if not u:
                return self._go("/login")

            # 🎁 FREE SERVER — generate
            # 🎁 WEEKLY 10 CREDIT
            # 🌐 DOMAIN — logo ke saath wale chip se
            if path == "/admin/domain":
                if u.get("role") != "admin":
                    ck2 = http.cookies.SimpleCookie(
                        self.headers.get("Cookie", ""))
                    tk2 = (ck2["rx_session"].value
                           if "rx_session" in ck2 else "")
                    if not admin_unlocked(tk2):
                        return self._go("/dashboard")
                okd, dv = tunnel.save_domain(
                    str(f.get("domain") or "")[:120])
                ref = self.headers.get("Referer", "") or "/dashboard"
                if "?" in ref:
                    ref = ref.split("?")[0]
                if okd:
                    return self._go(ref + "?ok=" + urllib.parse.quote(
                        f"Domain PERMANENT set ho gaya: {dv}"))
                # ⚠️ Domain ek baar set = permanent (malik ka hukum)
                if str(dv).startswith("LOCKED:"):
                    return self._go(ref + "?err=" + urllib.parse.quote(
                        "Domain pehle se set hai: "
                        + dv[7:] + " — ab badla nahi ja sakta"))
                why = {"khali": "Domain khali nahi ho sakta",
                       "galat": "Domain sahi nahi lag raha",
                       "save-fail": "Save nahi ho paya"}.get(
                           dv, "Domain sahi nahi hai")
                return self._go(ref + "?err=" + urllib.parse.quote(why))

            if path == "/free/credits":
                ok2, msg2, amt = unlock.claim_weekly(u["id"])
                return self._go("/free?" + ("ok=" if ok2 else "err=")
                                + urllib.parse.quote(msg2))

            if path == "/free/start":
                if unlock.is_black(u["id"]):
                    return self._send(freeserver.p_blacklisted(u))
                if unlock.has_claimed(u["id"]):
                    return self._go("/free")
                if not unlock.stock()["available"]:
                    return self._send(freeserver.p_free(u, "Stock khatam"))
                code = unlock.start(u["id"], self._ip())
                unlock.mark_generated(code, u["id"])
                link, is_short, serr = unlock.short_url(
                    code, u["id"], public_base(self))
                if not link:
                    return self._send(freeserver.p_shorterr(u, serr))
                return self._send(freeserver.p_generated(
                    u, code, link, is_short))

            # 🎁 FREE SERVER — verify token
            if path == "/free/verify":
                if unlock.is_black(u["id"]):
                    return self._send(freeserver.p_blacklisted(u))
                _lk = unlock.server_lock(u["id"])
                if _lk["locked"]:
                    return self._send(freeserver.p_free(
                        u, _lk["why"] + " — "
                        + unlock.human_left(_lk["left_sec"]) + " baaki"))
                if unlock.has_claimed(u["id"]):
                    return self._go("/servers")
                tk = (f.get("token") or "").strip()
                ok, reason = unlock.verify(tk, u["id"], self._ip())
                if not ok:
                    if unlock.is_black(u["id"]):
                        return self._send(freeserver.p_blacklisted(u))
                    return self._send(freeserver.p_enter(
                        u, unlock.reason_text(reason)))
                # ✅ server banao
                base = re.sub(r"[^a-z0-9]", "",
                              u["name"].lower().split()[0])[:12]
                sname = (base or "myapp") + str(u["id"])
                sid = db.create_app(u["id"], sname, "—", FREE_PLAN, "mumbai")
                engine.server_dir(u["id"], sid)
                pl = plan_of(FREE_PLAN)
                engine.log(sid, "━" * 40, "ok")
                engine.log(sid, f"🎉 FREE SERVER UNLOCKED!", "ok")
                engine.log(sid, f"🖥 {sname} — {pl[1]} plan")
                engine.log(sid, f"📦 {pl[3]}MB RAM · {pl[4]} · {pl[6]}GB disk")
                engine.log(sid, f"🎁 Pehle {FREE_HOURS} ghante FREE", "ok")
                engine.log(sid, "━" * 40)
                engine.log(sid, "👉 Ab apni file upload karo", "warn")
                unlock.mark_claimed(u["id"])
                # ⏳ 24 ghante ki mohar — expiry.py isse pakdega
                db.set_expiry(sid, unlock.FREE_SERVER_HOURS, free=True)
                # 🔒 30 din tak dobara free server nahi
                unlock.lock_server(u["id"])
                db.update_user(u["id"], plan=FREE_PLAN)
                return self._send(freeserver.p_success(u, sid, sname))

            if path == "/admin/stock":
                ck = http.cookies.SimpleCookie(self.headers.get("Cookie", ""))
                tk = ck["rx_session"].value if "rx_session" in ck else ""
                if admin_unlocked(tk):
                    try:
                        unlock.FREE_STOCK = max(0, int(f.get("n") or 0))
                    except Exception:
                        pass
                return self._go("/admin?ok=Stock+update")

            # 🔐 ADMIN UNLOCK
            if path == "/admin/unlock":
                ip = self._ip()
                ck = http.cookies.SimpleCookie(self.headers.get("Cookie", ""))
                tok = ck["rx_session"].value if "rx_session" in ck else ""
                if admin_blocked(ip):
                    return self._send(live.p_admin_lock(
                        u, "Bahut galat try — 10 minute baad koshish karo"))
                if (f.get("pass") or "") == ADMIN_PASS:
                    ADMIN_TRY.pop(ip, None)
                    admin_unlock(tok)
                    return self._go("/admin/welcome")
                blocked = admin_fail(ip)
                return self._send(live.p_admin_lock(
                    u, "5 galat try — 10 minute block" if blocked
                    else "Galat password"))

            m = re.match(r"^/(?:server|app)/(\d+)/cmd$", path)
            if m:
                sid = int(m.group(1))
                if db.get_app(sid, u["id"]):
                    cmd = (f.get("cmd") or "").strip()[:400]
                    if cmd:
                        threading.Thread(
                            target=engine.run_cmd,
                            args=(u["id"], sid, cmd), daemon=True).start()
                ref = self.headers.get("Referer", "")
                return self._go(f"/console?s={sid}" if "/console" in ref
                                else f"/server/{sid}")

            if path in ("/servers/new", "/apps/new"):
                if unlock.is_black(u["id"]):
                    return self._send(freeserver.p_blacklisted(u))
                name = re.sub(r"[^a-zA-Z0-9_-]", "", f.get("name") or "")[:30]
                if len(name) < 2:
                    return self._send(pages.p_new_server(
                        u, "Naam me kam se kam 2 letter (a-z, 0-9, - _)"))
                pl = plan_of(f.get("plan") or "starter")
                if len(db.user_apps(u["id"])) >= pl[5]:
                    return self._send(pages.p_new_server(
                        u, f"{pl[1]} plan me max {pl[5]} servers. Upgrade karo."))
                if u["credits"] < CREDIT_RATE:
                    return self._send(pages.p_new_server(
                        u, f"Kam se kam {CREDIT_RATE} credits chahiye"))
                sid = db.create_app(u["id"], name, "—", pl[0],
                                    f.get("region") or "mumbai")
                engine.server_dir(u["id"], sid)
                engine.log(sid, "━" * 40, "ok")
                engine.log(sid, f"🎉 Server '{name}' ban gaya!", "ok")
                engine.log(sid, f"📦 Plan: {pl[1]} — {pl[3]}MB RAM, {pl[4]}")
                engine.log(sid, f"🌐 Region: {f.get('region','mumbai').title()}")
                engine.log(sid, f"💰 Rate: {CREDIT_RATE} credits/ghanta")
                engine.log(sid, "━" * 40)
                engine.log(sid, "👉 Ab apni file upload karo", "warn")
                return self._go(f"/server/{sid}")

            if path == "/files/new":
                sid = int(f.get("s") or 0)
                if db.get_app(sid, u["id"]):
                    nm = re.sub(r"[^A-Za-z0-9._/-]", "",
                                f.get("name") or "")[:60]
                    if nm:
                        engine.write_file(u["id"], sid, nm,
                                          f.get("content") or "")
                return self._go(f"/files?s={sid}")

            if path == "/files/save":
                sid = int(f.get("s") or 0)
                if db.get_app(sid, u["id"]):
                    engine.write_file(u["id"], sid, f.get("p") or "",
                                      f.get("content") or "")
                return self._go(f"/files?s={sid}")

            if path == "/__old_apps_new":
                name = re.sub(r"[^a-zA-Z0-9_-]", "", f.get("name") or "")[:40]
                if len(name) < 2:
                    return self._send(p_new_app(u, "Naam me kam se kam 2 "
                                                "letter (a-z, 0-9, - _)"))
                pl = plan_of(f.get("plan") or "starter")
                if len(db.user_apps(u["id"])) >= pl[5]:
                    return self._send(p_new_app(
                        u, f"{pl[1]} plan me max {pl[5]} apps. Upgrade karo."))
                aid = db.create_app(u["id"], name, f.get("lang") or "Python",
                                    pl[0], (f.get("repo") or "").strip()[:200])
                return self._go(f"/app/{aid}")

            if path == "/recharge":
                if unlock.is_black(u["id"]):
                    return self._send(freeserver.p_blacklisted(u))
                try:
                    rs, cr = PACKS[int(f.get("pack") or 0)]
                except Exception:
                    return self._send(p_recharge(u, err="Pack sahi nahi"))
                utr = re.sub(r"\D", "", f.get("utr") or "")
                if len(utr) != 12:
                    return self._send(p_recharge(u, err="UTR 12 digit ka hota hai"))
                dup = db.utr_exists(utr)
                if dup:
                    return self._send(p_recharge(
                        u, err=f"Ye UTR pehle use ho chuka hai ({dup['ref']})"))
                ref = f"RX{u['id']}{int(time.time()) % 100000}"
                db.create_payment(u["id"], ref, rs, cr)
                db.set_payment(ref, utr=utr)
                return self._go("/recharge?ok=Payment+submit+ho+gaya!+"
                                "Admin+verify+karke+credits+dega.")

            if path == "/profile":
                db.update_user(u["id"],
                               name=(f.get("name") or u["name"]).strip()[:60],
                               phone=(f.get("phone") or "").strip()[:15])
                return self._go("/profile?ok=Profile+update+ho+gaya")

            if path == "/password":
                old, new = f.get("old") or "", f.get("new") or ""
                if not db.check_pw(old, u["pass_hash"], u["salt"]):
                    return self._send(p_profile(u, "❌ Purana password galat hai"))
                if len(new) < 8:
                    return self._send(p_profile(u, "❌ Naya password 8+ ka ho"))
                h, salt = db.hash_pw(new)
                db.update_user(u["id"], pass_hash=h, salt=salt)
                return self._go("/profile?ok=Password+badal+gaya")

            if path == "/support":
                db.create_ticket(u["id"], f.get("subject") or "",
                                 f.get("message") or "")
                return self._go("/support?ok=Ticket+bhej+diya!+Jaldi+jawab+milega.")

            return self._go("/dashboard")

        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            print("POST ERROR:", tb, flush=True)
            try:
                open("/tmp/rx_err.log", "a").write(tb + "\n")
            except Exception:
                pass
            return self._send(page("Error", f"""<div class="auth"><div class="box tc">
<div style="font-size:56px">⚠️</div><h2>Error</h2>
<p class="s">{esc(str(e)[:120])}</p>
<a href="/" class="btn btn-p">Home</a></div></div>"""), 500)


def lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def main():
    db.init()
    # 🗄️ Storage engine — website ke andar hi, koi alag command nahi
    try:
        storage.boot()
    except Exception as e:
        print(f"  ⚠️  Storage: {e}")

    # ☁️ Cloud restore (Render/Railway par zaroori)
    cb = cloudsync.boot()
    if cb.get("ok"):
        print(f"  ☁️  Cloud: {cb.get('src')} — {cb.get('msg','')}")
        if cb.get("restored"):
            print("  ♻️  Database cloud se restore ho gaya")
        if cb.get("files"):
            print("  📂 Server files bhi restore")
    elif cloudsync.is_ephemeral():
        print("  ⚠️  EPHEMERAL platform + cloud nahi = DATA CHALA JAYEGA!")
        print("     UPSTASH_REDIS_REST_URL / _TOKEN env me daalo")
    G, C, B, N, D = ("\033[0;32m", "\033[0;36m", "\033[1m",
                     "\033[0m", "\033[2m")
    print(f"""{C}{B}
  ╔═══════════════════════════════════════════════╗
  ║      🌐  R A V A N   X   H O S T I N G        ║
  ║           Power · Speed · Uptime              ║
  ╚═══════════════════════════════════════════════╝{N}

  {G}✅{N} Database : {D}{db.DB_PATH}{N}
  {G}✅{N} Users    : {db.stats()['users']}
  {G}✅{N} Port     : {PORT}
  {G}✅{N} Platform : {cloudsync.platform_name()}
  {G}✅{N} Cloud    : {"ON ☁️" if cloudsync.configured() else "OFF (local only)"}

  {B}Kholo:{N}
    {C}http://localhost:{PORT}{N}
    {C}http://{lan_ip()}:{PORT}{N}  {D}(doosre device se){N}

  {D}Pehla signup = ADMIN ban jayega{N}
  {D}Band karne ke liye: Ctrl+C{N}
""")
    tunnel.on_change(on_tunnel_change)
    # 🤖 Bot se link — website ka URL bot tak pahunchta rahega
    try:
        botlink.boot()
        botlink.publish(force=True)
        bi = botlink.bot_info()
        if bi.get("username"):
            print(f"  🤖 Bot linked : @{bi['username']}")
        else:
            print("  🤖 Bot link   : ready (bot connect hote hi dikhega)")
    except Exception as e:
        print(f"  ⚠️  Bot link: {str(e)[:50]}")
    try:
        botlink.boot()
        bi = botlink.bot_info()
        if bi.get("username"):
            print(f"  🤖 Bot linked: @{bi['username']}")
    except Exception:
        pass

    dom = tunnel.domain()
    if dom:
        print(f"  🌐 Domain    : {dom}")
        print(f"  {DM}   (tunnel ki zarurat nahi — apna domain hai){N}"
              if False else "     (tunnel band — apna domain lag gaya)")
    elif os.environ.get("TUNNEL", "").lower() in ("1", "true", "yes"):
        threading.Thread(target=lambda: tunnel.enable(PORT),
                         daemon=True).start()
        threading.Thread(target=tunnel.keepalive, args=(PORT,),
                         daemon=True).start()
    threading.Thread(target=billing_loop, daemon=True).start()
    threading.Thread(target=cloudsync.sync_loop, daemon=True).start()
    srv = ThreadingHTTPServer((HOST, PORT), App)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n  👋 Band ho gaya\n")
        srv.shutdown()


if __name__ == "__main__":
    main()
