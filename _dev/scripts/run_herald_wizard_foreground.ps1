<#
Opens a new PowerShell window and runs Herald in wizard mode in the foreground.
Usage: double-click this script or run from PowerShell.
#>

$python = "C:\workspace\herald\venv312\Scripts\python.exe"
$config = "C:\workspace\herald\config.json"

if (-not (Test-Path $python)) {
    Write-Host "Virtualenv python not found at $python; falling back to 'python' on PATH." -ForegroundColor Yellow
    $python = "python"
}

$psCommand = "& `"$python`" -m herald --wizard --config `"$config`""

# Start a new PowerShell window and run the command; keep the window open
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit","-Command",$psCommand
