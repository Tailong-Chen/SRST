# Shared by the Windows installer and launchers. Compatible with PowerShell 5.1.
Set-StrictMode -Version 2.0
$ErrorActionPreference = 'Stop'
$SrstRoot = Split-Path -Parent $PSScriptRoot
$SrstEnvironment = Join-Path $SrstRoot '.runtime\srst_demo'
$SrstReadyFile = Join-Path $SrstEnvironment '.srst-ready.json'

function Get-SrstFileHash {
    param([string]$Path)
    $stream = [IO.File]::OpenRead($Path)
    $algorithm = [Security.Cryptography.SHA256]::Create()
    try {
        return ([BitConverter]::ToString($algorithm.ComputeHash($stream))).Replace('-', '')
    } finally {
        $algorithm.Dispose()
        $stream.Dispose()
    }
}

function Assert-SrstDemoAssets {
    if (-not [Environment]::Is64BitOperatingSystem -or
        ($env:PROCESSOR_ARCHITECTURE -ne 'AMD64' -and $env:PROCESSOR_ARCHITEW6432 -ne 'AMD64')) {
        throw 'SRST requires x64 Windows.'
    }
    foreach ($asset in @('dataset\frame.tif', 'network\experiment1\model_2.pt',
                          'network\experiment1\param_run.yaml', 'psfmod\spline_calibration_3dcal.mat', 'fitting.ipynb')) {
        if (-not (Test-Path -LiteralPath (Join-Path $SrstRoot $asset) -PathType Leaf)) {
            throw "Required demo asset is missing: $asset. Extract the complete SRST folder."
        }
    }
}

function Get-SrstSetupSignature {
    $parts = foreach ($relative in @('requirements\windows-conda.txt', 'requirements\windows-demo.txt',
                                    'requirements\windows-constraints.txt', 'scripts\install_windows.ps1',
                                    'scripts\windows_common.ps1', 'scripts\check_notebook_kernel.py')) {
        $file = Join-Path $SrstRoot $relative
        if (-not (Test-Path -LiteralPath $file -PathType Leaf)) {
            throw "Required setup file is missing: $relative. Extract the complete SRST folder."
        }
        Get-SrstFileHash $file
    }
    return ($parts -join '|')
}

function Test-SrstEnvironmentReady {
    if (-not (Test-Path -LiteralPath $SrstReadyFile -PathType Leaf) -or
        -not (Test-Path -LiteralPath (Join-Path $SrstEnvironment 'python.exe') -PathType Leaf) -or
        -not (Get-SrstManager)) { return $false }
    try {
        $ready = Get-Content -LiteralPath $SrstReadyFile -Raw -Encoding UTF8 | ConvertFrom-Json
        return ($ready.schema -eq 1 -and $ready.environment -eq $SrstEnvironment -and
                $ready.signature -eq (Get-SrstSetupSignature))
    } catch {
        return $false
    }
}

function Set-SrstEnvironmentReady {
    param([string]$Signature)
    New-Item -ItemType Directory -Path $SrstEnvironment -Force | Out-Null
    $ready = [ordered]@{schema = 1; environment = $SrstEnvironment; signature = $Signature;
                       completedAtUTC = [DateTime]::UtcNow.ToString('o')}
    $partial = "$SrstReadyFile.tmp"
    $ready | ConvertTo-Json | Set-Content -LiteralPath $partial -Encoding UTF8
    Move-Item -LiteralPath $partial -Destination $SrstReadyFile -Force
}

function Get-SrstManager {
    $candidates = @()
    if ($env:CONDA_EXE) { $candidates += $env:CONDA_EXE }
    $bases = @( (Join-Path $SrstRoot '.runtime\miniforge3') )
    if ($env:CONDA_PREFIX) { $bases += $env:CONDA_PREFIX }
    if ($env:CONDA_PYTHON_EXE) { $bases += Split-Path -Parent $env:CONDA_PYTHON_EXE }
    foreach ($parent in @($env:USERPROFILE, $env:LOCALAPPDATA, $env:ProgramData)) {
        if ($parent) {
            foreach ($name in @('miniforge3', 'miniconda3', 'anaconda3')) {
                $bases += Join-Path $parent $name
            }
        }
    }
    foreach ($drive in Get-PSDrive -PSProvider FileSystem) {
        foreach ($name in @('Miniconda3', 'Anaconda3', 'Miniforge3', 'Mamba')) {
            $bases += Join-Path $drive.Root $name
        }
    }
    foreach ($base in $bases) {
        $candidates += Join-Path $base 'Scripts\conda.exe'
        $candidates += Join-Path $base 'condabin\conda.bat'
    }
    $candidates += Join-Path $SrstRoot '.runtime\micromamba.exe'
    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            return (Get-Item -LiteralPath $candidate).FullName
        }
    }
    foreach ($name in @('conda.exe', 'conda.bat')) {
        $command = Get-Command $name -ErrorAction SilentlyContinue
        if ($command) { return $command.Source }
    }
    return $null
}

function Invoke-SrstCommand {
    param([string]$File, [string[]]$Arguments)
    $previousPreference = $ErrorActionPreference
    try {
        # PS 5.1 represents native stderr as ErrorRecords. Record them in the
        # transcript without treating a progress/warning line as a failed command.
        $ErrorActionPreference = 'Continue'
        & $File @Arguments 2>&1 | ForEach-Object {
            if ($_ -is [System.Management.Automation.ErrorRecord]) {
                Write-Host $_.Exception.Message
            } else {
                Write-Host $_.ToString()
            }
        }
        $nativeExit = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousPreference
    }
    if ($nativeExit -ne 0) {
        throw "Command failed with exit code $nativeExit`: $File $($Arguments -join ' ')"
    }
}

function Install-SrstManager {
    $runtime = Join-Path $SrstRoot '.runtime'
    $executable = Join-Path $runtime 'micromamba.exe'
    $url = 'https://github.com/mamba-org/micromamba-releases/releases/download/2.9.0-0/micromamba-win-64.exe'
    $sha256 = 'a6d804394b2418991c4e29562853eaace2f2ce9d9da661a98e74e02e8dbb44b0'
    New-Item -ItemType Directory -Path $runtime -Force | Out-Null
    if (-not (Test-Path -LiteralPath $executable) -or
        (Get-SrstFileHash $executable) -ne $sha256) {
        Write-Host 'Conda was not found. Downloading official portable Micromamba ...'
        $partial = "$executable.part"
        $curl = Get-Command curl.exe -ErrorAction SilentlyContinue
        if ($curl) {
            Invoke-SrstCommand $curl.Source @('--fail', '--silent', '--show-error', '--location', '--retry', '3', '--connect-timeout', '30', '--output', $partial, $url)
        } else {
            [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
            Invoke-WebRequest -Uri $url -OutFile $partial -UseBasicParsing
        }
        if ((Get-SrstFileHash $partial) -ne $sha256) {
            throw 'The Micromamba download failed its SHA-256 check. Run the installer again.'
        }
        Move-Item -LiteralPath $partial -Destination $executable -Force
    }
    Invoke-SrstCommand $executable @('--version')
    return $executable
}

function Get-SrstPythonArguments {
    param([string]$Manager)
    if ([IO.Path]::GetFileNameWithoutExtension($Manager) -eq 'micromamba') {
        return @('run', '--root-prefix', (Join-Path $SrstRoot '.runtime\mamba'), '--prefix', $SrstEnvironment, 'python')
    }
    return @('run', '--no-capture-output', '--prefix', $SrstEnvironment, 'python')
}

function Get-SrstInstalledManager {
    $manager = Get-SrstManager
    if (-not $manager -or -not (Test-Path -LiteralPath (Join-Path $SrstEnvironment 'python.exe'))) {
        throw 'The SRST environment is not installed. Double-click start_srst.bat.'
    }
    return $manager
}
