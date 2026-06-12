@echo off
setlocal enabledelayedexpansion

:: Set working directory to project root
cd /d "%~dp0"

:: Detect Virtual Environment and activate it if present
if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
) else if exist "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat"
)

:: Check if Python is installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not added to PATH
    pause
    exit /b 1
)

:: Verify dependencies are installed
python -c "import yt_dlp, rich, PySide6, textual" >nul 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] Missing dependencies detected.
    echo Run: pip install -r requirements.txt
    echo.
    set /p "install_choice=Would you like to install requirements now? (y/n): "
    if /i "!install_choice!"=="y" (
        echo Installing dependencies...
        pip install -r requirements.txt
        if !errorlevel! neq 0 (
            echo [ERROR] Failed to install dependencies.
            pause
            exit /b 1
        )
    ) else (
        echo Exiting...
        exit /b 1
    )
)

:: Execute main application
python main.py %*
if %errorlevel% neq 0 (
    pause
)
