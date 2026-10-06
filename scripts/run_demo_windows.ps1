param([Parameter(ValueFromRemainingArguments=$true)][string[]]$DemoArguments)
. (Join-Path $PSScriptRoot 'windows_common.ps1')
try {
    Set-Location -LiteralPath $SrstRoot
    $conda = Get-SrstInstalledManager
    $arguments = @(Get-SrstPythonArguments $conda) + @('demo.py')
    if ($DemoArguments) { $arguments += $DemoArguments }
    Invoke-SrstCommand $conda $arguments
} catch {
    Write-Host "[ERROR] $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
