# Developing in ThingWorx: A Guide for LLMs

This guide outlines the workflow and best practices for developing solutions within the ThingWorx platform via the API.

## 1. Core Concepts

- **Thing**: A digital representation of a physical object or system.
- **ThingTemplate**: A blueprint for Things. All Things inherit from a Template.
- **ThingShape**: A reusable collection of properties and services that can be implemented by multiple Templates.
- **Service**: A function written in JavaScript (Rhino engine) that runs on the server.
- **Property**: A variable stored on a Thing (e.g., temperature, status).

## 2. Development Workflow

### Step 1: Define the Model
Before writing code, define the data model.
1. Identify the entities (Things).
2. Determine their Properties (state).
3. Determine their Services (behavior).

### Step 2: Create/Update Entities
Use the API to create Things or update their definitions.
- Use `EntityServices` to create new Things.
- Ensure Things are enabled (`EnableThing` service) after creation.

### Step 3: Implement Services
Services are the core logic.
- Language: JavaScript (Rhino ES5/ES6 compat).
- **Important**: ThingWorx JS is synchronous and server-side.
- Access Properties: `me.PropertyName`
- Call other Services: `me.OtherService()` or `Things["OtherThing"].Service()`

**Example Service Code:**
```javascript
// Input: temperature (NUMBER)
// Output: STRING

var result = "Normal";
if (temperature > 100) {
    result = "Overheat";
    // Log to Application Log
    logger.warn("Thing " + me.name + " is overheating!");
}
return result;
```

### Step 4: Testing
Test services by executing them via the REST API (`POST` request).
- Verify the output matches expectations.
- Check the `ApplicationLog` in ThingWorx for errors (`logger.info`, `logger.error`).

## 3. Best Practices for LLMs

1. **Idempotency**: When writing scripts to update Things, try to check if the Thing exists first.
2. **Error Handling**: Wrap critical logic in `try/catch` blocks within the JavaScript service code.
3. **Logging**: Use `logger.info()` liberally to help debug remote execution.
4. **Small Services**: Keep services focused on a single task. Compose complex logic by calling multiple smaller services.
5. **Security**: Do not hardcode credentials in service code. Use `ConfigurationTables` or `Password` properties if needed.

## 4. Common Tasks

**Searching for a Thing:**
Use `SearchThings` on `SearchFunctions` resource if you don't know the exact name.

**Restarting a Thing:**
Things generally don't need "restarting", but if you update a Template, you may need to restart the Thing to propagate changes (rare, usually automatic). Restarting the *Server* is a separate admin task.
