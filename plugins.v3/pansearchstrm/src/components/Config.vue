<template>
  <div class="plugin-config">
    <v-card flat class="rounded border">
      <v-card-title class="text-subtitle-1 d-flex align-center px-3 py-2 bg-primary-lighten-5">
        <v-icon icon="mdi-cog" class="mr-2" color="primary" size="small" />
        <span>网盘搜索STRM 配置</span>
        <v-spacer></v-spacer>
        <v-btn color="primary" size="small" variant="text" @click="$emit('switch')">
          <v-icon icon="mdi-arrow-left" size="small" class="mr-1"></v-icon>
          返回
        </v-btn>
      </v-card-title>

      <v-card-text class="px-3 py-2">
        <v-alert v-if="error" type="error" density="compact" variant="tonal" class="mb-2 text-caption" closable>
          {{ error }}
        </v-alert>
        <v-alert v-if="message" type="success" density="compact" variant="tonal" class="mb-2 text-caption" closable>
          {{ message }}
        </v-alert>

        <v-card flat class="rounded border mb-3">
          <v-card-title class="text-caption px-3 py-2 bg-primary-lighten-5">基础设置</v-card-title>
          <v-card-text class="px-3 py-2">
            <v-switch v-model="form.enabled" label="启用插件" color="primary" density="compact" hide-details />
            <v-switch v-model="form.notify" label="操作完成后发送通知" color="primary" density="compact" hide-details />
            <v-switch
              v-model="form.search_inject_enabled"
              label="把网盘资源并入默认「搜索资源」结果（搜索 PT 资源时同时返回网盘资源）"
              color="primary"
              density="compact"
              hide-details
            />
            <v-text-field
              v-model="form.moviepilot_address"
              label="MoviePilot 访问地址（用于生成 STRM 跳转端点）"
              placeholder="http://192.168.1.10:3001"
              variant="outlined"
              density="compact"
              hide-details
            />
          </v-card-text>
        </v-card>

        <v-card flat class="rounded border mb-3">
          <v-card-title class="text-caption px-3 py-2 bg-primary-lighten-5">盘搜渠道</v-card-title>
          <v-card-text class="px-3 py-2">
            <v-switch v-model="form.pansou.enabled" label="启用盘搜" color="primary" density="compact" hide-details />
            <v-text-field v-model="form.pansou.base_url" label="盘搜服务地址" variant="outlined" density="compact" hide-details class="mt-2" />
            <v-text-field v-model="form.pansou.username" label="用户名（可选）" variant="outlined" density="compact" hide-details class="mt-2" />
            <v-text-field v-model="form.pansou.password" label="密码（可选）" type="password" variant="outlined" density="compact" hide-details class="mt-2" />
            <v-text-field v-model.number="form.pansou.result_limit" label="结果条数上限" type="number" variant="outlined" density="compact" hide-details class="mt-2" />
          </v-card-text>
        </v-card>

        <v-card flat class="rounded border mb-3">
          <v-card-title class="text-caption px-3 py-2 bg-primary-lighten-5">聚影渠道</v-card-title>
          <v-card-text class="px-3 py-2">
            <v-switch v-model="form.juying.enabled" label="启用聚影" color="primary" density="compact" hide-details />
            <v-text-field v-model="form.juying.base_url" label="聚影站点地址" variant="outlined" density="compact" hide-details class="mt-2" />
            <v-text-field v-model="form.juying.username" label="账号" variant="outlined" density="compact" hide-details class="mt-2" />
            <v-text-field v-model="form.juying.password" label="密码" type="password" variant="outlined" density="compact" hide-details class="mt-2" />
            <v-text-field v-model.number="form.juying.result_limit" label="结果条数上限" type="number" variant="outlined" density="compact" hide-details class="mt-2" />
          </v-card-text>
        </v-card>

        <v-card flat class="rounded border mb-3">
          <v-card-title class="text-caption px-3 py-2 bg-primary-lighten-5">Telegram 渠道（扫码授权）</v-card-title>
          <v-card-text class="px-3 py-2">
            <v-switch v-model="form.telegram.enabled" label="启用 Telegram" color="primary" density="compact" hide-details />
            <v-text-field v-model="form.telegram.api_id" label="api_id（my.telegram.org 申请）" variant="outlined" density="compact" hide-details class="mt-2" />
            <v-text-field v-model="form.telegram.api_hash" label="api_hash" variant="outlined" density="compact" hide-details class="mt-2" />
            <v-textarea
              v-model="telegramChannels"
              label="搜索频道（每行一个，如 pan115share）"
              variant="outlined"
              density="compact"
              rows="4"
              hide-details
              class="mt-2"
            />
            <v-switch v-model="form.telegram.search_global" label="额外做账号全局搜索" color="primary" density="compact" hide-details class="mt-2" />
          </v-card-text>
        </v-card>

        <v-card flat class="rounded border mb-3">
          <v-card-title class="text-caption px-3 py-2 bg-primary-lighten-5">115 网盘</v-card-title>
          <v-card-text class="px-3 py-2">
            <v-text-field v-model="form.p115.receive_path" label="转存目标目录" variant="outlined" density="compact" hide-details />
            <v-text-field
              v-model.number="form.p115.share_duration"
              label="分享有效期天数（-1 为长期）"
              type="number"
              variant="outlined"
              density="compact"
              hide-details
              class="mt-2"
            />
            <v-switch v-model="form.p115.auto_renewal" label="开启分享自动续期" color="primary" density="compact" hide-details class="mt-2" />
            <v-text-field
              v-model.number="form.p115.request_timeout"
              label="请求超时（秒）"
              type="number"
              variant="outlined"
              density="compact"
              hide-details
              class="mt-2"
            />
          </v-card-text>
        </v-card>

        <v-card flat class="rounded border mb-3">
          <v-card-title class="text-caption px-3 py-2 bg-primary-lighten-5">STRM 生成</v-card-title>
          <v-card-text class="px-3 py-2">
            <v-switch v-model="form.strm.enabled" label="生成 STRM" color="primary" density="compact" hide-details />
            <v-text-field v-model="form.strm.output_path" label="STRM 输出目录" variant="outlined" density="compact" hide-details class="mt-2" />
            <v-select
              v-model="form.strm.url_mode"
              :items="urlModeItems"
              item-title="title"
              item-value="value"
              label="STRM 内容模式"
              variant="outlined"
              density="compact"
              hide-details
              class="mt-2"
            />
            <v-text-field v-model="form.strm.media_ext" label="媒体扩展名（逗号分隔）" variant="outlined" density="compact" hide-details class="mt-2" />
            <v-switch v-model="form.strm.overwrite" label="覆盖已存在的 STRM" color="primary" density="compact" hide-details class="mt-2" />
          </v-card-text>
        </v-card>

        <div class="d-flex justify-end">
          <v-btn color="primary" variant="flat" :loading="saving" @click="submit">保存配置</v-btn>
        </div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'

const props = defineProps({
  api: { type: Object, default: null },
  initialConfig: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['save', 'close', 'switch'])

const error = ref('')
const message = ref('')
const saving = ref(false)

const urlModeItems = [
  { title: '插件跳转端点（播放时 302 到 115 直链）', value: 'redirect' },
  { title: '直接写入 115 分享链接', value: 'share' },
]

/**
 * 生成带默认值的表单模型，确保嵌套字段始终存在。
 */
function buildForm(raw) {
  const source = raw || {}
  return reactive({
    enabled: Boolean(source.enabled),
    notify: source.notify !== false,
    search_inject_enabled: source.search_inject_enabled !== false,
    moviepilot_address: source.moviepilot_address || '',
    pansou: {
      enabled: Boolean(source.pansou?.enabled),
      base_url: source.pansou?.base_url || 'https://pansou.cc',
      username: source.pansou?.username || '',
      password: source.pansou?.password || '',
      result_limit: source.pansou?.result_limit ?? 20,
      timeout: source.pansou?.timeout ?? 30,
    },
    juying: {
      enabled: Boolean(source.juying?.enabled),
      base_url: source.juying?.base_url || 'https://www.jying.top',
      username: source.juying?.username || '',
      password: source.juying?.password || '',
      result_limit: source.juying?.result_limit ?? 20,
      timeout: source.juying?.timeout ?? 30,
    },
    telegram: {
      enabled: Boolean(source.telegram?.enabled),
      api_id: source.telegram?.api_id || '',
      api_hash: source.telegram?.api_hash || '',
      channels: Array.isArray(source.telegram?.channels) ? [...source.telegram.channels] : [],
      search_global: Boolean(source.telegram?.search_global),
      result_limit: source.telegram?.result_limit ?? 20,
      timeout: source.telegram?.timeout ?? 30,
    },
    p115: {
      cookies: source.p115?.cookies || '',
      receive_path: source.p115?.receive_path || '/网盘搜索转存',
      share_duration: source.p115?.share_duration ?? -1,
      auto_renewal: source.p115?.auto_renewal !== false,
      request_timeout: source.p115?.request_timeout ?? 60,
    },
    strm: {
      enabled: source.strm?.enabled !== false,
      output_path: source.strm?.output_path || '/media/网盘/STRM',
      url_mode: source.strm?.url_mode || 'redirect',
      media_ext: source.strm?.media_ext || 'mp4,mkv,ts,iso,m2ts,avi,rmvb,flv,mov,wmv',
      overwrite: Boolean(source.strm?.overwrite),
    },
  })
}

const form = buildForm(props.initialConfig)
const telegramChannels = ref((form.telegram.channels || []).join('\n'))

watch(
  () => props.initialConfig,
  (value) => {
    Object.assign(form, buildForm(value))
    telegramChannels.value = (form.telegram.channels || []).join('\n')
  }
)

/**
 * 提交配置到插件接口。
 */
async function submit() {
  error.value = ''
  message.value = ''
  form.telegram.channels = String(telegramChannels.value || '')
    .split('\n')
    .map((item) => item.trim())
    .filter((item) => item.length > 0)
  if (!props.api) {
    message.value = '开发预览模式：配置未提交'
    return
  }
  saving.value = true
  try {
    const resp = await props.api.post('plugin/PanSearchStrm/config', form)
    const payload =
      resp && typeof resp === 'object' && 'success' in resp
        ? resp
        : resp?.data && typeof resp.data === 'object'
          ? resp.data
          : resp || {}
    if (payload.success === false) {
      error.value = payload.message || '保存失败'
    } else {
      message.value = '配置已保存'
      emit('save', form)
    }
  } catch (err) {
    error.value = String(err?.message || err)
  } finally {
    saving.value = false
  }
}
</script>
