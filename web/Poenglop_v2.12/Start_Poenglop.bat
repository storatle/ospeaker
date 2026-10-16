@echo off
cd /d "%~dp0"
echo.> "%~dp0_skrivetest.tmp" 2>nul
if errorlevel 1 goto :skrivebeskyttet
del "%~dp0_skrivetest.tmp"
rem MySQL-driveren (mysql2) for direkte lesing: bruk den i API-mappen hvis den finnes, ellers installer her
set HAR_MYSQL2=
if exist node_modules\mysql2 set HAR_MYSQL2=1
for /d %%d in ("%~dp0..\Poeng*_BrikkesysAPI_v*") do if exist "%%d\node_modules\mysql2" set HAR_MYSQL2=1
if not defined HAR_MYSQL2 (
  echo   Installerer MySQL-driveren mysql2, krever internett en gang ...
  call npm install
  if errorlevel 1 echo   Fikk ikke installert mysql2. Poenglop bruker Brikkesys-API i stedet.
)
node Poenglop_v2.12_server.js
pause
goto :eof
:skrivebeskyttet
echo.
echo   Mappen "%~dp0" er skrivebeskyttet, typisk C:\Program Files.
echo   Flytt mappen til for eksempel C:\Poenglop og start pa nytt.
echo.
pause
