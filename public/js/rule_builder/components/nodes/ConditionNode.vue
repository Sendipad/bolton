<!-- Condition Node Component -->
<template>
  <div :class="['custom-node', 'condition-node', { 'node-selected': selected }]">
    <div class="node-header">
      <i class="fa fa-code-fork"></i>
      <span class="node-title">{{ data.label || 'Condition' }}</span>
    </div>
    <div v-if="data.condition_expression" class="node-body">
      <div class="node-condition">{{ data.condition_expression }}</div>
    </div>
    <Handle type="target" position="top" />
    <Handle id="true" type="source" position="bottom" :style="{ left: '30%' }" />
    <Handle id="false" type="source" position="bottom" :style="{ left: '70%' }" />
  </div>
</template>

<script setup>
import { Handle } from '@vue-flow/core'

defineProps({
  data: {
    type: Object,
    default: () => ({})
  },
  selected: {
    type: Boolean,
    default: false
  }
})
</script>

<style scoped>
.condition-node {
  background: white;
  border: 2px solid #f39c12;
  border-radius: 8px;
  min-width: 180px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.condition-node.node-selected {
  border-color: #e67e22;
  box-shadow: 0 0 0 3px rgba(243, 156, 18, 0.2), 0 4px 12px rgba(0, 0, 0, 0.15);
}

.node-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: #f39c12;
  border-radius: 6px 6px 0 0;
  color: white;
}

.node-header i {
  font-size: 14px;
}

.node-title {
  font-size: 13px;
  font-weight: 600;
}

.node-body {
  padding: 10px 14px;
}

.node-condition {
  font-size: 11px;
  color: #7f8c8d;
  font-weight: 500;
  font-family: 'Monaco', 'Menlo', monospace;
}
</style>
