#!/bin/bash
# Research script to understand Mashup JSON structure

# Source credentials
if [ -f .env.example ]; then
    source .env.example
else
    echo "Error: .env.example not found"
    exit 1
fi

MASHUP_NAME="Antigravity.ResearchMashup"

echo "========================================="
echo "Step 1: Create a simple Mashup"
echo "========================================="
# Note: Creating a Mashup usually requires a POST to /Resources/EntityServices/Services/CreateMashup
# or similar. Let's try the standard EntityServices endpoint.

curl --location --request POST "${THINGWORX_BASE_URL}/Resources/EntityServices/Services/CreateMashup" \
--header "appKey: $THINGWORX_APP_KEY" \
--header 'Content-Type: application/json' \
--header 'Accept: application/json' \
--data "{
    \"name\": \"$MASHUP_NAME\",
    \"description\": \"Temporary mashup for research\",
    \"tags\": []
}"

echo -e "\n\n========================================="
echo "Step 2: Get Mashup JSON Definition"
echo "========================================="
# We want the full definition to see widgets and bindings
curl --location --request GET "${THINGWORX_BASE_URL}/Mashups/${MASHUP_NAME}" \
--header "appKey: $THINGWORX_APP_KEY" \
--header 'Accept: application/json' \
> mashup_structure.json

echo -e "\n\n========================================="
echo "Mashup structure saved to mashup_structure.json"
echo "========================================="
