# Copyright (c) 2025, Bolton and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class NormalizationProfile(Document):
	"""Normalization Profile for text cleaning and standardization"""
	
	def validate(self):
		"""Validate profile configuration"""
		self.validate_json_fields()
	
	def validate_json_fields(self):
		"""Ensure JSON fields contain valid JSON"""
		import json
		
		if self.normalize_fields_json:
			try:
				fields = json.loads(self.normalize_fields_json)
				if not isinstance(fields, list):
					frappe.throw("normalize_fields_json must be an array of field configurations")
				
				# Validate each field config
				for field in fields:
					if not isinstance(field, dict):
						frappe.throw("Each field configuration must be an object")
					if 'fieldname' not in field:
						frappe.throw("Each field configuration must have a 'fieldname' property")
					if 'transformations' not in field:
						frappe.throw("Each field configuration must have a 'transformations' property")
						
			except json.JSONDecodeError as e:
				frappe.throw(f"Invalid JSON in normalize_fields_json: {str(e)}")
