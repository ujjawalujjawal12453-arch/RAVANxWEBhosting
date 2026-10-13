"""
storagepage.py — Storage ka UI
═══════════════════════════════
Dashboard ke andar "My Storage" page: token, upload, files, KV, logs.
"""

import html
import os
import time

import storage
import theme
from brand import ico, donut
from theme import esc, dash_page


def fsize(n):
    return storage.human(n)


def ago(t):
    return storage.ago(t)


def ficon(name):
    e = os.path.splitext(name)[1].lower()
    return {".py": "🐍", ".js": "🟢", ".json": "🧾", ".zip": "📦",
            ".txt": "📄", ".md": "📘", ".png": "🖼", ".jpg": "🖼",
            ".jpeg": "🖼", ".gif": "🖼", ".mp4": "🎬", ".mp3": "🎵",
            ".db": "🗃", ".sql": "🗃", ".sh": "📜", ".php": "🐘",
            ".go": "🐹", ".rb": "💎", ".html": "🌐", ".css": "🎨",
            ".pdf": "📕", ".apk": "🤖"}.get(e, "📄")


def p_storage(u, msg="", err="", tab="files"):
    a = storage.ensure_for_user(u)
    if not a:
        return dash_page("Storage", "", '<div class="card empty">'
                         '<div class="e">⚠️</div><h3>Storage ready nahi hui</h3>'
                         '</div>', u, "storage")

    q = storage.quota_info(a["id"])
    used, cnt = q["used"], q["files"]
    files = storage.list_files(a["id"])
    kvs = storage.kv_list(a["id"])
    lgs = storage.logs(a["id"], 25)
    st = storage.stats()

    m = ""
    if msg:
        m = f'<div class="msg ok">✅ {esc(msg)}</div>'
    elif err:
        m = f'<div class="msg err">⚠️ {esc(err)}</div>'

    # ── quota bar ──
    pct = q["pct"]
    col = "#EF4444" if pct >= 90 else ("#F59E0B" if pct >= 70 else "#22C55E")
    nx = theme.next_plan(q["plan"])
    upg = (f'<a href="/#pricing" class="btn btn-p btn-sm">'
           f'{ico("up",13)} {nx.title()} lo — {theme.storage_gb(nx)} GB</a>'
           if nx else '<span class="bdg on nd">Sabse bada plan</span>')
    warn = ""
    if pct >= 90:
        warn = ('<div class="msg err" style="margin-top:10px">⚠️ Jagah '
                'khatam hone wali hai — nayi file upload nahi hogi.</div>')
    elif pct >= 70:
        warn = ('<div class="msg warn" style="margin-top:10px">Jagah '
                '70% bhar gayi hai.</div>')

    quota = f"""<div class="card mb">
<div class="flex sb"><h3>{ico("disk",17)} Aapki jagah</h3>
<span class="bdg nd">{q["plan"].title()} plan</span></div>
<div class="qbar mt2"><i style="width:{pct}%;background:{col}"></i></div>
<div class="flex sb mt1" style="font-size:13px">
<span><b style="color:{col}">{q["used_h"]}</b>
<span class="dim"> / {q["cap_h"]} use hui</span></span>
<span class="dim">{q["left_h"]} bachi hai</span></div>
<div class="flex sb mt2" style="flex-wrap:wrap;gap:9px">
<span class="dim xs">Zyada jagah chahiye? Plan upgrade karo.</span>{upg}</div>
{warn}</div>"""

    # ── stat cards ──
    srv_files = len([f for f in files if f["path"].startswith("servers/")])
    mst = storage.mirror_status()
    dk = st["disk"]
    cards = f"""<div class="grid4 mb">
<div class="card st"><div class="i">{ico("db",19)}</div>
<div class="v">{cnt}</div><div class="l">Total files</div></div>
<div class="card st"><div class="i">{ico("disk",19)}</div>
<div class="v" style="color:{col}">{q["used_h"]}</div>
<div class="l">{q["cap_h"]} me se</div></div>
<div class="card st"><div class="i">{ico("server",19)}</div>
<div class="v">{srv_files}</div><div class="l">Server files (auto)</div></div>
<div class="card st"><div class="i">{ico("shield",19)}</div>
<div class="v" style="color:#22C55E">{q["left_h"]}</div>
<div class="l">Bachi hui jagah</div></div></div>"""

    # ── token box ──
    tokbox = f"""<div class="card mb">
<div class="flex sb"><h3>{ico("key",17)} Aapka Storage Token</h3>
<span class="bdg on nd">{ico("check",12)} Active</span></div>
<p class="s mt1">Ye token API ke liye hai — bot, script, curl, kuch bhi.
Kisi ko mat dena.</p>
<div class="tokrow mt2">
<code id="tk" class="tok">{esc(a["token"])}</code>
<button class="btn btn-g btn-sm" onclick="cp()">{ico("code",13)} Copy</button>
</div>
<div class="flex mt2" style="gap:8px;flex-wrap:wrap">
<span class="bdg nd">Account: <b>{esc(a["name"])}</b></span>
<span class="bdg nd">Bana: {ago(a["created"])}</span>
<span class="bdg nd">Aakhri baar: {ago(a["last_seen"])}</span>
</div>
<form method="post" action="/storage/token/reset" class="mt2"
onsubmit="return confirm('Purana token band ho jayega. Pakka?')">
<button class="btn btn-d btn-sm">{ico("refresh",13)} Naya token banao</button>
</form>
<script>function cp(){{navigator.clipboard.writeText(
document.getElementById('tk').innerText);event.target.innerText='✓ Copied';}}</script>
</div>"""

    # ── upload ──
    up = f"""<div class="card mb">
<h3>{ico("up",17)} File upload</h3>
<p class="s mt1">Ek file kitni bhi badi ho — bas aapke plan ki jagah
({q["left_h"]} bachi hai) ke andar honi chahiye. File seedha disk par
likhi jaati hai, RAM me nahi aati.</p>
<form method="post" action="/storage/upload" enctype="multipart/form-data"
class="mt2 upf">
<input type="file" name="file" required>
<input type="text" name="folder" placeholder="folder (optional) jaise: backup"
class="in">
<button class="btn btn-p">{ico("up",14)} Upload karo</button>
</form></div>"""

    # ── file list ──
    if files:
        rows = []
        for f in files[:200]:
            p = f["path"]
            auto = p.startswith("servers/")
            rows.append(f"""<div class="fr">
<span class="ic">{ficon(p)}</span>
<div class="fn"><b>{esc(p)}</b>
{'<span class="bdg nd xs">auto</span>' if auto else ''}
<span class="dim xs">{fsize(f["size"])} · {ago(f["updated"])} · {f["sha"]}</span></div>
<div class="fa">
<a class="btn btn-g btn-sm" href="/storage/get?path={html.escape(p, True)}">
{ico("dl",13)}</a>
<a class="btn btn-d btn-sm" href="/storage/del?path={html.escape(p, True)}"
onclick="return confirm('Trash me bhej dein?')">{ico("trash",13)}</a>
</div></div>""")
        flist = f"""<div class="card mb"><div class="flex sb">
<h3>{ico("folder",17)} Saari files ({cnt})</h3>
<span class="dim xs">delete = trash, hamesha ke liye nahi mitti</span></div>
<div class="mt2">{''.join(rows)}</div></div>"""
    else:
        flist = """<div class="card empty mb"><div class="e">📂</div>
<h3>Abhi koi file nahi</h3><p class="s">Upload karo — ya server par file
daalo, wo apne aap yahan aa jayegi.</p></div>"""

    # ── KV ──
    if kvs:
        kr = "".join(f"""<div class="fr"><span class="ic">🔑</span>
<div class="fn"><b>{esc(k["k"])}</b>
<span class="dim xs">{fsize(k["sz"] or 0)} · {ago(k["updated"])}</span></div>
</div>""" for k in kvs)
    else:
        kr = '<p class="s">Koi key nahi. Database backup yahan aata hai.</p>'
    kvbox = f"""<div class="card mb"><h3>{ico("db",17)} KV store ({len(kvs)})</h3>
<div class="mt2">{kr}</div></div>"""

    # ── logs ──
    if lgs:
        lr = "".join(f"""<div class="lgr"><span class="lga">{esc(l["action"])}</span>
<span class="lgd">{esc(l["detail"])}</span>
<span class="lgt">{ago(l["at"])}</span></div>""" for l in lgs)
    else:
        lr = '<p class="s">Kuch nahi hua abhi tak.</p>'
    logbox = f"""<div class="card mb"><h3>{ico("clock",17)} Activity</h3>
<div class="mt2 lgs">{lr}</div></div>"""

    # ── auto-mirror info ──
    auto = f"""<div class="card mb" style="border-color:rgba(124,58,237,.3)">
<h3>{ico("refresh",17)} Auto-backup chal raha hai</h3>
<p class="s mt1">Aapke server ki saari files har 3 minute me yahan
apne aap copy ho jati hain. Server restart ho, platform data uda de —
sab wapas aa jayega. Aapko kuch nahi karna.</p>
<div class="flex mt2" style="gap:8px;flex-wrap:wrap">
<span class="bdg on nd">{ico("check",12)} ON</span>
<span class="bdg nd">Aakhri baar: {ago(mst.get("last"))}</span>
<span class="bdg nd">{mst.get("files",0)} files last run</span></div></div>"""

    # ── API help ──
    api = f"""<div class="card mb"><h3>{ico("code",17)} API (bahar se bhi chalti hai)</h3>
<pre class="apibox"># Upload (koi bhi size)
curl -T bigfile.zip \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  "$BASE/api/storage/upload?path=backup/bigfile.zip"

# Download
curl -H "Authorization: Bearer YOUR_TOKEN" \\
  "$BASE/api/storage/file?path=backup/bigfile.zip" -o out.zip

# List
curl -H "Authorization: Bearer YOUR_TOKEN" "$BASE/api/storage/files"

# Database (KV)
curl -X POST -d '{{"a":1}}' -H "Authorization: Bearer YOUR_TOKEN" \\
  "$BASE/api/storage/kv?key=mydb"</pre>
<p class="s mt1">Bot me lagana ho to: <code>/setstorage YOUR_TOKEN</code></p>
</div>"""

    css = """<style>
.qbar{height:11px;background:rgba(255,255,255,.07);border-radius:99px;
overflow:hidden}
.qbar i{display:block;height:100%;border-radius:99px;
transition:width .6s cubic-bezier(.4,0,.2,1)}
.tokrow{display:flex;gap:9px;align-items:center;flex-wrap:wrap}
.tok{background:rgba(0,0,0,.45);border:1px solid rgba(124,58,237,.28);
padding:10px 13px;border-radius:9px;font-family:ui-monospace,monospace;
font-size:12.5px;color:#7C3AED;word-break:break-all;flex:1;min-width:220px}
.upf{display:flex;gap:9px;flex-wrap:wrap;align-items:center}
.upf input[type=file]{color:var(--dim);font-size:13px;flex:1;min-width:180px}
.upf .in{padding:9px 12px;border-radius:9px;background:rgba(255,255,255,.04);
border:1px solid rgba(255,255,255,.09);color:#F8FAFC;font-size:13px}
.fr{display:flex;align-items:center;gap:11px;padding:10px 2px;
border-bottom:1px solid rgba(255,255,255,.05)}
.fr:last-child{border:0}
.fr .ic{font-size:19px;width:26px;text-align:center}
.fr .fn{flex:1;min-width:0;display:flex;flex-direction:column;gap:2px}
.fr .fn b{font-size:13.5px;word-break:break-all;font-weight:600}
.fr .fa{display:flex;gap:6px}
.xs{font-size:11.5px}
.lgs{display:flex;flex-direction:column;gap:5px;max-height:330px;overflow:auto}
.lgr{display:flex;gap:10px;align-items:center;font-size:12.5px;
padding:6px 9px;background:rgba(255,255,255,.025);border-radius:7px}
.lga{color:#7C3AED;font-weight:600;min-width:86px}
.lgd{flex:1;color:var(--dim);word-break:break-all}
.lgt{color:var(--dim);font-size:11px;white-space:nowrap}
.apibox{background:rgba(0,0,0,.42);border:1px solid rgba(255,255,255,.07);
border-radius:10px;padding:14px;font-size:12px;overflow:auto;
color:#94A3B8;line-height:1.65;font-family:ui-monospace,monospace}
</style>"""

    body = (css + m + quota + cards + tokbox + auto + up + flist + kvbox
            + api + logbox)
    return dash_page("My Storage",
                     "Aapki saari files — kitni bhi badi, kabhi delete nahi",
                     body, u, "storage")
