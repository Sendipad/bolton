# Copyright (c) 2025, Bolton and contributors
# For license information, please see license.txt

"""
ActionExecutor - Executes rule actions on documents
Supports field setting, validations, notifications, etc.
"""

import frappe
import json
from typing import Dict, Any

# Whitelist of allowed methods for security
ALLOWED_METHODS = [
    "bolton.utils.send_email",
    "bolton.utils.create_todo",
    # Add other safe methods here
]


class ActionExecutor:
	"""Executes actions defined in a rule"""
	
	def __init__(self, rule_doc, target_doc):
		"""
		Initialize executor
		
		Args:
			rule_doc: Rule document
			target_doc: Document to execute actions on
		"""
		self.rule = rule_doc
		self.doc = target_doc
		self.actions = json.loads(rule_doc.actions_json) if rule_doc.actions_json else []
	
	def execute_all(self):
		"""Execute all actions in sequence"""
		for action in self.actions:
			self.execute_single(action)
	
	def execute_single(self, action: Dict):
		"""
		Execute a single action
		
		Args:
			action: Action dictionary with type and parameters
		"""
		action_type = action.get('type')
		
		# Map action types to handler methods
		handlers = {
			'set_field': self._action_set_field,
			'raise_error': self._action_raise_error,
			'raise_warning': self._action_raise_warning,
			'log_issue': self._action_log_issue,
			'call_method': self._action_call_method,
			'check_duplicates': self._action_check_duplicates,
			'run_normalization': self._action_run_normalization,
		}
		
		handler = handlers.get(action_type)
		if handler:
			try:
				handler(action)
			except Exception as e:
				frappe.log_error(
					title=f"Action Execution Failed: {action_type}",
					message=f"Rule: {self.rule.rule_name}\\nAction: {json.dumps(action)}\\nError: {str(e)}"
				)
		else:
			frappe.log_error(f"Unknown action type: {action_type}", "ActionExecutor")
	
	def _action_set_field(self, action: Dict):
		"""
		Set a field value
		
		Action format:
		{
			"type": "set_field",
			"field": "fieldname",
			"value": "literal value" OR {"type": "field", "value": "source_field"}
		}
		"""
		fieldname = action.get('field')
		value_def = action.get('value')
		
		if not fieldname:
			return
		
		# Resolve value
		if isinstance(value_def, dict):
			if value_def.get('type') == 'field':
				from bolton.ruleflow.utils.field_resolver import FieldResolver
				value = FieldResolver.resolve(self.doc, value_def.get('value'))
			elif value_def.get('type') == 'method':
				value = frappe.call(value_def.get('value'), doc=self.doc)
			else:
				value = value_def.get('value')
		else:
			value = value_def
		
		# Set field
		self.doc.set(fieldname, value)
	
	def _action_raise_error(self, action: Dict):
		"""
		Raise a validation error (blocks save)
		
		Action format:
		{
			"type": "raise_error",
			"message": "Error message"
		}
		"""
		message = action.get('message', 'Validation failed')
		frappe.throw(message)
	
	def _action_raise_warning(self, action: Dict):
		"""
		Raise a warning (doesn't block save)
		
		Action format:
		{
			"type": "raise_warning",
			"message": "Warning message"
		}
		"""
		message = action.get('message', 'Warning')
		frappe.msgprint(message, indicator='orange', alert=True)
	
	def _action_log_issue(self, action: Dict):
		"""
		Create a Data Quality Issue record
		
		Action format:
		{
			"type": "log_issue",
			"severity": "High|Medium|Low",
			"message": "Issue description"
		}
		"""
		severity = action.get('severity', 'Medium')
		message = action.get('message', 'Data quality issue detected')
		
		# Check permissions on reference document
		if not frappe.has_permission(self.doc.doctype, 'read', self.doc.name):
			frappe.log_error(f"Permission denied for log_issue on {self.doc.name}", "ActionExecutor")
			return

		frappe.get_doc({
			'doctype': 'Data Quality Issue',
			'reference_doctype': self.doc.doctype,
			'reference_name': self.doc.name,
			'rule': self.rule.name,
			'severity': severity,
			'status': 'Open',
			'message': message,
			'details_json': json.dumps({
				'rule_type': self.rule.rule_type,
				'trigger_event': self.rule.trigger_event,
			})
		}).insert(ignore_permissions=True)
	
	def _action_call_method(self, action: Dict):
		"""
		Call a custom method
		
		Action format:
		{
			"type": "call_method",
			"method": "module.path.to.method",
			"args": {...}
		}
		"""
		method = action.get('method')
		args = action.get('args', {})
		
		if not method:
			return
		
		# Check whitelist
		if method not in ALLOWED_METHODS:
			# Check if it's a hook-configured allowed method
			configured_methods = frappe.get_hooks("bolton_allowed_methods") or []
			if method not in configured_methods:
				frappe.log_error(f"Method not allowed: {method}", "ActionExecutor")
				return

		# Add doc to args
		args['doc'] = self.doc
		
		# Call method
		frappe.call(method, **args)
	
	def _action_check_duplicates(self, action: Dict):
		"""
		Check for duplicate records using ScoringEngine
		
		Action format:
		{
			"type": "check_duplicates",
			"raise_error": true|false,
			"create_issues": true|false
		}
		"""
		from bolton.ruleflow.core.scoring import ScoringEngine
		
		scoring_engine = ScoringEngine(self.rule)
		duplicates = scoring_engine.find_duplicates(self.doc)
		
		if not duplicates:
			return
		
		# Create issues for each duplicate found
		if action.get('create_issues', True):
			for dup in duplicates:
				frappe.get_doc({
					'doctype': 'Data Quality Issue',
					'reference_doctype': self.doc.doctype,
					'reference_name': self.doc.name,
					'rule': self.rule.name,
					'severity': 'High',
					'status': 'Open',
					'message': f'Potential duplicate found: {dup["name"]} (Score: {dup["score"]:.2f}%)',
					'details_json': json.dumps({
						'duplicate_name': dup['name'],
						'similarity_score': dup['score'],
						'matching_fields': dup['fields']
					})
				}).insert(ignore_permissions=True)
		
		# Raise error if configured
		if action.get('raise_error', False) and duplicates:
			top_match = duplicates[0]
			frappe.throw(
				f'Potential duplicate detected: {top_match["name"]} '
				f'(Similarity: {top_match["score"]:.2f}%). '
				f'Please review before saving.'
			)
	
	def _action_run_normalization(self, action: Dict):
		"""
		Run normalization on document fields
		
		Action format:
		{
			"type": "run_normalization",
			"profile": "Profile Name"
		}
		"""
		from bolton.ruleflow.core.normalization import NormalizationPipeline
		
		profile_name = action.get('profile')
		if not profile_name:
			return
		
		pipeline = NormalizationPipeline(profile_name)
		pipeline.normalize_document(self.doc)
