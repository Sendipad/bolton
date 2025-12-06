// Flow State Management
import { ref, computed } from 'vue'

export function useFlowState() {
    const nodes = ref([])
    const edges = ref([])
    const selectedNode = ref(null)
    const isModified = ref(false)

    function initializeFlow(actions) {
        // Convert Rule Actions to VueFlow nodes
        nodes.value = actions.map((action, index) => ({
            id: action.action_id || `node-${index}`,
            type: action.action_type.toLowerCase(),
            position: {
                x: action.position_x || (index * 250),
                y: action.position_y || (Math.floor(index / 4) * 150)
            },
            data: {
                label: action.action_label,
                ...action
            }
        }))

        // Convert connections to edges
        edges.value = []
        actions.forEach(action => {
            if (action.next_step_if_true) {
                edges.value.push({
                    id: `${action.action_id}-true`,
                    source: action.action_id,
                    target: action.next_step_if_true,
                    sourceHandle: action.action_type === 'Condition' ? 'true' : undefined
                })
            }
            if (action.next_step_if_false) {
                edges.value.push({
                    id: `${action.action_id}-false`,
                    source: action.action_id,
                    target: action.next_step_if_false,
                    sourceHandle: 'false'
                })
            }
        })
    }

    function exportFlow() {
        return nodes.value.map(node => ({
            action_id: node.id,
            action_type: node.type.charAt(0).toUpperCase() + node.type.slice(1),
            action_label: node.data.label,
            is_enabled: 1,
            position_x: node.position.x,
            position_y: node.position.y,
            ...node.data,
            next_step_if_true: edges.value.find(e => e.source === node.id && e.sourceHandle !== 'false')?.target,
            next_step_if_false: edges.value.find(e => e.source === node.id && e.sourceHandle === 'false')?.target
        }))
    }

    function updateNode(update) {
        const node = nodes.value.find(n => n.id === update.id)
        if (node) {
            node.data = { ...node.data, ...update.data }
            isModified.value = true
        }
    }

    function addNode(nodeType, position) {
        const newNode = {
            id: `node-${Date.now()}`,
            type: nodeType.type,
            position,
            data: {
                label: nodeType.label
            }
        }
        nodes.value.push(newNode)
        isModified.value = true
    }

    return {
        nodes,
        edges,
        selectedNode,
        isModified,
        initializeFlow,
        exportFlow,
        updateNode,
        addNode
    }
}
