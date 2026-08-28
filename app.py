#!/usr/bin/env python3
"""
app.py — RENDER / RAILWAY KE LIYE ENTRY POINT
══════════════════════════════════════════════

Render pe aap koi command nahi chala sakte — isliye ye file
sab kuch KHUD kar leti hai:

  1. Folders bana deti hai
  2. Cloud (Upstash) se purana data restore
  3. Database ready
  4. Server start

Render me sirf itna set karna hai:
    Build Command : (khali chhod do)
    Start Command : python3 app.py

Bas. Aur kuch nahi.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ═══════════════════════════════════════════════════════
#   🔑 .env SABSE PEHLE
#
#   ⚠️ Ye kisi bhi doosre import se PEHLE chalna chahiye.
#      Kyunki db/brain/coder jaise module import hote hi
#      os.environ padh lete hain — baad me .env load karne
#      ka koi fayda nahi hota.
# ═══════════════════════════════════════════════════════
try:
    import envload
    envload.load(verbose=False)
except Exception:
    pass

# Render PORT env se deta hai
if "PORT" not in os.environ:
    os.environ["PORT"] = "10000"

print("\n" + "=" * 52)
print("  🌐 RAVAN X HOSTING — starting")
print("=" * 52)


def boot():
    # 0. .env — sirf yahi file user badalta hai
    try:
        import envload
        made, p = envload.make_template()
        if made:
            print(f"  📝 .env bana diya: {p}")
            print("     Usme DOMAIN daal kar restart karo")
        got = envload.loaded()
        if got:
            for pth, n in got:
                print(f"  🔑 .env: {n} setting padhi")
        dom = os.environ.get("DOMAIN", "").strip()
        if dom:
            print(f"  🌐 Domain : {dom}")
    except Exception as e:
        print(f"  ⚠️  .env: {str(e)[:50]}")

    # 1. folders
    base = os.path.dirname(os.path.abspath(__file__))
    for d in ("data", "data/servers", "data/storage", "data/storage/files",
              "data/storage/trash", "data/storage/tmp", "bin"):
        os.makedirs(os.path.join(base, d), exist_ok=True)
    print("  ✅ Folders ready")

    # 2. database
    import db
    db.init()
    print(f"  ✅ Database ready ({db.user_count()} users)")

    # 3. cloud restore (ephemeral platform pe zaroori)
    try:
        import cloudsync
        plat = cloudsync.platform_name()
        print(f"  ✅ Platform : {plat}")
        r = cloudsync.boot()
        src = r.get("src", "")
        if r.get("restored"):
            print(f"  ♻️  Data cloud se wapas aa gaya ({src})")
        elif r.get("ok"):
            print(f"  ☁️  Cloud backup ON ({src}) — data safe")
        else:
            print(f"  ⚠️  Cloud: {r.get('msg', '')}")
    except Exception as e:
        print(f"  ⚠️  Cloud skip: {str(e)[:60]}")

    # 3b. STORAGE ENGINE (website ke andar hi — koi alag server nahi)
    try:
        import storage
        storage.init()
        st = storage.stats()
        dk = st.get("disk", {})
        print(f"  ✅ Storage : {st['accounts']} accounts • {st['files']} files"
              f" • {st['size_h']}  (disk free: {dk.get('free_h','?')})")
    except Exception as e:
        print(f"  ⚠️  Storage skip: {str(e)[:60]}")

    # 3c. DOMAIN check
    try:
        import tunnel
        dom = tunnel.domain()
        if dom:
            print(f"  ✅ Domain  : {dom}  (tunnel off)")
        else:
            print("  ℹ️  Domain  : nahi mila — tunnel use hoga")
    except Exception:
        pass

    # 3d. AI BRAIN
    try:
        import brain
        if brain.ok():
            t = brain.selftest()
            eng = []
            if t.get("gemini"):
                eng.append("Gemini")
            if t.get("sarvam"):
                eng.append("Sarvam")
            print(f"  ✅ AI Brain : {' + '.join(eng) or 'keys hain par test fail'}"
                  f"  ({brain.budget_left()} calls bache)")
        else:
            print("  ℹ️  AI Brain : key nahi — browser wala chalega")
    except Exception as e:
        print(f"  ⚠️  AI Brain: {str(e)[:50]}")

    # 3e. CODE DOCTOR
    try:
        import coder
        cs = coder.status()
        if cs["ok"]:
            eng = []
            if cs.get("groq"):
                eng.append("Groq")
            if cs.get("nvidia"):
                eng.append("NVIDIA")
            if cs["openrouter"]:
                eng.append("OpenRouter")
            if cs["gemini"]:
                eng.append("Gemini")
            bch = ("unlimited" if cs.get("unlimited")
                   else f"{cs['left']} check bache")
            print(f"  ✅ Code Doc : {' + '.join(eng)}"
                  f"  ({cs.get('models', 0)} model · {bch})")
    except Exception as e:
        print(f"  ⚠️  Code Doc: {str(e)[:45]}")

    # 3f. AI BOSS
    try:
        import aiboss
        st = aiboss.status({"role": "admin"}, True)
        print(f"  \u2705 AI Boss  : {st['total']} model \u00b7 "
              f"{len(st['providers'])} company \u00b7 "
              f"{st['job_types']} kaam  (Pro+ plan)")
        _cf = st['providers'].get('cf', 0)
        if _cf:
            print(f"  \u2705 Cloudflare: {_cf} model \u00b7 "
                  f"10,000 neuron/din  (Workers AI)")
        import bossagent
        print("  \u2705 Agent    : file khud uthaye \u00b7 "
              "theek kare \u00b7 poochh kar deploy  (Pro+)")
    except Exception as e:
        print(f"  \u26a0\ufe0f  AI Boss: {str(e)[:45]}")

    # 3g. ⏳ FREE SERVER AUTO-EXPIRE
    #     Bina iske free server hamesha chalta rehta aur stock
    #     kabhi khali nahi hota.
    try:
        import expiry
        expiry.start()
        import unlock as _u
        print(f"  ✅ Auto-expire: free server {_u.FREE_SERVER_HOURS}h "
              f"· weekly {_u.WEEKLY_CREDITS}cr/{_u.WEEKLY_DAYS}din "
              f"· server lock {_u.SERVER_LOCK_DAYS}din")
    except Exception as e:
        print(f"  ⚠️  Auto-expire: {str(e)[:50]}")

    # 3h. 📧 EMAIL — signup OTP
    try:
        import mailer
        if mailer.ready():
            print(f"  ✅ Email    : {mailer.which()} "
                  f"· from {mailer.FROM_ADDR}")
        else:
            print("  ⚠️  Email    : koi key nahi — OTP screen pe "
                  "dikhega (signup phir bhi chalega)")
            print("     Brevo se free key lo (300/din): brevo.com")
            print("     phir Render → Environment → BREVO_API_KEY")
    except Exception as e:
        print(f"  ⚠️  Email: {str(e)[:50]}")

    # 4. shortener check
    try:
        import unlock
        ok, msg = unlock.short_test()
        print(f"  {'✅' if ok else '⚠️ '} Shortener: "
              f"{unlock.SHORTENER['domain']} — {'LIVE' if ok else msg}")
    except Exception:
        pass

    print("=" * 52 + "\n")


if __name__ == "__main__":
    try:
        boot()
    except Exception as e:
        print(f"  ⚠️  Boot warning: {e}\n")
    import server
    server.main()
