# Copyright (c) 2025, Bolton and contributors
# For license information, please see license.txt

"""
Deduplication process methods for the Bolton Rule Engine
"""

import frappe
from frappe import _
from .utils import parse_field_list


def find_similar_records(context, fields=None, similarity_threshold=80, **kwargs):
    """
    Find similar records using fuzzy matching
    
    Args:
        context: Execution context containing 'doc'
        fields: List/text of fields to compare
        similarity_threshold: Minimum similarity score (0-100)
        
    Returns:
        List of similar document names with scores
    """
    doc = context.get('doc')
    field_list = parse_field_list(fields)
    
    # Convert threshold to 0-1 range if given as percentage
    threshold = similarity_threshold / 100 if similarity_threshold > 1 else similarity_threshold
    
    try:
        from rapidfuzz import fuzz
    except ImportError:
        frappe.logger().warning("rapidfuzz not installed, using exact matching")
        return find_duplicates_by_fields(context, fields=fields)
    
    # Get all documents to compare
    all_docs = frappe.get_all(
        doc.doctype,
        filters={'name': ['!=', doc.name], 'docstatus': ['!=', 2]},
        fields=['name'] + field_list
    )
    
    similar_docs = []
    for other_doc in all_docs:
        scores = []
        for field in field_list:
            value1 = str(doc.get(field) or '').lower()
            value2 = str(other_doc.get(field) or '').lower()
            
            if value1 and value2:
                score = fuzz.ratio(value1, value2) / 100.0
                scores.append(score)
        
        if scores:
            avg_score = sum(scores) / len(scores)
            if avg_score >= threshold:
                similar_docs.append({
                    'name': other_doc.name,
                    'similarity': round(avg_score * 100, 1)
                })
    
    return similar_docs


def find_duplicates_by_fields(context, fields=None, ignore_cancelled=True, **kwargs):
    """
    Find exact duplicate records based on field values
    """
    doc = context.get('doc')
    field_list = parse_field_list(fields)
    
    if not field_list:
        return []
    
    filters = {}
    for field in field_list:
        value = doc.get(field)
        if value:
            filters[field] = value
    
    if doc.name:
        filters['name'] = ['!=', doc.name]
    if ignore_cancelled:
        filters['docstatus'] = ['!=', 2]
    
    duplicates = frappe.get_all(doc.doctype, filters=filters, pluck='name')
    return duplicates


def check_duplicate_and_prevent_save(context, fields=None, **kwargs):
    """
    Block save if duplicate exists
    """
    doc = context.get('doc')
    duplicates = find_duplicates_by_fields(context, fields=fields)
    
    if duplicates:
        field_list = parse_field_list(fields)
        frappe.throw(
            _("Duplicate found: {0} has the same values for {1}").format(
                duplicates[0], ", ".join(field_list)
            ),
            exc=frappe.DuplicateEntryError
        )
    
    return True


def mark_as_duplicate(context, master_document=None, **kwargs):
    """
    Mark document as duplicate of another
    """
    doc = context.get('doc')
    
    if not master_document:
        return False
    
    # Set duplicate fields if they exist
    if hasattr(doc, 'is_duplicate'):
        doc.is_duplicate = 1
    if hasattr(doc, 'master_record'):
        doc.master_record = master_document
    
    return master_document


def find_duplicates_in_child_table(context, child_table_field, child_search_field, **kwargs):
    """
    Find duplicates based on values in a child table (One-to-Many matching).
    Useful for Contacts (phone_nos), Accounts (taxes), etc.
    
    Args:
        context: Execution context
        child_table_field: Fieldname of the child table in Parent Doc (e.g., 'phone_nos')
        child_search_field: Fieldname in the child table to check (e.g., 'phone')
        
    Returns:
        List of parent document names that share at least one value.
    """
    doc = context.get('doc')
    if not doc:
        return []
        
    # extract values from current doc's child table
    current_rows = doc.get(child_table_field) or []
    values_to_check = [
        r.get(child_search_field) 
        for r in current_rows 
        if r.get(child_search_field)
    ]
    
    if not values_to_check:
        return []

    # Identify Child DocType
    meta = frappe.get_meta(doc.doctype)
    child_doctype = None
    for df in meta.fields:
        if df.fieldname == child_table_field and df.fieldtype == 'Table':
            child_doctype = df.options
            break
            
    if not child_doctype:
        frappe.log_error(f"Child table field '{child_table_field}' not found in {doc.doctype}")
        return []

    # Find duplicates matches
    # We look for any row in the DB that matches one of our values
    # AND belongs to a different parent (if we are updating)
    
    filters = {
        child_search_field: ["in", values_to_check],
        "parenttype": doc.doctype,
        "docstatus": ["!=", 2] # Ignore cancelled
    }
    
    # Exclude self if saved
    if doc.name and not doc.is_new():
         filters["parent"] = ["!=", doc.name]

    duplicates = frappe.get_all(
        child_doctype, 
        filters=filters, 
        pluck="parent", 
        distinct=True
    )
    
    return duplicates
