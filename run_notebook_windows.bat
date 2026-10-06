@echo off
setlocal EnableExtensions
pushd "%~dp0"
if errorlevel 1 exit /b 1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\run_notebook_windows.ps1"
set "SRST_EXIT_CODE=%ERRORLEVEL%"
if not "%SRST_EXIT_CODE%"=="0" if not defined SRST_NO_PAUSE pause
popd
exit /b %SRST_EXIT_CODE%
