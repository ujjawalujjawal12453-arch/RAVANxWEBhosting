"""
pages.py — Naye hosting pages
══════════════════════════════
Real server create wizard, file manager, live console, analytics.
"""

import html
import json
import os
import time

import db
import engine
import theme
from brand import ico, logo, sparkline, minibars, donut, gauge
from theme import PLANS, PACKS, esc, dash_page, page, CREDIT_RATE


def money(n):
    return f"₹{n:,.0f}" if float(n) == int(n) else f"₹{n:,.2f}"


def ago(ts):
    if not ts:
        return "—"
    d = int(time.time()) - int(ts)
    if d < 60:
        return "abhi"
    if d < 3600:
        return f"{d//60}m pehle"
    if d < 86400:
        return f"{d//3600}h pehle"
    return f"{d//86400}d pehle"


def uptime(sec):
    if not sec:
        return "—"
    h, m = divmod(int(sec) // 60, 60)
    if h >= 24:
        return f"{h//24}d {h%24}h"
    return f"{h}h {m}m" if h else f"{m}m"


def plan_of(key):
    for p in PLANS:
        if p[0] == key:
            return p
    return PLANS[0]


def bar(pct):
    pct = max(0, min(100, int(pct)))
    c = "r" if pct >= 90 else ("y" if pct >= 70 else "")
    return f'<div class="bar {c}"><i style="width:{pct}%"></i></div>'


def fsize(n):
    if n < 1024:
        return f"{n} B"
    if n < 1048576:
        return f"{n/1024:.1f} KB"
    return f"{n/1048576:.1f} MB"


def hours_left(credits):
    return credits // CREDIT_RATE


# ══════════════════════════════════════════════
#   1. CREATE SERVER WIZARD
# ══════════════════════════════════════════════

def p_new_server(u, err="", step=1):
    e = f'<div class="msg err">⚠️ {esc(err)}</div>' if err else ""
    hrs = hours_left(u["credits"])

    low = ""
    if u["credits"] < CREDIT_RATE * 2:
        low = f"""<div class="msg warn">⚠️ Credits kam hain
(<b>{u['credits']}</b> = {hrs} ghante). Server banane ke baad
turant khatam ho sakta hai —
<a href="/recharge" style="color:var(--yel);text-decoration:underline">
recharge karo</a></div>"""

    cards = ""
    for i, (key, name, price, ram, cpu, napps, disk, feats) in enumerate(PLANS):
        hot = " hot" if i == 1 else ""
        tag = '<div class="tag">POPULAR</div>' if i == 1 else ""
        cards += f"""<label class="plan{hot}" style="cursor:pointer;display:block">
{tag}<input type="radio" name="plan" value="{key}"
{'checked' if i==0 else ''} style="display:none">
<h3>{name}</h3>
<div class="price">₹{price}<small>/mo</small></div>
<ul style="margin:14px 0">
<li>{ram} MB RAM</li><li>{cpu}</li>
<li>{disk} GB disk</li><li>{napps} servers</li></ul></label>"""

    content = f"""{low}{e}
<div class="card mb"><h3 class="mb">💳 Aapka balance</h3>
<div class="grid g3">
<div><div class="dim" style="font-size:13px">CREDITS</div>
<div class="big">{u['credits']}</div></div>
<div><div class="dim" style="font-size:13px">HOSTING TIME</div>
<div class="big">{hrs}h</div></div>
<div><div class="dim" style="font-size:13px">RATE</div>
<div class="big" style="font-size:24px">{CREDIT_RATE} cr/hr</div></div>
</div>
<div class="msg" style="background:rgba(47,129,247,.08);
border:1px solid rgba(47,129,247,.25);color:var(--acc3);margin-top:18px">
<b>ℹ️ Website par 1 ghanta = {CREDIT_RATE} credits</b><br>
<span style="color:var(--dim);font-size:13.5px">
Telegram bot par 1 credit lagta hai, yahan {CREDIT_RATE}.
Wajah — yahan aapko asli dedicated server milta hai, jiska
bandwidth, storage aur management team ka kharcha hum uthate hain.
Bot me shared resource hota hai, isliye sasta.</span></div></div>

<form method="POST" action="/servers/new">
<div class="card mb"><h3 class="mb">1️⃣ Server ka naam</h3>
<div class="fld"><input name="name" required placeholder="mera-bot"
maxlength="30" pattern="[a-zA-Z0-9_-]+"
style="font-size:16px"></div>
<p class="dim" style="font-size:13px">Sirf a-z, 0-9, - aur _ .
Aapka URL: <code>naam.ravanx.cloud</code></p></div>

<div class="card mb"><h3 class="mb">2️⃣ Plan chuno</h3>
<div class="grid g4">{cards}</div></div>

<div class="card mb"><h3 class="mb">3️⃣ Region</h3>
<div class="fld"><select name="region" style="font-size:15px">
<option value="mumbai">🇮🇳 Mumbai (sabse tez)</option>
<option value="delhi">🇮🇳 Delhi NCR</option>
<option value="banglore">🇮🇳 Bangalore</option>
</select></div></div>

<button class="btn btn-p" style="font-size:16px;padding:14px 32px">
🚀 Server Banao</button></form>"""

    return dash_page("Naya Server", "Apna dedicated server banao",
                     content, u, "new")


# ══════════════════════════════════════════════
#   2. SERVERS LIST
# ══════════════════════════════════════════════

def p_servers(u):
    apps = db.user_apps(u["id"])
    if not apps:
        content = """<div class="card empty"><div class="e">🖥</div>
<h3>Koi server nahi hai</h3>
<p class="dim mb">Apna pehla server banao — 1 minute me ready</p>
<a href="/servers/new" class="btn btn-p">{ico("plus",15)} Naya Server</a></div>"""
        return dash_page("My Servers", "0 servers", content, u, "servers")

    cards = ""
    for a in apps:
        sid = a["id"]
        run = engine.is_running(sid)
        us = engine.usage(sid)
        pl = plan_of(a["plan"])
        rp = min(100, int(us["ram"] / pl[3] * 100)) if pl[3] else 0
        dk = engine.disk_mb(u["id"], sid)
        # ⏳ FREE SERVER — kitna waqt bacha
        # User ko saaf dikhna chahiye ki server kab band hoga,
        # warna achanak band hone pe shikayat aati hai.
        _exp = ""
        try:
            import unlock as _ul
            _left = db.expiry_left(a)
            if _left > 0:
                _cls = "err" if _left < 3600 else "warn"
                _exp = (f'<div class="msg {_cls} mt2" style="padding:9px 12px">'
                        f'{ico("clock",14)}<div style="font-size:12.5px">'
                        f'<b>Free server</b> — {_ul.human_left(_left)} '
                        f'baad apne aap band ho jayega'
                        f'{" · abhi recharge karo!" if _left < 3600 else ""}'
                        f'</div></div>')
        except Exception:
            pass

        cards += f"""<div class="card">
<div class="flex" style="justify-content:space-between;align-items:start">
<div><h3>{esc(a['name'])}</h3>
<p class="dim" style="font-size:13px">{esc(a['lang'])} · {pl[1]}</p></div>
<span class="bdg {'on' if run else 'off'}">
{'● LIVE' if run else '○ OFF'}</span></div>
{_exp}

<div class="mt"><div class="flex" style="justify-content:space-between;
font-size:12.5px"><span class="dim">RAM</span>
<span>{us['ram']}/{pl[3]} MB</span></div>{bar(rp)}</div>

<div class="grid g3 mt" style="gap:8px;font-size:12.5px">
<div><div class="dim">CPU</div><b>{us['cpu']}%</b></div>
<div><div class="dim">DISK</div><b>{dk} MB</b></div>
<div><div class="dim">UPTIME</div><b>{uptime(us['uptime'])}</b></div></div>

<div class="flex mt">
<a href="/server/{sid}" class="btn btn-p btn-sm">{ico("edit",14)} Manage</a>
<a href="/server/{sid}/{'stop' if run else 'start'}"
class="btn {'btn-d' if run else 'btn-g'} btn-sm">
{'⏹ Stop' if run else '▶️ Start'}</a>
<a href="/console?s={sid}" class="btn btn-g btn-sm">🖥</a></div></div>"""

    return dash_page("My Servers", f"{len(apps)} servers",
                     f'<div class="grid g3">{cards}</div>', u, "servers",
                     f'<a href="/servers/new" class="btn btn-p">{ico("plus",15)} Naya</a>')


# ══════════════════════════════════════════════
#   3. SERVER DETAIL  (upload + console + control)
# ══════════════════════════════════════════════

def p_server(u, sid, msg="", err=""):
    a = db.get_app(sid, u["id"])
    if not a:
        return dash_page("404", "", '<div class="card empty"><div class="e">🔍</div>'
                         '<h3>Server nahi mila</h3></div>', u, "servers")

    run = engine.is_running(sid)
    busy = engine.is_busy(sid)
    us = engine.usage(sid)
    pl = plan_of(a["plan"])
    folder = engine.server_dir(u["id"], sid)
    info = engine.detect(folder)
    dk = engine.disk_mb(u["id"], sid)
    rp = min(100, int(us["ram"] / pl[3] * 100)) if pl[3] else 0

    m = ""
    if msg:
        m = f'<div class="msg ok">✅ {esc(msg)}</div>'
    elif err:
        m = f'<div class="msg err">⚠️ {esc(err)}</div>'

    # setup steps
    s1 = "done" if info["files"] else "now"
    s2 = "done" if info["entry"] else ("now" if info["files"] else "")
    s3 = "done" if run else ("now" if info["entry"] else "")
    steps = f"""<div class="card mb"><h3 class="mb">🎯 Setup</h3>
<div class="step {s1}"><div class="n">{'✓' if s1=='done' else '1'}</div>
<div><b>File upload</b><br><span class="dim" style="font-size:13px">
{f"{info['files']} files, {info['size_mb']} MB" if info['files']
  else 'Apna code upload karo (ZIP ya single file)'}</span></div></div>
<div class="step {s2}"><div class="n">{'✓' if s2=='done' else '2'}</div>
<div><b>Detect + Install</b><br><span class="dim" style="font-size:13px">
{f"{info['icon']} {info['lang']} — {info['entry']}" if info['entry']
  else 'main.py / index.js chahiye'}</span></div></div>
<div class="step {s3}"><div class="n">{'✓' if s3=='done' else '3'}</div>
<div><b>Server chalao</b><br><span class="dim" style="font-size:13px">
{f"LIVE — PID {us['pid']}" if run else 'Start dabao'}</span></div></div></div>"""

    deps = ""
    if info["has_deps"]:
        deps = f"""<a href="/server/{sid}/install"
class="btn btn-g">{ico("db",14)} Install deps</a>"""

    # 🔧 CODE DOCTOR
    try:
        import autofix
        _af = autofix.status(sid)
    except Exception:
        _af = {"on": False, "left": 0, "cap": 0, "tries_max": 3}
    try:
        import coder
        _cd = coder.status()
    except Exception:
        _cd = {"ok": False, "left": 0, "engine": "", "cap": 0,
               "models": 0, "unlimited": False}
    doctor = f'''<div class="card mb cdoc" id="cdoc">
<div class="flex between mb2">
<h3>{ico("shield",17)} Code Doctor
<span class="cdbeta">AI</span></h3>
<span class="bdg {'on' if _cd['ok'] else 'off'}">
{'READY' if _cd['ok'] else 'OFF'}</span></div>
<p class="s">Bot crash ho gaya? Error samajh nahi aa raha? JARVIS
padh kar batayega aur theek kar dega.
<b class="ok2">{_cd.get("models", 0)} AI model</b> laga hai
{'· unlimited' if _cd.get("unlimited") else f"· {_cd['left']} check bache"}.</p>
<div class="cdbtns mt2">
<button class="btn btn-p btn-sm" onclick="cdRun({sid},'fix')">
{ico("bolt",13)} Error theek karo</button>
<button class="btn btn-g btn-sm" onclick="cdRun({sid},'review')">
{ico("eye",13)} Code check karo</button>
<button class="btn btn-g btn-sm" onclick="cdRun({sid},'deps')">
{ico("db",13)} requirements banao</button>
</div>
<div class="afbox mt2">
<div class="afrow">
<div>
<b>{ico("bolt",13)} Auto-Fix — khud theek kare</b>
<p class="dim2 xs">Crash hote hi khud error dhoondhega, file
padhega, code theek karega, backup banayega aur restart
kar dega. {_af.get("tries_max",3)} baar try karega, phir aapko
bulayega. Aaj {_af.get("left",0)}/{_af.get("cap",0)} fix bache.</p>
</div>
<label class="sw">
<input type="checkbox" id="afsw" {'checked' if _af.get("on") else ''}
 onchange="afSet({sid},this.checked)">
<span></span></label>
</div>
<button class="btn btn-g btn-sm mt2" onclick="afNow({sid})">
{ico("bolt",13)} Abhi theek karo</button>
<div class="afout" id="afout"></div>
</div>
<div class="cdout" id="cdout"></div>
function cdRun(sid,mode){{
 var o=document.getElementById('cdout');
 var lbl={{fix:'Error padh raha hoon…',review:'Code check kar raha hoon…',
          deps:'Packages dhoondh raha hoon…'}}[mode];
 o.className='cdout on';
 o.innerHTML='<div class="cdload"><i></i><i></i><i></i><span>'+lbl+'</span></div>';
 fetch('/api/doctor',{{method:'POST',
  headers:{{'Content-Type':'application/json'}},
  body:JSON.stringify({{sid:sid,mode:mode}})}})
 .then(function(r){{return r.json()}}).then(function(d){{
  if(!d.ok){{o.innerHTML='<div class="cderr">'+esc(d.err||'Fail')+'</div>';
   return;}}
  if(d.mode==='deps'){{
   o.innerHTML='<div class="cdok">'+esc(d.file)+' bana diya</div>'+
    '<pre class="cdcode">'+esc(d.text)+'</pre>';
   if(window.jarvisSay) window.jarvisSay(d.file+' bana diya hai sir.');
   return;
  }}
  if(d.mode==='review'){{
   var h='<div class="cdhead '+(d.safe?'good':'bad')+'">'+
    '<b>'+(d.safe?'✔ Deploy kar sakte ho':'✘ Deploy mat karo')+'</b>'+
    '<span class="cdscore">'+d.score+'/100</span></div>'+
    '<p class="cdv">'+esc(d.verdict||'')+'</p>';
   if(d.issues&&d.issues.length){{h+='<div class="cdiss">';
    d.issues.forEach(function(i){{
     h+='<div class="cdi '+(i.bad||'medium')+'"><span class="cdt">'+
      esc(i.type)+'</span><span>'+esc(i.msg)+'</span>'+
      (i.line?'<i>L'+esc(i.line)+'</i>':'')+'</div>';}});
    h+='</div>';}}
   if(d.deps&&d.deps.length)
    h+='<p class="dim2 xs mt2">Packages: '+d.deps.map(esc).join(', ')+'</p>';
   o.innerHTML=h;
   if(window.jarvisSay) window.jarvisSay(d.verdict||'Check ho gaya sir.');
   return;
  }}
  // fix
  var h='<div class="cdhead '+(d.severity==='high'?'bad':
        (d.severity==='low'?'good':'warn'))+'">'+
   '<b>'+esc(d.problem)+'</b><span class="cdsev">'+esc(d.severity)+'</span></div>';
  if(d.why) h+='<p class="cdwhy">'+esc(d.why)+'</p>';
  if(d.fix) h+='<div class="cdfix">'+ico_check+' '+esc(d.fix)+'</div>';
  if(d.code){{
   h+='<pre class="cdcode">'+esc(d.code.slice(0,3000))+'</pre>'+
    '<div class="flex mt2" style="gap:8px">'+
    '<button class="btn btn-p btn-sm" onclick="cdApply('+sid+',\''+
     esc(d.file||'main.py')+'\')">Apply karo</button>'+
    '<span class="dim2 xs">Purani file .bak me bach jayegi</span></div>';
   window.__cdcode=d.code;
  }}
  h+='<p class="dim2 xs mt2">'+esc(d.engine||'')+' · '+
     esc((d.model||'').split('/').pop())+'</p>';
  o.innerHTML=h;
  if(window.jarvisSay) window.jarvisSay(d.problem+'. '+(d.fix||''));
 }}).catch(function(){{
  o.innerHTML='<div class="cderr">Server se baat nahi hui</div>';}});
}}
function cdApply(sid,file){{
 var o=document.getElementById('cdout');
 fetch('/api/doctor/apply',{{method:'POST',
  headers:{{'Content-Type':'application/json'}},
  body:JSON.stringify({{sid:sid,file:file,code:window.__cdcode||''}})}})
 .then(function(r){{return r.json()}}).then(function(d){{
  if(d.ok){{o.innerHTML='<div class="cdok">'+esc(d.file)+
   ' theek ho gaya! Ab server start karo.'+
   (d.backup?'<br><small>Purana: '+esc(d.backup)+'</small>':'')+'</div>';
   if(window.jarvisSay) window.jarvisSay('Code theek kar diya sir. Ab server chalaiye.');
   setTimeout(function(){{location.reload()}},2600);
  }} else o.innerHTML='<div class="cderr">Save nahi hua</div>';
 }});
}}
var ico_check='\u2714';
function esc(s){{return String(s==null?'':s).replace(/[&<>"]/g,function(c){{
 return {{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c]}})}}
</script>
<p class="dim2 xs mt2">{ico("check",11)} {_cd.get('left',0)} check
aaj bache · {esc(_cd.get('engine') or 'ready')}</p>
</div>'''

    files = engine.list_files(u["id"], sid)[:10]
    frows = "".join(f"""<div class="fr"><span class="ic">
{'📁' if f['dir'] else '📄'}</span>
<span class="nm">{esc(f['name'])}</span>
<span class="sz">{'' if f['dir'] else fsize(f['size'])}</span>
<a href="/files?s={sid}&del={esc(f['path'])}" class="btn btn-d btn-sm"
onclick="return confirm('Delete {esc(f['name'])}?')">🗑</a></div>"""
        for f in files) or '<div class="fr dim">Koi file nahi</div>'

    content = f"""{m}{doctor}{steps}
<div class="grid g4 mb">
<div class="card"><div class="dim" style="font-size:12.5px">STATUS</div>
<div style="margin-top:6px"><span class="bdg {'on' if run else 'off'}">
{'● LIVE' if run else '○ OFF'}</span></div>
{f'<div class="dim mt" style="font-size:12px">PID {us["pid"]}</div>' if run else ''}
</div>
<div class="card"><div class="dim" style="font-size:12.5px">RAM</div>
<div class="big" style="font-size:24px">{us['ram']} MB</div>{bar(rp)}
<div class="dim" style="font-size:12px">limit {pl[3]} MB</div></div>
<div class="card"><div class="dim" style="font-size:12.5px">CPU</div>
<div class="big" style="font-size:24px">{us['cpu']}%</div>
{bar(int(us['cpu']))}</div>
<div class="card"><div class="dim" style="font-size:12.5px">UPTIME</div>
<div class="big" style="font-size:24px">{uptime(us['uptime'])}</div>
<div class="dim" style="font-size:12px">{a['restarts']} restarts</div></div></div>

<div class="card mb"><div class="flex">
{'<span class="bdg wait">⏳ Install chal raha hai…</span>' if busy else f'''
<a href="/server/{sid}/{'stop' if run else 'start'}"
class="btn {'btn-d' if run else 'btn-p'}">{'⏹ Stop' if run else '▶️ Start'}</a>
<a href="/server/{sid}/restart" class="btn btn-g">{ico("refresh",14)} Restart</a>
{deps}
<a href="/console?s={sid}" class="btn btn-g">{ico("term",14)} Console</a>
<a href="/files?s={sid}" class="btn btn-g">{ico("folder",14)} Files</a>
<a href="/server/{sid}/delete" class="btn btn-d"
onclick="return confirm('Server delete? Saari files mit jayengi!')">🗑</a>'''}
</div></div>

<div class="grid g2">
<div class="card"><h3 class="mb">📤 File Upload</h3>
<form method="POST" action="/server/{sid}/upload"
enctype="multipart/form-data" id="uf">
<label class="drop" id="dz"><div class="i">📦</div>
<b>File chuno ya yahan drop karo</b>
<p class="dim mt" style="font-size:13px">
.py .js .php .go .rb .sh ya .zip (max 100 MB)</p>
<input type="file" name="file" id="fi" style="display:none"
accept=".py,.js,.php,.go,.rb,.sh,.zip,.txt,.json,.env,.md,.yml"></label>
<div id="fn" class="dim mt" style="font-size:13.5px"></div>
<button class="btn btn-p mt">{ico("up2",15)} Upload</button></form>
<script>
var dz=document.getElementById('dz'),fi=document.getElementById('fi'),
fn=document.getElementById('fn');
dz.onclick=function(){{fi.click()}};
fi.onchange=function(){{if(fi.files[0])fn.textContent='📄 '+fi.files[0].name+
' ('+(fi.files[0].size/1024).toFixed(0)+' KB)'}};
['dragover','dragenter'].forEach(function(e){{dz.addEventListener(e,function(ev){{
ev.preventDefault();dz.classList.add('over')}})}});
['dragleave','drop'].forEach(function(e){{dz.addEventListener(e,function(ev){{
ev.preventDefault();dz.classList.remove('over')}})}});
dz.addEventListener('drop',function(ev){{fi.files=ev.dataTransfer.files;
fi.onchange()}});
</script></div>

<div class="card" style="padding:0;overflow:hidden">
<div class="flex" style="padding:20px 20px 12px;justify-content:space-between">
<h3>📂 Files ({info['files']})</h3>
<a href="/files?s={sid}" class="btn btn-g btn-sm">Sab dekho</a></div>
{frows}</div></div>

<div class="card mt"><div class="flex mb" style="justify-content:space-between">
<h3>🖥 Live Console</h3>
<span class="live"><i></i> auto-refresh</span></div>
<div class="console" id="c"></div>
<form method="POST" action="/server/{sid}/cmd" class="flex mt">
<input name="cmd" placeholder="ls -la  /  pip install requests"
style="flex:1;padding:11px 14px;background:var(--bg2);
border:1px solid var(--line);border-radius:9px;color:var(--txt);
font-family:monospace;font-size:13.5px">
<button class="btn btn-p">{ico("play",14)} Run</button></form></div>

<div class="card mt"><h3 class="mb">📋 Details</h3>
<table>
<tr><td class="dim">Server ID</td><td><code>#{sid}</code></td></tr>
<tr><td class="dim">Domain</td><td><code>{esc(a['name'])}.ravanx.cloud</code></td></tr>
<tr><td class="dim">Language</td><td>{info['icon']} {info['lang'] or '—'}</td></tr>
<tr><td class="dim">Entry file</td><td><code>{esc(info['entry'] or '—')}</code></td></tr>
<tr><td class="dim">Plan</td><td>{pl[1]} — ₹{pl[2]}/mo</td></tr>
<tr><td class="dim">Disk</td><td>{dk} MB / {pl[6]} GB</td></tr>
<tr><td class="dim">Rate</td><td>{CREDIT_RATE} credits/ghanta</td></tr>
<tr><td class="dim">Created</td><td>{ago(a['created_at'])}</td></tr>
</table></div>

<script>
var last=0, box=document.getElementById('c');
function pull(){{
 fetch('/api/console/{sid}?since='+last).then(r=>r.json()).then(d=>{{
  if(d.lines&&d.lines.length){{
   d.lines.forEach(function(l){{
    var t=new Date(l.t*1000).toTimeString().slice(0,8);
    var e=document.createElement('div');
    e.className='cl '+l.l;
    e.innerHTML='<span class="ts">'+t+'</span><span class="tx"></span>';
    e.querySelector('.tx').textContent=l.x;
    box.appendChild(e);
   }});
   last=d.total;
   box.scrollTop=box.scrollHeight;
  }}
 }}).catch(function(){{}});
}}
pull(); setInterval(pull,1500);
</script>"""

    return dash_page(a["name"], f"{info['icon']} {info['lang'] or 'Server'} · {pl[1]}",
                     content, u, "servers",
                     '<a href="/servers" class="btn btn-g">← Back</a>')


# ══════════════════════════════════════════════
#   4. FILE MANAGER
# ══════════════════════════════════════════════

def p_files(u, sid=None, sub="", msg=""):
    apps = db.user_apps(u["id"])
    if not apps:
        return dash_page("Files", "", '<div class="card empty">'
                         '<div class="e">📂</div><h3>Pehle server banao</h3>'
                         f'<a href="/servers/new" class="btn btn-p mt">{ico("plus",15)} Naya Server</a>'
                         '</div>', u, "files")

    sid = sid or apps[0]["id"]
    a = db.get_app(sid, u["id"]) or apps[0]
    sid = a["id"]
    files = engine.list_files(u["id"], sid, sub)
    m = f'<div class="msg ok">✅ {esc(msg)}</div>' if msg else ""

    tabs = "".join(f"""<a href="/files?s={x['id']}"
class="btn {'btn-p' if x['id']==sid else 'btn-g'} btn-sm">
{esc(x['name'])}</a>""" for x in apps)

    up = ""
    if sub:
        parent = os.path.dirname(sub)
        up = f"""<div class="fr"><span class="ic">↩️</span>
<a href="/files?s={sid}&d={esc(parent)}" class="nm">.. (upar)</a></div>"""

    rows = up + ("".join(f"""<div class="fr">
<span class="ic">{'📁' if f['dir'] else '📄'}</span>
{f'<a href="/files?s={sid}&d={esc(f["path"])}" class="nm">{esc(f["name"])}</a>'
  if f['dir'] else
  f'<a href="/files?s={sid}&edit={esc(f["path"])}" class="nm">{esc(f["name"])}</a>'}
<span class="sz">{'' if f['dir'] else fsize(f['size'])}</span>
<a href="/files?s={sid}&del={esc(f['path'])}" class="btn btn-d btn-sm"
onclick="return confirm('Delete {esc(f['name'])}?')">🗑</a></div>"""
        for f in files) or '<div class="fr dim">Ye folder khali hai</div>')

    content = f"""{m}<div class="flex mb">{tabs}</div>
<div class="card mb"><h3 class="mb">{ico("up2",15)} Upload</h3>
<form method="POST" action="/server/{sid}/upload"
enctype="multipart/form-data" class="flex">
<input type="file" name="file" required style="flex:1;padding:9px;
background:var(--bg2);border:1px solid var(--line);border-radius:9px;
color:var(--txt);font-size:13.5px">
<button class="btn btn-p">Upload</button></form></div>

<div class="card" style="padding:0;overflow:hidden">
<div style="padding:18px 20px;border-bottom:1px solid var(--line)">
<b>📂 /{esc(sub) if sub else ''}</b>
<span class="dim" style="font-size:13px"> — {len(files)} items</span></div>
{rows}</div>

<div class="card mt"><h3 class="mb">➕ Nayi file banao</h3>
<form method="POST" action="/files/new">
<input type="hidden" name="s" value="{sid}">
<div class="fld"><input name="name" required placeholder="config.json"
maxlength="60"></div>
<div class="fld"><textarea name="content" placeholder="File ka content…"
style="font-family:monospace;min-height:150px"></textarea></div>
<button class="btn btn-p">{ico("check",15)} Banao</button></form></div>"""

    return dash_page("File Manager", f"{esc(a['name'])} — {len(files)} items",
                     content, u, "files")


def p_edit(u, sid, rel):
    a = db.get_app(sid, u["id"])
    if not a:
        return dash_page("404", "", '<div class="card empty">'
                         '<h3>Server nahi mila</h3></div>', u, "files")
    txt = engine.read_file(u["id"], sid, rel)
    if txt is None:
        return dash_page("404", "", '<div class="card empty">'
                         '<h3>File nahi padhi ja saki</h3></div>', u, "files")
    content = f"""<div class="card">
<form method="POST" action="/files/save">
<input type="hidden" name="s" value="{sid}">
<input type="hidden" name="p" value="{esc(rel)}">
<div class="fld"><textarea name="content" spellcheck="false"
style="font-family:'Cascadia Code',monospace;min-height:480px;
font-size:13px;line-height:1.6">{esc(txt)}</textarea></div>
<div class="flex"><button class="btn btn-p">{ico("check",15)} Save</button>
<a href="/files?s={sid}" class="btn btn-g">Cancel</a></div>
</form></div>"""
    return dash_page(f"✏️ {rel}", f"{esc(a['name'])} — {len(txt)} chars",
                     content, u, "files")


# ══════════════════════════════════════════════
#   5. LIVE CONSOLE (full page)
# ══════════════════════════════════════════════

def p_console(u, sid=None):
    apps = db.user_apps(u["id"])
    if not apps:
        return dash_page("Console", "", '<div class="card empty">'
                         '<div class="e">🖥</div><h3>Pehle server banao</h3>'
                         f'<a href="/servers/new" class="btn btn-p mt">{ico("plus",15)} Naya Server</a>'
                         '</div>', u, "console")
    sid = sid or apps[0]["id"]
    a = db.get_app(sid, u["id"]) or apps[0]
    sid = a["id"]
    run = engine.is_running(sid)
    us = engine.usage(sid)

    tabs = "".join(f"""<a href="/console?s={x['id']}"
class="btn {'btn-p' if x['id']==sid else 'btn-g'} btn-sm">
{'🟢' if engine.is_running(x['id']) else '🔴'} {esc(x['name'])}</a>"""
        for x in apps)

    content = f"""<div class="flex mb">{tabs}</div>
<div class="grid g4 mb">
<div class="card"><div class="dim" style="font-size:12.5px">STATUS</div>
<div style="margin-top:6px"><span class="bdg {'on' if run else 'off'}">
{'● LIVE' if run else '○ OFF'}</span></div></div>
<div class="card"><div class="dim" style="font-size:12.5px">RAM</div>
<div class="big" style="font-size:22px">{us['ram']} MB</div></div>
<div class="card"><div class="dim" style="font-size:12.5px">CPU</div>
<div class="big" style="font-size:22px">{us['cpu']}%</div></div>
<div class="card"><div class="dim" style="font-size:12.5px">UPTIME</div>
<div class="big" style="font-size:22px">{uptime(us['uptime'])}</div></div></div>

<div class="card"><div class="flex mb" style="justify-content:space-between">
<h3>🖥 {esc(a['name'])}</h3><div class="flex">
<span class="live"><i></i> live</span>
<a href="/server/{sid}/{'stop' if run else 'start'}"
class="btn {'btn-d' if run else 'btn-p'} btn-sm">
{'⏹ Stop' if run else '▶️ Start'}</a>
<a href="/server/{sid}/restart" class="btn btn-g btn-sm">🔄</a>
<a href="/console?s={sid}&clear=1" class="btn btn-g btn-sm">🧹</a></div></div>
<div class="console" id="c" style="height:520px"></div>
<form method="POST" action="/server/{sid}/cmd" class="flex mt">
<input name="cmd" autofocus autocomplete="off"
placeholder="ls -la   pip install requests   cat main.py"
style="flex:1;padding:12px 15px;background:var(--bg2);
border:1px solid var(--line);border-radius:9px;color:var(--txt);
font-family:monospace;font-size:13.5px">
<button class="btn btn-p">{ico("play",14)} Run</button></form>
<p class="dim mt" style="font-size:12.5px">
💡 Ye asli terminal hai — aapke server folder me chalta hai</p></div>

<script>
var last=0, box=document.getElementById('c');
function pull(){{
 fetch('/api/console/{sid}?since='+last).then(r=>r.json()).then(d=>{{
  if(d.lines&&d.lines.length){{
   d.lines.forEach(function(l){{
    var t=new Date(l.t*1000).toTimeString().slice(0,8);
    var e=document.createElement('div');
    e.className='cl '+l.l;
    e.innerHTML='<span class="ts">'+t+'</span><span class="tx"></span>';
    e.querySelector('.tx').textContent=l.x;
    box.appendChild(e);
   }});
   last=d.total; box.scrollTop=box.scrollHeight;
  }}
 }}).catch(function(){{}});
}}
pull(); setInterval(pull,1200);
</script>"""

    return dash_page("Live Console", f"{esc(a['name'])} — asli terminal",
                     content, u, "console")


# ══════════════════════════════════════════════
#   6. ANALYTICS
# ══════════════════════════════════════════════

def p_analytics(u):
    apps = db.user_apps(u["id"])
    tot_ram = tot_cpu = tot_disk = 0.0
    run = 0
    rows = ""
    for a in apps:
        us = engine.usage(a["id"])
        dk = engine.disk_mb(u["id"], a["id"])
        r = engine.is_running(a["id"])
        run += r
        tot_ram += us["ram"]
        tot_cpu += us["cpu"]
        tot_disk += dk
        pl = plan_of(a["plan"])
        rp = min(100, int(us["ram"] / pl[3] * 100)) if pl[3] else 0
        rows += f"""<tr><td><b>{esc(a['name'])}</b><br>
<span class="dim" style="font-size:12px">{esc(a['lang'])}</span></td>
<td><span class="bdg {'on' if r else 'off'}">{'LIVE' if r else 'OFF'}</span></td>
<td>{us['ram']} MB{bar(rp)}</td>
<td>{us['cpu']}%</td><td>{dk} MB</td>
<td>{uptime(us['uptime'])}</td>
<td>{a['restarts']}</td></tr>"""
    rows = rows or '<tr><td colspan="7" class="dim tc">Koi server nahi</td></tr>'

    hrs = hours_left(u["credits"])
    burn = run * CREDIT_RATE
    left = (u["credits"] // burn) if burn else "∞"

    content = f"""<div class="grid g4 mb">
<div class="card"><div class="dim" style="font-size:12.5px">SERVERS</div>
<div class="big">{len(apps)}</div>
<div class="dim" style="font-size:12.5px">{run} live</div></div>
<div class="card"><div class="dim" style="font-size:12.5px">TOTAL RAM</div>
<div class="big" style="font-size:26px">{tot_ram:.0f} MB</div></div>
<div class="card"><div class="dim" style="font-size:12.5px">TOTAL DISK</div>
<div class="big" style="font-size:26px">{tot_disk:.0f} MB</div></div>
<div class="card"><div class="dim" style="font-size:12.5px">BURN RATE</div>
<div class="big" style="font-size:26px">{burn}/hr</div>
<div class="dim" style="font-size:12.5px">{left} ghante bache</div></div></div>

<div class="card mb" style="padding:0;overflow:hidden">
<h3 style="padding:20px 20px 0">📊 Live Usage</h3>
<table><thead><tr><th>Server</th><th>Status</th><th>RAM</th><th>CPU</th>
<th>Disk</th><th>Uptime</th><th>Restarts</th></tr></thead>
<tbody>{rows}</tbody></table></div>

<div class="card"><h3 class="mb">💰 Credit Calculator</h3>
<div class="grid g3">
<div><div class="dim" style="font-size:13px">RATE</div>
<div class="big" style="font-size:26px">{CREDIT_RATE} cr/hr</div>
<div class="dim" style="font-size:12.5px">per server</div></div>
<div><div class="dim" style="font-size:13px">ABHI KHARCH</div>
<div class="big" style="font-size:26px">{burn} cr/hr</div>
<div class="dim" style="font-size:12.5px">{run} live servers</div></div>
<div><div class="dim" style="font-size:13px">BALANCE</div>
<div class="big" style="font-size:26px">{u['credits']}</div>
<div class="dim" style="font-size:12.5px">= {hrs}h single server</div></div>
</div>
<div class="msg mt" style="background:rgba(47,129,247,.08);
border:1px solid rgba(47,129,247,.25);color:var(--acc3)">
<b>ℹ️ Website par {CREDIT_RATE} credits/ghanta kyun?</b><br>
<span style="color:var(--dim);font-size:13.5px">
Yahan aapko asli dedicated server milta hai — apna folder, apna process,
apni RAM. Iska server cost, bandwidth aur management team ka kharcha
hum uthate hain. Telegram bot par shared resource hota hai, isliye
wahan 1 credit lagta hai.</span></div></div>"""

    return dash_page("Analytics", "Live resource usage", content, u, "analytics")
