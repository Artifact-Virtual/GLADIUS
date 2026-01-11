# Extended startup script: install Chrome/CRD/VSCode/OpenSSH + register CRD headless (one-shot)
# Runs as SYSTEM during instance startup. Appends a registration step that runs only once and records a marker file.

$ErrorActionPreference = "Stop"
$log = "C:\Windows\Temp\startup-extend-windows-setup-with-crd.log"
"Starting combined startup + CRD registration script at $(Get-Date)" | Out-File -FilePath $log -Encoding utf8 -Append

try {
    # Reuse existing install steps (Chrome, CRD, VS Code, OpenSSH) - assume they're idempotent
    # (This script assumes CRD is installed already. If not, the earlier startup script took care of it.)

    # Install VS Code silently (idempotent)
    try {
        $vscodeInstaller = "$env:TEMP\VSCodeSetup.exe"
        if (-not (Test-Path $vscodeInstaller)) {
            Invoke-WebRequest -Uri "https://update.code.visualstudio.com/latest/win32-x64/stable" -OutFile $vscodeInstaller -UseBasicParsing
        }
        Start-Process -FilePath $vscodeInstaller -ArgumentList '/silent','/verysilent','/norestart' -Wait
        Write-Output "VS Code install step finished" | Out-File -FilePath $log -Encoding utf8 -Append
    } catch {
        Write-Output "VS Code install error: $_" | Out-File -FilePath $log -Encoding utf8 -Append
    }

    # Ensure OpenSSH is installed and running (idempotent)
    try {
        $ssInstalled = Get-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
        if ($ssInstalled -and $ssInstalled.State -ne 'Installed') {
            Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0 | Out-File -FilePath $log -Encoding utf8 -Append
        }
        if (Get-Service -Name sshd -ErrorAction SilentlyContinue) {
            Start-Service sshd -ErrorAction SilentlyContinue
            Set-Service -Name sshd -StartupType 'Automatic' -ErrorAction SilentlyContinue
            if (-not (Get-NetFirewallRule -Name "sshd" -ErrorAction SilentlyContinue)) {
                New-NetFirewallRule -Name sshd -DisplayName 'OpenSSH' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22 | Out-File -FilePath $log -Encoding utf8 -Append
            }
        }
        Write-Output "OpenSSH configured" | Out-File -FilePath $log -Encoding utf8 -Append
    } catch {
        Write-Output "OpenSSH configuration error: $_" | Out-File -FilePath $log -Encoding utf8 -Append
    }

    # Create an RDP file on public desktop for IAP usage
    try {
        $desktop = "$env:PUBLIC\Desktop"
        $rdpContent = @"
full address:s:localhost:3389
prompt for credentials:i:1
username:s:gladius_user
"@
        $rdpPath = Join-Path $desktop 'windows-vm-iap.rdp'
        $rdpContent | Out-File -FilePath $rdpPath -Encoding ascii
        Write-Output "Created RDP file at $rdpPath" | Out-File -FilePath $log -Encoding utf8 -Append
    } catch {
        Write-Output "RDP file creation error: $_" | Out-File -FilePath $log -Encoding utf8 -Append
    }

    # --- One-shot Chrome Remote Desktop registration ---
    $regMarker = 'C:\Windows\Temp\crd_registered.txt'
    if (-not (Test-Path $regMarker)) {
        try {
            Write-Output "Attempting CRD headless registration..." | Out-File -FilePath $log -Encoding utf8 -Append
            $exe = Join-Path ${Env:PROGRAMFILES(X86)} 'Google\Chrome Remote Desktop\CurrentVersion\remoting_start_host.exe'
            $code = '4/0ASc3gC354QcUtMYMtNmB8mT9htNMm-9Ag1re8eXfOgXdXh5gW17k39Bn6co-2sO9EBEW_Q'
            $redirect = 'https://remotedesktop.google.com/_/oauthredirect'
            $name = $Env:COMPUTERNAME

            # Build a cmd string that pipes the PIN into the exe
            $pin = '9492'
            $cmd = "cmd.exe /c echo $pin | `"$exe`" --code=`"$code`" --redirect-url=`"$redirect`" --name=$name"

            Write-Output "Running: $cmd" | Out-File -FilePath $log -Encoding utf8 -Append
            # Use Invoke-Expression to run the command and capture output
            $output = Invoke-Expression $cmd 2>&1
            $output | Out-File -FilePath $log -Encoding utf8 -Append

            # Give some time for service to register and start
            Start-Sleep -Seconds 10

            # Mark success (we can't be 100% sure without querying remote status, but marker prevents re-run)
            New-Item -Path $regMarker -ItemType File -Force | Out-Null
            Write-Output "CRD registration step finished; marker created at $regMarker" | Out-File -FilePath $log -Encoding utf8 -Append
        } catch {
            Write-Output "CRD registration error: $_" | Out-File -FilePath $log -Encoding utf8 -Append
        }
    } else {
        Write-Output "CRD registration marker already present; skipping registration." | Out-File -FilePath $log -Encoding utf8 -Append
    }

    Write-Output "Startup + registration script completed." | Out-File -FilePath $log -Encoding utf8 -Append
} catch {
    Write-Output "ERROR in main script: $_" | Out-File -FilePath $log -Encoding utf8 -Append
}
