print("Running validator.py...")
import csv, sys, os
kb = os.path.join("02_structured","knowledge_base.csv")
if not os.path.exists(kb):
    print("❌ KB not found"); sys.exit(1)
with open(kb, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)
valid = [r for r in rows if all([r.get("date"), r.get("company"), r.get("product")])]
print(f"✅ Valid rows: {len(valid)} / {len(rows)}")
