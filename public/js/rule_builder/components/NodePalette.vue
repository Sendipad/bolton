<!-- Node Palette - Draggable Node Types -->
<template>
  <div class="node-palette">
    <div class="palette-header">
      <h4>Node Types</h4>
    </div>
    
    <div class="palette-content">
      <div class="node-category">
        <h5>Flow Control</h5>
        <div
          v-for="node in flowNodes"
          :key="node.type"
          class="palette-node"
          :class="`palette-node-${node.type}`"
          draggable="true"
          @dragstart="onDragStart($event, node)"
        >
          <i :class="node.icon"></i>
          <span>{{ node.label }}</span>
        </div>
      </div>

      <div class="node-category">
        <h5>Actions</h5>
        <div
          v-for="node in actionNodes"
          :key="node.type"
          class="palette-node"
          :class="`palette-node-${node.type}`"
          draggable="true"
          @dragstart="onDragStart($event, node)"
        >
          <i :class="node.icon"></i>
          <span>{{ node.label }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// Node definitions
const flowNodes = ref([
  {
    type: 'start',
    label: 'Start',
    icon: 'fa fa-play-circle',
    description: 'Entry point of the rule flow'
  },
  {
    type: 'condition',
    label: 'Condition',
    icon: 'fa fa-code-fork',
    description: 'Branching based on condition'
  },
  {
    type: 'stop',
    label: 'Stop',
    icon: 'fa fa-stop-circle',
    description: 'End of flow execution'
  }
])

const actionNodes = ref([
  {
    type: 'process',
    label: 'Process',
    icon: 'fa fa-cog',
    description: 'Execute a process method'
  }
])

// Methods
function onDragStart(event, nodeType) {
  event.dataTransfer.effectAllowed = 'move'
  event.dataTransfer.setData('application/vueflow', JSON.stringify(nodeType))
}
</script>

<style scoped>
.node-palette {
  width: 240px;
  background: white;
  border-right: 1px solid #e0e6ed;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.palette-header {
  padding: 16px 20px;
  border-bottom: 1px solid #e0e6ed;
  background: #f8f9fa;
}

.palette-header h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.palette-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.node-category {
  margin-bottom: 24px;
}

.node-category h5 {
  margin: 0 0 12px 0;
  font-size: 12px;
  font-weight: 600;
  color: #7f8c8d;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.palette-node {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  margin-bottom: 8px;
  background: #f8f9fa;
  border: 1px solid #e0e6ed;
  border-radius: 6px;
  cursor: grab;
  transition: all 0.2s ease;
  user-select: none;
}

.palette-node:hover {
  background: #e9ecef;
  border-color: #3498db;
  transform: translateX(4px);
}

.palette-node:active {
  cursor: grabbing;
  transform: scale(0.98);
}

.palette-node i {
  font-size: 16px;
  width: 20px;
  text-align: center;
}

.palette-node span {
  font-size: 13px;
  font-weight: 500;
  color: #2c3e50;
}

/* Node type specific colors */
.palette-node-start {
  border-left: 3px solid #27ae60;
}

.palette-node-start i {
  color: #27ae60;
}

.palette-node-condition {
  border-left: 3px solid #f39c12;
}

.palette-node-condition i {
  color: #f39c12;
}

.palette-node-process {
  border-left: 3px solid #3498db;
}

.palette-node-process i {
  color: #3498db;
}

.palette-node-stop {
  border-left: 3px solid #e74c3c;
}

.palette-node-stop i {
  color: #e74c3c;
}
</style>
