# Bolton Rule Engine

A clean, modern, enterprise-grade Rule Engine and Data Quality Framework for Frappe/ERPNext.

## Features

✅ **JSON-Based Rules** - No complex child tables, just clean JSON configurations
✅ **4 Rule Types** - Validation, Deduplication, Transformation, Enrichment
✅ **Flexible Conditions** - Nested AND/OR logic, multiple operators
✅ **Powerful Actions** - Set fields, raise errors/warnings, log issues, call methods
✅ **High Performance** - Built-in caching for rule lookups
✅ **Clean Architecture** - ~500 lines of core code (vs 1500+ in typical implementations)

## Architecture

```
Bolton Rule Engine
├── DocTypes (3 total)
│   ├── Rule (master)
│   ├── Normalization Profile 
│   └── Data Quality Issue (logs)
│
├── Core Services
│   ├── RuleCoordinator - Rule loading & dispatch
│   ├── ConditionEvaluator - JSON condition evaluation
│   ├── ActionExecutor - Action execution
│   └── ScoringEngine - Deduplication/matching
│
└── Hooks
    └── doc_events - Automatic rule execution
```

## Quick Start

### 1. Create a Simple Validation Rule

```python
rule = frappe.get_doc({
    "doctype": "Rule",
    "rule_name": "Email Required for Companies",
    "rule_type": "Validation",
    "document_type": "Customer",
    "trigger_event": "validate",
    "is_active": 1,
    "conditions_json": '[{"left": {"type": "field", "value": "customer_type"}, "operator": "==", "right": {"type": "literal", "value": "Company"}}]',
    "actions_json": '[{"type": "raise_error", "message": "Email is required for company customers"}]'
})
rule.insert()
```

### 2. Create a Transformation Rule

```python
rule = frappe.get_doc({
    "doctype": "Rule",
    "rule_name": "Auto-set Priority",
    "rule_type": "Transformation",
    "document_type": "Sales Order",
    "trigger_event": "before_save",
    "conditions_json": '[{"left": {"type": "field", "value": "grand_total"}, "operator": ">", "right": {"type": "literal", "value": 100000}}]',
    "actions_json": '[{"type": "set_field", "field": "priority", "value": {"type": "literal", "value": "High"}}]'
})
rule.insert()
```

### 3. Create a Deduplication Rule

```python
rule = frappe.get_doc({
    "doctype": "Rule",
    "rule_name": "Detect Duplicate Customers",
    "rule_type": "Deduplication",
    "document_type": "Customer",
    "trigger_event": "before_insert",
    "options_json": '{"match_threshold": 85, "blocking_fields": ["country"], "scoring_fields": [{"field": "customer_name", "weight": 0.7}, {"field": "email_id", "weight": 0.3}]}'
})
rule.insert()
```

## Rule Structure

### Conditions JSON Format

```json
[
  {
    "left": {"type": "field", "value": "fieldname"},
    "operator": "==",
    "right": {"type": "literal", "value": "some value"},
    "logical_operator": "AND"
  }
]
```

**Supported Operators:**
- `==`, `!=`, `>`, `<`, `>=`, `<=`
- `in`, `not_in`
- `contains`, `not_contains`
- `is_set`, `is_not_set`
- `regex`

**Value Types:**
- `field` - Document field value
- `literal` - Hard-coded value
- `method` - Call a method and use return value

### Actions JSON Format

```json
[
  {
    "type": "set_field",
    "field": "status",
    "value": {"type": "literal", "value": "Approved"}
  },
  {
    "type": "raise_error",
    "message": "Validation failed"
  },
  {
    "type": "log_issue",
    "severity": "High",
    "message": "Data quality issue detected"
  }
]
```

**Supported Actions:**
- `set_field` - Set a field value
- `raise_error` - Block save with error
- `raise_warning` - Show warning (doesn't block)
- `log_issue` - Create Data Quality Issue record
- `call_method` - Execute custom Python method

## Installation

```bash
# Get the app
cd frappe-bench
bench get-app bolton [git-url]

# Install to site
bench --site [sitename] install-app bolton

# Migrate
bench --site [sitename] migrate
```

## Development

```bash
# Run tests
bench --site [sitename] run-tests --app bolton

# Clear cache after rule changes
bench --site [sitename] clear-cache
```

## Documentation

- [Example Rules](./EXAMPLES.md) - Complete examples for all rule types
- [API Documentation](./API.md) - Developer API reference

## Comparison vs Traditional Approach

| Feature | Bolton | Traditional |
|---------|--------|-------------|
| DocTypes | 3 | 15-20 |
| Fields | ~35 total | 200+ |
| Core Code | ~500 lines | 1500+ lines |
| Condition Model | JSON arrays | Child tables (47 fields!) |
| Performance | Cached | Slower |
| Maintainability | High | Low |

## License

MIT

## Credits

Built with ❤️ for the Frappe/ERPNext community
