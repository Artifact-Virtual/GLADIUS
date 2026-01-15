# ARTIFACT QWEN OPERATIONAL TRAINER
# ==================================
# Train Qwen2.5-1.5B for Artifact infrastructure operations
# NOT GLADIUS - This is Artifact's operational AI

$ErrorActionPreference = "Continue"

Write-Host @"

╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║     A R T I F A C T   Q W E N   O P E R A T I O N A L        ║
║                                                               ║
║   Infrastructure AI for Artifact Virtual Enterprise          ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

"@

$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$ArtifactRoot = Split-Path -Parent $ScriptPath

# Activate venv if exists
if (Test-Path "$ArtifactRoot\.venv\Scripts\Activate.ps1") {
    . "$ArtifactRoot\.venv\Scripts\Activate.ps1"
}

Write-Host "Starting Artifact Qwen Operational Trainer..." -ForegroundColor Cyan
Write-Host "Purpose: Infrastructure operations (NOT GLADIUS)" -ForegroundColor Yellow
Write-Host ""

# Run trainer
python "$ScriptPath/qwen_operational.py" --train

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Qwen Operational training complete!" -ForegroundColor Green
    Write-Host "Model ready for Artifact infrastructure operations." -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Training encountered issues. Check logs." -ForegroundColor Red
}
