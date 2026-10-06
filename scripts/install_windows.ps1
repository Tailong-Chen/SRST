param([switch]$SkipSmokeTest, [switch]$NoTranscript)
. (Join-Path $PSScriptRoot 'windows_common.ps1')
$log = Join-Path $SrstRoot 'srst.log'
$transcriptStarted = $false
try {
    if (-not $NoTranscript) {
        Start-Transcript -Path $log -Append | Out-Null
        $transcriptStarted = $true
    }
    Set-Location -LiteralPath $SrstRoot
    Assert-SrstDemoAssets
    if (Test-Path -LiteralPath $SrstReadyFile) { Remove-Item -LiteralPath $SrstReadyFile }
    $setupSignature = Get-SrstSetupSignature
    Write-Host '[1/5] Preparing the environment manager ...'
    $conda = Get-SrstManager
    if (-not $conda) { $conda = Install-SrstManager }
    Write-Host "Environment manager: $conda"
    Write-Host "SRST environment: $SrstEnvironment"
    $env:CONDA_PKGS_DIRS = Join-Path $SrstRoot '.runtime\cache\conda'
    $env:PIP_CACHE_DIR = Join-Path $SrstRoot '.runtime\cache\pip'
    Write-Host '[2/5] Installing Python 3.9, compiled spline, PyTorch and Jupyter ...'
    $operation = 'create'
    if (Test-Path -LiteralPath (Join-Path $SrstEnvironment 'python.exe')) { $operation = 'install' }
    # Explicit channels are needed before Conda's pre-command plugins run.
    $condaArguments = @($operation, '--yes', '--override-channels', '--channel', 'turagalab', '--channel', 'conda-forge', '--prefix', $SrstEnvironment, '--file', (Join-Path $SrstRoot 'requirements\windows-conda.txt'))
    if ([IO.Path]::GetFileNameWithoutExtension($conda) -eq 'micromamba') {
        $condaArguments += @('--no-rc', '--root-prefix', (Join-Path $SrstRoot '.runtime\mamba'))
    } elseif ($operation -eq 'create') {
        $condaArguments += '--no-default-packages'
    }
    Invoke-SrstCommand $conda $condaArguments
    $run = @(Get-SrstPythonArguments $conda)
    # The CUDA wheel is several GB. Tolerate pauses and interrupted transfers
    # without changing the user's global pip configuration.
    Write-Host 'Large downloads: timeout 120 s, connection retries 10, resume attempts 20. Keep this window open while downloads resume.'
    Invoke-SrstCommand $conda ($run + @('-m', 'pip', 'install', '--timeout', '120', '--retries', '10', '--resume-retries', '20', '--requirement', (Join-Path $SrstRoot 'requirements\windows-demo.txt')))
    Write-Host '[3/5] Checking dependencies and the compiled spline module ...'
    Invoke-SrstCommand $conda ($run + @('-m', 'pip', 'check'))
    Invoke-SrstCommand $conda ($run + @('-c', "import torch, numpy, scipy, spline, decode, demo, notebook, jupyterlab, ipykernel; print('Python/NumPy/spline/SRST/Jupyter imports OK'); print('torch:', torch.__version__); print('numpy:', numpy.__version__); print('CUDA available:', torch.cuda.is_available())"))
    Write-Host '[4/5] Registering the SRST notebook kernel ...'
    Invoke-SrstCommand $conda ($run + @('-m', 'ipykernel', 'install', '--user', '--name', 'srst_demo', '--display-name', 'SRST (srst_demo)'))
    Invoke-SrstCommand $conda ($run + @((Join-Path $PSScriptRoot 'check_notebook_kernel.py')))
    Write-Host '[5/5] Checking the bundled model with 9 frames ...'
    if ($SkipSmokeTest) {
        Write-Host 'Localization check was explicitly skipped.'
    } else {
        Invoke-SrstCommand $conda ($run + @('demo.py', '--device', 'auto', '--max-frames', '9', '--batch-size', '1', '--output', (Join-Path $SrstRoot 'outputs\installation_check')))
        Set-SrstEnvironmentReady $setupSignature
    }
    Write-Host ''
    Write-Host 'Environment checks finished. Use start_srst.bat to open fitting.ipynb.'
    Write-Host 'In VS Code, select the kernel SRST (srst_demo). No model training is required.'
} catch {
    Write-Host "[ERROR] $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Full log: $log"
    exit 1
} finally {
    if ($transcriptStarted) { Stop-Transcript | Out-Null }
}
