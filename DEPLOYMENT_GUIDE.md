# Deployment Guide - ThingWorx Coding Agent (Production Edition)

This guide provides step-by-step instructions for deploying and running the **ThingWorx Coding Agent** in a production environment. This version of the agent is designed to run **100% locally**, using a local LLM (via Ollama) and a local RAG engine.

## 1. System Requirements

- **Operating System**: Linux (recommended), macOS, or Windows.
- **Python**: Version 3.8 or higher.
- **CPU/RAM**: A modern multi-core CPU and at least 16 GB of RAM are recommended for running the local LLM smoothly.
- **Disk Space**: Approximately 10 GB of free disk space for the LLM model files and RAG index.

## 2. Installation & Setup

### Step 1: Install Ollama

Ollama is required to serve the local Large Language Model. Follow the official instructions at [ollama.com](https://ollama.com) to install it on your system.

After installation, ensure the Ollama server is running. You can start it with:

```bash
ollama serve
```

### Step 2: Download the LLM Model

This agent is optimized for `llama3.1:8b`. Pull the model using the Ollama CLI:

```bash
ollama pull llama3.1:8b
```

This download is several gigabytes and may take some time.

### Step 3: Clone the Agent Repository

```bash
git clone https://github.com/HoussemS24/CodingAgentThingworx.git
cd CodingAgentThingworx
```

### Step 4: Set up Python Environment

Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
pip install -e .
```

### Step 5: Configure Environment Variables

Create a `.env` file from the template:

```bash
cp .env.example .env
```

Edit the `.env` file with your ThingWorx credentials and ensure the Ollama settings are correct (the defaults should work for a standard local installation).

```dotenv
# .env

# ThingWorx Configuration
THINGWORX_APP_KEY=YOUR_THINGWORX_APP_KEY
THINGWORX_BASE_URL=http://your-thingworx-server:8080/Thingworx

# LLM Configuration (Local Ollama)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

# RAG Configuration
USE_LOCAL_RAG=true
```

### Step 6: Set up ServiceHelper in ThingWorx

For efficient service creation, a one-time setup of the `ServiceHelper` Thing is required in your ThingWorx instance.

1.  In ThingWorx Composer, create a new **Thing** named `ServiceHelper` (template: `GenericThing`).
2.  On this Thing, create a new **Service** named `AddServiceToThing`.
3.  Copy the code from `docs/AddServiceToThing_Code.js` into the service.
4.  Define the service inputs as specified in the JS file (`thingName`, `serviceName`, etc.).
5.  Save and **Enable** the `ServiceHelper` Thing.

## 3. Running the Agent

### Step 1: Verify the Setup

Run the status command to check that all components are correctly configured:

```bash
twx-agent-local status
```

This command will check the connection to Ollama, the status of the RAG knowledge base, and the ThingWorx connection details.

### Step 2: Build the RAG Knowledge Base

Before you can generate context-aware specifications, you must build the local RAG index from the project's documentation.

```bash
twx-agent-local rag --rebuild
```

This process creates a `.kb_local/` directory containing the TF-IDF index. You only need to run this again if you update the documentation in the `docs/` folder.

### Step 3: Generate and Execute

Now you are ready to use the agent to build ThingWorx entities.

1.  **Build a specification** from a prompt:

    ```bash
    twx-agent-local build "Create a mashup for monitoring temperature sensors."
    ```

2.  **Review the generated spec** file in the `artifacts/specs/` directory.

3.  **Execute the specification**:

    ```bash
    # First, run a dry-run to see the plan
    twx-agent-local execute <path-to-your-spec.json> --dry-run

    # If the plan is correct, execute for real
    twx-agent-local execute <path-to-your-spec.json>
    ```

## 4. Troubleshooting

-   **Cannot connect to Ollama**: Ensure the `ollama serve` command is running and that the `OLLAMA_BASE_URL` in your `.env` file is correct.
-   **Model not found**: Verify that you have pulled the correct model using `ollama pull <model_name>` and that `OLLAMA_MODEL` in `.env` matches.
-   **ThingWorx Connection Errors**: Double-check your `THINGWORX_BASE_URL` and `THINGWORX_APP_KEY` in the `.env` file. Ensure your AppKey has the necessary permissions.
-   **RAG not working**: Make sure you have run `twx-agent-local rag --rebuild` at least once.
