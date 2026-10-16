#!/usr/bin/env bash
# Starter Poengløp i testmodus uten Brikkesys (tilsvarer Start_Poenglop_testmodus.bat).
exec "$(dirname "$(readlink -f "$0")")/start_poenglop.sh" --demo
