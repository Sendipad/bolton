app_name = "bolton"
app_title = "Bolton"
app_publisher = "Abdo Ruzaqi"
app_description = "Business Rule Hub for Master Data Management and Data Quality"
app_email = "ruzaqi@gmail.com"
app_license = "agpl-3.0"

# JS/CSS includes
app_include_css = "/assets/bolton/css/bolton.css"
app_include_js = "/assets/bolton/js/rule_builder.bundle.js"

# Document Events - ALL paths must be to MODULE-LEVEL functions
# NEVER use class method paths like "module.ClassName.method"
doc_events = {
    "*": {
        "before_insert": "bolton.ruleflow.hooks.execute_rules",
        "before_save": "bolton.ruleflow.hooks.execute_rules",
        "validate": "bolton.ruleflow.hooks.execute_rules",
        "after_insert": "bolton.ruleflow.hooks.execute_rules",
        "after_save": "bolton.ruleflow.hooks.execute_rules",
        "before_submit": "bolton.ruleflow.hooks.execute_rules",
        "on_submit": "bolton.ruleflow.hooks.execute_rules",
        "before_cancel": "bolton.ruleflow.hooks.execute_rules",
        "on_cancel": "bolton.ruleflow.hooks.execute_rules",
        "on_trash": "bolton.ruleflow.hooks.execute_rules",
    },
    "Rule": {
        "after_save": "bolton.ruleflow.hooks.clear_rule_cache",
        "on_trash": "bolton.ruleflow.hooks.clear_rule_cache"
    }
}

doctype_js = {
    "Rule": "ruleflow/doctype/rule/rule.js"
}

fixtures = [
    {
        "dt": "Process Method",
        "filters": [["module", "=", "Ruleflow"]]
    }
]

bolton_excluded_doctypes = [
    "Error Log",
    "Activity Log", 
    "Access Log",
    "Email Queue",
    "Scheduled Job Log",
    "Version",
    "Comment",
    "Communication",
    "File"
]

export_python_type_annotations = True
