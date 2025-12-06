# Copyright (c) 2025, Bolton and contributors
# For license information, please see license.txt

import frappe
import json
import importlib
from frappe.model.document import Document
from frappe import _


class ProcessMethod(Document):
	"""
	Registry of executable backend methods for the Rule Engine.
	Methods are validated on save and can have permission requirements.
	"""
	
	def validate(self):
		"""Validate method configuration on save"""
		self.validate_method_path()
		self.validate_config_schema()
		self.validate_usage_example()
	
	def validate_method_path(self):
		"""Ensure method_path points to a valid, callable function"""
		if not self.method_path:
			return
		
		try:
			# Split module path and function name
			parts = self.method_path.rsplit('.', 1)
			if len(parts) != 2:
				frappe.throw(_("Method path must be in format: module.path.function_name"))
			
			module_path, function_name = parts
			
			# Try to import the module
			module = importlib.import_module(module_path)
			
			# Check if function exists
			if not hasattr(module, function_name):
				frappe.throw(_("Function {0} not found in module {1}").format(function_name, module_path))
			
			# Check if it's callable
			func = getattr(module, function_name)
			if not callable(func):
				frappe.throw(_("{0} is not a callable function").format(self.method_path))
				
		except ImportError as e:
			frappe.throw(_("Cannot import module: {0}").format(str(e)))
		except Exception as e:
			frappe.throw(_("Method validation failed: {0}").format(str(e)))
	
	def validate_config_schema(self):
		"""Ensure config_schema is valid JSON Schema"""
		if not self.config_schema:
			return
		
		try:
			schema = json.loads(self.config_schema)
			
			# Basic JSON Schema validation
			if not isinstance(schema, dict):
				frappe.throw(_("Config schema must be a JSON object"))
			
			# Optionally validate it's a proper JSON Schema
			# This would require jsonschema library
			try:
				from jsonschema import Draft7Validator
				Draft7Validator.check_schema(schema)
			except ImportError:
				# jsonschema not installed, skip advanced validation
				frappe.logger().warning("jsonschema library not installed, skipping schema validation")
			except Exception as e:
				frappe.throw(_("Invalid JSON Schema: {0}").format(str(e)))
				
		except json.JSONDecodeError as e:
			frappe.throw(_("Config schema is not valid JSON: {0}").format(str(e)))
	
	def validate_usage_example(self):
		"""Validate usage example against config schema if both exist"""
		if not self.usage_example or not self.config_schema:
			return
		
		try:
			example = json.loads(self.usage_example)
			schema = json.loads(self.config_schema)
			
			# Validate example against schema
			try:
				from jsonschema import validate, ValidationError
				validate(instance=example, schema=schema)
			except ImportError:
				# jsonschema not installed, skip validation
				pass
			except ValidationError as e:
				frappe.throw(_("Usage example does not match config schema: {0}").format(str(e.message)))
				
		except json.JSONDecodeError as e:
			frappe.throw(_("Usage example is not valid JSON: {0}").format(str(e)))
	
	def execute(self, doc, context, config):
		"""
		Execute this process method with given configuration
		
		Args:
			doc: Frappe document being processed
			context: Execution context dict
			config: Configuration dict (validated against config_schema)
		
		Returns:
			Result based on return_type
		"""
		# Permission check
		if self.requires_permission:
			if not frappe.has_permission('Process Method', 'execute', self):
				frappe.throw(
					_("You don't have permission to execute {0}. Required role: {1}").format(
						self.method_name, self.requires_permission
					),
					frappe.PermissionError
				)
		
		# Validate config against schema
		if self.config_schema:
			self.validate_config_against_schema(config)
		
		# Import and execute method
		import time
		start_time = time.time()
		
		try:
			# Dynamic import
			parts = self.method_path.rsplit('.', 1)
			module_path, function_name = parts
			module = importlib.import_module(module_path)
			func = getattr(module, function_name)
			
			# Execute with doc, context, and unpacked config
			result = func(doc=doc, context=context, **config)
			
			# Update statistics
			execution_time = (time.time() - start_time) * 1000  # ms
			self.update_execution_stats(execution_time)
			
			return result
			
		except Exception as e:
			frappe.log_error(
				title=f"Process Method Execution Error: {self.method_name}",
				message=frappe.get_traceback()
			)
			raise
	
	def validate_config_against_schema(self, config):
		"""Validate configuration against JSON Schema"""
		try:
			from jsonschema import validate, ValidationError
			schema = json.loads(self.config_schema)
			validate(instance=config, schema=schema)
		except ImportError:
			frappe.logger().warning("jsonschema library not installed, skipping config validation")
		except ValidationError as e:
			frappe.throw(_("Configuration validation failed: {0}").format(str(e.message)))
		except Exception as e:
			frappe.throw(_("Schema validation error: {0}").format(str(e)))
	
	def update_execution_stats(self, execution_time_ms):
		"""Update execution statistics (non-blocking)"""
		try:
			# Use SQL for efficiency (avoid triggering validations)
			current_count = self.execution_count or 0
			current_avg = self.average_execution_time or 0
			
			# Calculate new average
			new_count = current_count + 1
			new_avg = ((current_avg * current_count) + execution_time_ms) / new_count
			
			frappe.db.set_value(
				'Process Method',
				self.name,
				{
					'execution_count': new_count,
					'last_executed': frappe.utils.now(),
					'average_execution_time': new_avg
				},
				update_modified=False
			)
			frappe.db.commit()
		except Exception as e:
			# Don't fail execution if stats update fails
			frappe.logger().error(f"Failed to update execution stats: {str(e)}")
