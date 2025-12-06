<!-- Stop Node Component -->
<template>
  <div :class="['custom-node', 'stop-node', { 'node-selected': selected }]">
    <div class="node-content">
      <i class="fa fa-stop-circle"></i>
      <span>Stop</span>
    </div>
    <Handle type="target" position="top" />
  </div>
</template>

<script setup>
import { Handle } from '@vue-flow/core'

defineProps({
  data: {
    type: Object,
    default: () => ({})  },
  selected: {
    type: Boolean,
    default: false
  }
})
</script>

<style scoped>
.stop-node {
  background: #e74c3c;
  border: 2px solid #c0392b;
  border-radius: 50px;
  color: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.stop-node.node-selected {
  box-shadow: 0 0 0 3px rgba(231, 76, 60, 0.3), 0 4px 12px rgba(0, 0, 0, 0.15);
}

.node-content {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  font-size: 13px;
  font-weight: 600;
}

.node-content i {
  font-size: 16px;
}
</style>
