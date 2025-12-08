# Copyright (c) 2025, Bolton and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json


class ProcessMethod(Document):
    def validate(self):
        self.validate_method_path()
        self.validate_config_schema()
        self.validate_input_output_schemas()
    
    def validate_method_path(self):
        """Validate that method_path points to an importable function"""
        if not self.method_path:
            return
        
        try:
            method = frappe.get_attr(self.method_path)
            if not callable(method):
                frappe.throw(f"'{self.method_path}' is not callable")
        except Exception as e:
            frappe.throw(f"Cannot import method '{self.method_path}': {str(e)}")
    
    def validate_config_schema(self):
        """Validate config_schema is valid JSON"""
        if self.config_schema:
            try:
                json.loads(self.config_schema)
            except json.JSONDecodeError as e:
                frappe.throw(f"Invalid config_schema JSON: {e}")
    
    def validate_input_output_schemas(self):
        """Validate input_schema and output_schema are valid JSON"""
        for field in ['input_schema', 'output_schema']:
            value = getattr(self, field, None)
            if value:
                try:
                    json.loads(value)
                except json.JSONDecodeError as e:
                    frappe.throw(f"Invalid {field} JSON: {e}")
    
    def execute(self, context, config=None, **kwargs):
        """
        Execute this process method
        
        Args:
            context: Execution context dict containing 'doc' and other variables
            config: Configuration dict for this method
            
        Returns:
            Result of the method execution
        """
        if not self.is_enabled:
            frappe.throw(f"Process method '{self.method_name}' is disabled")
        
        # Import and call the method
        method = frappe.get_attr(self.method_path)
        
        # Merge config with context-based params
        params = config or {}
        
        # Track execution stats
        import time
        start_time = time.time()
        
        try:
            result = method(context, **params)
            
            # Update stats
            execution_time = (time.time() - start_time) * 1000  # ms
            self.update_execution_stats(execution_time)
            
            return result
        except Exception as e:
            frappe.log_error(
                title=f"Process Method Error: {self.method_name}",
                message=f"Config: {params}\nError: {str(e)}"
            )
            raise
    
    def update_execution_stats(self, execution_time_ms):
        """Update execution statistics"""
        try:
            # Update atomically to avoid race conditions
            frappe.db.sql("""
                UPDATE `tabProcess Method`
                SET 
                    execution_count = execution_count + 1,
                    last_executed = NOW(),
                    average_execution_time = (
                        (average_execution_time * execution_count + %s) / (execution_count + 1)
                    )
                WHERE name = %s
            """, (execution_time_ms, self.name))
        except Exception:
            pass  # Don't fail execution due to stats update failure
    
    def get_schema_fields(self):
        """Parse config_schema and return list of field definitions"""
        if not self.config_schema:
            return []
        
        try:
            schema = json.loads(self.config_schema)
            return schema.get('fields', [])
        except json.JSONDecodeError:
            return []
