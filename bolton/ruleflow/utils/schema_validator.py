# Copyright (c) 2025, Bolton and contributors
# For license information, please see license.txt

"""
JSON Schema validation utility for Bolton Rule Engine
"""

import frappe
from frappe import _
import json


def validate_json_schema(instance, schema):
	"""
	Validate a JSON instance against a JSON Schema
	
	Args:
		instance: JSON object to validate
		schema: JSON Schema to validate against
		
	Returns:
		Dict with 'valid' boolean and optional 'errors' list
	"""
	try:
		from jsonschema import validate, ValidationError, Draft7Validator
		
		# Validate the schema itself first
		Draft7Validator.check_schema(schema)
		
		# Validate the instance
		validate(instance=instance, schema=schema)
		
		return {
			'valid': True,
			'errors': []
		}
		
	except ImportError:
		frappe.logger().warning("jsonschema library not installed")
		return {
			'valid': True,
			'errors': [],
			'warning': 'jsonschema library not installed - validation skipped'
		}
		
	except ValidationError as e:
		return {
			'valid': False,
			'errors': [
				{
					'message': e.message,
					'path': list(e.path),
					'validator': e.validator
				}
			]
		}
		
	except Exception as e:
		return {
			'valid': False,
			'errors': [
				{
					'message': str(e),
					'path': [],
					'validator': 'schema'
				}
			]
		}


def validate_configuration(config_json, schema_json):
	"""
	Validate configuration JSON string against schema JSON string
	
	Args:
		config_json: JSON string of configuration
		schema_json: JSON string of schema
		
	Returns:
		Dict with validation result
	"""
	try:
		config = json.loads(config_json) if isinstance(config_json, str) else config_json
		schema = json.loads(schema_json) if isinstance(schema_json, str) else schema_json
		
		return validate_json_schema(config, schema)
		
	except json.JSONDecodeError as e:
		return {
			'valid': False,
			'errors': [
				{
					'message': f'Invalid JSON: {str(e)}',
					'path': [],
					'validator': 'json'
				}
			]
		}


def get_schema_fields(schema):
	"""
	Extract field definitions from JSON Schema
	
	Args:
		schema: JSON Schema object or string
		
	Returns:
		List of field definitions with name, type, description, etc.
	"""
	if isinstance(schema, str):
		try:
			schema = json.loads(schema)
		except json.JSONDecodeError:
			return []
	
	if not isinstance(schema, dict):
		return []
	
	fields = []
	properties = schema.get('properties', {})
	required_fields = schema.get('required', [])
	
	for field_name, field_schema in properties.items():
		field_def = {
			'name': field_name,
			'type': field_schema.get('type', 'string'),
			'description': field_schema.get('description', ''),
			'required': field_name in required_fields,
			'default': field_schema.get('default'),
			'enum': field_schema.get('enum'),
			'minimum': field_schema.get('minimum'),
			'maximum': field_schema.get('maximum'),
			'pattern': field_schema.get('pattern')
		}
		
		# Handle oneOf (union types)
		if 'oneOf' in field_schema:
			types = [opt.get('type') for opt in field_schema['oneOf']]
			field_def['types'] = types
		
		# Handle array items
		if field_schema.get('type') == 'array' and 'items' in field_schema:
			field_def['item_type'] = field_schema['items'].get('type')
		
		# Handle object properties
		if field_schema.get('type') == 'object' and 'properties' in field_schema:
			field_def['nested_fields'] = get_schema_fields(field_schema)
		
		fields.append(field_def)
	
	return fields


def generate_default_config(schema):
	"""
	Generate default configuration from JSON Schema
	
	Args:
		schema: JSON Schema object or string
		
	Returns:
		Dict with default values based on schema
	"""
	if isinstance(schema, str):
		try:
			schema = json.loads(schema)
		except json.JSONDecodeError:
			return {}
	
	if not isinstance(schema, dict):
		return {}
	
	config = {}
	properties = schema.get('properties', {})
	
	for field_name, field_schema in properties.items():
		# Use default if specified
		if 'default' in field_schema:
			config[field_name] = field_schema['default']
		
		# Otherwise use type-based defaults
		elif field_schema.get('type') == 'string':
			config[field_name] = ''
		elif field_schema.get('type') == 'number':
			config[field_name] = 0
		elif field_schema.get('type') == 'integer':
			config[field_name] = 0
		elif field_schema.get('type') == 'boolean':
			config[field_name] = False
		elif field_schema.get('type') == 'array':
			config[field_name] = []
		elif field_schema.get('type') == 'object':
			config[field_name] = {}
	
	return config


def validate_field_type(value, field_type):
	"""
	Validate a value matches the expected type
	
	Args:
		value: Value to validate
		field_type: Expected type (string, number, boolean, etc.)
		
	Returns:
		Boolean indicating if type matches
	"""
	type_map = {
		'string': str,
		'number': (int, float),
		'integer': int,
		'boolean': bool,
		'array': list,
		'object': dict,
		'null': type(None)
	}
	
	expected_type = type_map.get(field_type)
	if not expected_type:
		return True  # Unknown type, accept
	
	return isinstance(value, expected_type)
