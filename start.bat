@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"

set "PY="

if exist "venv\Scripts\python.exe" (
    set "PY=%~dp0venv\Scripts\python.exe"
    goto :check_flask
)

if exist ".venv\Scripts\python.exe" (
    set "PY=%~dp0.venv\Scripts\python.exe"
    goto :check_flask
)

py -c "import flask" >nul 2>nul
if not errorlevel 1 (
    set "PY=py"
    goto :run
)

if exist "%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe" (
    "%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe" -c "import flask" >nul 2>nul
    if not errorlevel 1 (
        set "PY=%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe"
        goto :run
    )
)

echo Creating virtual environment in venv\ ...
py -m venv venv 2>nul || python -m venv venv
if errorlevel 1 (
    echo [ERROR] Python 3 not found. Install Python 3 and retry.
    pause
    exit /b 1
)
set "PY=%~dp0venv\Scripts\python.exe"

:check_flask
"%PY%" -c "import flask" >nul 2>nul
if errorlevel 1 (
    echo Installing dependencies from requirements.txt ...
    "%PY%" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies.
        pause
        exit /b 1
    )
)

:run
echo Starting Incident Management Center on http://127.0.0.1:5000 ...
echo Press Ctrl+C to stop the server.
if not "%NO_BROWSER%"=="1" (
    start "" /b cmd /c "timeout /t 2 /nobreak >nul && start http://127.0.0.1:5000"
)
"%PY%" app.py
if errorlevel 1 (
    echo.
    echo [ERROR] Server exited with code %errorlevel%.
    pause
)
