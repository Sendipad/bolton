<!-- Main Rule Builder Vue Application -->
<template>
  <div class="rule-builder-app">
    <!-- Main Layout -->
    <div class="builder-layout">
      <!-- Left Sidebar - Node Palette -->
      <NodePalette />

      <!-- Center - Canvas -->
      <div class="canvas-container">
        <RuleCanvas
          v-model:nodes="nodes"
          v-model:edges="edges"
          @node-click="onNodeClick"
          @selection-change="onSelectionChange"
        />
      </div>

      <!-- Right Sidebar - Configuration Panel -->
      <ConfigPanel
        :selected-node="selectedNode"
        :process-methods="processMethods"
        @update-node="updateNode"
      />
    </div>

    <!-- Bottom Panel - Test Results (when visible) -->
    <div v-if="showTestResults" class="test-results-panel">
      <div class="panel-header">
        <h4>Test Results</h4>
        <button @click="showTestResults = false" class="btn btn-sm btn-default">
          <i class="fa fa-times"></i>
        </button>
      </div>
      <div class="panel-content">
        <div v-if="testResults.success" class="alert alert-success">
          ✓ Rule executed successfully
        </div>
        <div v-else class="alert alert-danger">
          ✗ Rule execution failed: {{ testResults.error }}
        </div>
        
        <div class="execution-log">
          <h5>Execution Log:</h5>
          <div v-for="(log, idx) in testResults.execution_log" :key="idx" class="log-entry" :class="`log-${log.level.toLowerCase()}`">
            <span class="log-time">{{ log.timestamp }}</span>
            <span class="log-level">{{ log.level }}</span>
            <span class="log-message">{{ log.message }}</span>
          </div>
        </div>

        <div v-if="testResults.context" class="context-vars">
          <h5>Variables:</h5>
          <pre>{{ JSON.stringify(testResults.context.vars, null, 2) }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import RuleCanvas from './components/RuleCanvas.vue'
import NodePalette from './components/NodePalette.vue'
import ConfigPanel from './components/ConfigPanel.vue'
import { useRuleAPI } from './composables/useRuleAPI'
import { useFlowState } from './composables/useFlowState'

// Props
const props = defineProps({
  ruleName: {
    type: String,
    required: true
  },
  documentType: {
    type: String,
    required: true
  }
})

// State
const {
  loadRule,
  saveRuleFlow,
  getProcessMethods,
  testRuleExecution
} = useRuleAPI()

const {
  nodes,
  edges,
  selectedNode,
  isModified,
  initializeFlow,
  updateNode,
  exportFlow
} = useFlowState()

const processMethods = ref([])
const showTestResults = ref(false)
const testResults = ref({})

// Computed
const canTest = computed(() => {
  return nodes.value.length > 0 && props.documentType
})

// Methods
async function loadRuleData() {
  try {
    const data = await loadRule(props.ruleName)
    initializeFlow(data.actions || [])
  } catch (error) {
    frappe.msgprint({
      title: 'Error',
      message: `Failed to load rule: ${error.message}`,
      indicator: 'red'
    })
  }
}

async function loadProcessMethods() {
  try {
    processMethods.value = await getProcessMethods()
  } catch (error) {
    console.error('Failed to load process methods:', error)
  }
}

async function saveRule() {
  try {
    const flowData = exportFlow()
    await saveRuleFlow(props.ruleName, flowData)
    
    frappe.show_alert({
      message: 'Rule saved successfully',
      indicator: 'green'
    })
  } catch (error) {
    frappe.msgprint({
      title: 'Error',
      message: `Failed to save rule: ${error.message}`,
      indicator: 'red'
    })
  }
}

async function testRule() {
  // Prompt for document to test against
  const dialog = new frappe.ui.Dialog({
    title: 'Test Rule',
    fields: [
      {
        label: 'Document Name',
        fieldname: 'document_name',
        fieldtype: 'Link',
        options: props.documentType,
        reqd: 1
      }
    ],
    primary_action_label: 'Test',
    primary_action: async (values) => {
      try {
        const results = await testRuleExecution(props.ruleName, values.document_name)
        testResults.value = results
        showTestResults.value = true
        dialog.hide()
      } catch (error) {
        frappe.msgprint({
          title: 'Test Failed',
          message: error.message,
          indicator: 'red'
        })
      }
    }
  })
  dialog.show()
}

function onNodeClick(event) {
  // Node selection handled by useFlowState
}

function onSelectionChange(selection) {
  // Handle selection changes if needed
}

// Lifecycle
onMounted(async () => {
  await loadProcessMethods()
  await loadRuleData()
})

// Watchers
watch(() => props.ruleName, () => {
  loadRuleData()
})

// Expose methods for parent
defineExpose({
  saveRule,
  testRule,
  isModified
})
</script>

<style scoped>
.rule-builder-app {
  display: flex;
  flex-direction: column;
  height: calc(100vh - var(--navbar-height) - var(--page-head-height) - 40px);
  background: #f5f7fa;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: white;
  border-bottom: 1px solid #e0e6ed;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toolbar-left h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
}

.toolbar-right {
  display: flex;
  gap: 8px;
}

.badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
}

.badge-success {
  background: #d1f2eb;
  color: #00a65a;
}

.badge-warning {
  background: #fff3cd;
  color: #856404;
}

.builder-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.canvas-container {
  flex: 1;
  position: relative;
  background: #fafbfc;
}

.test-results-panel {
  height: 300px;
  border-top: 2px solid #e0e6ed;
  background: white;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  border-bottom: 1px solid #e0e6ed;
  background: #f8f9fa;
}

.panel-header h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
}

.panel-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.execution-log {
  margin-top: 20px;
}

.execution-log h5 {
  margin-bottom: 10px;
  font-size: 13px;
  font-weight: 600;
  color: #5a6c7d;
}

.log-entry {
  display: grid;
  grid-template-columns: 140px 80px 1fr;
  gap: 12px;
  padding: 8px 12px;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
  border-left: 3px solid #e0e6ed;
  margin-bottom: 4px;
}

.log-entry.log-info {
  border-left-color: #3498db;
  background: #f0f8ff;
}

.log-entry.log-debug {
  border-left-color: #95a5a6;
  background: #f8f9fa;
}

.log-entry.log-warning {
  border-left-color: #f39c12;
  background: #fff8e1;
}

.log-entry.log-error {
  border-left-color: #e74c3c;
  background: #ffebee;
}

.log-time {
  color: #7f8c8d;
  font-size: 11px;
}

.log-level {
  font-weight: 600;
  text-transform: uppercase;
}

.log-message {
  color: #2c3e50;
}

.context-vars {
  margin-top: 20px;
}

.context-vars h5 {
  margin-bottom: 10px;
  font-size: 13px;
  font-weight: 600;
  color: #5a6c7d;
}

.context-vars pre {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 4px;
  border: 1px solid #e0e6ed;
  font-size: 12px;
  overflow-x: auto;
}
</style>
