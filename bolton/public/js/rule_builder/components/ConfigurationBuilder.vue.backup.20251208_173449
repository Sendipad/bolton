<template>
    <div class="config-builder">
        <div class="config-header">
            <h6>{{ __("Configure Process Method") }}</h6>
            <button class="btn btn-xs btn-secondary" @click="clearAll">{{ __("Clear All") }}</button>
        </div>
        
        <div class="config-body">
            <div v-for="field in fields" :key="field.fieldname" class="form-group">
                <label>
                    {{ __(field.label) }}
                    <span v-if="field.reqd" class="text-danger">*</span>
                </label>
                
                <!-- Autocomplete for DocType fields -->
                <div v-if="field.fieldtype === 'Autocomplete'" class="autocomplete-wrapper">
                    <input 
                        type="text"
                        class="form-control form-control-sm"
                        :value="values[field.fieldname]"
                        @input="updateValue(field.fieldname, $event.target.value)"
                        :placeholder="field.description"
                        @focus="showAutocomplete(field)"
                    />
                    <div v-if="autocompleteField === field.fieldname && fieldOptions.length" class="autocomplete-results">
                        <div 
                            v-for="opt in fieldOptions" 
                            :key="opt.value"
                            class="autocomplete-item"
                            @click="selectAutocomplete(field.fieldname, opt.value)"
                        >
                            <strong>{{ opt.value }}</strong>
                            <small class="text-muted">{{ opt.description }}</small>
                        </div>
                    </div>
                </div>
                
                <!-- Select dropdown -->
                <select 
                    v-else-if="field.fieldtype === 'Select'"
                    class="form-control form-control-sm"
                    :value="values[field.fieldname]"
                    @change="updateValue(field.fieldname, $event.target.value)"
                >
                    <option value="">{{ __("Select...") }}</option>
                    <option v-for="opt in field.options.split('\n')" :key="opt" :value="opt">
                        {{ __(opt) }}
                    </option>
                </select>
                
                <!-- Checkbox -->
                <input 
                    v-else-if="field.fieldtype === 'Check'"
                    type="checkbox"
                    :checked="values[field.fieldname]"
                    @change="updateValue(field.fieldname, $event.target.checked)"
                />
                
                <!-- Code editor -->
                <textarea 
                    v-else-if="field.fieldtype === 'Code' || field.fieldtype === 'Small Text'"
                    class="form-control form-control-sm"
                    :value="values[field.fieldname]"
                    @input="updateValue(field.fieldname, $event.target.value)"
                    :placeholder="field.description"
                    rows="3"
                ></textarea>
                
                <!-- Number input -->
                <input 
                    v-else-if="field.fieldtype === 'Int' || field.fieldtype === 'Float'"
                    type="number"
                    class="form-control form-control-sm"
                    :value="values[field.fieldname]"
                    @input="updateValue(field.fieldname, $event.target.value)"
                    :step="field.fieldtype === 'Float' ? '0.01' : '1'"
                />
                
                <!-- Default text input -->
                <input 
                    v-else
                    type="text"
                    class="form-control form-control-sm"
                    :value="values[field.fieldname]"
                    @input="updateValue(field.fieldname, $event.target.value)"
                    :placeholder="field.description"
                />
                
                <small v-if="field.description" class="form-text text-muted">
                    {{ field.description }}
                </small>
            </div>
        </div>
        
        <div v-if="validationErrors.length" class="alert alert-danger">
            <ul class="mb-0">
                <li v-for="error in validationErrors" :key="error">{{ error }}</li>
            </ul>
        </div>
    </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue';
import { parseSchemaToFields, validateConfigAgainstSchema } from '../utils/schemaParser.js';

const props = defineProps({
    schema: Object,
    modelValue: [String, Object],
    documentType: String
});

const emit = defineEmits(['update:modelValue', 'validation-change']);

const fields = ref([]);
const values = ref({});
const autocompleteField = ref(null);
const fieldOptions = ref([]);
const validationErrors = ref([]);

watch(() => props.schema, (schema) => {
    if (!schema) {
        fields.value = [];
        return;
    }
    fields.value = parseSchemaToFields(schema, props.documentType);
}, { immediate: true });

watch(() => props.modelValue, (val) => {
    try {
        values.value = typeof val === 'string' ? JSON.parse(val) : (val || {});
    } catch (e) {
        values.value = {};
    }
    validate();
}, { immediate: true });

function updateValue(fieldname, value) {
    values.value[fieldname] = value;
    emit('update:modelValue', JSON.stringify(values.value));
    validate();
}

function validate() {
    const result = validateConfigAgainstSchema(values.value, props.schema);
    validationErrors.value = result.errors || [];
    emit('validation-change', result.valid);
}

function showAutocomplete(field) {
    if (field.options && typeof field.options === 'function') {
        fieldOptions.value = field.options();
        autocompleteField.value = field.fieldname;
    }
}

function selectAutocomplete(fieldname, value) {
    updateValue(fieldname, value);
    autocompleteField.value = null;
    fieldOptions.value = [];
}

function clearAll() {
    values.value = {};
    emit('update:modelValue', '{}');
    validate();
}
</script>

<style scoped>
.config-builder {
    max-height: 500px;
    overflow-y: auto;
}
.config-header {
    display: flex;
    justify-content: space-between;
    padding: 10px;
    border-bottom: 1px solid var(--border-color);
    position: sticky;
    top: 0;
    background: white;
    z-index: 1;
}
.config-body {
    padding: 15px;
}
.form-group {
    margin-bottom: 15px;
}
.form-group label {
    font-size: 13px;
    font-weight: 500;
    margin-bottom: 5px;
    display: block;
}
.autocomplete-wrapper {
    position: relative;
}
.autocomplete-results {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: white;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    max-height: 200px;
    overflow-y: auto;
    z-index: 10;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.autocomplete-item {
    padding: 8px 12px;
    cursor: pointer;
    display: flex;
    flex-direction: column;
}
.autocomplete-item:hover {
    background: var(--bg-light-gray);
}
.autocomplete-item strong {
    font-size: 13px;
}
.autocomplete-item small {
    font-size: 11px;
}
.alert {
    margin: 10px;
    font-size: 12px;
}
</style>
