# GLADIUS Multi-Expert Training Pipeline
# ========================================
# Distills knowledge from Qwen + Llama + Phi + Gemma into GLADIUS
# 
# Usage:
#   ./train_gladius_moe.ps1           # Full training (72 hours max)
#   ./train_gladius_moe.ps1 -Hours 24 # Custom time limit
#   ./train_gladius_moe.ps1 -Status   # Check status
#

param(
    [float]$Hours = 72,
    [switch]$Status,
    [switch]$Resume,
    [switch]$Help
)

$ErrorActionPreference = "Stop"

# Get script directory (portable)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = (Get-Item $ScriptDir).Parent.Parent.FullName

# Banner
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                                      ║" -ForegroundColor Cyan
Write-Host "║          G L A D I U S   M U L T I - E X P E R T   T R A I N E R    ║" -ForegroundColor Cyan
Write-Host "║                                                                      ║" -ForegroundColor Cyan
Write-Host "║     Building 1B Parameter Model with Custom Weights                  ║" -ForegroundColor Cyan
Write-Host "║     Expert Teachers: Qwen + Llama + Phi + Gemma                      ║" -ForegroundColor Cyan
Write-Host "║                                                                      ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

if ($Help) {
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  ./train_gladius_moe.ps1              # Full training (72h max)"
    Write-Host "  ./train_gladius_moe.ps1 -Hours 24    # Custom time limit"
    Write-Host "  ./train_gladius_moe.ps1 -Status      # Check training status"
    Write-Host "  ./train_gladius_moe.ps1 -Resume      # Resume from checkpoint"
    Write-Host ""
    Write-Host "Expert Teachers:" -ForegroundColor Yellow
    Write-Host "  - Qwen2.5-1.5B:  Tool-calling, structured output, multilingual"
    Write-Host "  - Llama-3.2-1B:  Reasoning, fluency, conversation"
    Write-Host "  - Phi-3-mini:    Mathematics, code generation"
    Write-Host "  - Gemma-2-2b:    Safety, instruction following"
    exit 0
}

# Check for training venv
$VenvPath = Join-Path $ScriptDir ".venv"
if (-not (Test-Path $VenvPath)) {
    Write-Host "Creating training virtual environment..." -ForegroundColor Yellow
    python3 -m venv $VenvPath
}

# Activate venv (Linux/WSL compatible)
$ActivateScript = Join-Path $VenvPath "bin/activate"
if (Test-Path $ActivateScript) {
    Write-Host "Activating virtual environment..." -ForegroundColor Gray
    # Note: In PowerShell on Linux, we run Python directly from venv
}

$PythonPath = Join-Path $VenvPath "bin/python"
if (-not (Test-Path $PythonPath)) {
    $PythonPath = "python3"
}

# Status check
if ($Status) {
    Write-Host "Checking training status..." -ForegroundColor Yellow
    & $PythonPath (Join-Path $ScriptDir "gladius_moe_trainer.py") --status
    exit 0
}

# Build command
$args_list = @("--hours", $Hours)
if ($Resume) {
    $args_list += "--resume"
}

Write-Host "Starting GLADIUS Multi-Expert Training" -ForegroundColor Green
Write-Host "  Time limit: $Hours hours" -ForegroundColor Gray
Write-Host "  Project root: $ProjectRoot" -ForegroundColor Gray
Write-Host ""

# Run training
& $PythonPath (Join-Path $ScriptDir "gladius_moe_trainer.py") @args_list

Write-Host ""
Write-Host "Training session ended." -ForegroundColor Cyan
