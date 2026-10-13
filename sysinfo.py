"""
sysinfo.py — ASLI system stats /proc se
════════════════════════════════════════
CPU, RAM, disk, network, load — sab real, sab live.
Koi library nahi, sirf /proc padhta hai.
"""

import os
import shutil
import time

_prev_cpu = None
_prev_net = None
_boot = time.time()

# history — chart ke liye (last 30 readings)
HIST = {"cpu": [], "ram": [], "net": [], "disk": []}
MAXH = 30


def _read(p):
    try:
        return open(p).read()
    except Exception:
        return ""


# ─────────────────────────────────────────────────────────
#  CPU
# ─────────────────────────────────────────────────────────

def cpu():
    """Asli CPU % — /proc/stat ke do reading ka farak."""
    global _prev_cpu
    txt = _read("/proc/stat")
    pct = 0.0
    if txt:
        for line in txt.splitlines():
            if line.startswith("cpu "):
                v = [int(x) for x in line.split()[1:11]]
                idle = v[3] + v[4]
                total = sum(v)
                if _prev_cpu:
                    dt = total - _prev_cpu[0]
                    di = idle - _prev_cpu[1]
                    if dt > 0:
                        pct = round((1 - di / dt) * 100, 1)
                _prev_cpu = (total, idle)
                break

    cores = os.cpu_count() or 1
    model = "CPU"
    mhz = 0
    ci = _read("/proc/cpuinfo")
    for line in ci.splitlines():
        low = line.lower()
        if ("model name" in low or "hardware" in low or
                "processor" in low and ":" in line and not line.split(":")[1].strip().isdigit()):
            if ":" in line:
                v = line.split(":", 1)[1].strip()
                if v and not v.isdigit():
                    model = v[:44]
                    break
    for line in ci.splitlines():
        if "cpu mhz" in line.lower() and ":" in line:
            try:
                mhz = int(float(line.split(":")[1].strip()))
            except Exception:
                pass
            break

    load = (0.0, 0.0, 0.0)
    try:
        load = os.getloadavg()
    except Exception:
        la = _read("/proc/loadavg").split()
        if len(la) >= 3:
            load = tuple(float(x) for x in la[:3])

    return {"percent": max(0.0, min(100.0, pct)), "cores": cores,
            "model": model, "mhz": mhz,
            "load1": round(load[0], 2), "load5": round(load[1], 2),
            "load15": round(load[2], 2),
            "load_pct": min(100, round(load[0] / cores * 100))}


# ─────────────────────────────────────────────────────────
#  RAM
# ─────────────────────────────────────────────────────────

def ram():
    d = {}
    for line in _read("/proc/meminfo").splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            try:
                d[k.strip()] = int(v.split()[0])
            except Exception:
                pass
    total = d.get("MemTotal", 0) / 1024
    avail = d.get("MemAvailable", d.get("MemFree", 0)) / 1024
    used = total - avail
    sw_t = d.get("SwapTotal", 0) / 1024
    sw_f = d.get("SwapFree", 0) / 1024
    return {
        "total": round(total), "used": round(used), "free": round(avail),
        "percent": round(used / total * 100, 1) if total else 0,
        "cached": round(d.get("Cached", 0) / 1024),
        "swap_total": round(sw_t), "swap_used": round(sw_t - sw_f),
        "swap_pct": round((sw_t - sw_f) / sw_t * 100) if sw_t else 0,
    }


# ─────────────────────────────────────────────────────────
#  DISK
# ─────────────────────────────────────────────────────────

def disk(path=None):
    path = path or os.path.dirname(os.path.abspath(__file__))
    try:
        t, u, f = shutil.disk_usage(path)
        return {"total": round(t / 1073741824, 1), "used": round(u / 1073741824, 1),
                "free": round(f / 1073741824, 1),
                "percent": round(u / t * 100, 1) if t else 0}
    except Exception:
        return {"total": 0, "used": 0, "free": 0, "percent": 0}


# ─────────────────────────────────────────────────────────
#  NETWORK
# ─────────────────────────────────────────────────────────

def network():
    global _prev_net
    rx = tx = 0
    for line in _read("/proc/net/dev").splitlines()[2:]:
        if ":" not in line:
            continue
        name, rest = line.split(":", 1)
        if name.strip() in ("lo",):
            continue
        p = rest.split()
        if len(p) >= 9:
            rx += int(p[0])
            tx += int(p[8])
    now = time.time()
    dn = up = 0.0
    if _prev_net:
        dt = now - _prev_net[2]
        if dt > 0:
            dn = max(0, (rx - _prev_net[0]) / dt / 1024)
            up = max(0, (tx - _prev_net[1]) / dt / 1024)
    _prev_net = (rx, tx, now)
    return {"rx_gb": round(rx / 1073741824, 2), "tx_gb": round(tx / 1073741824, 2),
            "down_kbs": round(dn, 1), "up_kbs": round(up, 1)}


# ─────────────────────────────────────────────────────────
#  UPTIME + PROCESSES
# ─────────────────────────────────────────────────────────

def uptime():
    try:
        return int(float(_read("/proc/uptime").split()[0]))
    except Exception:
        return int(time.time() - _boot)


def app_uptime():
    return int(time.time() - _boot)


def procs():
    try:
        return len([p for p in os.listdir("/proc") if p.isdigit()])
    except Exception:
        return 0


# ─────────────────────────────────────────────────────────
#  SNAPSHOT  (sab ek jagah)
# ─────────────────────────────────────────────────────────

def snapshot(push_hist=True):
    c, r, d, n = cpu(), ram(), disk(), network()

    if push_hist:
        for k, v in (("cpu", c["percent"]), ("ram", r["percent"]),
                     ("net", n["down_kbs"] + n["up_kbs"]),
                     ("disk", d["percent"])):
            HIST[k].append(v)
            if len(HIST[k]) > MAXH:
                HIST[k].pop(0)

    worst = max(c["percent"], r["percent"], d["percent"])
    if worst >= 90:
        health, hc = "CRITICAL", "err"
    elif worst >= 75:
        health, hc = "BUSY", "wait"
    else:
        health, hc = "HEALTHY", "on"

    return {"cpu": c, "ram": r, "disk": d, "net": n,
            "uptime": uptime(), "app_uptime": app_uptime(),
            "uptime_h": human_time(uptime()),
            "procs": procs(), "health": health, "hcls": hc,
            "hist": {k: list(v) for k, v in HIST.items()},
            "ts": int(time.time())}


def human_time(sec):
    sec = int(sec)
    d, sec = divmod(sec, 86400)
    h, sec = divmod(sec, 3600)
    m = sec // 60
    if d:
        return f"{d}d {h}h"
    if h:
        return f"{h}h {m}m"
    return f"{m}m"


# pehla reading — baseline ke liye
cpu()
network()
