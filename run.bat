@echo off
cd /d "%~dp0"
set "PYTHON_DIR=C:\Users\Leangheng Korn\AppData\Local\Programs\Python\Python312"
set "PATH=%PYTHON_DIR%;%PYTHON_DIR%\Scripts;%PATH%"

echo ========================================
echo  Starting QR Code Generator Pro...
echo ========================================
python app.py
if %ERRORLEVEL% neq 0 (
    pause
)
