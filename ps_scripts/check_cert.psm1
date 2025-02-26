function IsCertExistsInCurrentUserRootStore {
    param (
        [string]$certName
    )
    $cert = Get-ChildItem -Path "Cert:\CurrentUser\Root" | Where-Object { $_.Subject -like "*$certName*" }
    if ($cert) {
        Write-Host "-> Certificate '$certName' is installed."
        return $true
    } else {
        Write-Host "-> Certificate '$certName' is NOT installed."
        return $false
    }
}

Export-ModuleMember -Function IsCertExistsInCurrentUserRootStore