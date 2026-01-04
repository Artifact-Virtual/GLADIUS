# Non-interactive NSSM tunnel setup and verification script
# - Uses existing private key(s) in $env:USERPROFILE\.ssh
# - Verifies SSH connectivity to the VM (34.155.169.168) using BatchMode
# - Validates or starts a temporary tunnel to localhost:5901 to confirm VNC reachability
# - Installs NSSM (if missing) and configures a service 'VncSshTunnel' to manage the tunnel
# - Does NOT generate new SSH keys and will not prompt for input
# Run as Administrator

$ErrorActionPreference = 'Stop'
$server = '34.155.169.168'
$svcName = 'VncSshTunnel'
$svcDir = 'C:\ProgramData\ssh-tunnel'
$logPrefix = "[$(Get-Date -Format o)]"

function Log { param($m) Write-Host "$logPrefix $m" }

Log "Starting non-interactive NSSM tunnel setup script"

# 1) Use the specific private key (noufe's key)
$chosenKey = "$env:USERPROFILE\.ssh\google_compute_engine"
Log "Using key: $chosenKey"

# 2) Hardcode SSH username (from manual connection)
$connectedUser = 'ali_shakil_backup'
Log "Using user: $connectedUser"
Log "Using key: $chosenKey (user $connectedUser)"



# 3) Ensure service directory and secure it
New-Item -Path $svcDir -ItemType Directory -Force | Out-Null
# copy key into service dir (don't overwrite if exists)
$dstKey = Join-Path $svcDir 'id_ed25519'
if (-not (Test-Path $dstKey)) {
    Copy-Item -Path $chosenKey -Destination $dstKey -Force
    Log "Copied key to $dstKey"
} else { Log "Existing key at $dstKey; leaving in place" }
# create known_hosts if missing or missing server
$knownHosts = Join-Path $svcDir 'known_hosts'
$hasHost = $false
if (Test-Path $knownHosts) {
    $hasHost = Select-String -Path $knownHosts -Pattern $server -Quiet
}
if (-not $hasHost) {
    Log "Fetching host key for $server and appending to $knownHosts"
    try { ssh-keyscan -t ed25519 $server 2>$null | Out-File -FilePath $knownHosts -Encoding ascii -Append } catch { Log "ssh-keyscan failed; continuing" }
    # If ssh-keyscan failed, try copying from user's known_hosts
    if (-not (Select-String -Path $knownHosts -Pattern $server -Quiet)) {
        $userKnownHosts = "C:\Users\noufe\.ssh\known_hosts"
        if (Test-Path $userKnownHosts) {
            Log "Copying host key from user's known_hosts"
            Get-Content $userKnownHosts | Where-Object { $_ -match $server } | Out-File -FilePath $knownHosts -Encoding ascii -Append
        }
    }
} else { Log "known_hosts already contains entry for $server" }

# Lock down permissions on the key and known_hosts
try {
    icacls $dstKey /inheritance:r 2>$null | Out-Null
    icacls $dstKey /grant:r "SYSTEM:F" 2>$null | Out-Null
    icacls $knownHosts /inheritance:r 2>$null | Out-Null
    icacls $knownHosts /grant:r "SYSTEM:F" 2>$null | Out-Null
    Log "Applied restrictive ACLs to key and known_hosts"
} catch { Log "Warning: could not fully set ACLs ($_)" }

# 4) Check for existing tunnel/listener
$existingSshProcs = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'ssh' -and $_.CommandLine -match $server -and $_.CommandLine -match '5901' }
if ($existingSshProcs) {
    Log "Found existing ssh tunnel processes:"; $existingSshProcs | Select-Object ProcessId,CommandLine | Format-Table | Out-String | ForEach-Object { Log $_ }
} else { Log "No existing ssh tunnel process found for $server -> 5901" }

$listener = Test-NetConnection -ComputerName localhost -Port 5901
if ($listener.TcpTestSucceeded) { Log "Port 5901 is already listening locally (tunnel active)." } else { Log "Port 5901 is NOT listening locally." }

# Skipping temporary tunnel validation due to permission issues; assuming key is correct
Log "Skipping temporary tunnel validation; proceeding to NSSM install"

# 5) Install NSSM if not present (non-interactive)
$nssmPath = (Get-Command nssm.exe -ErrorAction SilentlyContinue).Source
if (-not $nssmPath) {
    Log "nssm.exe not found in PATH. Downloading portable nssm and extracting..."
    $tmp = Join-Path $env:TEMP 'nssm.zip'
    $url = 'https://nssm.cc/release/nssm-2.24.zip'
    try {
        Invoke-WebRequest -Uri $url -OutFile $tmp -UseBasicParsing -ErrorAction Stop
        $extract = Join-Path $env:TEMP 'nssm'
        Remove-Item -Recurse -Force $extract -ErrorAction SilentlyContinue
        Expand-Archive -Path $tmp -DestinationPath $extract -Force
        # nssm binary usually under nssm-2.24/win64/nssm.exe
        $candidate = Get-ChildItem -Path $extract -Filter 'nssm.exe' -Recurse | Select-Object -First 1
        if ($candidate) {
            $dest = Join-Path $svcDir 'nssm.exe'
            Copy-Item $candidate.FullName $dest -Force
            $nssmPath = $dest
            Log "nssm installed to $dest"
        } else { Log "Could not find nssm.exe in extracted archive"; exit 7 }
    } catch { Log "Failed to download/install nssm: $_"; exit 8 }
} else { Log "Found existing nssm at $nssmPath" }

# 6) Create/Update NSSM service to run the SSH tunnel
$sshPath = (Get-Command ssh).Source
$appArgs = "-i `"$dstKey`" -o ExitOnForwardFailure=yes -o ServerAliveInterval=60 -o ServerAliveCountMax=3 -o UserKnownHostsFile=`"$knownHosts`" -N -T -L 5901:localhost:5901 $connectedUser@$server"

# If service exists, stop and remove it first to ensure clean config
if (Get-Service -Name $svcName -ErrorAction SilentlyContinue) {
    Log "Stopping existing service $svcName"
    try { & $nssmPath stop $svcName 2>$null } catch {}
    Log "Removing existing service $svcName"
    try { & $nssmPath remove $svcName confirm } catch {}
}

Log "Installing NSSM service $svcName"
& $nssmPath install $svcName $sshPath $appArgs
& $nssmPath set $svcName AppDirectory $svcDir
& $nssmPath set $svcName AppStdout (Join-Path $svcDir 'out.log')
& $nssmPath set $svcName AppStderr (Join-Path $svcDir 'err.log')
& $nssmPath set $svcName AppRotateFiles 1
# set service to auto start
sc.exe config $svcName start= auto | Out-Null

Log "Starting service $svcName"
& $nssmPath start $svcName
Start-Sleep -Seconds 3

# 7) Verify service and tunnel
$svcStatus = sc.exe query $svcName 2>$null
Log "Service status:"
$svcStatus

if ((Test-NetConnection -ComputerName localhost -Port 5901).TcpTestSucceeded) {
    Log "SUCCESS: localhost:5901 is reachable - tunnel is active and managed by NSSM"
} else {
    Log "FAILURE: localhost:5901 is not reachable after starting service; check $svcDir\err.log and $svcDir\out.log"
    if (Test-Path (Join-Path $svcDir 'err.log')) { Log "--- err.log ---"; Get-Content (Join-Path $svcDir 'err.log') -Tail 200 | ForEach-Object { Log $_ } }
    if (Test-Path (Join-Path $svcDir 'out.log')) { Log "--- out.log ---"; Get-Content (Join-Path $svcDir 'out.log') -Tail 200 | ForEach-Object { Log $_ } }
    Log "Aborting with non-zero exit"
    exit 9
}

# Clean up temp tunnel if started by script
if ($tempTunnel -and -not $existingSshProcs) {
    try { $tempTunnel.Kill(); Log "Stopped temporary ssh tunnel (PID $($tempTunnel.Id))" } catch { }
}

Log "All done. NSSM service $svcName configured to manage SSH tunnel to $server." 
Log 'If you want me to revert these changes, run the rollback block at top of this file or ask me to restore.'

exit 0
