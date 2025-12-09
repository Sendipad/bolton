<template>
    <div class="rule-sidebar">
        <div class="sidebar-header">
            <h4>{{ selectedNode?.data?.action_label || selectedNode?.label || 'Properties' }}</h4>
            <button class="btn-close" @click="$emit('close')">×</button>
        </div>
        
        <div class="sidebar-content" v-if="selectedNode">
            <!-- Start Node -->
            <template v-if="selectedNode.type === 'start'">
                <div class="form-group">
                    <label>Document Type</label>
                    <input type="text" class="form-control" :value="selectedNode.data?.document_type" readonly />
                </div>
                <div class="form-group">
                    <label>Trigger Event</label>
                    <input type="text" class="form-control" :value="selectedNode.data?.trigger_event" readonly />
                </div>
            </template>
            
            <!-- Action Nodes -->
            <template v-else>
                <div class="form-group">
                    <label>Label</label>
                    <input type="text" class="form-control" 
                        :value="selectedNode.label"
                        @input="updateLabel($event.target.value)" />
                </div>
                
                <div class="form-group">
                    <label>Type</label>
                    <select class="form-control" 
                        :value="selectedNode.data?.action_type"
                        @change="updateActionType($event.target.value)">
                        <option value="Process">Process</option>
                        <option value="Condition">Condition</option>
                        <option value="Stop">Stop</option>
                    </select>
                </div>
                
                <template v-if="selectedNode.data?.action_type === 'Process'">
                    <div class="form-group">
                        <label>Method</label>
                        <select class="form-control"
                            :value="selectedNode.data?.process_method"
                            @change="updateProcessMethod($event.target.value)">
                            <option value="">-- Select --</option>
                            <option v-for="m in store.process_methods" :key="m.name" :value="m.name">
                                {{ m.method_name }}
                            </option>
                        </select>
                    </div>
                    
                    <button v-if="selectedNode.data?.process_method"
                        class="btn btn-sm btn-default w-100" 
                        @click="openConfigDialog">
                        <i class="fa fa-cog"></i> Configure
                    </button>
                </template>
                
                <div class="form-group" v-if="selectedNode.data?.action_type === 'Condition'">
                    <label>Expression</label>
                    <textarea class="form-control" rows="3"
                        :value="selectedNode.data?.condition_expression"
                        @input="updateField('condition_expression', $event.target.value)"
                        placeholder="doc.status == 'Active'"></textarea>
                </div>
                
                <div class="form-group" v-if="selectedNode.type !== 'stop'">
                    <label>{{ selectedNode.data?.action_type === 'Condition' ? 'If True →' : 'Next →' }}</label>
                    <select class="form-control"
                        :value="selectedNode.data?.next_step_if_true"
                        @change="updateNextStep('next_step_if_true', $event.target.value)">
                        <option value="">End Flow</option>
                        <option v-for="node in availableNextNodes" :key="node.id" :value="node.id">
                            {{ node.label }}
                        </option>
                    </select>
                </div>
                
                <div class="form-group" v-if="selectedNode.data?.action_type === 'Condition'">
                    <label>If False →</label>
                    <select class="form-control"
                        :value="selectedNode.data?.next_step_if_false"
                        @change="updateNextStep('next_step_if_false', $event.target.value)">
                        <option value="">End Flow</option>
                        <option v-for="node in availableNextNodes" :key="node.id" :value="node.id">
                            {{ node.label }}
                        </option>
                    </select>
                </div>
                
                <hr />
                
                <label class="checkbox-label">
                    <input type="checkbox" 
                        :checked="selectedNode.data?.is_enabled !== 0"
                        @change="updateField('is_enabled', $event.target.checked ? 1 : 0)" />
                    Enabled
                </label>
                
                <button class="btn btn-sm btn-danger w-100 mt-3" @click="deleteNode">
                    <i class="fa fa-trash"></i> Delete
                </button>
            </template>
        </div>
    </div>
</template>

<script setup>
import { computed } from 'vue';
import { useStore } from '../store';

const emit = defineEmits(['close']);
const store = useStore();

const selectedNode = computed(() => store.graph.selected);

const availableNextNodes = computed(() => {
    return store.graph.elements
        .filter(el => el.position && el.id !== selectedNode.value?.id && el.id !== 'start')
        .map(el => ({ id: el.id, label: el.label || el.id }));
});

function updateLabel(value) {
    if (!selectedNode.value) return;
    selectedNode.value.label = value;
    if (selectedNode.value.data) selectedNode.value.data.action_label = value;
    store.mark_dirty();
}

function updateField(field, value) {
    if (!selectedNode.value?.data) return;
    selectedNode.value.data[field] = value;
    store.mark_dirty();
}

function updateActionType(value) {
    if (!selectedNode.value) return;
    selectedNode.value.type = value.toLowerCase();
    if (selectedNode.value.data) selectedNode.value.data.action_type = value;
    store.mark_dirty();
}

function updateProcessMethod(value) {
    if (!selectedNode.value?.data) return;
    selectedNode.value.data.process_method = value;
    selectedNode.value.data.configuration = null;
    store.mark_dirty();
}

function updateNextStep(field, value) {
    if (!selectedNode.value?.data) return;
    selectedNode.value.data[field] = value || null;
    updateEdge(field, value);
    store.mark_dirty();
}

function updateEdge(field, newTarget) {
    const nodeId = selectedNode.value.id;
    const handleType = field === 'next_step_if_true' ? 
        (selectedNode.value.data?.action_type === 'Condition' ? 'true' : 'default') : 'false';
    
    store.graph.elements = store.graph.elements.filter(el => 
        !(el.source === nodeId && el.sourceHandle === handleType)
    );
    
    if (newTarget) {
        store.graph.elements.push({
            id: `e-${nodeId}-${newTarget}-${handleType}`,
            source: nodeId,
            target: newTarget,
            sourceHandle: handleType
        });
    }
}

function deleteNode() {
    if (selectedNode.value) {
        store.delete_node(selectedNode.value.id);
        emit('close');
    }
}

async function openConfigDialog() {
    const methodName = selectedNode.value?.data?.process_method;
    if (!methodName) return;
    
    const schema = await store.get_process_method_schema(methodName);
    if (!schema?.fields) {
        frappe.msgprint(__('No configuration available'));
        return;
    }
    
    const parentDoctype = store.rule_doc?.document_type;
    const childTables = schema.child_tables || {};
    const dialogFields = await buildDialogFields(schema.fields, parentDoctype, childTables);
    
    // Parse current config
    let currentConfig = {};
    try {
        const configStr = selectedNode.value.data?.configuration;
        if (configStr && configStr !== '{}' && configStr !== 'null') {
            currentConfig = JSON.parse(configStr);
        }
    } catch (e) {
        console.error('Failed to parse configuration:', e);
    }
    
    // Pre-populate Table field data in the field definitions
    dialogFields.forEach(f => {
        if (f.fieldtype === 'Table' && currentConfig[f.fieldname]) {
            f.data = currentConfig[f.fieldname];
        } else if (currentConfig[f.fieldname] !== undefined && f.fieldtype !== 'Table') {
            f.default = currentConfig[f.fieldname];
        }
    });
    
    const dialog = new frappe.ui.Dialog({
        title: schema.method_name || methodName,
        fields: dialogFields,
        size: 'large',
        primary_action_label: __('Save'),
        primary_action: () => {
            const values = dialog.get_values();
            if (values) {
                // For Table fields, get data from grid
                dialogFields.forEach(f => {
                    if (f.fieldtype === 'Table') {
                        const field = dialog.fields_dict[f.fieldname];
                        if (field && field.grid) {
                            values[f.fieldname] = field.grid.get_data();
                        }
                    }
                });
                
                selectedNode.value.data.configuration = JSON.stringify(values);
                store.mark_dirty();
                frappe.show_alert({ message: __('Configuration saved'), indicator: 'green' });
            }
            dialog.hide();
        }
    });
    
    dialog.show();
    
    // For Table fields, refresh grid with data after dialog is shown
    setTimeout(() => {
        dialogFields.forEach(f => {
            if (f.fieldtype === 'Table' && currentConfig[f.fieldname]) {
                const field = dialog.fields_dict[f.fieldname];
                if (field && field.grid) {
                    // Clear and set data
                    field.grid.df.data = currentConfig[f.fieldname];
                    field.grid.refresh();
                }
            }
        });
        
        // Set non-table values
        const nonTableConfig = {};
        Object.keys(currentConfig).forEach(key => {
            const field = dialogFields.find(f => f.fieldname === key);
            if (field && field.fieldtype !== 'Table') {
                nonTableConfig[key] = currentConfig[key];
            }
        });
        if (Object.keys(nonTableConfig).length > 0) {
            dialog.set_values(nonTableConfig);
        }
    }, 150);
}

async function buildDialogFields(schemaFields, parentDoctype, childTables = {}) {
    const fields = [];
    
    for (const field of schemaFields) {
        const mapped = await mapSchemaField(field, parentDoctype, childTables);
        if (mapped) {
            // Handle array of fields (e.g., Table expands to label + table)
            if (Array.isArray(mapped)) {
                fields.push(...mapped);
            } else {
                fields.push(mapped);
            }
        }
    }
    
    return fields;
}

async function mapSchemaField(field, parentDoctype, childTables) {
    const { fieldname, fieldtype, label, reqd, options, description } = field;
    const defaultVal = field.default;
    
    switch (fieldtype) {
        case 'DocField':
            // Single field picker → Autocomplete
            return {
                fieldname,
                fieldtype: 'Autocomplete',
                label,
                reqd,
                description,
                options: await getFieldOptions(options, parentDoctype)
            };
        
        case 'MultiDocField':
            // Multi field picker → MultiCheck with checkboxes
            const multiOptions = await getFieldOptions(options, parentDoctype);
            return {
                fieldname,
                fieldtype: 'MultiCheck',
                label,
                reqd,
                description,
                options: multiOptions,
                columns: 2,
                select_all: true
            };
        
        case 'Table':
            // Inline table → Table control with child fields
            const childSchema = childTables[options] || [];
            if (!childSchema.length) {
                console.warn(`No child_tables definition for: ${options}`);
                return null;
            }
            
            // Map child fields recursively
            const childFields = [];
            for (const cf of childSchema) {
                const mappedChild = await mapSchemaField(cf, parentDoctype, {});
                if (mappedChild && !Array.isArray(mappedChild)) {
                    // For table child fields, convert Autocomplete to Data with options
                    if (mappedChild.fieldtype === 'Autocomplete') {
                        mappedChild.fieldtype = 'Select';
                        mappedChild.options = mappedChild.options?.map(o => o.value || o).join('\n') || '';
                    }
                    if (mappedChild.fieldtype === 'MultiCheck') {
                        mappedChild.fieldtype = 'Select';
                        mappedChild.options = mappedChild.options?.map(o => o.value || o).join('\n') || '';
                    }
                    mappedChild.in_list_view = 1;
                    childFields.push(mappedChild);
                }
            }
            
            return {
                fieldname,
                fieldtype: 'Table',
                label,
                reqd,
                description,
                fields: childFields,
                data: [],
                cannot_add_rows: false,
                in_place_edit: true
            };
        
        case 'MultiSelect':
            // Multi-select → MultiCheck
            const selectOpts = parseSelectOptions(options);
            return {
                fieldname,
                fieldtype: 'MultiCheck',
                label,
                reqd,
                description,
                options: selectOpts,
                columns: 2
            };
        
        case 'Percent':
            // Percent → Float with description
            return {
                fieldname,
                fieldtype: 'Float',
                label,
                reqd,
                description: description || 'Value from 0-100',
                default: defaultVal
            };
        
        default:
            // Standard Frappe fieldtype - pass through
            return {
                fieldname,
                fieldtype,
                label,
                reqd,
                options,
                description,
                default: defaultVal
            };
    }
}

async function getFieldOptions(optionsRef, parentDoctype) {
    let targetDoctype = parentDoctype;
    
    if (optionsRef === 'parent.document_type') {
        targetDoctype = parentDoctype;
    } else if (optionsRef && !optionsRef.includes('.')) {
        targetDoctype = optionsRef;
    }
    
    if (!targetDoctype) return [];
    
    try {
        const result = await frappe.call({
            method: 'bolton.ruleflow.api.get_doctype_fields',
            args: { doctype: targetDoctype }
        });
        
        if (result.message?.parent_fields) {
            const opts = result.message.parent_fields.map(f => ({
                value: f.value,
                label: `${f.label} (${f.fieldtype})`
            }));
            
            // Add child table fields
            if (result.message.child_tables) {
                result.message.child_tables.forEach(table => {
                    opts.push({ value: '', label: `── ${table.table_label} ──`, disabled: true });
                    table.fields.forEach(f => {
                        opts.push({ value: f.value, label: `  ${f.label}` });
                    });
                });
            }
            
            return opts;
        }
    } catch (e) {
        console.error('Failed to fetch field options:', e);
    }
    
    return [];
}

function parseSelectOptions(options) {
    if (!options) return [];
    return options.split('\n').filter(Boolean).map(opt => ({
        value: opt.trim(),
        label: opt.trim()
    }));
}

</script>

<style scoped>
.rule-sidebar {
    width: 280px;
    height: 100%;
    display: flex;
    flex-direction: column;
}

.sidebar-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 15px;
    border-bottom: 1px solid var(--border-color);
}

.sidebar-header h4 {
    margin: 0;
    font-size: 14px;
    font-weight: 600;
}

.btn-close {
    background: none;
    border: none;
    font-size: 18px;
    cursor: pointer;
    color: var(--text-muted);
    padding: 0;
}

.sidebar-content {
    flex: 1;
    padding: 15px;
    overflow-y: auto;
}

.form-group {
    margin-bottom: 12px;
}

.form-group label {
    display: block;
    font-size: 11px;
    font-weight: 500;
    margin-bottom: 4px;
    color: var(--text-muted);
    text-transform: uppercase;
}

.form-control {
    width: 100%;
    padding: 6px 10px;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    font-size: 13px;
}

.checkbox-label {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
}

hr {
    margin: 15px 0;
    border: none;
    border-top: 1px solid var(--border-color);
}

.w-100 { width: 100%; }
.mt-3 { margin-top: 15px; }
</style>
