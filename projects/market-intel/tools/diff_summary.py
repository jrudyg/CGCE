import argparse, os, hashlib

def sha256p(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(65536), b''): h.update(b)
    return h.hexdigest()

def walk(d):
    out=[]
    for root,_,files in os.walk(d):
        for fn in files:
            out.append(os.path.relpath(os.path.join(root,fn), d))
    return set(out)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--old", required=True)
    ap.add_argument("--new", required=True)
    ap.add_argument("--out", default="AUDIT/diff_summary.md")
    a=ap.parse_args()
    old,new=a.old,a.new
    oldset, newset = walk(old), walk(new)
    added = sorted(newset-oldset)
    removed = sorted(oldset-newset)
    common = sorted(newset&oldset)
    changed=[]
    for rel in common:
        po, pn = os.path.join(old,rel), os.path.join(new,rel)
        if os.path.isfile(po) and os.path.isfile(pn):
            if sha256p(po)!=sha256p(pn):
                changed.append(rel)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out,'w',encoding='utf-8') as f:
        f.write("# Diff Summary\n\n")
        f.write("## Added\n" + ("\n".join(f"- {x}" for x in added) if added else "- (none)") + "\n\n")
        f.write("## Removed\n" + ("\n".join(f"- {x}" for x in removed) if removed else "- (none)") + "\n\n")
        f.write("## Changed\n" + ("\n".join(f"- {x}" for x in changed) if changed else "- (none)") + "\n")
    print(f"wrote {a.out}")

if __name__=="__main__":
    main()
