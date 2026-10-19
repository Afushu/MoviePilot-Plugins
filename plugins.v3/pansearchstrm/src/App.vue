<template>
  <v-app>
    <v-main class="pa-4">
      <SearchPanel :api="mockApi" plugin-id="PanSearchStrm" />
    </v-main>
  </v-app>
</template>

<script setup>
import SearchPanel from './components/SearchPanel.vue'

/**
 * 开发预览用的空实现，正式运行时由 MoviePilot 注入真实 api 对象。
 */
const mockApi = {
  get: async () => ({ data: {} }),
  post: async () => ({ data: {} }),
}
</script>
