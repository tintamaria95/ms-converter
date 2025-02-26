$currFolderPath = Split-Path -Parent $PSCommandPath
$pythonDir = [System.IO.Path]::Combine($currFolderPath, "python")
$pythonInstaller = [System.IO.Path]::Combine($pythonDir, "python-installer.exe")
$pythonExe = [System.IO.Path]::Combine($pythonDir, "python.exe")
$checkCertFile = [System.IO.Path]::Combine($currFolderPath, "check_cert.psm1")

Import-Module $checkCertFile -Force

if (!(Test-Path $pythonDir)) {
    New-Item -ItemType Directory -Path $pythonDir | Out-Null
}

Write-Host "STEP ?/? Checking python installation" -ForegroundColor Cyan
if ( Get-Command $pythonExe -ErrorAction SilentlyContinue){
    Write-Host "-> Python aleady installed"
} else {
    Write-Host "-> Python not installed"
    $pythonInstallationFilePath = [System.IO.Path]::Combine($currFolderPath, "0_install_python.ps1")
    & $pythonInstallationFilePath
}


Write-Host "STEP ?? Checking mitmproxy installation" -ForegroundColor Cyan
$mitmdumpExe = [System.IO.Path]::Combine($pythonDir, "Scripts", "mitmdump.exe")
if ( Get-Command $mitmdumpExe -ErrorAction SilentlyContinue){
    Write-Host "-> mitmproxy already installed"
} else {
    Write-Host "-> mitmproxy not installed"
    Write-Host "-> Proceeding with mitmproxy installation using pip"
    & $pythonExe -m pip install mitmproxy
}

Write-Host "STEP ?? Checking mitmproxy certificate" -ForegroundColor Cyan
if (IsCertExistsInCurrentUserRootStore -certName "mitmproxy"){
    Write-Host "-> mitmproxy certificate already added to current user root store"
} else {
    Write-Host "-> mitmproxy certificate not found in current user root store"
    Write-Host "-> Proceeding with mitmproxy certificate download/export to store"
    $certInstallationFilePath = [System.IO.Path]::Combine($currFolderPath, "1_install_mitmproxy_certificate.ps1")
    & $certInstallationFilePath
}

Write-Host "STEP Installation completed!" -ForegroundColor Green


# TODO: 
# 1) install mitm and requirements
# check if cert in auth store if not continue, else stop
# 1bis)  run mitm
# 2) Set proxy  -> proxy_set
# 3) Goto cert url and download cert (cannot do it without mitm active) -> step2_2 done
# 4) install cert in auth store
# 5) disable proxy / stop mitm
# 6) log user as installation is finished

# need for condition if already installed

