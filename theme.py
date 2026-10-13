"""
theme.py — RAVAN X CLOUD ka poora UI
═════════════════════════════════════
Modern dark theme, inline CSS (koi CDN nahi — offline bhi chalega).
"""

import brand
import icon as appicon
from brand import ico, logo, sparkline, minibars, donut, gauge, areachart, multichart

BRAND = "RAVAN X HOSTING"
TAGLINE = "Power · Speed · Uptime"
SUPPORT = "@UjjawalXsarkar"
CHANNEL = "officialxujjawal"
UPI_ID = "9098219576-2@ybl"
UPI_NAME = "Sanjay Verma"

# 💰 Website par 1 ghanta = 2 credits (bot me 1)
#    Wajah: yahan asli server, bandwidth, management team ka kharcha hai
CREDIT_RATE = 2

# 🔐 Admin password — sirf ye daalne wala admin panel me ghusega
#    Env se badlo: ADMIN_PASS=meranaya
import os as _os
ADMIN_PASS = _os.environ.get("ADMIN_PASS", "ravanx2026")

# 🎁 Signup par: koi credits nahi, seedha ek FREE starter server
FREE_PLAN = "starter"
FREE_HOURS = 24          # pehle 24 ghante free (credits nahi katenge)

PLANS = [
    ("starter", "Starter", 149, 512, "1 vCPU", 2, 5,
     ["512 MB RAM", "1 vCPU", "2 apps", "5 GB storage", "Daily backup",
      "Community support"]),
    ("pro", "Pro", 399, 1024, "2 vCPU", 5, 15,
     ["1 GB RAM", "2 vCPU", "5 apps", "15 GB storage", "Auto backup",
      "Priority support", "Custom domain"]),
    ("ultra", "Ultra", 799, 2048, "4 vCPU", 12, 40,
     ["2 GB RAM", "4 vCPU", "12 apps", "40 GB storage", "Hourly backup",
      "24/7 support", "Custom domain", "SSL free"]),
    ("business", "Business", 1499, 4096, "8 vCPU", 30, 100,
     ["4 GB RAM", "8 vCPU", "30 apps", "100 GB storage", "Realtime backup",
      "Dedicated manager", "Custom domain", "SSL + CDN"]),
]

PACKS = [(149, 150), (399, 420), (799, 900), (1499, 1800), (2999, 3800)]

# 🗄️ STORAGE — plan ke hisaab se jagah (GB)
#    Yahi limit hai. Isse zyada file upload nahi hogi.
STORAGE_GB = {
    "free":     1,      # signup par
    "starter":  5,
    "pro":      15,
    "ultra":    40,
    "business": 100,
}


def storage_gb(plan):
    return STORAGE_GB.get(plan or "free", STORAGE_GB["free"])


def next_plan(plan):
    """Agla bada plan — 'jagah kam hai' wale message ke liye."""
    order = ["free", "starter", "pro", "ultra", "business"]
    try:
        i = order.index(plan or "free")
    except ValueError:
        i = 0
    return order[i + 1] if i + 1 < len(order) else None


from css import CSS



def _voice_engine():
    try:
        import voice
        return voice.engine()
    except Exception:
        return ""


def _voice_btn():
    try:
        import voice
        return voice.button()
    except Exception:
        return ""


def _jv_link(user):
    """🤖 JARVIS page ka shortcut — navbar me."""
    if not user:
        return ""
    return (f'<a href="/admin/jarvis" class="jvlink" '
            f'title="JARVIS Control Room">{ico("bolt", 16)}</a>')


def _mic_all():
    try:
        import voice
        return voice.mic_engine() + voice.mic_panel()
    except Exception:
        return ""


def _voice_css():
    try:
        import voice
        return f"<style>{voice.css()}</style>"
    except Exception:
        return ""


def esc(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def page(title, body, user=None, active="", extra_head=""):
    if user:
        nav = f'''<a href="/dashboard">{ico("grid",15)} Dashboard</a>
        <a href="/servers">{ico("server",15)} Servers</a>
        <a href="/console">{ico("term",15)} Console</a>
        <a href="/admin">{ico("crown",15)} Admin</a>
        <a href="/logout" class="btn btn-g btn-sm">{ico("logout",14)} Logout</a>'''
    else:
        nav = '''<a href="/#features">Features</a><a href="/#pricing">Pricing</a>
        <a href="/#compare">Compare</a><a href="/#faq">FAQ</a>
        <a href="/login">Login</a>
        <a href="/signup" class="btn btn-p btn-sm">Get Started →</a>'''

    return f"""<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#05080f">
<title>{esc(title)} — {BRAND}</title>
<meta name="description" content="{TAGLINE} — 99.9% uptime, instant deploy,
India ke servers. Bots aur apps 24/7 online rakho.">
{appicon.favicon_tag()}
<style>{CSS}</style>{_voice_css()}{extra_head}</head><body>
{_voice_engine()}{_mic_all()}
<nav><div class="wrap">
<a href="/" class="lg">{appicon.img(34)}
<span class="ltx"><b>RAVAN</b><em>X</em><span class="lsub">HOSTING</span></span></a>
{_dom_chip(user)}
<button class="burger" onclick="document.querySelector('.nlinks').classList.toggle('open')">
{ico("menu",21)}</button>
<div class="nlinks">{nav}</div>
{_voice_btn()}{dotmenu(user, active)}
</div></nav>
{body}
{dotpanel(user, active)}
{_dom_box(user)}
{_tab_if_needed(body, user, active)}
</body></html>"""


def _dom_chip(user):
    """
    🌐 DOMAIN — logo ke bilkul saath, sabse upar.

    Malik ka hukum: "domain daalne ka option sabse top par,
    jahan RAVAN X ka logo aata hai wahin per".

    Sirf ADMIN ko dikhta hai. Ek tap = popup, domain daalo,
    save. Restart ki zarurat nahi.
    """
    if not user or user.get("role") != "admin":
        return ""
    try:
        import tunnel
        d = tunnel.domain()
        saved = tunnel.saved_domain()
    except Exception:
        d, saved = "", ""

    if d:
        show = d.replace("https://", "").replace("http://", "")
        if len(show) > 22:
            show = show[:20] + "…"
        cls, ic = "dchip live", "globe"
    else:
        show = "Domain daalo"
        cls, ic = "dchip", "plus"

    return (f'<button class="{cls}" onclick="domOpen()" '
            f'title="Apna domain set karo">{ico(ic,13)}'
            f'<span>{esc(show)}</span></button>')


def _dom_box(user):
    """
    🌐 Domain wala popup — <body> ke seedha andar.

    ⚠️ ZAROORI: ye <nav> ke ANDAR nahi ja sakta. Nav pe
       `backdrop-filter: blur()` laga hai, aur CSS ka niyam hai
       ki aisa parent `position:fixed` ko apne andar phansa
       deta hai. Isi wajah se popup screen se bahar (top=-247)
       chala gaya tha aur "Save karo" button dikhta hi nahi tha.
       Isliye chip nav me, popup body me — alag-alag.
    """
    if not user or user.get("role") != "admin":
        return ""
    try:
        import tunnel
        d = tunnel.domain()
        saved = tunnel.saved_domain()
    except Exception:
        d, saved = "", ""

    lock = False
    try:
        import tunnel as _t
        lock = _t.locked()
    except Exception:
        pass

    if lock:
        # 🔒 Domain PERMANENT ho chuka — ab badal nahi sakta
        inner = f'''<div class="domlock">{ico("lock",30)}
<b>Domain permanent set hai</b>
<div class="domval">{esc(d)}</div>
<p class="dim sm">Ye ab badla nahi ja sakta — ek baar set,
hamesha ke liye. Poori website ke link isi pe bane hain.</p>
<p class="dim2 xs">Sach me badalna hai? Server par
<code>data/domain.txt</code> file delete karke restart
karna hoga.</p></div>'''
    else:
        inner = f'''<p class="dim sm">Render pe deploy karne ke baad
wahan se jo link milta hai, wo yahan paste kar dijiye.</p>
<div class="msg warn" style="margin-top:11px">{ico("info",15)}
<div><b>Dhyaan se —</b> ek baar set hone ke baad domain
<b>PERMANENT</b> ho jayega. Phir badal nahi paoge.</div></div>
<form method="POST" action="/admin/domain">
<input name="domain" class="dominp" autocomplete="off"
placeholder="ravanx-hosting.onrender.com" required>
<p class="dim2 xs">https:// mat likhiye — sirf naam.</p>
<button class="btn btn-p btn-b" style="margin-top:12px">
{ico("check",15)} Permanent set karo</button>
</form>'''

    return f'''<div class="dombg" id="dombg" onclick="domClose()"></div>
<div class="dombox" id="dombox">
<div class="domh">{ico("globe",17)} <b>Apna Domain</b>
{'<span class="bdg on" style="margin-left:8px;font-size:10px">LOCKED</span>'
 if lock else ''}
<button onclick="domClose()">{ico("x",16)}</button></div>
<div class="domb">{inner}</div></div>

<script>
function domOpen(){{document.getElementById('dombox').classList.add('on');
document.getElementById('dombg').classList.add('on');
setTimeout(function(){{var i=document.querySelector('.dominp');
if(i)i.focus()}},150);}}
function domClose(){{document.getElementById('dombox').classList.remove('on');
document.getElementById('dombg').classList.remove('on');}}
</script>'''


def _tab_if_needed(body, user, active):
    """
    📱 Bottom bar har logged-in page pe.

    ⚠️ dash_page() khud bottombar() laga deta hai. Par kuch pages
       (jaise /boss) seedha page() use karte hain — wahan bottom
       bar gayab tha. Mobile test me ye pakda gaya (btab=0px).
       Ab yahan check kar lete hain: pehle se hai to dobara mat
       lagao, warna laga do.
    """
    if not user:
        return ""
    if '<div class="mnav">' in body:
        return ""
    return bottombar(active) + _sd_js()


def footer():
    return f"""<footer><div class="wrap"><div class="fg">
<div>{logo(30, sub=True)}
<p class="mt2" style="max-width:300px">{TAGLINE}. Apne bots aur apps ko
24/7 online rakho — bina server ki tension ke.</p>
<div class="flex mt2">
<span class="bdg on nd">{ico("check",12)} 99.9% Uptime</span>
<span class="bdg info nd">{ico("globe",12)} India Servers</span></div></div>
<div><h4>Product</h4><a href="/#features">Features</a>
<a href="/#pricing">Pricing</a><a href="/#compare">Compare</a>
<a href="/signup">Sign Up</a><a href="/login">Login</a></div>
<div><h4>Support</h4>
<a href="https://t.me/{SUPPORT.lstrip('@')}">Telegram Support</a>
<a href="https://t.me/{CHANNEL}">Updates Channel</a>
<a href="/#faq">FAQ</a><a href="/status">Status</a></div>
<div><h4>Legal</h4><a href="/terms">Terms</a><a href="/privacy">Privacy</a>
<a href="/refund">Refund</a><a href="/sla">SLA</a></div></div>
<div class="fbot"><span>© 2026 {BRAND} · Made by
<b style="color:var(--dim)">Ujjawal X Official</b></span>
<span>{SUPPORT}</span></div></div></footer>"""


def sidebar(active, user):
    """10 pages + live balance card."""
    items = [
        ("OVERVIEW", None, None, None),
        ("Dashboard",     "/dashboard",   "dashboard", "grid"),
        ("My Servers",    "/servers",     "servers",   "server"),
        ("Deploy New",    "/servers/new", "new",       "plus"),
        ("Free Server",   "/free",        "free",      "gift"),
        ("MANAGE", None, None, None),
        ("File Manager",  "/files",       "files",     "folder"),
        ("My Storage",    "/storage",     "storage",   "db"),
        ("Live Console",  "/console",     "console",   "term"),
        ("Analytics",     "/analytics",   "analytics", "chart"),
        ("Live System",   "/system",      "system",    "cpu"),
        ("BILLING", None, None, None),
        ("Wallet",        "/billing",     "billing",   "wallet"),
        ("Add Credits",   "/recharge",    "recharge",  "card"),
        ("ACCOUNT", None, None, None),
        ("Profile",       "/profile",     "profile",   "user"),
        ("Support",       "/support",     "support",   "help"),
    ]
    items += [("ADMIN", None, None, None),
              ("JARVIS", "/admin/jarvis", "jarvis", "bolt"),
              ("Control Panel", "/admin", "admin", "crown")]

    cr = user.get("credits", 0)
    hrs = int(cr // CREDIT_RATE)
    bal = f'''<div class="bal"><div class="l">Balance</div>
<div class="v">{cr:.0f} <span style="font-size:12px;color:var(--dim);
font-weight:500">cr</span></div>
<div class="xs dim">≈ {hrs} ghante hosting</div>
<a href="/recharge" class="btn btn-p btn-sm btn-b" style="margin-top:9px">
{ico("plus",13)} Add Credits</a></div>'''

    # 📱 Mobile drawer ka header — band karne ka button
    out = ['<div class="sdclose"><b>Menu</b>'
           '<button onclick="sdT()" aria-label="Band karo">'
           + ico("x", 18) + '</button></div>', bal]
    for label, href, key, icn in items:
        if href is None:
            out.append(f'<div class="hd">{label}</div>')
        else:
            on = " on" if key == active else ""
            out.append(f'<a href="{href}" class="{on.strip()}">'
                       f'{ico(icn,17)} {label}</a>')
    return f'<aside class="side">{"".join(out)}</aside>'


# ═══════════════════════════════════════════════
#   ⋮  THREE-DOT MENU — saare functions ek jagah
# ═══════════════════════════════════════════════

MENU = [
    ("OVERVIEW", [
        ("Dashboard",     "/dashboard",   "grid",    "Sab kuch ek nazar me"),
        ("My Servers",    "/servers",     "server",  "Aapke saare servers"),
        ("Deploy New",    "/servers/new", "plus",    "Naya server banao"),
        ("Free Server",   "/free",        "gift",    "Muft server — link se"),
    ]),
    ("MANAGE", [
        ("File Manager",  "/files",       "folder",  "Files dekho, edit karo"),
        ("My Storage",    "/storage",     "db",      "Apna storage + token"),
        ("Live Console",  "/console",     "term",    "Live output dekho"),
        ("Analytics",     "/analytics",   "chart",   "Graph aur stats"),
        ("Live System",   "/system",      "cpu",     "CPU/RAM/disk/network"),
    ]),
    ("AI", [
        ("AI Boss",       "/boss",        "crown",   "90 model · chat karo"),
        ("Boss Agent",    "/boss#agent",  "search",
                                          "File khud theek kare"),
        ("Code Doctor",   "/servers",     "shield",  "Error fix karo"),
    ]),
    ("BILLING", [
        ("Wallet",        "/billing",     "wallet",  "Balance aur history"),
        ("Add Credits",   "/recharge",    "card",    "UPI se recharge"),
        ("Pricing",       "/#pricing",    "star",    "Saare plans dekho"),
    ]),
    ("ACCOUNT", [
        ("Profile",       "/profile",     "user",    "Naam, phone, password"),
        ("Support",       "/support",     "help",    "Ticket banao"),
        ("Status",        "/status",      "bolt",    "Sab chalu hai?"),
    ]),
    ("ADMIN", [
        ("JARVIS",        "/admin/jarvis", "bolt",   "Bol kar control karo"),
        ("Control Panel", "/admin",        "crown",  "Users, payments, tunnel"),
    ]),
    ("LEGAL", [
        ("Terms",         "/terms",       "file",    "Shartein"),
        ("Privacy",       "/privacy",     "shield",  "Aapka data"),
        ("Refund",        "/refund",      "refresh", "Paisa wapas policy"),
        ("SLA",           "/sla",         "check",   "Uptime guarantee"),
    ]),
]


def dotmenu(user=None, active=""):
    """
    ⋮ Teen-dot menu — website ke SAARE functions ek hi jagah.
    Har page par upar-daayein milega.
    """
    groups = []
    for title, rows in MENU:
        cells = []
        for label, href, icn, desc in rows:
            on = " on" if href.strip("/#") == active else ""
            cells.append(
                f'<a href="{href}" class="dmi{on}">'
                f'<span class="dmic">{ico(icn, 16)}</span>'
                f'<span class="dmt"><b>{esc(label)}</b>'
                f'<i>{esc(desc)}</i></span></a>')
        groups.append(
            f'<div class="dmg"><div class="dmh">{title}</div>'
            f'<div class="dmr">{"".join(cells)}</div></div>')

    if user:
        foot = (f'<div class="dmf">'
                f'<a href="/logout" class="btn btn-g btn-sm">'
                f'{ico("logout", 13)} Logout</a>'
                f'<span class="dim xs">{esc(user.get("email", ""))}</span>'
                f'</div>')
    else:
        foot = (f'<div class="dmf">'
                f'<a href="/login" class="btn btn-g btn-sm">'
                f'{ico("user", 13)} Login</a>'
                f'<a href="/signup" class="btn btn-p btn-sm">'
                f'{ico("rocket", 13)} Sign Up</a></div>')

    js = (
        "function dmT(){"
        "var p=document.getElementById('dmp'),"
        "b=document.getElementById('dmbk'),n=document.getElementById('dmb');"
        "var o=p.classList.toggle('on');b.classList.toggle('on',o);"
        "n.classList.toggle('on',o);"
        "document.body.style.overflow=o?'hidden':'';}"
        "document.addEventListener('keydown',function(e){"
        "if(e.key==='Escape'){var p=document.getElementById('dmp');"
        "if(p&&p.classList.contains('on'))dmT();}});"
    )

    # ⚠️ SIRF BUTTON yahan. Panel <nav> ke BAHAR jata hai.
    #
    #    Wajah: nav pe `backdrop-filter: blur(22px)` laga hai.
    #    CSS ka niyam — aisa parent `position:fixed` ko apne
    #    andar PHANSA deta hai. Isliye panel nav ki chaudai me
    #    kaid ho jata tha aur phone pe (khaaskar "Desktop site"
    #    mode me) screen se bahar chala jata tha — "Depl...",
    #    "Code..." kat jate the.
    #
    #    Ab: button nav me, panel body me — alag-alag.
    return (f'<button class="dmbtn" id="dmb" onclick="dmT()" '
            f'aria-label="Saare functions">'
            f'<i></i><i></i><i></i></button>')


def dotpanel(user=None, active=""):
    """
    ⋮ Panel ka asli HTML — ye <body> ke seedha andar jata hai,
    <nav> ke andar NAHI (upar wali wajah dekho).
    """
    groups = []
    for title, rows in MENU:
        cells = []
        for label, href, icn, desc in rows:
            on = " on" if href.strip("/#") == active else ""
            cells.append(
                f'<a href="{href}" class="dmi{on}">'
                f'<span class="dmic">{ico(icn, 16)}</span>'
                f'<span class="dmt"><b>{esc(label)}</b>'
                f'<i>{esc(desc)}</i></span></a>')
        groups.append(
            f'<div class="dmg"><div class="dmh">{title}</div>'
            f'<div class="dmr">{"".join(cells)}</div></div>')

    if user:
        foot = (f'<div class="dmf">'
                f'<a href="/logout" class="btn btn-g btn-sm">'
                f'{ico("logout", 13)} Logout</a>'
                f'<span class="dim xs">{esc(user.get("email", ""))}</span>'
                f'</div>')
    else:
        foot = (f'<div class="dmf">'
                f'<a href="/login" class="btn btn-g btn-sm">'
                f'{ico("user", 13)} Login</a>'
                f'<a href="/signup" class="btn btn-p btn-sm">'
                f'{ico("rocket", 13)} Sign Up</a></div>')

    js = (
        "function dmT(){"
        "var p=document.getElementById('dmp'),"
        "b=document.getElementById('dmbk'),n=document.getElementById('dmb');"
        "if(!p)return;"
        "var o=p.classList.toggle('on');"
        "if(b)b.classList.toggle('on',o);"
        "if(n)n.classList.toggle('on',o);"
        "document.body.style.overflow=o?'hidden':'';}"
        "document.addEventListener('keydown',function(e){"
        "if(e.key==='Escape'){var p=document.getElementById('dmp');"
        "if(p&&p.classList.contains('on'))dmT();}});")

    return (f'<div class="dmback" id="dmbk" onclick="dmT()"></div>'
            f'<div class="dmpanel" id="dmp">'
            f'<div class="dmtop"><b>{ico("grid", 15)} Saare functions</b>'
            f'<button class="dmx" onclick="dmT()">{ico("x", 15)}</button>'
            f'</div>'
            f'<div class="dmbody">{"".join(groups)}</div>'
            f'{foot}</div>'
            f'<script>{js}</script>')



def livebar():
    """
    📊 Har dashboard page par live system strip.
    CPU · RAM · DISK · NETWORK — sab har 2 second update.
    """
    try:
        import sysinfo
        s = sysinfo.snapshot(push_hist=False)
        c, r, d, n = s["cpu"], s["ram"], s["disk"], s["net"]
        cpu_p, ram_p, dsk_p = c["percent"], r["percent"], d["percent"]
        dn, up = n["down_kbs"], n["up_kbs"]
        hl, hc = s["health"], s["hcls"]
        upt = s["uptime_h"]
    except Exception:
        cpu_p = ram_p = dsk_p = dn = up = 0
        hl, hc, upt = "—", "off", "—"

    def cell(key, label, val, unit, pct, icn, col):
        cls = "r" if pct >= 90 else ("y" if pct >= 70 else "")
        return f"""<div class="lvc">
<div class="lvt">{ico(icn,13)}<span>{label}</span></div>
<div class="lvv"><b data-live="lb-{key}">{val}</b><i>{unit}</i></div>
<div class="lvb {cls}" id="lbb-{key}"><i style="width:{min(100,pct)}%;
background:{col}"></i></div></div>"""

    return f"""<div class="livebar">
{cell("cpu","CPU",cpu_p,"%",cpu_p,"cpu","#7C3AED")}
{cell("ram","RAM",ram_p,"%",ram_p,"ram","#00E6FF")}
{cell("disk","DISK",dsk_p,"%",dsk_p,"disk","#8B5CF6")}
<div class="lvc">
<div class="lvt">{ico("globe",13)}<span>NETWORK</span></div>
<div class="lvv"><b data-live="lb-dn">{dn}</b><i>KB/s ↓</i></div>
<div class="lvn">↑ <b data-live="lb-up">{up}</b> KB/s</div></div>
<div class="lvc lvend">
<div class="lvt">{ico("shield",13)}<span>HEALTH</span></div>
<div class="lvv"><span class="bdg {hc}" data-live-cls="lb-h"
id="lb-hlth">{hl}</span></div>
<div class="lvn">up {upt}</div></div>
</div>
<script>
(function(){{
 if(window.__lb) return; window.__lb=1;
 function px(k,v){{document.querySelectorAll('[data-live="lb-'+k+'"]')
  .forEach(function(e){{e.textContent=v}})}}
 function bar(k,p){{var b=document.getElementById('lbb-'+k);
  if(!b)return; var i=b.querySelector('i'); if(i)i.style.width=
  Math.min(100,p)+'%';
  b.className='lvb'+(p>=90?' r':(p>=70?' y':''))}}
 function tick(){{
  fetch('/api/live').then(function(r){{return r.json()}}).then(function(d){{
   px('cpu',d.cpu); px('ram',d.ram); px('disk',d.disk);
   px('dn',d.dn); px('up',d.up);
   bar('cpu',d.cpu); bar('ram',d.ram); bar('disk',d.disk);
   var h=document.getElementById('lb-hlth');
   if(h){{h.textContent=d.health; h.className='bdg '+d.hcls}}
  }}).catch(function(){{}});
 }}
 setInterval(tick,2000); tick();
}})();
</script>"""


def dash_page(title, sub, content, user, active, actions=""):
    ban = ""
    try:
        import unlock
        if unlock.is_black(user["id"]):
            import freeserver
            ban = freeserver.blacklist_banner(user["id"])
    except Exception:
        pass
    content = ban + content
    body = f"""<div class="dash"><div class="sdim" onclick="sdT()"></div>
{sidebar(active, user)}
<main class="main"><div class="ph"><div>
<h1>{esc(title)}</h1><p>{sub}</p></div>
<div class="flex">{actions}{_jv_link(user)}</div></div>
{livebar()}
{content}</main></div>{bottombar(active)}{_sd_js()}"""
    return page(title, body, user, active)


def bottombar(active=""):
    """
    📱 Neeche wali patti — sirf mobile pe dikhti hai.

    User ki shikayat thi ki "desktop mode pe hi sab dikhta hai".
    Wajah: sidebar mobile pe poori tarah gayab ho jaata tha aur
    16 me se ek bhi link pahunch me nahi rehta tha.

    Ab 5 sabse zaroori kaam hamesha ungli ke paas hain, aur
    baaki sab "Menu" se drawer me khul jaate hain.
    """
    tabs = [
        ("Home",    "/dashboard", "dashboard", "grid"),
        ("Servers", "/servers",   "servers",   "server"),
        ("Free",    "/free",      "free",      "gift"),
        ("Wallet",  "/billing",   "billing",   "wallet"),
    ]
    out = []
    for label, href, key, icn in tabs:
        on = " on" if key == active else ""
        out.append(f'<a href="{href}" class="{on.strip()}">'
                   f'{ico(icn, 19)}<span class="bt">{label}</span></a>')
    # 5th = drawer kholne wala
    out.append('<a href="javascript:void(0)" onclick="sdT()">'
               + ico("menu", 19) + '<span class="bt">Menu</span></a>')
    return '<div class="mnav">' + "".join(out) + '</div>'


def _sd_js():
    """Drawer khol-band karne ka chhota sa script"""
    return """<script>
function sdT(){
 var s=document.querySelector('.side'),d=document.querySelector('.sdim');
 if(!s)return;
 var o=s.classList.toggle('open');
 if(d)d.classList.toggle('open',o);
 document.body.style.overflow=o?'hidden':'';
}
// drawer me link dabaya -> band ho jaye
document.addEventListener('click',function(e){
 var a=e.target.closest('.side a');
 if(a&&window.innerWidth<=1080)setTimeout(sdT,60);
});
// peeche wala button drawer band kare
window.addEventListener('popstate',function(){
 var s=document.querySelector('.side');
 if(s&&s.classList.contains('open'))sdT();
});
</script>""" + _tbl_js()


def _tbl_js():
    """
    📱 TABLE ko CARD banane wala label-lagane ka script.

    ⚠️ Kyun JS se, CSS se kyun nahi:
       CSS card banane ke liye har <td> pe data-l chahiye
       (taaki "PLAN", "STATUS" jaisa label dikhe). Website me
       109 <td> hain 5 alag files me — sab haath se badalna
       galti ka khatra tha. Ye script <thead> se heading
       padh kar khud laga deta hai. Ek jagah fix, sab jagah
       kaam.
    """
    return """<script>
(function(){
 function lbl(){
  if(window.innerWidth>720)return;
  document.querySelectorAll('.tbl table').forEach(function(t){
   if(t.dataset.lbl)return; t.dataset.lbl='1';
   var hs=[].map.call(t.querySelectorAll('thead th'),
           function(h){return (h.textContent||'').trim()});
   if(!hs.length)return;
   t.querySelectorAll('tbody tr').forEach(function(r){
    [].forEach.call(r.children,function(td,i){
     if(hs[i]&&!td.getAttribute('data-l'))
      td.setAttribute('data-l',hs[i]);
    });
   });
  });
 }
 if(document.readyState!=='loading')lbl();
 else document.addEventListener('DOMContentLoaded',lbl);
 window.addEventListener('resize',lbl);
})();
</script>"""
