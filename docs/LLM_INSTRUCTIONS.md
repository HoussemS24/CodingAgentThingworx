# LLM Instructions: ThingWorx Service Creation

## ⚠️ CRITICAL: Token-Efficient Service Management

When working with ThingWorx, **NEVER** download entire Thing definitions. They are 200,000+ lines and will consume excessive tokens.

## ✅ ALWAYS Use ServiceHelper

Use the `ServiceHelper.AddServiceToThing` service for all service creation tasks.

## Standard Workflow

### 1. Create a Thing
```bash
curl --location --request POST 'http://192.168.20.3:8080/Thingworx/Resources/EntityServices/Services/CreateThing' \
--header 'appKey: ${THINGWORX_APP_KEY}' \
--header 'Content-Type: application/json' \
--data '{
    "name": "ThingName",
    "thingTemplateName": "GenericThing"
}'
```

### 2. Enable the Thing
```bash
curl --location --request POST 'http://192.168.20.3:8080/Thingworx/Things/ThingName/Services/EnableThing' \
--header 'appKey: ${THINGWORX_APP_KEY}' \
--header 'Content-Type: application/json'
```

### 3. Add Services (Use ServiceHelper)
```bash
curl --location --request POST 'http://192.168.20.3:8080/Thingworx/Things/ServiceHelper/Services/AddServiceToThing' \
--header 'appKey: ${THINGWORX_APP_KEY}' \
--header 'Accept: application/json' \
--header 'Content-Type: application/json' \
--data '{
    "thingName": "ThingName",
    "serviceName": "ServiceName",
    "serviceCode": "var result = a + b;",
    "parameters": {
        "a": "NUMBER",
        "b": "NUMBER"
    },
    "resultType": "NUMBER"
}'
```

### 4. Test the Service
```bash
curl --location --request POST 'http://192.168.20.3:8080/Thingworx/Things/ThingName/Services/ServiceName' \
--header 'appKey: ${THINGWORX_APP_KEY}' \
--header 'Content-Type: application/json' \
--data '{
    "a": 10,
    "b": 20
}'
```

## Parameter Types

Common ThingWorx base types:
- `STRING`
- `NUMBER`
- `INTEGER`
- `LONG`
- `BOOLEAN`
- `DATETIME`
- `LOCATION`
- `JSON`
- `INFOTABLE`

## Service Code Examples

### Simple Calculation
```javascript
var result = a + b;
```

### Conditional Logic
```javascript
var result = "Normal";
if (temperature > 100) {
    result = "Overheat";
    logger.warn("Temperature too high!");
}
```

### Calling Other Services
```javascript
var otherResult = me.OtherService({param: value});
var result = otherResult + 10;
```

### Accessing Properties
```javascript
var currentValue = me.PropertyName;
me.PropertyName = newValue;
var result = currentValue;
```

## Service Header Format

**MANDATORY**: Every service MUST include a header comment block with change information (similar to git commits).

### Header Template
```javascript
/**
 * Service: ServiceName
 * Created: YYYY-MM-DD HH:MM by AuthorName
 * Last Modified: YYYY-MM-DD HH:MM by AuthorName
 * 
 * Description:
 *   Brief description of what this service does
 * 
 * Inputs:
 *   - paramName (TYPE): Description
 *   - paramName2 (TYPE): Description
 * 
 * Output:
 *   - TYPE: Description of return value
 * 
 * Change Log:
 *   YYYY-MM-DD - AuthorName - Initial creation
 *   YYYY-MM-DD - AuthorName - Description of changes made
 */
```

### Example with Header
```javascript
/**
 * Service: SolveQuadratic
 * Created: 2025-11-24 15:37 by Antigravity LLM
 * Last Modified: 2025-11-24 15:37 by Antigravity LLM
 * 
 * Description:
 *   Solves quadratic equations using the quadratic formula
 *   Formula: ax^2 + bx + c = 0
 *   Solutions: x = (-b ± sqrt(b^2 - 4ac)) / 2a
 * 
 * Inputs:
 *   - a (NUMBER): Coefficient of x^2
 *   - b (NUMBER): Coefficient of x
 *   - c (NUMBER): Constant term
 * 
 * Output:
 *   - JSON: Object containing solution1, solution2, discriminant, and message/error
 * 
 * Change Log:
 *   2025-11-24 - Antigravity LLM - Initial creation with error handling
 */

var discriminant = (b * b) - (4 * a * c);
var result = {};
// ... rest of code
```

### When Updating Services
When modifying an existing service:
1. Update the "Last Modified" line
2. Add a new entry to the Change Log
3. Keep all previous change log entries

Example update:
```javascript
/**
 * Service: CalculateTotal
 * Created: 2025-11-20 10:00 by Developer1
 * Last Modified: 2025-11-24 15:00 by Antigravity LLM
 * 
 * Description:
 *   Calculates total with tax and discount
 * 
 * Change Log:
 *   2025-11-20 - Developer1 - Initial creation
 *   2025-11-22 - Developer2 - Added discount logic
 *   2025-11-24 - Antigravity LLM - Fixed tax calculation rounding error
 */
```

## Best Practices

1. ✅ **Use ServiceHelper** - Always use for service creation
2. ✅ **Small Services** - Keep services focused on single tasks
3. ✅ **Error Handling** - Use try/catch in complex services
4. ✅ **Logging** - Use `logger.info()`, `logger.warn()`, `logger.error()`
5. ✅ **Test Incrementally** - Test each service after creation

## ❌ What NOT to Do

- ❌ Don't download Thing definitions with `GET /Things/ThingName`
- ❌ Don't use `AddServiceDefinition` (creates empty services only)
- ❌ Don't try to upload modified Thing JSON files
- ❌ Don't hardcode credentials in service code

## Environment Variables

Always source credentials from `.env.example`:
```bash
source .env.example
echo $THINGWORX_APP_KEY
echo $THINGWORX_BASE_URL
```

## Troubleshooting

**Service not found after creation?**
- Restart the Thing: `POST /Things/ThingName/Services/RestartThing`

**Authentication errors?**
- Verify AppKey is correct
- Check Thing permissions

**Service execution errors?**
- Check ApplicationLog in ThingWorx
- Verify parameter types match
- Check service code syntax
