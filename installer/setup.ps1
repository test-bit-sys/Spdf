$appName = "Spdf"
$installDir = "$env:LOCALAPPDATA\Programs\$appName"
$sourceDir = (Resolve-Path "$PSScriptRoot\..\dist\Spdf").Path

if (-not (Test-Path $sourceDir)) {
    $sourceDir = (Resolve-Path "$PSScriptRoot\..").Path
}

Write-Host "Installing $appName to: $installDir..." -ForegroundColor Cyan

if (-not (Test-Path $installDir)) {
    New-Item -ItemType Directory -Path $installDir -Force | Out-Null
}

Write-Host "Copying application binaries..." -ForegroundColor Gray
Copy-Item -Path "$sourceDir\*" -Destination $installDir -Recurse -Force

# Create Desktop Shortcut
$wsh = New-Object -ComObject WScript.Shell
$desktopPath = [Environment]::GetFolderPath("Desktop")
$shortcut = $wsh.CreateShortcut("$desktopPath\$appName.lnk")
$shortcut.TargetPath = "$installDir\Spdf.exe"
$shortcut.WorkingDirectory = $installDir
$shortcut.IconLocation = "$installDir\assets\app_icon.ico, 0"
$shortcut.Description = "Spdf - Professional PDF Editor"
$shortcut.Save()

# Create Start Menu Shortcut
$startMenuPath = [Environment]::GetFolderPath("Programs")
$shortcutSM = $wsh.CreateShortcut("$startMenuPath\$appName.lnk")
$shortcutSM.TargetPath = "$installDir\Spdf.exe"
$shortcutSM.WorkingDirectory = $installDir
$shortcutSM.IconLocation = "$installDir\assets\app_icon.ico, 0"
$shortcutSM.Description = "Spdf - Professional PDF Editor"
$shortcutSM.Save()

Write-Host "`n[SUCCESS] $appName has been successfully installed!" -ForegroundColor Green
Write-Host "Shortcuts created on Desktop and in Start Menu." -ForegroundColor Green
