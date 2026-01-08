import argparse
from pathlib import Path
import yaml

from agent.generate_spec import heuristic, get_rag, llm_generate, validate
from executor.apply_spec import apply_spec

ROOT = Path(__file__).resolve().parents[1]
PROMPTS = ROOT / "tests" / "prompts.yaml"
REPORT = ROOT / "reports" / "eval.md"

def gen(prompt: str, use_rag: bool):
    ctx = get_rag(prompt) if use_rag else []
    spec = llm_generate(prompt, ctx) or heuristic(prompt)
    errs = validate(spec)
    if errs:
        raise RuntimeError("Invalid spec: " + "; ".join(errs[:5]))
    return spec

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--use-rag", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    prompts = yaml.safe_load(PROMPTS.read_text(encoding="utf-8"))
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    total = 0
    ok = 0
    fails = []

    for item in prompts:
        total += 1
        p = item["prompt"]
        try:
            spec = gen(p, a.use_rag)
            if a.apply:
                apply_spec(spec, dry_run=a.dry_run)
            ok += 1
        except Exception as e:
            fails.append((p, str(e)))

    lines = []
    lines.append("# Eval Report")
    lines.append(f"- use_rag: {a.use_rag}")
    lines.append(f"- apply: {a.apply}")
    lines.append(f"- dry_run: {a.dry_run}")
    lines.append(f"- success: {ok}/{total} ({(ok/total*100):.1f}%)")
    if fails:
        lines.append("")
        lines.append("## Failures")
        for p, err in fails[:10]:
            lines.append(f"- **Prompt:** {p}")
            lines.append(f"  - Error: {err}")

    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(str(REPORT))

if __name__ == "__main__":
    main()
