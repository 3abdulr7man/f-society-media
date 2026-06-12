# F-SOCIETY MEDIA PowerShell Launcher
# Usage: powershell -ExecutionPolicy Bypass -File .\run.ps1

$ProjectDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Path
Set-Location -Path $ProjectDir

# Activate Virtual Environment if exists
if (Test-Path "$ProjectDir\.venv\Scripts\Activate.ps1") {
    . "$ProjectDir\.venv\Scripts\Activate.ps1"
} elseif (Test-Path "$ProjectDir\venv\Scripts\Activate.ps1") {
    . "$ProjectDir\venv\Scripts\Activate.ps1"
}

# Detect Python
$pythonAvailable = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonAvailable) {
    Write-Host "[ERROR] Python is not installed or not added to PATH" -ForegroundColor Red
    Read-Host "Press Enter to exit..."
    Exit 1
}

# Verify Dependencies
python -c "import yt_dlp, rich, PySide6, textual" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARNING] Missing dependencies detected." -ForegroundColor Yellow
    Write-Host "Run: pip install -r requirements.txt" -ForegroundColor Yellow
    Write-Host ""
    $choice = Read-Host "Would you like to install requirements now? (y/n)"
    if ($choice.ToLower() -eq 'y') {
        Write-Host "Installing dependencies..."
        pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[ERROR] Failed to install dependencies." -ForegroundColor Red
            Read-Host "Press Enter to exit..."
            Exit 1
        }
    } else {
        Exit 1
    }
}

# Execute main application with all passed arguments
python main.py $args
if ($LASTEXITCODE -ne 0) {
    Write-Host "[PROCESS FINISHED WITH ERROR CODE $LASTEXITCODE]" -ForegroundColor Red
    Read-Host "Press Enter to exit..."
}
