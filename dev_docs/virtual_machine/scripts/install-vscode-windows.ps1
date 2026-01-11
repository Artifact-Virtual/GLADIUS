<#
install-vscode-windows.ps1
Installs Visual Studio Code silently, optionally enables OpenSSH Server, creates a local RDP file for IAP tunneling.
Run as Administrator (PowerShell elevated).
#>

param(
    [switch]$EnableOpenSSH # pass -EnableOpenSSH to install and configure OpenSSH
)

$log = "C:\Windows\Temp\install-vscode-windows.log"
"Starting install at $(Get-Date)" | Out-File -FilePath $log -Encoding utf8 -Append

function Ensure-Admin {
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $isAdmin) {
        Write-Error "This script must be run as Administrator."
        exit 1
    }
}

Ensure-Admin

try {
    # 1) Install VS Code
    $installer = "$env:TEMP\VSCodeSetup.exe"
    Invoke-WebRequest -Uri "https://update.code.visualstudio.com/latest/win32-x64/stable" -OutFile $installer -UseBasicParsing
    Start-Process -FilePath $installer -ArgumentList '/silent','/verysilent','/norestart' -Wait
    "VS Code installer finished at $(Get-Date)" | Out-File -FilePath $log -Encoding utf8 -Append

    # 2) Optional: Install and enable OpenSSH Server
    if ($EnableOpenSSH) {
        Write-Output "Installing OpenSSH Server..." | Out-File -FilePath $log -Encoding utf8 -Append
        Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0 | Out-File -FilePath $log -Encoding utf8 -Append
        Start-Service sshd
        Set-Service -Name sshd -StartupType 'Automatic'
        # Allow through firewall
        if (-not (Get-NetFirewallRule -Name "sshd" -ErrorAction SilentlyContinue)) {
            New-NetFirewallRule -Name sshd -DisplayName 'OpenSSH' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22 | Out-File -FilePath $log -Encoding utf8 -Append
        }
        "OpenSSH installed and configured" | Out-File -FilePath $log -Encoding utf8 -Append
    }

    # 3) Create a convenient RDP file pointing to localhost:3389 (for IAP tunnel usage)
    $rdpContent = @"
full address:s:localhost:3389
prompt for credentials:i:1
username:s:gladius_user
"@
    $desktop = [Environment]::GetFolderPath('Desktop')
    $rdpPath = Join-Path $desktop 'windows-vm-iap.rdp'
    $rdpContent | Out-File -FilePath $rdpPath -Encoding ascii
    "Created RDP file at $rdpPath" | Out-File -FilePath $log -Encoding utf8 -Append

    Write-Output "Install completed successfully. Check $log for details." | Out-File -FilePath $log -Encoding utf8 -Append
    Write-Host "Install completed. RDP file created on Desktop: $rdpPath"
} catch {
    "ERROR: $_" | Out-File -FilePath $log -Encoding utf8 -Append
    Write-Error "An error occurred. See $log for details."
    exit 1
}
