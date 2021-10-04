#define MyAppName "DepthAI"
#define MyAppVersion "1.0"
#define MyAppPublisher "Luxonis"
#define MyAppURL "https://www.luxonis.com/"
#define MyAppExeName "DepthAI.lnk"
#define MyAppIconName "logo_only_EBl_icon.ico"

; Helper to install all files including hidden
#pragma parseroption -p-

; If the file is found by calling FindFirst without faHidden, it's not hidden
#define FileParams(FileName) \
    Local[0] = FindFirst(FileName, 0), \
    (!Local[0] ? "; Attribs: hidden" : "")

#define FileEntry(Source, DestDir) \
    "Source: \"" + Source + "\"; DestDir: \"" + DestDir + "\"" + \
    FileParams(Source) + "\n"

#define ProcessFile(Source, DestDir, FindResult, FindHandle) \
    FindResult \
        ? \
            Local[0] = FindGetFileName(FindHandle), \
            Local[1] = Source + "\\" + Local[0], \
            (Local[0] != "." && Local[0] != ".." \
                ? (DirExists(Local[1]) \
                      ? ProcessFolder(Local[1], DestDir + "\\" + Local[0]) \
                      : FileEntry(Local[1], DestDir)) \
                : "") + \
            ProcessFile(Source, DestDir, FindNext(FindHandle), FindHandle) \
        : \
            ""

#define ProcessFolder(Source, DestDir) \
    Local[0] = FindFirst(Source + "\\*", faAnyFile), \
    ProcessFile(Source, DestDir, Local[0], Local[0])

#pragma parseroption -p+


[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{6C2FE7A9-8A5C-4F45-B151-DDDC2A523590}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
; Remove the following line to run in administrative install mode (install for all users.)
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=commandline
OutputBaseFilename=DepthAI_setup
SetupIconFile=logo_only_EBl_icon.ico
UninstallDisplayIcon=logo_only_EBl_icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
; Output build location
OutputDir=build\Output

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; 

[Files]
; Source: "build\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Install 'depthai' repo (/w hidden files)
; Source: "build\depthai\*"; DestDir: "{app}\depthai"; Flags: ignoreversion recursesubdirs createallsubdirs
#emit ProcessFolder("build\depthai", "{app}\depthai")

; Install embedded Python
Source: "build\WPy64-3950\*"; DestDir: "{app}\WPy64-3950"; Flags: ignoreversion recursesubdirs createallsubdirs
; Installs venv as well (TBD)
; Source: "build\venv\*"; DestDir: "{app}\venv"; Flags: ignoreversion recursesubdirs createallsubdirs

; Install Windows specific scripts
Source: "src\create_shortcut.ps1"; DestDir: "{app}"; Flags: ignoreversion
Source: "src\prerequisite.ps1"; DestDir: "{app}"; Flags: ignoreversion

; Install launcher sources
Source: "..\{#MyAppIconName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\launcher.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\requirements.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\splash2.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\splash_screen.py"; DestDir: "{app}"; Flags: ignoreversion
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppIconName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -File ""{app}\prerequisite.ps1"""; WorkingDir: {app}; Flags: runhidden
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: shellexec postinstall skipifsilent

; Creates DepthAI shortcut in installation directory, before installing it as a Desktop Icon
[Code]
function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  ResultCode: Integer;
  Success: Boolean;
begin
  Log('Creating main shortcut');
  ExtractTemporaryFile('create_shortcut.ps1');
  ForceDirectories(ExpandConstant('{app}'));
  FileCopy(ExpandConstant('{tmp}\create_shortcut.ps1'), ExpandConstant('{app}\create_shortcut.ps1'), False);
  Exec('powershell.exe', ExpandConstant('-ExecutionPolicy Bypass -File {app}\create_shortcut.ps1'), ExpandConstant('{app}'), SW_HIDE, ewWaitUntilTerminated, ResultCode);
  
  NeedsRestart := False;
  Result := '';   
end;

[UninstallDelete]
Type: filesandordirs; Name: "{app}"