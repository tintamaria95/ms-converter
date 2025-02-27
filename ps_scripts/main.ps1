$currFolderPath = Split-Path -Parent $PSCommandPath
$pythonDir = [System.IO.Path]::Combine($currFolderPath, "python")
$pythonInstaller = [System.IO.Path]::Combine($pythonDir, "python-installer.exe")
$pythonExe = [System.IO.Path]::Combine($pythonDir, "python.exe")


if (!(Test-Path $pythonDir)) {
    New-Item -ItemType Directory -Path $pythonDir | Out-Null
}

Write-Host "STEP 1/3 Python installation" -ForegroundColor Cyan
if ( Get-Command $pythonExe -ErrorAction SilentlyContinue){
    Write-Host "-> Python already installed"
} else {
    Write-Host "-> Python not installed"
    $pythonInstallationFilePath = [System.IO.Path]::Combine($currFolderPath, "0_install_python.ps1")
    & $pythonInstallationFilePath
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "Python installation encountered an issue. Stopping execution."  -ForegroundColor Red
    exit $LASTEXITCODE
}


Write-Host "STEP 2/3: Upgrading pip" -ForegroundColor Cyan
& $pythonExe -m pip install --upgrade pip --no-warn-script-location


Write-Host "STEP 3/3: Installing python requirements..." -ForegroundColor Cyan
$requirementsPath = [System.IO.Path]::Combine($currFolderPath, "..", "requirements.txt")
& $pythonExe -m pip install -r requirements.txt  --no-warn-script-location

Write-Host "Installation completed!" -ForegroundColor Green