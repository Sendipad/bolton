<!-- Process Method Configurator -->
<template>
  <div class="configurator process-configurator">
    <div class="config-section">
      <h5>Process Method</h5>
      
      <div class="form-group">
        <label>Method</label>
        <select v-model="localData.process_method" class="form-control" @change="onMethodChange">
          <option value="">Select method...</option>
          <option v-for="method in processMethods" :key="method.name" :value="method.name">
            {{ method.method_name }}
          </option>
        </select>
      </div>

      <div v-if="selectedMethod" class="method-info">
        <div class="info-badge" :class="`badge-${selectedMethod.category.toLowerCase()}`">
          {{ selected Method.category }}
        </div>
        <p class="method-description" v-html="selectedMethod.description"></p>
      </div>

      <div v-if="localData.process_method && schema" class="form-group">
        <label>Configuration</label>
        <textarea
          v-model="localData.configuration"
          class="form-control code-editor"
          rows="8"
          placeholder="{}"
          @blur="validateConfig"
        ></textarea>
        <small v-if="!configValid" class="text-danger">Invalid JSON</small>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  nodeData: Object,
  processMethods: Array
})

const emit = defineEmits(['update'])

const localData = ref({ ...props.nodeData })
const configValid = ref(true)

const selectedMethod = computed(() => {
  if (!localData.value.process_method) return null
  return props.processMethods.find(m => m.name === localData.value.process_method)
})

const schema = computed(() => {
  if (!selectedMethod.value?.config_schema) return null
  try {
    return JSON.parse(selectedMethod.value.config_schema)
  } catch {
    return null
  }
})

function onMethodChange() {
  // Set example configuration
  if (selectedMethod.value?.usage_example) {
    localData.value.configuration = selectedMethod.value.usage_example
  }
  emit('update')
}

function validateConfig() {
  try {
    if (localData.value.configuration) {
      JSON.parse(localData.value.configuration)
    }
    configValid.value = true
  } catch {
    configValid.value = false
  }
}

watch(localData, () => emit('update'), { deep: true })
</script>

<style scoped>
.method-info {
  margin-top: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 4px;
}

.info-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  margin-bottom: 8px;
}

.badge-validation { background: #e3f2fd; color: #1976d2; }
.badge-enrichment { background: #f3e5f5; color: #7b1fa2; }
.badge-notification { background: #fff3e0; color: #e65100; }
.badge-deduplication { background: #e8f5e9; color: #2e7d32; }

.method-description {
  font-size: 12px;
  color: #5a6c7d;
  margin: 0;
}

.code-editor {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
}
</style>
