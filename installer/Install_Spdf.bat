@echo off
setlocal
echo =====================================================
echo           Spdf PDF Suite - Windows Installer
echo =====================================================
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1"
pause
