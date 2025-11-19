.PHONY: setup lint test run-week audit clean
PY:=python

setup:
	@echo "python: $$(python --version)"
	@test -d .venv || python -m venv .venv
	@. .venv/bin/activate; echo "venv ready"

lint:
	@$(PY) -m py_compile agents/*.py tools/*.py

test:
	@chmod +x tools/hash_sidecar.sh tests/test_pipeline.sh || true
	@$(PY) tools/validate_jsonl.py --schema 02_structured/structurer_schema.json --input tests/schema_samples/valid_signals.jsonl || true
	@./tests/test_pipeline.sh

run-week:
	@$(PY) tools/job_orchestrator.py --jobs JOBS/2025W45.jobs.json

audit:
	@$(PY) agents/auditor.py && $(PY) agents/cleaner.py

clean:
	@rm -rf 01_raw_scans 02_structured 03_analysis 04_comparisons 05_strategy AUDIT BLOCKER.md .venv
