$currFolderPath = Split-Path -Parent $PSCommandPath
$pythonDir = [System.IO.Path]::Combine($currFolderPath, "python")
$pythonInstaller = [System.IO.Path]::Combine($pythonDir, "python-installer.exe")
$pythonExe = [System.IO.Path]::Combine($pythonDir, "python.exe")
$checkCertFile = [System.IO.Path]::Combine($currFolderPath, "check_cert.psm1")

Import-Module $checkCertFile -Force

if (!(Test-Path $pythonDir)) {
    New-Item -ItemType Directory -Path $pythonDir | Out-Null
}

Write-Host "Please wait until the installation finishes, do not close this window !" -ForegroundColor Magenta
Write-Host "STEP 1/4 Python local installation (within directory)" -ForegroundColor Cyan
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

Write-Host " "
Write-Host "STEP 2/4: Upgrading pip" -ForegroundColor Cyan
& $pythonExe -m pip install --upgrade pip --no-warn-script-location

Write-Host " "
Write-Host "STEP 3/4: Installing python requirements..." -ForegroundColor Cyan
$requirementsPath = [System.IO.Path]::Combine($currFolderPath, "..", "requirements.txt")
& $pythonExe -m pip install -r requirements.txt  --no-warn-script-location --quiet

Write-Host " "
Write-Host "STEP 4/4 Checking mitmproxy certificate" -ForegroundColor Cyan
if (IsCertExistsInCurrentUserRootStore -certName "mitmproxy"){
    Write-Host "-> mitmproxy certificate already added to current user root store"
} else {
    Write-Host "-> mitmproxy certificate not found in current user root store"
    Write-Host "-> Proceeding with mitmproxy certificate download/export to store"
    $certInstallationFilePath = [System.IO.Path]::Combine($currFolderPath, "1_install_mitmproxy_certificate.ps1")
    & $certInstallationFilePath
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "Python installation encountered an issue. Stopping execution."  -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "Installation completed!" -ForegroundColor Green