import argparse, os, glob

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--rubric", default="00_instructions/rubric_success_criteria.md")
    ap.add_argument("--outdir", default="AUDIT")
    args=ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    issues=[]
    for fp in glob.glob("03_analysis/*.md")+glob.glob("04_comparisons/*.md")+glob.glob("05_strategy/*.md"):
        txt=open(fp,"r",encoding="utf-8").read()
        if "UNKNOWN" in txt:
            issues.append((fp,"MEDIUM","UNKNOWN cells present"))
        if ("Recommendation" in txt or "Findings" in txt) and ("evidence:" not in txt and "EVIDENCED" not in txt):
            issues.append((fp,"HIGH","Missing explicit evidence refs"))
    with open(os.path.join(args.outdir,"audit_report.md"),"w",encoding="utf-8") as f:
        f.write("# Audit Report\n\n")
        if not issues: f.write("- No issues found (basic checks)\n")
        for fp,sev,msg in issues:
            f.write(f"- [{sev}] {fp}: {msg}\n")
    with open(os.path.join(args.outdir,"prompt_patch.md"),"w",encoding="utf-8") as f:
        f.write("# Prompt Patch\n\n")
        for fp,sev,msg in issues:
            if "UNKNOWN" in msg:
                f.write(f"- In `{fp}` replace `UNKNOWN` cells with `ESTIMATE_W_REASON` including method note, or provide `EVIDENCED: path#locator`.\n")
            if "Missing explicit evidence" in msg:
                f.write(f"- In `{fp}` add evidence references for each claim using `path#locator` notation.\n")
    print("auditor: audit_report + prompt_patch written")

if __name__=="__main__":
    main()
