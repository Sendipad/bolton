<!-- Condition Configurator -->
<template>
  <div class="configurator condition-configurator">
    <div class="config-section">
      <h5>Condition</h5>
      
      <div class="form-group">
        <label>Expression</label>
        <textarea
          v-model="localData.condition_expression"
          class="form-control code-editor"
          rows="4"
          placeholder="doc.field_name == 'value'"
          @input="updateData"
        ></textarea>
        <small class="help-text">
          Python expression. Available: doc, vars, frappe
        </small>
      </div>

      <div class="form-group">
        <label>
          <input type="checkbox" v-model="useJson" @change="toggleJson" />
          Use JSON Filters
        </label>
      </div>

      <div v-if="useJson" class="form-group">
        <label>JSON Condition</label>
        <textarea
          v-model="localData.condition_json"
          class="form-control code-editor"
          rows="6"
          placeholder='[["field", "=", "value"]]'
          @input="updateData"
        ></textarea>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  nodeData: Object
})

const emit = defineEmits(['update'])

const localData = ref({ ...props.nodeData })
const useJson = ref(!!props.nodeData.condition_json)

function toggleJson() {
  if (!useJson.value) {
    localData.value.condition_json = ''
  }
  updateData()
}

function updateData() {
  emit('update')
}

watch(localData, () => emit('update'), { deep: true })
</script>

<style scoped>
.code-editor {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
}

.help-text {
  display: block;
  margin-top: 4px;
  font-size: 11px;
  color: #7f8c8d;
}
</style>
