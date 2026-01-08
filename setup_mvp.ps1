# setup_mvp.ps1
$ErrorActionPreference = "Stop"

function Ensure-Dir([string]$p) {
  if (!(Test-Path $p)) { New-Item -ItemType Directory -Force -Path $p | Out-Null }
}

function Write-Text([string]$path, [string]$text) {
  $dir = Split-Path $path -Parent
  if ($dir -and !(Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
  Set-Content -Path $path -Value $text -Encoding UTF8
}

Ensure-Dir "spec"
Ensure-Dir "spec\examples"
Ensure-Dir "executor"
Ensure-Dir "agent"
Ensure-Dir "rag"
Ensure-Dir "tests"
Ensure-Dir "reports"
Ensure-Dir "logs"
Ensure-Dir "out"
Ensure-Dir "cache"

# -------------------------
# Root files
# -------------------------
Write-Text ".env.example" @'
THINGWORX_BASE_URL=https://your-thingworx-host/Thingworx
THINGWORX_APP_KEY=REPLACE_WITH_LOCAL_APP_KEY
THINGWORX_SERVICEHELPER_THING=ServiceHelper
THINGWORX_VERIFY_TLS=true

# Optional (for agent LLM mode)
OPENAI_API_KEY=REPLACE_IF_YOU_WANT_LLM
OPENAI_MODEL=gpt-4.1-mini
'@

Write-Text ".gitignore" @'
.env
__pycache__/
*.pyc
.venv/
venv/
cache/
logs/
out/
reports/
*.log
*.pkl
'@

Write-Text "requirements.txt" @'
requests==2.32.3
python-dotenv==1.0.1
PyYAML==6.0.2
jsonschema==4.23.0
tqdm==4.66.5
'@

Write-Text "ASSUMPTIONS.md" @'
# Assumptions

- ThingWorx base URL is `THINGWORX_BASE_URL`, typically `https://host/Thingworx`.
- Auth uses AppKey header: `appKey: <key>`. Key is never logged.
- No destructive ops: no DELETE/reset/permission escalation.
- Services are injected via **ServiceHelper.AddServiceToThing** (primary).
  - If ServiceHelper is missing, executor logs a clear setup hint.
  - REST AddServiceDefinition exists in ThingWorx, but this MVP uses it only as an optional fallback (disabled by default).
- Mashups use **stringified JSON mashupContent**. Update tries known safe paths; exact endpoints vary by ThingWorx version.
- Tests can run in dry-run mode without a server.
- Agent: LLM call is optional (requires OPENAI_API_KEY). Without key, agent uses deterministic templates + schema validation.
'@

Write-Text "README_MVP.md" @'
# CodingAgent ThingWorx MVP (Phase A + Phase B)

## Setup (Windows PowerShell)
```powershell
cd C:\dev\CodingAgentThingworx
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
notepad .env
