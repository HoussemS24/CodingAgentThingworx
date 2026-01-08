import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "spec" / "schema.json").read_text(encoding="utf-8-sig"))

def validate(spec: Dict[str, Any]) -> List[str]:
    v = Draft202012Validator(SCHEMA)
    errs = sorted(v.iter_errors(spec), key=lambda e: e.path)
    out = []
    for e in errs:
        loc = ".".join(map(str, e.path)) or "<root>"
        out.append(f"{loc}: {e.message}")
    return out

def get_rag(prompt: str, top_k: int = 6) -> List[Dict[str, Any]]:
    idx_path = ROOT / "rag" / "index.pkl"
    if not idx_path.exists():
        return []
    from rag.query_rag import cached
    return cached(prompt, top_k)

def heuristic(prompt: str) -> Dict[str, Any]:
    p = prompt.lower()
    def mash(name: str):
        return {
            "name": name,
            "description": "MVP placeholder",
            "mashupContent": json.dumps({"mashupName": name, "widgets": [], "layout": {"type": "Absolute", "width": 800, "height": 600}}, separators=(",", ":"))
        }
    if "celsius" in p and "fahrenheit" in p:
        return {
            "apiVersion":"1.0",
            "metadata":{"name":"CelsiusToFahrenheit App","description":prompt},
            "things":[{
                "name":"CelsiusToFahrenheitThing","template":"GenericThing","enable":True,
                "properties":[],
                "services":[{
                    "name":"CelsiusToFahrenheit",
                    "description":"Convert C to F",
                    "inputs":[{"name":"c","baseType":"NUMBER","required":True}],
                    "outputs":{"baseType":"NUMBER","description":"fahrenheit"},
                    "code":"var f = (c * 9/5) + 32;\nf;"
                }]
            }],
            "mashups":[mash("CelsiusToFahrenheitMashup")]
        }
    if "add" in p or "addition" in p or "sum" in p:
        return {
            "apiVersion":"1.0",
            "metadata":{"name":"Addition App","description":prompt},
            "things":[{
                "name":"AdditionThing","template":"GenericThing","enable":True,
                "properties":[],
                "services":[{
                    "name":"Add",
                    "description":"Add two numbers",
                    "inputs":[{"name":"x","baseType":"NUMBER","required":True},{"name":"y","baseType":"NUMBER","required":True}],
                    "outputs":{"baseType":"NUMBER","description":"sum"},
                    "code":"var z = x + y;\nz;"
                }]
            }],
            "mashups":[mash("AdditionMashup")]
        }
    return {
        "apiVersion":"1.0",
        "metadata":{"name":"Quadratic Solver App","description":prompt},
        "things":[{
            "name":"QuadraticSolverThing","template":"GenericThing","enable":True,
            "properties":[{"name":"a","baseType":"NUMBER"},{"name":"b","baseType":"NUMBER"},{"name":"c","baseType":"NUMBER"}],
            "services":[{
                "name":"SolveQuadratic",
                "description":"Solve ax^2 + bx + c = 0",
                "inputs":[{"name":"a","baseType":"NUMBER","required":True},{"name":"b","baseType":"NUMBER","required":True},{"name":"c","baseType":"NUMBER","required":True}],
                "outputs":{"baseType":"INFOTABLE","description":"roots"},
                "code":"// See example spec for full implementation\nvar disc = b*b - 4*a*c;\nvar out = {disc:disc};\nout;"
            }]
        }],
        "mashups":[mash("QuadraticSolverMashup")]
    }

def llm_generate(prompt: str, ctx: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    key = os.getenv("OPENAI_API_KEY","").strip()
    model = os.getenv("OPENAI_MODEL","gpt-4.1-mini").strip()
    if not key or "REPLACE" in key:
        return None

    sys_msg = (
        "Return ONLY valid JSON matching the schema. No commentary. "
        "No destructive actions. Services via ServiceHelper.AddServiceToThing. "
        "Mashup mashupContent must be stringified JSON."
    )
    ctx_text = "\n\n".join([f"[{c['source_path']}] {c['text'][:800]}" for c in ctx])
    user_msg = f"Prompt:\n{prompt}\n\nContext:\n{ctx_text}\n\nReturn ONLY JSON."

    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={"model": model, "temperature": 0, "messages": [{"role":"system","content":sys_msg},{"role":"user","content":user_msg}]},
        timeout=60
    )
    if r.status_code != 200:
        return None
    txt = r.json()["choices"][0]["message"]["content"]
    return json.loads(txt)

def main():
    load_dotenv()
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--use-rag", action="store_true")
    ap.add_argument("--output", default="out/spec.generated.json")
    ap.add_argument("--no-llm", action="store_true")
    a = ap.parse_args()

    ctx = get_rag(a.prompt, top_k=6) if a.use_rag else []
    spec = None if a.no_llm else llm_generate(a.prompt, ctx)
    if spec is None:
        spec = heuristic(a.prompt)

    errs = validate(spec)
    if errs:
        raise SystemExit("Spec invalid:\n- " + "\n- ".join(errs[:20]))

    outp = Path(a.output)
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
    print(str(outp))

if __name__ == "__main__":
    main()
