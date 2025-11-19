## Purpose
Platform-neutral agentic pipeline for ongoing market intelligence in parcel & e-fulfillment, tailored to a systems integrator (SI).

## Scope
Entities: vendors, integrators, robotics/AMR, sortation, WES/WCS/WMS, AS/RS, conveyors, pick/pack, labeling, parcel injection.  
Signals: launches, partnerships, reference sites, pricing/terms signals, lead times, failures/recalls, funding, M&A, wins/losses, SLAs, support coverage.  
Sources: official sites, filings, technical docs, release notes, RFP/RFQ artifacts the SI possesses, conference agendas, job postings.

## Lifecycle (weekly)
1) Scanner → `01_raw_scans/`
2) Structurer → `02_structured/`
3) Analyst → `03_analysis/`
4) Comparator → `04_comparisons/`
5) Strategist → `05_strategy/`
6) Ruthless Auditor → `AUDIT/`
7) Cleaner → corrected `*_cleaned.*` + diffs

## Parallelization
Scanner per topic/entity, Structurer per batch, Analyst per theme, Comparator per set, Strategist single. All agents use file-path inputs and write deterministic outputs with checksums.

## Evidence & Reproducibility
Every claim cites file path + locator; unknowns = `UNKNOWN`. Provide machine-readable + human-readable outputs. Sidecar `*.meta.json`:
```json
{"source_url":"", "collected_at":"YYYY-MM-DDThh:mmZ", "collector":"<agent>", "hash_sha256":""}
```

## Naming
`YYYYMMDD_slug_nn.*`

## Stop Rules
Each agent ≤2 loops unless criteria failing; else emit `BLOCKER.md` with missing inputs.

## Audit Loop
Auditor flags: errors, unsupported claims, vague language, missing evidence/criteria, hallucinations. Cleaner applies patch; produce `*_cleaned.*` + diff notes.
