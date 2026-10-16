#!/usr/bin/env bash
# Starter Poengløp på Ubuntu/Linux (tilsvarer Start_Poenglop.bat).
#   ./start_poenglop.sh          Brikkesys direkte eller via API
#   ./start_poenglop.sh --demo   testmodus, ingen database
cd "$(dirname "$(readlink -f "$0")")" || exit 1
URL=http://127.0.0.1:8090
DEMO=""
[ "${1:-}" = "--demo" ] && DEMO="--demo"

if ! command -v node >/dev/null 2>&1; then
  echo "  Node.js er ikke installert. Se Poenglop_v2.12_INSTALLASJON_UBUNTU.txt, steg 1."
  exit 1
fi
if [ "$(node -p 'process.versions.node.split(".")[0]')" -lt 18 ]; then
  echo "  Node.js $(node --version) er for gammel. Poengløp trenger v18 eller nyere."
  echo "  Se Poenglop_v2.12_INSTALLASJON_UBUNTU.txt, steg 1."
  exit 1
fi
if [ ! -w . ]; then
  echo "  Mappen $PWD er skrivebeskyttet. Flytt den til for eksempel ~/Poenglop og start på nytt."
  exit 1
fi

# MySQL-driveren (mysql2) for direkte lesing: bruk den i API-mappen hvis den finnes, ellers installer her
if [ -z "$DEMO" ]; then
  HAR_MYSQL2=""
  [ -d node_modules/mysql2 ] && HAR_MYSQL2=1
  for d in ../Poeng*_BrikkesysAPI_v*/node_modules/mysql2; do [ -d "$d" ] && HAR_MYSQL2=1; done
  if [ -z "$HAR_MYSQL2" ]; then
    echo "  Installerer MySQL-driveren mysql2, krever internett en gang ..."
    if ! npm install --no-audit --no-fund; then
      echo "  Fikk ikke installert mysql2. Poengløp bruker Brikkesys-API i stedet."
    fi
  fi
fi

# Poengløp åpner bare nettleseren selv på Windows
if command -v xdg-open >/dev/null 2>&1 && [ -n "${DISPLAY:-}${WAYLAND_DISPLAY:-}" ]; then
  ( sleep 2; xdg-open "$URL" >/dev/null 2>&1 ) &
else
  echo "  Åpne $URL i nettleseren."
fi
exec node Poenglop_v2.12_server.js $DEMO
