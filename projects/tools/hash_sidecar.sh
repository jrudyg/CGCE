    #!/usr/bin/env bash
    set -euo pipefail
    if [ $# -lt 1 ]; then echo "usage: $0 <file>"; exit 2; fi
    FILE="$1"
    if [ ! -f "$FILE" ]; then echo "not found: $FILE"; exit 3; fi
    HASH="$(python3 - <<'PY'
    import sys,hashlib,json,datetime
    p=sys.argv[1]
    h=hashlib.sha256(open(p,'rb').read()).hexdigest()
    meta={"source_url":"","collected_at":datetime.datetime.utcnow().replace(microsecond=0).isoformat()+"Z","collector":"unknown","hash_sha256":h}
    print(json.dumps(meta))
PY
    "$FILE")"
    echo "$HASH" > "${FILE}.meta.json"
    echo "wrote ${FILE}.meta.json"
