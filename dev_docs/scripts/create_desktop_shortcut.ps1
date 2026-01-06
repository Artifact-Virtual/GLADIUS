$WshShell = New-Object -ComObject WScript.Shell
$desktop = [Environment]::GetFolderPath('Desktop')
$lnkPath = Join-Path $desktop 'Launch Herald and MT5.lnk'
$shortcut = $WshShell.CreateShortcut($lnkPath)
$shortcut.TargetPath = 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'
$shortcut.Arguments = '-NoProfile -ExecutionPolicy Bypass -WindowStyle Normal -File "C:\workspace\_dev\scripts\desktop_launch_herald_and_mt5.ps1"'
$shortcut.WorkingDirectory = 'C:\workspace'
$shortcut.IconLocation = 'C:\Program Files\MetaTrader 5\terminal64.exe,0'
$shortcut.Save()
Write-Output "Created shortcut: $lnkPath"
