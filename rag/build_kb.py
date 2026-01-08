import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "rag" / "kb.jsonl"

def iter_files():
    # Use docs + research_*.md + README files
    paths = []
    for base in [ROOT / "docs", ROOT]:
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if p.is_dir():
                continue
            if p.name in (".env", ".env.example"):
                continue
            if p.suffix.lower() not in (".md", ".js", ".json"):
                continue
            if "docs" in p.parts or p.name.startswith("research_") or p.name.lower().startswith("readme"):
                paths.append(p)
    return sorted(set(paths))

def chunk_text(text: str, is_md: bool):
    if not is_md:
        return [text[:4000]] if text.strip() else []
    parts = re.split(r"\n(?=#+\s)", text)
    out = []
    for part in parts:
        part = part.strip()
        if len(part) >= 200:
            out.append(part[:4000])
    if not out and text.strip():
        out = [text.strip()[:4000]]
    return out

def guess_type(path: Path) -> str:
    s = str(path).lower()
    if "mashup_examples" in s:
        return "example"
    if "recipe" in s:
        return "recipe"
    if "api" in s:
        return "endpoint"
    if s.endswith(".js"):
        return "code"
    return "rule"

def guess_entity(text: str, path: Path) -> str:
    blob = (text + " " + str(path)).lower()
    if "mashup" in blob:
        return "Mashup"
    if "service" in blob:
        return "Service"
    if "property" in blob:
        return "Property"
    return "Thing"

def keywords(text: str):
    toks = re.findall(r"[A-Za-z][A-Za-z0-9_]{2,}", text.lower())
    common = {"thingworx","thing","things","service","services","mashup","property","properties","create","update","rest","json"}
    toks = [t for t in toks if t not in common]
    seen = set()
    out = []
    for t in toks:
        if t not in seen:
            out.append(t); seen.add(t)
        if len(out) >= 20:
            break
    return out

def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    idx = 0
    with OUT.open("w", encoding="utf-8") as f:
        for p in iter_files():
            txt = p.read_text(encoding="utf-8", errors="ignore")
            chunks = chunk_text(txt, p.suffix.lower() == ".md")
            for c in chunks:
                rec = {
                    "id": f"kb_{idx:06d}",
                    "source_path": str(p.relative_to(ROOT)).replace("\\", "/"),
                    "type": guess_type(p),
                    "entity": guess_entity(c, p),
                    "keywords": keywords(c),
                    "text": c,
                }
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                idx += 1
    print(f"Wrote {idx} chunks -> {OUT}")

if __name__ == "__main__":
    main()
