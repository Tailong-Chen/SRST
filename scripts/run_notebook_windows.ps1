. (Join-Path $PSScriptRoot 'windows_common.ps1')
try {
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
}
