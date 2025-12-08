# Copyright (c) 2025, Bolton and contributors
# For license information, please see license.txt

import frappe

def execute():
    """
    Rename all Process Methods to use method_path as their name.
    Updates all Rule Action links accordingly.
    """
    # Get all Process Methods
    methods = frappe.get_all(
        "Process Method",
        fields=["name", "method_path"],
        filters={"method_path": ["is", "set"]}
    )
    
    # Track renames for Rule Action update
    rename_map = {}
    
    for method in methods:
        old_name = method.name
        new_name = method.method_path
        
        if old_name != new_name:
            # Check if target name already exists
            if frappe.db.exists("Process Method", new_name):
                # Delete the duplicate (old entry)
                frappe.delete_doc("Process Method", old_name, force=True)
            else:
                frappe.rename_doc(
                    "Process Method", 
                    old_name, 
                    new_name, 
                    merge=False,
                    force=True
                )
            rename_map[old_name] = new_name
            print(f"  Renamed: {old_name} -> {new_name}")
    
    # Update Rule Action links
    if rename_map:
        for old_name, new_name in rename_map.items():
            frappe.db.sql("""
                UPDATE `tabRule Action`
                SET process_method = %s
                WHERE process_method = %s
            """, (new_name, old_name))
        
        frappe.db.commit()
        print(f"  ✓ Updated Rule Action links")
    
    print(f"  ✓ Migration complete: {len(rename_map)} methods renamed")
