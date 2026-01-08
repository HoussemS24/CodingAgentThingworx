# Research: Service Generation Pattern

## Overview
To optimize LLM token usage and enable dynamic system modification, we can use "Meta-Services" in ThingWorx. These are services designed to create or modify other entities (Things, Services, Mashups) programmatically.

## Benefits
- **Token Efficiency**: Instead of the LLM generating the full verbose JSON for a Thing definition every time, it can generate a compact call to a meta-service.
- **Abstraction**: Complex ThingWorx API details (headers, URL structures) are hidden within the meta-service.

## Implemented Meta-Services

### 1. `AddServiceToThing`
Adds a new JavaScript service to an existing Thing.
- **File**: `docs/utils/AddServiceToThing.js`
- **Usage**:
  ```javascript
  // LLM generates a call like this:
  Things["MyMetaThing"].AddServiceToThing({
      thingName: "TargetThing",
      serviceName: "NewFeature",
      serviceCode: "var x = 1; result = x + 1;",
      parameters: {"input1": "NUMBER"},
      resultType: "NUMBER"
  });
  ```

### 2. `UpdateMashupContent`
Updates the UI structure (`mashupContent`) of a Mashup.
- **File**: `docs/utils/UpdateMashupContent.js`
- **Usage**:
  ```javascript
  // LLM generates a call like this:
  Things["MyMetaThing"].UpdateMashupContent({
      mashupName: "mqtt.Test-mu",
      mashupContent: "{\"resourceId\":\"...\",\"root\":{...}}" // New UI JSON
  });
  ```
