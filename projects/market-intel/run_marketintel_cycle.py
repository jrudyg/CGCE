print("Running run_marketintel_cycle.py...")
import datetime, csv, os, json
root = os.getcwd()
kb = os.path.join(root,"02_structured","knowledge_base.csv")
outdir = os.path.join(root,"03_analysis","weekly_notes")
os.makedirs(outdir, exist_ok=True)
ts = datetime.date.today().isoformat()
out = os.path.join(outdir, f"weekly_{ts}.md")
with open(kb, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)
md = [f"# Weekly Notes — Auto summary for {ts}", ""]
for r in rows:
    md.append(f"- {r['date']} {r['company']} {r['product']}: {r['headline']}")
open(out,"w",encoding="utf-8").write("\n".join(md))
print(f"✅ Created {out}")
