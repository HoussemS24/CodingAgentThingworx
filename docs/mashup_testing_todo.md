# ThingWorx Mashup Testing To-Do List

## Overview
Comprehensive testing plan for LLM-based mashup generation capabilities. This tests various layouts, widgets, and data binding scenarios.

---

## Phase 1: Container & Layout Testing

### 1.1 Responsive Containers (flexcontainer)
- [ ] Create a mashup with a single centered responsive container
- [ ] Create nested responsive containers (container within container)
- [ ] Test flex-direction: row vs column
- [ ] Test justify-content: flex-start, center, flex-end, space-between
- [ ] Test align-items: flex-start, center, flex-end, stretch

### 1.2 Static Containers
- [ ] Create a static container with fixed positioning
- [ ] Test absolute positioning (Top, Left properties)
- [ ] Mix static and responsive containers in the same mashup

---

## Phase 2: Label Alignment Testing

### 2.1 Horizontal Alignment
- [ ] Label aligned left (HorizontalAlignment: "left")
- [ ] Label aligned center (HorizontalAlignment: "center")
- [ ] Label aligned right (HorizontalAlignment: "right")

### 2.2 Vertical Alignment
- [ ] Label aligned top (VerticalAlignment: "flex-start")
- [ ] Label aligned center (VerticalAlignment: "center")
- [ ] Label aligned bottom (VerticalAlignment: "flex-end")

### 2.3 Combined Alignment
- [ ] Label centered both horizontally and vertically
- [ ] Label in top-left corner
- [ ] Label in bottom-right corner

---

## Phase 3: Widget Testing

### 3.1 Buttons (ptcsbutton)
- [ ] Create a basic button with text
- [ ] Create a button with an icon
- [ ] Create a disabled button
- [ ] Test button click event binding

### 3.2 Contained Mashups
- [ ] Embed a simple mashup inside another mashup
- [ ] Pass parameters to the contained mashup
- [ ] Test mashup-to-mashup communication

### 3.3 Gauges
- [ ] Create a linear gauge (ptcslineargauge)
- [ ] Create a radial gauge (ptcsradialgauge)
- [ ] Bind gauge to a dynamic value
- [ ] Set min/max values and thresholds

### 3.4 Collections (Repeater/Grid)
- [ ] Create a grid widget (ptcsgrid)
- [ ] Bind grid to an InfoTable service
- [ ] Configure grid columns
- [ ] Test row selection

### 3.5 Radio Buttons (ptcsradiogroup)
- [ ] Create a radio button group
- [ ] Set default selected value
- [ ] Bind selection to a property
- [ ] Test value change event

### 3.6 Toggle Buttons (ptcstogglebutton)
- [ ] Create a toggle button
- [ ] Set default state (on/off)
- [ ] Bind to a boolean property
- [ ] Test state change event

---

## Phase 4: Data Binding Testing

### 4.1 Service Binding
- [ ] Create a Thing with test services
  - [ ] Service returning a STRING
  - [ ] Service returning a NUMBER
  - [ ] Service returning a BOOLEAN
  - [ ] Service returning an INFOTABLE
- [ ] Bind service output to label (display value)
- [ ] Bind service output to gauge (numeric value)
- [ ] Bind service output to grid (InfoTable)

### 4.2 Property Binding
- [ ] Create a Thing with test properties
  - [ ] STRING property
  - [ ] NUMBER property
  - [ ] BOOLEAN property
- [ ] Bind property to label
- [ ] Bind property to toggle button
- [ ] Test two-way binding (widget updates property)

### 4.3 Event Binding
- [ ] Bind button click to invoke a service
- [ ] Bind toggle change to update a property
- [ ] Bind grid row selection to display details in labels

### 4.4 Auto-Refresh
- [ ] Configure service to auto-refresh every 5 seconds
- [ ] Test that bound widgets update automatically

---

## Phase 5: Complex Mashup Scenarios

### 5.1 Dashboard Layout
- [ ] Create a 2x2 grid layout with 4 containers
- [ ] Each container has a different widget (gauge, label, button, grid)
- [ ] All widgets bound to live data

### 5.2 Form Layout
- [ ] Create a vertical form with:
  - [ ] Text input field
  - [ ] Dropdown selector
  - [ ] Radio button group
  - [ ] Submit button
- [ ] Bind submit button to create/update a Thing property

### 5.3 Master-Detail View
- [ ] Grid showing list of items
- [ ] Click a row to display details in labels/gauges
- [ ] Edit button to modify selected item

---

## Phase 6: Styling & Theming

### 6.1 Widget Styles
- [ ] Apply custom style to a label
- [ ] Apply custom style to a button
- [ ] Test UseTheme property (true/false)

### 6.2 Container Styles
- [ ] Set background color on a container
- [ ] Set border on a container
- [ ] Test padding and margin

---

## Success Criteria

✅ All widgets render correctly in the mashup viewer
✅ All data bindings work (values display correctly)
✅ All events trigger correctly (button clicks, selections)
✅ Layout is responsive and adapts to different screen sizes
✅ No console errors in browser developer tools
✅ Mashup can be saved and reopened without errors

---

## Notes

- Test each item incrementally (don't create everything at once)
- Save working examples for reference
- Document any issues or limitations discovered
- Keep track of which widget types and properties work vs. which don't
