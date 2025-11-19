Set-StrictMode -Version Latest
$ErrorActionPreference="Stop"
Write-Output "[1] clean"
Remove-Item -Recurse -Force 01_raw_scans,02_structured,03_analysis,04_comparisons,05_strategy,AUDIT,BLOCKER.md -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force 01_raw_scans,02_structured,03_analysis,04_comparisons,05_strategy,AUDIT | Out-Null
Write-Output "[2] scanner"
python agents/scanner_stub.py
Write-Output "[3] structurer"
python agents/structurer.py
Write-Output "[4] analyst"
python agents/analyst.py
Write-Output "[5] comparator"
python agents/comparator.py
Write-Output "[6] strategist"
python agents/strategist.py
Write-Output "[7] auditor"
python agents/auditor.py
Write-Output "[8] cleaner"
python agents/cleaner.py
Write-Output "PASS"
