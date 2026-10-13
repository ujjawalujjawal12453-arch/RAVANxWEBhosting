"""
freeserver.py — 🎁 Free server unlock pages
════════════════════════════════════════════
Stock check → website link → GENERATE → shortener → token → server
"""

import time

import db
import engine
import theme
import unlock
from brand import ico, logo, donut
from theme import CREDIT_RATE, FREE_PLAN, FREE_HOURS, esc, page, dash_page


def _plan():
    for p in theme.PLANS:
        if p[0] == FREE_PLAN:
            return p
    return theme.PLANS[0]


# ══════════════════════════════════════════════
#   BLACKLIST NOTICE — har jagah dikhega
# ══════════════════════════════════════════════

def blacklist_banner(uid):
    if not unlock.is_black(uid):
        return ""
    b = unlock.black_info(uid) or {}
    return f"""<div class="blkban">
<div class="bi">{ico("shield",22)}</div>
<div><b>ACCOUNT BLACKLISTED</b>
<p>{esc(b.get('reason','Cheating detect hua'))} —
{time.strftime('%d %b, %H:%M', time.localtime(b.get('at', 0)))}</p>
<p class="xs">Free server, purchase aur recharge band hai.
Galti se hua ho to <a href="https://t.me/{theme.SUPPORT.lstrip('@')}">
support</a> se baat karo.</p></div></div>
<style>.blkban{{display:flex;gap:14px;padding:16px 18px;border-radius:14px;
background:linear-gradient(135deg,rgba(239,68,68,.14),rgba(239,68,68,.04));
border:1px solid rgba(239,68,68,.34);margin-bottom:20px;
animation:shake .5s var(--ease)}}
.blkban .bi{{color:#FF6B8A;flex-shrink:0}}
.blkban b{{color:#FF6B8A;font-size:15px;letter-spacing:.4px}}
.blkban p{{color:var(--dim);font-size:13.5px;margin-top:3px}}
.blkban a{{color:#FF8FA8;text-decoration:underline}}
@keyframes shake{{0%,100%{{transform:translateX(0)}}
25%{{transform:translateX(-5px)}}75%{{transform:translateX(5px)}}}}</style>"""


def p_blacklisted(u):
    b = unlock.black_info(u["id"]) or {}
    body = f"""<div class="auth"><div class="box" style="max-width:520px;
border-color:rgba(239,68,68,.34)">
<div class="bh"><div class="blkicon">{ico("shield",38)}</div>
<h2 style="color:#FF6B8A">Account Blacklisted</h2>
<p class="s">Ye action aapke liye band hai</p></div>
<div class="msg err">{ico("x",15)}<div>
<b>Wajah:</b> {esc(b.get('reason','Cheating detect hua'))}<br>
<span class="xs">{time.strftime('%d %B %Y, %H:%M',
time.localtime(b.get('at', 0)))}</span></div></div>
<div class="card flat" style="background:var(--bg2)">
<b class="sm">Kya band hai:</b>
<p class="dim sm mt2">{ico("x",13)} Free server</p>
<p class="dim sm">{ico("x",13)} Koi bhi purchase</p>
<p class="dim sm">{ico("x",13)} Credit recharge</p>
<p class="dim sm mt2" style="color:#22C55E">{ico("check",13)}
Purane servers chal rahe hain</p></div>
<a href="https://t.me/{theme.SUPPORT.lstrip('@')}" class="btn btn-g btn-b mt">
{ico("help",15)} Support se baat karo</a>
<a href="/dashboard" class="btn btn-g btn-b mt2">Dashboard</a>
</div></div>
<style>.blkicon{{width:80px;height:80px;border-radius:24px;margin:0 auto 6px;
display:grid;place-items:center;color:#FF6B8A;
background:linear-gradient(135deg,rgba(239,68,68,.16),transparent);
border:1px solid rgba(239,68,68,.3);animation:shake .6s var(--ease)}}
@keyframes shake{{0%,100%{{transform:translateX(0)}}
20%{{transform:translateX(-7px)}}60%{{transform:translateX(7px)}}}}</style>"""
    return page("Blacklisted", body, u)


# ══════════════════════════════════════════════
#   STEP 1 — stock check + start
# ══════════════════════════════════════════════

def _weekly_card(u):
    """
    🎁 Har 7 din me 10 credit ka card.

    ⚠️ Malik ka niyam: credit lene ke baad 30 din tak free
       SERVER nahi milega. Ye baat SAAF likhi honi chahiye —
       warna user ko dhokha lagega.
    """
    w = unlock.weekly_status(u["id"])
    lk = unlock.server_lock(u["id"])

    if lk["locked"]:
        badge = (f'<span class="bdg warn">{ico("lock",12)} '
                 f'Server lock — {unlock.human_left(lk["left_sec"])}</span>')
    else:
        badge = (f'<span class="bdg on">{ico("check",12)} '
                 f'Server bhi le sakte ho</span>')

    if w["can"]:
        btn = (f'<form method="POST" action="/free/credits" '
               f'style="margin-top:14px">'
               f'<button class="btn btn-p btn-b" type="submit">'
               f'{ico("gift",15)} {w["amount"]} Credit lo</button></form>')
        note = (f'<div class="msg warn mt2">{ico("info",15)}<div>'
                f'<b>Dhyaan se:</b> credit lete hi <b>'
                f'{w["lock_days"]} din</b> tak free SERVER nahi '
                f'milega. Dono ek saath nahi milte.</div></div>')
    else:
        btn = (f'<div class="card flat mt2" style="background:var(--bg2);'
               f'padding:14px;text-align:center">'
               f'<div class="dim2 xs">AGLA CREDIT</div>'
               f'<b style="font-size:18px">'
               f'{unlock.human_left(w["left_sec"])}</b></div>')
        note = ""

    return f"""<div class="card mb">
<div class="flex mb2" style="justify-content:space-between">
<h3>{ico("gift",18)} Har {w['days']} din — {w['amount']} credit muft</h3>
{badge}</div>
<p class="dim">Bina kuch kiye, har {w['days']} din me {w['amount']}
credit wallet me. Ye {w['amount'] // 2} ghante hosting ke barabar hai.</p>
{note}{btn}</div>"""


def p_free(u, err=""):
    if unlock.is_black(u["id"]):
        return p_blacklisted(u)

    st = unlock.stock()
    pl = _plan()
    e = (f'<div class="msg err">{ico("x",15)}<div>{esc(err)}</div></div>'
         if err else "")

    wk = _weekly_card(u)
    lk = unlock.server_lock(u["id"])

    # 🔒 Credit le liya = 30 din server band
    if lk["locked"]:
        content = e + wk + f"""<div class="card empty">
<div class="ei" style="color:#F59E0B">{ico("lock",30)}</div>
<h3>Free server abhi lock hai</h3>
<p>{esc(lk['why'])}.<br>
<b>{unlock.human_left(lk['left_sec'])}</b> baaki hain.</p>
<div class="flex" style="justify-content:center">
<a href="/servers/new" class="btn btn-p">{ico("rocket",15)} Paid Plan lo</a>
<a href="/billing" class="btn btn-g">{ico("wallet",15)} Wallet</a>
</div></div>"""
        return dash_page("Free Server", "Lock hai", content, u, "free")

    if unlock.has_claimed(u["id"]):
        content = wk + f"""<div class="card empty">
<div class="ei" style="color:#22C55E">{ico("check",30)}</div>
<h3>Free server pehle hi mil chuka hai</h3>
<p>Ek account = ek free server. Aur chahiye to plan lo.</p>
<a href="/servers" class="btn btn-p">{ico("server",15)} Mere Servers</a>
</div>"""
        return dash_page("Free Server", "Already claimed", content, u, "free")

    if not st["available"]:
        content = wk + f"""<div class="card empty">
<div class="ei" style="color:#8B5CF6">{ico("clock",30)}</div>
<h3>Abhi stock khatam hai</h3>
<p>Saare {st['total']} free servers busy hain.
Thodi der baad try karo — ya paid plan lo (turant milta hai).</p>
<div class="flex" style="justify-content:center">
<a href="/free" class="btn btn-g">{ico("refresh",15)} Dobara check</a>
<a href="/servers/new" class="btn btn-p">{ico("rocket",15)} Paid Plan</a>
</div></div>"""
        return dash_page("Free Server", "Stock khatam", content, u, "free")

    content = f"""{e}{wk}
<div class="grid g32 mb">
<div class="card tc">
{donut(st['percent'], 150, 13, "#7C3AED",
label=str(st['left']), sub="bache hain")}
<div class="dim2 xs mt2">{st['used']} / {st['total']} claim ho chuke</div>
</div>
<div class="card">
<div class="flex mb2"><span class="bdg on">{ico("check",12)} STOCK AVAILABLE</span></div>
<h3 style="font-size:20px">Free {pl[1]} Server</h3>
<p class="dim mt2">Ek chhota sa task karo, server free me le jao.</p>
<div class="grid g2 mt" style="gap:10px">
<div class="card flat" style="background:var(--bg2);padding:13px">
<div class="dim2 xs">RAM</div><b>{pl[3]} MB</b></div>
<div class="card flat" style="background:var(--bg2);padding:13px">
<div class="dim2 xs">CPU</div><b>{pl[4]}</b></div>
<div class="card flat" style="background:var(--bg2);padding:13px">
<div class="dim2 xs">DISK</div><b>{pl[6]} GB</b></div>
<div class="card flat" style="background:var(--bg2);padding:13px">
<div class="dim2 xs">FREE TIME</div><b>{FREE_HOURS} ghante</b></div>
</div></div></div>

<div class="card mb"><h3 class="mb2">{ico("gift",18)} Kaise milega</h3>
<div class="steps">
<div class="step now"><div class="n">1</div><div class="sc">
<b>Stock check</b><p>Abhi <b style="color:#22C55E">{st['left']} servers</b>
available hain ✅</p></div></div>
<div class="step"><div class="n">2</div><div class="sc">
<b>Generate dabao</b><p>Neeche wala button — ek link banegi</p></div></div>
<div class="step"><div class="n">3</div><div class="sc">
<b>Link complete karo</b><p>{unlock.SHORTENER['name']} par 2-3 step,
15-20 second ka kaam</p></div></div>
<div class="step"><div class="n">4</div><div class="sc">
<b>Token milega</b><p>Wapas aake token daalo — server ready</p>
</div></div></div></div>

<div class="msg warn">{ico("shield",15)}<div>
<b>⚠️ Dhyan se padho</b><br>
Link skip karne ki koshish, fake token, ya seedha endpoint hit karna —
kuch bhi galat kiya to account <b>permanently blacklist</b> ho jayega.
Phir kabhi free server nahi milega, na kuch buy kar paoge.</div></div>

<form method="POST" action="/free/start">
<button class="btn btn-p btn-lg btn-b" style="max-width:340px;margin:0 auto">
{ico("bolt",17)} GENERATE LINK</button></form>"""

    return dash_page("Free Server", f"{st['left']} servers available",
                     content, u, "free")


# ══════════════════════════════════════════════
#   STEP 2 — link generate ho gayi
# ══════════════════════════════════════════════

def p_generated(u, code, link, is_short):
    content = f"""<div class="card glow mb tc" style="padding:34px">
<div class="genicon">{ico("bolt",34)}</div>
<h3 style="font-size:21px;margin-top:12px">Link ready hai!</h3>
<p class="dim mt2">Neeche wale button se link kholo, complete karo,
phir token yahan daalo.</p>
<a href="{link}" target="_blank" rel="noopener"
class="btn btn-p btn-lg mt" style="min-width:280px">
{ico("globe",17)} LINK KHOLO {ico("up",15)}</a>
<p class="dim2 xs mt2">{ico("globe",12)}
{f"{unlock.SHORTENER['domain']} par jayega — 2-3 step" if is_short
 else "TEST MODE — localhost par shortener nahi chalta"}</p>
<div class="linkbox">{esc(link[:56])}</div>
</div>

<div class="card mb"><h3 class="mb2">{ico("clock",18)} Ab kya karna hai</h3>
<div class="steps">
<div class="step done"><div class="n">{ico("check",14)}</div><div class="sc">
<b>Link generate</b><p>Ho gaya</p></div></div>
<div class="step now"><div class="n">2</div><div class="sc">
<b>Link complete karo</b><p>Upar wala button dabao, saare step karo</p>
</div></div>
<div class="step"><div class="n">3</div><div class="sc">
<b>Token copy karo</b><p>Last page par token milega</p></div></div>
<div class="step"><div class="n">4</div><div class="sc">
<b>Neeche daalo</b><p>Server turant ban jayega</p></div></div></div></div>

<div class="card"><h3 class="mb2">{ico("key",18)} Token daalo</h3>
<form method="POST" action="/free/verify">
<div class="fld">
<input name="token" required placeholder="ABCD1234EF-xxxxxxxxxxxxxxxx"
style="font-family:monospace;font-size:15px;letter-spacing:.5px" autofocus>
<div class="hint">{ico("shield",12)} Link complete kiye bina token daaloge
to blacklist ho jaoge</div></div>
<button class="btn btn-p btn-b">{ico("check",16)} Verify karo</button>
</form>
<div class="mt2 tc"><a href="/free" class="dim2 xs">
{ico("refresh",12)} Nayi link chahiye?</a></div></div>

<style>.linkbox{{background:var(--bg2);border:1px solid var(--line);
border-radius:9px;padding:9px 13px;margin:14px auto 0;max-width:420px;
font-family:monospace;font-size:11.5px;color:var(--dim);
word-break:break-all}}
.genicon{{width:74px;height:74px;border-radius:22px;margin:0 auto;
display:grid;place-items:center;color:var(--acc3);
background:linear-gradient(135deg,rgba(124,58,237,.2),transparent);
border:1px solid rgba(124,58,237,.3);animation:pulse2 2s infinite}}
@keyframes pulse2{{0%,100%{{transform:scale(1)}}50%{{transform:scale(1.05)}}}}
</style>"""
    return dash_page("Link Ready", "Complete karo aur token lao",
                     content, u, "free")


def p_shorterr(u, err=""):
    """Shortener fail — server nahi milega."""
    content = f"""<div class="card empty" style="border-color:rgba(245,158,11,.3)">
<div class="ei" style="color:#8B5CF6">{ico("globe",30)}</div>
<h3>Link nahi ban paayi</h3>
<p>{unlock.SHORTENER['name']} abhi respond nahi kar raha.<br>
<span class="dim2 xs">{esc(err) if err else 'Network problem'}</span></p>
<div class="msg warn" style="text-align:left;max-width:420px;margin:16px auto">
{ico("shield",15)}<div>Security ke liye bina shortener complete kiye
server nahi milta. Thodi der baad try karo.</div></div>
<div class="flex" style="justify-content:center">
<a href="/free" class="btn btn-p">{ico("refresh",15)} Dobara try</a>
<a href="https://t.me/{theme.SUPPORT.lstrip('@')}" class="btn btn-g">
{ico("help",15)} Support</a></div></div>"""
    return dash_page("Link Error", "Shortener respond nahi kar raha",
                     content, u, "free")


# ══════════════════════════════════════════════
#   STEP 3 — token page (shortener ke baad)
# ══════════════════════════════════════════════

def p_token(u, token):
    content = f"""<div class="card glow tc" style="padding:40px">
<div class="genicon" style="color:#22C55E;
background:linear-gradient(135deg,rgba(34,197,94,.18),transparent);
border-color:rgba(34,197,94,.3)">{ico("check",34)}</div>
<h3 style="font-size:22px;margin-top:14px">Ye raha aapka token</h3>
<p class="dim mt2">Copy karke website par daal do</p>
<div class="tokbox" onclick="cp()">
<code id="tk">{esc(token)}</code>
<span class="dim2 xs">{ico("code",12)} tap = copy</span></div>
<div id="cpok" class="xs" style="color:#22C55E;height:16px"></div>
<a href="/free/enter" class="btn btn-p btn-lg mt">
{ico("rocket",17)} Server Banao</a></div>
<style>.tokbox{{background:var(--bg2);border:1px dashed var(--acc);
border-radius:12px;padding:16px;margin:20px auto;max-width:420px;
cursor:pointer;transition:.2s}}
.tokbox:hover{{background:var(--card2);border-style:solid}}
.tokbox code{{display:block;font-size:15px;word-break:break-all;
margin-bottom:6px;background:none;border:0;color:var(--acc3)}}</style>
<script>
function cp(){{
 var t=document.getElementById('tk').textContent;
 navigator.clipboard.writeText(t).then(function(){{
  document.getElementById('cpok').textContent='✓ Copy ho gaya!'}})
 .catch(function(){{document.getElementById('cpok').textContent=
  'Manually copy karo'}});
}}
</script>"""
    return dash_page("Token Ready", "Copy karke aage badho", content, u, "free")


def p_enter(u, err=""):
    if unlock.is_black(u["id"]):
        return p_blacklisted(u)
    e = (f'<div class="msg err">{ico("x",15)}<div>{esc(err)}</div></div>'
         if err else "")
    content = f"""{e}<div class="card" style="max-width:520px;margin:0 auto">
<h3 class="mb2">{ico("key",18)} Token daalo</h3>
<form method="POST" action="/free/verify">
<div class="fld"><input name="token" required autofocus
placeholder="ABCD1234EF-xxxxxxxxxxxxxxxx"
style="font-family:monospace;font-size:15px"></div>
<button class="btn btn-p btn-b btn-lg">{ico("check",16)} Server Banao</button>
</form></div>"""
    return dash_page("Token", "Aakhri step", content, u, "free")


def p_success(u, sid, sname):
    body = f"""<div class="succwrap">
<div class="sring"><div class="sicon">{ico("check",44)}</div></div>
<h1>Server ready hai!</h1>
<p><b>{esc(sname)}</b> ban gaya — {FREE_HOURS} ghante free</p>
<div class="sload"><i></i></div>
<p class="dim2 xs mt">Server page khul raha hai…</p></div>
<style>
.succwrap{{min-height:calc(100vh - 68px);display:grid;place-items:center;
align-content:center;gap:5px;text-align:center;animation:fadein .4s}}
.sring{{width:120px;height:120px;border-radius:50%;display:grid;
place-items:center;margin-bottom:18px;position:relative;
background:radial-gradient(circle,rgba(34,197,94,.2),transparent 70%)}}
.sring::before{{content:'';position:absolute;inset:0;border-radius:50%;
border:2.5px solid transparent;border-top-color:#22C55E;
border-right-color:#22C55E;animation:spin 1s linear infinite}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
.sicon{{color:#22C55E;animation:pop .6s var(--ease)}}
@keyframes pop{{from{{transform:scale(0);opacity:0}}
60%{{transform:scale(1.18)}}}}
.succwrap h1{{font-size:32px;font-weight:840;letter-spacing:-1px;
background:linear-gradient(120deg,#22C55E,var(--acc3));
-webkit-background-clip:text;-webkit-text-fill-color:transparent;
animation:su .5s .12s both}}
.succwrap p{{color:var(--dim);animation:su .5s .2s both}}
.sload{{width:240px;height:4px;background:var(--card2);border-radius:99px;
overflow:hidden;margin-top:20px}}
.sload i{{display:block;height:100%;border-radius:99px;
background:linear-gradient(90deg,#22C55E,var(--acc));
animation:fill 1.6s var(--ease) forwards}}
@keyframes fill{{from{{width:0}}to{{width:100%}}}}
@keyframes fadein{{from{{opacity:0}}}}
@keyframes su{{from{{transform:translateY(16px);opacity:0}}}}
</style>
<script>setTimeout(function(){{location.href='/server/{sid}'}},1800);</script>"""
    return page("Server Ready", body, u)
