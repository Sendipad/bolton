# Copyright (c) 2025, Bolton and contributors
# For license information, please see license.txt

"""
Validation process methods for the Bolton Rule Engine
"""

import frappe
from frappe import _


def validate_required_fields(doc, context, fields, **kwargs):
    """
    Validate that specified fields have values
    
    Args:
        doc: Document being processed
        context: Execution context
        fields: List of field names to validate
    
    Returns:
        Boolean: True if all fields have values
    """
    missing_fields = []
    
    for field in fields:
        value = doc.get(field)
        if not value:
            missing_fields.append(field)
    
    if missing_fields:
        frappe.throw(
            _("Required fields are missing: {0}").format(", ".join(missing_fields))
        )
    
    return True


def validate_field_pattern(doc, context, field, pattern, error_message=None, **kwargs):
    """
    Validate that a field value matches a regex pattern
    
    Args:
        doc: Document being processed
        context: Execution context
        field: Field name to validate
        pattern: Regex pattern to match
        error_message: Custom error message
    
    Returns:
        Boolean: True if pattern matches
    """
    import re
    
    value = doc.get(field)
    if not value:
        return True  # Empty values pass
    
    if not re.match(pattern, str(value)):
        msg = error_message or _(f"Field {field} does not match required pattern")
        frappe.throw(msg)
    
    return True


def validate_value_in_range(doc, context, field, min_value=None, max_value=None, **kwargs):
    """
    Validate that a numeric field is within a specified range
    
    Args:
        doc: Document being processed
        context: Execution context
        field: Field name to validate
        min_value: Minimum allowed value
        max_value: Maximum allowed value
    
    Returns:
        Boolean: True if value is in range
    """
    value = doc.get(field)
    if value is None:
        return True
    
    try:
        num_value = float(value)
    except (ValueError, TypeError):
        frappe.throw(_(f"Field {field} must be numeric"))
    
    if min_value is not None and num_value < min_value:
        frappe.throw(_(f"Field {field} must be at least {min_value}"))
    
    if max_value is not None and num_value > max_value:
        frappe.throw(_(f"Field {field} must be at most {max_value}"))
    
    return True


def validate_unique_field(doc, context, field, ignore_cancelled=True, **kwargs):
    """
    Validate that a field value is unique across all documents
    
    Args:
        doc: Document being processed
        context: Execution context
        field: Field to check for uniqueness
        ignore_cancelled: Ignore cancelled documents
    
    Returns:
        Boolean: True if unique
    """
    value = doc.get(field)
    if not value:
        return True
    
    filters = {field: value}
    if ignore_cancelled:
        filters['docstatus'] = ['!=', 2]
    
    # Exclude current document
    if doc.name:
        filters['name'] = ['!=', doc.name]
    
    duplicates = frappe.get_all(
        doc.doctype,
        filters=filters,
        limit=1
    )
    
    if duplicates:
        frappe.throw(
            _(f"Value '{value}' for field {field} already exists in {duplicates[0].name}")
        )
    
    return True


def validate_conditional_required(doc, context, condition_field, condition_value, required_fields, **kwargs):
    """
    Make fields required when a specific condition is met
    
    Args:
        doc: Document being processed
        context: Execution context
        condition_field: Field to check condition on
        condition_value: Value that triggers requirement
        required_fields: List of fields that become required
    
    Returns:
        Boolean: True if validation passes
    """
    current_value = doc.get(condition_field)
    
    # Check if condition is met
    if current_value == condition_value:
        missing = []
        for field in required_fields:
            if not doc.get(field):
                missing.append(field)
        
        if missing:
            frappe.throw(
                _(f"When {condition_field} is '{condition_value}', these fields are required: {', '.join(missing)}")
            )
    
    return True
