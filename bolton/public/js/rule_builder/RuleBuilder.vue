<template>
    <div class="rule-builder-container">
        <!-- Toolbar -->
        <div class="builder-toolbar">
            <div class="toolbar-left">
                <div class="btn-group">
                    <button class="btn btn-xs btn-default" @click="addNode('process')" title="Add Process">
                        <i class="fa fa-cog"></i> Process
                    </button>
                    <button class="btn btn-xs btn-default" @click="addNode('condition')" title="Add Condition">
                        <i class="fa fa-code-fork"></i> Condition
                    </button>
                    <button class="btn btn-xs btn-default" @click="addNode('stop')" title="Add Stop">
                        <i class="fa fa-stop-circle"></i> Stop
                    </button>
                </div>
            </div>
            <div class="toolbar-right">
                <button class="btn btn-xs btn-default" @click="fitView()" title="Fit View">
                    <i class="fa fa-expand"></i>
                </button>
            </div>
        </div>
        
        <!-- Main Canvas + Sidebar -->
        <div class="builder-main">
            <div class="sidebar-container" v-if="showSidebar" @click.stop>
                <Sidebar @close="closeSidebar" />
            </div>
            <div class="canvas-container">
                <VueFlow
                    v-model:nodes="nodes"
                    v-model:edges="edges"
                    :default-viewport="{ zoom: 1 }"
                    :min-zoom="0.2"
                    :max-zoom="2"
                    :snap-to-grid="true"
                    :snap-grid="[15, 15]"
                    fit-view-on-init
                    @node-click="onNodeClick"
                    @pane-click="onPaneClick"
                    @connect="onConnect"
                    @nodes-change="onNodesChange"
                >
                    <template #node-start="nodeProps">
                        <StartNode v-bind="nodeProps" />
                    </template>
                    <template #node-process="nodeProps">
                        <ProcessNode v-bind="nodeProps" />
                    </template>
                    <template #node-condition="nodeProps">
                        <ConditionNode v-bind="nodeProps" />
                    </template>
                    <template #node-stop="nodeProps">
                        <StopNode v-bind="nodeProps" />
                    </template>
                    
                    <Background :gap="15" />
                    <Panel :position="PanelPosition.BottomLeft">
                        <button class="btn btn-sm btn-default mr-2" @click="zoomIn">+</button>
                        <button class="btn btn-sm btn-default mr-2" @click="zoomOut">-</button>
                        <button class="btn btn-sm btn-default" @click="fitView()">Fit</button>
                    </Panel>
                </VueFlow>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { VueFlow, useVueFlow, Panel, PanelPosition } from '@vue-flow/core';
import { Background } from '@vue-flow/background';
import { useStore } from './store';

import StartNode from './components/nodes/StartNode.vue';
import ProcessNode from './components/nodes/ProcessNode.vue';
import ConditionNode from './components/nodes/ConditionNode.vue';
import StopNode from './components/nodes/StopNode.vue';
import Sidebar from './components/Sidebar.vue';

const props = defineProps({ rule: String });
const store = useStore();
const { fitView, zoomIn, zoomOut } = useVueFlow();

const nodes = computed({
    get: () => store.graph.elements.filter(el => el.position),
    set: (val) => {
        const edges = store.graph.elements.filter(el => el.source);
        store.graph.elements = [...val, ...edges];
    }
});

const edges = computed({
    get: () => store.graph.elements.filter(el => el.source),
    set: (val) => {
        const nodesList = store.graph.elements.filter(el => el.position);
        store.graph.elements = [...nodesList, ...val];
    }
});

const showSidebar = computed(() => store.graph.selected !== null);

function closeSidebar() {
    store.graph.selected = null;
}

onMounted(async () => {
    if (props.rule) {
        store.rule_name = props.rule;
    }
    await store.fetch();
    autoConnectStartNode();
});

function autoConnectStartNode() {
    const hasStartEdge = store.graph.elements.some(el => el.source === 'start');
    if (hasStartEdge) return;
    
    const firstNode = store.graph.elements.find(el => 
        el.position && el.id !== 'start' && el.data?.is_enabled !== 0
    );
    
    if (firstNode) {
        store.graph.elements.push({
            id: `e-start-${firstNode.id}`,
            source: 'start',
            target: firstNode.id,
            sourceHandle: 'default',
            animated: true
        });
    }
}

function onNodeClick(event) {
    store.graph.selected = event.node;
}

function onPaneClick() {
    store.graph.selected = null;
}

function onConnect(params) {
    const newEdge = {
        id: `e-${params.source}-${params.target}-${params.sourceHandle || 'default'}`,
        source: params.source,
        target: params.target,
        sourceHandle: params.sourceHandle || 'default',
        animated: params.source === 'start'
    };
    
    store.graph.elements.push(newEdge);
    store.mark_dirty();
}

function onNodesChange(changes) {
    const hasDrag = changes.some(c => c.type === 'position' && c.dragging === false);
    if (hasDrag) {
        store.mark_position_change();
    }
}

function addNode(type) {
    const id = `${type}-${Date.now()}`;
    const label = type === 'process' ? 'New Process' : 
                  type === 'condition' ? 'New Condition' : 'Stop';
    
    const newNode = {
        id,
        type,
        position: { x: 300, y: 200 },
        label,
        data: {
            action_id: id,
            action_type: type.charAt(0).toUpperCase() + type.slice(1),
            action_label: label,
            is_enabled: 1
        }
    };
    
    store.graph.elements.push(newNode);
    store.graph.selected = newNode;
    store.mark_dirty();
}
</script>

<style>
@import '@vue-flow/core/dist/style.css';
@import '@vue-flow/core/dist/theme-default.css';

.rule-builder-container {
    display: flex;
    flex-direction: column;
    height: calc(100vh - var(--navbar-height) - var(--page-head-height) - 60px);
}

.builder-toolbar {
    display: flex;
    justify-content: space-between;
    padding: 8px 15px;
    background: var(--fg-color);
    border-bottom: 1px solid var(--border-color);
}

.builder-main {
    flex: 1;
    display: flex;
    position: relative;
    overflow: hidden;
}

.sidebar-container {
    position: relative;
    height: 100%;
    margin-right: 10px;
    border-radius: var(--border-radius-lg);
    border: 1px solid var(--border-color);
    background-color: var(--fg-color);
}

.canvas-container {
    flex: 1;
    height: 100%;
    border-radius: var(--border-radius-lg);
    border: 1px solid var(--border-color);
    background-color: var(--fg-color);
}
</style>
