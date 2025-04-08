
Write-Host "STEP 1.1/4: Download Python-3.11.6 installer..." -ForegroundColor Cyan
if (Test-Path $pythonInstaller) {
    Write-Host "-> python-installer.exe already downloaded."
} else {
    Write-Host "-> Downloading python-installer.exe."
    Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.11.6/python-3.11.6-amd64.exe" -OutFile $pythonInstaller
    if (-Not (Test-Path $pythonInstaller)) {
        Write-Host "-> Download failed." -ForegroundColor Red
        exit 1
    }
    Write-Host "-> Download succeeded."
}


Write-Host "STEP 1.2/4:: Installing Python. Please wait and do not close this window..." -ForegroundColor Cyan
Start-Process -FilePath $pythonInstaller -ArgumentList "/quiet InstallAllUsers=0 TargetDir=`"$pythonDir`" PrependPath=0" -Wait

if ( -Not(Get-Command $pythonExe -ErrorAction SilentlyContinue)){
    Write-Host "Python installation did not succeed, please use GUI and select `"Repair Python`""
    Start-Process -FilePath $pythonInstaller -ArgumentList "Repair"  -Wait
} 

if ( Get-Command $pythonExe -ErrorAction SilentlyContinue){
    Write-Host "-> Local Python installation completed in $pythonDir"
} else {
    Write-Host "-> Local Python installation did not complete in $pythonDir"
    exit 1
}


