@echo off
title F-SOCIETY YT-DLP TOOL - CMD LAUNCHER
color 0A

:: Check if standard python command works
where python >nul 2>nul
if %errorlevel% equ 0 (
    python "%~dp0main.py" %*
    goto end
)

:: Try py command
where py >nul 2>nul
if %errorlevel% equ 0 (
    py "%~dp0main.py" %*
    goto end
)

:: Search common installation directories
echo [INFO] Python not found in system PATH. Searching common directories...
for /d %%d in ("%USERPROFILE%\AppData\Local\Programs\Python\Python*") do (
    if exist "%%d\python.exe" (
        "%%d\python.exe" "%~dp0main.py" %*
        goto end
    )
)
for /d %%d in ("%SystemDrive%\Python*") do (
    if exist "%%d\python.exe" (
        "%%d\python.exe" "%~dp0main.py" %*
        goto end
    )
)
for /d %%d in ("%ProgramFiles%\Python*") do (
    if exist "%%d\python.exe" (
        "%%d\python.exe" "%~dp0main.py" %*
        goto end
    )
)

echo.
echo [ERROR] Python was not found on your system.
echo Please install Python 3 from https://www.python.org/
echo Ensure the "Add Python to PATH" option is checked during installation.
echo.
pause

:end
if %errorlevel% neq 0 (
    pause
)