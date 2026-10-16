#!/usr/bin/env bash
# Starter Brikkesys-API med nettleservisning på http://127.0.0.1:8091 (tilsvarer 1_Start_Brikkesys-API.bat).
cd "$(dirname "$(readlink -f "$0")")" || exit 1
URL=http://127.0.0.1:8091
if ! command -v node >/dev/null 2>&1; then echo "  Node.js er ikke installert."; exit 1; fi
if [ ! -w . ]; then echo "  Mappen $PWD er skrivebeskyttet. Flytt den til for eksempel ~/Poenglop."; exit 1; fi
[ -d node_modules/mysql2 ] || npm install --no-audit --no-fund || exit 1
if command -v xdg-open >/dev/null 2>&1 && [ -n "${DISPLAY:-}${WAYLAND_DISPLAY:-}" ]; then
  ( sleep 2; xdg-open "$URL" >/dev/null 2>&1 ) &
fi
exec node Poenglop_BrikkesysAPI_v1.4.js
