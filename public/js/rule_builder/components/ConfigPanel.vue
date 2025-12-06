<!-- Configuration Panel for Selected Node -->
<template>
  <div class="config-panel">
    <div v-if="!selectedNode" class="empty-state">
      <i class="fa fa-hand-pointer-o"></i>
      <p>Select a node to configure</p>
    </div>

    <div v-else class="panel-content">
      <div class="panel-header">
        <h4>{{ nodeTypeLabel }}</h4>
        <button @click="deleteNode" class="btn btn-sm btn-danger">
          <i class="fa fa-trash"></i>
        </button>
      </div>

      <!-- Common Fields -->
      <div class="config-section">
        <div class="form-group">
          <label>Label</label>
          <input
            v-model="nodeData.label"
            type="text"
            class="form-control"
            placeholder="Node label"
            @input="updateNodeData"
          />
        </div>

        <div class="form-group">
          <label>Description</label>
          <textarea
            v-model="nodeData.description"
            class="form-control"
            rows="2"
            placeholder="Optional description"
            @input="updateNodeData"
          ></textarea>
        </div>
      </div>

      <!-- Process Node Configuration -->
      <ProcessConfigurator
        v-if="selectedNode.type === 'process'"
        :node-data="nodeData"
        :process-methods="processMethods"
        @update="updateNodeData"
      />

      <!-- Condition Node Configuration -->
      <ConditionConfigurator
        v-if="selectedNode.type === 'condition'"
        :node-data="nodeData"
        @update="updateNodeData"
      />

      <!-- Flow Control -->
      <div class="config-section">
        <h5>Flow Control</h5>
        
        <div v-if="selectedNode.type === 'condition'" class="form-group">
          <label>Next if True</label>
          <input
            v-model="nodeData.next_step_if_true"
            type="text"
            class="form-control"
            placeholder="Action ID"
          />
        </div>

        <div v-if="selectedNode.type === 'condition'" class="form-group">
          <label>Next if False</label>
          <input
            v-model="nodeData.next_step_if_false"
            type="text"
            class="form-control"
            placeholder="Action ID"
          />
        </div>

        <div v-if="selectedNode.type === 'process'" class="form-group">
          <label>Next Step</label>
          <input
            v-model="nodeData.next_step_if_true"
            type="text"
            class="form-control"
            placeholder="Action ID"
          />
        </div>

        <div v-if="selectedNode.type === 'process'" class="form-group">
          <label>Return Variable</label>
          <input
            v-model="nodeData.return_variable"
            type="text"
            class="form-control"
            placeholder="Variable name"
          />
        </div>
      </div>

      <!-- Error Handling (for Process nodes) -->
      <div v-if="selectedNode.type === 'process'" class="config-section">
        <h5>Error Handling</h5>
        
        <div class="form-group">
          <label>On Error</label>
          <select v-model="nodeData.on_error" class="form-control" @change="updateNodeData">
            <option value="Stop">Stop Execution</option>
            <option value="Continue">Continue  to Next</option>
            <option value="Retry">Retry</option>
            <option value="Rollback">Rollback Transaction</option>
          </select>
        </div>

        <div v-if="nodeData.on_error === 'Retry'" class="form-group">
          <label>Retry Count</label>
          <input
            v-model.number="nodeData.retry_count"
            type="number"
            class="form-control"
            min="0"
            max="5"
            @input="updateNodeData"
          />
        </div>

        <div class="form-group">
          <label>Timeout (seconds)</label>
          <input
            v-model.number="nodeData.timeout"
            type="number"
            class="form-control"
            min="1"
            max="300"
            @input="updateNodeData"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import ProcessConfigurator from './configurators/ProcessConfigurator.vue'
import ConditionConfigurator from './configurators/ConditionConfigurator.vue'

// Props
const props = defineProps({
  selectedNode: {
    type: Object,
    default: null
  },
  processMethods: {
    type: Array,
    default: () => []
  }
})

// Emits
const emit = defineEmits(['update-node', 'delete-node'])

// State
const nodeData = ref({})

// Computed
const nodeTypeLabel = computed(() => {
  if (!props.selectedNode) return ''
  const typeLabels = {
    start: 'Start Node',
    process: 'Process Node',
    condition: 'Condition Node',
    stop: 'Stop Node'
  }
  return typeLabels[props.selectedNode.type] || 'Node'
})

// Watchers
watch(() => props.selectedNode, (newNode) => {
  if (newNode) {
    nodeData.value = { ...newNode.data }
  } else {
    nodeData.value = {}
  }
}, { immediate: true })

// Methods
function updateNodeData() {
  if (props.selectedNode) {
    emit('update-node', {
      id: props.selectedNode.id,
      data: nodeData.value
    })
  }
}

function deleteNode() {
  if (props.selectedNode) {
    emit('delete-node', props.selectedNode.id)
  }
}
</script>

<style scoped>
.config-panel {
  width: 320px;
  background: white;
  border-left: 1px solid #e0e6ed;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #95a5a6;
  padding: 40px 20px;
  text-align: center;
}

.empty-state i {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-state p {
  margin: 0;
  font-size: 14px;
  font-weight: 500;
}

.panel-content {
  flex: 1;
  overflow-y: auto;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e0e6ed;
  background: #f8f9fa;
  position: sticky;
  top: 0;
  z-index: 10;
}

.panel-header h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
}

.config-section {
  padding: 20px;
  border-bottom: 1px solid #f0f3f5;
}

.config-section h5 {
  margin: 0 0 16px 0;
  font-size: 12px;
  font-weight: 600;
  color: #7f8c8d;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-size: 12px;
  font-weight: 500;
  color: #5a6c7d;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 8px 12px;
  font-size: 13px;
  border: 1px solid #d1d8dd;
  border-radius: 4px;
  transition: all 0.2s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.form-group textarea {
  resize: vertical;
  font-family: inherit;
}
</style>
