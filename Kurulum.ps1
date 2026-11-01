param([string]$Python)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (-not (Test-Path '.venv\Scripts\python.exe')) {
    if (-not $Python) { $Python = (Get-Command python -ErrorAction Stop).Source }
    & $Python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Python 3.12 x64 gerekli. -Python ile python.exe yolunu belirtin.' }
}
& '.\.venv\Scripts\python.exe' -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Paket kurulumu basarisiz.' }
New-Item -ItemType Directory -Force models | Out-Null
if (-not (Test-Path 'models\vosk-model-small-tr-0.3')) {
    $zip = Join-Path $PSScriptRoot 'models\turkce.zip'
    Invoke-WebRequest 'https://alphacephei.com/vosk/models/vosk-model-small-tr-0.3.zip' -OutFile $zip
    Expand-Archive -LiteralPath $zip -DestinationPath (Join-Path $PSScriptRoot 'models') -Force
    Remove-Item -LiteralPath $zip
}
Write-Host 'Kurulum tamamlandi. Baslat.cmd dosyasini acin.'
