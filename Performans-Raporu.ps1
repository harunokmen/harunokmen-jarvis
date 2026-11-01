$ErrorActionPreference = 'Stop'
$report = [ordered]@{ Tarih = (Get-Date).ToString('o'); Hatalar = @() }
try {
    $report.Sistem = Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version,TotalVisibleMemorySize,FreePhysicalMemory,LastBootUpTime
    $report.Islemci = Get-CimInstance Win32_Processor | Select-Object Name,LoadPercentage
    $report.Baslangic = Get-CimInstance Win32_StartupCommand | Select-Object Name,Location
} catch { $report.Hatalar += $_.Exception.Message }
try {
    $report.Diskler = Get-PSDrive -PSProvider FileSystem | Select-Object Name,Used,Free
    $report.BellekKullananlar = Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 15 ProcessName,@{n='RAM_MB';e={[math]::Round($_.WorkingSet64/1MB)}}
    $report.GucPlani = (& powercfg.exe /getactivescheme 2>&1 | Out-String).Trim()
} catch { $report.Hatalar += $_.Exception.Message }
$report | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'performans-raporu.json') -Encoding UTF8
Write-Host 'Rapor kaydedildi. Sistem ayarlari degistirilmedi.'
