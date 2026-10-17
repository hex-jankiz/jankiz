# Jankiz Telegram Bot PowerShell Launcher
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir
Write-Host "Starting Jankiz Programming News Bot..." -ForegroundColor Cyan
python bot.py
