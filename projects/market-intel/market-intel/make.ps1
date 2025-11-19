param([Parameter(Mandatory=$true)][ValidateSet("setup","lint","test","run-week","audit","clean")]$Target)
switch ($Target) {
 "setup" {
   if (-not (Test-Path ".venv")) { python -m venv .venv }
   Write-Output "venv ready"
 }
 "lint" { python -m py_compile agents\*.py tools\*.py }
 "test" {
   powershell -ExecutionPolicy Bypass -File tests\test_pipeline.ps1
 }
 "run-week" {
   python tools\job_orchestrator.py --jobs JOBS\2025W45.jobs.json
 }
 "audit" {
   python agents\auditor.py; python agents\cleaner.py
 }
 "clean" {
   Remove-Item -Recurse -Force 01_raw_scans,02_structured,03_analysis,04_comparisons,05_strategy,AUDIT,BLOCKER.md,.venv -ErrorAction SilentlyContinue
 }
}
