// Rule API Integration
export function useRuleAPI() {
    async function loadRule(ruleName) {
        return await frappe.call({
            method: 'bolton.ruleflow.api.get_rule',
            args: { rule_name: ruleName }
        }).then(r => r.message)
    }

    async function saveRuleFlow(ruleName, actions) {
        return await frappe.call({
            method: 'bolton.ruleflow.api.save_rule_flow',
            args: {
                rule_name: ruleName,
                actions: JSON.stringify(actions)
            }
        }).then(r => r.message)
    }

    async function getProcessMethods(category = null) {
        return await frappe.call({
            method: 'bolton.ruleflow.api.get_process_methods',
            args: { category }
        }).then(r => r.message)
    }

    async function testRuleExecution(ruleName, documentName) {
        return await frappe.call({
            method: 'bolton.ruleflow.api.test_rule',
            args: {
                rule_name: ruleName,
                document_name: documentName
            }
        }).then(r => r.message)
    }

    return {
        loadRule,
        saveRuleFlow,
        getProcessMethods,
        testRuleExecution
    }
}
