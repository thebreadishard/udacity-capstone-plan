# Start the calculation queue and detach from this shell.
#
#   .\run_queue.ps1
#
# Then close everything, including VS Code. The queue keeps running.
# When you come back, read batch_results\STATUS.md.

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$python = Join-Path $env:USERPROFILE ".conda\envs\qc\python.exe"
if (-not (Test-Path $python)) {
    Write-Host "Cannot find the qc environment at $python" -ForegroundColor Red
    Write-Host "Recreate it with:  conda create -n qc -c conda-forge psi4 rdkit -y"
    exit 1
}

# A stale STOP would make the runner exit immediately, which looks like a crash.
Remove-Item "batch_results\STOP" -ErrorAction SilentlyContinue

$running = Get-Content "batch_results\heartbeat.json" -ErrorAction SilentlyContinue |
           ConvertFrom-Json -ErrorAction SilentlyContinue
if ($running -and $running.state -eq "running" -and (Get-Process -Id $running.pid -ErrorAction SilentlyContinue)) {
    Write-Host "A queue is already running (pid $($running.pid), job $($running.current_job))." -ForegroundColor Yellow
    Write-Host "Two runners would fight over the same result files. Nothing started."
    exit 1
}

Start-Process -FilePath $python -ArgumentList "batch_runner.py" `
              -WorkingDirectory $PSScriptRoot -WindowStyle Hidden

Start-Sleep -Seconds 5
$hb = Get-Content "batch_results\heartbeat.json" -ErrorAction SilentlyContinue | ConvertFrom-Json

Write-Host ""
Write-Host "Queue started." -ForegroundColor Green
if ($hb) { Write-Host "  pid $($hb.pid), now on: $($hb.current_job)" }
Write-Host ""
Write-Host "Safe to close this window and VS Code. Finished jobs are never repeated,"
Write-Host "so if the machine reboots just run this script again."
Write-Host ""
Write-Host "  progress   batch_results\STATUS.md"
Write-Host "  stop       .\stop_queue.ps1"
Write-Host ""
