<template>
  <div class="condition-builder">
    <div ref="filterWrapper"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';

const props = defineProps({
  doctype: {
    type: String,
    required: true
  },
  initialConditions: {
    type: String, // JSON string
    default: '[]'
  }
});

const emit = defineEmits(['change']);
const filterWrapper = ref(null);
let filterGroup = null;

onMounted(() => {
  initFilterGroup();
});

watch(() => props.initialConditions, (newVal) => {
    // Only update if significantly different to avoid loops
    // For now, we assume initialConditions is only set on load
});

function initFilterGroup() {
  if (!filterWrapper.value) return;
  
  // Parse initial conditions
  let filters = [];
  try {
      filters = JSON.parse(props.initialConditions || '[]');
  } catch (e) {
      console.error("Invalid initial conditions", e);
  }

  filterGroup = new frappe.ui.FilterGroup({
    parent: $(filterWrapper.value),
    doctype: props.doctype,
    on_change: () => {
        const currentFilters = filterGroup.get_filters();
        emit('change', JSON.stringify(currentFilters));
    }
  });
  
  // Add initial filters
  if (filters.length > 0) {
      filters.forEach(f => {
          filterGroup.add_filter(f[0], f[1], f[2], f[3]);
      });
  }
}
</script>

<style scoped>
.condition-builder {
  padding: 10px;
  background: #f9f9f9;
  border: 1px solid #ddd;
  border-radius: 4px;
}
</style>
