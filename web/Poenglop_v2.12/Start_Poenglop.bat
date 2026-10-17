@echo off
cd /d "%~dp0"
rem Skrivetest: sjekker om fila ble laget (ERRORLEVEL er ikke palitelig ved mislykket omdirigering)
echo.> "%~dp0_skrivetest.tmp" 2>nul
if not exist "%~dp0_skrivetest.tmp" goto :skrivebeskyttet
del "%~dp0_skrivetest.tmp"
rem Node.js 18 eller nyere trengs (fetch finnes forst i Node 18)
where node >nul 2>nul
if errorlevel 1 goto :ingennode
set NODEVER=0
for /f "tokens=1 delims=." %%v in ('node -p "process.versions.node"') do set NODEVER=%%v
if %NODEVER% LSS 18 goto :gammelnode
rem MySQL-driveren (mysql2) for direkte lesing: bruk den i API-mappen hvis den finnes, ellers installer her
set HAR_MYSQL2=
if exist node_modules\mysql2 set HAR_MYSQL2=1
for /d %%d in ("%~dp0..\Poeng*_BrikkesysAPI_v*") do if exist "%%d\node_modules\mysql2" set HAR_MYSQL2=1
if not defined HAR_MYSQL2 (
  echo   Installerer MySQL-driveren mysql2, krever internett en gang ...
  call npm install
  if errorlevel 1 echo   Fikk ikke installert mysql2 ^(krever internett og npm^). Poenglop bruker Brikkesys-API i stedet.
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
goto :eof
:ingennode
echo.
echo   Node.js er ikke installert, eller finnes ikke i PATH.
echo   Installer Node.js 18 eller nyere fra https://nodejs.org og start pa nytt.
echo.
pause
goto :eof
:gammelnode
echo.
for /f "delims=" %%v in ('node --version') do echo   Node.js %%v er for gammel. Poenglop trenger v18 eller nyere.
echo   Installer ny versjon fra https://nodejs.org og start pa nytt.
echo.
pause
