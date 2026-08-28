"""
live.py — Real-time system page + admin lock
═════════════════════════════════════════════
Sab stats ek jagah, 2 second me auto-update.
"""

import time

import db
import engine
import sysinfo
import theme
from brand import (ico, logo, sparkline, minibars, donut, gauge,
                   areachart, multichart, bargraph, stackbars)
from theme import CREDIT_RATE, esc, page, dash_page


def _bar(pct):
    pct = max(0, min(100, int(pct)))
    c = "r" if pct >= 90 else ("y" if pct >= 70 else "")
    return f'<div class="bar {c}"><i style="width:{pct}%"></i></div>'


# ══════════════════════════════════════════════
#   SYSTEM PAGE — sab ek jagah, real-time
# ══════════════════════════════════════════════

def p_system(u):
    s = sysinfo.snapshot()
    c, r, d, n = s["cpu"], s["ram"], s["disk"], s["net"]
    apps = db.user_apps(u["id"])
    run = sum(1 for a in apps if engine.is_running(a["id"]))
    my_ram = sum(engine.usage(a["id"])["ram"] for a in apps)
    my_disk = sum(engine.disk_mb(u["id"], a["id"]) for a in apps)

    rows = ""
    for a in apps:
        sid = a["id"]
        rr = engine.is_running(sid)
        us = engine.usage(sid)
        dk = engine.disk_mb(u["id"], sid)
        rows += f"""<tr>
<td><b>{esc(a['name'])}</b><div class="dim2 xs">{esc(a['lang'])}</div></td>
<td><span class="bdg {'on' if rr else 'off'}">{'Live' if rr else 'Off'}</span></td>
<td><b class="mono" data-live="ram-{sid}">{us['ram']}</b> MB</td>
<td><b class="mono" data-live="cpu-{sid}">{us['cpu']}</b>%</td>
<td>{dk} MB</td>
<td class="dim mono" data-live="up-{sid}">{sysinfo.human_time(us['uptime']) if rr else '—'}</td>
<td class="dim2 mono">{us['pid'] or '—'}</td></tr>"""
    rows = rows or ('<tr><td colspan="7" class="dim tc" '
                    'style="padding:26px">Koi server nahi</td></tr>')

    content = f"""<div class="flex between mb">
<span class="live"><i></i> LIVE — har 2 second update</span>
<span class="bdg {s['hcls']}" id="hlth">{s['health']}</span></div>

<div class="grid g4 mb">
<div class="stat"><div class="top"><span class="lbl">CPU</span>
<span class="ib">{ico("cpu",15)}</span></div>
<div class="val"><span data-live="cpu">{c['percent']}</span><small
style="font-size:16px">%</small></div>
<div id="cpubar">{_bar(c['percent'])}</div>
<div class="sub">{c['cores']} cores · load
<span data-live="load">{c['load1']}</span></div>
<div class="chart" id="cpuchart">{minibars(s['hist']['cpu'] or [0],110,30,"#00E6FF")}</div>
</div>

<div class="stat"><div class="top"><span class="lbl">RAM</span>
<span class="ib c">{ico("ram",15)}</span></div>
<div class="val"><span data-live="ram">{r['percent']}</span><small
style="font-size:16px">%</small></div>
<div id="rambar">{_bar(r['percent'])}</div>
<div class="sub"><span data-live="ramu">{r['used']}</span> / {r['total']} MB</div>
<div class="chart" id="ramchart">{minibars(s['hist']['ram'] or [0],110,30,"#22D3EE")}</div>
</div>

<div class="stat"><div class="top"><span class="lbl">DISK</span>
<span class="ib p">{ico("disk",15)}</span></div>
<div class="val">{d['percent']}<small style="font-size:16px">%</small></div>
{_bar(d['percent'])}
<div class="sub">{d['used']} / {d['total']} GB</div>
<div class="chart">{minibars(s['hist']['disk'] or [0],110,30,"#8B5CF6")}</div>
</div>

<div class="stat"><div class="top"><span class="lbl">NETWORK</span>
<span class="ib g">{ico("globe",15)}</span></div>
<div class="val" style="font-size:25px">
<span data-live="down">{n['down_kbs']}</span><small
style="font-size:14px"> KB/s</small></div>
<div class="sub">↑ <span data-live="up">{n['up_kbs']}</span> KB/s ·
{n['rx_gb']} GB total</div>
<div class="chart" id="netchart">{sparkline(s['hist']['net'] or [0,0],110,30,"#22C55E",sid="nt")}</div>
</div></div>

<div class="card mb"><div class="flex between mb2">
<h3>{ico("chart",18)} Live Performance</h3>
<span class="live"><i></i> 2s refresh</span></div>
<div id="bigchart">{stackbars([
("CPU", s["hist"]["cpu"] or [0], "#7C3AED"),
("RAM", s["hist"]["ram"] or [0], "#00E6FF"),
("DISK", s["hist"]["disk"] or [0], "#8B5CF6")], 560, 215, "mc")}</div></div>

<div class="grid g2 mb">
<div class="card"><div class="flex between mb2">
<h3 class="sm dim">CPU BAR HISTORY</h3>
<b class="sm" data-live="cpu2">{c['percent']}%</b></div>
<div id="cpubig">{bargraph(s["hist"]["cpu"] or [0], 520, 180,
"#7C3AED", "c1", "%", 100)}</div></div>
<div class="card"><div class="flex between mb2">
<h3 class="sm dim">RAM BAR HISTORY</h3>
<b class="sm" data-live="ram2">{r['percent']}%</b></div>
<div id="rambig">{bargraph(s["hist"]["ram"] or [0], 520, 180,
"#00E6FF", "r1", "%", 100)}</div></div></div>

<div class="grid g2 mb">
<div class="card"><h3 class="mb2 sm dim">DISK BAR HISTORY</h3>
<div id="diskbig">{bargraph(s["hist"]["disk"] or [0], 520, 175,
"#8B5CF6", "d1", "%", 100)}</div></div>
<div class="card"><h3 class="mb2 sm dim">NETWORK KB/s</h3>
<div id="netbig">{bargraph(s["hist"]["net"] or [0], 520, 175,
"#22C55E", "n1", " KB/s")}</div></div></div>

<div class="grid g3 mb">
<div class="card tc"><h3 class="mb2 sm dim">CPU LOAD</h3>
<div id="gauge1">{gauge(c['load_pct'], 210, 108)}</div>
<div class="dim2 xs mt2">1m: {c['load1']} · 5m: {c['load5']} ·
15m: {c['load15']}</div></div>

<div class="card tc"><h3 class="mb2 sm dim">MEMORY</h3>
<div id="don1">{donut(r['percent'], 128, 12, "#22D3EE",
label=f"{r['percent']:.0f}%", sub="used")}</div>
<div class="dim2 xs mt2">{r['free']} MB free · {r['cached']} MB cached</div></div>

<div class="card tc"><h3 class="mb2 sm dim">STORAGE</h3>
{donut(d['percent'], 128, 12, "#8B5CF6", label=f"{d['used']:.0f}", sub="GB used")}
<div class="dim2 xs mt2">{d['free']} GB free of {d['total']} GB</div></div>
</div>

<div class="grid g4 mb">
<div class="card"><div class="dim2 xs">SYSTEM UPTIME</div>
<div class="big" style="font-size:22px">{sysinfo.human_time(s['uptime'])}</div></div>
<div class="card"><div class="dim2 xs">PROCESSES</div>
<div class="big" style="font-size:22px" data-live="procs">{s['procs']}</div></div>
<div class="card"><div class="dim2 xs">MY SERVERS</div>
<div class="big" style="font-size:22px">{run}/{len(apps)}</div></div>
<div class="card"><div class="dim2 xs">MY USAGE</div>
<div class="big" style="font-size:22px">{my_ram:.0f} MB</div>
<div class="dim2 xs">{my_disk:.0f} MB disk</div></div></div>

<div class="tbl mb"><div class="th"><h3>{ico("server",17)} Mere Servers</h3>
<span class="live"><i></i> live</span></div>
<table><thead><tr><th>Server</th><th>Status</th><th>RAM</th><th>CPU</th>
<th>Disk</th><th>Uptime</th><th>PID</th></tr></thead>
<tbody>{rows}</tbody></table></div>

<div class="card"><h3 class="mb2">{ico("cpu",18)} Hardware</h3>
<table>
<tr><td class="dim">Processor</td><td><b>{esc(c['model'])}</b></td></tr>
<tr><td class="dim">Cores</td><td>{c['cores']} vCPU
{f"· {c['mhz']} MHz" if c['mhz'] else ""}</td></tr>
<tr><td class="dim">Total RAM</td><td>{r['total']} MB</td></tr>
<tr><td class="dim">Swap</td><td>{r['swap_used']} / {r['swap_total']} MB</td></tr>
<tr><td class="dim">Storage</td><td>{d['total']} GB</td></tr>
<tr><td class="dim">Platform</td><td>{_platform()}</td></tr>
<tr><td class="dim">Network total</td><td>↓ {n['rx_gb']} GB ·
↑ {n['tx_gb']} GB</td></tr>
</table></div>

<style>.mono{{font-variant-numeric:tabular-nums}}</style>
<script>
function upd(){{
 fetch('/api/system').then(r=>r.json()).then(d=>{{
  var set=function(k,v){{
   document.querySelectorAll('[data-live="'+k+'"]').forEach(function(e){{
    e.textContent=v}})}};
  set('cpu',d.cpu.percent); set('ram',d.ram.percent);
  set('cpu2',d.cpu.percent+'%'); set('ram2',d.ram.percent+'%');
  set('ramu',d.ram.used); set('load',d.cpu.load1);
  set('down',d.net.down_kbs); set('up',d.net.up_kbs);
  set('procs',d.procs);
  var bar=function(id,p){{
   var el=document.querySelector('#'+id+' i');
   if(el){{el.style.width=p+'%';
    var b=el.parentElement;
    b.className='bar'+(p>=90?' r':(p>=70?' y':''))}}}};
  bar('cpubar',d.cpu.percent); bar('rambar',d.ram.percent);
  var h=document.getElementById('hlth');
  if(h){{h.textContent=d.health;h.className='bdg '+d.hcls}}
  (d.servers||[]).forEach(function(s){{
   set('ram-'+s.id,s.ram); set('cpu-'+s.id,s.cpu); set('up-'+s.id,s.up)}});
  if(d.charts){{
   ['cpuchart','ramchart','netchart','bigchart','cpubig','rambig',
    'diskbig','netbig']
   .forEach(function(id,i){{
    var e=document.getElementById(id);
    if(e&&d.charts[i])e.innerHTML=d.charts[i]}});
  }}
 }}).catch(function(){{}});
}}
setInterval(upd,2000);
</script>"""

    return dash_page("Live System", "Sab kuch real-time — asli numbers",
                     content, u, "system")


def _platform():
    try:
        import cloudsync
        p = cloudsync.platform_name()
        return f"{p}{' (ephemeral)' if cloudsync.is_ephemeral() else ''}"
    except Exception:
        return "Local"


# ══════════════════════════════════════════════
#   ADMIN LOCK — password screen
# ══════════════════════════════════════════════

def p_admin_lock(u, err=""):
    e = (f'<div class="msg err">{ico("x",15)}<div>{esc(err)}</div></div>'
         if err else "")
    body = f"""<div class="dash">{theme.sidebar("admin", u)}
<main class="main"><div class="auth" style="min-height:auto;padding:40px 0">
<div class="box" style="max-width:420px">
<div class="bh">
<div class="lockbox">{ico("lock",30)}</div>
<h2>Admin Panel</h2>
<p class="s">Ye area protected hai — password daalo</p></div>{e}
<form method="POST" action="/admin/unlock">
<div class="fld"><label>Admin Password</label>
<input name="pass" type="password" required autofocus
placeholder="••••••••••" style="text-align:center;font-size:19px;
letter-spacing:5px;font-family:monospace"></div>
<button class="btn btn-p btn-b btn-lg">{ico("key",16)} Unlock karo</button>
</form>
<div class="msg info mt">{ico("shield",15)}<div>
Galat password 5 baar daalne par 10 minute ke liye lock ho jayega.</div></div>
</div></div></main></div>
<style>
.lockbox{{width:74px;height:74px;border-radius:22px;margin:0 auto 6px;
display:grid;place-items:center;color:var(--acc3);
background:linear-gradient(135deg,rgba(47,129,247,.18),rgba(0,230,255,.06));
border:1px solid rgba(47,129,247,.3);animation:lockin .6s var(--ease)}}
@keyframes lockin{{from{{transform:scale(.6) rotate(-14deg);opacity:0}}}}
.box{{animation:slideup .5s var(--ease)}}
@keyframes slideup{{from{{transform:translateY(22px);opacity:0}}}}
</style>"""
    return page("Admin", body, u, "admin")


def p_admin_welcome(u):
    """Unlock hone ke baad ka animation."""
    body = f"""<div class="unlockwrap">
<div class="uring"><div class="uicon">{ico("crown",42)}</div></div>
<h1>Welcome, Admin</h1>
<p>Control panel khul raha hai…</p>
<div class="uload"><i></i></div></div>
<style>
.unlockwrap{{min-height:calc(100vh - 68px);display:grid;place-items:center;
align-content:center;gap:6px;text-align:center;
animation:fadein .4s var(--ease)}}
.uring{{width:112px;height:112px;border-radius:50%;display:grid;
place-items:center;margin-bottom:18px;position:relative;
background:radial-gradient(circle,rgba(47,129,247,.2),transparent 70%)}}
.uring::before,.uring::after{{content:'';position:absolute;inset:0;
border-radius:50%;border:2px solid transparent;
border-top-color:var(--acc);animation:spin 1.1s linear infinite}}
.uring::after{{inset:11px;border-top-color:var(--cy);
animation-duration:1.6s;animation-direction:reverse}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
.uicon{{color:var(--acc3);animation:pop .55s var(--ease)}}
@keyframes pop{{from{{transform:scale(0) rotate(-40deg);opacity:0}}}}
.unlockwrap h1{{font-size:31px;font-weight:840;letter-spacing:-1px;
background:linear-gradient(120deg,var(--acc4),var(--cy));
-webkit-background-clip:text;-webkit-text-fill-color:transparent;
animation:slideup .5s .12s both var(--ease)}}
.unlockwrap p{{color:var(--dim);animation:slideup .5s .2s both var(--ease)}}
.uload{{width:230px;height:4px;background:var(--card2);border-radius:99px;
overflow:hidden;margin-top:22px}}
.uload i{{display:block;height:100%;border-radius:99px;
background:linear-gradient(90deg,var(--acc),var(--cy));
animation:fill 1.25s var(--ease) forwards}}
@keyframes fill{{from{{width:0}}to{{width:100%}}}}
@keyframes fadein{{from{{opacity:0}}}}
@keyframes slideup{{from{{transform:translateY(16px);opacity:0}}}}
</style>
<script>setTimeout(function(){{location.href='/admin'}},2100);</script>"""
    try:
        import voice
        body += voice.speak(
            "Access granted. Welcome back, Admin. "
            "Opening control panel.", 250)
    except Exception:
        pass
    return page("Welcome Admin", body, u, "admin")
