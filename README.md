# ThingWorx Coding Agent

This repository contains the **ThingWorx Coding Agent**, a command-line tool designed to automate and streamline development on the ThingWorx IoT platform. It leverages a Large Language Model (LLM) with Retrieval-Augmented Generation (RAG) to convert natural language prompts into safe, executable ThingWorx operations.

The agent is built with robust safety guardrails to prevent destructive actions and ensure all operations are deterministic and testable.

## ✨ Features

- **Prompt-Driven Development**: Generate complex ThingWorx entities and services from simple text prompts.
- **Retrieval-Augmented Generation (RAG)**: Automatically injects relevant context from your local documentation to improve the accuracy and quality of the generated code.
- **Safety First**: A powerful guardrail system explicitly blocks destructive actions (e.g., delete, reset) and permission escalations.
- **Deterministic & Testable**: Generates JSON specifications for all operations, enabling validation, logging, and automated testing.
- **End-to-End Automation**: A complete CLI workflow from prompt to deployed and verified ThingWorx services.
- **Secure**: Manages credentials securely using `.env` files, which are never committed to the repository.
- **Extensible**: Designed to be easily extended with new actions and capabilities.

## ⚙️ Prerequisites

1.  **Python**: Version 3.8 or higher.
2.  **ThingWorx Instance**: A running ThingWorx server.
3.  **ThingWorx AppKey**: An AppKey with appropriate permissions to create and manage entities.
4.  **ServiceHelper Thing**: A one-time setup of a helper Thing in your ThingWorx instance is required to enable token-efficient service creation. See the setup instructions below.

## 🚀 Setup & Installation

### 1. Clone the Repository

```bash
git clone https://github.com/HoussemS24/CodingAgentThingworx.git
cd CodingAgentThingworx
```

### 2. Create a Virtual Environment

It is highly recommended to use a virtual environment to manage dependencies.

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

Install the required Python packages, including the agent itself in editable mode.

```bash
pip install -r requirements.txt
pip install -e .
```

### 4. Configure Environment Variables

Copy the example environment file and fill in your ThingWorx server details. **This file contains secrets and should never be committed to Git.**

```bash
cp .env.example .env
```

Now, edit the `.env` file with your credentials:

```dotenv
# .env
THINGWORX_APP_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
THINGWORX_BASE_URL=http://your-server.com:8080/Thingworx
```

### 5. Set up ServiceHelper in ThingWorx (One-Time Setup)

The agent uses a server-side helper service (`ServiceHelper.AddServiceToThing`) to create services efficiently without downloading or uploading large Thing definitions. This is a crucial pattern for performance and token efficiency.

1.  In your ThingWorx Composer, create a new **Thing** named `ServiceHelper` using the `GenericThing` template.
2.  On the `ServiceHelper` Thing, create a new **Service** with the following properties:
    *   **Name**: `AddServiceToThing`
    *   **Inputs**:
        *   `thingName` (STRING)
        *   `serviceName` (STRING)
        *   `serviceCode` (STRING)
        *   `parameters` (JSON)
        *   `resultType` (STRING)
    *   **Output**: `STRING`
3.  Copy the entire JavaScript code from `docs/AddServiceToThing_Code.js` and paste it into the service editor.
4.  **Save** the service and **Enable** the `ServiceHelper` Thing.

## 🤖 Usage

The agent provides a command-line interface (`twx-agent`) for all its functionalities.

### RAG: Knowledge Base Management

First, build the local knowledge base from the documentation files. This step creates vector embeddings of your documents, which the agent uses to find relevant context for your prompts.

```bash
# Build the knowledge base from the 'docs/' directory
twx-agent rag build
```

You can query the knowledge base directly to find information:

```bash
# Ask a question
twx-agent rag query "How do I create a service?"

# Get stats about the knowledge base
twx-agent rag stats
```

### Generating Specifications

Use the `generate-spec` command to turn a prompt into a JSON specification file. The agent will automatically use the RAG-indexed knowledge base to inform the generation process.

```bash
# Generate a spec from a prompt
twx-agent generate-spec "Create a Thing called MyCalculator with a service that adds two numbers, a and b."
```

This command creates a timestamped `.json` file in the `artifacts/specs/` directory. This file is fully validated against the project's schema and guardrails before being saved.

### Executing Specifications

Once you have a specification file, you can execute it against your ThingWorx instance.

First, perform a **dry run** to review the planned API calls without making any actual changes:

```bash
twx-agent execute-spec artifacts/specs/<your-spec-file>.json --dry-run
```

If the plan looks correct, execute it for real:

```bash
twx-agent execute-spec artifacts/specs/<your-spec-file>.json
```

The agent will prompt for confirmation before executing. All operations are logged to a file in `artifacts/logs/`.

## 📋 Workflow Example

Here is a complete end-to-end workflow:

1.  **Build the knowledge base** (only needs to be done once or when docs change):
    ```bash
    twx-agent rag build
    ```

2.  **Generate a spec** from a prompt:
    ```bash
    twx-agent generate-spec "Create a test Thing named E2ETestThing. It should have a service called 'HelloWorld' that takes a 'name' as a STRING input and returns a STRING greeting like 'Hello, {name}!'." 
    ```

3.  **Review the generated spec** in `artifacts/specs/`.

4.  **Execute the spec** (after confirming the dry run):
    ```bash
    twx-agent execute-spec artifacts/specs/<generated-spec-file>.json
    ```

5.  **Verify in ThingWorx**: The `E2ETestThing` now exists, is enabled, and has a working `HelloWorld` service.

## 🧪 Development & Testing

This project includes a comprehensive test suite to ensure reliability and correctness.

### Running Tests

To run all tests, use `pytest`:

```bash
# Activate virtual environment first
source venv/bin/activate

# Run all tests
pytest
```

The test suite is divided into several categories:

-   **Unit Tests** (`tests/unit/`): Test individual components like the schema validator and guardrails in isolation. These run quickly and have no external dependencies.
-   **Golden Tests** (`tests/golden/`): Test the RAG retrieval system against a set of "golden" queries to ensure it returns the expected documents. These require the knowledge base to be built (`twx-agent rag build`).
-   **E2E Tests** (`tests/e2e/`): Perform a full end-to-end workflow, from spec generation to execution and verification against a live ThingWorx instance. These are skipped by default if a valid `.env` file is not configured.

### Extending the Agent

Adding a new capability (e.g., a new action type) is a structured process. For detailed instructions, please refer to the guide:

**[📄 How to Add a New Action/Capability](docs/Extending_The_Agent.md)**

## 📂 Project Structure

```
.
├── .github/                # CI/CD workflows
├── .kb/                    # Persistent RAG knowledge base (ignored by git)
├── artifacts/
│   ├── logs/               # Execution logs
│   └── specs/              # Generated JSON specifications
├── docs/                   # Project documentation for RAG
├── src/
│   ├── cli/                # CLI command definitions (Click)
│   ├── executor/           # Logic for executing specs via REST API
│   ├── generator.py        # LLM-based spec generator
│   ├── guardrails/         # Safety and security constraints
│   ├── rag/                # RAG engine for knowledge base management
│   └── schema/             # JSON schema and validator
├── tests/
│   ├── e2e/                # End-to-end tests
│   ├── fixtures/           # Test data and sample specs
│   └── unit/               # Unit tests
├── .env.example            # Template for environment variables
├── .gitignore
├── README.md               # This file
├── requirements.txt        # Python dependencies
└── setup.py                # Package setup script
```

## 🔐 Security

-   **No Secrets in Git**: The `.gitignore` file is configured to prevent `.env` files, artifacts, and other sensitive information from being committed.
-   **Guardrails**: The executor validates every action against a strict allowlist and blocklist to prevent unintended or destructive operations.
-   **Repo Pattern**: All service creation is funneled through the `ServiceHelper` Thing, following the repository pattern to encapsulate data access and prevent direct, unsafe modifications of Thing entities.
