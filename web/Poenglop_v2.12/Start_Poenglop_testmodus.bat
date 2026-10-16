@echo off
cd /d "%~dp0"
echo.> "%~dp0_skrivetest.tmp" 2>nul
if errorlevel 1 goto :skrivebeskyttet
del "%~dp0_skrivetest.tmp"
node Poenglop_v2.12_server.js --demo
pause
goto :eof
:skrivebeskyttet
echo.
echo   Mappen "%~dp0" er skrivebeskyttet, typisk C:\Program Files.
echo   Flytt mappen til for eksempel C:\Poenglop og start pa nytt.
echo.
pause
