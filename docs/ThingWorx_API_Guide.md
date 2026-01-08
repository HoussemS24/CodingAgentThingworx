# ThingWorx REST API Guide for LLMs

This guide provides instructions on how to interact with the ThingWorx server using its REST API. This is intended for LLMs or developers automating tasks.

## 1. Base Configuration

All API requests should be directed to the ThingWorx server base URL.

**Base URL Format:**
`http://<server-host>:<port>/Thingworx`

**Example Environment:**
- Host: `192.168.20.3`
- Port: `8080`

## 2. Authentication

Authentication is typically handled via an Application Key (AppKey).

**Headers Required:**
- `appKey`: `<YOUR_APP_KEY>`
- `Content-Type`: `application/json`
- `Accept`: `application/json`

## 3. Common Operations (with cURL Examples)

The following examples assume:
- Host: `192.168.20.3:8080`
- Thing: `atio.example-thing`
- AppKey: `ea56f55d-1f9e-4f11-9159-016728a7a3c6` (Replace with your actual key)

### 3.1. Properties

#### Get a Property
Retrieves the current value of a specific property.

**Endpoint:** `GET /Things/<ThingName>/Properties/<PropertyName>`

**cURL Example:**
```bash
curl --location 'http://192.168.20.3:8080/Thingworx/Things/atio.example-thing/Properties/exampleInt' \
--header 'appKey: ea56f55d-1f9e-4f11-9159-016728a7a3c6' \
--header 'Accept: application/json' \
--header 'Content-Type: application/json'
```

#### Set a Property
Updates the value of a specific property. Note that we use `PUT` on the `Properties` collection with a JSON body containing the key-value pair.

**Endpoint:** `PUT /Things/<ThingName>/Properties/*`

**cURL Example:**
```bash
curl --location --request PUT 'http://192.168.20.3:8080/Thingworx/Things/atio.example-thing/Properties/*' \
--header 'appKey: ea56f55d-1f9e-4f11-9159-016728a7a3c6' \
--header 'Accept: application/json' \
--header 'Content-Type: application/json' \
--data '{
    "exampleInt": 10
}'
```

### 3.2. Services

#### Execute a Service
Runs a service defined on a Thing.

**Endpoint:** `POST /Things/<ThingName>/Services/<ServiceName>`

**cURL Example:**
```bash
curl --location --request POST 'http://192.168.20.3:8080/Thingworx/Things/atio.example-thing/Services/doubleExampleInt' \
--header 'appKey: ea56f55d-1f9e-4f11-9159-016728a7a3c6' \
--header 'Accept: application/json' \
--header 'Content-Type: application/json'
```
*Note: If the service requires parameters, include them in the `--data` JSON object.*

## 4. Entity Management

### 4.1. Creating a Thing
To create a new Thing, use the `CreateThing` service on the `EntityServices` resource.

**Endpoint:** `POST /Resources/EntityServices/Services/CreateThing`

**Parameters:**
- `name`: Name of the new Thing.
- `thingTemplateName`: The template to inherit from (e.g., 'GenericThing').

**cURL Example:**
```bash
curl --location --request POST 'http://192.168.20.3:8080/Thingworx/Resources/EntityServices/Services/CreateThing' \
--header 'appKey: ea56f55d-1f9e-4f11-9159-016728a7a3c6' \
--header 'Accept: application/json' \
--header 'Content-Type: application/json' \
--data '{
    "name": "MyNewThing",
    "thingTemplateName": "GenericThing"
}'
```
*After creation, you typically need to enable the Thing using the `EnableThing` service.*

### 4.2. Creating a Property
To add a property definition to a specific Thing (not a template), use the `AddPropertyDefinition` service on the Thing itself.

**Endpoint:** `POST /Things/<ThingName>/Services/AddPropertyDefinition`

**Parameters:**
- `name`: Property name.
- `type`: Data type (STRING, NUMBER, BOOLEAN, etc.).
- `description`: (Optional) Description.

**cURL Example:**
```bash
curl --location --request POST 'http://192.168.20.3:8080/Thingworx/Things/MyNewThing/Services/AddPropertyDefinition' \
--header 'appKey: ea56f55d-1f9e-4f11-9159-016728a7a3c6' \
--header 'Accept: application/json' \
--header 'Content-Type: application/json' \
--data '{
    "name": "MyNewProperty",
    "type": "STRING",
    "description": "A property created via API"
}'
```
*Note: You may need to restart the Thing or the server for some changes to fully take effect, though usually adding a property is immediate.*

### 4.3. Writing (Defining) a Service
To add a new service definition to a Thing, use `AddServiceDefinition`. To update the code of an existing service, use `UpdateServiceDefinition` (or `AddServiceDefinition` with overwrite parameters depending on version, but `Add` is safer for creation).

**Endpoint:** `POST /Things/<ThingName>/Services/AddServiceDefinition`

**Parameters:**
- `name`: Service name.
- `code`: The JavaScript code.
- `resultType`: Return type.
- `parameters`: JSON object defining input parameters.

**cURL Example:**
```bash
curl --location --request POST 'http://192.168.20.3:8080/Thingworx/Things/MyNewThing/Services/AddServiceDefinition' \
--header 'appKey: ea56f55d-1f9e-4f11-9159-016728a7a3c6' \
--header 'Accept: application/json' \
--header 'Content-Type: application/json' \
--data '{
    "name": "MyNewService",
    "description": "Returns a greeting",
    "category": "",
    "code": "var result = \"Hello, \" + name;",
    "isAllowOverride": true,
    "isLocalOnly": false,
    "isOpen": false,
    "isPrivate": false,
    "isProtected": false,
    "resultType": "STRING",
    "parameters": {
        "rows": [
            {
                "name": "name",
                "baseType": "STRING",
                "description": "Name to greet",
                "aspects": {}
            }
        ]
    }
}'
```

### 4.4. Creating a Project
To create a Project, use a `PUT` request to the `/Projects` collection endpoint.

**Endpoint:** `PUT /Projects`

**cURL Example:**
```bash
curl --location --request PUT 'http://192.168.20.3:8080/Thingworx/Projects?Content-Type=application/json' \
--header 'appKey: <YOUR_APP_KEY>' \
--header 'Accept: application/json' \
--header 'Content-Type: application/json' \
--data '{
    "entityType": "Projects",
    "name": "MyNewProject",
    "description": "A new project",
    "tags": []
}'
```

### 4.5. Assigning Entities to a Project
When creating an entity (Mashups, Things, etc.), you can assign it to a Project by including the `projectName` property in the main JSON payload.

**Key Property:**
`"projectName": "<ProjectName>"`

**Example Payload (for Mashup creation):**
```json
{
    "entityType": "Mashups",
    "name": "MyProjectMashup",
    "projectName": "MyNewProject", // Assigns this entity to 'MyNewProject'
    "mashupContent": "..."
}
```
*Note: If `projectName` is omitted, entities are typically assigned to 'PTCDefaultProject' or the system default.*

