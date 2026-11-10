@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Magic Rain needs a local Python environment. Run Setup-Magic-Rain.cmd.
    pause
    exit /b 1
)
set "PYTHONUTF8=1"
".venv\Scripts\python.exe" -m magic_rain %*
set "result=%errorlevel%"
if not "%result%"=="0" if "%~1"=="" pause
exit /b %result%
