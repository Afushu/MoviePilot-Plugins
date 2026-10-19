<template>
  <div class="pansearch-page">
    <SearchPanel :api="api" :plugin-id="pluginId" />
  </div>
</template>

<script setup>
import SearchPanel from './SearchPanel.vue'

defineProps({
  api: { type: Object, default: null },
  pluginId: { type: String, default: 'PanSearchStrm' },
})

defineEmits(['action', 'switch', 'close'])
</script>
