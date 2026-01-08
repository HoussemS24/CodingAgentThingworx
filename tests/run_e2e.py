import argparse
from pathlib import Path
from executor.apply_spec import apply_spec, load_json

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = [
    ROOT / "spec" / "examples" / "quadratic_solver_app.json",
    ROOT / "spec" / "examples" / "addition_app.json",
    ROOT / "spec" / "examples" / "celsius_to_fahrenheit_app.json",
]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    for p in EXAMPLES:
        spec = load_json(str(p))
        print(f"APPLY {p.name} dry_run={args.dry_run}")
        apply_spec(spec, dry_run=args.dry_run)

    print("E2E OK" + (" (dry-run)" if args.dry_run else ""))

if __name__ == "__main__":
    main()
