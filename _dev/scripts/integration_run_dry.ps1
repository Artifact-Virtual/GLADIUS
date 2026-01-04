$proc = Start-Process -FilePath 'C:\workspace\herald\venv312\Scripts\python.exe' -ArgumentList '-m','herald','--config','C:\workspace\herald\config.json','--dry-run','--skip-setup','--no-prompt','--log-level','INFO' -PassThru
Start-Sleep -Seconds 8
if (-not $proc.HasExited) {
    try { $proc.CloseMainWindow() } catch {}
    Start-Sleep -Seconds 2
    if (-not $proc.HasExited) { $proc.Kill() }
}

Write-Output "PROCESS_ENDED"
