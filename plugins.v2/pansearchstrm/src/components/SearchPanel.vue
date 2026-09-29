<template>
  <div class="pansearch-panel">
    <!-- 115 网盘配置 -->
    <v-card flat class="rounded border mb-3">
      <v-card-title class="text-subtitle-2 d-flex align-center px-3 py-2 bg-primary-lighten-5">
        <v-icon icon="mdi-cloud" class="mr-2" color="primary" size="small" />
        <span>115 网盘配置</span>
        <v-spacer></v-spacer>
        <v-chip size="small" variant="tonal" :color="status.p115?.authorized ? 'success' : 'warning'">
          {{ status.p115?.authorized ? `已授权（${status.p115?.account || '账号信息不可用'}）` : '未授权' }}
        </v-chip>
      </v-card-title>
      <v-card-text class="px-3 py-2">
        <div class="d-flex align-center flex-wrap ga-2">
          <v-text-field
            :model-value="cookieMasked"
            label="Cookie"
            variant="outlined"
            density="compact"
            readonly
            hide-details
            style="min-width: 320px"
            class="flex-grow-1"
          />
          <v-btn size="small" color="primary" variant="tonal" @click="openQrcode115">
            <v-icon icon="mdi-qrcode-scan" size="small" class="mr-1"></v-icon>
            扫码
          </v-btn>
          <v-btn size="small" color="primary" variant="tonal" @click="openCookieDialog">
            <v-icon icon="mdi-key-variant" size="small" class="mr-1"></v-icon>
            手动填写
          </v-btn>
          <v-btn size="small" variant="tonal" :loading="browsing" @click="openBrowseDialog">
            <v-icon icon="mdi-folder-search-outline" size="small" class="mr-1"></v-icon>
            浏览选择目录
          </v-btn>
        </div>
        <div class="d-flex align-center flex-wrap ga-2 mt-3">
          <v-text-field
            v-model="receivePath"
            label="转存目录（115 网盘路径）"
            variant="outlined"
            density="compact"
            hide-details
            style="min-width: 260px"
            class="flex-grow-1"
          />
          <v-btn size="small" color="primary" variant="flat" :loading="savingPath" @click="saveReceivePath">
            保存目录
          </v-btn>
        </div>
        <div class="text-caption text-medium-emphasis mt-2">
          转存的资源会先保存到该目录，再生成长期分享链接并写出 STRM。
        </div>
      </v-card-text>
    </v-card>

    <!-- 搜索（同时用于默认「搜索资源」注入的渠道） -->
    <v-card flat class="rounded border mb-3">
      <v-card-title class="text-subtitle-2 d-flex align-center px-3 py-2 bg-primary-lighten-5">
        <v-icon icon="mdi-cloud-search" class="mr-2" color="primary" size="small" />
        <span>网盘资源搜索</span>
        <v-spacer></v-spacer>
        <span class="text-caption text-medium-emphasis mr-2">
          {{ status.search_inject_enabled ? '已并入默认搜索资源' : '仅本页搜索' }}
        </span>
        <v-btn size="small" variant="text" color="primary" @click="loadStatus">
          <v-icon icon="mdi-refresh" size="small" class="mr-1"></v-icon>
          刷新
        </v-btn>
      </v-card-title>
      <v-card-text class="px-3 py-2">
        <v-alert v-if="error" type="error" density="compact" variant="tonal" class="mb-2 text-caption" closable>
          {{ error }}
        </v-alert>
        <v-alert v-if="message" type="success" density="compact" variant="tonal" class="mb-2 text-caption" closable>
          {{ message }}
        </v-alert>

        <div class="d-flex align-center flex-wrap ga-2 mb-2">
          <v-btn size="small" variant="tonal" @click="openQrcodeTelegram">
            <v-icon icon="mdi-send" size="small" class="mr-1"></v-icon>
            Telegram 扫码授权
          </v-btn>
          <v-chip size="small" variant="tonal" :color="status.telegram?.authorized ? 'success' : 'warning'">
            TG {{ status.telegram?.authorized ? '已授权' : '未授权' }}
          </v-chip>
        </div>

        <div class="d-flex align-center flex-wrap ga-2">
          <v-text-field
            v-model="keyword"
            label="搜索关键词（影片名或资源名）"
            variant="outlined"
            density="compact"
            hide-details
            style="min-width: 260px"
            @keyup.enter="doSearch"
          />
          <v-select
            v-model="selectedSources"
            :items="sourceItems"
            item-title="title"
            item-value="value"
            label="搜索渠道"
            variant="outlined"
            density="compact"
            multiple
            chips
            hide-details
            style="min-width: 240px"
          />
          <v-btn color="primary" variant="flat" :loading="searching" @click="doSearch">
            <v-icon icon="mdi-magnify" size="small" class="mr-1"></v-icon>
            搜索
          </v-btn>
        </div>
      </v-card-text>
    </v-card>

    <!-- 分享链接操作 -->
    <v-card flat class="rounded border mb-3">
      <v-card-title class="text-subtitle-2 d-flex align-center px-3 py-2 bg-primary-lighten-5">
        <v-icon icon="mdi-link-variant" class="mr-2" color="primary" size="small" />
        <span>115 分享链接</span>
      </v-card-title>
      <v-card-text class="px-3 py-2">
        <v-text-field
          v-model="linkUrl"
          label="粘贴 115 分享链接（支持带提取码）"
          placeholder="https://115.com/s/xxxxxxx?password=xxxx"
          variant="outlined"
          density="compact"
          hide-details
          @keyup.enter="previewLink"
        />
        <div class="d-flex align-center flex-wrap ga-2 mt-3">
          <v-btn size="small" color="primary" variant="tonal" :loading="linkBusy === 'preview'" @click="previewLink">
            <v-icon icon="mdi-file-search-outline" size="small" class="mr-1"></v-icon>
            解析链接
          </v-btn>
          <v-btn size="small" color="primary" variant="tonal" :loading="linkBusy === 'browse'" @click="openLinkList">
            <v-icon icon="mdi-format-list-bulleted" size="small" class="mr-1"></v-icon>
            文件列表
          </v-btn>
          <v-btn size="small" color="primary" variant="flat" :loading="linkBusy === 'transfer'" @click="transferLink">
            <v-icon icon="mdi-cloud-download" size="small" class="mr-1"></v-icon>
            转存
          </v-btn>
          <v-btn size="small" color="primary" variant="flat" :loading="linkBusy === 'strm'" @click="strmLink">
            <v-icon icon="mdi-file-link" size="small" class="mr-1"></v-icon>
            生成 STRM
          </v-btn>
          <v-chip v-if="selectedFids.length" size="small" variant="tonal" closable @click:close="selectedFids = []">
            已选 {{ selectedFids.length }} 项
          </v-chip>
        </div>

        <v-card v-if="linkPreview" flat class="rounded border mt-3">
          <v-card-text class="px-3 py-2">
            <div class="text-body-2 font-weight-medium">
              {{ linkPreview.title || linkPreview.share_code }}
            </div>
            <div class="text-caption text-medium-emphasis mt-1">
              文件数：{{ linkPreview.count }} · 总大小：{{ linkPreview.size_text || '未知' }}
            </div>
            <div v-if="linkPreview.entries?.length" class="mt-2">
              <div v-for="entry in linkPreview.entries" :key="entry.fid" class="d-flex align-center text-caption py-1">
                <v-icon
                  :icon="entry.is_dir ? 'mdi-folder' : 'mdi-file-video-outline'"
                  size="x-small"
                  class="mr-2"
                  :color="entry.is_dir ? 'amber' : 'primary'"
                />
                <span class="flex-grow-1" style="word-break: break-all">{{ entry.name }}</span>
                <span class="text-medium-emphasis ml-2">{{ entry.size_text }}</span>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-card-text>
    </v-card>

    <!-- 链接管理 -->
    <v-card flat class="rounded border">
      <v-card-title class="text-subtitle-2 d-flex align-center px-3 py-2 bg-primary-lighten-5">
        <v-icon icon="mdi-link-box-variant" class="mr-2" color="primary" size="small" />
        <span>链接管理</span>
        <v-spacer></v-spacer>
        <v-btn size="small" variant="text" color="primary" :loading="loadingRecords" @click="loadRecords">
          <v-icon icon="mdi-refresh" size="small" class="mr-1"></v-icon>
          刷新
        </v-btn>
      </v-card-title>
      <v-card-text class="px-3 py-2">
        <v-alert v-if="!records.length" type="info" density="compact" variant="tonal" class="text-caption">
          暂无记录。粘贴 115 分享链接后执行「转存」或「生成 STRM」，记录会显示在这里。
        </v-alert>
        <v-card v-for="(record, index) in records" :key="index" flat class="rounded border mb-2">
          <v-card-text class="px-3 py-2">
            <div class="d-flex align-center flex-wrap">
              <span class="text-body-2 font-weight-medium flex-grow-1" style="word-break: break-all">
                {{ record.title || record.share_url }}
              </span>
              <v-chip size="x-small" variant="tonal" class="ml-2">
                {{ record.source === 'link' ? '手动链接' : record.source }}
              </v-chip>
              <v-chip v-if="record.result?.total" size="x-small" variant="tonal" color="primary" class="ml-2">
                STRM {{ record.result.total }} 个
              </v-chip>
              <v-chip v-if="isPermanent(record)" size="x-small" variant="tonal" color="success" class="ml-2">
                长期有效
              </v-chip>
            </div>
            <div class="text-caption text-medium-emphasis mt-1" style="word-break: break-all">
              {{ record.result?.share_link || record.share_url }}
            </div>
            <div v-if="record.result?.output_path" class="text-caption text-medium-emphasis mt-1">
              输出目录：{{ record.result.output_path }}
            </div>
            <div class="d-flex align-center flex-wrap ga-2 mt-2">
              <v-btn size="x-small" variant="tonal" @click="copyText(record.result?.share_link || record.share_url)">
                <v-icon icon="mdi-content-copy" size="x-small" class="mr-1"></v-icon>
                复制链接
              </v-btn>
              <v-btn size="x-small" variant="tonal" @click="useRecord(record)">
                <v-icon icon="mdi-arrow-up-bold-box-outline" size="x-small" class="mr-1"></v-icon>
                填入链接
              </v-btn>
              <v-btn size="x-small" variant="tonal" :loading="recordBusy === index" @click="regenerate(record, index)">
                <v-icon icon="mdi-file-link" size="x-small" class="mr-1"></v-icon>
                生成 STRM
              </v-btn>
              <v-btn size="x-small" variant="text" color="error" @click="removeRecord(index)">
                <v-icon icon="mdi-delete-outline" size="x-small" class="mr-1"></v-icon>
                移除记录
              </v-btn>
            </div>
          </v-card-text>
        </v-card>
      </v-card-text>
    </v-card>

    <!-- 搜索结果 -->
    <v-card v-if="results.length" flat class="rounded border mt-3">
      <v-card-title class="text-subtitle-2 px-3 py-2 bg-primary-lighten-5">
        搜索结果（{{ results.length }}）
      </v-card-title>
      <v-card-text class="px-3 py-2">
        <v-card v-for="(item, index) in results" :key="index" flat class="rounded border mb-2">
          <v-card-text class="px-3 py-2">
            <div class="text-body-2 font-weight-medium">{{ item.title || item.share_url }}</div>
            <div class="text-caption text-medium-emphasis mt-1">
              来源：{{ item.source }} · 网盘：{{ item.resource_type || '未知' }}
              <span v-if="item.size_text"> · 大小：{{ item.size_text }}</span>
              <span v-if="item.access_code"> · 提取码：{{ item.access_code }}</span>
              <span v-if="item.channel"> · 频道：{{ item.channel }}</span>
            </div>
            <div class="d-flex justify-end flex-wrap ga-2 mt-2">
              <v-btn size="small" variant="text" @click="useLink(item)">
                <v-icon icon="mdi-arrow-up-bold-box-outline" size="small" class="mr-1"></v-icon>
                填入链接
              </v-btn>
              <v-btn size="small" color="primary" variant="tonal" :loading="transferringIndex === index" @click="transfer(item, index)">
                <v-icon icon="mdi-cloud-download" size="small" class="mr-1"></v-icon>
                转存并生成 STRM
              </v-btn>
            </div>
          </v-card-text>
        </v-card>
      </v-card-text>
    </v-card>

    <!-- 扫码对话框 -->
    <v-dialog v-model="qrcodeDialog" max-width="420">
      <v-card>
        <v-card-title class="text-subtitle-2 d-flex align-center">
          <v-icon icon="mdi-qrcode-scan" class="mr-2" size="small" color="primary" />
          {{ qrcodeTitle }}
          <v-spacer></v-spacer>
          <v-btn icon="mdi-close" variant="text" size="small" @click="closeQrcode"></v-btn>
        </v-card-title>
        <v-card-text class="text-center">
          <v-img
            v-if="qrcodeImage"
            :src="qrcodeImage"
            width="280"
            height="280"
            class="mx-auto my-2"
            contain
          />
          <div v-else class="text-caption text-medium-emphasis my-4">
            二维码未加载：{{ qrcodeHint || '请点击刷新' }}
          </div>
          <div class="text-caption mb-2">{{ qrcodeHint }}</div>
          <v-btn size="small" variant="tonal" :loading="qrcodeLoading" @click="refreshQrcode">
            <v-icon icon="mdi-refresh" size="small" class="mr-1"></v-icon>
            刷新二维码
          </v-btn>
          <v-text-field
            v-if="qrcodeContent"
            :model-value="qrcodeContent"
            :label="
              qrcodeMode === 'telegram'
                ? '登录链接（可在 Telegram App 内打开）'
                : '二维码内容（扫码不可用时可在 115 App 内打开）'
            "
            variant="outlined"
            density="compact"
            readonly
            hide-details
            class="mt-3 text-left"
          />
          <v-text-field
            v-if="telegramPasswordRequired"
            v-model="telegramPassword"
            label="两步验证密码"
            type="password"
            variant="outlined"
            density="compact"
            class="mt-3 text-left"
          />
        </v-card-text>
        <v-card-actions>
          <v-btn variant="text" @click="closeQrcode">关闭</v-btn>
          <v-spacer></v-spacer>
          <v-btn color="primary" variant="flat" :loading="polling" @click="pollQrcode">
            {{ qrcodeMode === 'telegram' ? '我已扫码' : '检查状态' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 分享文件列表对话框 -->
    <v-dialog v-model="listDialog" max-width="720">
      <v-card>
        <v-card-title class="text-subtitle-2 d-flex align-center">
          <v-icon icon="mdi-folder-open" class="mr-2" size="small" color="primary" />
          <span>文件列表</span>
          <v-spacer></v-spacer>
          <v-btn v-if="browseStack.length > 1" size="small" variant="text" @click="browseUp">上级</v-btn>
          <v-btn icon="mdi-close" variant="text" size="small" @click="listDialog = false"></v-btn>
        </v-card-title>
        <v-card-text style="max-height: 60vh; overflow-y: auto">
          <div class="text-caption text-medium-emphasis mb-2">
            当前目录：{{ browseStack.length ? browseStack[browseStack.length - 1].name : '根目录' }}
            <span v-if="listSizeText"> · 本层大小 {{ listSizeText }}</span>
          </div>
          <v-alert v-if="!listEntries.length" type="info" density="compact" variant="tonal" class="text-caption">
            该目录为空
          </v-alert>
          <div v-for="entry in listEntries" :key="entry.fid" class="d-flex align-center py-1">
            <v-checkbox-btn
              v-if="!entry.is_dir"
              :model-value="selectedFids.includes(entry.fid)"
              density="compact"
              hide-details
              class="mr-1"
              @update:model-value="(v) => toggleFid(entry.fid, v)"
            />
            <v-icon
              :icon="entry.is_dir ? 'mdi-folder' : 'mdi-file-video-outline'"
              size="small"
              class="mr-2"
              :color="entry.is_dir ? 'amber' : 'primary'"
            />
            <span class="flex-grow-1 text-body-2" style="word-break: break-all">{{ entry.name }}</span>
            <span class="text-caption text-medium-emphasis ml-2 mr-2">{{ entry.size_text }}</span>
            <v-btn v-if="entry.is_dir" size="x-small" variant="text" @click="browseInto(entry)">进入</v-btn>
          </div>
        </v-card-text>
        <v-card-actions>
          <v-btn variant="text" @click="listDialog = false">关闭</v-btn>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="selectedFids = []">清空选择</v-btn>
          <v-btn color="primary" variant="flat" :loading="linkBusy === 'transfer'" @click="transferLink">转存选中</v-btn>
          <v-btn color="primary" variant="flat" :loading="linkBusy === 'strm'" @click="strmLink">生成 STRM</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 网盘目录选择对话框 -->
    <v-dialog v-model="browseDialog" max-width="620">
      <v-card>
        <v-card-title class="text-subtitle-2 d-flex align-center">
          <v-icon icon="mdi-folder-search-outline" class="mr-2" size="small" color="primary" />
          <span>选择 115 转存目录</span>
          <v-spacer></v-spacer>
          <v-btn icon="mdi-close" variant="text" size="small" @click="browseDialog = false"></v-btn>
        </v-card-title>
        <v-card-text style="max-height: 55vh; overflow-y: auto">
          <div class="text-caption text-medium-emphasis mb-2">
            当前路径：{{ drivePath || '/' }}
          </div>
          <v-btn v-if="drivePath" size="small" variant="text" class="mb-2" @click="browseDrive('', 0)">
            返回根目录
          </v-btn>
          <v-alert v-if="!driveFolders.length" type="info" density="compact" variant="tonal" class="text-caption">
            没有子目录
          </v-alert>
          <div v-for="folder in driveFolders" :key="folder.fid" class="d-flex align-center py-1">
            <v-icon icon="mdi-folder" size="small" color="amber" class="mr-2" />
            <span class="flex-grow-1 text-body-2">{{ folder.name }}</span>
            <v-btn size="x-small" variant="text" @click="browseDrive(joinPath(drivePath, folder.name), Number(folder.fid))">进入</v-btn>
            <v-btn size="x-small" variant="text" color="primary" @click="pickDriveFolder(joinPath(drivePath, folder.name))">选择</v-btn>
          </div>
        </v-card-text>
        <v-card-actions>
          <v-btn variant="text" @click="browseDialog = false">关闭</v-btn>
          <v-spacer></v-spacer>
          <v-btn color="primary" variant="flat" @click="pickDriveFolder(drivePath || '/')">选择当前目录</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Cookie 对话框 -->
    <v-dialog v-model="cookieDialog" max-width="560">
      <v-card>
        <v-card-title class="text-subtitle-2 d-flex align-center">
          <v-icon icon="mdi-key-variant" class="mr-2" size="small" color="primary" />
          115 Cookie
          <v-spacer></v-spacer>
          <v-btn icon="mdi-close" variant="text" size="small" @click="cookieDialog = false"></v-btn>
        </v-card-title>
        <v-card-text>
          <div class="text-caption text-medium-emphasis mb-2">
            当前状态：{{ cookieInfo.authorized ? `已授权（${cookieInfo.account || '账号信息不可用'}）` : '未授权' }}
          </div>
          <v-text-field
            :model-value="cookieInfo.cookie_masked || '未设置'"
            label="当前 Cookie（脱敏）"
            variant="outlined"
            density="compact"
            readonly
            hide-details
          />
          <v-textarea
            v-model="cookieInput"
            label="粘贴新的 Cookie"
            variant="outlined"
            density="compact"
            rows="4"
            class="mt-3"
            placeholder="UID=...; CID=...; SEID=...; KID=..."
          />
        </v-card-text>
        <v-card-actions>
          <v-btn variant="text" @click="cookieDialog = false">关闭</v-btn>
          <v-spacer></v-spacer>
          <v-btn color="primary" variant="flat" :loading="cookieSaving" @click="saveCookie">保存并校验</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'

const props = defineProps({
  api: { type: Object, default: null },
  pluginId: { type: String, default: 'PanSearchStrm' },
  navKey: { type: String, default: 'main' },
})

const keyword = ref('')
const selectedSources = ref([])
const sourceItems = ref([])
const results = ref([])
const status = ref({ sources: [], p115: {}, telegram: {}, search_inject_enabled: true })
const error = ref('')
const message = ref('')
const searching = ref(false)
const transferringIndex = ref(-1)

const receivePath = ref('')
const savingPath = ref(false)
const cookieMasked = ref('未设置')

const linkUrl = ref('')
const linkPreview = ref(null)
const linkBusy = ref('')
const listDialog = ref(false)
const listEntries = ref([])
const listSizeText = ref('')
const browseStack = ref([{ cid: 0, name: '根目录' }])
const selectedFids = ref([])

const records = ref([])
const loadingRecords = ref(false)
const recordBusy = ref(-1)

const qrcodeDialog = ref(false)
const qrcodeMode = ref('115')
const qrcodeImage = ref('')
const qrcodeContent = ref('')
const qrcodeHint = ref('')
const qrcodeLoading = ref(false)
const polling = ref(false)
const telegramPassword = ref('')
const telegramPasswordRequired = ref(false)

const browseDialog = ref(false)
const drivePath = ref('')
const driveFolders = ref([])
const browsing = ref(false)

const cookieDialog = ref(false)
const cookieInfo = ref({})
const cookieInput = ref('')
const cookieSaving = ref(false)

const qrcodeTitle = computed(() =>
  qrcodeMode.value === '115' ? '115 网盘扫码登录' : 'Telegram 扫码登录'
)

/**
 * 统一解包接口返回：MoviePilot 注入的 api 会直接把插件返回值交给调用方。
 */
function unwrap(resp) {
  if (!resp || typeof resp !== 'object') return {}
  if ('success' in resp || 'entries' in resp || 'records' in resp) return resp
  if (resp.data && typeof resp.data === 'object' && !Array.isArray(resp.data)) return resp.data
  return resp
}

/**
 * 读取插件状态、115 授权状态与渠道列表。
 */
async function loadStatus() {
  if (!props.api) return
  try {
    const payload = unwrap(await props.api.get(`plugin/${props.pluginId}/status`))
    status.value = payload
    receivePath.value = payload.p115?.receive_path || receivePath.value
    const names = (payload.sources || []).map((item) => ({
      title: { pansou: '盘搜', juying: '聚影', telegram: 'Telegram' }[item] || item,
      value: item,
    }))
    sourceItems.value = names
    if (!selectedSources.value.length) {
      selectedSources.value = names.map((item) => item.value)
    }
  } catch (err) {
    error.value = `读取插件状态失败：${err?.message || err}`
  }
}

/**
 * 读取脱敏后的 Cookie 与授权状态。
 */
async function loadCookie() {
  if (!props.api) return
  try {
    const payload = unwrap(await props.api.get(`plugin/${props.pluginId}/p115/cookie`))
    cookieInfo.value = payload
    cookieMasked.value = payload.cookie_masked || '未设置'
  } catch (err) {
    cookieMasked.value = '读取失败'
  }
}

/**
 * 执行网盘资源搜索。
 */
async function doSearch() {
  error.value = ''
  message.value = ''
  if (!keyword.value.trim()) {
    error.value = '请输入搜索关键词'
    return
  }
  searching.value = true
  try {
    const payload = unwrap(
      await props.api.post(`plugin/${props.pluginId}/search`, {
        keyword: keyword.value.trim(),
        sources: selectedSources.value,
      })
    )
    if (payload.success === false) {
      error.value = payload.message || '搜索失败'
      results.value = []
    } else {
      results.value = payload.results || []
      message.value = `共找到 ${results.value.length} 条网盘资源`
    }
  } catch (err) {
    error.value = `搜索失败：${err?.message || err}`
  } finally {
    searching.value = false
  }
}

/**
 * 保存 115 转存目录。
 */
async function saveReceivePath() {
  if (!receivePath.value.trim()) {
    error.value = '转存目录不能为空'
    return
  }
  savingPath.value = true
  error.value = ''
  try {
    const payload = unwrap(await props.api.get(`plugin/${props.pluginId}/config`))
    const config = payload.config || payload || {}
    config.p115 = { ...(config.p115 || {}), receive_path: receivePath.value.trim() }
    const saved = unwrap(await props.api.post(`plugin/${props.pluginId}/config`, config))
    if (saved.success === false) {
      error.value = saved.message || '保存失败'
    } else {
      message.value = `转存目录已保存：${receivePath.value.trim()}`
    }
  } catch (err) {
    error.value = `保存失败：${err?.message || err}`
  } finally {
    savingPath.value = false
  }
}

/**
 * 打开 115 网盘目录浏览器。
 */
async function openBrowseDialog() {
  browseDialog.value = true
  await browseDrive('', 0)
}

/**
 * 浏览 115 网盘指定目录。
 */
async function browseDrive(path, cid) {
  browsing.value = true
  try {
    const payload = unwrap(
      await props.api.get(`plugin/${props.pluginId}/browse?path=${encodeURIComponent(path)}&cid=${cid}`)
    )
    if (payload.success === false) {
      error.value = payload.message || '浏览目录失败'
      driveFolders.value = []
      return
    }
    drivePath.value = path || ''
    driveFolders.value = payload.folders || []
  } catch (err) {
    error.value = `浏览目录失败：${err?.message || err}`
  } finally {
    browsing.value = false
  }
}

/**
 * 拼接网盘路径。
 */
function joinPath(base, name) {
  const prefix = String(base || '').replace(/^\/+|\/+$/g, '')
  return prefix ? `/${prefix}/${name}` : `/${name}`
}

/**
 * 采用选中的网盘目录作为转存目录。
 */
function pickDriveFolder(path) {
  receivePath.value = path || '/'
  browseDialog.value = false
  saveReceivePath()
}

/**
 * 把链接或搜索结果填入分享链接框。
 */
function useLink(item) {
  linkUrl.value = item.share_url || ''
  linkPreview.value = null
  selectedFids.value = []
  message.value = '已填入分享链接，可继续执行文件列表、转存或生成 STRM'
}

/**
 * 把历史记录里的链接重新填入操作区。
 */
function useRecord(record) {
  linkUrl.value = record.result?.share_link || record.share_url || ''
  message.value = '已填入链接'
}

/**
 * 判断记录是否为长期分享。
 */
function isPermanent(record) {
  const duration = Number(record.result?.duration)
  return record.result?.share_code && duration === -1
}

/**
 * 解析分享链接并展示根目录条目。
 */
async function previewLink() {
  error.value = ''
  message.value = ''
  if (!linkUrl.value.trim()) {
    error.value = '请先粘贴 115 分享链接'
    return
  }
  linkBusy.value = 'preview'
  try {
    const payload = unwrap(
      await props.api.post(`plugin/${props.pluginId}/link/preview`, { url: linkUrl.value.trim() })
    )
    if (payload.success === false) {
      error.value = payload.message || '解析失败'
      linkPreview.value = null
    } else {
      linkPreview.value = payload
      message.value = `已解析：${payload.title || payload.share_code}`
    }
  } catch (err) {
    error.value = `解析失败：${err?.message || err}`
  } finally {
    linkBusy.value = ''
  }
}

/**
 * 打开分享文件列表。
 */
async function openLinkList() {
  if (!linkUrl.value.trim()) {
    error.value = '请先粘贴 115 分享链接'
    return
  }
  browseStack.value = [{ cid: 0, name: '根目录' }]
  listDialog.value = true
  await browseShare(0)
}

/**
 * 读取分享中某个目录的条目。
 */
async function browseShare(cid) {
  linkBusy.value = 'browse'
  error.value = ''
  try {
    const payload = unwrap(
      await props.api.post(`plugin/${props.pluginId}/link/browse`, {
        url: linkUrl.value.trim(),
        cid,
      })
    )
    if (payload.success === false) {
      error.value = payload.message || '读取目录失败'
      listEntries.value = []
    } else {
      listEntries.value = payload.entries || []
      listSizeText.value = payload.size_text || ''
    }
  } catch (err) {
    error.value = `读取目录失败：${err?.message || err}`
  } finally {
    linkBusy.value = ''
  }
}

/**
 * 进入分享中的子目录。
 */
async function browseInto(entry) {
  browseStack.value.push({ cid: Number(entry.fid), name: entry.name })
  await browseShare(Number(entry.fid))
}

/**
 * 返回分享的上级目录。
 */
async function browseUp() {
  if (browseStack.value.length <= 1) return
  browseStack.value.pop()
  const parent = browseStack.value[browseStack.value.length - 1]
  await browseShare(parent.cid)
}

/**
 * 切换单个文件的选择状态。
 */
function toggleFid(fid, checked) {
  if (checked) {
    if (!selectedFids.value.includes(fid)) selectedFids.value.push(fid)
  } else {
    selectedFids.value = selectedFids.value.filter((item) => item !== fid)
  }
}

/**
 * 仅转存分享内容。
 */
async function transferLink() {
  error.value = ''
  message.value = ''
  if (!linkUrl.value.trim()) {
    error.value = '请先粘贴 115 分享链接'
    return
  }
  linkBusy.value = 'transfer'
  try {
    const payload = unwrap(
      await props.api.post(`plugin/${props.pluginId}/link/transfer`, {
        url: linkUrl.value.trim(),
        file_ids: selectedFids.value,
        title: linkPreview.value?.title || '',
      })
    )
    if (payload.success === false) {
      error.value = payload.message || '转存失败'
    } else {
      message.value = `已转存 ${payload.transferred || 0} 项到 ${payload.target_path || ''}`
      listDialog.value = false
      await loadRecords()
    }
  } catch (err) {
    error.value = `转存失败：${err?.message || err}`
  } finally {
    linkBusy.value = ''
  }
}

/**
 * 转存后生成长期分享并写出 STRM。
 */
async function strmLink() {
  error.value = ''
  message.value = ''
  if (!linkUrl.value.trim()) {
    error.value = '请先粘贴 115 分享链接'
    return
  }
  linkBusy.value = 'strm'
  try {
    const payload = unwrap(
      await props.api.post(`plugin/${props.pluginId}/link/strm`, {
        url: linkUrl.value.trim(),
        file_ids: selectedFids.value,
        title: linkPreview.value?.title || '',
      })
    )
    if (payload.success === false) {
      error.value = payload.message || '生成失败'
    } else {
      message.value = `已生成 ${payload.total || 0} 个 STRM，输出目录：${payload.output_path || ''}`
      listDialog.value = false
      await loadRecords()
    }
  } catch (err) {
    error.value = `生成失败：${err?.message || err}`
  } finally {
    linkBusy.value = ''
  }
}

/**
 * 转存搜索结果中的单条资源。
 */
async function transfer(item, index) {
  error.value = ''
  message.value = ''
  transferringIndex.value = index
  try {
    const payload = unwrap(await props.api.post(`plugin/${props.pluginId}/transfer`, item))
    if (payload.success === false) {
      error.value = payload.message || '转存失败'
    } else {
      message.value = `已生成 ${payload.total || 0} 个 STRM，输出目录：${payload.output_path || ''}`
      await loadRecords()
    }
  } catch (err) {
    error.value = `转存失败：${err?.message || err}`
  } finally {
    transferringIndex.value = -1
  }
}

/**
 * 用历史记录的分享链接重新生成 STRM。
 */
async function regenerate(record, index) {
  const url = record.result?.share_link || record.share_url
  if (!url) {
    error.value = '该记录没有可用的分享链接'
    return
  }
  recordBusy.value = index
  error.value = ''
  try {
    const payload = unwrap(
      await props.api.post(`plugin/${props.pluginId}/link/strm`, { url, title: record.title || '' })
    )
    if (payload.success === false) {
      error.value = payload.message || '生成失败'
    } else {
      message.value = `已重新生成 ${payload.total || 0} 个 STRM`
      await loadRecords()
    }
  } catch (err) {
    error.value = `生成失败：${err?.message || err}`
  } finally {
    recordBusy.value = -1
  }
}

/**
 * 移除一条转存记录。
 */
async function removeRecord(index) {
  error.value = ''
  try {
    const payload = unwrap(
      await props.api.post(`plugin/${props.pluginId}/records/remove`, { index })
    )
    if (payload.success === false) {
      error.value = payload.message || '移除失败'
    } else {
      records.value = payload.records || []
    }
  } catch (err) {
    error.value = `移除失败：${err?.message || err}`
  }
}

/**
 * 复制文本到剪贴板。
 */
async function copyText(text) {
  if (!text) return
  try {
    await navigator.clipboard.writeText(text)
    message.value = '链接已复制'
  } catch (err) {
    message.value = `复制失败，请手动复制：${text}`
  }
}

/**
 * 按当前扫码模式刷新二维码，避免 Telegram 模式下误取 115 的二维码。
 */
async function refreshQrcode() {
  if (qrcodeMode.value === 'telegram') {
    await refreshQrcodeTelegram()
    return
  }
  await refreshQrcode115()
}

/**
 * 加载 115 扫码登录二维码。
 */
async function refreshQrcode115() {
  qrcodeLoading.value = true
  qrcodeImage.value = ''
  qrcodeContent.value = ''
  try {
    const payload = unwrap(await props.api.get(`plugin/${props.pluginId}/qrcode/115`))
    if (payload.success === false) {
      qrcodeHint.value = payload.message || '获取二维码失败'
      return
    }
    qrcodeImage.value = payload.qr_image || ''
    qrcodeContent.value = payload.qr_content || ''
    qrcodeHint.value = payload.qr_image
      ? payload.tips || '请使用 115 客户端扫描二维码'
      : '二维码图片生成失败，请用 115 App 打开下方链接'
  } catch (err) {
    qrcodeHint.value = `获取二维码失败：${err?.message || err}`
  } finally {
    qrcodeLoading.value = false
  }
}

/**
 * 加载 Telegram 扫码登录二维码。
 */
async function refreshQrcodeTelegram() {
  qrcodeLoading.value = true
  qrcodeImage.value = ''
  qrcodeContent.value = ''
  qrcodeHint.value = '正在获取 Telegram 登录二维码…'
  try {
    const payload = unwrap(await props.api.get(`plugin/${props.pluginId}/qrcode/telegram`))
    if (payload.success === false) {
      qrcodeHint.value = payload.message || '获取二维码失败'
      return
    }
    qrcodeImage.value = payload.qr_image || ''
    qrcodeContent.value = payload.url || ''
    qrcodeHint.value = '请使用 Telegram App 扫码并在 App 内确认登录'
  } catch (err) {
    qrcodeHint.value = `获取二维码失败：${err?.message || err}`
  } finally {
    qrcodeLoading.value = false
  }
}

/**
 * 打开 115 扫码登录对话框。
 */
async function openQrcode115() {
  qrcodeMode.value = '115'
  telegramPasswordRequired.value = false
  qrcodeDialog.value = true
  await refreshQrcode115()
}

/**
 * 打开 Telegram 扫码登录对话框。
 */
async function openQrcodeTelegram() {
  qrcodeMode.value = 'telegram'
  telegramPasswordRequired.value = false
  qrcodeDialog.value = true
  await refreshQrcodeTelegram()
}

/**
 * 轮询扫码结果。
 */
async function pollQrcode() {
  polling.value = true
  try {
    if (qrcodeMode.value === '115') {
      const payload = unwrap(await props.api.get(`plugin/${props.pluginId}/qrcode/115/status`))
      qrcodeHint.value = payload.message || '等待扫码'
      if (payload.status === 'confirmed') {
        message.value = '115 授权成功'
        qrcodeDialog.value = false
        await loadStatus()
        await loadCookie()
      } else if (payload.status === 'expired') {
        await refreshQrcode()
      }
    } else {
      const payload = unwrap(
        await props.api.post(`plugin/${props.pluginId}/qrcode/telegram/wait`, {
          password: telegramPassword.value,
        })
      )
      qrcodeHint.value = payload.message || '等待扫码'
      if (payload.status === 'password_required') {
        telegramPasswordRequired.value = true
      }
      if (payload.status === 'confirmed') {
        message.value = 'Telegram 授权成功'
        qrcodeDialog.value = false
        await loadStatus()
      }
    }
  } catch (err) {
    qrcodeHint.value = `检查失败：${err?.message || err}`
  } finally {
    polling.value = false
  }
}

/**
 * 关闭扫码对话框。
 */
function closeQrcode() {
  qrcodeDialog.value = false
  telegramPassword.value = ''
  telegramPasswordRequired.value = false
}

/**
 * 打开 Cookie 管理对话框。
 */
async function openCookieDialog() {
  cookieDialog.value = true
  cookieInput.value = ''
  await loadCookie()
}

/**
 * 保存手动填写的 Cookie 并校验。
 */
async function saveCookie() {
  error.value = ''
  message.value = ''
  cookieSaving.value = true
  try {
    const payload = unwrap(
      await props.api.post(`plugin/${props.pluginId}/p115/cookie`, {
        cookies: cookieInput.value,
      })
    )
    if (payload.success === false) {
      error.value = payload.message || '保存失败'
    } else {
      message.value = payload.authorized
        ? `Cookie 已保存，账号：${payload.account || '未知'}`
        : payload.message || 'Cookie 已保存，但校验未通过'
      cookieInput.value = ''
      await loadCookie()
      await loadStatus()
    }
  } catch (err) {
    error.value = `保存失败：${err?.message || err}`
  } finally {
    cookieSaving.value = false
  }
}

/**
 * 读取转存记录。
 */
async function loadRecords() {
  if (!props.api) return
  loadingRecords.value = true
  try {
    const payload = unwrap(await props.api.get(`plugin/${props.pluginId}/records`))
    records.value = payload.records || []
  } catch (err) {
    error.value = `读取记录失败：${err?.message || err}`
  } finally {
    loadingRecords.value = false
  }
}

onMounted(async () => {
  await loadStatus()
  await loadCookie()
  await loadRecords()
})
</script>
