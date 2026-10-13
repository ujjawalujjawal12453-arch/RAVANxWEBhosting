"""
brand.py — RAVAN X CLOUD ka asli logo aur brand system
═══════════════════════════════════════════════════════
Sab SVG — kabhi pixelate nahi hoga, koi image file nahi.
"""

# ─────────────────────────────────────────────────────────
#  LOGO — hexagon cloud + circuit (hosting + power)
# ─────────────────────────────────────────────────────────

def logo_mark(size=34, glow=True):
    g = f'''<filter id="lg{size}" x="-50%" y="-50%" width="200%" height="200%">
<feGaussianBlur stdDeviation="2.5" result="b"/>
<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>''' if glow else ""
    fg = f'filter="url(#lg{size})"' if glow else ""
    return f'''<svg width="{size}" height="{size}" viewBox="0 0 48 48"
fill="none" xmlns="http://www.w3.org/2000/svg" class="lmark">
<defs>{g}
<linearGradient id="lgr{size}" x1="4" y1="2" x2="44" y2="46">
<stop stop-color="#22D3EE"/><stop offset=".5" stop-color="#00E6FF"/>
<stop offset="1" stop-color="#1a5fd0"/></linearGradient>
<linearGradient id="lin{size}" x1="12" y1="12" x2="36" y2="36">
<stop stop-color="#F8FAFC"/><stop offset="1" stop-color="#CBD5E1"/>
</linearGradient></defs>
<path d="M24 2 43 13v22L24 46 5 35V13z" fill="url(#lgr{size})" {fg}/>
<path d="M24 2 43 13v22L24 46 5 35V13z" stroke="#67E8F9"
stroke-opacity=".45" stroke-width="1.1"/>
<path d="M18.5 30.5h11.8a4.4 4.4 0 0 0 .5-8.77 6.6 6.6 0 0 0-12.68-1.5
 4.6 4.6 0 0 0 .38 10.27z" fill="url(#lin{size})"/>
<circle cx="24" cy="35.6" r="1.5" fill="#F8FAFC" opacity=".92"/>
<path d="M24 34.1v-2.6" stroke="#F8FAFC" stroke-width="1.3"
stroke-linecap="round" opacity=".72"/>
<circle cx="17.4" cy="34.4" r="1.05" fill="#CBD5E1" opacity=".7"/>
<circle cx="30.6" cy="34.4" r="1.05" fill="#CBD5E1" opacity=".7"/>
</svg>'''


def logo(size=34, text=True, sub=False):
    if not text:
        return logo_mark(size)
    s = ('<span class="lsub">CLOUD</span>' if sub else '')
    return f'''<span class="lg">{logo_mark(size)}
<span class="ltx"><b>RAVAN</b><em>X</em>{s}</span></span>'''


def favicon():
    """Data-URI favicon — koi file nahi chahiye."""
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">'
           '<defs><linearGradient id="g" x1="4" y1="2" x2="44" y2="46">'
           '<stop stop-color="%234d9fff"/><stop offset="1" stop-color="%231a5fd0"/>'
           '</linearGradient></defs>'
           '<path d="M24 2 43 13v22L24 46 5 35V13z" fill="url(%23g)"/>'
           '<path d="M18.5 30.5h11.8a4.4 4.4 0 0 0 .5-8.77 6.6 6.6 0 0 0-12.68-1.5'
           ' 4.6 4.6 0 0 0 .38 10.27z" fill="%23eaf3ff"/></svg>')
    return f'<link rel="icon" href="data:image/svg+xml,{svg}">'


# ─────────────────────────────────────────────────────────
#  ICONS — stroke SVG (emoji nahi)
# ─────────────────────────────────────────────────────────

_I = {
    "grid": "M3 3h7v7H3zM14 3h7v7h-7zM14 14h7v7h-7zM3 14h7v7H3z",
    "server": "M4 4h16v6H4zM4 14h16v6H4z|M8 7h.01M8 17h.01",
    "plus": "M12 5v14M5 12h14",
    "folder": "M3 6a2 2 0 0 1 2-2h4l2 3h8a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z",
    "term": "m5 8 4 4-4 4M13 16h6",
    "chart": "M3 21h18M7 17V9M12 17V5M17 17v-6",
    "wallet": "M3 7a2 2 0 0 1 2-2h13a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z|M16 12h.01",
    "card": "M2 7h20v11H2zM2 11h20",
    "user": "M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2|M12 3a4 4 0 1 1 0 8 4 4 0 0 1 0-8",
    "help": "M12 3a9 9 0 1 1 0 18 9 9 0 0 1 0-18|M9.1 9a3 3 0 0 1 5.8 1c0 2-3 3-3 3M12 17h.01",
    "crown": "M3 7l4 4 5-7 5 7 4-4v10H3z",
    "bolt": "M13 2 4 14h6l-1 8 9-12h-6z",
    "shield": "M12 2 4 5v6c0 5 3.4 9.4 8 11 4.6-1.6 8-6 8-11V5z",
    "clock": "M12 3a9 9 0 1 1 0 18 9 9 0 0 1 0-18|M12 7v5l3 2",
    "up": "M3 17l6-6 4 4 7-7|M14 8h6v6",
    "cpu": "M6 6h12v12H6z|M9 2v4M15 2v4M9 18v4M15 18v4M2 9h4M2 15h4M18 9h4M18 15h4",
    "ram": "M3 8h18v8H3z|M7 8v8M12 8v8M17 8v8",
    "disk": "M12 3a9 9 0 1 1 0 18 9 9 0 0 1 0-18|M12 10a2 2 0 1 1 0 4 2 2 0 0 1 0-4",
    "globe": "M12 3a9 9 0 1 1 0 18 9 9 0 0 1 0-18|M3 12h18M12 3c2.5 2.7 2.5 15.3 0 18",
    "check": "M20 6 9 17l-5-5",
    "x": "M18 6 6 18M6 6l12 12",
    "play": "m6 4 14 8-14 8z",
    "stop": "M6 6h12v12H6z",
    "refresh": "M21 12a9 9 0 1 1-3-6.7|M21 3v6h-6",
    "trash": "M3 6h18M8 6V4h8v2M6 6l1 14h10l1-14",
    "up2": "M12 19V5M5 12l7-7 7 7",
    "dl": "M12 3v12M7 10l5 5 5-5M4 21h16",
    "code": "m8 6-6 6 6 6M16 6l6 6-6 6",
    "lock": "M5 11h14v10H5z|M8 11V7a4 4 0 0 1 8 0v4",
    "bell": "M18 8a6 6 0 1 0-12 0c0 7-3 8-3 8h18s-3-1-3-8|M13.7 21a2 2 0 0 1-3.4 0",
    "mic": "M12 2a3 3 0 0 1 3 3v7a3 3 0 0 1-6 0V5a3 3 0 0 1 3-3|M19 10v2a7 7 0 0 1-14 0v-2|M12 19v3M8 22h8",
    "speaker": "M11 5 6 9H2v6h4l5 4z|M15.5 8.5a5 5 0 0 1 0 7M19 5a9 9 0 0 1 0 14",
    "mute": "M11 5 6 9H2v6h4l5 4z|M22 9l-6 6M16 9l6 6",
    "search": "M11 4a7 7 0 1 1 0 14 7 7 0 0 1 0-14|m20 20-4-4",
    "menu": "M3 6h18M3 12h18M3 18h18",
    "logout": "M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4|m16 17 5-5-5-5M21 12H9",
    "rocket": "M5 13c-1.5 1.5-2 5-2 5s3.5-.5 5-2M9 15l-3-3 5-6a9 9 0 0 1 8-4 9 9 0 0 1-4 8z|M14 10h.01",
    "spark": "m12 2 2.4 6.6L21 11l-6.6 2.4L12 20l-2.4-6.6L3 11l6.6-2.4z",
    "db": "M4 6c0-1.7 3.6-3 8-3s8 1.3 8 3-3.6 3-8 3-8-1.3-8-3|M4 6v12c0 1.7 3.6 3 8 3s8-1.3 8-3V6|M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3",
    "file": "M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z|M14 3v5h5",
    "edit": "M12 20h9|M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z",
    "eye": "M2 12s4-7 10-7 10 7 10 7-4 7-10 7-10-7-10-7|M12 9a3 3 0 1 1 0 6 3 3 0 0 1 0-6",
    "star": "m12 2 3.1 6.3 6.9 1-5 4.9 1.2 6.8-6.2-3.3-6.2 3.3L7 14.2l-5-4.9 6.9-1z",
    "gift": "M20 12v9H4v-9|M2 7h20v5H2zM12 21V7|M12 7H7.5a2.5 2.5 0 1 1 0-5C11 2 12 7 12 7M12 7h4.5a2.5 2.5 0 1 0 0-5C13 2 12 7 12 7",
    "ticket": "M3 8a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v2a2 2 0 0 0 0 4v2a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-2a2 2 0 0 0 0-4z",
    "key": "M15 2a7 7 0 1 0-6.7 9L7 12.3V15H4v3H2v3h5l7.3-7.3A7 7 0 0 0 15 2|M17 6h.01",
}


def ico(name, size=17, cls=""):
    d = _I.get(name, _I["grid"])
    paths = "".join(f'<path d="{p}"/>' for p in d.split("|"))
    return (f'<svg class="i {cls}" width="{size}" height="{size}" '
            f'viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="1.9" stroke-linecap="round" '
            f'stroke-linejoin="round">{paths}</svg>')


# ─────────────────────────────────────────────────────────
#  CHARTS — pure SVG, koi library nahi
# ─────────────────────────────────────────────────────────

def sparkline(vals, w=110, h=34, color="#00E6FF", fill=True, sid="s"):
    """Chhoti line chart — stat card ke liye."""
    if not vals or len(vals) < 2:
        vals = [0, 0]
    lo, hi = min(vals), max(vals)
    rng = (hi - lo) or 1
    step = w / (len(vals) - 1)
    pts = [(i * step, h - 3 - ((v - lo) / rng) * (h - 8))
           for i, v in enumerate(vals)]
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    area = ""
    if fill:
        area = (f'<defs><linearGradient id="sp{sid}" x1="0" y1="0" x2="0" y2="1">'
                f'<stop stop-color="{color}" stop-opacity=".35"/>'
                f'<stop offset="1" stop-color="{color}" stop-opacity="0"/>'
                f'</linearGradient></defs>'
                f'<polygon points="0,{h} {line} {w},{h}" fill="url(#sp{sid})"/>')
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'class="spark">{area}<polyline points="{line}" fill="none" '
            f'stroke="{color}" stroke-width="2" stroke-linecap="round" '
            f'stroke-linejoin="round"/>'
            f'<circle cx="{pts[-1][0]:.1f}" cy="{pts[-1][1]:.1f}" r="2.6" '
            f'fill="{color}"/></svg>')


def minibars(vals, w=104, h=32, color="#00E6FF"):
    """Chhote bars — usage ke liye."""
    if not vals:
        vals = [0]
    hi = max(vals) or 1
    n = len(vals)
    bw = w / n * .62
    gap = w / n
    bars = ""
    for i, v in enumerate(vals):
        bh = max(2.5, (v / hi) * (h - 4))
        op = .35 + .65 * (v / hi)
        bars += (f'<rect x="{i*gap:.1f}" y="{h-bh:.1f}" width="{bw:.1f}" '
                 f'height="{bh:.1f}" rx="1.8" fill="{color}" '
                 f'opacity="{op:.2f}"/>')
    return f'<svg width="{w}" height="{h}" class="mbars">{bars}</svg>'


def donut(pct, size=120, stroke=11, color="#00E6FF", label="", sub=""):
    """Ring chart — bada number ke saath."""
    pct = max(0, min(100, pct))
    r = (size - stroke) / 2
    c = 2 * 3.14159 * r
    off = c * (1 - pct / 100)
    cx = size / 2
    return f'''<div class="donut">
<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">
<circle cx="{cx}" cy="{cx}" r="{r}" fill="none" stroke="#131A2B"
stroke-width="{stroke}"/>
<circle cx="{cx}" cy="{cx}" r="{r}" fill="none" stroke="{color}"
stroke-width="{stroke}" stroke-linecap="round"
stroke-dasharray="{c:.1f}" stroke-dashoffset="{off:.1f}"
transform="rotate(-90 {cx} {cx})" class="dring"/></svg>
<div class="dctr"><b>{label or f"{int(pct)}%"}</b>
{f"<span>{sub}</span>" if sub else ""}</div></div>'''


def gauge(pct, w=200, h=104, color="#00E6FF"):
    """Half-circle gauge."""
    pct = max(0, min(100, pct))
    r, cx, cy = 78, w / 2, h - 8
    import math
    a = math.pi * (1 - pct / 100)
    x, y = cx + r * math.cos(a), cy - r * math.sin(a)
    c = math.pi * r
    return f'''<svg width="{w}" height="{h}" class="gauge">
<path d="M{cx-r} {cy}A{r} {r} 0 0 1 {cx+r} {cy}" fill="none"
stroke="#131A2B" stroke-width="12" stroke-linecap="round"/>
<path d="M{cx-r} {cy}A{r} {r} 0 0 1 {cx+r} {cy}" fill="none"
stroke="{color}" stroke-width="12" stroke-linecap="round"
stroke-dasharray="{c:.1f}" stroke-dashoffset="{c*(1-pct/100):.1f}"/>
<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{color}"/>
<circle cx="{x:.1f}" cy="{y:.1f}" r="2.6" fill="#0b1220"/></svg>'''


# ─────────────────────────────────────────────────────────
#  📈 BIG AREA CHART — dot grid + points + labels
# ─────────────────────────────────────────────────────────

def areachart(vals, w=520, h=190, color="#00E6FF", sid="a",
              unit="%", ymax=None, labels=None):
    """
    Poora chart: grid lines, dotted background, area fill,
    smooth line, har point par dot, hover values.
    """
    if not vals or len(vals) < 2:
        vals = [0, 0]
    pad_l, pad_r, pad_t, pad_b = 42, 12, 14, 22
    iw = w - pad_l - pad_r
    ih = h - pad_t - pad_b
    hi = ymax if ymax is not None else (max(vals) or 1)
    hi = max(hi, 1)
    step = iw / (len(vals) - 1)

    pts = [(pad_l + i * step, pad_t + ih - (min(v, hi) / hi) * ih)
           for i, v in enumerate(vals)]

    # grid
    grid = ""
    for k in range(5):
        y = pad_t + ih * k / 4
        val = hi * (1 - k / 4)
        grid += (f'<line x1="{pad_l}" y1="{y:.1f}" x2="{w-pad_r}" y2="{y:.1f}" '
                 f'stroke="#1E293B" stroke-width="1" '
                 f'{"stroke-dasharray=3,4" if k else ""}/>'
                 f'<text x="{pad_l-7}" y="{y+3.5:.1f}" fill="#64748B" '
                 f'font-size="9.5" text-anchor="end" '
                 f'font-family="monospace">{val:.0f}</text>')
    # vertical dots
    for i in range(0, len(vals), max(1, len(vals) // 8)):
        x = pad_l + i * step
        grid += (f'<line x1="{x:.1f}" y1="{pad_t}" x2="{x:.1f}" '
                 f'y2="{pad_t+ih}" stroke="#111827" stroke-width="1" '
                 f'stroke-dasharray="2,5"/>')

    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    dots = "".join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.6" fill="{color}" '
        f'stroke="#070B14" stroke-width="1.4"><title>{vals[i]:.1f}{unit}</title>'
        f'</circle>' for i, (x, y) in enumerate(pts))
    lastx, lasty = pts[-1]

    return f'''<svg viewBox="0 0 {w} {h}" class="achart" preserveAspectRatio="none">
<defs><linearGradient id="ag{sid}" x1="0" y1="0" x2="0" y2="1">
<stop stop-color="{color}" stop-opacity=".38"/>
<stop offset="1" stop-color="{color}" stop-opacity="0"/></linearGradient>
<filter id="gl{sid}"><feGaussianBlur stdDeviation="2.5" result="b"/>
<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter></defs>
{grid}
<polygon points="{pad_l},{pad_t+ih} {line} {w-pad_r},{pad_t+ih}"
fill="url(#ag{sid})"/>
<polyline points="{line}" fill="none" stroke="{color}" stroke-width="2.2"
stroke-linecap="round" stroke-linejoin="round" filter="url(#gl{sid})"/>
{dots}
<circle cx="{lastx:.1f}" cy="{lasty:.1f}" r="5" fill="{color}"
opacity=".28"><animate attributeName="r" values="4;9;4" dur="2s"
repeatCount="indefinite"/><animate attributeName="opacity"
values=".4;0;.4" dur="2s" repeatCount="indefinite"/></circle>
<circle cx="{lastx:.1f}" cy="{lasty:.1f}" r="3.4" fill="{color}"
stroke="#070B14" stroke-width="1.6"/>
</svg>'''


def multichart(series, w=520, h=200, sid="m", ymax=100):
    """
    Ek hi chart me kayi lines — CPU + RAM + DISK saath me.
    series = [(name, [vals], color), ...]
    """
    pad_l, pad_r, pad_t, pad_b = 42, 12, 14, 26
    iw, ih = w - pad_l - pad_r, h - pad_t - pad_b
    n = max(len(v) for _, v, _ in series) if series else 2
    n = max(n, 2)
    step = iw / (n - 1)

    grid = ""
    for k in range(5):
        y = pad_t + ih * k / 4
        grid += (f'<line x1="{pad_l}" y1="{y:.1f}" x2="{w-pad_r}" y2="{y:.1f}" '
                 f'stroke="#1E293B" stroke-width="1" '
                 f'{"stroke-dasharray=3,4" if k else ""}/>'
                 f'<text x="{pad_l-7}" y="{y+3.5:.1f}" fill="#64748B" '
                 f'font-size="9.5" text-anchor="end" font-family="monospace">'
                 f'{ymax*(1-k/4):.0f}</text>')
    for i in range(0, n, max(1, n // 8)):
        x = pad_l + i * step
        grid += (f'<line x1="{x:.1f}" y1="{pad_t}" x2="{x:.1f}" y2="{pad_t+ih}" '
                 f'stroke="#111827" stroke-width="1" stroke-dasharray="2,5"/>')

    body, legend = "", ""
    for si, (name, vals, color) in enumerate(series):
        if not vals:
            vals = [0, 0]
        v = ([vals[0]] * (n - len(vals))) + list(vals) if len(vals) < n else vals[-n:]
        pts = [(pad_l + i * step, pad_t + ih - (min(x, ymax) / ymax) * ih)
               for i, x in enumerate(v)]
        line = " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)
        body += (f'<polyline points="{line}" fill="none" stroke="{color}" '
                 f'stroke-width="2" stroke-linecap="round" '
                 f'stroke-linejoin="round" opacity=".95"/>')
        for a, b in pts[::max(1, len(pts) // 12)]:
            body += (f'<circle cx="{a:.1f}" cy="{b:.1f}" r="2.1" '
                     f'fill="{color}"/>')
        lx, ly = pts[-1]
        body += (f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="3.4" fill="{color}" '
                 f'stroke="#070B14" stroke-width="1.5"/>')
        legend += (f'<span class="lgi"><i style="background:{color}"></i>'
                   f'{name} <b>{v[-1]:.0f}%</b></span>')

    return (f'<svg viewBox="0 0 {w} {h}" class="achart" '
            f'preserveAspectRatio="none">{grid}{body}</svg>'
            f'<div class="lgnd">{legend}</div>')


# ─────────────────────────────────────────────────────────
#  📊 ANIMATED BAR GRAPH — har bar CSS se badhta hai
# ─────────────────────────────────────────────────────────

def bargraph(vals, w=520, h=200, color="#7C3AED", sid="bg",
             unit="%", ymax=None, labels=None, animate=True):
    """
    Poora bar chart — grid, Y-axis, glow bars, value on hover.
    Har bar neeche se upar animate hoti hai.
    """
    if not vals:
        vals = [0]
    pad_l, pad_r, pad_t, pad_b = 40, 10, 14, 24
    iw, ih = w - pad_l - pad_r, h - pad_t - pad_b
    hi = ymax if ymax is not None else max(max(vals), 1)
    hi = max(hi, 1)
    n = len(vals)
    gap = iw / n
    bw = gap * 0.66

    grid = ""
    for k in range(5):
        y = pad_t + ih * k / 4
        grid += (f'<line x1="{pad_l}" y1="{y:.1f}" x2="{w-pad_r}" y2="{y:.1f}" '
                 f'stroke="#1E293B" stroke-width="1" '
                 f'{"stroke-dasharray=3,4" if k else ""}/>'
                 f'<text x="{pad_l-6}" y="{y+3.5:.1f}" fill="#64748B" '
                 f'font-size="9.5" text-anchor="end" font-family="monospace">'
                 f'{hi*(1-k/4):.0f}</text>')

    bars = ""
    for i, v in enumerate(vals):
        bh = max(2.0, (min(v, hi) / hi) * ih)
        x = pad_l + i * gap + (gap - bw) / 2
        y = pad_t + ih - bh
        # rang value ke hisaab se
        pc = v / hi * 100
        c = "#EF4444" if pc >= 90 else ("#F59E0B" if pc >= 70 else color)
        op = 0.45 + 0.55 * (v / hi)
        anim = ""
        if animate:
            anim = (f'<animate attributeName="height" from="0" to="{bh:.1f}" '
                    f'dur="0.5s" begin="{i*0.02:.2f}s" fill="freeze"/>'
                    f'<animate attributeName="y" from="{pad_t+ih}" '
                    f'to="{y:.1f}" dur="0.5s" begin="{i*0.02:.2f}s" '
                    f'fill="freeze"/>')
        bars += (f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" '
                 f'height="{bh:.1f}" rx="2.5" fill="{c}" opacity="{op:.2f}" '
                 f'class="bgb">{anim}'
                 f'<title>{v:.1f}{unit}</title></rect>')

    # last bar highlight
    if vals:
        lv = vals[-1]
        lbh = max(2.0, (min(lv, hi) / hi) * ih)
        lx = pad_l + (n - 1) * gap + (gap - bw) / 2
        ly = pad_t + ih - lbh
        bars += (f'<rect x="{lx:.1f}" y="{ly:.1f}" width="{bw:.1f}" '
                 f'height="{lbh:.1f}" rx="2.5" fill="none" '
                 f'stroke="{color}" stroke-width="1.4" opacity=".9"/>')

    lbl = ""
    if labels:
        for i, t in enumerate(labels):
            if i % max(1, len(labels) // 6) == 0:
                lbl += (f'<text x="{pad_l+i*gap+gap/2:.1f}" y="{h-7}" '
                        f'fill="#64748B" font-size="9" text-anchor="middle" '
                        f'font-family="monospace">{t}</text>')

    return (f'<svg viewBox="0 0 {w} {h}" class="achart bargraph" '
            f'preserveAspectRatio="none">{grid}{bars}{lbl}</svg>')


def stackbars(series, w=520, h=210, sid="sb", ymax=100):
    """
    Grouped bars — CPU, RAM, DISK saath saath.
    series = [(name, [vals], color), ...]
    """
    if not series:
        return ""
    pad_l, pad_r, pad_t, pad_b = 40, 10, 14, 26
    iw, ih = w - pad_l - pad_r, h - pad_t - pad_b
    n = max(len(v) for _, v, _ in series)
    n = max(n, 1)
    k = len(series)
    gap = iw / n
    bw = (gap * 0.72) / k

    grid = ""
    for j in range(5):
        y = pad_t + ih * j / 4
        grid += (f'<line x1="{pad_l}" y1="{y:.1f}" x2="{w-pad_r}" y2="{y:.1f}" '
                 f'stroke="#1E293B" stroke-width="1" '
                 f'{"stroke-dasharray=3,4" if j else ""}/>'
                 f'<text x="{pad_l-6}" y="{y+3.5:.1f}" fill="#64748B" '
                 f'font-size="9.5" text-anchor="end" font-family="monospace">'
                 f'{ymax*(1-j/4):.0f}</text>')

    bars, legend = "", ""
    for si, (name, vals, color) in enumerate(series):
        v = list(vals) or [0]
        if len(v) < n:
            v = [v[0]] * (n - len(v)) + v
        v = v[-n:]
        for i, val in enumerate(v):
            bh = max(1.6, (min(val, ymax) / ymax) * ih)
            x = pad_l + i * gap + (gap * 0.14) + si * bw
            y = pad_t + ih - bh
            bars += (f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw*0.86:.1f}" '
                     f'height="{bh:.1f}" rx="1.8" fill="{color}" '
                     f'opacity="{0.4+0.6*(val/ymax):.2f}">'
                     f'<animate attributeName="height" from="0" to="{bh:.1f}" '
                     f'dur="0.45s" begin="{i*0.015:.2f}s" fill="freeze"/>'
                     f'<animate attributeName="y" from="{pad_t+ih}" '
                     f'to="{y:.1f}" dur="0.45s" begin="{i*0.015:.2f}s" '
                     f'fill="freeze"/>'
                     f'<title>{name}: {val:.1f}%</title></rect>')
        legend += (f'<span class="lgi"><i style="background:{color}"></i>'
                   f'{name} <b>{v[-1]:.0f}%</b></span>')

    return (f'<svg viewBox="0 0 {w} {h}" class="achart" '
            f'preserveAspectRatio="none">{grid}{bars}</svg>'
            f'<div class="lgnd">{legend}</div>')
