// Service: AddServiceToThing
// Inputs:
//   - thingName (STRING): Name of the Thing to modify
//   - serviceName (STRING): Name of the service to create
//   - serviceCode (STRING): JavaScript code for the service
//   - parameters (JSON): Parameter definitions as JSON object, e.g. {"a": "NUMBER", "b": "STRING"}
//   - resultType (STRING): Return type (e.g. "NUMBER", "STRING", "BOOLEAN", "INFOTABLE", etc.)
// Output: STRING (success message or error)
let result = "";
try {
    // Get the current Thing's configuration as JSON
    var url = "http://localhost:8080/Thingworx/Things/" + thingName;
    var headers = {
        "appKey": "59a7e8dd-6b19-4c0e-9b46-419c071d74f5",
        "Accept": "application/json",
        "Content-Type": "application/json"
    };
    var config = Resources["ContentLoaderFunctions"].GetJSON({
        "url": url,
        "headers": headers,
        "ignoreSSLErrors": true
    });

    //let result = config;


    // Convert the parameters object into ThingWorx parameter definition format
    var parameterDefinitions = {};
    let stringParams = JSON.stringify(parameters);
    let newJSONparams = JSON.parse(stringParams);

    var paramKeys = Object.keys(newJSONparams);
    var paramKeysLength = paramKeys.length;
    //result = paramKeysLength;

    for (var i = 0; i < paramKeysLength; i++) {
        var paramName = paramKeys[i];
        var paramType = parameters[paramName];

        parameterDefinitions[paramName] = {
            "name": paramName,
            "aspects": {},
            "description": "",
            "baseType": paramType,
            "ordinal": i
        };
    }

    // Create the service definition
    var definition = {
        "isAllowOverride": false,
        "isOpen": false,
        "sourceType": "Unknown",
        "parameterDefinitions": parameterDefinitions,
        "name": serviceName,
        "aspects": {
            "isAsync": false
        },
        "isLocalOnly": false,
        "description": "",
        "isPrivate": false,
        "sourceName": "",
        "category": "",
        "resultType": {
            "name": "result",
            "aspects": {},
            "description": "",
            "baseType": resultType,
            "ordinal": 0
        }
    };

    // Create the service implementation
    var implementation = {
        "name": serviceName,
        "description": "",
        "handlerName": "Script",
        "configurationTables": {
            "Script": {
                "isMultiRow": false,
                "name": "Script",
                "description": "Script",
                "rows": [{
                    "code": serviceCode
                }],
                "ordinal": 0,
                "dataShape": {
                    "fieldDefinitions": {
                        "code": {
                            "name": "code",
                            "aspects": {},
                            "description": "code",
                            "baseType": "STRING",
                            "ordinal": 0
                        }
                    }
                }
            }
        }
    };

    // Add the service to both effectiveShape and thingShape
    if (!config.effectiveShape.serviceDefinitions) {
        config.effectiveShape.serviceDefinitions = {};
    }
    if (!config.effectiveShape.serviceImplementations) {
        config.effectiveShape.serviceImplementations = {};
    }

    config.effectiveShape.serviceDefinitions[serviceName] = definition;
    config.effectiveShape.serviceImplementations[serviceName] = implementation;

    if (!config.thingShape.serviceDefinitions) {
        config.thingShape.serviceDefinitions = {};
    }
    if (!config.thingShape.serviceImplementations) {
        config.thingShape.serviceImplementations = {};
    }

    config.thingShape.serviceDefinitions[serviceName] = definition;
    config.thingShape.serviceImplementations[serviceName] = implementation;

    // Push the updated configuration back to ThingWorx

    Resources["ContentLoaderFunctions"].PutJSON({
        "url": url,
        "content": JSON.stringify(config),
        "ignoreSSLErrors": true,
        "headers": headers
    });


    result = "Successfully added service '" + serviceName + "' to Thing '" + thingName + "'";

} catch (error) {
    result = "Error: " + error.message;
    logger.error("AddServiceToThing failed: " + error.message);
}
