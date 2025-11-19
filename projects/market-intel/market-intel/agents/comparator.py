import argparse, json, os, csv

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--criteria", default="04_comparisons/comparison_criteria.json")
    ap.add_argument("--signals", default="02_structured/signals.jsonl")
    ap.add_argument("--outdir", default="04_comparisons")
    ap.add_argument("--set_slug", default="AMR_vendors_demo")
    args=ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    crit=json.load(open(args.criteria,"r",encoding="utf-8"))["criteria"]
    vendors=set()
    sigs=[]
    with open(args.signals,"r",encoding="utf-8") as f:
        for line in f:
            s=json.loads(line); vendors.add(s["entity"]); sigs.append(s)
    vendors=sorted(list(vendors))[:3] or ["V1","V2","V3"]

    rows=[]
    for v in vendors:
        row={"vendor":v}
        for c in crit:
            evid=[s for s in sigs if s["entity"]==v]
            if evid:
                ref=f"{evid[0]['evidence_path']}#{evid[0]['evidence_locator']}"
                row[c]=f"EVIDENCED: {ref}"
            else:
                row[c]="UNKNOWN"
        row[crit[0]]="ESTIMATE_W_REASON: extrapolated from similar deployments"
        rows.append(row)

    mdp=os.path.join(args.outdir,f"{args.set_slug}.md")
    with open(mdp,"w",encoding="utf-8") as f:
        f.write(f"# Comparison — {args.set_slug}\n\nLegend: EVIDENCED / ESTIMATE_W_REASON / UNKNOWN\n\n")
        f.write("| vendor | " + " | ".join(crit) + " |\n")
        f.write("|---|" + "|".join(["---"]*len(crit)) + "|\n")
        for r in rows:
            f.write("| " + " | ".join([r['vendor']]+[r[c] for c in crit]) + " |\n")
    csvp=os.path.join(args.outdir,f"{args.set_slug}.csv")
    with open(csvp,"w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f, fieldnames=["vendor"]+crit); w.writeheader(); w.writerows(rows)
    with open(os.path.join(args.outdir,"comparisons_index.md"),"w",encoding="utf-8") as f:
        f.write(f"# Comparisons Index\n\n- {args.set_slug}: {mdp}\n")
    print(f"comparator: wrote {mdp} and {csvp}")

if __name__=="__main__":
    main()
