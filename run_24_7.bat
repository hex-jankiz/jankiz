@echo off
REM Jankiz Telegram Bot - 24/7 Server Runner
title Jankiz Bot 24/7 Server Supervisor
cd /d "%~dp0"
echo ========================================================
echo   JANKIZ TELEGRAM BOT - 24/7 HIGH-AVAILABILITY SERVER
echo ========================================================
echo Starting self-healing supervisor...
python supervisor.py
pause
