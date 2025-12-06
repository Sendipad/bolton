# Copyright (c) 2025, Bolton and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Rule(Document):
    """Core Rule DocType for Bolton Rule Engine"""
    
    def validate(self):
        """Validate rule configuration"""
        self.validate_json_fields()
        self.validate_document_type()
    
    def validate_json_fields(self):
        """Ensure JSON fields contain valid JSON"""
        import json
        
        for field in ['conditions_json', 'actions_json', 'options_json']:
            value = self.get(field)
            if value:
                try:
                    json.loads(value)
                except json.JSONDecodeError as e:
                    frappe.throw(f"Invalid JSON in {field}: {str(e)}")
    
    def validate_document_type(self):
        """Ensure document type exists and is valid"""
        if self.document_type:
            if not frappe.db.exists("DocType", self.document_type):
                frappe.throw(f"DocType {self.document_type} does not exist")
            
            # Check if single or child table
            meta = frappe.get_meta(self.document_type)
            if meta.issingle or meta.istable:
                frappe.throw(f"{self.document_type} is a single or child DocType. Rules can only be applied to standard DocTypes.")
    
    def on_update(self):
        """Clear cache on update"""
        self._clear_rule_cache()
    
    def on_trash(self):
        """Clear cache on delete"""
        self._clear_rule_cache()
    
    def _clear_rule_cache(self):
        """Helper to clear cache safely"""
        try:
            from bolton.ruleflow.core.coordinator import RuleCoordinator
            RuleCoordinator.clear_cache(self.document_type)
        except ImportError:
            # Coordinator may not exist, ignore
            pass
