<template>
  <v-card flat class="rounded border">
    <v-card-title class="text-caption d-flex align-center px-3 py-2">
      <v-icon icon="mdi-cloud-search" size="small" class="mr-2" color="primary" />
      <span>网盘搜索STRM</span>
    </v-card-title>
    <v-card-text class="px-3 py-2 text-caption">
      已启用渠道：{{ (status.sources || []).join('、') || '未启用' }}
    </v-card-text>
  </v-card>
</template>

<script setup>
import { onMounted, ref } from 'vue'

const props = defineProps({
  api: { type: Object, default: null },
  config: { type: Object, default: () => ({}) },
  allowRefresh: { type: Boolean, default: true },
})

const status = ref({ sources: [] })

/**
 * 读取插件状态，用于仪表板展示。
 */
async function loadStatus() {
  if (!props.api) return
  try {
    const resp = await props.api.get('plugin/PanSearchStrm/status')
    status.value =
      resp && typeof resp === 'object' && ('sources' in resp || 'success' in resp)
        ? resp
        : resp?.data && typeof resp.data === 'object'
          ? resp.data
          : resp || {}
  } catch (error) {
    status.value = { sources: [] }
  }
}

onMounted(loadStatus)
</script>
