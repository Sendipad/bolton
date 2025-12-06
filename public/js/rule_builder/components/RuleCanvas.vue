<!-- Rule Canvas with VueFlow Integration -->
<template>
  <div class="rule-canvas">
    <VueFlow
      v-model:nodes="flowNodes"
      v-model:edges="flowEdges"
      :fit-view-on-init="true"
      :min-zoom="0.2"
      :max-zoom="2"
      @node-click="onNodeClick"
      @edge-click="onEdgeClick"
      @pane-click="onPaneClick"
    >
      <!-- Custom Node Types -->
      <template #node-start="props">
        <StartNode v-bind="props" />
      </template>
      
      <template #node-process="props">
        <ProcessNode v-bind="props" />
      </template>
      
      <template #node-condition="props">
        <ConditionNode v-bind="props" />
      </template>
      
      <template #node-stop="props">
        <StopNode v-bind="props" />
      </template>

      <!-- Flow Controls -->
      <Background pattern-color="#c3cdd8" :gap="16" />
      <Controls />
      <MiniMap />
    </VueFlow>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { VueFlow, useVueFlow } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import { MiniMap } from '@vue-flow/minimap'
import StartNode from './nodes/StartNode.vue'
import ProcessNode from './nodes/ProcessNode.vue'
import ConditionNode from './nodes/ConditionNode.vue'
import StopNode from './nodes/StopNode.vue'

// Props
const props = defineProps({
  nodes: {
    type: Array,
    default: () => []
  },
  edges: {
    type: Array,
    default: () => []
  }
})

// Emits
const emit = defineEmits(['update:nodes', 'update:edges', 'node-click', 'selection-change'])

// VueFlow instance
const { onPaneReady, fitView, addEdges, addNodes } = useVueFlow()

// Local state
const flowNodes = computed({
  get: () => props.nodes,
  set: (value) => emit('update:nodes', value)
})

const flowEdges = computed({
  get: () => props.edges,
  set: (value) => emit('update:edges', value)
})

// Methods
function onNodeClick(event) {
  emit('node-click', event)
}

function onEdgeClick(event) {
  // Handle edge click if needed
}

function onPaneClick(event) {
  // Clear selection when clicking on empty canvas
  emit('selection-change', [])
}

// Initialize flow when pane is ready
onPaneReady(() => {
  fitView({ padding: 0.2 })
})
</script>

<style>
.rule-canvas {
  width: 100%;
  height: 100%;
  position: relative;
}

/* Custom VueFlow styling */
.vue-flow__node {
  cursor: pointer;
}

.vue-flow__node:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.vue-flow__node.selected {
  box-shadow: 0 0 0 2px #3498db;
}

.vue-flow__edge-path {
  stroke-width: 2;
  stroke: #95a5a6;
}

.vue-flow__edge.selected .vue-flow__edge-path {
  stroke: #3498db;
  stroke-width: 3;
}

.vue-flow__edge:hover .vue-flow__edge-path {
  stroke: #2980b9;
}

/* Minimap styling */
.vue-flow__minimap {
  background: white;
  border: 1px solid #e0e6ed;
  border-radius: 4px;
}

/* Controls styling */
.vue-flow__controls {
  background: white;
  border: 1px solid #e0e6ed;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.vue-flow__controls-button {
  background: white;
  border-bottom: 1px solid #e0e6ed;
}

.vue-flow__controls-button:hover {
  background: #f8f9fa;
}
</style>
