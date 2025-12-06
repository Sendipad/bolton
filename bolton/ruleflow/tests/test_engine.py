# Copyright (c) 2025, Bolton and contributors
# For license information, please see license.txt

import frappe
import unittest
from frappe.tests.utils import FrappeTestCase


class TestRuleEngine(FrappeTestCase):
    """Test cases for Rule Engine"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        frappe.set_user('Administrator')
        # Create test rule
        if not frappe.db.exists("Rule", "Test Validation Rule"):
            frappe.get_doc({
                "doctype": "Rule",
                "rule_name": "Test Validation Rule",
                "document_type": "ToDo",
                "trigger_event": "Validate",
                "is_active": 1,
                "priority": 10
            }).insert(ignore_permissions=True)
    
    def test_rule_creation(self):
        """Test rule is created correctly"""
        rule = frappe.get_doc("Rule", "Test Validation Rule")
        self.assertEqual(rule.document_type, "ToDo")
        self.assertEqual(rule.is_active, 1)
    
    def test_process_method_loading(self):
        """Test process methods can be loaded"""
        from bolton.ruleflow.methods.validation import validate_required_fields
        from bolton.ruleflow.methods.enrichment import set_default_value
        
        self.assertTrue(callable(validate_required_fields))
        self.assertTrue(callable(set_default_value))
    
    @classmethod  
    def tearDownClass(cls):
        # Cleanup - don't delete, just rollback
        frappe.db.rollback()
        super().tearDownClass()


class TestValidationMethods(FrappeTestCase):
    """Test validation process methods"""
    
    def test_validate_required_fields_pass(self):
        """Test required fields validation passes"""
        from bolton.ruleflow.methods.validation import validate_required_fields
        
        doc = frappe.get_doc({"doctype": "ToDo", "description": "Test"})
        result = validate_required_fields(doc, {}, fields=["description"])
        self.assertTrue(result)
    
    def test_validate_required_fields_fail(self):
        """Test required fields validation fails"""
        from bolton.ruleflow.methods.validation import validate_required_fields
        
        doc = frappe.get_doc({"doctype": "ToDo", "description": ""})
        
        with self.assertRaises(frappe.ValidationError):
            validate_required_fields(doc, {}, fields=["description"])
    
    def test_validate_field_pattern(self):
        """Test regex pattern validation"""
        from bolton.ruleflow.methods.validation import validate_field_pattern
        
        doc = frappe._dict({"email": "test@example.com"})
        result = validate_field_pattern(doc, {}, field="email", pattern=r".*@.*\..*")
        self.assertTrue(result)


class TestEnrichmentMethods(FrappeTestCase):
    """Test enrichment process methods"""
    
    def test_set_default_value(self):
        """Test default value setting"""
        from bolton.ruleflow.methods.enrichment import set_default_value
        
        # Use actual document, not _dict
        doc = frappe.get_doc({"doctype": "ToDo", "description": "Test"})
        result = set_default_value(doc, {}, field="priority", default_value="Medium")
        
        self.assertEqual(doc.priority, "Medium")
        self.assertEqual(result, "Medium")
    
    def test_set_default_no_overwrite(self):
        """Test default doesn't overwrite existing"""
        from bolton.ruleflow.methods.enrichment import set_default_value
        
        doc = frappe.get_doc({"doctype": "ToDo", "description": "Test", "priority": "High"})
        result = set_default_value(doc, {}, field="priority", default_value="Low", overwrite=False)
        
        self.assertEqual(doc.priority, "High")
    
    def test_calculate_field_value(self):
        """Test formula calculation"""
        from bolton.ruleflow.methods.enrichment import calculate_field_value
        
        # Use actual document with set() method
        doc = frappe.get_doc({"doctype": "ToDo", "description": "Test"})
        result = calculate_field_value(doc, {}, target_field="priority", formula='"High"')
        
        self.assertEqual(doc.priority, "High")
