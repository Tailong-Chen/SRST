@echo off
setlocal EnableExtensions
pushd "%~dp0"
if errorlevel 1 (
    echo [ERROR] Cannot open the SRST project folder: %~dp0
    exit /b 1
)

set "ENV_NAME=srst_demo"
set "CONDA_BAT="
for %%P in ("%CONDA_PREFIX%\condabin\conda.bat" "%USERPROFILE%\miniconda3\condabin\conda.bat" "%USERPROFILE%\anaconda3\condabin\conda.bat" "%USERPROFILE%\miniforge3\condabin\conda.bat" "%LOCALAPPDATA%\miniforge3\condabin\conda.bat" "%ProgramData%\miniconda3\condabin\conda.bat" "%ProgramData%\Anaconda3\condabin\conda.bat" "%ProgramData%\miniforge3\condabin\conda.bat") do (
    if not defined CONDA_BAT if exist "%%~P" set "CONDA_BAT=%%~P"
)
if not defined CONDA_BAT for /f "delims=" %%P in ('where conda.bat 2^>nul') do if not defined CONDA_BAT set "CONDA_BAT=%%P"

if not defined CONDA_BAT (
    echo [ERROR] Conda was not found. Miniconda, Anaconda, or Miniforge is required.
    echo Run install_windows.bat first.
    goto :fail
)

call "%CONDA_BAT%" run --no-capture-output -n %ENV_NAME% python demo.py %*
if errorlevel 1 (
    echo.
    echo Demo failed. Check the error above and README_WINDOWS.md.
    goto :fail
)

echo.
echo Demo complete. Results are in outputs\demo.
goto :success

:fail
popd
exit /b 1

:success
popd
exit /b 0
