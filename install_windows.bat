@echo off
setlocal EnableExtensions
pushd "%~dp0"
if errorlevel 1 (
    echo [ERROR] Cannot open the SRST project folder: %~dp0
    exit /b 1
)

set "ENV_NAME=srst_demo"
for %%F in ("dataset\frame.tif" "network\experiment1\model_2.pt" "network\experiment1\param_run.yaml" "psfmod\spline_calibration_3dcal.mat") do (
    if not exist "%%~F" (
        echo [ERROR] Required demo asset is missing: %%~F
        goto :fail
    )
)
set "CONDA_BAT="
for %%P in ("%CONDA_PREFIX%\condabin\conda.bat" "%USERPROFILE%\miniconda3\condabin\conda.bat" "%USERPROFILE%\anaconda3\condabin\conda.bat" "%USERPROFILE%\miniforge3\condabin\conda.bat" "%LOCALAPPDATA%\miniforge3\condabin\conda.bat" "%ProgramData%\miniconda3\condabin\conda.bat" "%ProgramData%\Anaconda3\condabin\conda.bat" "%ProgramData%\miniforge3\condabin\conda.bat") do (
    if not defined CONDA_BAT if exist "%%~P" set "CONDA_BAT=%%~P"
)
if not defined CONDA_BAT for /f "delims=" %%P in ('where conda.bat 2^>nul') do if not defined CONDA_BAT set "CONDA_BAT=%%P"

if not defined CONDA_BAT (
    where winget >nul 2>&1
    if not errorlevel 1 (
        echo Conda was not found. Trying a per-user Miniforge install via winget ...
        winget install --id CondaForge.Miniforge3 --exact --scope user --silent --accept-source-agreements --accept-package-agreements
        for %%P in ("%USERPROFILE%\miniforge3\condabin\conda.bat" "%LOCALAPPDATA%\miniforge3\condabin\conda.bat" "%ProgramData%\miniforge3\condabin\conda.bat") do (
            if not defined CONDA_BAT if exist "%%~P" set "CONDA_BAT=%%~P"
        )
    )
)

if not defined CONDA_BAT (
    echo [ERROR] Miniconda, Anaconda, or Miniforge was not found.
    echo Install Miniconda for Windows from https://docs.conda.io/projects/miniconda/en/latest/
    echo Then run this file again.
    goto :fail
)

call "%CONDA_BAT%" env list | findstr /R /C:"^[^#].*%ENV_NAME%" >nul
if errorlevel 1 (
    echo Creating conda environment %ENV_NAME% ...
    call "%CONDA_BAT%" env create -f environment-windows-demo.yml
    if errorlevel 1 goto :fail
) else (
    echo Conda environment %ENV_NAME% already exists; updating it ...
    call "%CONDA_BAT%" env update -f environment-windows-demo.yml --prune
    if errorlevel 1 goto :fail
)

echo Verifying the demo installation ...
call "%CONDA_BAT%" run --no-capture-output -n %ENV_NAME% python -c "import torch, tifffile, spline, decode, demo, jupyterlab, ipykernel; print('torch', torch.__version__); print('cuda_runtime', torch.version.cuda); print('cuda_available', torch.cuda.is_available()); print('cuda_devices', torch.cuda.device_count()); print('tifffile', tifffile.__version__); print('spline', getattr(spline, '__version__', 'available')); print('jupyterlab', jupyterlab.__version__); print('SRST import OK')"
if errorlevel 1 goto :fail
where nvidia-smi >nul 2>&1
if not errorlevel 1 (
    echo NVIDIA driver detected; checking the CUDA PyTorch path ...
    call "%CONDA_BAT%" run --no-capture-output -n %ENV_NAME% python -c "import torch, sys; sys.exit(0 if torch.cuda.is_available() else 1)"
    if errorlevel 1 (
        echo [ERROR] nvidia-smi is available, but PyTorch cannot access CUDA.
        echo Update the NVIDIA driver and rerun this installer.
        goto :fail
    )
    call "%CONDA_BAT%" run --no-capture-output -n %ENV_NAME% python -c "import torch; print('cuda_device', torch.cuda.get_device_name(0))"
    if errorlevel 1 goto :fail
    echo Running a 9-frame CUDA smoke test ...
    call "%CONDA_BAT%" run --no-capture-output -n %ENV_NAME% python demo.py --device cuda:0 --max-frames 9 --output "%TEMP%\srst_gpu_smoke"
    if errorlevel 1 goto :fail
)
call "%CONDA_BAT%" run --no-capture-output -n %ENV_NAME% python -m ipykernel install --user --name srst_demo --display-name "SRST (srst_demo)"
if errorlevel 1 goto :fail

echo Installation complete. Run run_demo_windows.bat to start the demo.
goto :success

:fail
popd
exit /b 1

:success
popd
exit /b 0
