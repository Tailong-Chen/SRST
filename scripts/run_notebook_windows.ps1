param([switch]$NoTranscript)
. (Join-Path $PSScriptRoot 'windows_common.ps1')
$transcriptStarted = $false
try {
    if (-not $NoTranscript) {
        Start-Transcript -Path (Join-Path $SrstRoot 'srst.log') -Append | Out-Null
        $transcriptStarted = $true
    }
    Set-Location -LiteralPath $SrstRoot
    $conda = Get-SrstInstalledManager
    $run = @(Get-SrstPythonArguments $conda)
    Invoke-SrstCommand $conda ($run + @('-c', 'import notebook, ipykernel, spline, decode'))
    Invoke-SrstCommand $conda ($run + @('-m', 'ipykernel', 'install', '--user', '--name', 'srst_demo', '--display-name', 'SRST (srst_demo)'))
    Write-Host 'Opening fitting.ipynb. Keep this window open while using Jupyter.'
    Invoke-SrstCommand $conda ($run + @('-m', 'notebook', "--notebook-dir=$SrstRoot", (Join-Path $SrstRoot 'fitting.ipynb')))
} catch {
    Write-Host "[ERROR] $($_.Exception.Message)" -ForegroundColor Red
    exit 1
} finally {
    if ($transcriptStarted) { Stop-Transcript | Out-Null }
}
