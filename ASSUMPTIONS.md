# Assumptions

- ThingWorx base URL is `THINGWORX_BASE_URL`, typically `https://host/Thingworx`.
- Auth uses AppKey header: `appKey: <key>`. Key is never logged.
- No destructive ops: no DELETE/reset/permission escalation.
- Services are injected via **ServiceHelper.AddServiceToThing** (primary).
  - If ServiceHelper is missing, executor logs a clear setup hint.
- Mashups use **stringified JSON mashupContent**. Update tries common safe paths; endpoints vary by ThingWorx version.
- Tests can run in dry-run mode without a server; real E2E needs valid .env.
