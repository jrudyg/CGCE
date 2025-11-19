## Objective
Operate a weekly, parallelized market-intel pipeline for a systems integrator (parcel & e-fulfillment). Produce auditable artifacts for design, estimating, delivery, and strategy.

## Weekly Cadence
1) Plan (Mon AM): update `scanner_config.json`, `comparison_criteria.json`.
2) Collect (Mon–Tue): run **Scanner** per topic/entity in parallel; check `01_raw_scans/scanner_index.md` (≥10 items/topic or `NO_NEW_SIGNALS`).
3) Structure (Tue PM): run **Structurer**; validate schema; if errors → `BLOCKER.md`.
4) Analyze (Wed): run **Analyst**; ensure each finding cites evidence row(s).
5) Compare (Thu AM): run **Comparator**; target ≥80% non-UNKNOWN cells.
6) Strategize (Thu PM): run **Strategist**; produce options, recommendation, risks/mitigations with owners and due dates.
7) Audit & Clean (Fri): **Ruthless Auditor** issues → **Cleaner** applies patch; generate `*_cleaned.*`, `AUDIT/fix_log.md`, `AUDIT/diff_summary.md`.

## Parallelization
- Scanner: 1 worker/topic or entity
- Structurer: 1 worker per 20–30 raw items
- Analyst: 1 worker/theme (AMR, WES, AS/RS)
- Comparator: 1 worker/comparison set
- Strategist: single owner aggregation
- Track with `JOBS/<week>.jobs.json`

## Storage & Provenance
- Use date prefixes `YYYYMMDD_slug_nn.ext`.
- Sidecar `*.meta.json` with SHA-256 for each artifact.
- Keep `CHANGELOG.md` per week; optional weekly subfolders (`2025W45/…`).

## Audit Handoff
- Provide `strategy_index.md` paths for audit.
- Auditor flags: errors, unsupported claims, vagueness, missing evidence/criteria, hallucinations.
- Cleaner applies `AUDIT/prompt_patch.md` precisely; log diffs.

## Release Gate
- Ship only if rubric in `00_instructions/rubric_success_criteria.md` shows **GOOD/EXCELLENT** across all agents; any **MISSING** → stop.

## Recovery
- If any agent emits `BLOCKER.md`, halt downstream; list missing inputs/owner; fix and re-run.

## Minimal Tooling
- Python 3.10+, POSIX shell or PowerShell, checksum utility (built into scripts), text editor.
