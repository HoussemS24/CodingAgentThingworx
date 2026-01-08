import argparse
import hashlib
import json
import math
import pickle
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "rag" / "index.pkl"
CACHE_DIR = ROOT / "cache"

def tokenize(text: str):
    return re.findall(r"[A-Za-z][A-Za-z0-9_]{2,}", text.lower())[:2000]

def load_index():
    return pickle.loads(INDEX.read_bytes())

def query(prompt: str, top_k: int = 6):
    idx = load_index()
    idf = idx["idf"]; inv = idx["inv"]; norms = idx["norms"]; meta = idx["meta"]

    q_tf = Counter(tokenize(prompt))
    q_vec = {t: (1 + math.log(c)) * idf[t] for t, c in q_tf.items() if t in idf}
    q_norm = math.sqrt(sum(w*w for w in q_vec.values())) or 1.0

    scores = defaultdict(float)
    for t, qw in q_vec.items():
        for doc_i, dw in inv.get(t, []):
            scores[doc_i] += qw * dw

    ranked = sorted(scores.items(), key=lambda x: x[1] / (norms[x[0]] * q_norm), reverse=True)[:top_k]
    out = []
    for doc_i, s in ranked:
        r = dict(meta[doc_i])
        r["score"] = float(s / (norms[doc_i] * q_norm))
        out.append(r)
    return out

def cached(prompt: str, top_k: int):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    h = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16]
    p = CACHE_DIR / f"rag_{h}_k{top_k}.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    res = query(prompt, top_k)
    p.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    return res

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--top-k", type=int, default=6)
    a = ap.parse_args()
    print(json.dumps(cached(a.prompt, a.top_k), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
