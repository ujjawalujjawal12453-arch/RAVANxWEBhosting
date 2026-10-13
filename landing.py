"""
landing.py — Company-level landing page
════════════════════════════════════════
Hero + stats + features + how-it-works + pricing + compare + FAQ + CTA
"""

import db
import icon as appicon
import theme
from brand import ico, logo, sparkline, minibars, donut
from theme import BRAND, TAGLINE, PLANS, CREDIT_RATE, esc, page, footer


def _plans_html(signup=True):
    out = ""
    for i, (key, name, price, ram, cpu, napps, disk, feats) in enumerate(PLANS):
        hot = " hot" if i == 1 else ""
        tag = '<div class="tag">MOST POPULAR</div>' if i == 1 else ""
        li = "".join(f'<li>{ico("check",14)} {f}</li>' for f in feats)
        # jo nahi hai
        extra = []
        if i < 2:
            extra.append("Dedicated IP")
        if i < 1:
            extra.append("Priority CPU")
        li += "".join(f'<li class="no">{ico("x",14)} {e}</li>' for e in extra)
        href = f"/signup?plan={key}" if signup else f"/servers/new?plan={key}"
        out += f"""<div class="plan{hot}">{tag}
<h3>{name}</h3>
<div class="pr">₹{price}<small>/mo</small></div>
<div class="spec">{ram} MB RAM · {cpu} · {disk} GB SSD</div>
<ul>{li}</ul>
<a href="{href}" class="btn {'btn-p' if i==1 else 'btn-g'} btn-b">
{'Start Now' if i==1 else 'Choose'} {ico('up',14)}</a></div>"""
    return out


def p_home():
    s = db.stats()
    users = max(s["users"], 240)
    apps = max(s["apps"], 680)

    # ── hero live panel ──
    hero_panel = f"""<div class="card glow" style="max-width:940px;
margin:52px auto 0;padding:0;overflow:hidden;text-align:left">
<div class="flex between" style="padding:13px 18px;
border-bottom:1px solid var(--line);background:var(--bg2)">
<div class="flex" style="gap:7px">
<span style="width:11px;height:11px;border-radius:50%;background:#FF0080"></span>
<span style="width:11px;height:11px;border-radius:50%;background:#F59E0B"></span>
<span style="width:11px;height:11px;border-radius:50%;background:#28c840"></span>
<span class="dim2 xs" style="margin-left:10px">ravanx.cloud/dashboard</span>
</div><span class="live"><i></i> LIVE</span></div>
<div style="padding:20px">
<div class="grid g4 mb2" style="gap:12px">
<div class="stat" style="padding:15px">
<div class="top"><span class="lbl">Servers</span>
<span class="ib">{ico("server",15)}</span></div>
<div class="val" style="font-size:24px">12</div>
<div class="chart">{sparkline([3,5,4,8,7,11,12], 100, 26, "#00E6FF", sid="h1")}</div>
</div>
<div class="stat" style="padding:15px">
<div class="top"><span class="lbl">Uptime</span>
<span class="ib g">{ico("check",15)}</span></div>
<div class="val" style="font-size:24px">99.9<small style="font-size:14px">%</small></div>
<div class="chart">{minibars([88,92,96,99,97,100,99], 100, 26, "#22C55E")}</div>
</div>
<div class="stat" style="padding:15px">
<div class="top"><span class="lbl">RAM</span>
<span class="ib c">{ico("ram",15)}</span></div>
<div class="val" style="font-size:24px">1.2<small style="font-size:14px">GB</small></div>
<div class="chart">{sparkline([400,620,580,900,860,1100,1200], 100, 26, "#22D3EE", sid="h2")}</div>
</div>
<div class="stat" style="padding:15px">
<div class="top"><span class="lbl">Requests</span>
<span class="ib p">{ico("bolt",15)}</span></div>
<div class="val" style="font-size:24px">48<small style="font-size:14px">k</small></div>
<div class="chart">{sparkline([12,19,16,28,34,42,48], 100, 26, "#8B5CF6", sid="h3")}</div>
</div></div>
<div class="console" style="height:150px">
<div class="cl ok"><span class="ts">18:42:01</span>
<span class="tx">🚀 Deploying mybot…</span></div>
<div class="cl out"><span class="ts">18:42:02</span>
<span class="tx">📦 Installing dependencies (requirements.txt)</span></div>
<div class="cl out"><span class="ts">18:42:07</span>
<span class="tx">Successfully installed aiohttp-3.9.1 requests-2.31.0</span></div>
<div class="cl ok"><span class="ts">18:42:08</span>
<span class="tx">✅ Build complete in 6.4s</span></div>
<div class="cl cmd"><span class="ts">18:42:09</span>
<span class="tx">$ python3 -u main.py</span></div>
<div class="cl out"><span class="ts">18:42:09</span>
<span class="tx">Bot chalu ho gaya — PID 4821</span></div>
<div class="cl ok"><span class="ts">18:42:10</span>
<span class="tx">🟢 LIVE at mybot.ravanx.cloud</span></div>
</div></div></div>"""

    # ── features (12) ──
    feats = [
        ("bolt", "Instant Deploy", "Code upload karo — 30 second me live. "
         "Build, install, start — sab automatic."),
        ("term", "Real Live Console", "Asli terminal, asli output. Jo server "
         "par ho raha hai wo browser me live dikhta hai."),
        ("refresh", "Auto Restart", "App crash ho to 5 second me wapas. "
         "Aapko uthna bhi nahi padega."),
        ("chart", "Live Analytics", "RAM, CPU, disk, uptime — real numbers, "
         "graph ke saath. /proc se seedha."),
        ("shield", "4-Layer Backup", "Files 4 jagah safe. Delete, crash, "
         "format — kuch bhi ho, data rehta hai."),
        ("folder", "File Manager", "Browser se hi files browse, edit aur "
         "delete karo. VS Code ki zarurat nahi."),
        ("globe", "Free Subdomain", "app.ravanx.cloud SSL ke saath — "
         "bilkul free, turant active."),
        ("code", "6 Languages", "Python, Node.js, PHP, Go, Ruby, Bash — "
         "auto-detect hota hai."),
        ("db", "ZIP Deploy", "Poora project ZIP me daalo, hum khud "
         "extract karke chala denge."),
        ("clock", "Per-Hour Billing", f"{CREDIT_RATE} credits/ghanta. Server "
         "band = billing band. Mahine ka commitment nahi."),
        ("lock", "Secure by Default", "PBKDF2 password, isolated folders, "
         "encrypted sessions."),
        ("help", "Hindi Support", "Telegram pe seedha baat karo. "
         "Ticket system bhi hai."),
    ]
    fcards = "".join(f"""<div class="feat">
<div class="fi">{ico(i,21)}</div><h3>{t}</h3><p>{d}</p></div>"""
        for i, t, d in feats)

    # ── how it works ──
    steps = [
        ("Account banao", "Email se signup — 25 credits free. Card nahi chahiye.",
         "user"),
        ("Server chuno", "Plan select karo, region chuno. 10 second me ready.",
         "server"),
        ("Code upload", "File ya ZIP drag-drop karo. Language auto-detect.",
         "up2"),
        ("Deploy & Live", "Start dabao — console me live dekho, app online.",
         "rocket"),
    ]
    hcards = "".join(f"""<div class="feat" style="text-align:center">
<div class="fi" style="margin:0 auto 15px">{ico(i,21)}</div>
<div class="stag" style="margin-bottom:10px">STEP {n+1}</div>
<h3>{t}</h3><p>{d}</p></div>""" for n, (t, d, i) in enumerate(steps))

    # ── compare ──
    rows = [
        ("Setup time", "30 seconds", "2-3 ghante", True),
        ("Live console", "✓ Real-time", "SSH chahiye", True),
        ("Auto restart", "✓ Built-in", "Khud setup karo", True),
        ("Backup", "✓ 4-layer auto", "Manual", True),
        ("Hindi support", "✓ Telegram", "Email only", True),
        ("Billing", "Per ghanta", "Poora mahina", True),
        ("Starting price", "₹149/mo", "₹500+/mo", True),
    ]
    crows = "".join(f"""<tr><td class="dim">{a}</td>
<td><b style="color:var(--acc3)">{b}</b></td>
<td class="dim2">{c}</td></tr>""" for a, b, c, _ in rows)

    # ── FAQ ──
    faqs = [
        ("Kaunsi language support hai?",
         "Python, Node.js, PHP, Ruby, Go aur Bash. File upload karte hi bot "
         "khud pehchan leta hai. ZIP me poora project bhi daal sakte ho."),
        (f"Credits kaise kaam karte hain?",
         f"1 ghanta hosting = {CREDIT_RATE} credits. Server band karoge to "
         f"billing bhi band. Signup pe 25 credits free milte hain."),
        ("Payment kaise karun?",
         "UPI se — PhonePe, GPay, Paytm koi bhi. QR scan karo, UTR (12 digit) "
         "daalo. Verify hote hi credits mil jate hain."),
        ("Mera data safe hai?",
         "Haan. Har server ka apna alag folder hai. Password PBKDF2 se "
         "encrypted (120k iterations) — hum bhi nahi padh sakte. 4-layer backup."),
        ("App crash ho gaya to?",
         "Console me error dikhega, aur auto-restart on ho to 5 second me "
         "wapas chalu. Logs me poora traceback milega."),
        ("Refund milta hai?",
         "7 din ke andar service se khush nahi ho — poora refund, koi sawaal "
         "nahi. Unused credits ka pro-rata refund bhi."),
        ("Telegram bot se kya farak hai?",
         f"Bot me shared resource hai, isliye 1 credit/ghanta. Website par "
         f"aapko asli dedicated server milta hai — apna folder, apna process, "
         f"apni RAM. Isliye {CREDIT_RATE} credits."),
        ("Kitne servers bana sakta hoon?",
         "Plan par depend karta hai — Starter me 2, Pro me 5, Ultra me 12, "
         "Business me 30. Kabhi bhi upgrade kar sakte ho."),
    ]
    fq = "".join(f"""<details class="acc"><summary>{q}</summary>
<div class="ac">{a}</div></details>""" for q, a in faqs)

    body = f"""<section class="hero"><div class="wrap">
<div class="herologo">{appicon.big(158)}</div>
<div class="pill"><span class="dot"></span> 99.9% Uptime ·
{users}+ developers · India servers</div>
<h1>Deploy karo.<br><span class="gr">Chalta rahega.</span></h1>
<p class="lead">Bots aur apps ke liye India ka apna cloud.
Code upload karo — build, install, deploy sab hum karenge.
Server ki tension bhool jao.</p>
<div class="cta">
<a href="/signup" class="btn btn-p btn-lg">{ico("rocket",17)} Free me shuru karo</a>
<a href="#pricing" class="btn btn-g btn-lg">Pricing dekho</a></div>
<div class="trust">
<span>{ico("check",14)} Card nahi chahiye</span>
<span>{ico("gift",14)} 25 credits free</span>
<span>{ico("clock",14)} 30 sec setup</span>
<span>{ico("shield",14)} 7-din refund</span></div>
{hero_panel}</div></section>

<div class="wrap"><div class="grid g4" style="margin:64px 0">
<div class="stat"><div class="top"><span class="lbl">Developers</span>
<span class="ib">{ico("user",15)}</span></div>
<div class="val">{users}+</div>
<div class="sub"><span class="up">{ico("up",12)} 18%</span> is mahine</div></div>
<div class="stat"><div class="top"><span class="lbl">Apps Hosted</span>
<span class="ib p">{ico("server",15)}</span></div>
<div class="val">{apps}+</div>
<div class="sub"><span class="up">{ico("up",12)} 24%</span> is mahine</div></div>
<div class="stat"><div class="top"><span class="lbl">Uptime</span>
<span class="ib g">{ico("bolt",15)}</span></div>
<div class="val">99.9%</div>
<div class="sub">Pichhle 90 din</div></div>
<div class="stat"><div class="top"><span class="lbl">Support</span>
<span class="ib y">{ico("help",15)}</span></div>
<div class="val">24/7</div>
<div class="sub">Hindi + English</div></div></div></div>

<section class="sec alt" id="features"><div class="wrap">
<div class="shead"><div class="stag">Features</div>
<h2>Sab kuch jo chahiye</h2>
<p>Ek platform jo aapki zubaan samajhta hai aur aapka kaam
aasan banata hai</p></div>
<div class="grid g4">{fcards}</div></div></section>

<section class="sec" id="how"><div class="wrap">
<div class="shead"><div class="stag">Kaise chalta hai</div>
<h2>4 step me live</h2>
<p>Pehli baar host kar rahe ho? Koi baat nahi — 2 minute me ho jayega</p>
</div><div class="grid g4">{hcards}</div></div></section>

<section class="sec alt" id="pricing"><div class="wrap">
<div class="shead"><div class="stag">Pricing</div>
<h2>Simple, saaf pricing</h2>
<p>Koi chhupa charge nahi. Jab chaho upgrade ya cancel karo.</p></div>
<div class="grid g4">{_plans_html()}</div>
<div class="card mt flat" style="text-align:center;
background:linear-gradient(135deg,rgba(47,129,247,.07),transparent)">
<div class="flex" style="justify-content:center;gap:26px;flex-wrap:wrap">
<span class="dim sm">{ico("check",14)} Free SSL</span>
<span class="dim sm">{ico("check",14)} Daily backup</span>
<span class="dim sm">{ico("check",14)} 24/7 monitoring</span>
<span class="dim sm">{ico("check",14)} Live console</span>
<span class="dim sm">{ico("check",14)} Per-hour billing</span></div></div>
</div></section>

<section class="sec" id="compare"><div class="wrap">
<div class="shead"><div class="stag">Comparison</div>
<h2>Normal VPS se behtar</h2>
<p>Aapko server manage nahi karna — sirf code chalana hai</p></div>
<div class="tbl" style="max-width:860px;margin:0 auto">
<table><thead><tr><th></th>
<th style="color:var(--acc3)">RAVAN X CLOUD</th>
<th>Normal VPS</th></tr></thead><tbody>{crows}</tbody></table></div>
</div></section>

<section class="sec alt" id="faq"><div class="wrap">
<div class="shead"><div class="stag">FAQ</div>
<h2>Sawaal jawab</h2><p>Jo aksar poocha jata hai</p></div>
<div style="max-width:780px;margin:0 auto">{fq}</div></div></section>

<section class="sec"><div class="wrap">
<div class="card glow" style="text-align:center;padding:60px 30px">
<div style="margin-bottom:18px">{logo(48, text=False)}</div>
<h2 style="font-size:clamp(25px,4vw,36px);font-weight:840;
letter-spacing:-1.2px">Aaj hi shuru karo</h2>
<p class="dim mt2" style="max-width:460px;margin:12px auto 26px;font-size:16px">
Signup pe <b style="color:var(--acc3)">25 credits free</b> —
card ki zarurat nahi, koi commitment nahi.</p>
<div class="flex" style="justify-content:center">
<a href="/signup" class="btn btn-p btn-lg">{ico("rocket",17)} Free Account Banao</a>
<a href="https://t.me/{theme.SUPPORT.lstrip('@')}" class="btn btn-g btn-lg">
{ico("help",16)} Baat karo</a></div></div></div></section>
{footer()}"""

    return page("India ka Apna Cloud", body)


def p_legal(kind):
    data = {
        "terms": ("Terms of Service", "terms", [
            ("Service", "RAVAN X CLOUD bot aur application hosting deta hai. "
             "Hum 99.9% uptime ka target rakhte hain. Service 'as-is' provide "
             "ki jaati hai."),
            ("Aapki zimmedari", "Jo code aap host karte ho uske aap zimmedar ho. "
             "Illegal content, spam, phishing, crypto mining, DDoS tools — "
             "kuch bhi allowed nahi. Doosron ke resources par asar dalne wale "
             "apps band kar diye jayenge."),
            ("Billing", f"1 ghanta hosting = {CREDIT_RATE} credits. Credits "
             "prepaid hain. Server band karoge to billing bhi ruk jayegi. "
             "Credits khatam hote hi servers apne aap band ho jate hain."),
            ("Fair use", "CPU aur RAM plan ke hisaab se milta hai. Continuous "
             "100% CPU use karne wale apps throttle ho sakte hain."),
            ("Suspension", "Rules todne par account bina notice band ho sakta "
             "hai. Serious cases me data bhi delete ho sakta hai."),
            ("Changes", "Terms kabhi bhi update ho sakte hain. Bade badlav ka "
             "notice email par milega."),
        ]),
        "privacy": ("Privacy Policy", "privacy", [
            ("Kya collect karte hain", "Naam, email, phone (optional) aur "
             "aapke servers ka metadata. Password PBKDF2 (120,000 iterations) "
             "se hashed hai — hum bhi nahi padh sakte."),
            ("Kya nahi karte", "Aapka data kisi ko bechte nahi. Koi third-party "
             "tracker nahi hai. Koi ad network nahi."),
            ("Aapka code", "Hum aapke code ko padhte nahi, sirf chalate hain. "
             "Har server ka apna isolated folder hai. Backup encrypted rehta hai."),
            ("Logs", "Console logs 400 lines tak memory me rehti hain, disk par "
             "permanent nahi. Access logs 30 din me delete ho jate hain."),
            ("Cookies", "Sirf ek session cookie (HttpOnly, SameSite=Lax). "
             "Koi tracking cookie nahi."),
            ("Delete", "Account delete karne par 30 din me sab data permanently "
             "mit jata hai. Turant chahiye to support se bolo."),
        ]),
        "refund": ("Refund Policy", "refund", [
            ("7 din guarantee", "Service se khush nahi? Pehle 7 din ke andar "
             "poora refund — koi sawaal nahi poochenge."),
            ("Kaise lein", "Support ticket kholo ya Telegram par message karo. "
             "3-5 working day me paisa wapas aa jata hai (usi UPI par)."),
            ("Unused credits", "Bache hue credits ka pro-rata refund milta hai. "
             "Use ho chuke ghante ka nahi."),
            ("Kab nahi milega", "Agar account rules todne par band hua ho, "
             "ya 7 din nikal gaye hon, ya fraud/chargeback ka case ho."),
            ("Downtime credit", "Agar mahine me uptime 99% se neeche gaya to "
             "us mahine ke credits wapas mil jate hain."),
        ]),
        "sla": ("Service Level Agreement", "sla", [
            ("Uptime commitment", "Hum 99.9% monthly uptime ka target rakhte "
             "hain (mahine me ~43 minute downtime tak)."),
            ("Kya count hota hai", "Downtime = aapka server hamare karan band "
             "raha. Aapke code ka crash, credits khatam hona, ya aapka khud "
             "stop karna count nahi hota."),
            ("Compensation", "99%-99.9% = 10% credits wapas. 95%-99% = 25%. "
             "95% se neeche = 50% credits wapas."),
            ("Maintenance", "Planned maintenance ka 48 ghante pehle notice "
             "milega, aur ye uptime me count nahi hota."),
            ("Claim kaise", "Downtime ke 7 din ke andar support ticket kholo. "
             "Hum logs check karke credits add kar denge."),
        ]),
    }[kind]

    secs = "".join(f"""<div class="card mb2 flat">
<h3 style="font-size:16.5px;margin-bottom:8px;display:flex;
align-items:center;gap:9px">{ico("check",16,"")} {h}</h3>
<p class="dim" style="font-size:14.5px;line-height:1.72">{p}</p></div>"""
        for h, p in data[2])

    body = f"""<div class="wrap sec">
<div class="shead"><div class="stag">Legal</div><h2>{data[0]}</h2>
<p>Last updated: 19 August 2026</p></div>
<div style="max-width:800px;margin:0 auto">{secs}
<div class="card mt flat" style="text-align:center">
<p class="dim">Koi sawaal hai?</p>
<a href="https://t.me/{theme.SUPPORT.lstrip('@')}" class="btn btn-g mt2">
{ico("help",15)} Support se poocho</a></div></div></div>{footer()}"""
    return page(data[0], body)


def p_status():
    """Public status page."""
    s = db.stats()
    svcs = [
        ("Web Dashboard", "operational", 99.98),
        ("Hosting Engine", "operational", 99.94),
        ("File Storage", "operational", 100.0),
        ("Payment System", "operational", 99.99),
        ("Console Streaming", "operational", 99.91),
    ]
    rows = "".join(f"""<tr><td><b>{n}</b></td>
<td><span class="bdg on">Operational</span></td>
<td style="width:170px">{minibars([97,99,98,100,99,100,int(u)], 150, 26, "#22C55E")}</td>
<td><b style="color:#22C55E">{u}%</b></td></tr>"""
        for n, st, u in svcs)

    body = f"""<div class="wrap sec">
<div class="shead"><div class="stag">System Status</div>
<h2>Sab kuch theek chal raha hai</h2>
<p>Live status — har 60 second update hota hai</p></div>
<div style="max-width:900px;margin:0 auto">
<div class="card glow mb" style="text-align:center;padding:34px">
<div class="ib g" style="width:56px;height:56px;margin:0 auto 14px;
border-radius:16px;display:grid;place-items:center;
background:rgba(34,197,94,.12);color:#22C55E">{ico("check",27)}</div>
<h3 style="font-size:21px;font-weight:780">All Systems Operational</h3>
<p class="dim mt2">Koi problem report nahi hui</p></div>
<div class="tbl"><div class="th"><h3>{ico("chart",17)} Services</h3>
<span class="live"><i></i> live</span></div>
<table><thead><tr><th>Service</th><th>Status</th><th>7 din</th>
<th>Uptime</th></tr></thead><tbody>{rows}</tbody></table></div>
<div class="grid g3 mt">
<div class="stat"><div class="top"><span class="lbl">Total Servers</span>
<span class="ib">{ico("server",15)}</span></div>
<div class="val">{max(s['apps'],680)}</div></div>
<div class="stat"><div class="top"><span class="lbl">Running Now</span>
<span class="ib g">{ico("bolt",15)}</span></div>
<div class="val">{max(s['running'],412)}</div></div>
<div class="stat"><div class="top"><span class="lbl">Avg Response</span>
<span class="ib c">{ico("clock",15)}</span></div>
<div class="val">42<small style="font-size:15px">ms</small></div></div>
</div></div></div>{footer()}"""
    return page("Status", body)


def p_frombot(info, tok=""):
    """
    🤖 Bot se aaya banda — khali haath nahi jayega.
    Uska naam, bot ka naam, aur seedha aage ka rasta.
    """
    import botlink
    nm = esc(str(info.get("name") or "dost"))
    b = botlink.bot_info()
    bu = esc(str(b.get("username") or "").lstrip("@"))
    known = bool(info)

    hi = (f"Namaste <b>{nm}</b>!" if known
          else "Namaste! Aap sahi jagah aaye hain.")
    sub = ("Aapka bot account pehchan liya — ab website par bhi "
           "sab kuch mil jayega." if known else
           "Bot aur website — dono ek hi RAVAN X HOSTING ka hissa hain.")

    step = f"/signup?b={esc(tok)}" if (known and tok) else "/signup"

    plans = "".join(
        f"""<div class="fbp">
<div class="fbn">{esc(p[1])}</div>
<div class="fbr">₹{p[2]}<span>/mo</span></div>
<div class="fbd">{p[3]} MB RAM · {theme.storage_gb(p[0])} GB storage</div>
</div>""" for p in theme.PLANS[:3])

    body = f"""<section class="hero" style="padding:44px 0 60px">
<div class="wrap">
<div class="herologo">{appicon.big(120)}</div>
<div class="pill"><span class="dot"></span>
{'Bot se aaye hain' if known else 'Welcome'}</div>
<h1 style="font-size:clamp(28px,5vw,46px)">{hi}</h1>
<p class="lead">{sub}</p>

<div class="fbgrid">
<div class="card fbc">
<div class="fbi">{ico("rocket",22)}</div>
<b>Asli servers</b>
<p>Aapka code asli process me chalega — dikhawa nahi.
Python, Node, PHP, Go, Ruby, Bash.</p></div>
<div class="card fbc">
<div class="fbi">{ico("db",22)}</div>
<b>Apna storage</b>
<p>Har account ko apni jagah. File kitni bhi badi ho —
plan ke andar chalegi.</p></div>
<div class="card fbc">
<div class="fbi">{ico("chart",22)}</div>
<b>Live sab kuch</b>
<p>CPU, RAM, disk, network — har 2 second update.
Console live chalti hai.</p></div>
</div>

<div class="fbplans">{plans}</div>

<div class="cta" style="margin-top:30px">
<a href="{step}" class="btn btn-p btn-lg">
{ico("rocket",17)} Account banao — free</a>
<a href="/login" class="btn btn-g btn-lg">Pehle se account hai</a></div>

{f'''<p class="dim2 xs" style="margin-top:22px">
{ico("check",12)} Bot: <a href="https://t.me/{bu}"
style="color:var(--cy)">@{bu}</a> se juda hua</p>''' if bu else ''}
</div></section>

<style>
.fbgrid{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;
max-width:900px;margin:40px auto 0;text-align:left}}
.fbc{{padding:22px}}
.fbc .fbi{{width:44px;height:44px;border-radius:12px;display:grid;
place-items:center;background:linear-gradient(135deg,
rgba(124,58,237,.22),rgba(0,230,255,.12));color:var(--acc4);
margin-bottom:13px}}
.fbc b{{display:block;font-size:15.5px;margin-bottom:6px}}
.fbc p{{font-size:13.3px;color:var(--dim);line-height:1.62}}
.fbplans{{display:flex;gap:12px;justify-content:center;flex-wrap:wrap;
margin-top:26px}}
.fbp{{background:linear-gradient(160deg,var(--card),var(--bg2));
border:1px solid var(--line);border-radius:12px;padding:14px 20px;
min-width:158px;transition:.25s var(--ease)}}
.fbp:hover{{border-color:var(--line2);box-shadow:0 0 24px var(--glow);
transform:translateY(-3px)}}
.fbn{{font-size:11px;letter-spacing:1.2px;color:var(--dim2);
font-weight:700}}
.fbr{{font-size:24px;font-weight:830;letter-spacing:-1px;margin:3px 0}}
.fbr span{{font-size:12px;color:var(--dim2);font-weight:600}}
.fbd{{font-size:11.5px;color:var(--dim2)}}
@media(max-width:820px){{.fbgrid{{grid-template-columns:1fr}}}}
</style>
{theme.footer()}"""
    return theme.page("Welcome", body)
