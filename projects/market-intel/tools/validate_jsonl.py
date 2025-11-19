import argparse, json, sys

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--schema", required=True)
    ap.add_argument("--input", required=True)
    args = ap.parse_args()

    schema = json.load(open(args.schema, "r", encoding="utf-8"))
    required = set(schema.get("required", []))
    fields = set(schema.get("fields", []))
    ok = True
    with open(args.input, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line: 
                print(f"[L{i}] empty line"); ok=False; continue
            try:
                obj = json.loads(line)
            except Exception as e:
                print(f"[L{i}] invalid json: {e}"); ok=False; continue
            miss = [k for k in required if k not in obj or (isinstance(obj[k], str) and not obj[k].strip())]
            extr = [k for k in obj.keys() if k not in fields]
            if miss:
                print(f"[L{i}] missing required: {','.join(miss)}"); ok=False
            if extr:
                print(f"[L{i}] warning extra fields: {','.join(extr)}")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
