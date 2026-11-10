@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    py -3.12 -m venv .venv
    if errorlevel 1 py -3.11 -m venv .venv
    if errorlevel 1 (
        echo Install Python 3.12 or 3.11 before running setup.
        pause
        exit /b 1
    )
)
".venv\Scripts\python.exe" -m pip --version >nul 2>&1
if errorlevel 1 ".venv\Scripts\python.exe" -m ensurepip --upgrade
if errorlevel 1 exit /b 1
".venv\Scripts\python.exe" -m pip install .
if errorlevel 1 (
    echo Setup failed. See the messages above.
    pause
    exit /b 1
)
echo Magic Rain is ready. Open Start-Magic-Rain.cmd to play.
pause
