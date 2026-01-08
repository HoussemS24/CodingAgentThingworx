# CodingAgent ThingWorx MVP (Phase A + Phase B)

## Prereqs
- Python 3.10+
- Access to a ThingWorx instance
- A ThingWorx AppKey with permission to create/update Things and Mashups

## Setup (Windows)
`powershell
cd C:\dev\CodingAgentThingworx
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
notepad .env
