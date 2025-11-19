## Scanner — Bootstrap
Role: Scanner (raw, attributed items; minimal descriptor).  
Inputs: `[TOPIC_LIST]`, `[ENTITY_LIST]`, `[START_DATE]–[END_DATE]`.  
Write raw to `/market-intel/01_raw_scans/YYYYMMDD_<slug>_<nn>.raw.md|.pdf|.png` + sidecar `.meta.json`. Append to `scanner_index.md`.  
Stop: if <10 items/topic → one targeted pass on top 3 entities → else `NO_NEW_SIGNALS`.  
Success: working links; unique items; quotes for paraphrase.

## Structurer — Bootstrap
Role: Structurer (normalize + summaries).  
Schema fields: `entity, product, event_type, event_date, claim, evidence_path, evidence_locator, confidence, market_segment, geography, impact_area`.  
Outputs: `02_structured/signals.jsonl`, `signals.csv`, `doc_summaries/*.md`, `structured_manifest.md`.  
Stop: one normalize + one validation pass; persistent schema errors → `BLOCKER.md`.  
Success: 100% schema-valid; complete back-references.

## Comparator — Bootstrap
Role: Comparator (matrices).  
Inputs: `03_analysis/findings.md`, `03_analysis/implications.md`, `02_structured/signals.*`.  
Criteria JSON: `throughput, reliability, install_time, service_coverage, integration_effort, TCO_band, references, lead_time, SLA_terms`.  
Outputs: `04_comparisons/[SET_SLUG].md` + `.csv`; include legend + assumptions.  
Stop: one build + one gap-fill pass.  
Success: ≥80% non-UNKNOWN cells; clear legends/definitions.
