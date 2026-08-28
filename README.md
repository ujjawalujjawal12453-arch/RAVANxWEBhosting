# 🌐 RAVAN X CLOUD

## 🔐 ADMIN PASSWORD
```
ravanx2026
```

## ⚡ TERMUX — bas ek line
```bash
python3 ~/storage/downloads/ravanx-website.py
```
Kuch nahi poochega. Install → cloud restore → server start, sab khud.
Kholo: `http://localhost:8080`

Baad me: `cd ~/ravanx-web && bash start.sh`

## ☁️ CLOUD BACKUP — pehle se laga hai
Upstash creds **built-in** hain. Kuch set nahi karna.

- Har 60 sec — database cloud pe
- Har 5 min — server files cloud pe
- Boot pe — cloud se wapas

**Data kabhi nahi jayega** — Render restart ho, phone format ho, kuch bhi.

Apna cloud chahiye to env me `UPSTASH_REDIS_REST_URL` + `_TOKEN`.

## 🚀 RENDER — 3 step
1. Code GitHub pe
2. Render → **New → Web Service** → repo
3. **Create**

Bas. `render.yaml` me sab bhara hai — admin pass, EarnLinks API,
Upstash creds. Build command khali, start `python3 app.py`.

**Railway:** New Project → repo → done

## 🌐 TUNNEL (localhost ke liye)
Default **ON**. Cloudflare khud download hoke chalta hai.

URL badle to:
- Naya URL save
- Pending links dobara bante hain
- **Purane URL wale apne aap naye pe** (301)
- Tunnel gire to 15 sec me restart

## 🔗 EarnLinks (LIVE ✅)
`earnlinks.in` — API key laga hua hai.

## 🎁 Free Server
Stock → GENERATE → EarnLinks → token → server

**Anti-cheat:** fake token · generate skip · shortener skip ·
doosre ka token · dobara · fake signature → **BLACKLIST**

## 📊 Live System
Animated bar graphs, har 2 sec, sab `/proc` se asli.

## ⚙️ Env (sab optional)
| Var | Default |
|---|---|
| `ADMIN_PASS` | ravanx2026 |
| `FREE_STOCK` | 50 |
| `TUNNEL` | true |
| `UPSTASH_*` | built-in |

---
Made by **Ujjawal X Official** · @UjjawalXsarkar
