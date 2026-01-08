// Service: UpdateMashupContent
// Inputs:
//   - mashupName (STRING): Name of the Mashup to modify
//   - mashupContent (STRING): The new stringified JSON content for the mashup UI
// Output: STRING (success message or error)

let result = "";
try {
    // Construct the URL for the Mashup
    // Note: Assuming localhost/default port if not specified, or relative if running on same instance.
    // For robustness in this script, we use the full URL pattern provided in examples.
    var url = "http://localhost:8080/Thingworx/Mashups/" + mashupName;

    var headers = {
        "appKey": "59a7e8dd-6b19-4c0e-9b46-419c071d74f5",
        "Accept": "application/json",
        "Content-Type": "application/json"
    };

    // 1. Get the current Mashup definition
    var mashupDefinition = Resources["ContentLoaderFunctions"].GetJSON({
        "url": url,
        "headers": headers,
        "ignoreSSLErrors": true
    });

    // 2. Update the mashupContent
    // The mashupContent is a stringified JSON inside the main JSON.
    // We assume the input 'mashupContent' is already a valid stringified JSON of the UI structure.
    mashupDefinition.mashupContent = mashupContent;

    // 3. Push the updated definition back to ThingWorx
    Resources["ContentLoaderFunctions"].PutJSON({
        "url": url,
        "content": JSON.stringify(mashupDefinition),
        "headers": headers,
        "ignoreSSLErrors": true
    });

    result = "Successfully updated content for Mashup '" + mashupName + "'";

} catch (error) {
    result = "Error updating mashup: " + error.message;
    logger.error("UpdateMashupContent failed: " + error.message);
}
