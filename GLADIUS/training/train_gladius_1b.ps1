#!/usr/bin/env pwsh
<#
.SYNOPSIS
    GLADIUS 1B Parameter Continuous Trainer - PowerShell Wrapper

.DESCRIPTION
    Launches and manages the GLADIUS 1B training pipeline.
    Supports continuous training, status monitoring, and recovery.

.PARAMETER Action
    Action to perform: start, status, stop, resume, export

.PARAMETER Hours
    Maximum training hours (default: 168 = 1 week)

.PARAMETER BaseModel
    Base model to use (default: Qwen/Qwen2.5-1.5B)

.PARAMETER BatchSize
    Training batch size (default: 4)

.EXAMPLE
    ./train_gladius_1b.ps1 start
    ./train_gladius_1b.ps1 status
    ./train_gladius_1b.ps1 -Hours 48 -BatchSize 2 start

.NOTES
    Author: Artifact Virtual Systems
    Target: 1 Billion Parameters
#>

param(
    [Parameter(Position=0)]
    [ValidateSet("start", "status", "stop", "resume", "export", "help")]
    [string]$Action = "help",
    
    [int]$Hours = 168,
    [string]$BaseModel = "Qwen/Qwen2.5-1.5B",
    [int]$BatchSize = 4
)

# Configuration
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$TrainerScript = Join-Path $ScriptRoot "gladius_1b_trainer.py"
$LogDir = Join-Path (Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $ScriptRoot))) "logs" "training"
$PidFile = Join-Path $LogDir "trainer.pid"

# Colors
$ColorHeader = "Cyan"
$ColorSuccess = "Green"
$ColorWarning = "Yellow"
$ColorError = "Red"
$ColorInfo = "White"

function Write-Banner {
    $banner = @"

╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║         G L A D I U S   1 B   T R A I N E R                  ║
║                                                              ║
║      Continuous Training Pipeline to 1 Billion Parameters   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

"@
    Write-Host $banner -ForegroundColor $ColorHeader
}

function Test-Python {
    try {
        $version = python3 --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  [OK] Python: $version" -ForegroundColor $ColorSuccess
            return $true
        }
    } catch {}
    
    try {
        $version = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  [OK] Python: $version" -ForegroundColor $ColorSuccess
            return $true
        }
    } catch {}
    
    Write-Host "  [ERROR] Python not found" -ForegroundColor $ColorError
    return $false
}

function Test-Dependencies {
    Write-Host "Checking Dependencies..." -ForegroundColor $ColorInfo
    
    $deps = @("torch", "transformers", "peft", "accelerate", "datasets")
    $missing = @()
    
    foreach ($dep in $deps) {
        $check = python3 -c "import $dep" 2>&1
        if ($LASTEXITCODE -ne 0) {
            $missing += $dep
            Write-Host "  [MISSING] $dep" -ForegroundColor $ColorWarning
        } else {
            Write-Host "  [OK] $dep" -ForegroundColor $ColorSuccess
        }
    }
    
    if ($missing.Count -gt 0) {
        Write-Host "`nInstalling missing dependencies..." -ForegroundColor $ColorInfo
        pip install torch transformers peft accelerate datasets bitsandbytes --quiet
    }
    
    return $true
}

function Start-Training {
    param([int]$MaxHours, [string]$Model, [int]$Batch)
    
    Write-Host "Starting GLADIUS 1B Training..." -ForegroundColor $ColorInfo
    Write-Host "  Max Hours: $MaxHours" -ForegroundColor $ColorInfo
    Write-Host "  Base Model: $Model" -ForegroundColor $ColorInfo
    Write-Host "  Batch Size: $Batch" -ForegroundColor $ColorInfo
    Write-Host ""
    
    # Create log directory
    if (-not (Test-Path $LogDir)) {
        New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
    }
    
    $LogFile = Join-Path $LogDir "training_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
    
    # Start training process
    $process = Start-Process -FilePath "python3" `
        -ArgumentList @(
            $TrainerScript,
            "--hours", $MaxHours,
            "--base-model", $Model,
            "--batch-size", $Batch
        ) `
        -RedirectStandardOutput $LogFile `
        -RedirectStandardError (Join-Path $LogDir "training_error.log") `
        -PassThru `
        -NoNewWindow
    
    # Save PID
    $process.Id | Out-File -FilePath $PidFile
    
    Write-Host "[STARTED] Training process PID: $($process.Id)" -ForegroundColor $ColorSuccess
    Write-Host "  Log file: $LogFile" -ForegroundColor $ColorInfo
    Write-Host ""
    Write-Host "Monitor with: ./train_gladius_1b.ps1 status" -ForegroundColor $ColorInfo
    Write-Host "Stop with:    ./train_gladius_1b.ps1 stop" -ForegroundColor $ColorInfo
}

function Get-TrainingStatus {
    Write-Host "Training Status" -ForegroundColor $ColorHeader
    Write-Host "─────────────────────────────────────────────" -ForegroundColor $ColorInfo
    
    # Check if process is running
    if (Test-Path $PidFile) {
        $pid = Get-Content $PidFile
        $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
        if ($process) {
            Write-Host "  Process:     RUNNING (PID: $pid)" -ForegroundColor $ColorSuccess
            Write-Host "  Runtime:     $((Get-Date) - $process.StartTime)" -ForegroundColor $ColorInfo
        } else {
            Write-Host "  Process:     NOT RUNNING" -ForegroundColor $ColorWarning
        }
    } else {
        Write-Host "  Process:     NOT STARTED" -ForegroundColor $ColorWarning
    }
    
    # Get state from trainer
    python3 $TrainerScript --status
}

function Stop-Training {
    Write-Host "Stopping Training..." -ForegroundColor $ColorInfo
    
    if (Test-Path $PidFile) {
        $pid = Get-Content $PidFile
        $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
        if ($process) {
            Stop-Process -Id $pid -Force
            Write-Host "  [STOPPED] Process $pid terminated" -ForegroundColor $ColorSuccess
        } else {
            Write-Host "  [INFO] Process already stopped" -ForegroundColor $ColorWarning
        }
        Remove-Item $PidFile -Force
    } else {
        Write-Host "  [INFO] No training process found" -ForegroundColor $ColorWarning
    }
}

function Resume-Training {
    Write-Host "Resuming Training from Checkpoint..." -ForegroundColor $ColorInfo
    
    # Stop any existing process
    Stop-Training
    
    # Start with resume flag
    $LogFile = Join-Path $LogDir "training_resume_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
    
    $process = Start-Process -FilePath "python3" `
        -ArgumentList @($TrainerScript, "--resume", "--hours", $Hours) `
        -RedirectStandardOutput $LogFile `
        -RedirectStandardError (Join-Path $LogDir "training_error.log") `
        -PassThru `
        -NoNewWindow
    
    $process.Id | Out-File -FilePath $PidFile
    
    Write-Host "[RESUMED] Training process PID: $($process.Id)" -ForegroundColor $ColorSuccess
}

function Export-Model {
    Write-Host "Exporting Model to GGUF..." -ForegroundColor $ColorInfo
    python3 $TrainerScript --export-only
}

function Show-Help {
    Write-Host @"
GLADIUS 1B Trainer - Commands
─────────────────────────────────────────────

  start     Start continuous training
  status    Show current training status
  stop      Stop training (saves checkpoint)
  resume    Resume from last checkpoint
  export    Export trained model to GGUF

Parameters:
  -Hours      Maximum training hours (default: 168)
  -BaseModel  Base model (default: Qwen/Qwen2.5-1.5B)
  -BatchSize  Training batch size (default: 4)

Examples:
  ./train_gladius_1b.ps1 start
  ./train_gladius_1b.ps1 -Hours 48 start
  ./train_gladius_1b.ps1 status
  ./train_gladius_1b.ps1 stop

"@ -ForegroundColor $ColorInfo
}

# Main execution
Write-Banner

if (-not (Test-Python)) {
    exit 1
}

switch ($Action) {
    "start" {
        Test-Dependencies
        Start-Training -MaxHours $Hours -Model $BaseModel -Batch $BatchSize
    }
    "status" {
        Get-TrainingStatus
    }
    "stop" {
        Stop-Training
    }
    "resume" {
        Test-Dependencies
        Resume-Training
    }
    "export" {
        Export-Model
    }
    "help" {
        Show-Help
    }
}
