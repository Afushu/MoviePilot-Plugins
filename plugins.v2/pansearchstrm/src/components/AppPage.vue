<template>
  <div class="pansearch-app-page">
    <SearchPanel :api="api" :plugin-id="pluginId" :nav-key="navKey" />
  </div>
</template>

<script setup>
import SearchPanel from './SearchPanel.vue'

defineProps({
  api: { type: Object, default: null },
  pluginId: { type: String, default: 'PanSearchStrm' },
  navKey: { type: String, default: 'main' },
})
</script>
