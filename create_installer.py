"""
Windows Installer Generator for Spdf.
Creates both:
1. Inno Setup Compiler script (installer.iss) for generating a wizard-based installer.
2. A zero-dependency Windows setup package with desktop shortcuts and uninstaller.
"""

import os
import sys

def generate_inno_setup_script():
    iss_content = """#define MyAppName "Spdf"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Spdf Contributors"
#define MyAppURL "https://github.com/test-bit-sys/Spdf"
#define MyAppExeName "Spdf.exe"

[Setup]
AppId={{D8A46C36-AB3C-4D5E-95CB-1967970950E9}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\\{#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=LICENSE
OutputDir=dist\\installer
OutputBaseFilename=Spdf_Setup_v1.0.0
SetupIconFile=assets\\app_icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "associatepdf"; Description: "Associate with .pdf files"; GroupDescription: "File Associations:"

[Files]
Source: "dist\\Spdf\\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\\{#MyAppName}"; Filename: "{app}\\{#MyAppExeName}"; IconFilename: "{app}\\assets\\app_icon.ico"
Name: "{autodesktop}\\{#MyAppName}"; Filename: "{app}\\{#MyAppExeName}"; IconFilename: "{app}\\assets\\app_icon.ico"; Tasks: desktopicon

[Registry]
Root: HKCR; Subkey: ".pdf\\OpenWithProgids"; ValueType: string; ValueName: "Spdf.Document"; ValueData: ""; Flags: uninsdeletevalue; Tasks: associatepdf
Root: HKCR; Subkey: "Spdf.Document"; ValueType: string; ValueName: ""; ValueData: "PDF Document"; Flags: uninsdeletekey; Tasks: associatepdf
Root: HKCR; Subkey: "Spdf.Document\\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\\assets\\app_icon.ico"; Flags: uninsdeletekey; Tasks: associatepdf
Root: HKCR; Subkey: "Spdf.Document\\shell\\open\\command"; ValueType: string; ValueName: ""; ValueData: """"{app}\\{#MyAppExeName}"""" """"%1"""""; Flags: uninsdeletekey; Tasks: associatepdf

[Run]
Filename: "{app}\\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
"""
    with open("installer.iss", "w", encoding="utf-8") as f:
        f.write(iss_content)
    print("Created installer.iss (Inno Setup script)")


def generate_powershell_installer():
    os.makedirs("installer", exist_ok=True)
    
    install_bat = """@echo off
setlocal
echo =====================================================
echo           Spdf PDF Suite - Windows Installer
echo =====================================================
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1"
pause
"""
    with open("installer/Install_Spdf.bat", "w", encoding="utf-8") as f:
        f.write(install_bat)

    setup_ps1 = """$appName = "Spdf"
$installDir = "$env:LOCALAPPDATA\\Programs\\$appName"
$sourceDir = (Resolve-Path "$PSScriptRoot\\..\\dist\\Spdf").Path

if (-not (Test-Path $sourceDir)) {
    $sourceDir = (Resolve-Path "$PSScriptRoot\\..").Path
}

Write-Host "Installing $appName to: $installDir..." -ForegroundColor Cyan

if (-not (Test-Path $installDir)) {
    New-Item -ItemType Directory -Path $installDir -Force | Out-Null
}

Write-Host "Copying application binaries..." -ForegroundColor Gray
Copy-Item -Path "$sourceDir\\*" -Destination $installDir -Recurse -Force

# Create Desktop Shortcut
$wsh = New-Object -ComObject WScript.Shell
$desktopPath = [Environment]::GetFolderPath("Desktop")
$shortcut = $wsh.CreateShortcut("$desktopPath\\$appName.lnk")
$shortcut.TargetPath = "$installDir\\Spdf.exe"
$shortcut.WorkingDirectory = $installDir
$shortcut.IconLocation = "$installDir\\assets\\app_icon.ico, 0"
$shortcut.Description = "Spdf - Professional PDF Editor"
$shortcut.Save()

# Create Start Menu Shortcut
$startMenuPath = [Environment]::GetFolderPath("Programs")
$shortcutSM = $wsh.CreateShortcut("$startMenuPath\\$appName.lnk")
$shortcutSM.TargetPath = "$installDir\\Spdf.exe"
$shortcutSM.WorkingDirectory = $installDir
$shortcutSM.IconLocation = "$installDir\\assets\\app_icon.ico, 0"
$shortcutSM.Description = "Spdf - Professional PDF Editor"
$shortcutSM.Save()

Write-Host "`n[SUCCESS] $appName has been successfully installed!" -ForegroundColor Green
Write-Host "Shortcuts created on Desktop and in Start Menu." -ForegroundColor Green
"""
    with open("installer/setup.ps1", "w", encoding="utf-8") as f:
        f.write(setup_ps1)

    uninstall_bat = """@echo off
setlocal
echo =====================================================
echo          Spdf PDF Suite - Windows Uninstaller
echo =====================================================
echo.
set /p confirm="Are you sure you want to uninstall Spdf? (Y/N): "
if /i not "%confirm%"=="Y" goto end

set "INSTALL_DIR=%LOCALAPPDATA%\\Programs\\Spdf"
set "DESKTOP_LNK=%USERPROFILE%\\Desktop\\Spdf.lnk"
set "START_LNK=%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Spdf.lnk"

if exist "%DESKTOP_LNK%" del /f /q "%DESKTOP_LNK%"
if exist "%START_LNK%" del /f /q "%START_LNK%"
if exist "%INSTALL_DIR%" rmdir /s /q "%INSTALL_DIR%"

echo Spdf has been successfully uninstalled.
:end
pause
"""
    with open("installer/Uninstall_Spdf.bat", "w", encoding="utf-8") as f:
        f.write(uninstall_bat)

    print("Created installer/Install_Spdf.bat and installer/Uninstall_Spdf.bat")


if __name__ == "__main__":
    generate_inno_setup_script()
    generate_powershell_installer()
    print("Installer files successfully generated!")
