import argparse, json, os, re, csv, subprocess, sys, glob

def first_sentence(txt):
    import re
    m=re.split(r'(?<=[.!?])\s+', txt.strip(), maxsplit=1)
    return m[0] if m else txt.strip()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--inputs", default="01_raw_scans/*.raw.md")
    ap.add_argument("--schema", default="02_structured/structurer_schema.json")
    ap.add_argument("--outdir", default="02_structured")
    args=ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    rows=[]
    for path in sorted(glob.glob(args.inputs)):
        with open(path,"r",encoding="utf-8") as f:
            lines=f.readlines()
        title=lines[0].strip() if lines else os.path.basename(path)
        claim=first_sentence("".join(lines[1:]) or title)
        row={
            "entity": re.sub(r'[^A-Za-z0-9]+','_', title.split(" ")[0]).strip("_") or "UNKNOWN",
            "product": "UNKNOWN",
            "event_type": "unspecified",
            "event_date": "UNKNOWN",
            "claim": claim[:280],
            "evidence_path": path,
            "evidence_locator": "L2-L5" if len(lines)>=5 else f"L1-L{max(1,len(lines))}",
            "confidence": "low",
            "market_segment": "parcel/e-fulfillment",
            "geography": "UNKNOWN",
            "impact_area": "UNKNOWN"
        }
        rows.append(row)

    jsonl=os.path.join(args.outdir,"signals.jsonl")
    with open(jsonl,"w",encoding="utf-8") as f:
        for r in rows: f.write(json.dumps(r,ensure_ascii=False)+"\n")

    csvp=os.path.join(args.outdir,"signals.csv")
    with open(csvp,"w",encoding="utf-8",newline="") as f:
        if rows:
            w=csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader(); w.writerows(rows)

    os.makedirs(os.path.join(args.outdir,"doc_summaries"), exist_ok=True)
    for r in rows:
        slug=os.path.basename(r["evidence_path"]).replace(".raw.md","")
        with open(os.path.join(args.outdir,"doc_summaries", f"{slug}.md"),"w",encoding="utf-8") as f:
            f.write(f"# {slug}\n\n- Entity: {r['entity']}\n- Event: {r['event_type']}\n- Claim: {r['claim']}\n- Evidence: {r['evidence_path']}#{r['evidence_locator']}\n")

    manifest=os.path.join(args.outdir,"structured_manifest.md")
    with open(manifest,"w",encoding="utf-8") as f:
        f.write(f"# Structured Manifest\n\n- rows: {len(rows)}\n")

    # validate
    code=subprocess.call([sys.executable,"tools/validate_jsonl.py","--schema",args.schema,"--input",jsonl])
    if code!=0:
        open("BLOCKER.md","w",encoding="utf-8").write("Structurer schema validation failed\n")
        sys.exit(code)
    print(f"structurer: wrote {jsonl}, {csvp}, summaries, manifest")

if __name__=="__main__":
    main()
