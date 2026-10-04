#!/bin/bash
# Spustí dashboard cez localhost (potrebné pre "Stiahnuť označené" + výber priečinka).
cd "$(dirname "$0")/../.." || exit 1
PORT=8077
pkill -f "http.server $PORT" 2>/dev/null
python3 -m http.server "$PORT" >/dev/null 2>&1 &
sleep 1
open "http://localhost:$PORT/dashboard.html"
echo "Dashboard beží: http://localhost:$PORT/dashboard.html"
echo "Server zastavíš: pkill -f http.server"
