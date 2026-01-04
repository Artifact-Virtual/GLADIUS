#!/usr/bin/env pwsh
<#
start_tiger.ps1
Convenience launcher: ensures an SSH tunnel (localhost:5901 -> remote:5901) and starts TigerVNC viewer.
Usage (PowerShell):
  .\start_tiger.ps1                      # uses defaults from script
  .\start_tiger.ps1 -Server user@host    # custom server
  .\start_tiger.ps1 -Key C:\path\to\key -LocalPort 5901
#>

param(
  [string]$Server = 'ali_shakil_backup@34.155.169.168',
  [string]$Key = "C:\Users\noufe\.ssh\id_ed25519",
  [int]$LocalPort = 5901,
  [int]$RemotePort = 5901,
  [string]$ViewerPath = 'C:\Program Files\TigerVNC\vncviewer.exe'
)

function Test-PortListening { param($port) $r = Test-NetConnection -ComputerName localhost -Port $port -WarningAction SilentlyContinue; return [bool]$r.TcpTestSucceeded }

Write-Host "[start_tiger] Viewer: $ViewerPath | Server: $Server | Key: $Key | Port: $LocalPort"

if (-not (Test-Path $ViewerPath)) {
  Write-Warning "Viewer not found at $ViewerPath. Install TigerVNC or edit -ViewerPath to point to the correct binary.";
  exit 2
}

# If port already listening, assume tunnel exists
if (Test-PortListening -port $LocalPort) {
  Write-Host "Local port $LocalPort is already listening. Skipping tunnel creation."
} else {

  Write-Host "Starting SSH tunnel: local $LocalPort -> ${Server}:${RemotePort}"
  $sshArgs = @('-i', $Key, '-N', '-L', "$LocalPort:localhost:$RemotePort", $Server)
  try {
    Start-Process -FilePath 'ssh' -ArgumentList $sshArgs -NoNewWindow -PassThru -ErrorAction Stop | Out-Null
  } catch {
    Write-Error "Failed to start ssh tunnel: $_"; exit 3
  }
  # Wait for port to come up (simple loop)
  $tries = 0
  while (-not (Test-PortListening -port $LocalPort) -and $tries -lt 15) { Start-Sleep -Seconds 1; $tries++ }
  if (-not (Test-PortListening -port $LocalPort)) { Write-Warning "Tunnel did not appear on port $LocalPort after waiting."; exit 4 }
  Write-Host "Tunnel established on localhost:$LocalPort"
}

Write-Host "Launching TigerVNC viewer..."
Start-Process -FilePath $ViewerPath -ArgumentList "localhost:$LocalPort"
Write-Host "Viewer started. Use the VNC password when prompted. To stop the tunnel, end the ssh process (Task Manager or Get-Process ssh | Stop-Process)."
