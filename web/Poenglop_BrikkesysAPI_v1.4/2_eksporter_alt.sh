#!/usr/bin/env bash
# Eksporterer alle tabeller og struktur.md til mappen eksport (tilsvarer 2_Eksporter_alt.bat).
# Eksporten inneholder personopplysninger. Slett den etter bruk.
cd "$(dirname "$(readlink -f "$0")")" || exit 1
if ! command -v node >/dev/null 2>&1; then echo "  Node.js er ikke installert."; exit 1; fi
if [ ! -w . ]; then echo "  Mappen $PWD er skrivebeskyttet. Flytt den til for eksempel ~/Poenglop."; exit 1; fi
[ -d node_modules/mysql2 ] || npm install --no-audit --no-fund || exit 1
node Poenglop_BrikkesysAPI_v1.4.js --eksport || exit 1
if command -v xdg-open >/dev/null 2>&1 && [ -n "${DISPLAY:-}${WAYLAND_DISPLAY:-}" ]; then
  xdg-open eksport >/dev/null 2>&1 &
fi
