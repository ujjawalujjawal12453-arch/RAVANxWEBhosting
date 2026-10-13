"""
👑 AI BOSS ka page — /boss
Pro+ plan aur admin ko hi dikhta hai.
"""

import theme
from theme import ico, esc

try:
    import aiboss
except Exception:
    aiboss = None

try:
    import bossagent
except Exception:
    bossagent = None


def _locked(u, st):
    """Free/Starter wale ko kya dikhega."""
    plan = (u or {}).get("plan", "free")
    return f'''
<div class="card bosslock">
<div class="bltop">{ico("crown", 34)}</div>
<h2>👑 AI BOSS</h2>
<p class="s mt2">Ek AI jo baaki <b>{st["total"]} AI ka boss</b> hai.
Aap kaam batao — wo khud decide karega kaunsa model us kaam ke
liye sabse achha hai, use bhejega, jawab check karega, aur galat
lage to doosre se dobara karwayega.</p>

<div class="blgrid mt">
<div><b>{st["total"]}</b><i>AI model</i></div>
<div><b>{st["job_types"]}</b><i>kaam ke type</i></div>
<div><b>{len(st["providers"])}</b><i>company</i></div>
<div><b>&#8377;0</b><i>extra kharcha</i></div>
</div>

<div class="blwarn mt">
{ico("lock", 15)} Aapka plan: <b>{esc(plan)}</b> &mdash;
AI Boss <b>Pro plan</b> se milta hai.
</div>

<table class="bltab mt">
<tr><th>Plan</th><th>Boss</th><th>Kaam/din</th><th>Team mode</th>
<th>Panel</th></tr>
<tr><td>Free</td><td class="no">&#10007;</td><td>&mdash;</td>
<td class="no">&#10007;</td><td class="no">&#10007;</td></tr>
<tr><td>Starter</td><td class="no">&#10007;</td><td>&mdash;</td>
<td class="no">&#10007;</td><td class="no">&#10007;</td></tr>
<tr class="hl"><td>Pro</td><td class="ye">&#10003;</td><td>40</td>
<td class="no">&#10007;</td><td class="no">&#10007;</td></tr>
<tr><td>Ultra</td><td class="ye">&#10003;</td><td>150</td>
<td class="ye">&#10003;</td><td class="no">&#10007;</td></tr>
<tr><td>Business</td><td class="ye">&#10003;</td><td>500</td>
<td class="ye">&#10003;</td><td class="ye">&#10003;</td></tr>
</table>

<div class="blperks mt">
<div><b>&#128172;</b><span>Live chat — Boss se seedhi baat</span></div>
<div><b>&#127919;</b><span>Model khud chuno ya Boss pe chhodo</span></div>
<div><b>&#129302;</b><span>Boss Agent — file khud theek kare</span></div>
<div><b>&#128081;</b><span>VIP pehchan — Boss aapko naam se jaanega</span></div>
<div><b>&#129504;</b><span>Chat memory — pichhli baat yaad</span></div>
<div><b>&#128640;</b><span>Deploy — poochh kar khud kar de</span></div>
</div>

<p class="dim2 xs mt2"><b>Team mode</b> = ek hi kaam 3 alag model
ko ek saath jaata hai, phir Boss teeno jawab padh kar sabse achha
chunta hai.</p>

<a href="/plans" class="btn btn-p mt">{ico("up2", 15)}
Plan upgrade karo</a>
</div>'''


def _chip(job):
    return (f'<button class="bchip" onclick="bJob(\'{job["id"]}\')" '
            f'data-j="{job["id"]}">{esc(job["name"])}</button>')


def _agent_box(u, is_admin, srv):
    """🕵️ Agent section — Boss ka haath-paanv."""
    if not bossagent:
        return ""
    a = bossagent.status(u, is_admin)
    if not a["on"]:
        return ""
    if not srv:
        return f'''
<div class="card mb">
<h3>{ico("search", 17)} Boss Agent</h3>
<p class="s mt2">Agent aapke server ki files khud uthata hai,
padhta hai, galti dhoondhta hai aur theek karta hai.
<b>Pehle koi server banao</b> — phir yahan dikhega.</p>
<a href="/servers/new" class="btn btn-p btn-sm mt2">
{ico("plus", 13)} Server banao</a></div>'''

    opts = "".join(f'<option value="{s["id"]}">{esc(s["name"])}'
                   f'</option>' for s in srv)
    dep = ("deploy bhi kar sakta hai" if a["deploy"]
           else "deploy Ultra plan se")
    left = a.get("left_txt") or f'{a["left"]}/{a["runs"]} bache'
    unl = a.get("unlimited")
    bdg = (f'<span class="bdg on">{ico("crown",11)} UNLIMITED</span>'
           if unl else
           f'<span class="bdg {"on" if a["left"] > 0 else "warn"}">'
           f'{left}</span>')

    return f'''
<div class="card mb agentcard">
<div class="flex between mb2">
<h3>{ico("search", 17)} Boss Agent
<span class="cdbeta">CHAT</span></h3>
{bdg}</div>

<p class="s">Server chuno aur <b>baat karo</b>. Agent aapki
files khud padhta hai — phir jawab deta hai, bug batata hai,
fix likhta hai. Fix pasand aaye to ek tap me laga do.</p>

<div class="agrow mt2">
<select id="agsrv" class="agsel">{opts}</select>
<button class="btn btn-g btn-sm" onclick="agScan()"
title="Poora scan — saari file ek saath">
{ico("search", 13)} Auto scan</button>
</div>

<div class="agchat" id="agchat">
<div class="cmsg bot"><div class="cav">{ico("search",13)}</div>
<div class="cbub"><b>Boss Agent</b><br>
Namaste! Server chuniye aur poochhiye — jaise:<br>
<i>"mera bot crash kyun ho raha hai"</i><br>
<i>"main.py me kya galti hai"</i><br>
<i>"is error ko theek karo"</i></div></div>
</div>

<div class="agrow mt2">
<input id="agmsg" class="aginp"
placeholder="Agent se poochho..."
onkeydown="if(event.key==='Enter'&&!event.shiftKey)
{{event.preventDefault();agSend()}}">
<button class="btn btn-p" id="agbtn" onclick="agSend()">
{ico("bolt", 14)}</button>
</div>
<p class="dim2 xs mt2">{a["files"]} file tak padhta hai ·
{dep} · purani file hamesha <b>.bak</b> me safe</p>

<div id="agout" class="agout"></div>
</div>'''


def p_boss(u, is_admin=False, srv=None):
    if not aiboss:
        return theme.page("AI Boss", "<div class='card'>Boss module "
                                     "load nahi hua</div>", u, "boss")
    st = aiboss.status(u, is_admin)

    if not st["on"]:
        return theme.page("AI Boss", _locked(u, st), u, "boss")

    jobs = "".join(_chip(j) for j in aiboss.job_list())
    provs = " · ".join(f"{k} {v}" for k, v in
                       sorted(st["providers"].items(), key=lambda x: -x[1]))

    panel = ""
    if st["panel"]:
        panel = f'''
<div class="card mb">
<div class="flex between mb2">
<h3>{ico("chart", 17)} Boss ka Panel <span class="cdbeta">BUSINESS</span></h3>
<button class="btn btn-g btn-sm" onclick="bBoard()">
{ico("refresh", 13)} Refresh</button></div>
<p class="s">Kaunsa model kitna kaam kar raha hai, kiski izzat
kitni hai — Boss ki apni ranking.</p>
<div id="bboard" class="bboard"></div>
</div>'''

    body = rf'''
<div class="bosshead">
<div class="bhleft">
<div class="bhicon">{ico("crown", 26)}</div>
<div>
<h2>AI BOSS</h2>
<p class="dim2 xs">{st["total"]} model · {len(st["providers"])} company
· {st["job_types"]} tarah ke kaam</p>
</div></div>
<div class="bhright">
<div class="bstat"><b>{st["left"]}</b><i>kaam bache</i></div>
<div class="bstat"><b>{st["fan"]}</b><i>model/kaam</i></div>
<div class="bstat {"on" if st["team"] else "off"}">
<b>{"ON" if st["team"] else "OFF"}</b><i>Team mode</i></div>
</div></div>

<div class="card mb chatcard">
<div class="flex between mb2">
<h3>{ico("bolt", 17)} Boss se baat karo</h3>
<span class="viptag" style="--c:{st.get("rank_color","#64748B")}">
{ico("crown", 12)} {esc(st.get("rank", ""))}</span></div>

<div id="bmlim" class="bmlim"></div>

<div class="chatwrap">
<div id="bchat" class="chatbox">
<div class="cmsg bot"><div class="cav">{ico("crown", 14)}</div>
<div class="cbub"><b>Namaste {esc(st.get("who") or "sir")}!</b>
Main aapka AI Boss hoon. {st["total"]} model mere paas hain.
Aap <b>{esc(st.get("rank_label", ""))}</b> hain — batao kya
karna hai?</div></div>
</div>
</div>

<div class="bchips mt2">
<button class="bchip on" onclick="bJob('')" data-j="">
&#10022; Khud pehchano</button>
{jobs}
</div>

<div class="chatbar mt2">
<select id="bmodel" class="cmsel" title="Model chuno">
<option value="">&#9889; Boss khud chune</option>
</select>
<textarea id="bq" class="cminput" rows="1"
placeholder="Yahan likho... (Enter = bhejo)"></textarea>
<button class="cmsend" id="bsend" onclick="bAsk()" title="Bhejo">
{ico("bolt", 17)}</button>
</div>

<div class="flex between mt2 wrap chatfoot">
<div class="flex" style="gap:14px;flex-wrap:wrap">
{'<label class="bteam"><input type="checkbox" id="bteam" checked> Team mode (3 model)</label>' if st["team"] else ''}
<label class="bteam"><input type="checkbox" id="bmem" checked>
Pichhli baat yaad rakhe</label>
</div>
<button class="btn btn-g btn-sm" onclick="bClear()">
{ico("trash", 12)} Saaf karo</button>
</div>
</div>

{_agent_box(u, is_admin, srv or [])}

{panel}

<div class="card">
<h3>{ico("db", 17)} Kaunsi company ke model</h3>
<p class="s mt2">{esc(provs)}</p>
<p class="dim2 xs mt2">Har model 22 Aug 2026 ko live test kiya
gaya. Jo nahi chale wo hataye ja chuke hain.</p>
</div>

<script>
var BJOB = '';
function bJob(j){{
  BJOB = j;
  var all = document.querySelectorAll('.bchip');
  for (var i = 0; i < all.length; i++)
    all[i].className = (all[i].dataset.j === j) ? 'bchip on' : 'bchip';
}}
function bOut(h, cls){{
  var o = document.getElementById('bout');
  if (!o) return;
  o.className = 'bout on ' + (cls || '');
  o.innerHTML = h;
}}
function bEsc(s){{
  return String(s == null ? '' : s).replace(/&/g, '&amp;')
    .replace(/</g, '&lt;').replace(/>/g, '&gt;');
}}
var BHIST = [];
function bScroll(){{
  var c = document.getElementById('bchat');
  if (c) c.scrollTop = c.scrollHeight;
}}
function bAdd(who, html, cls){{
  var c = document.getElementById('bchat');
  if (!c) return null;
  var d = document.createElement('div');
  d.className = 'cmsg ' + who + (cls ? ' ' + cls : '');
  d.innerHTML = '<div class="cav">'
    + (who === 'me' ? '\ud83d\udc64' : '\ud83d\udc51')
    + '</div><div class="cbub">' + html + '</div>';
  c.appendChild(d); bScroll();
  return d;
}}
function bFmt(t){{
  var h = bEsc(t);
  h = h.replace(/```([a-zA-Z0-9]*)\n([\s\S]*?)```/g,
    function(_, l, c){{ return '<pre class="ccode">' + c + '</pre>'; }});
  h = h.replace(/`([^`\n]+)`/g, '<code>$1</code>');
  h = h.replace(/\*\*([^*\n]+)\*\*/g, '<b>$1</b>');
  return h.replace(/\n/g, '<br>');
}}
function bClear(){{
  BHIST = [];
  var c = document.getElementById('bchat');
  if (c) c.innerHTML = '';
  bAdd('bot', 'Chat saaf kar di. Batao kya karna hai?');
}}
function bModels(){{
  var sel = document.getElementById('bmodel');
  if (!sel) return;
  fetch('/api/boss', {{method: 'POST',
    headers: {{'Content-Type': 'application/json'}},
    body: JSON.stringify({{act: 'models'}})}})
  .then(function(r){{ return r.json(); }})
  .then(function(d){{
    if (!d.ok || !d.models) return;
    if (d.limited) {{
      var bar = document.getElementById('bmlim');
      if (bar) bar.innerHTML = '\ud83d\udd13 Aapke paas <b>' + d.mine
        + ' model</b> hain \u00b7 <a href="/#pricing">upgrade karke '
        + 'saare 85 unlock karo</a>';
    }}
    var by = {{}};
    for (var i = 0; i < d.models.length; i++) {{
      var m = d.models[i];
      if (m.k !== 'chat') continue;
      (by[m.p] = by[m.p] || []).push(m);
    }}
    var order = ['groq', 'nvidia', 'gemini', 'sarvam',
                 'openrouter', 'zai'];
    var keys = Object.keys(by).sort(function(a, b){{
      var x = order.indexOf(a), y = order.indexOf(b);
      return (x < 0 ? 99 : x) - (y < 0 ? 99 : y);
    }});
    for (var k = 0; k < keys.length; k++) {{
      var p = keys[k];
      var g = document.createElement('optgroup');
      g.label = p.toUpperCase() + '  (' + by[p].length + ')';
      by[p].sort(function(a, b){{ return a.s - b.s; }});
      for (var j = 0; j < by[p].length; j++) {{
        var m = by[p][j];
        var o = document.createElement('option');
        o.value = m.p + '|' + m.m;
        var nm = m.m.split('/').pop();
        if (m.lock) {{
          o.textContent = '\ud83d\udd12 ' + nm + '  \u00b7 upgrade';
          o.disabled = true;
        }} else {{
          o.textContent = nm + '  \u00b7 ' + m.s + 's  \u00b7 '
            + (m.sk || []).slice(0, 2).join('/');
        }}
        g.appendChild(o);
      }}
      sel.appendChild(g);
    }}
  }}).catch(function(){{}});
}}
function bAsk(){{
  var ta = document.getElementById('bq');
  var q = ta.value.trim();
  if (!q) return;
  var tm = document.getElementById('bteam');
  var mem = document.getElementById('bmem');
  var fm = document.getElementById('bmodel');
  var btn = document.getElementById('bsend');
  bAdd('me', bFmt(q));
  ta.value = ''; ta.style.height = 'auto';
  if (btn) btn.classList.add('busy');
  var wait = bAdd('bot', '<span class="ctype"><i></i><i></i><i></i>'
    + '</span> <span class="dim2">Boss soch raha hai\u2026</span>');
  fetch('/api/boss', {{method: 'POST',
    headers: {{'Content-Type': 'application/json'}},
    body: JSON.stringify({{act: 'ask', text: q, job: BJOB,
      team: tm ? tm.checked : false,
      force: fm ? fm.value : '',
      hist: (mem && mem.checked) ? BHIST.slice(-8) : []}})}})
  .then(function(r){{ return r.json(); }})
  .then(function(d){{
    if (wait) wait.remove();
    if (btn) btn.classList.remove('busy');
    if (!d.ok) {{
      bAdd('bot', '\u2139\ufe0f ' + bEsc(d.msg || d.err
        || 'nahi ho paya'), 'warn');
      return;
    }}
    var meta = '<div class="cmeta"><span class="bjob">'
      + bEsc(d.jobname || d.job) + '</span><span>' + bEsc(d.provider)
      + '/' + bEsc(String(d.model).split('/').pop()) + '</span>'
      + '<span>' + d.ms + 'ms</span>';
    if (d.team) meta += '<span class="bteamtag">TEAM '
      + d.squad + '</span>';
    meta += '</div>';
    var warn = '';
    if (d.swapped)
      warn = '<div class="cswap">\u26a0\ufe0f ' + bEsc(d.swapped)
           + '</div>';
    bAdd('bot', meta + warn + bFmt(d.answer));
    BHIST.push({{r: 'u', t: q}});
    BHIST.push({{r: 'a', t: d.answer}});
    if (BHIST.length > 16) BHIST = BHIST.slice(-16);
  }})
  .catch(function(e){{
    if (wait) wait.remove();
    if (btn) btn.classList.remove('busy');
    bAdd('bot', '\u274c ' + bEsc(e), 'warn');
  }});
}}
(function(){{
  bModels();
  var ta = document.getElementById('bq');
  if (!ta) return;
  ta.addEventListener('input', function(){{
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 130) + 'px';
  }});
  ta.addEventListener('keydown', function(e){{
    if (e.key === 'Enter' && !e.shiftKey) {{ e.preventDefault(); bAsk(); }}
  }});
}})();
var AGID = '';
function agOut(h, cls){{
  var o = document.getElementById('agout');
  if (!o) return;
  o.className = 'agout on ' + (cls || '');
  o.innerHTML = h;
}}
function agPost(body, cb){{
  fetch('/api/agent', {{method: 'POST',
    headers: {{'Content-Type': 'application/json'}},
    body: JSON.stringify(body)}})
  .then(function(r){{ return r.json(); }}).then(cb)
  .catch(function(e){{ agOut('\u274c ' + bEsc(e), 'err'); }});
}}
// ═══ 💬 AGENT SE BAAT ═══
//
// Malik ka hukum: "chat board jaisa rahega, usse hum baat
// kar sake". Isliye ab poora chat hai — agent file padh kar
// jawab deta hai.
var AGHIST = [];
var AGBUSY = false;

function agEsc(t){{
  return String(t == null ? '' : t)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}}

// Code block ko sundar dikhao
function agMd(t){{
  var out = '', parts = String(t).split('```');
  for (var i = 0; i < parts.length; i++) {{
    if (i % 2 === 0) {{
      out += agEsc(parts[i]).replace(/\n/g, '<br>')
             .replace(/\*\*(.+?)\*\*/g, '<b>$1</b>')
             .replace(/`([^`]+)`/g, '<code>$1</code>');
    }} else {{
      var c = parts[i].replace(/^[a-zA-Z]*\n/, '');
      out += '<pre class="agcode">' + agEsc(c) + '</pre>';
    }}
  }}
  return out;
}}

function agAdd(who, html){{
  var box = document.getElementById('agchat');
  if (!box) return null;
  var d = document.createElement('div');
  d.className = 'cmsg ' + (who === 'u' ? 'me' : 'bot');
  d.innerHTML = (who === 'u'
    ? '<div class="cbub">' + html + '</div>'
    : '<div class="cav">\u26a1</div><div class="cbub">'
      + html + '</div>');
  box.appendChild(d);
  box.scrollTop = box.scrollHeight;
  return d;
}}

function agSend(){{
  if (AGBUSY) return;
  var inp = document.getElementById('agmsg');
  var txt = (inp.value || '').trim();
  if (!txt) return;
  var sel = document.getElementById('agsrv');
  var sid = parseInt((sel && sel.value) || 0);
  if (!sid) {{ agAdd('b', 'Pehle upar se server chuniye.'); return; }}

  inp.value = '';
  AGBUSY = true;
  var btn = document.getElementById('agbtn');
  if (btn) btn.disabled = true;

  agAdd('u', agEsc(txt).replace(/\n/g, '<br>'));
  var wait = agAdd('b',
    '<span class="agdots"><i></i><i></i><i></i></span> '
    + 'file padh raha hoon\u2026');

  fetch('/api/agent', {{
    method: 'POST',
    headers: {{'Content-Type': 'application/json'}},
    body: JSON.stringify({{act: 'chat', sid: sid, text: txt,
                          hist: AGHIST.slice(-6)}})
  }})
  .then(function(r){{ return r.json(); }})
  .then(function(d){{
    if (wait && wait.parentNode) wait.parentNode.removeChild(wait);
    AGBUSY = false;
    if (btn) btn.disabled = false;

    if (!d.ok) {{
      agAdd('b', '\u26a0\ufe0f ' + agEsc(d.msg || d.err || 'fail'));
      return;
    }}
    var h = agMd(d.answer || '');
    var meta = [];
    if (d.files_read) meta.push(d.files_read + ' file padhi');
    if (d.crashed) meta.push('\u26a0\ufe0f crash mila');
    if (d.ms) meta.push(d.ms + 'ms');
    if (d.left >= 0) meta.push(d.left + ' run bache');
    if (meta.length)
      h += '<div class="agmeta">' + meta.join(' \u00b7 ') + '</div>';

    // fix taiyaar hai? — lagane ka button
    if (d.plan_id) {{
      h += '<div class="agfix">'
         + '<b>\u2713 Fix taiyaar hai</b>'
         + '<span>' + agEsc(d.file || '') + '</span>'
         + '<button class="btn btn-p btn-sm" '
         + 'onclick="agApply(\'' + d.plan_id + '\', this)">'
         + 'File me laga do</button></div>';
    }} else if (d.no_fix) {{
      // Code to aaya par lagane layak nahi — wajah batao.
      // Warna user ko lagta hai kuch hua hi nahi.
      h += '<div class="agfix agwarn">'
         + '<b>\u26a0\ufe0f Ye code apne aap nahi laga sakta</b>'
         + '<span>' + agEsc(d.no_fix) + '</span>'
         + '<span class="dim2 xs">Upar wala code copy karke '
         + 'File Manager se daal dijiye.</span></div>';
    }}
    agAdd('b', h);
    AGHIST.push({{r: 'u', t: txt}});
    AGHIST.push({{r: 'a', t: (d.answer || '').slice(0, 900)}});
  }})
  .catch(function(e){{
    if (wait && wait.parentNode) wait.parentNode.removeChild(wait);
    AGBUSY = false;
    if (btn) btn.disabled = false;
    agAdd('b', '\u26a0\ufe0f Network problem: ' + agEsc(e));
  }});
}}

function agApply(pid, btn){{
  btn.disabled = true;
  btn.textContent = 'Laga raha hoon\u2026';
  agPost({{act: 'apply', id: pid}}, function(d){{
    if (d.ok) {{
      btn.textContent = '\u2705 Lag gaya';
      agAdd('b', 'File update ho gayi. Purani <b>.bak</b> me '
               + 'safe hai. Ab server restart karke dekhiye.');
    }} else {{
      btn.disabled = false;
      btn.textContent = 'Dobara try';
      agAdd('b', '\u26a0\ufe0f ' + agEsc(d.msg || d.err));
    }}
  }});
}}

function agScan(){{
  var sid = parseInt(document.getElementById('agsrv').value || 0);
  var note = '';
  agOut('<div class="cdload"><i></i><i></i><i></i>'
      + '<span>Agent files uthaa raha hai\u2026</span></div>');
  agPost({{act: 'scan', sid: sid, note: note}}, function(d){{
    if (!d.ok) {{ agOut('\u2139\ufe0f ' + bEsc(d.msg || d.err),
                        'warn'); return; }}
    AGID = d.id;
    var h = '<div class="agsay">\ud83d\udd75\ufe0f '
          + bEsc(d.say) + '</div>';
    h += '<div class="agfiles">';
    for (var i = 0; i < d.steps.length; i++) {{
      var s = d.steps[i];
      var cl = s.st === 'fix' ? 'bad' : (s.st === 'clean' ? 'ok' : 'warn');
      var ic = s.st === 'fix' ? '\u26a0\ufe0f'
             : (s.st === 'clean' ? '\u2713' : '\u2717');
      h += '<div class="agf ' + cl + '"><b>' + ic + ' '
         + bEsc(s.file) + '</b>';
      if (s.why) for (var k = 0; k < s.why.length && k < 4; k++)
        h += '<i>\u00b7 ' + bEsc(s.why[k]) + '</i>';
      else h += '<i>' + bEsc(s.msg) + '</i>';
      if (s.model) h += '<u>' + bEsc(s.prov || '') + '/'
                      + bEsc(String(s.model).split('/').pop()) + '</u>';
      h += '</div>';
    }}
    h += '</div>';
    h += '<div class="agmeta">' + d.scanned + ' file padhi \u00b7 '
       + d.found + ' me galti \u00b7 ' + d.ms + 'ms</div>';
    if (d.ask === 'apply') {{
      h += '<div class="agask"><b>Sir, ye ' + d.found
         + ' file theek kar dun?</b>'
         + '<div class="agbtns">'
         + '<button class="btn btn-p btn-sm" onclick="agApply()">'
         + '\u2713 Haan, kar do</button>'
         + '<button class="btn btn-g btn-sm" onclick="agOut('
         + "'\\u270b Theek hai sir, rehne diya','warn')"
         + '">\u2717 Nahi</button></div></div>';
    }}
    agOut(h, d.found ? 'warn' : 'ok');
  }});
}}
function agApply(){{
  agOut('<div class="cdload"><i></i><i></i><i></i>'
      + '<span>Files badal raha hoon (backup ke saath)\u2026</span></div>');
  agPost({{act: 'apply', id: AGID}}, function(d){{
    if (!d.ok) {{ agOut('\u2139\ufe0f ' + bEsc(d.msg), 'warn'); return; }}
    var h = '<div class="agsay">\u2705 ' + bEsc(d.msg) + '</div>';
    if (d.done && d.done.length) {{
      h += '<div class="agfiles">';
      for (var i = 0; i < d.done.length; i++)
        h += '<div class="agf ok"><b>\u2713 ' + bEsc(d.done[i])
           + '</b><i>\ud83d\udcbe purana ' + bEsc(d.done[i])
           + '.bak me safe</i></div>';
      h += '</div>';
    }}
    if (d.ask === 'deploy') {{
      h += '<div class="agask"><b>Ab deploy kar dun?</b>'
         + '<div class="agbtns">'
         + '<button class="btn btn-p btn-sm" onclick="agDeploy()">'
         + '\ud83d\ude80 Haan, deploy karo</button>'
         + '<button class="btn btn-g btn-sm" onclick="agUndo()">'
         + '\u21a9 Wapas purana karo</button></div></div>';
    }} else {{
      h += '<div class="agbtns mt2">'
         + '<button class="btn btn-g btn-sm" onclick="agUndo()">'
         + '\u21a9 Wapas purana karo</button></div>';
    }}
    agOut(h, 'ok');
  }});
}}
function agDeploy(){{
  agOut('<div class="cdload"><i></i><i></i><i></i>'
      + '<span>Deploy kar raha hoon\u2026</span></div>');
  agPost({{act: 'deploy', id: AGID}}, function(d){{
    if (!d.ok) {{ agOut('\u2139\ufe0f ' + bEsc(d.msg), 'warn'); return; }}
    var h = '<div class="agsay">'
          + (d.worked ? '\ud83c\udf89 ' : '\u26a0\ufe0f ')
          + bEsc(d.msg) + '</div>';
    h += '<div class="agbtns mt2">';
    if (d.ask === 'retry')
      h += '<button class="btn btn-p btn-sm" onclick="agScan()">'
         + '\ud83d\udd0d Haan, dobara dhoondho</button>';
    h += '<button class="btn btn-g btn-sm" onclick="agUndo()">'
       + '\u21a9 Wapas purana karo</button></div>';
    agOut(h, d.worked ? 'ok' : 'warn');
  }});
}}
function agUndo(){{
  agPost({{act: 'undo', id: AGID}}, function(d){{
    agOut((d.ok ? '\u21a9 ' : '\u2139\ufe0f ') + bEsc(d.msg),
          d.ok ? 'ok' : 'warn');
  }});
}}
function bBoard(){{
  var o = document.getElementById('bboard');
  if (!o) return;
  o.innerHTML = '<div class="cdload"><i></i><i></i><i></i></div>';
  fetch('/api/boss', {{method: 'POST',
    headers: {{'Content-Type': 'application/json'}},
    body: JSON.stringify({{act: 'board'}})}})
  .then(function(r){{ return r.json(); }})
  .then(function(d){{
    if (!d.ok) {{ o.innerHTML = 'Panel nahi mila'; return; }}
    var h = '<table class="btab"><tr><th>#</th><th>Model</th>'
          + '<th>Company</th><th>Kaam</th><th>Izzat</th>'
          + '<th>Speed</th></tr>';
    for (var i = 0; i < d.board.length; i++) {{
      var r = d.board[i];
      var pc = Math.round(r.rep * 100);
      h += '<tr><td data-l="Rank">#' + (i + 1) + '</td>'
        + '<td class="bm" data-l="Model">'
        + bEsc(r.model.split('/').pop()) + '</td>'
        + '<td data-l="Company">' + bEsc(r.prov) + '</td>'
        + '<td data-l="Kaam">' + r.used + '</td>'
        + '<td data-l="Bharosa"><span class="brep" style="--w:' + pc + '%">'
        + pc + '%</span></td>'
        + '<td data-l="Speed">' + r.ms + 'ms</td></tr>';
    }}
    h += '</table>';
    o.innerHTML = h;
  }})
  .catch(function(e){{ o.innerHTML = 'Error: ' + bEsc(e); }});
}}
{'bBoard();' if st["panel"] else ''}
</script>'''
    return theme.page("AI Boss", body, u, "boss")
