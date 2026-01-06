<#
Desktop launcher helper
- Ensures MT5 terminal is running (starts it if not)
- Calls the existing launcher to start Herald in wizard mode
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Paths - adjust if your MT5 install is elsewhere
$mt5Path = 'C:\Program Files\MetaTrader 5\terminal64.exe'
$heraldLauncher = 'C:\workspace\_dev\scripts\launch_herald_global.ps1'

function Start-MT5IfMissing {
    try {
        $running = Get-Process | Where-Object { $_.Path -and ($_.Path -ieq $mt5Path) } -ErrorAction SilentlyContinue
        if ($running) {
            Write-Output "[desktop-launcher] MT5 already running (PID: $($running.Id))"
            return $true
        }
    } catch {
        # fallback: check by process name
        $runningByName = Get-Process -Name terminal64 -ErrorAction SilentlyContinue
        if ($runningByName) {
            Write-Output "[desktop-launcher] MT5 terminal process running (PID: $($runningByName.Id))"
            return $true
        }
    }

    if (-not (Test-Path $mt5Path)) {
        Write-Warning "[desktop-launcher] MT5 executable not found at $mt5Path. Skipping MT5 launch."
        return $false
    }

    try {
        Start-Process -FilePath $mt5Path -WorkingDirectory (Split-Path $mt5Path) -WindowStyle Normal
        Write-Output "[desktop-launcher] Launched MT5: $mt5Path"
        return $true
    } catch {
        Write-Warning "[desktop-launcher] Failed to start MT5: $($_.Exception.Message)"
        return $false
    }
}

# Ensure Herald launcher exists
if (-not (Test-Path $heraldLauncher)) {
    Write-Error "[desktop-launcher] Herald launcher not found: $heraldLauncher"
    exit 2
}

Start-MT5IfMissing | Out-Null

# Launch the existing launcher script (opens interactive wizard)
Start-Process -FilePath 'powershell.exe' -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File',"$heraldLauncher" -WorkingDirectory 'C:\workspace' -WindowStyle Normal

Write-Output "[desktop-launcher] Started Herald launcher (wizard)."
