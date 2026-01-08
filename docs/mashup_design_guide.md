# ThingWorx Mashup Design Guide

This guide outlines best practices, standard widgets, and layout strategies for creating effective ThingWorx Mashups.

## Best Practices

### 1. Layout Strategy
*   **Responsive Design**: Always prefer **Responsive** layouts over Static layouts. This ensures your application adapts to different screen sizes (desktop, tablet, mobile).
*   **Containers**: Use `Layout` widgets (Rows and Columns) to structure your page. Avoid placing widgets directly on the root canvas if possible; nest them in containers for better control.

### 2. Naming Conventions
*   **Meaningful Names**: Give every widget a descriptive `DisplayName` (e.g., `lblTemperature`, `btnSubmit`, `gridOrderHistory`). This makes binding and debugging significantly easier.
*   **Consistency**: Stick to a prefix convention (e.g., `lbl` for Labels, `btn` for Buttons, `txt` for TextFields).

### 3. Performance
*   **Minimize Bindings**: Too many bindings can slow down the Mashup load time. Group data in services where possible.
*   **Service Execution**: Use `InvokeService` only when necessary. Avoid auto-refreshing heavy services at short intervals.
*   **Lazy Loading**: Load data only when the user needs to see it (e.g., in a tab that isn't initially visible).

## Standard Widgets Reference

Here is a list of commonly used widgets:

| Widget Name | Type in JSON | Description | Common Use Case |
| :--- | :--- | :--- | :--- |
| **Label (Modern)** | `ptcslabel` | Displays static or dynamic text with modern styling. | Headers, data values, instructions. |
| **Label (Legacy)** | `Label` | Old label widget - **avoid using**. | Legacy mashups only. |
| **Button** | `ptcsbutton` | Clickable element to trigger events. | Submitting forms, navigation, refreshing data. |
| **TextField** | `ptcstextfield` | Single-line text input. | Search bars, form inputs. |
| **TextArea** | `ptcstextarea` | Multi-line text input. | Comments, descriptions. |
| **Grid (Advanced)** | `ptcsgrid` | Displays data in a tabular format. | Lists of items, reports, data management. |
| **Navigation** | `navigation` | Links to other Mashups or URLs. | Menus, links. |
| **Image** | `image` | Displays an image. | Logos, product photos, status icons. |
| **Checkbox** | `ptcscheckbox` | Boolean input. | Toggles, settings. |
| **Dropdown** | `ptcsdropdown` | Select one item from a list. | Filtering, form selection. |
| **Date Time Picker** | `ptcsdatetimepicker` | Select date and time. | Filtering by date range, scheduling. |
| **Tabs** | `ptcstabs` | Organizes content into selectable views. | Categorizing complex information. |
| **Responsive Container** | `flexcontainer` | Flex-based container for responsive layouts. | **Required for modern mashups**. |
| **Numeric Input** | `numericentry` | Legacy numeric input (lowercase). | Input numbers. **Requires explicit width/height**. |
| **Radio Button** | `ptcsradio` | Modern radio button. | Single choice selection. |
| **Toggle Button** | `ptcstogglebutton` | On/Off switch. | Boolean settings, enabling features. |

### ⚠️ Critical: Modern Widget Types
**Always use the modern `ptcs*` widget types** (e.g., `ptcslabel`, `ptcsbutton`) instead of legacy types (e.g., `Label`, `Button`). The legacy widgets may not render correctly in newer ThingWorx versions.

### ⚠️ Critical: Use Responsive Containers
**Never place widgets directly in the mashup root.** Always wrap them in a `flexcontainer` (Responsive Container) first. This is required for proper rendering and responsive behavior.

**Example Structure:**
```
Mashup Root (mashup-root)
  └── Responsive Container (flexcontainer)
        └── Label (ptcslabel)
        └── Button (ptcsbutton)
```

## Layout Containers

Layouts are crucial for structure. Common patterns include:

*   **Header**: Top strip for branding, global actions (Logout), and page titles.
*   **Sidebar**: Left (or right) panel for navigation menus.
*   **Footer**: Bottom strip for copyright, version info, or status.
*   **Content**: The main central area where the specific page functionality lives.

## Master Mashups

**Master Mashups** are templates that define the consistent outer shell of your application.

### Purpose
1.  **Consistent Navigation**: You define the **Sidebar** (Navigation Menu) and **Header** once in the Master Mashup. All "Child Mashups" loaded into this Master will automatically inherit these elements.
2.  **Theming**: The Master Mashup helps enforce a consistent visual theme (colors, fonts, spacing) across all pages that use it.

### Implementation
*   Create a Mashup with the type `Master`.
*   Add your **Logo** and **Title** to the Header area.
*   Add a **Menu** widget to the Sidebar area for navigation.
*   Define a **Content** placeholder. When you create a standard Mashup, you select this Master, and your standard Mashup's content will fill this placeholder.

### Benefits
*   **Maintainability**: Change the menu item in one place (the Master), and it updates everywhere.
*   **User Experience**: Users get a seamless experience as the frame (header/nav) stays stable while the content area transitions.

## Detailed Widget Recipes

For specific configurations of tricky widgets like **Numeric Input** and **Radio Buttons**, please refer to [Widget Recipes](widget_recipes.md).
