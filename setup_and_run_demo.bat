@echo off
setlocal EnableExtensions
cd /d "%~dp0"

call install_windows.bat
if errorlevel 1 exit /b 1

call run_demo_windows.bat %*
exit /b %errorlevel%
