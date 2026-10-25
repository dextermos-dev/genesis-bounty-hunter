@echo off
title Doomsday 24/7 VPS Miner - Dexter Rig
color 0a

echo ========================================================
echo   DOOMSDAY 24/7 MINER FOR WINDOWS VPS
echo   Account Worker: doom162df6bb0c219de72343658ec04c1d9b1939c3c5c02f6b94f
echo   Settlement Wallet: 0x8366bCe3a2D379Dec7656D7A67015789FaF999f20
echo ========================================================
echo.

:loop
echo [%date% %time%] Starting Doomsday Miner...
doomsday_miner_windows_x64.exe -worker Dexter-Windows-VPS-Rig
echo.
echo [%date% %time%] Miner stopped or network disconnected. Restarting in 5 seconds...
timeout /t 5 /nobreak >nul
goto loop
