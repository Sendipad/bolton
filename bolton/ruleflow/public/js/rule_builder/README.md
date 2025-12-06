# Bolton Rule Builder - Frontend Components

This directory contains Vue.js components for visual rule building.

## Components

### RuleBuilder.vue
Main component that provides a visual interface for:
- Adding/editing conditions with dropdown operators
- Adding/editing actions with type selection
- Syncing with Frappe form fields

## Usage

The Rule Builder is integrated into the Rule DocType form via `rule.js`.

### Features

**Condition Builder:**
- Field selection
- Operator dropdown (==, !=, >, <, contains, etc.)
- Value input
- Logical operators (AND/OR)

**Action Builder:**
- Action type selection
- Dynamic fields based on action type
- Multiple actions support

**Form Integration:**
- Load from JSON fields
- Save back to JSON fields
- Real-time validation

## Development

To modify the builder:

1. Edit `RuleBuilder.vue`
2. Run `bench build --app bolton`
3. Reload the browser

## Architecture

```
Rule Form (Frappe)
    ↓
rule.js (Form Script)
    ↓
RuleBuilder.vue (Visual Editor)
    ↓  
Saves to conditions_json & actions_json
```

## Alternative: JSON-Only Approach

The current implementation provides **inline JSON examples and validation** in  `rule.js` which may be sufficient for most users without needing the full Vue builder.

Features in `rule.js`:
- ✅ JSON validation with error messages
- ✅ Example snippets (click "Examples" button)
- ✅ One-click example insertion
- ✅ Test rule functionality
- ✅ Cache clearing

This approach is:
- Simpler to maintain
- No build step required
- Works out of the box
