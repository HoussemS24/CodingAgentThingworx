# Research: Mashup Structure and Retrieval

## Overview
To programmatically analyze or modify ThingWorx Mashups, we can retrieve their structure as JSON. This is particularly useful for LLM-based workflows where an agent needs to understand or edit the UI definition.

## Creating a Mashup
To create a new Mashup programmatically, use a **PUT request** to the `/Thingworx/Mashups` endpoint.

### API Endpoint
```
PUT http://192.168.20.3:8080/Thingworx/Mashups?Content-Type=application%2Fjson&reason=created%20by%20LLM
```

### Headers
```javascript
{
    "appKey": "59a7e8dd-6b19-4c0e-9b46-419c071d74f5",
    "Content-Type": "application/json",
    "Accept": "application/json"
}
```

### Request Payload Structure
The payload must include:
- `entityType`: "Mashups"
- `name`: The mashup name (e.g., "antigravity.test-mu")
- `description`: Description text
- `mashupContent`: **Stringified JSON** containing the UI definition
- `configurationTables`: Mobile settings configuration
- `aspects`: Mashup type and responsive settings
- `projectName`: Usually "PTCDefaultProject"

### Example: Creating a Simple Mashup
⚠️ **Important**: This example uses the **correct modern structure** with `flexcontainer` and `ptcslabel`.

```javascript
const payload = {
    "entityType": "Mashups",
    "name": "antigravity.test-mu",
    "description": "Test mashup created by Antigravity Agent",
    "configurationTables": {
        "MobileSettings": {
            "description": "",
            "isMultiRow": false,
            "name": "MobileSettings",
            "isHidden": true,
            "dataShape": { /* ... mobile settings schema ... */ },
            "rows": [{ /* ... default mobile settings ... */ }]
        }
    },
    "designTimePermissions": {"Delete": [], "Read": [], "Update": [], "Create": []},
    "runTimePermissions": {"permissions": []},
    "tags": [],
    "aspects": {
        "mashupType": "mashup",
        "isResponsive": true,
        "isFlex": true
    },
    "mashupContent": JSON.stringify({
        "UI": {
            "Properties": {
                "Id": "mashup-root",
                "Type": "mashup",
                "ResponsiveLayout": true,
                "Width": 1024,
                "Height": 618,
                "Style": "DefaultMashupStyle",
                "StyleTheme": "PTC Convergence Theme",
                /* ... other UI properties ... */
            },
            "Widgets": [
                // ⚠️ CRITICAL: Always wrap widgets in a flexcontainer!
                {
                    "Properties": {
                        "Type": "flexcontainer",
                        "__TypeDisplayName": "Responsive Container",
                        "Id": "flexcontainer-2",
                        "DisplayName": "container-2",
                        "flex-direction": "row",
                        "align-items": "center",
                        "justify-content": "center",
                        "flex-grow": 1,
                        "ResponsiveLayout": true,
                        "LastContainer": true
                    },
                    "Widgets": [
                        // ⚠️ Use modern widget types like ptcslabel, not Label!
                        {
                            "Properties": {
                                "Type": "ptcslabel",
                                "__TypeDisplayName": "Label",
                                "Id": "ptcslabel-3",
                                "DisplayName": "ptcs-label-3",
                                "LabelText": "Hello World",
                                "HorizontalAlignment": "left",
                                "VerticalAlignment": "flex-start",
                                "UseTheme": true,
                                "Visible": true
                            },
                            "Widgets": []
                        }
                    ]
                }
            ]
        },
        "Data": {
            "Session": { /* ... session data source ... */ },
            "UserExtensions": { /* ... user extensions data source ... */ }
        },
        "Events": [],
        "DataBindings": [],
        "mashupType": "mashup"
    }),
    "projectName": "PTCDefaultProject"
};
```

### ⚠️ Common Mistakes to Avoid
1. **Using legacy widget types** like `Label` instead of `ptcslabel` - widgets won't render!
2. **Placing widgets directly in the mashup root** without a `flexcontainer` - layout will break!
3. **Forgetting flex properties** like `justify-content` and `align-items` for centering.
4. **Using `Text` property** instead of `LabelText` for `ptcslabel` widgets.

### Full Example Script
See `create_test_mashup.js` for a complete working example.

## Retrieving Mashup JSON
The `ContentLoaderFunctions` resource in ThingWorx provides a `GetJSON` service that can be used to fetch the Mashup definition.

### Service Call Example
```javascript
var url = "http://192.168.20.3:8080/Thingworx/Mashups/mqtt.Test-mu";
var headers = {
    "appKey": "59a7e8dd-6b19-4c0e-9b46-419c071d74f5",
    "Accept": "application/json",
    "Content-Type": "application/json"
};

var mashupDefinition = Resources["ContentLoaderFunctions"].GetJSON({
    "url": url,
    "headers": headers,
    "ignoreSSLErrors": true
});
```

### Key Structure: `mashupContent`
The most critical part of the returned JSON is the `mashupContent` key.
- **Type**: String (Stringified JSON)
- **Purpose**: Contains the actual UI definition, including widgets, layout, and bindings.
- **Usage**: An LLM can parse this string, modify the UI structure (e.g., add a button, change a label), stringify it back, and update the Mashup.

## Updating a Mashup
To update the mashup, you would modify the `mashupContent` property of the fetched definition and use `ContentLoaderFunctions.PutJSON` to send it back.

```javascript
// ... modify mashupDefinition.mashupContent ...

Resources["ContentLoaderFunctions"].PutJSON({
    "url": url,
    "content": JSON.stringify(mashupDefinition),
    "headers": headers,
    "ignoreSSLErrors": true
});
```

