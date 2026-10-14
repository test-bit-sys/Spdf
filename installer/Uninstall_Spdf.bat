@echo off
setlocal
echo =====================================================
echo          Spdf PDF Suite - Windows Uninstaller
echo =====================================================
echo.
set /p confirm="Are you sure you want to uninstall Spdf? (Y/N): "
if /i not "%confirm%"=="Y" goto end

set "INSTALL_DIR=%LOCALAPPDATA%\Programs\Spdf"
set "DESKTOP_LNK=%USERPROFILE%\Desktop\Spdf.lnk"
set "START_LNK=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Spdf.lnk"

if exist "%DESKTOP_LNK%" del /f /q "%DESKTOP_LNK%"
if exist "%START_LNK%" del /f /q "%START_LNK%"
if exist "%INSTALL_DIR%" rmdir /s /q "%INSTALL_DIR%"

echo Spdf has been successfully uninstalled.
:end
pause
