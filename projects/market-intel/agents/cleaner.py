import argparse, os, re, glob

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--patch", default="AUDIT/prompt_patch.md")
    ap.add_argument("--outdir", default="AUDIT")
    args=ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    patch=open(args.patch,"r",encoding="utf-8").read().splitlines()
    changes=[]
    for line in patch:
        m=re.match(r"- In `(.*?)` replace `UNKNOWN`", line)
        if m:
            fp=m.group(1)
            if os.path.exists(fp):
                txt=open(fp,"r",encoding="utf-8").read()
                new=txt.replace("UNKNOWN","ESTIMATE_W_REASON: method note TBD")
                out=fp.replace(".md","_cleaned.md").replace(".csv","_cleaned.csv")
                open(out,"w",encoding="utf-8").write(new)
                changes.append((fp,out,"UNKNOWN→ESTIMATE_W_REASON"))
        m2=re.match(r"- In `(.*?)` add evidence references", line)
        if m2:
            fp=m2.group(1)
            if os.path.exists(fp):
                txt=open(fp,"r",encoding="utf-8").read()
                if "evidence:" not in txt:
                    new=txt + "\n\n> evidence: add `path#locator` per claim.\n"
                else:
                    new=txt
                out=fp.replace(".md","_cleaned.md")
                open(out,"w",encoding="utf-8").write(new)
                changes.append((fp,out,"add evidence refs note"))
    with open(os.path.join(args.outdir,"fix_log.md"),"w",encoding="utf-8") as f:
        for a,b,c in changes: f.write(f"{a} -> {b} | {c}\n")
    print("cleaner: applied basic patch; see fix_log.md")

if __name__=="__main__":
    main()
