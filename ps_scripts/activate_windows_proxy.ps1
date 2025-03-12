$currFolderPath = Split-Path -Parent $PSCommandPath
$confFile = [System.IO.Path]::Combine($currFolderPath, "..", "conf.json")
$proxy_config = Get-Content -Path $confFile -Raw | ConvertFrom-Json
$ip="127.0.0.1" #$proxy_config.ip
$port="8080" #$proxy_config.port
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings" -Name ProxyEnable -Type DWord -Value 1
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings" -Name ProxyServer -Type String -Value "${ip}:${port}"
