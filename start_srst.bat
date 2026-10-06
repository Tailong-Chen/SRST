@echo off
setlocal EnableExtensions
pushd "%~dp0"
if errorlevel 1 exit /b 1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start_windows.ps1" %*
set "SRST_EXIT_CODE=%ERRORLEVEL%"
if not "%SRST_EXIT_CODE%"=="0" (
    echo.
    echo [ERROR] See srst.log for details.
    if not defined SRST_NO_PAUSE pause
)
popd
exit /b %SRST_EXIT_CODE%
