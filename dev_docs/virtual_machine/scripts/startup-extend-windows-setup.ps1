# Combined startup script: existing Chrome/CRD install + VS Code + optional OpenSSH
# This script is intended to be used as instance metadata `windows-startup-script-ps1`.
# It runs as SYSTEM during instance startup.

$ErrorActionPreference = "Stop"
$log = "C:\Windows\Temp\startup-extend-windows-setup.log"
"Starting combined startup script at $(Get-Date)" | Out-File -FilePath $log -Encoding utf8 -Append

try {
    # Existing: Install Chrome
    $chromeUrl = "https://dl.google.com/edgedl/chrome/install/GoogleChromeStandaloneEnterprise64.msi"
    $crdUrl = "https://dl.google.com/livedownload/chromeremotedesktophost.msi"

    $chromePath = "$env:TEMP\GoogleChromeStandaloneEnterprise64.msi"
    $crdPath = "$env:TEMP\chromeremotedesktophost.msi"

    Write-Output "Downloading Chrome..." | Out-File -FilePath $log -Encoding utf8 -Append
    Invoke-WebRequest -Uri $chromeUrl -OutFile $chromePath -UseBasicParsing
    Write-Output "Installing Chrome..." | Out-File -FilePath $log -Encoding utf8 -Append
    Start-Process -FilePath "msiexec.exe" -ArgumentList "/i `"$chromePath`" /quiet /norestart" -Wait -Verb RunAs

    Write-Output "Downloading Chrome Remote Desktop..." | Out-File -FilePath $log -Encoding utf8 -Append
    Invoke-WebRequest -Uri $crdUrl -OutFile $crdPath -UseBasicParsing
    Write-Output "Installing Chrome Remote Desktop..." | Out-File -FilePath $log -Encoding utf8 -Append
    Start-Process -FilePath "msiexec.exe" -ArgumentList "/i `"$crdPath`" /quiet /norestart" -Wait -Verb RunAs

    Write-Output "Chrome + CRD installation completed" | Out-File -FilePath $log -Encoding utf8 -Append

    # New: Install VS Code silently
    $vscodeInstaller = "$env:TEMP\VSCodeSetup.exe"
    Write-Output "Downloading VS Code..." | Out-File -FilePath $log -Encoding utf8 -Append
    Invoke-WebRequest -Uri "https://update.code.visualstudio.com/latest/win32-x64/stable" -OutFile $vscodeInstaller -UseBasicParsing
    Write-Output "Installing VS Code..." | Out-File -FilePath $log -Encoding utf8 -Append
    Start-Process -FilePath $vscodeInstaller -ArgumentList '/silent','/verysilent','/norestart' -Wait
    Write-Output "VS Code install finished" | Out-File -FilePath $log -Encoding utf8 -Append

    # New: Install and enable OpenSSH Server (so Remote - SSH works), if not already present
    try {
        $ssInstalled = Get-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
        if ($ssInstalled -and $ssInstalled.State -ne 'Installed') {
            Write-Output "Installing OpenSSH Server..." | Out-File -FilePath $log -Encoding utf8 -Append
            Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0 | Out-File -FilePath $log -Encoding utf8 -Append
        }
        # Start and enable service
        if (Get-Service -Name sshd -ErrorAction SilentlyContinue) {
            Start-Service sshd -ErrorAction SilentlyContinue
            Set-Service -Name sshd -StartupType 'Automatic' -ErrorAction SilentlyContinue
        }
        # Ensure firewall rule exists
        if (-not (Get-NetFirewallRule -Name "sshd" -ErrorAction SilentlyContinue)) {
            New-NetFirewallRule -Name sshd -DisplayName 'OpenSSH' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22 | Out-File -FilePath $log -Encoding utf8 -Append
        }
        Write-Output "OpenSSH installed/configured" | Out-File -FilePath $log -Encoding utf8 -Append
    } catch {
        Write-Output "OpenSSH install error: $_" | Out-File -FilePath $log -Encoding utf8 -Append
    }

    # Create an RDP file on the default user's desktop (if possible)
    try {
        $defaultUser = (Get-LocalUser | Where-Object { $_.Name -notlike 'DefaultAccount' -and $_.Name -notlike 'WDAGUtilityAccount' -and $_.Name -ne 'SYSTEM' } | Select-Object -First 1).Name
        if ($defaultUser) {
            $profile = (Get-LocalUser -Name $defaultUser | ForEach-Object { (Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList\*") })
        }
    } catch {
        # ignore
    }
    $desktop = "$env:PUBLIC\Desktop"
    $rdpContent = @"
full address:s:localhost:3389
prompt for credentials:i:1
username:s:gladius_user
"@
    $rdpPath = Join-Path $desktop 'windows-vm-iap.rdp'
    $rdpContent | Out-File -FilePath $rdpPath -Encoding ascii
    Write-Output "Created RDP file at $rdpPath" | Out-File -FilePath $log -Encoding utf8 -Append

    Write-Output "All startup tasks completed successfully." | Out-File -FilePath $log -Encoding utf8 -Append
} catch {
    Write-Output "ERROR in startup script: $_" | Out-File -FilePath $log -Encoding utf8 -Append
}
" > /dev/null 2>&1
