# Fix PSReadLine and execution policy for CurrentUser
Write-Host "Checking execution policy..." -ForegroundColor Cyan
Get-ExecutionPolicy -List

Write-Host "Setting ExecutionPolicy to RemoteSigned for CurrentUser..." -ForegroundColor Cyan
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force

Write-Host "Installing/updating PSReadLine..." -ForegroundColor Cyan
try {
    Install-Module -Name PSReadLine -Scope CurrentUser -Force -AllowClobber -ErrorAction Stop
} catch {
    Write-Host "Install-Module failed or requires confirmation: $_" -ForegroundColor Yellow
}

$prof = $Profile.CurrentUserAllHosts
Write-Host "Ensuring profile: $prof" -ForegroundColor Cyan
if (!(Test-Path -Path $prof)) {
    New-Item -ItemType File -Path $prof -Force | Out-Null
}

# Backup existing profile
$bak = "$prof.bak"
Copy-Item -Path $prof -Destination $bak -Force -ErrorAction SilentlyContinue

# Add a guarded PSReadLine import if profile doesn't already reference it
try {
    $content = Get-Content -Path $prof -Raw -ErrorAction SilentlyContinue
} catch {
    $content = ""
}

if ($content -notmatch 'PSReadLine') {
    $guard = @'
try {
  if (-not (Get-Module -ListAvailable -Name PSReadLine)) {
    Install-Module -Name PSReadLine -Scope CurrentUser -Force -AllowClobber -ErrorAction SilentlyContinue
  }
  Import-Module PSReadLine -ErrorAction Stop
} catch {
  Write-Host 'Warning: PSReadLine not available — running without it.' -ForegroundColor Yellow
}
'@
    Add-Content -Path $prof -Value $guard
    Write-Host "Added guarded PSReadLine import to profile ($prof). Backup at $bak" -ForegroundColor Green
} else {
    Write-Host "Profile already references PSReadLine; no change. Backup at $bak" -ForegroundColor Yellow
}

Write-Host "Done. Restart PowerShell to apply changes." -ForegroundColor Green
