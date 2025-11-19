
---

## 4. Schema Governance
- One global, versioned `schemas/` repo.
- No silent changes: bump schema version + run canary eval.
- Prevents drift and keeps Planner ↔ Codex contracts honest.

---

## 5. Model, Cost, and Performance
- Model selection: **Accuracy → Cost**.
- Proof-of-concept on **cost-free** surfaces; scale only after success.
- Prompt caching allowed if it improves value without risk.
- Chunk data as needed; avoid monolithic prompts.

---

## 6. Evaluation & QA
- Evals required before shipping any tool.
- Measure: schema correctness, functional success, edge-case handling, security assertions.
- Canary evals on prompt, tool, or schema changes.
- Automated, reproducible, versioned with the code.

---

## 7. Production Hardening
Mandatory for every tool call:
- Retries
- Timeouts
- Idempotency
**Why it matters:** prevents cascade failures, hangs, or duplicate side effects.

PII redaction: optional, not default.

---

## 8. Observability & Monitoring
Dashboards (minimal set, high value):
- Usage
- Cost
- Latency
- Tool-error rate

Logs captured for debugging and governance.

---

## 9. Safety & Governance
- No free-form Planner → Codex handoffs without schema.
- No unbounded tool loops.
- Any schema, prompt, or tool change → version bump + canary eval.
- Keep instructions concise, deterministic, and security-aware.

---

## 10. Roadmap Features
Adopt when high value + low complexity:
- GPT Actions (direct system integrations)
- Agents (multi-tool orchestration)
- MCP servers for structured tool ecosystems
- Realtime API only when voice/streaming UX is required

---

## 11. Build Loop (Repeatable)
1. Plan (Planner decomposes task)
2. Spec (Schemas and tool list)
3. Implement (Codex + tests)
4. Evaluate (automated)
5. Ship (canary)
6. Observe (dashboards)
7. Iterate
