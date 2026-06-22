#!/usr/bin/env bash
# Serve the live build board. Frees the port first, so you never hit
# "Address already in use". Usage: ./serve.sh [port]   (default 8765)
cd "$(dirname "$0")" || exit 1
PORT="${1:-8765}"
fuser -k "${PORT}/tcp" 2>/dev/null || true
# On WSL2, localhost forwarding is often broken — the LAN IP always works.
# Recompute each run (the WSL IP changes across reboots).
IP="$(hostname -I 2>/dev/null | awk '{print $1}')"
echo "Build board → http://${IP:-localhost}:${PORT}/dashboard.html   (Ctrl-C to stop)"
echo "  (if localhost works for you: http://localhost:${PORT}/dashboard.html)"
exec python3 -m http.server "${PORT}" --bind 0.0.0.0
