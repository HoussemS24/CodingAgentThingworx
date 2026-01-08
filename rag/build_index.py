import json
import math
import pickle
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KB = ROOT / "rag" / "kb.jsonl"
OUT = ROOT / "rag" / "index.pkl"

def tokenize(text: str):
    return re.findall(r"[A-Za-z][A-Za-z0-9_]{2,}", text.lower())[:2000]

def main():
    docs = []
    df = Counter()

    for line in KB.read_text(encoding="utf-8").splitlines():
        rec = json.loads(line)
        toks = tokenize(rec["text"])
        docs.append((rec, toks))
        for t in set(toks):
            df[t] += 1

    N = len(docs)
    idf = {t: math.log((N + 1) / (c + 1)) + 1.0 for t, c in df.items()}

    inv = defaultdict(list)
    norms = []
    meta = []

    for i, (rec, toks) in enumerate(docs):
        tf = Counter(toks)
        vec = {t: (1 + math.log(c)) * idf.get(t, 0.0) for t, c in tf.items()}
        n = math.sqrt(sum(w*w for w in vec.values())) or 1.0
        norms.append(n)
        meta.append({k: rec[k] for k in ("id","source_path","type","entity","keywords","text")})
        for t, w in vec.items():
            if w:
                inv[t].append((i, w))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(pickle.dumps({"idf": idf, "inv": dict(inv), "norms": norms, "meta": meta}))
    print(f"Indexed {N} chunks -> {OUT}")

if __name__ == "__main__":
    main()
