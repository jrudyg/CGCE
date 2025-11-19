import argparse, json, os

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--signals", default="02_structured/signals.jsonl")
    ap.add_argument("--outdir", default="03_analysis")
    args=ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    findings=[]
    with open(args.signals,"r",encoding="utf-8") as f:
        for i,line in enumerate(f,1):
            s=json.loads(line)
            findings.append(f"- [{i}] {s['entity']} — {s['claim']} (evidence: {s['evidence_path']}#{s['evidence_locator']})")
    with open(os.path.join(args.outdir,"findings.md"),"w",encoding="utf-8") as f:
        f.write("# Findings\n\n" + ("\n".join(findings) if findings else "- NONE") + "\n")
    implications=["- Check integration impact (WES/WCS).","- Validate lead times with vendor rep.","- Assess retrofit vs greenfield fit."]
    with open(os.path.join(args.outdir,"implications.md"),"w",encoding="utf-8") as f:
        f.write("# Implications\n\n"+ "\n".join(implications) + "\n")
    with open(os.path.join(args.outdir,"analysis_index.md"),"w",encoding="utf-8") as f:
        f.write("# Analysis Index\n\n- comparable_sets: AMR_vendors_demo\n")
    print("analyst: findings + implications generated")

if __name__=="__main__":
    main()
