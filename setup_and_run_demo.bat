@echo off
setlocal EnableExtensions
pushd "%~dp0"
if errorlevel 1 goto :fail
set "PUSHD_OK=1"

set "LOG_FILE=%~dp0setup_and_run_demo.log"
>"%LOG_FILE%" echo SRST setup started at %DATE% %TIME%
echo [1/2] Installing or updating the srst_demo environment ...
call install_windows.bat > "%LOG_FILE%" 2>&1
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" goto :fail
type "%LOG_FILE%"

echo [2/2] Running the pretrained demo ...
call run_demo_windows.bat %* >> "%LOG_FILE%" 2>&1
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" goto :fail
type "%LOG_FILE%"

echo.
echo Setup and demo completed successfully.
echo Results are in outputs\demo.
echo Log: %LOG_FILE%
pause
popd
exit /b 0

:fail
echo.
echo [ERROR] SRST setup or demo failed. Exit code %RC%.
echo The window is being kept open so the error above can be read.
echo Log: %LOG_FILE%
if exist "%LOG_FILE%" type "%LOG_FILE%"
pause
if "%PUSHD_OK%"=="1" popd
exit /b 1
