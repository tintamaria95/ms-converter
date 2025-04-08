function IsCertExistsInCurrentUserRootStore {
    param (
        [string]$certName
    )
    $cert = Get-ChildItem -Path "Cert:\CurrentUser\Root" | Where-Object { $_.Subject -like "*$certName*" }
    if ($cert) {
        return $true
    } else {
        return $false
    }
}

Export-ModuleMember -Function IsCertExistsInCurrentUserRootStore