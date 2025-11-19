#!/usr/bin/env bash
set -euo pipefail
echo "[1] clean"
rm -rf 01_raw_scans 02_structured 03_analysis 04_comparisons 05_strategy AUDIT BLOCKER.md || true
mkdir -p 01_raw_scans 02_structured 03_analysis 04_comparisons 05_strategy AUDIT
echo "[2] scanner"
python agents/scanner_stub.py
echo "[3] structurer"
python agents/structurer.py
echo "[4] analyst"
python agents/analyst.py
echo "[5] comparator"
python agents/comparator.py
echo "[6] strategist"
python agents/strategist.py
echo "[7] auditor"
python agents/auditor.py
echo "[8] cleaner"
python agents/cleaner.py
echo "PASS"
