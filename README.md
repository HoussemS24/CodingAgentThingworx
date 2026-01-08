# ThingWorx Development Environment for LLMs

This repository provides guides and tools for LLMs to interact with and develop on ThingWorx servers via the REST API.

## 📋 Contents

### Documentation
- **[ThingWorx API Guide](docs/ThingWorx_API_Guide.md)**: Complete REST API reference with cURL examples
- **[Developing in ThingWorx](docs/Developing_in_ThingWorx.md)**: Best practices and development workflow
- **[Managing Credentials](docs/Managing_Credentials.md)**: Secure credential handling with `.env` files
- **[Advanced Service Management](docs/Advanced_Service_Management.md)**: Efficient service creation patterns
- **[Service Header Standard](docs/Service_Header_Standard.md)**: Mandatory header format for all services
- **[ServiceHelper Implementation](docs/AddServiceToThing_Code.js)**: Working code for server-side service management

### Configuration
- **[Configuration Template](config/thingworx_config.json)**: Server connection settings
- **[Environment Variables](.env.example)**: Template for storing credentials securely

### Scripts
- **[test_service_helper.sh](test_service_helper.sh)**: Example script using ServiceHelper

## 🚀 Quick Start

1. **Configure your environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your ThingWorx AppKey
   ```

2. **Set up ServiceHelper** (One-time setup):
   - Create a Thing called `ServiceHelper` with template `GenericThing`
   - Create a service called `AddServiceToThing` with inputs:
     - `thingName` (STRING)
     - `serviceName` (STRING)
     - `serviceCode` (STRING)
     - `parameters` (JSON)
     - `resultType` (STRING)
   - Copy the code from `docs/AddServiceToThing_Code.js` into the service
   - Enable the `ServiceHelper` Thing

3. **Use ServiceHelper to add services**:
   ```bash
   ./test_service_helper.sh
   ```

## 🤖 Instructions for LLMs

### ⚠️ IMPORTANT: Use ServiceHelper for All Service Creation

**DO NOT** download entire Thing definitions (they are 200k+ lines and waste tokens).

**ALWAYS** use the `ServiceHelper.AddServiceToThing` service to add services with code.

### Example: Adding a Service

```bash
curl --location --request POST 'http://192.168.20.3:8080/Thingworx/Things/ServiceHelper/Services/AddServiceToThing' \
--header 'appKey: YOUR_APP_KEY' \
--header 'Accept: application/json' \
--header 'Content-Type: application/json' \
--data '{
    "thingName": "MyThing",
    "serviceName": "MyService",
    "serviceCode": "var result = input1 + input2;",
    "parameters": {
        "input1": "NUMBER",
        "input2": "NUMBER"
    },
    "resultType": "NUMBER"
}'
```

### Workflow for Creating Things with Services

1. **Create the Thing**:
   ```bash
   POST /Resources/EntityServices/Services/CreateThing
   Body: {"name": "MyThing", "thingTemplateName": "GenericThing"}
   ```

2. **Enable the Thing**:
   ```bash
   POST /Things/MyThing/Services/EnableThing
   ```

3. **Add Services using ServiceHelper**:
   ```bash
   POST /Things/ServiceHelper/Services/AddServiceToThing
   Body: {thingName, serviceName, serviceCode, parameters, resultType}
   ```

4. **Test the Service**:
   ```bash
   POST /Things/MyThing/Services/MyService
   Body: {param1: value1, param2: value2}
   ```

## 📦 Repository Structure

```
.
├── .env.example              # Environment variable template
├── .gitignore               # Git ignore rules
├── README.md                # This file
├── config/
│   └── thingworx_config.json # Server configuration
├── docs/
│   ├── ThingWorx_API_Guide.md
│   ├── Developing_in_ThingWorx.md
│   ├── Managing_Credentials.md
│   ├── Advanced_Service_Management.md
│   ├── ServiceHelper_Success.md
│   └── AddServiceToThing_Code.js
└── test_service_helper.sh   # Example usage script
```

## 🔐 Security Notes

- Never commit `.env` files (they contain secrets)
- Use `.env.example` as a template
- Share AppKeys securely with team members
- The `.gitignore` file protects sensitive files

## 💡 Benefits of This Approach

✅ **Token Efficient**: Small API calls instead of massive JSON files  
✅ **Fast**: Server-side processing  
✅ **Reusable**: One ServiceHelper for all Things  
✅ **Simple**: Clean, documented API  
✅ **Secure**: Credentials managed via environment variables
