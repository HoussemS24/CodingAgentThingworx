# ThingWorx Coding Agent - Production Edition

This repository contains the **ThingWorx Coding Agent**, a production-ready command-line tool designed to automate and streamline development on the ThingWorx IoT platform. It leverages a **local Large Language Model (LLM)** with **Retrieval-Augmented Generation (RAG)** to convert natural language prompts into safe, executable ThingWorx operations, including the creation of **Things, Mashups, and complete Applications**.

The agent is built with robust safety guardrails to prevent destructive actions and ensure all operations are deterministic and testable. It runs **100% locally** without requiring external API keys for LLM access.

## ✨ Features

- **Local LLM Support**: Integrates with any Ollama-compatible endpoint (e.g., `llama3.1:8b`) for fully local and secure operation. No OpenAI API key needed.
- **Full Application Generation**: Create not just Things, but also complex Mashups and complete ThingWorx Application entities from a single prompt.
- **Local RAG Engine**: A lightweight, dependency-free RAG engine uses TF-IDF to inject relevant context from your local documentation, improving the accuracy of generated code.
- **Safety First**: A powerful guardrail system explicitly blocks destructive actions (e.g., delete, reset) and permission escalations.
- **Deterministic & Testable**: Generates JSON specifications for all operations, enabling validation, logging, and automated testing.
- **End-to-End Automation**: A complete CLI workflow from prompt to deployed and verified ThingWorx entities.
- **Secure**: Manages credentials securely using `.env` files, which are never committed to the repository.

## ⚙️ Prerequisites

1.  **Python**: Version 3.8 or higher.
2.  **Ollama**: A running Ollama instance to serve the local LLM. See [ollama.com](https://ollama.com) for installation instructions.
3.  **ThingWorx Instance**: A running ThingWorx server.
4.  **ThingWorx AppKey**: An AppKey with appropriate permissions to create and manage entities.
5.  **ServiceHelper Thing**: A one-time setup of a helper Thing in your ThingWorx instance is required to enable token-efficient service creation. See the setup instructions below.

## 🚀 Setup & Installation

### 1. Clone the Repository

```bash
git clone https://github.com/HoussemS24/CodingAgentThingworx.git
cd CodingAgentThingworx
```

### 2. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
pip install -e .
```

### 4. Configure Environment Variables

Copy the example environment file and fill in your details. **This file contains secrets and should never be committed to Git.**

```bash
cp .env.example .env
```

Now, edit the `.env` file with your credentials and local LLM configuration:

```dotenv
# .env

# ThingWorx Configuration
THINGWORX_APP_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
THINGWORX_BASE_URL=http://your-server.com:8080/Thingworx

# LLM Configuration (Local Ollama)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

# RAG Configuration
USE_LOCAL_RAG=true
```

### 5. Set up Ollama and Download Model

Ensure your Ollama server is running. Then, pull the desired model:

```bash
ollama pull llama3.1:8b
```

### 6. Set up ServiceHelper in ThingWorx (One-Time Setup)

This helper service is crucial for creating services efficiently.

1.  In your ThingWorx Composer, create a new **Thing** named `ServiceHelper` using the `GenericThing` template.
2.  On the `ServiceHelper` Thing, create a new **Service** named `AddServiceToThing` with the inputs defined in `docs/AddServiceToThing_Code.js`.
3.  Copy the entire JavaScript code from `docs/AddServiceToThing_Code.js` and paste it into the service editor.
4.  **Save** the service and **Enable** the `ServiceHelper` Thing.

## 🤖 Usage

The agent provides a dedicated command-line interface for the production app: `twx-agent-local`.

### 1. Check System Status

Verify that all components (Ollama, RAG, ThingWorx) are configured correctly.

```bash
twx-agent-local status
```

### 2. Build the Knowledge Base

Build the local RAG knowledge base from the documentation files. This only needs to be done once or when your documentation changes.

```bash
twx-agent-local rag --rebuild
```

You can also query the knowledge base directly:

```bash
twx-agent-local query "How do I create a mashup?"
```

### 3. Build ThingWorx Entities

Use the `build` command to generate a JSON specification from a natural language prompt. The agent will automatically use the RAG-indexed knowledge base to inform the generation process.

```bash
# Build a Thing
twx-agent-local build "Create a Thing called MySensor with a service that returns a random temperature."

# Build a Mashup
twx-agent-local build "Create a dashboard mashup named SensorDashboard with a title and a PTC label."

# Build a full Application
twx-agent-local build "Create a Monitoring App with a home mashup and a settings mashup."
```

This command creates a timestamped `.json` file in the `artifacts/specs/` directory.

### 4. Execute the Specification

Once you have a specification file, you can execute it against your ThingWorx instance.

First, perform a **dry run** to review the planned API calls:

```bash
twx-agent-local execute artifacts/specs/<your-spec-file>.json --dry-run
```

If the plan looks correct, execute it for real (with confirmation):

```bash
twx-agent-local execute artifacts/specs/<your-spec-file>.json
```

## 📂 Project Structure

```
.
├── .kb_local/              # Persistent local RAG knowledge base
├── artifacts/
│   ├── logs/               # Execution logs
│   └── specs/              # Generated JSON specifications
├── docs/                   # Project documentation for RAG
├── src/
│   ├── cli/                # CLI command definitions
│   │   └── production_cli.py # Main CLI for the production app
│   ├── executor/           # Logic for executing specs (Thing, Mashup, App)
│   ├── llm/                # Local LLM client (Ollama)
│   ├── rag/                # Local RAG engine (TF-IDF)
│   └── ...
├── tests/
├── .env.example
├── README.md
└── setup.py
```
