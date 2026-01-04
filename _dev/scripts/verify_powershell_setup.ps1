Write-Host "=== ExecutionPolicy ===" -ForegroundColor Cyan
Get-ExecutionPolicy -List | Format-List *

Write-Host "`n=== Machine PSModulePath ===" -ForegroundColor Cyan
[Environment]::GetEnvironmentVariable('PSModulePath','Machine') | Write-Host

Write-Host "`n=== PSReadLine modules ===" -ForegroundColor Cyan
Get-Module -ListAvailable -Name PSReadLine | Select-Object Name,Version,Path | Format-List

$users = @('alish','noufe')
foreach ($u in $users) {
  Write-Host "`n--- User: $u ---" -ForegroundColor Cyan
  $paths = @(
    "C:\Users\$u\OneDrive\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1",
    "C:\Users\$u\OneDrive\Documents\WindowsPowerShell\profile.ps1"
  )
  foreach ($p in $paths) {
    Write-Host "Profile: $p" -ForegroundColor Yellow
    if (Test-Path $p) {
      Write-Host "Exists. Checking for PSReadLine reference..." -ForegroundColor Green
      $content = Get-Content -Path $p -Raw -ErrorAction SilentlyContinue
      if ($content -match 'PSReadLine') { Write-Host "Contains PSReadLine references." -ForegroundColor Green } else { Write-Host "No PSReadLine references found." -ForegroundColor Yellow }
      Write-Host "--- Content start ---" -ForegroundColor DarkGray
      $content | Write-Host
      Write-Host "--- Content end ---" -ForegroundColor DarkGray
    } else {
      Write-Host "Missing" -ForegroundColor Red
    }
  }
}

# Basic automated checks
$ok = $true
$ep = (Get-ExecutionPolicy -List | Where-Object { $_.Scope -eq 'LocalMachine' }).ExecutionPolicy
if ($ep -ne 'RemoteSigned') { Write-Host "LocalMachine ExecutionPolicy is $ep (expected RemoteSigned)" -ForegroundColor Red; $ok = $false } else { Write-Host "LocalMachine ExecutionPolicy is RemoteSigned" -ForegroundColor Green }

$machinePath = [Environment]::GetEnvironmentVariable('PSModulePath','Machine')
$expected = 'C:\Users\alish\OneDrive\Documents\WindowsPowerShell\Modules'
if ($machinePath -notlike "*$expected*") { Write-Host "Machine PSModulePath does not contain $expected" -ForegroundColor Red; $ok = $false } else { Write-Host "Machine PSModulePath contains $expected" -ForegroundColor Green }

$psr = Get-Module -ListAvailable -Name PSReadLine
if (!$psr) { Write-Host "PSReadLine not found in module paths" -ForegroundColor Red; $ok = $false } else { Write-Host "PSReadLine found:" -ForegroundColor Green; $psr | Select-Object Name,Version,Path | Format-List }

if ($ok) { Write-Host "`nVERIFICATION OK: All checks passed." -ForegroundColor Green; exit 0 } else { Write-Host "`nVERIFICATION ISSUES: Please review the red messages above." -ForegroundColor Red; exit 2 }