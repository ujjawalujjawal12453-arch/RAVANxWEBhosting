#!/usr/bin/env bash
# 🌐 RAVAN X CLOUD — sab automatic, kuch poochta nahi
cd "$(dirname "$0")" || exit 1

command -v python3 >/dev/null 2>&1 || {
    echo "📦 Python install ho raha hai..."
    if [ -d "/data/data/com.termux" ]; then pkg install -y python
    else sudo apt-get install -y python3; fi
}

# Termux: wake-lock (phone sleep me bhi chale)
if [ -d "/data/data/com.termux" ]; then
    command -v termux-wake-lock >/dev/null 2>&1 && termux-wake-lock 2>/dev/null
fi

export PORT="${PORT:-8080}"
export TUNNEL="${TUNNEL:-true}"

while true; do
    python3 app.py
    CODE=$?
    [ $CODE -eq 0 ] && { echo "👋 Band ho gaya."; break; }
    echo "⚠️  Crash (exit $CODE) — 3 sec me restart..."
    sleep 3
done
