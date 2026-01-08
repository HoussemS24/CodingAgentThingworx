#!/bin/bash
# Test the ServiceHelper.AddServiceToThing service

# Source the configuration
if [ -f .env.example ]; then
    source .env.example
else
    echo "Error: .env.example not found"
    exit 1
fi

echo "Using AppKey: $THINGWORX_APP_KEY"
echo "Using Base URL: $THINGWORX_BASE_URL"

THING_NAME="gemini.test-helper"

echo "----------------------------------------"
echo "Using ServiceHelper to add 'AddNumbers' service to '$THING_NAME'..."

curl --location --request POST "${THINGWORX_BASE_URL}/Things/ServiceHelper/Services/AddServiceToThing" \
--header "appKey: $THINGWORX_APP_KEY" \
--header 'Accept: application/json' \
--header 'Content-Type: application/json' \
--data '{
    "thingName": "'"$THING_NAME"'",
    "serviceName": "AddNumbers",
    "serviceCode": "var result = a + b;",
    "parameters": {
        "a": "NUMBER",
        "b": "NUMBER"
    },
    "resultType": "NUMBER"
}'

echo -e "\n----------------------------------------"
echo "Testing the newly created service (10 + 20)..."

curl --location --request POST "${THINGWORX_BASE_URL}/Things/${THING_NAME}/Services/AddNumbers" \
--header "appKey: $THINGWORX_APP_KEY" \
--header 'Accept: application/json' \
--header 'Content-Type: application/json' \
--data '{
    "a": 10,
    "b": 20
}'

echo -e "\n----------------------------------------"
echo "Done!"
