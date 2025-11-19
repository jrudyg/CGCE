## Common I/O
Inputs: file paths + config JSON. Outputs: files in designated folder + `*.meta.json` with hashes and provenance. Stop Rule: ≤2 loops; else `BLOCKER.md`.

### 1) Scanner
Role: Acquire raw, attributed intel.  
Inputs: `scanner_config.json`, seed URLs/docs.  
Outputs: `01_raw_scans/*.raw.md|.txt|.pdf|.png` + sidecars; `scanner_index.md`.  
Success: ≥10 unique items/topic or `NO_NEW_SIGNALS`; working citations; quotes for paraphrase.  
Handoff → Structurer: `scanner_index.md`.

### 2) Structurer
Role: Normalize to schema + doc summaries.  
Inputs: `01_raw_scans/*`, `02_structured/structurer_schema.json`.  
Outputs: `signals.jsonl`, `signals.csv`, `doc_summaries/*.md`, `structured_manifest.md`.  
Success: 100% schema-valid; each row back-references raw evidence.  
Handoff → Analyst: `structured_manifest.md`.

### 3) Analyst
Role: Findings + SI implications.  
Inputs: `signals.*` + manifest.  
Outputs: `findings.md`, `implications.md`.  
Success: Each finding cites ≥1 evidence row; implications map to SI actions.  
Handoff → Comparator: `analysis_index.md`.

### 4) Comparator
Role: Side-by-side matrices.  
Inputs: `03_analysis/*`, `04_comparisons/comparison_criteria.json`.  
Outputs: `{set}.md`, `{set}.csv`, `comparisons_index.md`.  
Success: ≥80% non-UNKNOWN; legends + criteria definitions.  
Handoff → Strategist: `comparisons_index.md`.

### 5) Strategist
Role: Options, recommendation, risks/mitigations.  
Inputs: `04_comparisons/*`.  
Outputs: `options.md`, `recommendation.md`, `risks_mitigations.md`, `strategy_index.md`.  
Success: Recs cite comparison cells; actions have owner/due/output path.  
Handoff → Auditor: `strategy_index.md`.

### 6) Ruthless Auditor
Role: Detect errors/unsupported claims/vagueness/missing evidence/criteria/hallucinations; produce patch.  
Inputs: `02_*` → `05_*`, rubric file.  
Outputs: `AUDIT/audit_report.md`, `AUDIT/prompt_patch.md`.  
Success: Issues link to file + line; patch atomic/testable.  
Handoff → Cleaner: patch + checklist.

### 7) Cleaner
Role: Apply patch; regenerate corrected artifacts.  
Inputs: `AUDIT/prompt_patch.md`, originals.  
Outputs: `*_cleaned.*`, `AUDIT/fix_log.md`, `AUDIT/diff_summary.md`.  
Success: All critical issues resolved or `WON'T_FIX` with reason; no new violations.
