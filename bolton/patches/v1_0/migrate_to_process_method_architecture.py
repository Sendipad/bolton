# Copyright (c) 2025, Bolton and contributors
# For license information, please see license.txt

"""
Migration patch to upgrade to Process Method architecture
Migrates existing rules to use the new Process Method DocType
"""

import frappe
import json
import uuid
from frappe import _


def execute():
	"""
	Main migration function
	"""
	frappe.logger().info("Starting Bolton architecture migration...")
	
	try:
		# 1. Update Rule DocType fields
		update_rule_fields()
		
		# 2. Create Process Methods from Rule Actions
		create_process_methods_from_actions()
		
		# 3. Update Rule Actions to link to Process Methods
		update_rule_actions()
		
		# 4. Clean up legacy fields
		cleanup_legacy_data()
		
		# 5. Clear all rule caches
		clear_caches()
		
		frappe.logger().info("Bolton architecture migration completed successfully")
		
	except Exception as e:
		frappe.log_error(
			title="Bolton Migration Failed",
			message=frappe.get_traceback()
		)
		raise


def update_rule_fields():
	"""Add default values for new fields in Rule DocType"""
	frappe.logger().info("Updating Rule fields...")
	
	rules = frappe.get_all('Rule', fields=['name'])
	
	for rule in rules:
		try:
			# Set defaults for new fields
			frappe.db.set_value(
				'Rule',
				rule.name,
				{
					'execution_mode': 'Synchronous',
					'max_execution_time': 30,
					'apply_to_child_tables': 0
				},
				update_modified=False
			)
		except Exception as e:
			frappe.logger().error(f"Failed to update Rule {rule.name}: {str(e)}")
	
	frappe.db.commit()
	frappe.logger().info(f"Updated {len(rules)} rules")


def create_process_methods_from_actions():
	"""
	Create Process Method records from unique action_method values in Rule Actions
	"""
	frappe.logger().info("Creating Process Methods from existing actions...")
	
	# Get unique action methods from Rule Action
	# Note: action_method field may not exist in new schema, so we skip this
	# if migrating from a version that never had action_method
	
	# Check if action_method field exists
	meta = frappe.get_meta('Rule Action')
	if not meta.has_field('action_method'):
		frappe.logger().info("No legacy action_method field found, skipping process method creation")
		return
	
	# Get unique methods
	existing_methods = frappe.db.sql("""
		SELECT DISTINCT action_method
		FROM `tabRule Action`
		WHERE action_method IS NOT NULL
		AND action_method != ''
		AND action_type = 'Action'
	""", as_dict=True)
	
	created_count = 0
	
	for row in existing_methods:
		method_path = row.get('action_method')
		if not method_path:
			continue
		
		# Generate method name from path
		method_name = method_path.split('.')[-1].replace('_', ' ').title()
		
		# Check if already exists
		if frappe.db.exists('Process Method', {'method_path': method_path}):
			frappe.logger().info(f"Process Method for {method_path} already exists")
			continue
		
		try:
			# Create Process Method
			process_method = frappe.get_doc({
				'doctype': 'Process Method',
				'method_name': method_name,
				'method_path': method_path,
				'category': 'Custom',
				'description': f'<p>Migrated from legacy action method</p>',
				'is_enabled': 1,
				'return_type': 'None',
				'version': '1.0'
			})
			
			process_method.insert(ignore_permissions=True)
			created_count += 1
			
		except Exception as e:
			frappe.logger().error(f"Failed to create Process Method for {method_path}: {str(e)}")
	
	frappe.db.commit()
	frappe.logger().info(f"Created {created_count} Process Methods")


def update_rule_actions():
	"""
	Update Rule Actions with new fields and link to Process Methods
	"""
	frappe.logger().info("Updating Rule Actions...")
	
	actions = frappe.get_all('Rule Action', fields=['name', 'parent', 'parentfield', 'parenttype'])
	
	updated_count = 0
	
	for action in actions:
		try:
			# Load full action
			action_doc = frappe.get_doc('Rule Action', action.name)
			
			# Generate action_id if missing
			if not action_doc.get('action_id'):
				action_doc.action_id = str(uuid.uuid4())[:8]
			
			# Set is_enabled default
			if not hasattr(action_doc, 'is_enabled'):
				action_doc.is_enabled = 1
			
			# Update action_type mapping
			if action_doc.action_type == 'Action':
				action_doc.action_type = 'Process'
				
				# Link to Process Method if action_method exists
				if hasattr(action_doc, 'action_method') and action_doc.action_method:
					# Find corresponding Process Method
					process_method = frappe.db.get_value(
						'Process Method',
						{'method_path': action_doc.action_method},
						'name'
					)
					
					if process_method:
						action_doc.process_method = process_method
					else:
						frappe.logger().warning(
							f"No Process Method found for action_method: {action_doc.action_method}"
						)
			
			# Set default error handling
			if action_doc.action_type == 'Process':
				if not action_doc.get('on_error'):
					action_doc.on_error = 'Stop'
				if not action_doc.get('timeout'):
					action_doc.timeout = 30
				if not action_doc.get('retry_count'):
					action_doc.retry_count = 0
			
			# Save without triggering validations (direct DB update)
			action_doc.db_update()
			updated_count += 1
			
		except Exception as e:
			frappe.logger().error(f"Failed to update Rule Action {action.name}: {str(e)}")
	
	frappe.db.commit()
	frappe.logger().info(f"Updated {updated_count} Rule Actions")


def cleanup_legacy_data():
	"""
	Clean up legacy fields and data
	"""
	frappe.logger().info("Cleaning up legacy data...")
	
	# Remove rule_type and options_json data from Rule
	try:
		frappe.db.sql("""
			UPDATE `tabRule`
			SET rule_type = NULL,
			    options_json = NULL
		""")
		frappe.db.commit()
		frappe.logger().info("Cleaned up legacy Rule fields")
	except Exception as e:
		frappe.logger().error(f"Failed to clean up Rule fields: {str(e)}")
	
	# Note: We keep action_method field for reference, can be removed in future version


def clear_caches():
	"""Clear all rule-related caches"""
	frappe.logger().info("Clearing rule caches...")
	
	try:
		frappe.cache().delete_keys("rules:*")
		frappe.cache().delete_keys("has_rules:*")
		frappe.clear_cache(doctype='Rule')
		frappe.clear_cache(doctype='Rule Action')
		frappe.clear_cache(doctype='Process Method')
		
		frappe.logger().info("Caches cleared successfully")
	except Exception as e:
		frappe.logger().error(f"Failed to clear caches: {str(e)}")
