## Global Rubric (EXCELLENT / GOOD / LIMITED / MISSING)

| Dimension | EXCELLENT | GOOD | LIMITED | MISSING |
|---|---|---|---|---|
| Evidence Traceability | Every claim cites file path + locator + hash | Minor gaps | Many missing | None |
| Reproducibility | Steps + checksums | Mostly reproducible | Manual gaps | Not reproducible |
| Clarity/Specificity | SI-actionable | Mostly specific | Mixed | Vague |
| Assumptions/Unknowns | Explicit, bounded | Mostly explicit | Partly implicit | Hidden |
| Consistency | Names/schemas/legends consistent | Minor drift | Several inconsistencies | Incoherent |
| Error Rate | No material errors | Minor | Some material | Frequent |

### Per-Agent Checks
Scanner: count target met; working sources; quotes present.  
Structurer: 100% schema-valid; back-references.  
Analyst: findings ↔ evidence; implications map to SI tasks.  
Comparator: ≥80% non-UNKNOWN; legend + definitions.  
Strategist: recs cite cells; actions (owner/due/path).  
Auditor: issues have severity + location + rule; patch atomic.  
Cleaner: critical issues closed; diff summary present.

### Pass/Fail
Release only if all agents score **GOOD** or **EXCELLENT**; any **MISSING** halts release.
