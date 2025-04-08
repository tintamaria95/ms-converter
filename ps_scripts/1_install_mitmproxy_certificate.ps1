Write-Host "STEP 4.1/4: Running MITM..." -ForegroundColor Cyan
$mitmdumpExe = [System.IO.Path]::Combine($pythonDir, "Scripts", "mitmdump") # does not work when writing .exe
$mitmJob = Start-Job -ScriptBlock { & $using:mitmdumpExe }

$currFolderPath = Split-Path -Parent $PSCommandPath
$configPath = [System.IO.Path]::Combine($currFolderPath, "..", "conf.json")

if (!(Test-Path $configPath)) {
    Write-Host "-> Path $configPath does not exist"
    exit 1
}

$configContent = Get-Content -Path $configPath -Raw | ConvertFrom-Json
$ip = $configContent.proxy_ip
$port = $configContent.proxy_port
$timeout = 5
$elapsed = 0

while (-not (Test-NetConnection -ComputerName $ip -Port $port -InformationLevel Quiet)) {
    if ($elapsed -ge $timeout) {
        Stop-Job -Job $mitmJob
        Remove-Job -Job $mitmJob
        throw "Error: mitmproxy did not start listening on ${ip}:${port} within ${timeout} seconds."
        exit 1
    }
    Start-Sleep -Seconds 1
    $elapsed++
}
Write-Host "-> mitmproxy is running and listening on ${ip}:${port}"

Write-Host "STEP 4.2/4: Enable proxy" -ForegroundColor Cyan
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings" -Name ProxyEnable -Type DWord -Value 1
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings" -Name ProxyServer -Type String -Value "${ip}:${port}"
Write-Host "-> Proxy enabled"
Write-Host "-> IP: $ip"
Write-Host "-> PORT: $port"

Write-Host "STEP 4.3/4: Downloading MITMProxy certificate" -ForegroundColor Cyan
$mitmproxy_cert_url = $configContent.mitmproxy_cert_url
if (-not $mitmproxy_cert_url) {
    Write-Host "ERROR: Missing required cert URL value in conf.json" -ForegroundColor Red
    exit 1
}
$certPath = [System.IO.Path]::Combine($currFolderPath, "mitmproxy-cert-ca.p12")
try {
    Invoke-WebRequest -Uri $mitmproxy_cert_url -OutFile $certPath -ErrorAction Stop
    Write-Host "-> Saved as: $certPath"    
} catch {
    Write-Host "Download of mitmproxy certificate failed: $_" -ForegroundColor Red
    Write-Host "-> Check if mitmproxy ran correctly and if URL is valid: $mitmproxy_cert_url" -ForegroundColor Red
    exit 1
}

Write-Host "-> Stopping mitmproxy job"
Stop-Job -Id $mitmJob.Id
Remove-Job -Id $mitmJob.Id
Write-Host "-> Disabling proxy"
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings" -Name ProxyEnable -Type DWord -Value 0

Write-Host " "
Write-Host "STEP 4.4/4:  Adding certificate to the Trusted Root Certification Authorities" -ForegroundColor Cyan
# ERROR while automating it: Workaround is semi-automatic while following the GUI
& $certPath
Write-Host "*** IMPORTANT ***"
Write-Host "Certificate importation assistant opens. Follow instructions below:"
Write-Host " "
Write-Host '1) Welcome / Storage location page'
Write-Host '-> Choose "Current User"/"Utilisateur actuel"'
Write-Host '-> [Next]/[Suivant]'
Write-Host '2) You are required to choose a file to import (nothing to change)'
Write-Host '-> [Next]/[Suivant]'
Write-Host '3) You are required to enter private key password: (nothing to change/ leave it blank)'
Write-Host '-> [Next]/[Suivant]'
Write-Host '4) You are required to choose certificate store:'
Write-Host '-> Select "Put certificates in following store /Placer tous les certificats dans le magasin suivant"' -ForegroundColor Magenta
Write-Host '-> [Browse...]/[Parcourir...]' -ForegroundColor Magenta
Write-Host '-> Select "Root store"/"Autorité de certification racines de confinace"' -ForegroundColor Magenta
Write-Host '-> [Next]/[Suivant]'
Write-Host '-> [Finish]/[Terminer]'
Write-Host '-> Validate Importation when windows pops up'