<!-- Process Node Component -->
<template>
  <div :class="['custom-node', 'process-node', { 'node-selected': selected }]">
    <div class="node-header">
      <i class="fa fa-cog"></i>
      <span class="node-title">{{ data.label || 'Process' }}</span>
    </div>
    <div v-if="data.process_method" class="node-body">
      <div class="node-method">{{ data.process_method }}</div>
    </div>
    <Handle type="target" position="top" />
    <Handle type="source" position="bottom" />
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
.process-node {
  background: white;
  border: 2px solid #3498db;
  border-radius: 8px;
  min-width: 180px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.process-node.node-selected {
  border-color: #2980b9;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.2), 0 4px 12px rgba(0, 0, 0, 0.15);
}

.node-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: #3498db;
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

.node-method {
  font-size: 11px;
  color: #7f8c8d;
  font-weight: 500;
}
</style>
