# Stop the calculation queue.
#
#   .\stop_queue.ps1        finish the running job, then stop  (default, keeps the work)
#   .\stop_queue.ps1 -Now   kill the running job too           (loses it, it restarts later)

param([switch]$Now)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

New-Item -ItemType File -Path "batch_results\STOP" -Force | Out-Null

$hb = Get-Content "batch_results\heartbeat.json" -ErrorAction SilentlyContinue | ConvertFrom-Json
if (-not $hb -or -not (Get-Process -Id $hb.pid -ErrorAction SilentlyContinue)) {
    Write-Host "No queue is running. STOP file placed anyway, so a restart would exit at once."
    Write-Host "Remove it with:  Remove-Item batch_results\STOP"
    exit 0
}

if ($Now) {
    Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
    Write-Host "Queue and running job both killed." -ForegroundColor Yellow
    Write-Host "The unfinished job left no result file, so it will simply run again next time."
} else {
    # Kill only the manager. Its child writes its own result file, so the hour
    # already spent on the current molecule is kept rather than thrown away.
    Stop-Process -Id $hb.pid -Force -ErrorAction SilentlyContinue
    Write-Host "Queue stopped. The running job ($($hb.current_job)) is still going and" -ForegroundColor Green
    Write-Host "will save itself when it finishes. Nothing starts after it."
}

Write-Host ""
Write-Host "Restart later with:  .\run_queue.ps1"
