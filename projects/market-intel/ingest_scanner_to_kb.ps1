param()
Write-Host "Running ingest_scanner_to_kb.ps1..." -ForegroundColor Cyan
$scanPath = "01_raw_scans\daily_scans\scan_01.txt"
$kbPath   = "02_structured\knowledge_base.csv"

if (-not (Test-Path $scanPath)) {
    Write-Host "⚠️  No scan file found at $scanPath" -ForegroundColor Yellow
    exit 1
}

# Append sample record if KB empty
if ((Get-Content $kbPath | Measure-Object -Line).Lines -le 1) {
    Add-Content $kbPath "2025-11-07,Geek+,RoboShuttle RS8,Auto-ingest placeholder,,\"Initial scan\",$scanPath,scan_01"
    Write-Host "✅ Added sample record to KB."
} else {
    Write-Host "✅ KB already populated."
}
