@echo off
cd /d "%~dp0"
echo.> "%~dp0_skrivetest.tmp" 2>nul
if errorlevel 1 goto :skrivebeskyttet
del "%~dp0_skrivetest.tmp"
if not exist node_modules\mysql2 call npm install
start "" http://127.0.0.1:8091
node Poenglop_BrikkesysAPI_v1.4.js
pause
goto :eof
:skrivebeskyttet
echo.
echo   Mappen "%~dp0" er skrivebeskyttet, typisk C:\Program Files.
echo   Flytt mappen til for eksempel C:\Poenglop og start pa nytt.
echo.
pause
