<!-- Start Node Component -->
<template>
  <div :class="['custom-node', 'start-node', { 'node-selected': selected }]">
    <div class="node-content">
      <i class="fa fa-play-circle"></i>
      <span>Start</span>
    </div>
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
.start-node {
  background: #27ae60;
  border: 2px solid #229954;
  border-radius: 50px;
  color: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.start-node.node-selected {
  box-shadow: 0 0 0 3px rgba(39, 174, 96, 0.3), 0 4px 12px rgba(0, 0, 0, 0.15);
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
