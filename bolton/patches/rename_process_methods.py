# Copyright (c) 2025, Bolton and contributors
# For license information, please see license.txt

"""
Migration patch: Rename Process Method documents from method_name to method_path
This is required because autoname is changing from field:method_name to field:method_path
"""

import frappe


def execute():
    """
    Rename all Process Method documents from method_name to method_path
    """
    # Check if we need to run this migration
    if not frappe.db.exists("DocType", "Process Method"):
        return
    
    # Get all process methods
    process_methods = frappe.get_all(
        "Process Method",
        fields=["name", "method_name", "method_path"]
    )
    
    for pm in process_methods:
        old_name = pm.name
        new_name = pm.method_path
        
        # Skip if already renamed (name equals method_path)
        if old_name == new_name:
            continue
        
        # Skip if new_name is empty
        if not new_name:
            print(f"Skipped {old_name}: method_path is empty")
            continue
        
        try:
            # Check if new name already exists
            if frappe.db.exists("Process Method", new_name):
                # Delete the old record since the new one already has correct name
                print(f"Deleting duplicate {old_name} (target {new_name} already exists)")
                frappe.delete_doc("Process Method", old_name, force=True, ignore_permissions=True)
                frappe.db.commit()
                continue
            
            # Rename the document
            frappe.rename_doc("Process Method", old_name, new_name, merge=False)
            frappe.db.commit()
            
            # Update references in Rule Action child table
            frappe.db.sql("""
                UPDATE `tabRule Action` 
                SET process_method = %s 
                WHERE process_method = %s
            """, (new_name, old_name))
            frappe.db.commit()
            
            print(f"Renamed Process Method: {old_name} -> {new_name}")
            
        except Exception as e:
            print(f"Failed to process {old_name}: {str(e)}")
            frappe.db.rollback()
    
    # Clear cache
    frappe.clear_cache()

