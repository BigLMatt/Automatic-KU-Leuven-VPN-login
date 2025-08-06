[Setup]
AppName=VPN KUL Connector
AppVersion=1.0
DefaultDirName={localappdata}\VPN_KUL_Connector
DisableProgramGroupPage=yes
OutputDir=C:\Users\Matteo\Desktop\installer
OutputBaseFilename=VPN_KUL_Installer_v1.0
Compression=lzma
SolidCompression=yes

[Files]
Source: "C:\Users\Matteo\Desktop\package\vpn_kul.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\Matteo\Desktop\package\vpn_kul_settings.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\Matteo\Desktop\package\programicon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Tasks]
Name: "desktopicon_connector"; Description: "Desktop shortcut for VPN KUL Connector"; GroupDescription: "Desktop shortcuts:"; Flags: unchecked
Name: "desktopicon_settings"; Description: "Desktop shortcut for VPN KUL Settings"; GroupDescription: "Desktop shortcuts:"; Flags: unchecked
Name: "startsettings"; Description: "Start settings after installation"; Flags: unchecked

[Icons]
Name: "{userdesktop}\VPN KUL"; Filename: "{app}\vpn_kul.exe"; WorkingDir: "{app}"; IconFilename: "{app}\programicon.ico"; Tasks: desktopicon_connector
Name: "{userdesktop}\VPN Settings"; Filename: "{app}\vpn_kul_settings.exe"; WorkingDir: "{app}"; IconFilename: "{app}\programicon.ico"; Tasks: desktopicon_settings

[Run]
Filename: "{app}\vpn_kul_settings.exe"; Description: "Start settings after installation"; Flags: nowait postinstall skipifsilent; Tasks: startsettings