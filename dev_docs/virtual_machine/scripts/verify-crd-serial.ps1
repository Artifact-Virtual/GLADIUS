# One-shot verification script for Chrome Remote Desktop
# Prints CRD logs, marker file, folder listing and service status to the console (captured by serial output)
$ErrorActionPreference = 'Stop'
Write-Output "=== CRD Verif Start ==="

$logPath = 'C:\Windows\Temp\startup-extend-windows-setup-with-crd.log'
$marker = 'C:\Windows\Temp\crd_registered.txt'
$crdFolder = "$Env:ProgramFiles(x86)\Google\Chrome Remote Desktop\CurrentVersion"

Write-Output "Checking log: $logPath"
if (Test-Path $logPath) {
    Write-Output "--- Log contents start ---"
    Get-Content $logPath -ErrorAction SilentlyContinue | ForEach-Object { Write-Output $_ }
    Write-Output "--- Log contents end ---"
} else {
    Write-Output "Log not found: $logPath"
}

Write-Output "Checking marker: $marker"
if (Test-Path $marker) {
    Write-Output "Marker present. Contents:"
    Get-Content $marker -ErrorAction SilentlyContinue | ForEach-Object { Write-Output $_ }
} else {
    Write-Output "Marker not present"
}

Write-Output "Listing CRD install folder: $crdFolder"
if (Test-Path $crdFolder) {
    Get-ChildItem -Path $crdFolder -Recurse -ErrorAction SilentlyContinue | Select-Object FullName,Length,LastWriteTime -First 100 | ForEach-Object { Write-Output ("{0} {1} {2}" -f $_.LastWriteTime, $_.Length, $_.FullName) }
} else {
    Write-Output "CRD folder not found"
}

Write-Output "Querying services related to CRD"
Get-Service | Where-Object { $_.Name -match 'remote|chrome|crd|remoting' -or $_.DisplayName -match 'remote|chrome|crd|remoting' } | Select-Object Status,Name,DisplayName | ForEach-Object { Write-Output ("{0} {1} {2}" -f $_.Status, $_.Name, $_.DisplayName) }

Write-Output "=== CRD Verif End ==="

# Sleep briefly to ensure output is flushed
Start-Sleep -Seconds 5
