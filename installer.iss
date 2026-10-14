#define MyAppName "Spdf"
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
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=LICENSE
OutputDir=dist\installer
OutputBaseFilename=Spdf_Setup_v1.0.0
SetupIconFile=assets\app_icon.ico
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
Source: "dist\Spdf\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\app_icon.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\app_icon.ico"; Tasks: desktopicon

[Registry]
Root: HKCR; Subkey: ".pdf\OpenWithProgids"; ValueType: string; ValueName: "Spdf.Document"; ValueData: ""; Flags: uninsdeletevalue; Tasks: associatepdf
Root: HKCR; Subkey: "Spdf.Document"; ValueType: string; ValueName: ""; ValueData: "PDF Document"; Flags: uninsdeletekey; Tasks: associatepdf
Root: HKCR; Subkey: "Spdf.Document\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\assets\app_icon.ico"; Flags: uninsdeletekey; Tasks: associatepdf
Root: HKCR; Subkey: "Spdf.Document\shell\open\command"; ValueType: string; ValueName: ""; ValueData: {app}\{#MyAppExeName} %1"; Flags: uninsdeletekey; Tasks: associatepdf

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
