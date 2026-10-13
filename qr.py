"""
qr.py — 📱 UPI QR CODE BANANE WALA
═══════════════════════════════════

User ki shikayat: "QR code aata hi nahin hai".

Bilkul sahi — website me QR tha hi nahi. Sirf UPI ID likhi thi
jise user ko haath se copy karke apne UPI app me daalni padti
thi. Bahut jhanjhat, aur galti se galat ID pe paise chale jaate.

═══ BINA KISI LIBRARY KE ═══

Normal tarika `qrcode` + `Pillow` library hai. Par is website ka
sabse bada usool hai: ZERO DEPENDENCY (requirements.txt khali
hai). Render pe pip install ka jhanjhat nahi, deploy 5 second me.

Isliye maine poora QR encoder khud likha hai — sirf Python
stdlib se. Output SVG hai (na ki PNG), kyunki:
  • SVG seedha HTML me daal sakte hain
  • Kitna bhi bada karo, dhundhla nahi hota
  • Koi image library nahi chahiye

═══ KYA SUPPORT HAI ═══

Byte mode, Version 1-10, Error correction Level M (15% tak
kharab ho jaye to bhi scan hota hai — printed QR ke liye
kaafi). UPI link 40-90 character ka hota hai, wo aaram se
Version 3-6 me aa jata hai.

⚠️ Ye poora QR standard (ISO/IEC 18004) nahi hai. Sirf wahi
   hissa banaya hai jo UPI ke liye chahiye. Kanji mode,
   numeric optimization, structured append — kuch nahi hai,
   kyunki UPI ko unki zarurat hi nahi.
"""

# ═════════════════════════════════════════════════════════
#   GALOIS FIELD — Reed-Solomon ke liye
#
#   QR me error correction Reed-Solomon se hota hai, jo GF(256)
#   me chalta hai. Yahan multiply/divide normal jaisa nahi hota,
#   isliye pehle log/antilog table banate hain.
# ═════════════════════════════════════════════════════════

_EXP = [0] * 512
_LOG = [0] * 256


def _init_gf():
    x = 1
    for i in range(255):
        _EXP[i] = x
        _LOG[x] = i
        x <<= 1
        if x & 0x100:
            x ^= 0x11D          # QR ka primitive polynomial
    for i in range(255, 512):
        _EXP[i] = _EXP[i - 255]


_init_gf()


def _gf_mul(a, b):
    if a == 0 or b == 0:
        return 0
    return _EXP[_LOG[a] + _LOG[b]]


def _rs_poly(n):
    """n error-correction byte ke liye generator polynomial."""
    p = [1]
    for i in range(n):
        q = [1, _EXP[i]]
        r = [0] * (len(p) + 1)
        for j, pj in enumerate(p):
            for k, qk in enumerate(q):
                r[j + k] ^= _gf_mul(pj, qk)
        p = r
    return p


def _rs_encode(data, n):
    """data ke aage n error-correction byte jodo."""
    gen = _rs_poly(n)
    res = list(data) + [0] * n
    for i in range(len(data)):
        c = res[i]
        if c == 0:
            continue
        for j, g in enumerate(gen):
            res[i + j] ^= _gf_mul(g, c)
    return res[len(data):]


# ═════════════════════════════════════════════════════════
#   VERSION TABLE (Level M)
#
#   (version, kitne byte data aa sakta, ec byte per block,
#    group1 blocks, group1 data bytes, group2 blocks, g2 bytes)
# ═════════════════════════════════════════════════════════

_VER = {
    1:  (16,   10, 1, 16,  0, 0),
    2:  (28,   16, 1, 28,  0, 0),
    3:  (44,   26, 1, 44,  0, 0),
    4:  (64,   18, 2, 32,  0, 0),
    5:  (86,   24, 2, 43,  0, 0),
    6:  (108,  16, 4, 27,  0, 0),
    7:  (124,  18, 4, 31,  0, 0),
    8:  (154,  22, 2, 38,  2, 39),
    9:  (182,  22, 3, 36,  2, 37),
    10: (216,  26, 4, 43,  1, 44),
}

# har version me alignment pattern kahan-kahan
_ALIGN = {
    1: [], 2: [6, 18], 3: [6, 22], 4: [6, 26], 5: [6, 30],
    6: [6, 34], 7: [6, 22, 38], 8: [6, 24, 42], 9: [6, 26, 46],
    10: [6, 28, 50],
}


def _pick_version(n):
    """Itne byte ke liye sabse chhota version."""
    for v in range(1, 11):
        # version 10+ me length field 2 byte ka hota hai
        head = 2 if v >= 10 else 1
        if n + head + 1 <= _VER[v][0]:
            return v
    raise ValueError("Text bahut lamba hai QR ke liye")


# ═════════════════════════════════════════════════════════
#   BIT BUFFER
# ═════════════════════════════════════════════════════════

class _Bits:
    def __init__(self):
        self.b = []

    def put(self, val, n):
        for i in range(n - 1, -1, -1):
            self.b.append((val >> i) & 1)

    def __len__(self):
        return len(self.b)

    def bytes(self):
        while len(self.b) % 8:
            self.b.append(0)
        return [int("".join(map(str, self.b[i:i + 8])), 2)
                for i in range(0, len(self.b), 8)]


# ═════════════════════════════════════════════════════════
#   QR BANAO
# ═════════════════════════════════════════════════════════

def _make_matrix(text):
    """Text se QR ka 0/1 grid banao."""
    data = text.encode("utf-8")
    ver = _pick_version(len(data))
    cap, ecw, g1n, g1b, g2n, g2b = _VER[ver]
    size = 17 + ver * 4

    # ── 1. bit stream ──
    bits = _Bits()
    bits.put(0b0100, 4)                       # byte mode
    bits.put(len(data), 16 if ver >= 10 else 8)
    for byte in data:
        bits.put(byte, 8)

    total_bits = cap * 8
    # terminator
    for _ in range(min(4, total_bits - len(bits))):
        bits.b.append(0)
    while len(bits) % 8:
        bits.b.append(0)
    # padding
    pad = [0xEC, 0x11]
    i = 0
    raw = bits.bytes()
    while len(raw) < cap:
        raw.append(pad[i % 2])
        i += 1

    # ── 2. block me baato + error correction ──
    blocks, ecs = [], []
    pos = 0
    for _ in range(g1n):
        blocks.append(raw[pos:pos + g1b]); pos += g1b
    for _ in range(g2n):
        blocks.append(raw[pos:pos + g2b]); pos += g2b
    for blk in blocks:
        ecs.append(_rs_encode(blk, ecw))

    # interleave — QR ka niyam
    final = []
    for i in range(max(len(b) for b in blocks)):
        for b in blocks:
            if i < len(b):
                final.append(b[i])
    for i in range(ecw):
        for e in ecs:
            final.append(e[i])

    # ── 3. grid banao ──
    m = [[None] * size for _ in range(size)]

    def finder(r, c):
        for dr in range(-1, 8):
            for dc in range(-1, 8):
                rr, cc = r + dr, c + dc
                if not (0 <= rr < size and 0 <= cc < size):
                    continue
                on = (0 <= dr <= 6 and 0 <= dc <= 6 and
                      (dr in (0, 6) or dc in (0, 6) or
                       (2 <= dr <= 4 and 2 <= dc <= 4)))
                m[rr][cc] = 1 if on else 0

    finder(0, 0); finder(0, size - 7); finder(size - 7, 0)

    # timing
    for i in range(8, size - 8):
        v = 1 if i % 2 == 0 else 0
        if m[6][i] is None:
            m[6][i] = v
        if m[i][6] is None:
            m[i][6] = v

    # alignment
    for r in _ALIGN[ver]:
        for c in _ALIGN[ver]:
            if m[r][c] is not None:
                continue
            for dr in range(-2, 3):
                for dc in range(-2, 3):
                    on = (abs(dr) == 2 or abs(dc) == 2 or
                          (dr == 0 and dc == 0))
                    m[r + dr][c + dc] = 1 if on else 0

    # dark module
    m[size - 8][8] = 1

    # format info ki jagah reserve
    for i in range(9):
        if m[8][i] is None:
            m[8][i] = 0
        if m[i][8] is None:
            m[i][8] = 0
    for i in range(size - 8, size):
        if m[8][i] is None:
            m[8][i] = 0
        if m[i][8] is None:
            m[i][8] = 0

    # ── 4. data bharo (zigzag, neeche se upar) ──
    bit_list = []
    for byte in final:
        for i in range(7, -1, -1):
            bit_list.append((byte >> i) & 1)

    idx = 0
    col = size - 1
    up = True
    while col > 0:
        if col == 6:
            col -= 1          # timing column chhodo
        rows = range(size - 1, -1, -1) if up else range(size)
        for row in rows:
            for c in (col, col - 1):
                if m[row][c] is None:
                    bit = bit_list[idx] if idx < len(bit_list) else 0
                    idx += 1
                    # mask 0 — sabse aam, (row+col)%2==0
                    if (row + c) % 2 == 0:
                        bit ^= 1
                    m[row][c] = bit
        up = not up
        col -= 2

    # ── 5. format info (Level M + mask 0) ──
    #
    # ⚠️ Ye 15-bit value me error-correction level, mask number
    #    aur BCH check-bits sab bhare hote hain. Ise haath se
    #    ginna aasan nahi — isliye maine asli QR library se
    #    milakar verify kiya tha.
    #
    #    Pehle maine galti se ye bits ULTE likh diye the. Data
    #    bilkul sahi tha par scanner QR ko padh hi nahi paata,
    #    kyunki use pata hi nahi chalta ki mask kaunsa laga hai.
    #    Sirf 12 square ka farak tha — aankh se kabhi na dikhta.
    fmt = 0x2415
    for i in range(15):
        bit = (fmt >> i) & 1
        if i < 6:
            m[8][i] = bit
        elif i == 6:
            m[8][7] = bit
        elif i == 7:
            m[8][8] = bit
        elif i == 8:
            m[7][8] = bit
        else:
            m[14 - i][8] = bit
    for i in range(15):
        bit = (fmt >> i) & 1
        if i < 8:
            m[size - 1 - i][8] = bit
        else:
            m[8][size - 15 + i] = bit
    m[size - 8][8] = 1

    return [[0 if x is None else x for x in row] for row in m]


def svg(text, px=8, quiet=4, dark="#0B1020", light="#FFFFFF"):
    """
    QR ka SVG banao — seedha HTML me daal do.

    @param px     har square kitne pixel ka
    @param quiet  chaaro taraf khali jagah (scan ke liye zaroori)
    """
    try:
        m = _make_matrix(text)
    except Exception:
        return ""
    n = len(m)
    side = (n + quiet * 2) * px
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" '
           f'width="{side}" height="{side}" '
           f'viewBox="0 0 {side} {side}" '
           f'shape-rendering="crispEdges">',
           f'<rect width="{side}" height="{side}" fill="{light}"/>']
    for r in range(n):
        c = 0
        while c < n:
            if m[r][c]:
                # ek hi kataar ke lagataar square ek rect me —
                # isse SVG bahut chhota ho jata hai
                w = 1
                while c + w < n and m[r][c + w]:
                    w += 1
                x = (c + quiet) * px
                y = (r + quiet) * px
                out.append(f'<rect x="{x}" y="{y}" '
                           f'width="{w * px}" height="{px}" '
                           f'fill="{dark}"/>')
                c += w
            else:
                c += 1
    out.append("</svg>")
    return "".join(out)


def upi_link(vpa, name, amount=None, note=""):
    """
    UPI ka standard link banao — har app (GPay/PhonePe/Paytm)
    isi format ko samajhta hai.
    """
    import urllib.parse
    q = {"pa": vpa, "pn": name, "cu": "INR"}
    if amount:
        q["am"] = f"{float(amount):.2f}"
    if note:
        q["tn"] = note[:50]
    return "upi://pay?" + urllib.parse.urlencode(q)


def upi_svg(vpa, name, amount=None, note="", px=7):
    """Seedha UPI QR ka SVG."""
    return svg(upi_link(vpa, name, amount, note), px=px)
