Write-Host "STEP ?/?: Running MITM..." -ForegroundColor Cyan
$mitmdumpExe = [System.IO.Path]::Combine($pythonDir, "Scripts", "mitmdump") # does not work when writing .exe
$mitmJob = Start-Job -ScriptBlock { & $using:mitmdumpExe }
$ip = "127.0.0.1"
$port = 8080
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

Write-Host "STEP ?/?: Enable proxy" -ForegroundColor Cyan
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings" -Name ProxyEnable -Type DWord -Value 1
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings" -Name ProxyServer -Type String -Value "${ip}:${port}"
Write-Host "-> Proxy enabled"
Write-Host "-> IP: $ip"
Write-Host "-> PORT: $port"

Write-Host "STEP?/?: Downloading MITMProxy certificate" -ForegroundColor Cyan
$confFile = [System.IO.Path]::Combine($currFolderPath, "..",  "conf.json")
$config = Get-Content -Path $confFile -Raw | ConvertFrom-Json
$mitmproxy_cert_url = $config.mitmproxy_cert_url
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

Write-Host "STEP?/?:  Adding certificate to the Trusted Root Certification Authorities" -ForegroundColor Cyan
# ERROR while automating it: Workaround is semi-automatic while following the GUI
& $certPath


