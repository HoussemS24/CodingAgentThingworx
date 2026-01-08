# Managing Credentials Securely

You asked if you can use **GitHub Secrets** for local development. The short answer is **no, not directly**.

GitHub Secrets are designed for **GitHub Actions** (CI/CD pipelines) and are not automatically synced to your local machine or your colleagues' machines for security reasons.

## Recommended Solution: Environment Variables (`.env`)

The standard industry practice for sharing configuration without sharing secrets publicly is to use **Environment Variables** loaded from a `.env` file.

### How it works

1.  **The `.env` file**: This file contains your secrets (like `THINGWORX_APP_KEY`).
2.  **Git Ignore**: We add `.env` to `.gitignore` so it is **never** committed to the repository.
3.  **The `.env.example` file**: We commit a template file (e.g., `.env.example`) that lists the required variables but leaves the values empty or with placeholders.

### Setup Instructions for You and Your Colleagues

1.  **Clone the repo**.
2.  **Create your local secret file**:
    Copy `.env.example` to a new file named `.env`.
    ```bash
    cp .env.example .env
    ```
3.  **Fill in your secrets**:
    Open `.env` and paste your actual App Key.
    ```properties
    THINGWORX_APP_KEY=your-actual-uuid-key-here
    ```
4.  **Run your code**:
    Your application code (or LLM script) should be written to read from these environment variables.

### Example: Reading Credentials in Node.js

If you are writing a Node.js script, use the `dotenv` package:

```javascript
require('dotenv').config();

const appKey = process.env.THINGWORX_APP_KEY;
const baseUrl = process.env.THINGWORX_BASE_URL || config.thingworxServer.baseUrl;

// Now use appKey in your headers
```

### Example: Reading Credentials in Python

```python
import os
from dotenv import load_dotenv

load_dotenv()

app_key = os.getenv("THINGWORX_APP_KEY")
```

## Sharing with Colleagues

To share the secret key with colleagues:
1.  Use a secure channel (Password Manager, encrypted chat, 1Password, LastPass).
2.  Do **not** send it via email or Slack if possible.
3.  They will paste it into their own local `.env` file.
