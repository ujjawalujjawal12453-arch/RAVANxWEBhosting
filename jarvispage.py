"""
jarvispage.py — J.A.R.V.I.S. CONTROL ROOM
══════════════════════════════════════════

Poora JARVIS interface — sirf ADMIN ke liye.
Admin panel ke andar: /admin/jarvis

Isme kya hai:
  • Bada arc reactor — bolte waqt dhadakta hai
  • Live chat — aap bolo, wo jawab de
  • Real-time system rings (CPU / RAM / DISK / NET)
  • Ek-tap command buttons
  • Server list — bol kar ya tap kar ke control
  • Command history
  • Always-listening toggle
"""

import time

import db
import theme
import brain
import vcmd
from brand import ico
from theme import esc, page


def _fmt(ts):
    if not ts:
        return "—"
    d = int(time.time()) - int(ts)
    if d < 60:
        return f"{d}s"
    if d < 3600:
        return f"{d // 60}m"
    if d < 86400:
        return f"{d // 3600}h"
    return f"{d // 86400}d"


QUICK = [
    ("status",   "Status batao",        "chart",  "CPU, RAM, servers"),
    ("users",    "Kitne users hain",    "user",   "Total count"),
    ("backup",   "Backup lo",           "db",     "Cloud par save"),
    ("server_on", "Sab server chalu",   "play",   "Sab start"),
    ("server_off", "Sab server band",   "stop",   "⚠️ poochega"),
    ("free_off", "Free service band",   "gift",   "⚠️ poochega"),
    ("free_on",  "Free service chalu",  "check",  "Wapas khol do"),
    ("maint_on", "Maintenance on",      "shield", "⚠️ poochega"),
]


def p_jarvis(u):
    """🤖 JARVIS Control Room — admin only."""
    f = vcmd.flags()
    _b = brain.status()
    try:
        import coder
        _c = coder.status()
    except Exception:
        _c = {"ok": False, "left": 0}
    st = db.stats()
    apps = _all_apps()
    import engine
    live = sum(1 for a in apps if engine.is_running(a["id"]))

    # ── server rows ──
    rows = []
    for a in apps[:12]:
        r = engine.is_running(a["id"])
        us = engine.usage(a["id"])
        rows.append(f"""<div class="jsv">
<span class="jsd {'on' if r else ''}"></span>
<div class="jsn"><b>{esc(a['name'])}</b>
<i>{esc(a.get('lang') or '—')} · {us['ram']} MB</i></div>
<div class="jsa">
<a href="/admin/jarvis/srv/{a['id']}/{'stop' if r else 'start'}"
class="jsb">{ico('stop' if r else 'play', 12)}</a></div></div>""")
    srv_html = "".join(rows) or (
        '<div class="jsempty">Koi server nahi</div>')

    # ── quick buttons ──
    qb = "".join(f"""<button class="jq" onclick="jvSend('{c}')"
data-a="{c}"><span class="jqi">{ico(i, 15)}</span>
<span class="jqt"><b>{esc(lbl)}</b><i>{esc(d)}</i></span></button>"""
                 for c, lbl, i, d in QUICK)

    # ── history ──
    hist = vcmd.history(12)
    hh = "".join(f"""<div class="jh">
<span class="jht">{_fmt(x['at'])}</span>
<span class="jhc">{esc(x['cmd'])}</span>
<span class="jhr">{esc(x['res'])}</span></div>""" for x in hist) or \
        '<div class="jsempty">Abhi tak koi command nahi</div>'

    # ── flags ──
    def sw(key, label, on, onurl, offurl):
        return f"""<div class="jf {'on' if on else 'off'}">
<div><b>{label}</b><i>{'CHALU' if on else 'BAND'}</i></div>
<a href="{offurl if on else onurl}" class="jfb">
{'Band karo' if on else 'Chalu karo'}</a></div>"""

    flags_html = (
        sw("free", "Free service", f["free_open"],
           "/admin/flag/free/1", "/admin/flag/free/0") +
        sw("signup", "Naye signup", f["signup_open"],
           "/admin/flag/signup/1", "/admin/flag/signup/0") +
        sw("maint", "Website", not f["maintenance"],
           "/admin/flag/maint/0", "/admin/flag/maint/1"))

    body = f"""<div class="jwrap">

<!-- ══ REACTOR + CHAT ══ -->
<div class="jmain">
<div class="jreactor" id="jrx">
  <svg viewBox="0 0 200 200" class="jring">
    <defs>
      <linearGradient id="g1" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#00E6FF"/>
        <stop offset="50%" stop-color="#7C3AED"/>
        <stop offset="100%" stop-color="#FF0080"/>
      </linearGradient>
      <filter id="gl"><feGaussianBlur stdDeviation="3" result="b"/>
        <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/>
        </feMerge></filter>
    </defs>
    <circle cx="100" cy="100" r="92" fill="none" stroke="url(#g1)"
      stroke-width="1" opacity=".25"/>
    <circle cx="100" cy="100" r="80" fill="none" stroke="url(#g1)"
      stroke-width="2" stroke-dasharray="8 6" class="r1" filter="url(#gl)"/>
    <circle cx="100" cy="100" r="64" fill="none" stroke="#00E6FF"
      stroke-width="1.5" stroke-dasharray="30 120" class="r2"/>
    <circle cx="100" cy="100" r="52" fill="none" stroke="#7C3AED"
      stroke-width="2.5" stroke-dasharray="60 90" class="r3"/>
    <circle cx="100" cy="100" r="38" fill="none" stroke="#FF0080"
      stroke-width="1" stroke-dasharray="4 8" class="r4"/>
    <circle cx="100" cy="100" r="26" fill="url(#g1)" opacity=".18"
      class="core"/>
    <circle cx="100" cy="100" r="17" fill="url(#g1)" opacity=".55"
      class="core2" filter="url(#gl)"/>
  </svg>
  <div class="jrtxt"><b id="jrs">JARVIS</b><i id="jrm">standby</i></div>
</div>

<div class="jchat">
  <div class="jclog" id="jclog">
    <div class="jm bot"><span class="jmi">{ico("bolt", 13)}</span>
      <div>Good day, sir. Main JARVIS hoon.<br>
      <small>Mic dabaiye ya neeche button use kariye.</small></div></div>
  </div>
  <div class="jcin">
    <button class="jmic" id="jmic" onclick="jvMic()">
      {ico("mic", 19)}<i class="jmr"></i></button>
    <input id="jtxt" placeholder="…ya yahan likh kar bhejo"
      onkeydown="if(event.key==='Enter')jvType()">
    <button class="jsend" onclick="jvType()">{ico("check", 16)}</button>
    <button class="jwake" id="jwake" onclick="jvWake()"
      title="Hamesha sunta rahe">{ico("bolt", 15)}</button>
  </div>
</div>
</div>

<!-- ══ LIVE RINGS ══ -->
<div class="jstats">
{_ringbox("CPU", "cpu", "#7C3AED")}
{_ringbox("RAM", "ram", "#00E6FF")}
{_ringbox("DISK", "disk", "#8B5CF6")}
{_ringbox("NET", "net", "#22C55E", unit=" KB/s", max_=1000)}
</div>

<!-- ══ QUICK + FLAGS ══ -->
<div class="jgrid">
<div class="card">
<h3 class="mb2">{ico("bolt", 17)} Ek tap me command</h3>
<div class="jqs">{qb}</div></div>

<div class="card">
<h3 class="mb2">{ico("shield", 17)} Control switches</h3>
<div class="jfs">{flags_html}</div>
<div class="jstat mt2">
<div><b>{st['users']}</b><i>users</i></div>
<div><b>{live}/{len(apps)}</b><i>servers live</i></div>
<div><b>{st.get('apps', 0)}</b><i>total apps</i></div>
</div></div>
</div>

<!-- ══ AI ENGINE ══ -->
<div class="card jai">
<div class="flex between mb2">
<h3>{ico("bolt", 17)} AI Engine</h3>
<span class="bdg {'on' if _b['ok'] else 'err'}">
{'LIVE' if _b['ok'] else 'OFF'}</span></div>
<div class="jaig">
<div class="jaie {'on' if _b['gemini'] else 'off'}">
<b>Gemini</b><i>{'connected' if _b['gemini'] else 'no key'}</i>
<span>free · 1500/din</span></div>
<div class="jaie {'on' if _b['sarvam'] else 'off'}">
<b>Sarvam</b><i>{'connected' if _b['sarvam'] else 'no key'}</i>
<span>Indian voice</span></div>
<div class="jaie {'on' if _c.get('groq') else 'off'}">
<b>Groq LPU</b><i>{'connected' if _c.get('groq') else 'no key'}</i>
<span>0.2s · 14,400/din</span></div>
<div class="jaie {'on' if _c.get('nvidia') else 'off'}">
<b>NVIDIA NIM</b><i>{'connected' if _c.get('nvidia') else 'no key'}</i>
<span>{_c.get('nv_models',0)} model · unlimited</span></div>
<div class="jaie {'on' if _c['ok'] else 'off'}">
<b>Code Doctor</b><i>{'ready' if _c['ok'] else 'off'}</i>
<span>{'unlimited' if _c.get('unlimited') else str(_c['left'])+' bache'}</span></div>
</div>
<div class="jaib mt2">
<div><i>Aaj use hua</i><b>{_b['used']} / {_b['cap']}</b></div>
<div><i>Bacha hai</i><b>{_b['left']}</b></div>
<div><i>Samajhne me</i><b>{_b['think_ms']} ms</b></div>
<div><i>Bolne me</i><b>{_b['tts_ms']} ms</b></div>
</div>
{f'<p class="dim2 xs mt2">⚠️ {esc(_b["error"][:90])}</p>'
 if _b.get("error") else ''}
</div>

<!-- ══ SERVERS + HISTORY ══ -->
<div class="jgrid">
<div class="card">
<h3 class="mb2">{ico("server", 17)} Servers ({len(apps)})</h3>
<div class="jsvs">{srv_html}</div></div>

<div class="card">
<h3 class="mb2">{ico("clock", 17)} Command history</h3>
<div class="jhs">{hh}</div></div>
</div>

</div>

{_css()}
{_js()}
"""
    return theme.dash_page("JARVIS Control Room",
                           "Bolo — sab kuch ho jayega", body, u, "admin")


def _ringbox(label, key, col, unit="%", max_=100):
    return f"""<div class="jsb2">
<svg viewBox="0 0 100 100" class="jsr">
<circle cx="50" cy="50" r="40" fill="none" stroke="rgba(148,163,184,.12)"
  stroke-width="7"/>
<circle cx="50" cy="50" r="40" fill="none" stroke="{col}" stroke-width="7"
  stroke-linecap="round" stroke-dasharray="251" stroke-dashoffset="251"
  transform="rotate(-90 50 50)" id="ring-{key}"
  style="transition:stroke-dashoffset .7s cubic-bezier(.22,1,.36,1)"/>
</svg>
<div class="jsv2"><b id="val-{key}">0</b><i>{unit}</i></div>
<div class="jsl">{label}</div></div>"""


def _all_apps():
    c = db.conn()
    rows = c.execute("SELECT * FROM apps ORDER BY id DESC").fetchall()
    c.close()
    return [dict(r) for r in rows]


def _css():
    return """<style>
.jwrap{display:flex;flex-direction:column;gap:16px}

/* ── REACTOR + CHAT ── */
.jmain{display:grid;grid-template-columns:270px 1fr;gap:16px;
background:linear-gradient(160deg,#0F172A,#0B1020);
border:1px solid var(--line);border-radius:16px;padding:18px;
position:relative;overflow:hidden}
.jmain::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;
background:linear-gradient(90deg,transparent,rgba(0,230,255,.6),
rgba(124,58,237,.6),rgba(255,0,128,.4),transparent)}

.jreactor{position:relative;display:grid;place-items:center;
min-height:230px}
.jring{width:210px;height:210px}
.jring .r1{transform-origin:100px 100px;animation:sp1 14s linear infinite}
.jring .r2{transform-origin:100px 100px;animation:sp2 7s linear infinite}
.jring .r3{transform-origin:100px 100px;animation:sp1 10s linear infinite
reverse}
.jring .r4{transform-origin:100px 100px;animation:sp2 5s linear infinite
reverse}
@keyframes sp1{to{transform:rotate(360deg)}}
@keyframes sp2{to{transform:rotate(-360deg)}}
.jring .core{animation:pul 3.2s ease-in-out infinite}
.jring .core2{animation:pul 2.1s ease-in-out infinite}
@keyframes pul{0%,100%{opacity:.2;r:24}50%{opacity:.55;r:29}}
.jrtxt{position:absolute;text-align:center;pointer-events:none}
.jrtxt b{display:block;font-size:15px;font-weight:830;letter-spacing:2.6px;
background:linear-gradient(120deg,#00E6FF,#7C3AED 50%,#EC4899);
-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.jrtxt i{font-style:normal;font-size:9.5px;letter-spacing:1.6px;
color:var(--dim3);text-transform:uppercase}

/* states */
.jreactor.listening .jring .r2,.jreactor.listening .jring .r3{
animation-duration:2s}
.jreactor.listening .jrtxt i{color:var(--cy)}
.jreactor.working .jring{animation:shake .35s infinite}
.jreactor.working .jrtxt i{color:var(--pk2)}
@keyframes shake{0%,100%{transform:translateX(0)}
25%{transform:translateX(-1.5px)}75%{transform:translateX(1.5px)}}
.jreactor.ask .jrtxt i{color:var(--warn)}
.jreactor.done .jrtxt i{color:var(--ok)}

/* ── CHAT ── */
.jchat{display:flex;flex-direction:column;min-height:230px}
.jclog{flex:1;overflow-y:auto;max-height:270px;display:flex;
flex-direction:column;gap:9px;padding-right:6px}
.jclog::-webkit-scrollbar{width:5px}
.jclog::-webkit-scrollbar-thumb{background:var(--line2);border-radius:9px}
.jm{display:flex;gap:9px;font-size:13.5px;line-height:1.55;
animation:jmin .3s var(--ease)}
@keyframes jmin{from{opacity:0;transform:translateY(6px)}}
.jm .jmi{width:26px;height:26px;border-radius:8px;flex-shrink:0;
display:grid;place-items:center;
background:linear-gradient(135deg,rgba(124,58,237,.25),rgba(0,230,255,.12));
color:var(--acc4)}
.jm.bot div{background:rgba(0,230,255,.06);padding:9px 12px;
border-radius:11px;border-left:2px solid rgba(0,230,255,.4);flex:1}
.jm.me{flex-direction:row-reverse}
.jm.me .jmi{background:linear-gradient(135deg,rgba(255,0,128,.22),
rgba(124,58,237,.14));color:var(--pk2)}
.jm.me div{background:rgba(124,58,237,.1);padding:9px 12px;
border-radius:11px;border-right:2px solid rgba(124,58,237,.45);
text-align:right;flex:1}
.jm small{color:var(--dim2);font-size:11.5px}
.jm.warn div{background:rgba(245,158,11,.1);
border-left-color:rgba(245,158,11,.6)}
.jm.ok div{background:rgba(34,197,94,.09);
border-left-color:rgba(34,197,94,.5)}
.jm.err div{background:rgba(239,68,68,.09);
border-left-color:rgba(239,68,68,.5)}

.jcin{display:flex;gap:8px;margin-top:12px;align-items:center}
.jmic{width:44px;height:44px;border-radius:12px;flex-shrink:0;cursor:pointer;
display:grid;place-items:center;position:relative;color:var(--cy);
background:linear-gradient(160deg,var(--card2),var(--bg2));
border:1px solid rgba(0,230,255,.3);transition:.24s var(--ease)}
.jmic:hover{box-shadow:0 0 22px var(--bglow);border-color:var(--cy)}
.jmic .jmr{position:absolute;inset:-3px;border-radius:14px;
border:2px solid var(--cy);opacity:0;pointer-events:none}
.jmic.live{background:linear-gradient(135deg,#00E6FF,#7C3AED);color:#fff;
border-color:transparent}
.jmic.live .jmr{opacity:1;animation:jmr 1.2s ease-out infinite}
@keyframes jmr{0%{inset:-3px;opacity:.9}100%{inset:-15px;opacity:0}}
.jmic.ask{background:linear-gradient(135deg,#F59E0B,#EC4899);color:#fff;
border-color:transparent}
.jmic.ask .jmr{opacity:1;border-color:var(--warn);
animation:jmr 1s ease-out infinite}
#jtxt{flex:1;padding:12px 15px;border-radius:12px;font-size:14px;
background:rgba(255,255,255,.04);border:1px solid var(--line);
color:var(--txt);outline:none;transition:.2s}
#jtxt:focus{border-color:var(--line2);background:rgba(255,255,255,.06)}
.jsend,.jwake{width:42px;height:44px;border-radius:12px;cursor:pointer;
display:grid;place-items:center;border:1px solid var(--line);
background:linear-gradient(160deg,var(--card2),var(--bg2));
color:var(--dim);transition:.24s var(--ease);flex-shrink:0}
.jsend{background:var(--g1);color:#fff;border-color:transparent}
.jsend:hover{box-shadow:0 4px 18px var(--glow)}
.jwake:hover{color:var(--acc4);border-color:var(--line2)}
.jwake.on{background:linear-gradient(135deg,rgba(0,230,255,.2),
rgba(124,58,237,.14));border-color:var(--cy);color:var(--cy)}
.jwake.on::after{content:'';position:absolute;width:7px;height:7px;
border-radius:50%;background:#22C55E;box-shadow:0 0 8px #22C55E;
margin:-26px 0 0 26px;animation:bp 1.8s infinite}

/* ── LIVE RINGS ── */
.jstats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
.jsb2{background:linear-gradient(160deg,var(--card),var(--bg2));
border:1px solid var(--line);border-radius:14px;padding:14px;
text-align:center;position:relative}
.jsr{width:82px;height:82px;display:block;margin:0 auto}
.jsv2{position:absolute;top:44px;left:0;right:0;pointer-events:none}
.jsv2 b{font-size:19px;font-weight:830;font-variant-numeric:tabular-nums}
.jsv2 i{font-style:normal;font-size:10px;color:var(--dim2)}
.jsl{font-size:10px;letter-spacing:1.6px;color:var(--dim2);
font-weight:700;margin-top:6px}

/* ── QUICK ── */
.jgrid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.jqs{display:grid;grid-template-columns:1fr 1fr;gap:7px}
.jq{display:flex;align-items:center;gap:9px;padding:10px;border-radius:11px;
cursor:pointer;text-align:left;transition:.2s var(--ease);
background:rgba(255,255,255,.03);border:1px solid var(--line)}
.jq:hover{background:rgba(124,58,237,.12);border-color:rgba(124,58,237,.4);
transform:translateY(-2px)}
.jqi{width:29px;height:29px;border-radius:9px;flex-shrink:0;display:grid;
place-items:center;color:var(--acc4);
background:linear-gradient(135deg,rgba(124,58,237,.2),rgba(0,230,255,.1))}
.jqt{min-width:0;display:flex;flex-direction:column}
.jqt b{font-size:12.5px;color:var(--txt);white-space:nowrap;
overflow:hidden;text-overflow:ellipsis}
.jqt i{font-style:normal;font-size:10.5px;color:var(--dim2);
white-space:nowrap;overflow:hidden;text-overflow:ellipsis}

/* ── FLAGS ── */
.jfs{display:flex;flex-direction:column;gap:7px}
.jf{display:flex;align-items:center;justify-content:space-between;gap:9px;
padding:10px 12px;border-radius:11px;background:rgba(255,255,255,.03);
border:1px solid var(--line)}
.jf.on{border-color:rgba(34,197,94,.3)}
.jf.off{border-color:rgba(239,68,68,.3)}
.jf b{display:block;font-size:13px}
.jf i{font-style:normal;font-size:10px;letter-spacing:1.1px;font-weight:700}
.jf.on i{color:var(--ok)}
.jf.off i{color:var(--err)}
.jfb{padding:6px 12px;border-radius:8px;font-size:11.5px;font-weight:650;
background:rgba(255,255,255,.05);border:1px solid var(--line2);
color:var(--dim);white-space:nowrap}
.jfb:hover{color:var(--txt);border-color:var(--acc)}
.jstat{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;
padding-top:12px;border-top:1px solid var(--line)}
.jstat div{text-align:center}
.jstat b{display:block;font-size:19px;font-weight:830}
.jstat i{font-style:normal;font-size:10px;color:var(--dim2);
letter-spacing:.9px}

/* ── AI ENGINE ── */
.jai{grid-column:1/-1}
.jaig{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.jaie{padding:11px 13px;border-radius:11px;background:rgba(255,255,255,.03);
border:1px solid var(--line)}
.jaie.on{border-color:rgba(34,197,94,.35);
background:linear-gradient(160deg,rgba(34,197,94,.07),rgba(0,230,255,.03))}
.jaie.off{opacity:.55}
.jaie b{display:block;font-size:13.5px;margin-bottom:1px}
.jaie i{display:block;font-style:normal;font-size:10.5px;font-weight:700;
letter-spacing:.7px;margin-bottom:3px}
.jaie.on i{color:var(--ok)}
.jaie.off i{color:var(--dim3)}
.jaie span{font-size:10.5px;color:var(--dim2)}
.jaib{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;
padding-top:11px;border-top:1px solid var(--line)}
.jaib div{text-align:center}
.jaib i{display:block;font-style:normal;font-size:9.5px;color:var(--dim3);
letter-spacing:.8px;margin-bottom:2px}
.jaib b{font-size:15px;font-variant-numeric:tabular-nums}
@media(max-width:700px){.jaig{grid-template-columns:1fr}
.jaib{grid-template-columns:repeat(2,1fr)}}

/* ── SERVERS ── */
.jsvs{display:flex;flex-direction:column;gap:5px;max-height:250px;
overflow-y:auto}
.jsv{display:flex;align-items:center;gap:10px;padding:8px 11px;
border-radius:10px;background:rgba(255,255,255,.03)}
.jsd{width:8px;height:8px;border-radius:50%;background:var(--dim3);
flex-shrink:0}
.jsd.on{background:var(--ok);box-shadow:0 0 9px var(--ok);
animation:bp 2.2s infinite}
.jsn{flex:1;min-width:0}
.jsn b{display:block;font-size:12.8px;white-space:nowrap;overflow:hidden;
text-overflow:ellipsis}
.jsn i{font-style:normal;font-size:10.5px;color:var(--dim2)}
.jsb{width:28px;height:28px;border-radius:8px;display:grid;
place-items:center;background:rgba(255,255,255,.05);
border:1px solid var(--line2);color:var(--dim)}
.jsb:hover{color:var(--acc4);border-color:var(--acc)}
.jsempty{padding:22px;text-align:center;color:var(--dim2);font-size:13px}

/* ── HISTORY ── */
.jhs{display:flex;flex-direction:column;gap:4px;max-height:250px;
overflow-y:auto}
.jh{display:flex;gap:9px;align-items:center;font-size:11.5px;
padding:6px 10px;border-radius:8px;background:rgba(255,255,255,.025)}
.jht{color:var(--dim3);min-width:30px;font-variant-numeric:tabular-nums}
.jhc{flex:1;color:var(--dim);overflow:hidden;text-overflow:ellipsis;
white-space:nowrap}
.jhr{color:var(--acc4);white-space:nowrap;font-size:11px}

@media(max-width:900px){
.jmain{grid-template-columns:1fr}
.jreactor{min-height:190px}.jring{width:165px;height:165px}
.jgrid{grid-template-columns:1fr}
.jstats{grid-template-columns:repeat(2,1fr)}
.jqs{grid-template-columns:1fr}}
</style>"""


def _js():
    return """<script>
(function(){
 var pending='', SR=window.SpeechRecognition||window.webkitSpeechRecognition;
 var rec=null, listening=false, awake=false, tmo=null;
 var AUTO=(localStorage.getItem('rx_wake')||'0')==='1';
 var WAKE=/\\b(jarvis|jervis|jaarvis|jarwis|jarvish|service)\\b/i;

 function el(i){return document.getElementById(i)}
 function state(s,m){
  var r=el('jrx'),b=el('jmic');
  if(r) r.className='jreactor'+(s?' '+s:'');
  if(b) b.className='jmic'+((s==='listening'||s==='working')?' live':
   (s==='ask'?' ask':''));
  if(el('jrm')) el('jrm').textContent=m||{listening:'listening',
   working:'processing',ask:'awaiting reply',done:'done',
   err:'error'}[s]||'standby';
 }
 function msg(who,txt,cls){
  var l=el('jclog'); if(!l) return;
  var d=document.createElement('div');
  d.className='jm '+who+(cls?' '+cls:'');
  d.innerHTML='<span class="jmi">'+(who==='me'?'\\u25CF':'\\u26A1')+
   '</span><div>'+txt.replace(/</g,'&lt;')+'</div>';
  l.appendChild(d); l.scrollTop=l.scrollHeight;
  while(l.children.length>40) l.removeChild(l.firstChild);
 }
 function speak(t,o){ if(window.jarvis) window.jarvis(t,o); }

 window.jvType=function(){
  var i=el('jtxt'); if(!i||!i.value.trim()) return;
  var t=i.value.trim(); i.value='';
  msg('me',t); state('working'); send(t);
 };

 window.jvSend=function(cmd){
  var lbl={status:'Status batao',users:'Kitne users hain',
   backup:'Backup lo',server_on:'Sab server chalu kar do',
   server_off:'Sab server band kar do',free_off:'Free service band kar do',
   free_on:'Free service chalu kar do',
   maint_on:'Maintenance on kar do'}[cmd]||cmd;
  msg('me',lbl); state('working'); send('jarvis '+lbl);
 };

 function send(txt){
  fetch('/api/jarvis',{method:'POST',
   headers:{'Content-Type':'application/json'},
   body:JSON.stringify({text:txt,pending:pending})})
  .then(function(r){return r.json()}).then(function(d){
   if(d.confirm){
    pending=d.pending; state('ask');
    msg('bot',d.say+'<br><small>Boliye "haan" ya "nahi" — '+
     'ya neeche likh do</small>','warn');
    speak(d.say);
    clearTimeout(tmo);
    tmo=setTimeout(function(){
     if(pending){pending='';state('');
      msg('bot','Time out — cancel kar diya.','err');}},20000);
    if(AUTO||listening) setTimeout(function(){start(false)},900);
    return;
   }
   pending='';
   state(d.ok?'done':'err');
   msg('bot',(d.shown||d.say||'—'),d.ok?'ok':'err');
   if(d.say) speak(d.say);
   if(d.reload) setTimeout(function(){location.reload()},2600);
   else setTimeout(function(){state(AUTO?'':'')},3000);
  }).catch(function(){
   pending=''; state('err'); msg('bot','Server se baat nahi hui','err');
   setTimeout(function(){state('')},2500);
  });
 }

 function start(cont){
  if(!SR||listening) return;
  rec=new SR(); rec.lang='en-IN'; rec.interimResults=true;
  rec.continuous=!!cont; listening=true;
  rec.onresult=function(e){
   var fin='',part='';
   for(var i=e.resultIndex;i<e.results.length;i++){
    var r=e.results[i];
    if(r.isFinal) fin+=r[0].transcript; else part+=r[0].transcript;
   }
   var live=(fin||part).trim();
   if(AUTO&&!awake&&!pending){
    if(WAKE.test(live)){awake=true;state('listening','ji sir…');
     speak('Yes sir?',{rate:1.12});
     clearTimeout(tmo);
     tmo=setTimeout(function(){awake=false;state('')},9000);
    } else return;
   }
   if(live) state(pending?'ask':'listening',live.slice(0,26));
   if(fin.trim()){
    clearTimeout(tmo); var s=fin.trim();
    msg('me',s); state('working'); send(s); awake=false;
    if(!cont) listening=false;
   }
  };
  rec.onerror=function(e){
   listening=false;
   if(e.error==='not-allowed'){AUTO=false;
    localStorage.setItem('rx_wake','0');
    msg('bot','Mic ki permission chahiye — browser me Allow dabaiye','err');
    state('err');setTimeout(function(){state('')},3000);return;}
   if(AUTO) setTimeout(function(){start(true)},700); else state('');
  };
  rec.onend=function(){listening=false;
   if(AUTO) setTimeout(function(){start(true)},350);
   else if(!pending) state('');};
  try{rec.start()}catch(e){listening=false}
 }

 // ══ ASLI RECORDER — har browser me chalta hai ══
 var MR=null, chunks=[], recording=false;

 window.jvRec=function(){
  if(recording){ try{MR.stop()}catch(e){} return; }
  if(!navigator.mediaDevices||!window.MediaRecorder){
   msg('bot','Recording support nahi hai — mic button use kariye','err');
   return;
  }
  navigator.mediaDevices.getUserMedia({audio:{
    channelCount:1, echoCancellation:true, noiseSuppression:true}})
  .then(function(stream){
   chunks=[];
   var mime='';
   ['audio/webm;codecs=opus','audio/webm','audio/ogg;codecs=opus','audio/mp4']
    .forEach(function(m){ if(!mime&&window.MediaRecorder.isTypeSupported(m))
      mime=m; });
   MR=new MediaRecorder(stream, mime?{mimeType:mime}:{});
   MR.ondataavailable=function(e){ if(e.data.size) chunks.push(e.data); };
   MR.onstop=function(){
    recording=false;
    stream.getTracks().forEach(function(t){t.stop()});
    var blob=new Blob(chunks,{type:MR.mimeType||'audio/webm'});
    if(blob.size<1200){ state(''); msg('bot','Kuch sunayi nahi diya','err');
     return; }
    state('working','bhej raha hoon…');
    fetch('/api/jarvis/stt',{method:'POST',
     headers:{'X-Audio-Mime':(MR.mimeType||'audio/webm').split(';')[0]},
     body:blob})
    .then(function(r){return r.json()}).then(function(d){
     if(!d.ok||!d.text){ state('err'); 
      msg('bot',d.err||'Samajh nahi aaya','err');
      setTimeout(function(){state('')},2500); return; }
     msg('me',d.text+' <small>['+(d.engine||'')+']</small>');
     state('working'); send(d.text);
    }).catch(function(){ state('err');
     msg('bot','Server se baat nahi hui','err');
     setTimeout(function(){state('')},2500); });
   };
   MR.start();
   recording=true;
   state('listening','bol rahe hain…');
   speak('Yes sir?',{quick:true});
   // 12 sec max
   setTimeout(function(){ if(recording){try{MR.stop()}catch(e){}} },12000);
  })
  .catch(function(){
   msg('bot','Mic ki permission chahiye — browser me Allow dabaiye','err');
   state('err'); setTimeout(function(){state('')},3000);
  });
 };

 window.jvMic=function(){
  // pehle asli recorder (Sarvam/Gemini — behtar Hinglish)
  if(navigator.mediaDevices&&window.MediaRecorder&&!AUTO){
   return window.jvRec();
  }
  if(!SR){msg('bot','Aapka browser voice support nahi karta. '+
   'Chrome ya Edge use kariye.','err');return;}
  if(AUTO){awake=true;state('listening','ji sir…');
   speak('Yes sir?',{rate:1.12});return;}
  if(listening){try{rec.abort()}catch(e){}listening=false;state('');return;}
  state('listening'); speak('Yes?',{rate:1.12}); start(false);
 };

 window.jvWake=function(){
  AUTO=!AUTO; localStorage.setItem('rx_wake',AUTO?'1':'0');
  var w=el('jwake'); if(w) w.classList.toggle('on',AUTO);
  if(AUTO){msg('bot','Always listening ON. Bas "Jarvis" boliye.','ok');
   speak('Always listening. Bas Jarvis boliye.'); start(true);}
  else{msg('bot','Always listening OFF.');
   speak('Always listening off.');
   try{if(rec){rec.onend=null;rec.abort();}}catch(e){}
   listening=false; state('');}
 };

 // live rings
 function rings(){
  fetch('/api/live').then(function(r){return r.json()}).then(function(d){
   [['cpu',d.cpu,100],['ram',d.ram,100],['disk',d.disk,100],
    ['net',d.dn,1000]].forEach(function(x){
    var v=el('val-'+x[0]), c=el('ring-'+x[0]);
    if(v) v.textContent=x[0]==='net'?x[1]:Math.round(x[1]);
    if(c) c.setAttribute('stroke-dashoffset',
     251-(251*Math.min(1,x[1]/x[2])));
   });
  }).catch(function(){});
 }
 setInterval(rings,2000); rings();

 var w=el('jwake'); if(w) w.classList.toggle('on',AUTO);
 if(AUTO){var go=function(){start(true);
  document.removeEventListener('click',go)};
  document.addEventListener('click',go,{once:true});}
})();
</script>"""
