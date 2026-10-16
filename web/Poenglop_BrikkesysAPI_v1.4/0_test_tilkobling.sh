#!/usr/bin/env bash
# Tester tilkoblingen til Brikkesys (tilsvarer 0_Test_tilkobling.bat).
# Første gang installeres mysql2, som krever internett.
cd "$(dirname "$(readlink -f "$0")")" || exit 1
if ! command -v node >/dev/null 2>&1; then echo "  Node.js er ikke installert."; exit 1; fi
if [ ! -w . ]; then echo "  Mappen $PWD er skrivebeskyttet. Flytt den til for eksempel ~/Poenglop."; exit 1; fi
[ -d node_modules/mysql2 ] || npm install --no-audit --no-fund || exit 1
node Poenglop_BrikkesysAPI_v1.4.js --test
