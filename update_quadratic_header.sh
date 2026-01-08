#!/bin/bash
# Update the SolveQuadratic service with proper header
# Following LLM_INSTRUCTIONS.md header format

# Source credentials
if [ -f .env.example ]; then
    source .env.example
else
    echo "Error: .env.example not found"
    exit 1
fi

THING_NAME="Antigravity.test-thing"

echo "========================================="
echo "Updating SolveQuadratic Service with Header"
echo "========================================="

# Get current timestamp
TIMESTAMP=$(date +"%Y-%m-%d %H:%M")

curl --location --request POST "${THINGWORX_BASE_URL}/Things/ServiceHelper/Services/AddServiceToThing" \
--header "appKey: $THINGWORX_APP_KEY" \
--header 'Accept: application/json' \
--header 'Content-Type: application/json' \
--data '{
    "thingName": "'"$THING_NAME"'",
    "serviceName": "SolveQuadratic",
    "serviceCode": "/**\n * Service: SolveQuadratic\n * Created: 2025-11-24 15:37 by Antigravity LLM\n * Last Modified: '"$TIMESTAMP"' by Antigravity LLM\n * \n * Description:\n *   Solves quadratic equations using the quadratic formula\n *   Formula: ax^2 + bx + c = 0\n *   Solutions: x = (-b ± sqrt(b^2 - 4ac)) / 2a\n * \n * Inputs:\n *   - a (NUMBER): Coefficient of x^2 (cannot be zero)\n *   - b (NUMBER): Coefficient of x\n *   - c (NUMBER): Constant term\n * \n * Output:\n *   - JSON: Object containing:\n *     - solution1 (NUMBER): First solution (if exists)\n *     - solution2 (NUMBER): Second solution (if exists)\n *     - discriminant (NUMBER): The discriminant value\n *     - message (STRING): Status message\n *     - error (STRING): Error message (if applicable)\n * \n * Change Log:\n *   2025-11-24 15:37 - Antigravity LLM - Initial creation with error handling\n *   '"$TIMESTAMP"' - Antigravity LLM - Added proper service header documentation\n */\n\n// Calculate discriminant\nvar discriminant = (b * b) - (4 * a * c);\nvar result = {};\n\n// Validate input\nif (a === 0) {\n    result.error = \"Coefficient a cannot be zero\";\n    logger.error(\"SolveQuadratic: Invalid input - a cannot be zero\");\n} else if (discriminant < 0) {\n    // No real solutions\n    result.error = \"No real solutions (discriminant < 0)\";\n    result.discriminant = discriminant;\n    logger.info(\"SolveQuadratic: No real solutions for a=\" + a + \", b=\" + b + \", c=\" + c);\n} else if (discriminant === 0) {\n    // One repeated solution\n    result.solution1 = -b / (2 * a);\n    result.solution2 = result.solution1;\n    result.discriminant = discriminant;\n    result.message = \"One repeated solution\";\n    logger.info(\"SolveQuadratic: One solution x=\" + result.solution1);\n} else {\n    // Two distinct solutions\n    var sqrtDiscriminant = Math.sqrt(discriminant);\n    result.solution1 = (-b + sqrtDiscriminant) / (2 * a);\n    result.solution2 = (-b - sqrtDiscriminant) / (2 * a);\n    result.discriminant = discriminant;\n    result.message = \"Two distinct solutions\";\n    logger.info(\"SolveQuadratic: Solutions x1=\" + result.solution1 + \", x2=\" + result.solution2);\n}",
    "parameters": {
        "a": "NUMBER",
        "b": "NUMBER",
        "c": "NUMBER"
    },
    "resultType": "JSON"
}'

echo -e "\n\n========================================="
echo "✅ Service updated with proper header!"
echo "========================================="
