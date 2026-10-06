param([switch]$Repair)
. (Join-Path $PSScriptRoot 'windows_common.ps1')
$log = Join-Path $SrstRoot 'srst.log'
$transcriptStarted = $false
try {
    Start-Transcript -Path $log -Append | Out-Null
    $transcriptStarted = $true
    Set-Location -LiteralPath $SrstRoot
    Assert-SrstDemoAssets
    Write-Host 'SRST - fitting.ipynb'
    Get-SrstRequiredManager | Out-Null
    if (-not $Repair -and (Test-SrstEnvironmentReady)) {
        Write-Host 'The verified environment is ready. Opening the notebook ...'
    } else {
        Write-Host 'Preparing and checking the environment. The first launch downloads several GB; keep this window open.'
        Invoke-SrstCommand 'powershell.exe' @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', (Join-Path $PSScriptRoot 'install_windows.ps1'), '-NoTranscript')
    }
    Invoke-SrstCommand 'powershell.exe' @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', (Join-Path $PSScriptRoot 'run_notebook_windows.ps1'), '-NoTranscript')
} catch {
    Write-Host "[ERROR] $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Full log: $log"
    Write-Host 'After resolving the error, double-click start_srst.bat again. Guide: docs/windows_zh.md'
    exit 1
} finally {
    if ($transcriptStarted) { Stop-Transcript | Out-Null }
}
