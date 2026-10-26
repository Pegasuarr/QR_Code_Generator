# Refresh PATH with Python 3.12 for this terminal session
$pythonDir = "C:\Users\Leangheng Korn\AppData\Local\Programs\Python\Python312"
$scriptsDir = "$pythonDir\Scripts"

if ($env:PATH -notlike "*$pythonDir*") {
    $env:PATH = "$pythonDir;$scriptsDir;$env:PATH"
}

Write-Host "Starting QR Code Generator Pro..." -ForegroundColor Cyan
python app.py
