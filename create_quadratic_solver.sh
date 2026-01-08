#!/bin/bash
# Create Antigravity.test-thing and add quadratic formula solver
# Following LLM_INSTRUCTIONS.md workflow

# Source credentials
if [ -f .env.example ]; then
    source .env.example
else
    echo "Error: .env.example not found"
    exit 1
fi

THING_NAME="Antigravity.test-thing"

echo "========================================="
echo "Step 1: Create Thing '$THING_NAME'"
echo "========================================="
curl --location --request POST "${THINGWORX_BASE_URL}/Resources/EntityServices/Services/CreateThing" \
--header "appKey: $THINGWORX_APP_KEY" \
--header 'Content-Type: application/json' \
--header 'Accept: application/json' \
--data "{
    \"name\": \"$THING_NAME\",
    \"thingTemplateName\": \"GenericThing\"
}"

echo -e "\n\n========================================="
echo "Step 2: Enable Thing"
echo "========================================="
curl --location --request POST "${THINGWORX_BASE_URL}/Things/${THING_NAME}/Services/EnableThing" \
--header "appKey: $THINGWORX_APP_KEY" \
--header 'Content-Type: application/json' \
--header 'Accept: application/json'

echo -e "\n\n========================================="
echo "Step 3: Add QuadraticFormula Service"
echo "========================================="
curl --location --request POST "${THINGWORX_BASE_URL}/Things/ServiceHelper/Services/AddServiceToThing" \
--header "appKey: $THINGWORX_APP_KEY" \
--header 'Accept: application/json' \
--header 'Content-Type: application/json' \
--data '{
    "thingName": "'"$THING_NAME"'",
    "serviceName": "SolveQuadratic",
    "serviceCode": "// Quadratic formula: ax^2 + bx + c = 0\n// Solutions: x = (-b ± sqrt(b^2 - 4ac)) / 2a\n\nvar discriminant = (b * b) - (4 * a * c);\nvar result = {};\n\nif (a === 0) {\n    result.error = \"Coefficient a cannot be zero\";\n} else if (discriminant < 0) {\n    result.error = \"No real solutions (discriminant < 0)\";\n    result.discriminant = discriminant;\n} else if (discriminant === 0) {\n    result.solution1 = -b / (2 * a);\n    result.solution2 = result.solution1;\n    result.discriminant = discriminant;\n    result.message = \"One repeated solution\";\n} else {\n    var sqrtDiscriminant = Math.sqrt(discriminant);\n    result.solution1 = (-b + sqrtDiscriminant) / (2 * a);\n    result.solution2 = (-b - sqrtDiscriminant) / (2 * a);\n    result.discriminant = discriminant;\n    result.message = \"Two distinct solutions\";\n}\n\nlogger.info(\"Solved quadratic: a=\" + a + \", b=\" + b + \", c=\" + c);",
    "parameters": {
        "a": "NUMBER",
        "b": "NUMBER",
        "c": "NUMBER"
    },
    "resultType": "JSON"
}'

echo -e "\n\n========================================="
echo "Step 4: Test Service - Example: x^2 - 5x + 6 = 0"
echo "Expected solutions: x = 2 and x = 3"
echo "========================================="
curl --location --request POST "${THINGWORX_BASE_URL}/Things/${THING_NAME}/Services/SolveQuadratic" \
--header "appKey: $THINGWORX_APP_KEY" \
--header 'Accept: application/json' \
--header 'Content-Type: application/json' \
--data '{
    "a": 1,
    "b": -5,
    "c": 6
}'

echo -e "\n\n========================================="
echo "Test 2: x^2 + 2x + 1 = 0 (one solution)"
echo "Expected: x = -1 (repeated)"
echo "========================================="
curl --location --request POST "${THINGWORX_BASE_URL}/Things/${THING_NAME}/Services/SolveQuadratic" \
--header "appKey: $THINGWORX_APP_KEY" \
--header 'Accept: application/json' \
--header 'Content-Type: application/json' \
--data '{
    "a": 1,
    "b": 2,
    "c": 1
}'

echo -e "\n\n========================================="
echo "Test 3: x^2 + x + 1 = 0 (no real solutions)"
echo "Expected: error message"
echo "========================================="
curl --location --request POST "${THINGWORX_BASE_URL}/Things/${THING_NAME}/Services/SolveQuadratic" \
--header "appKey: $THINGWORX_APP_KEY" \
--header 'Accept: application/json' \
--header 'Content-Type: application/json' \
--data '{
    "a": 1,
    "b": 1,
    "c": 1
}'

echo -e "\n\n========================================="
echo "✅ Complete!"
echo "========================================="
