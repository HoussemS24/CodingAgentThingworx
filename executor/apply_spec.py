import argparse
import datetime as dt
import json
import os
from pathlib import Path
from typing import Any, Dict

from jsonschema import Draft202012Validator

from executor.tw_client import ThingWorxClient, TWError

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "spec" / "schema.json"

def load_json(path: str) -> Dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))

def validate_spec(spec: Dict[str, Any]) -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8-sig"))
    v = Draft202012Validator(schema)
    errs = sorted(v.iter_errors(spec), key=lambda e: e.path)
    if errs:
        lines = ["Spec validation failed:"]
        for e in errs[:20]:
            loc = ".".join([str(x) for x in e.path]) or "<root>"
            lines.append(f"- {loc}: {e.message}")
        raise ValueError("\n".join(lines))

def redact(s: str) -> str:
    key = os.getenv("THINGWORX_APP_KEY", "")
    return s.replace(key, "***REDACTED***") if key else s

def apply_spec(spec: Dict[str, Any], *, dry_run: bool = False, log_file: str = "") -> None:
    validate_spec(spec)

    helper = os.getenv("THINGWORX_SERVICEHELPER_THING", "ServiceHelper")
    client = None if dry_run else ThingWorxClient.from_env()

    log_dir = ROOT / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    if not log_file:
        ts = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        log_file = str(log_dir / f"apply_spec_{ts}.log")

    with open(log_file, "w", encoding="utf-8") as fp:
        fp.write(f"dry_run={dry_run}\n")
        fp.write(f"things={len(spec.get('things', []))} mashups={len(spec.get('mashups', []))}\n")

        steps = spec.get("steps") or [
            {"action": "createOrUpdateThing"},
            {"action": "enableThing"},
            {"action": "addProperties"},
            {"action": "addServices"},
            {"action": "createOrUpdateMashups"},
        ]

        for step in steps:
            action = step["action"]
            fp.write(f"\n== STEP: {action} ==\n")
            fp.flush()

            if action == "createOrUpdateThing":
                for t in spec["things"]:
                    fp.write(f"Thing createOrUpdate: {t['name']}\n")
                    if dry_run:
                        continue
                    client.create_thing(
                        t["name"],
                        template=t.get("template", "GenericThing"),
                        description=t.get("description", ""),
                    )

            elif action == "enableThing":
                for t in spec["things"]:
                    if not bool(t.get("enable", True)):
                        continue
                    fp.write(f"EnableThing: {t['name']}\n")
                    if dry_run:
                        continue
                    try:
                        client.enable_thing(t["name"])
                    except TWError as e:
                        fp.write(redact(str(e)) + "\n")

            elif action == "addProperties":
                for t in spec["things"]:
                    for p in t.get("properties", []):
                        fp.write(f"AddProperty: {t['name']}.{p['name']}\n")
                        if dry_run:
                            continue
                        client.add_property_definition(t["name"], p)

            elif action == "addServices":
                for t in spec["things"]:
                    services = t.get("services", [])
                    if not services:
                        continue
                    fp.write(f"Services for Thing: {t['name']} (count={len(services)})\n")
                    if dry_run:
                        continue
                    ok, msg = client.check_servicehelper(helper)
                    if not ok:
                        raise RuntimeError(msg)
                    for svc in services:
                        fp.write(f"InjectService: {t['name']}.{svc['name']}\n")
                        client.inject_service_via_helper(helper, t["name"], svc)

            elif action == "createOrUpdateMashups":
                for m in spec.get("mashups", []):
                    fp.write(f"Mashup createOrUpdate: {m['name']}\n")
                    if dry_run:
                        continue
                    client.create_or_update_mashup(
                        m["name"],
                        m["mashupContent"],
                        description=m.get("description", ""),
                    )
            else:
                raise ValueError(f"Unknown action: {action}")

        fp.write("\nDONE\n")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--log-file", default="")
    args = ap.parse_args()

    spec = load_json(args.spec)
    apply_spec(spec, dry_run=args.dry_run, log_file=args.log_file)
    print("OK")

if __name__ == "__main__":
    main()

