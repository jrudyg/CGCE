import argparse, os, shutil, glob, datetime, subprocess, sys

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--fixtures", default="tests/fixtures/01_raw_scans_sample")
    ap.add_argument("--outdir", default="01_raw_scans")
    ap.add_argument("--hash_tool", default="tools/hash_sidecar.sh")
    args=ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    idx=os.path.join(args.outdir,"scanner_index.md")
    date=datetime.datetime.utcnow().strftime("%Y%m%d")
    count=0
    for i, fp in enumerate(sorted(glob.glob(os.path.join(args.fixtures,"*.raw.md"))),1):
        slug=os.path.splitext(os.path.basename(fp))[0]
        dst=os.path.join(args.outdir, f"{date}_{slug}_{i:02d}.raw.md")
        shutil.copyfile(fp, dst)
        # sidecar
        if os.name == "nt":
            subprocess.check_call(["powershell","-ExecutionPolicy","Bypass","-File","tools/hash_sidecar.ps1", dst])
        else:
            subprocess.check_call([args.hash_tool, dst])
        # index
        with open(idx,"a",encoding="utf-8") as f:
            f.write(f"- {os.path.basename(dst)} | fixture:{slug}\n")
        count+=1
    print(f"scanner_stub: copied {count} items to {args.outdir}")

if __name__=="__main__":
    main()
