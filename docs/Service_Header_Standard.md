# Service Header Standard

## Overview

All ThingWorx services created or modified by LLMs MUST include a standardized header comment block with change tracking information (similar to git commits).

## Mandatory Header Format

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

## Header Components

### 1. Service Identification
- **Service**: The exact name of the service
- **Created**: Initial creation timestamp and author
- **Last Modified**: Most recent modification timestamp and author

### 2. Description
- Clear explanation of what the service does
- Include formulas, algorithms, or business logic if relevant
- Keep it concise but informative

### 3. Inputs
- List all input parameters
- Include data type and description for each
- Note any constraints or special requirements

### 4. Output
- Specify the return type
- Describe what the output represents
- For complex types (JSON, INFOTABLE), describe the structure

### 5. Change Log
- **Chronological list** of all changes
- Format: `YYYY-MM-DD - AuthorName - Description`
- Keep ALL previous entries (don't delete history)
- Be specific about what changed

## Examples

### New Service
```javascript
/**
 * Service: CalculateDiscount
 * Created: 2025-11-24 16:00 by Antigravity LLM
 * Last Modified: 2025-11-24 16:00 by Antigravity LLM
 * 
 * Description:
 *   Calculates the discounted price based on original price and discount percentage
 * 
 * Inputs:
 *   - originalPrice (NUMBER): Original price before discount
 *   - discountPercent (NUMBER): Discount percentage (0-100)
 * 
 * Output:
 *   - NUMBER: Final price after applying discount
 * 
 * Change Log:
 *   2025-11-24 - Antigravity LLM - Initial creation
 */

var result = originalPrice * (1 - (discountPercent / 100));
```

### Updated Service
```javascript
/**
 * Service: CalculateDiscount
 * Created: 2025-11-24 16:00 by Antigravity LLM
 * Last Modified: 2025-11-24 16:30 by Antigravity LLM
 * 
 * Description:
 *   Calculates the discounted price based on original price and discount percentage
 *   Now includes validation to prevent negative prices
 * 
 * Inputs:
 *   - originalPrice (NUMBER): Original price before discount (must be > 0)
 *   - discountPercent (NUMBER): Discount percentage (0-100)
 * 
 * Output:
 *   - JSON: Object with finalPrice and savings, or error message
 * 
 * Change Log:
 *   2025-11-24 16:00 - Antigravity LLM - Initial creation
 *   2025-11-24 16:30 - Antigravity LLM - Added input validation and error handling
 */

var result = {};

if (originalPrice <= 0) {
    result.error = "Original price must be greater than 0";
} else if (discountPercent < 0 || discountPercent > 100) {
    result.error = "Discount must be between 0 and 100";
} else {
    result.finalPrice = originalPrice * (1 - (discountPercent / 100));
    result.savings = originalPrice - result.finalPrice;
}
```

## Benefits

✅ **Traceability**: Know who changed what and when  
✅ **Documentation**: Self-documenting code  
✅ **Collaboration**: Team members understand service history  
✅ **Debugging**: Easier to track down when issues were introduced  
✅ **Compliance**: Audit trail for changes

## LLM Implementation

When using ServiceHelper to create/update services, the header is part of the `serviceCode` parameter:

```bash
curl ... --data '{
    "thingName": "MyThing",
    "serviceName": "MyService",
    "serviceCode": "/**\n * Service: MyService\n * Created: ...\n * ...\n */\n\nvar result = ...;",
    ...
}'
```

Note: Use `\n` for newlines in the JSON string.
