@echo off
setlocal EnableExtensions
pushd "%~dp0"
if errorlevel 1 exit /b 1
set "SRST_NO_PAUSE=1"
call install_windows.bat
set "SRST_EXIT_CODE=%ERRORLEVEL%"
if not "%SRST_EXIT_CODE%"=="0" goto :finish
call run_notebook_windows.bat
set "SRST_EXIT_CODE=%ERRORLEVEL%"
:finish
if not "%SRST_EXIT_CODE%"=="0" echo [ERROR] See setup_and_run_demo.log for installation details.
pause
popd
exit /b %SRST_EXIT_CODE%
