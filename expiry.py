"""
expiry.py — ⏳ FREE SERVER APNE AAP BAND
════════════════════════════════════════

Malik ka niyam:
  • Free server sirf 24 ghante chalta hai
  • Waqt poora = server band + files delete + slot wapas

⚠️ Ye background me chalta hai, har 2 minute me check karta
   hai. Bina iske server hamesha chalta rehta aur free stock
   kabhi khali nahi hota.

Expire hone par kya-kya hota hai:
  1. Server ROK diya jata hai (process kill)
  2. Log me saaf likha jata hai — user ko pata chale
  3. Files delete (disk khali)
  4. DB se entry hat jati hai
  5. Free stock me slot wapas
"""

import os
import shutil
import threading
import time

CHECK_EVERY = int(os.environ.get("EXPIRY_CHECK_SEC", "120"))
_started = False


def _kill(uid, sid):
    """Server ka process band karo"""
    try:
        import engine
        engine.stop(uid, sid)
    except Exception:
        pass


def _wipe(uid, sid):
    """Files hata do — disk khali karo"""
    try:
        import engine
        d = engine.server_dir(uid, sid)
        if d and os.path.isdir(d):
            shutil.rmtree(d, ignore_errors=True)
    except Exception:
        pass


def sweep():
    """
    Ek baar poora check.
    Return: kitne server band kiye
    """
    try:
        import db
    except Exception:
        return 0
    try:
        gone = db.expired_apps()
    except Exception:
        return 0
    if not gone:
        return 0

    n = 0
    for a in gone:
        sid = a.get("id")
        uid = a.get("user_id")
        nm = a.get("name", "?")
        try:
            # 1. saaf-saaf log — user ko dikhe kyun band hua
            try:
                import engine
                engine.log(sid, "━" * 40, "warn")
                engine.log(sid, "⏳ 24 GHANTE POORE HO GAYE", "warn")
                engine.log(sid, f"🛑 {nm} band kar diya gaya", "err")
                engine.log(sid, "Free server sirf 24 ghante ka hota "
                                "hai — ye pehle hi bataya gaya tha.",
                           "warn")
                engine.log(sid, "💳 Chalu rakhna hai? /recharge se "
                                "credit daalo", "ok")
                engine.log(sid, "━" * 40, "warn")
            except Exception:
                pass

            _kill(uid, sid)
            _wipe(uid, sid)
            db.delete_app(sid)

            # 2. free stock wapas — doosre ko mauka mile
            try:
                import unlock
                st = unlock._load()
                if str(uid) in st.get("claimed", []):
                    st["claimed"].remove(str(uid))
                    unlock._save()
            except Exception:
                pass

            n += 1
            print(f"  ⏳ Free server expire: #{sid} {nm} (user {uid})")
        except Exception as e:
            print(f"  ⚠️  expire fail #{sid}: {str(e)[:60]}")
    return n


def _loop():
    # boot ke turant baad ek baar — restart me chhoote hue pakdo
    time.sleep(20)
    while True:
        try:
            sweep()
        except Exception:
            pass
        time.sleep(CHECK_EVERY)


def start():
    """Background me chalu karo — ek hi baar"""
    global _started
    if _started:
        return False
    _started = True
    threading.Thread(target=_loop, daemon=True,
                     name="expiry-sweeper").start()
    return True
