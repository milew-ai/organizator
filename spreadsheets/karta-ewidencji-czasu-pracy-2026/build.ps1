<#
.SYNOPSIS
    Buduje arkusz „Karta ewidencji czasu pracy" z generatora Pythona.

.DESCRIPTION
    Pełny potok: gen_karta.py (.fods) -> LibreOffice (--convert-to xlsx)
    -> postprocess_xlsx.py (poprawki nagłówka/wydruku/validacji).
    Każdy krok sprawdza kod wyjścia i przerywa budowanie przy błędzie.

.PARAMETER Year
    Rok arkusza. Domyślnie 2026.

.PARAMETER Soffice
    Ścieżka do soffice.exe. Domyślnie instalacja LibreOffice w Program Files.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\build.ps1
    powershell -ExecutionPolicy Bypass -File .\build.ps1 -Year 2027
#>
param(
    [int]$Year = 2026,
    [string]$Soffice = "C:\Program Files\LibreOffice\program\soffice.exe"
)

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$name = "Karta_ewidencji_czasu_pracy_$Year"
$fods = Join-Path $here "$name.fods"
$xlsx = Join-Path $here "$name.xlsx"
$profile = Join-Path $env:TEMP ("loprof_" + [guid]::NewGuid().ToString("N"))

# Uruchamia polecenie i pilnuje kodu wyjścia (Windows PowerShell 5.1 sam tego nie robi).
function Invoke-Checked {
    param([string]$File, [string[]]$Arguments)
    & $File @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Polecenie nie powiodło się (kod $LASTEXITCODE): $File $($Arguments -join ' ')"
    }
}

try {
    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        throw "Brak Pythona w PATH. Zainstaluj Python 3.8+ i spróbuj ponownie."
    }
    if (-not (Test-Path $Soffice)) {
        throw "Nie znaleziono LibreOffice: $Soffice. Podaj ścieżkę parametrem -Soffice."
    }

    # 1) Generator -> .fods
    Invoke-Checked python @((Join-Path $here "gen_karta.py"), "--year", "$Year", "--out", $fods)

    # 2) Konwersja do .xlsx (osobny profil, żeby nie psuć działającej instancji LO)
    Remove-Item $xlsx -Force -ErrorAction SilentlyContinue
    $profileUrl = "file:///" + ($profile -replace '\\', '/')
    Invoke-Checked $Soffice @("--headless", "-env:UserInstallation=$profileUrl",
                              "--convert-to", "xlsx", "--outdir", $here, $fods)
    for ($i = 0; $i -lt 30 -and -not (Test-Path $xlsx); $i++) { Start-Sleep -Milliseconds 500 }
    if (-not (Test-Path $xlsx)) { throw "Konwersja do .xlsx nie powiodła się: $xlsx" }

    # 3) Poprawki powierzchniowe
    Invoke-Checked python @((Join-Path $here "postprocess_xlsx.py"), $xlsx)

    Write-Host "Gotowe: $xlsx"
}
finally {
    Remove-Item $profile -Recurse -Force -ErrorAction SilentlyContinue
}
