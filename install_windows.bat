@echo off
setlocal EnableExtensions
pushd "%~dp0"
if errorlevel 1 exit /b 1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\install_windows.ps1" %*
set "SRST_EXIT_CODE=%ERRORLEVEL%"
echo.
echo Installation log: %~dp0setup_and_run_demo.log
if not defined SRST_NO_PAUSE pause
popd
exit /b %SRST_EXIT_CODE%
