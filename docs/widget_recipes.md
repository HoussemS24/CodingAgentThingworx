
# Widget Layout Recipes

## Standard Widget Recipes
For standard input widgets, use the following configurations to ensure compatibility and correct rendering.

### 1. Numeric Input (legacy: `numericentry`)
For numeric inputs, use the **legacy** `numericentry` widget type (all lowercase).
**Crucial Properties:**
- `ResponsiveLayout`: `false`
- `Width`: Explicit value (e.g., `200`)
- `Height`: Explicit value (e.g., `30`)
- `Style`: `"DefaultTextBoxStyle"`
- `NumericEntryLabelStyle`: `"DefaultWidgetLabelStyle"`
- `NumericEntryFocusStyle`: `"DefaultFocusStyle"`

**Example JSON:**
```json
{
    "Properties": {
        "Type": "numericentry",
        "Id": "numericentry-1", // Use lowercase prefix
        "Label": "Numeric Input",
        "Value": 0,
        "Visible": true,
        "ResponsiveLayout": false,
        "Width": 200,
        "Height": 30,
        "Style": "DefaultTextBoxStyle",
        "NumericEntryLabelStyle": "DefaultWidgetLabelStyle",
        "NumericEntryFocusStyle": "DefaultFocusStyle"
    },
    "Widgets": []
}
```

### 2. Radio Button (modern: `ptcsradio`)
For radio buttons, use the `ptcsradio` widget type.
**Crucial Properties:**
- `ResponsiveLayout`: `false` (Recommended for safety in mixed layouts)
- `Width`: Explicit value (e.g., `200`)
- `Height`: Explicit value (e.g., `30`)

**Example JSON:**
```json
{
    "Properties": {
        "Type": "ptcsradio",
        "Id": "ptcsradio-1",
        "Label": "Radio Option",
        "Visible": true,
        "ResponsiveLayout": false,
        "Width": 200,
        "Height": 30
    },
    "Widgets": []
}
```

### 3. Other Modern Widgets (`ptcs*`)
Standard modern widgets usually work with `ResponsiveLayout: true` (default in flex containers), but can be constrained if needed.
- **Button**: `ptcsbutton`
- **TextField**: `ptcstextfield`

### 4. Toggle Button (`ptcstogglebutton`)
Used for On/Off switches.
**Properties:**
- `State`: `true` or `false` (The value).
- `LabelAlignment`: `"right"` (Places text next to switch).

**Example JSON:**
```json
{
    "Properties": {
        "Type": "ptcstogglebutton",
        "Id": "ptcstogglebutton-1",
        "Label": "Toggle Feature",
        "LabelAlignment": "right",
        "State": false,
        "Visible": true
    },
    "Widgets": []
}
```

### 5. Slider (`ptcsslider`)
For slider controls to select numeric values within a range.
**Crucial Properties:**
- `Value`: Current value (e.g., `50`)
- `Minimum`: Minimum value (e.g., `0`)
- `Maximum`: Maximum value (e.g., `100`)
- `StepSize`: Increment step (e.g., `1`)
- `ResponsiveLayout`: `false` (Recommended for consistent sizing)
- `Width`: Explicit value (e.g., `300`)
- `Height`: Explicit value (e.g., `50`)

**Example JSON:**
```json
{
    "Properties": {
        "Type": "ptcsslider",
        "Id": "ptcsslider-1",
        "DisplayName": "slider-1",
        "Label": "Slider Input",
        "Value": 50,
        "Minimum": 0,
        "Maximum": 100,
        "StepSize": 1,
        "Visible": true,
        "ResponsiveLayout": false,
        "Width": 300,
        "Height": 50
    },
    "Widgets": []
}
```

---

## Data Binding Recipe
To bind properties between widgets (e.g., Numeric Entry Value -> Label Text), use the `DataBindings` array at the Mashup root level.

**Structure:**
- **SourceId**: ID of the source widget (e.g., `numericentry-1`).
- **TargetId**: ID of the target widget (e.g., `ptcslabel-1`).
- **SourceProperty**: The property to read from (e.g., `Value`).
- **TargetProperty**: The property to write to (e.g., `LabelText`).
- **SourceSection**: Usually `""` (empty string) for widget properties, or `"Data"` for service results.
- **TargetSection**: Usually `"Properties"`.

**Example JSON (Numeric Value -> Label Text):**
```json
"DataBindings": [
    {
        "Id": "binding-numeric-to-label",
        "PropertyMaps": [
            {
                "SourceProperty": "Value",
                "TargetProperty": "LabelText",
                "SourcePropertyType": "Property",
                "TargetPropertyType": "Property"
            }
        ],
        "SourceArea": "UI",
        "SourceId": "numericentry-1",
        "SourceSection": "",
        "TargetArea": "UI",
        "TargetId": "ptcslabel-1",
        "TargetSection": "Properties"
    }
]
```

**Example JSON (Slider Value -> Label Text):**
```json
"DataBindings": [
    {
        "Id": "binding-slider-to-label",
        "PropertyMaps": [
            {
                "SourceProperty": "Value",
                "TargetProperty": "LabelText",
                "SourcePropertyType": "Property",
                "TargetPropertyType": "Property"
            }
        ],
        "SourceArea": "UI",
        "SourceId": "ptcsslider-1",
        "SourceSection": "",
        "TargetArea": "UI",
        "TargetId": "ptcslabel-1",
        "TargetSection": "Properties"
    }
]
```

