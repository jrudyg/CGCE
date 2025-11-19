import argparse, json, subprocess, sys, os, datetime

def run(cmd):
    print(">>", " ".join(cmd))
    return subprocess.call(cmd)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--jobs", required=True)
    args=ap.parse_args()
    jobs=json.load(open(args.jobs,"r",encoding="utf-8"))
    logp=f"JOBS/{os.path.basename(args.jobs)}.log"
    os.makedirs("JOBS", exist_ok=True)
    with open(logp,"a",encoding="utf-8") as log:
        for j in jobs:
            ts=datetime.datetime.utcnow().isoformat()+"Z"
            log.write(f"[{ts}] START {j['task']} by {j['agent']}\n")
            if any(not os.path.exists(p) for p in j.get("inputs",[])):
                open("BLOCKER.md","w").write(f"Missing inputs for {j['task']}: {j.get('inputs')}\n")
                log.write(f"[{ts}] BLOCKER {j['task']}\n"); print("BLOCKER"); sys.exit(1)
            code = run(j["command"])
            ts2=datetime.datetime.utcnow().isoformat()+"Z"
            status="OK" if code==0 else f"ERR({code})"
            log.write(f"[{ts2}] END {j['task']} {status}\n")
            if code!=0: sys.exit(code)
    print("jobs complete")

if __name__=="__main__":
    main()
