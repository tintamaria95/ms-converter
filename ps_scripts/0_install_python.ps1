
Write-Host "STEP 1/?: Download Python-3.11.6 installer..." -ForegroundColor Cyan
if (Test-Path $pythonInstaller) {
    Write-Host "-> python-installer.exe already downloaded."
} else {
    Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.11.6/python-3.11.6-amd64.exe" -OutFile $pythonInstaller
    if (-Not (Test-Path $pythonInstaller)) {
        Write-Host "-> Download failed. EXIT SCRIPT" -ForegroundColor Red
        exit 1
    }
    Write-Host "-> Download succeeded."
}


Write-Host "STEP2/?: Python installation" -ForegroundColor Cyan
Start-Process -FilePath $pythonInstaller -ArgumentList "/quiet InstallAllUsers=0 TargetDir=$pythonDir PrependPath=0" -Wait
# TODO add Get-Command to check installation was really successful, if not add advice to repair python or script to do so
Write-Host "-> Local Python installation completed in $pythonDir"

Write-Host "STEP ?/?: Upgrading pip" -ForegroundColor Cyan
& $pythonExe -m pip install --upgrade pip --no-warn-script-location


Write-Host "STEP ?/?: Installing python requirements..." -ForegroundColor Cyan
$requirementsPath = [System.IO.Path]::Combine($currFolderPath, "..", "requirements.txt")
& $pythonExe -m pip install -r requirements.txt  --no-warn-script-location
