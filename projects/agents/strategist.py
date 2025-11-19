import argparse, os

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--comparisons", default="04_comparisons/AMR_vendors_demo.md")
    ap.add_argument("--outdir", default="05_strategy")
    args=ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    with open(os.path.join(args.outdir,"options.md"),"w",encoding="utf-8") as f:
        f.write("# Options\n\n- A: Pilot with Vendor X in small cell\n- B: RFP to top 2 vendors\n- C: Defer pending lead-time clarity\n")
    with open(os.path.join(args.outdir,"recommendation.md"),"w",encoding="utf-8") as f:
        f.write("# Recommendation\n\n- Proceed with Option B; cite cells in comparisons file for throughput/reliability.\n")
    with open(os.path.join(args.outdir,"risks_mitigations.md"),"w",encoding="utf-8") as f:
        f.write("# Risks & Mitigations\n\n- Lead time risk → early PO; - Integration risk → sandbox WES\n")
    with open(os.path.join(args.outdir,"strategy_index.md"),"w",encoding="utf-8") as f:
        f.write("# Strategy Index\n\n- options.md\n- recommendation.md\n- risks_mitigations.md\n")
    print("strategist: outputs generated")

if __name__=="__main__":
    main()
