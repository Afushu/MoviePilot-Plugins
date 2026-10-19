import { importShared } from './__federation_fn_import-JrT3xvdd.js';

const {resolveComponent:_resolveComponent,createVNode:_createVNode,createElementVNode:_createElementVNode,toDisplayString:_toDisplayString,createTextVNode:_createTextVNode,withCtx:_withCtx,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,withKeys:_withKeys,renderList:_renderList,Fragment:_Fragment,createElementBlock:_createElementBlock} = await importShared('vue');


const _hoisted_1 = { class: "pansearch-panel" };
const _hoisted_2 = { class: "d-flex align-center flex-wrap ga-2" };
const _hoisted_3 = { class: "d-flex align-center flex-wrap ga-2 mt-3" };
const _hoisted_4 = { class: "text-caption text-medium-emphasis mr-2" };
const _hoisted_5 = { class: "d-flex align-center flex-wrap ga-2 mb-2" };
const _hoisted_6 = { class: "d-flex align-center flex-wrap ga-2" };
const _hoisted_7 = { class: "d-flex align-center flex-wrap ga-2 mt-3" };
const _hoisted_8 = { class: "text-body-2 font-weight-medium" };
const _hoisted_9 = { class: "text-caption text-medium-emphasis mt-1" };
const _hoisted_10 = {
  key: 0,
  class: "mt-2"
};
const _hoisted_11 = {
  class: "flex-grow-1",
  style: {"word-break":"break-all"}
};
const _hoisted_12 = { class: "text-medium-emphasis ml-2" };
const _hoisted_13 = { class: "d-flex align-center flex-wrap" };
const _hoisted_14 = {
  class: "text-body-2 font-weight-medium flex-grow-1",
  style: {"word-break":"break-all"}
};
const _hoisted_15 = {
  class: "text-caption text-medium-emphasis mt-1",
  style: {"word-break":"break-all"}
};
const _hoisted_16 = {
  key: 0,
  class: "text-caption text-medium-emphasis mt-1"
};
const _hoisted_17 = { class: "d-flex align-center flex-wrap ga-2 mt-2" };
const _hoisted_18 = { class: "text-body-2 font-weight-medium" };
const _hoisted_19 = { class: "text-caption text-medium-emphasis mt-1" };
const _hoisted_20 = { key: 0 };
const _hoisted_21 = { key: 1 };
const _hoisted_22 = { key: 2 };
const _hoisted_23 = { class: "d-flex justify-end flex-wrap ga-2 mt-2" };
const _hoisted_24 = {
  key: 1,
  class: "text-caption text-medium-emphasis my-4"
};
const _hoisted_25 = { class: "text-caption mb-2" };
const _hoisted_26 = { class: "text-caption text-medium-emphasis mb-2" };
const _hoisted_27 = { key: 0 };
const _hoisted_28 = {
  class: "flex-grow-1 text-body-2",
  style: {"word-break":"break-all"}
};
const _hoisted_29 = { class: "text-caption text-medium-emphasis ml-2 mr-2" };
const _hoisted_30 = { class: "text-caption text-medium-emphasis mb-2" };
const _hoisted_31 = { class: "flex-grow-1 text-body-2" };
const _hoisted_32 = { class: "text-caption text-medium-emphasis mb-2" };

const {computed,onMounted,ref} = await importShared('vue');



const _sfc_main = {
  __name: 'SearchPanel',
  props: {
  api: { type: Object, default: null },
  pluginId: { type: String, default: 'PanSearchStrm' },
  navKey: { type: String, default: 'main' },
},
  setup(__props) {

const props = __props;

const keyword = ref('');
const selectedSources = ref([]);
const sourceItems = ref([]);
const results = ref([]);
const status = ref({ sources: [], p115: {}, telegram: {}, search_inject_enabled: true });
const error = ref('');
const message = ref('');
const searching = ref(false);
const transferringIndex = ref(-1);

const receivePath = ref('');
const savingPath = ref(false);
const cookieMasked = ref('未设置');

const linkUrl = ref('');
const linkPreview = ref(null);
const linkBusy = ref('');
const listDialog = ref(false);
const listEntries = ref([]);
const listSizeText = ref('');
const browseStack = ref([{ cid: 0, name: '根目录' }]);
const selectedFids = ref([]);

const records = ref([]);
const loadingRecords = ref(false);
const recordBusy = ref(-1);

const qrcodeDialog = ref(false);
const qrcodeMode = ref('115');
const qrcodeImage = ref('');
const qrcodeContent = ref('');
const qrcodeHint = ref('');
const qrcodeLoading = ref(false);
const polling = ref(false);
const telegramPassword = ref('');
const telegramPasswordRequired = ref(false);

const browseDialog = ref(false);
const drivePath = ref('');
const driveFolders = ref([]);
const browsing = ref(false);

const cookieDialog = ref(false);
const cookieInfo = ref({});
const cookieInput = ref('');
const cookieSaving = ref(false);

const qrcodeTitle = computed(() =>
  qrcodeMode.value === '115' ? '115 网盘扫码登录' : 'Telegram 扫码登录'
);

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
    const payload = unwrap(await props.api.get(`plugin/${props.pluginId}/status`));
    status.value = payload;
    receivePath.value = payload.p115?.receive_path || receivePath.value;
    const names = (payload.sources || []).map((item) => ({
      title: { pansou: '盘搜', juying: '聚影', telegram: 'Telegram' }[item] || item,
      value: item,
    }));
    sourceItems.value = names;
    if (!selectedSources.value.length) {
      selectedSources.value = names.map((item) => item.value);
    }
  } catch (err) {
    error.value = `读取插件状态失败：${err?.message || err}`;
  }
}

/**
 * 读取脱敏后的 Cookie 与授权状态。
 */
async function loadCookie() {
  if (!props.api) return
  try {
    const payload = unwrap(await props.api.get(`plugin/${props.pluginId}/p115/cookie`));
    cookieInfo.value = payload;
    cookieMasked.value = payload.cookie_masked || '未设置';
  } catch (err) {
    cookieMasked.value = '读取失败';
  }
}

/**
 * 执行网盘资源搜索。
 */
async function doSearch() {
  error.value = '';
  message.value = '';
  if (!keyword.value.trim()) {
    error.value = '请输入搜索关键词';
    return
  }
  searching.value = true;
  try {
    const payload = unwrap(
      await props.api.post(`plugin/${props.pluginId}/search`, {
        keyword: keyword.value.trim(),
        sources: selectedSources.value,
      })
    );
    if (payload.success === false) {
      error.value = payload.message || '搜索失败';
      results.value = [];
    } else {
      results.value = payload.results || [];
      message.value = `共找到 ${results.value.length} 条网盘资源`;
    }
  } catch (err) {
    error.value = `搜索失败：${err?.message || err}`;
  } finally {
    searching.value = false;
  }
}

/**
 * 保存 115 转存目录。
 */
async function saveReceivePath() {
  if (!receivePath.value.trim()) {
    error.value = '转存目录不能为空';
    return
  }
  savingPath.value = true;
  error.value = '';
  try {
    const payload = unwrap(await props.api.get(`plugin/${props.pluginId}/config`));
    const config = payload.config || payload || {};
    config.p115 = { ...(config.p115 || {}), receive_path: receivePath.value.trim() };
    const saved = unwrap(await props.api.post(`plugin/${props.pluginId}/config`, config));
    if (saved.success === false) {
      error.value = saved.message || '保存失败';
    } else {
      message.value = `转存目录已保存：${receivePath.value.trim()}`;
    }
  } catch (err) {
    error.value = `保存失败：${err?.message || err}`;
  } finally {
    savingPath.value = false;
  }
}

/**
 * 打开 115 网盘目录浏览器。
 */
async function openBrowseDialog() {
  browseDialog.value = true;
  await browseDrive('', 0);
}

/**
 * 浏览 115 网盘指定目录。
 */
async function browseDrive(path, cid) {
  browsing.value = true;
  try {
    const payload = unwrap(
      await props.api.get(`plugin/${props.pluginId}/browse?path=${encodeURIComponent(path)}&cid=${cid}`)
    );
    if (payload.success === false) {
      error.value = payload.message || '浏览目录失败';
      driveFolders.value = [];
      return
    }
    drivePath.value = path || '';
    driveFolders.value = payload.folders || [];
  } catch (err) {
    error.value = `浏览目录失败：${err?.message || err}`;
  } finally {
    browsing.value = false;
  }
}

/**
 * 拼接网盘路径。
 */
function joinPath(base, name) {
  const prefix = String(base || '').replace(/^\/+|\/+$/g, '');
  return prefix ? `/${prefix}/${name}` : `/${name}`
}

/**
 * 采用选中的网盘目录作为转存目录。
 */
function pickDriveFolder(path) {
  receivePath.value = path || '/';
  browseDialog.value = false;
  saveReceivePath();
}

/**
 * 把链接或搜索结果填入分享链接框。
 */
function useLink(item) {
  linkUrl.value = item.share_url || '';
  linkPreview.value = null;
  selectedFids.value = [];
  message.value = '已填入分享链接，可继续执行文件列表、转存或生成 STRM';
}

/**
 * 把历史记录里的链接重新填入操作区。
 */
function useRecord(record) {
  linkUrl.value = record.result?.share_link || record.share_url || '';
  message.value = '已填入链接';
}

/**
 * 判断记录是否为长期分享。
 */
function isPermanent(record) {
  const duration = Number(record.result?.duration);
  return record.result?.share_code && duration === -1
}

/**
 * 解析分享链接并展示根目录条目。
 */
async function previewLink() {
  error.value = '';
  message.value = '';
  if (!linkUrl.value.trim()) {
    error.value = '请先粘贴 115 分享链接';
    return
  }
  linkBusy.value = 'preview';
  try {
    const payload = unwrap(
      await props.api.post(`plugin/${props.pluginId}/link/preview`, { url: linkUrl.value.trim() })
    );
    if (payload.success === false) {
      error.value = payload.message || '解析失败';
      linkPreview.value = null;
    } else {
      linkPreview.value = payload;
      message.value = `已解析：${payload.title || payload.share_code}`;
    }
  } catch (err) {
    error.value = `解析失败：${err?.message || err}`;
  } finally {
    linkBusy.value = '';
  }
}

/**
 * 打开分享文件列表。
 */
async function openLinkList() {
  if (!linkUrl.value.trim()) {
    error.value = '请先粘贴 115 分享链接';
    return
  }
  browseStack.value = [{ cid: 0, name: '根目录' }];
  listDialog.value = true;
  await browseShare(0);
}

/**
 * 读取分享中某个目录的条目。
 */
async function browseShare(cid) {
  linkBusy.value = 'browse';
  error.value = '';
  try {
    const payload = unwrap(
      await props.api.post(`plugin/${props.pluginId}/link/browse`, {
        url: linkUrl.value.trim(),
        cid,
      })
    );
    if (payload.success === false) {
      error.value = payload.message || '读取目录失败';
      listEntries.value = [];
    } else {
      listEntries.value = payload.entries || [];
      listSizeText.value = payload.size_text || '';
    }
  } catch (err) {
    error.value = `读取目录失败：${err?.message || err}`;
  } finally {
    linkBusy.value = '';
  }
}

/**
 * 进入分享中的子目录。
 */
async function browseInto(entry) {
  browseStack.value.push({ cid: Number(entry.fid), name: entry.name });
  await browseShare(Number(entry.fid));
}

/**
 * 返回分享的上级目录。
 */
async function browseUp() {
  if (browseStack.value.length <= 1) return
  browseStack.value.pop();
  const parent = browseStack.value[browseStack.value.length - 1];
  await browseShare(parent.cid);
}

/**
 * 切换单个文件的选择状态。
 */
function toggleFid(fid, checked) {
  if (checked) {
    if (!selectedFids.value.includes(fid)) selectedFids.value.push(fid);
  } else {
    selectedFids.value = selectedFids.value.filter((item) => item !== fid);
  }
}

/**
 * 仅转存分享内容。
 */
async function transferLink() {
  error.value = '';
  message.value = '';
  if (!linkUrl.value.trim()) {
    error.value = '请先粘贴 115 分享链接';
    return
  }
  linkBusy.value = 'transfer';
  try {
    const payload = unwrap(
      await props.api.post(`plugin/${props.pluginId}/link/transfer`, {
        url: linkUrl.value.trim(),
        file_ids: selectedFids.value,
        title: linkPreview.value?.title || '',
      })
    );
    if (payload.success === false) {
      error.value = payload.message || '转存失败';
    } else {
      message.value = `已转存 ${payload.transferred || 0} 项到 ${payload.target_path || ''}`;
      listDialog.value = false;
      await loadRecords();
    }
  } catch (err) {
    error.value = `转存失败：${err?.message || err}`;
  } finally {
    linkBusy.value = '';
  }
}

/**
 * 转存后生成长期分享并写出 STRM。
 */
async function strmLink() {
  error.value = '';
  message.value = '';
  if (!linkUrl.value.trim()) {
    error.value = '请先粘贴 115 分享链接';
    return
  }
  linkBusy.value = 'strm';
  try {
    const payload = unwrap(
      await props.api.post(`plugin/${props.pluginId}/link/strm`, {
        url: linkUrl.value.trim(),
        file_ids: selectedFids.value,
        title: linkPreview.value?.title || '',
      })
    );
    if (payload.success === false) {
      error.value = payload.message || '生成失败';
    } else {
      message.value = `已生成 ${payload.total || 0} 个 STRM，输出目录：${payload.output_path || ''}`;
      listDialog.value = false;
      await loadRecords();
    }
  } catch (err) {
    error.value = `生成失败：${err?.message || err}`;
  } finally {
    linkBusy.value = '';
  }
}

/**
 * 转存搜索结果中的单条资源。
 */
async function transfer(item, index) {
  error.value = '';
  message.value = '';
  transferringIndex.value = index;
  try {
    const payload = unwrap(await props.api.post(`plugin/${props.pluginId}/transfer`, item));
    if (payload.success === false) {
      error.value = payload.message || '转存失败';
    } else {
      message.value = `已生成 ${payload.total || 0} 个 STRM，输出目录：${payload.output_path || ''}`;
      await loadRecords();
    }
  } catch (err) {
    error.value = `转存失败：${err?.message || err}`;
  } finally {
    transferringIndex.value = -1;
  }
}

/**
 * 用历史记录的分享链接重新生成 STRM。
 */
async function regenerate(record, index) {
  const url = record.result?.share_link || record.share_url;
  if (!url) {
    error.value = '该记录没有可用的分享链接';
    return
  }
  recordBusy.value = index;
  error.value = '';
  try {
    const payload = unwrap(
      await props.api.post(`plugin/${props.pluginId}/link/strm`, { url, title: record.title || '' })
    );
    if (payload.success === false) {
      error.value = payload.message || '生成失败';
    } else {
      message.value = `已重新生成 ${payload.total || 0} 个 STRM`;
      await loadRecords();
    }
  } catch (err) {
    error.value = `生成失败：${err?.message || err}`;
  } finally {
    recordBusy.value = -1;
  }
}

/**
 * 移除一条转存记录。
 */
async function removeRecord(index) {
  error.value = '';
  try {
    const payload = unwrap(
      await props.api.post(`plugin/${props.pluginId}/records/remove`, { index })
    );
    if (payload.success === false) {
      error.value = payload.message || '移除失败';
    } else {
      records.value = payload.records || [];
    }
  } catch (err) {
    error.value = `移除失败：${err?.message || err}`;
  }
}

/**
 * 复制文本到剪贴板。
 */
async function copyText(text) {
  if (!text) return
  try {
    await navigator.clipboard.writeText(text);
    message.value = '链接已复制';
  } catch (err) {
    message.value = `复制失败，请手动复制：${text}`;
  }
}

/**
 * 按当前扫码模式刷新二维码，避免 Telegram 模式下误取 115 的二维码。
 */
async function refreshQrcode() {
  if (qrcodeMode.value === 'telegram') {
    await refreshQrcodeTelegram();
    return
  }
  await refreshQrcode115();
}

/**
 * 加载 115 扫码登录二维码。
 */
async function refreshQrcode115() {
  qrcodeLoading.value = true;
  qrcodeImage.value = '';
  qrcodeContent.value = '';
  try {
    const payload = unwrap(await props.api.get(`plugin/${props.pluginId}/qrcode/115`));
    if (payload.success === false) {
      qrcodeHint.value = payload.message || '获取二维码失败';
      return
    }
    qrcodeImage.value = payload.qr_image || '';
    qrcodeContent.value = payload.qr_content || '';
    qrcodeHint.value = payload.qr_image
      ? payload.tips || '请使用 115 客户端扫描二维码'
      : '二维码图片生成失败，请用 115 App 打开下方链接';
  } catch (err) {
    qrcodeHint.value = `获取二维码失败：${err?.message || err}`;
  } finally {
    qrcodeLoading.value = false;
  }
}

/**
 * 加载 Telegram 扫码登录二维码。
 */
async function refreshQrcodeTelegram() {
  qrcodeLoading.value = true;
  qrcodeImage.value = '';
  qrcodeContent.value = '';
  qrcodeHint.value = '正在获取 Telegram 登录二维码…';
  try {
    const payload = unwrap(await props.api.get(`plugin/${props.pluginId}/qrcode/telegram`));
    if (payload.success === false) {
      qrcodeHint.value = payload.message || '获取二维码失败';
      return
    }
    qrcodeImage.value = payload.qr_image || '';
    qrcodeContent.value = payload.url || '';
    qrcodeHint.value = '请使用 Telegram App 扫码并在 App 内确认登录';
  } catch (err) {
    qrcodeHint.value = `获取二维码失败：${err?.message || err}`;
  } finally {
    qrcodeLoading.value = false;
  }
}

/**
 * 打开 115 扫码登录对话框。
 */
async function openQrcode115() {
  qrcodeMode.value = '115';
  telegramPasswordRequired.value = false;
  qrcodeDialog.value = true;
  await refreshQrcode115();
}

/**
 * 打开 Telegram 扫码登录对话框。
 */
async function openQrcodeTelegram() {
  qrcodeMode.value = 'telegram';
  telegramPasswordRequired.value = false;
  qrcodeDialog.value = true;
  await refreshQrcodeTelegram();
}

/**
 * 轮询扫码结果。
 */
async function pollQrcode() {
  polling.value = true;
  try {
    if (qrcodeMode.value === '115') {
      const payload = unwrap(await props.api.get(`plugin/${props.pluginId}/qrcode/115/status`));
      qrcodeHint.value = payload.message || '等待扫码';
      if (payload.status === 'confirmed') {
        message.value = '115 授权成功';
        qrcodeDialog.value = false;
        await loadStatus();
        await loadCookie();
      } else if (payload.status === 'expired') {
        await refreshQrcode();
      }
    } else {
      const payload = unwrap(
        await props.api.post(`plugin/${props.pluginId}/qrcode/telegram/wait`, {
          password: telegramPassword.value,
        })
      );
      qrcodeHint.value = payload.message || '等待扫码';
      if (payload.status === 'password_required') {
        telegramPasswordRequired.value = true;
      }
      if (payload.status === 'confirmed') {
        message.value = 'Telegram 授权成功';
        qrcodeDialog.value = false;
        await loadStatus();
      }
    }
  } catch (err) {
    qrcodeHint.value = `检查失败：${err?.message || err}`;
  } finally {
    polling.value = false;
  }
}

/**
 * 关闭扫码对话框。
 */
function closeQrcode() {
  qrcodeDialog.value = false;
  telegramPassword.value = '';
  telegramPasswordRequired.value = false;
}

/**
 * 打开 Cookie 管理对话框。
 */
async function openCookieDialog() {
  cookieDialog.value = true;
  cookieInput.value = '';
  await loadCookie();
}

/**
 * 保存手动填写的 Cookie 并校验。
 */
async function saveCookie() {
  error.value = '';
  message.value = '';
  cookieSaving.value = true;
  try {
    const payload = unwrap(
      await props.api.post(`plugin/${props.pluginId}/p115/cookie`, {
        cookies: cookieInput.value,
      })
    );
    if (payload.success === false) {
      error.value = payload.message || '保存失败';
    } else {
      message.value = payload.authorized
        ? `Cookie 已保存，账号：${payload.account || '未知'}`
        : payload.message || 'Cookie 已保存，但校验未通过';
      cookieInput.value = '';
      await loadCookie();
      await loadStatus();
    }
  } catch (err) {
    error.value = `保存失败：${err?.message || err}`;
  } finally {
    cookieSaving.value = false;
  }
}

/**
 * 读取转存记录。
 */
async function loadRecords() {
  if (!props.api) return
  loadingRecords.value = true;
  try {
    const payload = unwrap(await props.api.get(`plugin/${props.pluginId}/records`));
    records.value = payload.records || [];
  } catch (err) {
    error.value = `读取记录失败：${err?.message || err}`;
  } finally {
    loadingRecords.value = false;
  }
}

onMounted(async () => {
  await loadStatus();
  await loadCookie();
  await loadRecords();
});

return (_ctx, _cache) => {
  const _component_v_icon = _resolveComponent("v-icon");
  const _component_v_spacer = _resolveComponent("v-spacer");
  const _component_v_chip = _resolveComponent("v-chip");
  const _component_v_card_title = _resolveComponent("v-card-title");
  const _component_v_text_field = _resolveComponent("v-text-field");
  const _component_v_btn = _resolveComponent("v-btn");
  const _component_v_card_text = _resolveComponent("v-card-text");
  const _component_v_card = _resolveComponent("v-card");
  const _component_v_alert = _resolveComponent("v-alert");
  const _component_v_select = _resolveComponent("v-select");
  const _component_v_img = _resolveComponent("v-img");
  const _component_v_card_actions = _resolveComponent("v-card-actions");
  const _component_v_dialog = _resolveComponent("v-dialog");
  const _component_v_checkbox_btn = _resolveComponent("v-checkbox-btn");
  const _component_v_textarea = _resolveComponent("v-textarea");

  return (_openBlock(), _createElementBlock("div", _hoisted_1, [
    _createVNode(_component_v_card, {
      flat: "",
      class: "rounded border mb-3"
    }, {
      default: _withCtx(() => [
        _createVNode(_component_v_card_title, { class: "text-subtitle-2 d-flex align-center px-3 py-2 bg-primary-lighten-5" }, {
          default: _withCtx(() => [
            _createVNode(_component_v_icon, {
              icon: "mdi-cloud",
              class: "mr-2",
              color: "primary",
              size: "small"
            }),
            _cache[20] || (_cache[20] = _createElementVNode("span", null, "115 网盘配置", -1)),
            _createVNode(_component_v_spacer),
            _createVNode(_component_v_chip, {
              size: "small",
              variant: "tonal",
              color: status.value.p115?.authorized ? 'success' : 'warning'
            }, {
              default: _withCtx(() => [
                _createTextVNode(_toDisplayString(status.value.p115?.authorized ? `已授权（${status.value.p115?.account || '账号信息不可用'}）` : '未授权'), 1)
              ]),
              _: 1
            }, 8, ["color"])
          ]),
          _: 1
        }),
        _createVNode(_component_v_card_text, { class: "px-3 py-2" }, {
          default: _withCtx(() => [
            _createElementVNode("div", _hoisted_2, [
              _createVNode(_component_v_text_field, {
                "model-value": cookieMasked.value,
                label: "Cookie",
                variant: "outlined",
                density: "compact",
                readonly: "",
                "hide-details": "",
                style: {"min-width":"320px"},
                class: "flex-grow-1"
              }, null, 8, ["model-value"]),
              _createVNode(_component_v_btn, {
                size: "small",
                color: "primary",
                variant: "tonal",
                onClick: openQrcode115
              }, {
                default: _withCtx(() => [
                  _createVNode(_component_v_icon, {
                    icon: "mdi-qrcode-scan",
                    size: "small",
                    class: "mr-1"
                  }),
                  _cache[21] || (_cache[21] = _createTextVNode(" 扫码 ", -1))
                ]),
                _: 1
              }),
              _createVNode(_component_v_btn, {
                size: "small",
                color: "primary",
                variant: "tonal",
                onClick: openCookieDialog
              }, {
                default: _withCtx(() => [
                  _createVNode(_component_v_icon, {
                    icon: "mdi-key-variant",
                    size: "small",
                    class: "mr-1"
                  }),
                  _cache[22] || (_cache[22] = _createTextVNode(" 手动填写 ", -1))
                ]),
                _: 1
              }),
              _createVNode(_component_v_btn, {
                size: "small",
                variant: "tonal",
                loading: browsing.value,
                onClick: openBrowseDialog
              }, {
                default: _withCtx(() => [
                  _createVNode(_component_v_icon, {
                    icon: "mdi-folder-search-outline",
                    size: "small",
                    class: "mr-1"
                  }),
                  _cache[23] || (_cache[23] = _createTextVNode(" 浏览选择目录 ", -1))
                ]),
                _: 1
              }, 8, ["loading"])
            ]),
            _createElementVNode("div", _hoisted_3, [
              _createVNode(_component_v_text_field, {
                modelValue: receivePath.value,
                "onUpdate:modelValue": _cache[0] || (_cache[0] = $event => ((receivePath).value = $event)),
                label: "转存目录（115 网盘路径）",
                variant: "outlined",
                density: "compact",
                "hide-details": "",
                style: {"min-width":"260px"},
                class: "flex-grow-1"
              }, null, 8, ["modelValue"]),
              _createVNode(_component_v_btn, {
                size: "small",
                color: "primary",
                variant: "flat",
                loading: savingPath.value,
                onClick: saveReceivePath
              }, {
                default: _withCtx(() => [...(_cache[24] || (_cache[24] = [
                  _createTextVNode(" 保存目录 ", -1)
                ]))]),
                _: 1
              }, 8, ["loading"])
            ]),
            _cache[25] || (_cache[25] = _createElementVNode("div", { class: "text-caption text-medium-emphasis mt-2" }, " 转存的资源会先保存到该目录，再生成长期分享链接并写出 STRM。 ", -1))
          ]),
          _: 1
        })
      ]),
      _: 1
    }),
    _createVNode(_component_v_card, {
      flat: "",
      class: "rounded border mb-3"
    }, {
      default: _withCtx(() => [
        _createVNode(_component_v_card_title, { class: "text-subtitle-2 d-flex align-center px-3 py-2 bg-primary-lighten-5" }, {
          default: _withCtx(() => [
            _createVNode(_component_v_icon, {
              icon: "mdi-cloud-search",
              class: "mr-2",
              color: "primary",
              size: "small"
            }),
            _cache[27] || (_cache[27] = _createElementVNode("span", null, "网盘资源搜索", -1)),
            _createVNode(_component_v_spacer),
            _createElementVNode("span", _hoisted_4, _toDisplayString(status.value.search_inject_enabled ? '已并入默认搜索资源' : '仅本页搜索'), 1),
            _createVNode(_component_v_btn, {
              size: "small",
              variant: "text",
              color: "primary",
              onClick: loadStatus
            }, {
              default: _withCtx(() => [
                _createVNode(_component_v_icon, {
                  icon: "mdi-refresh",
                  size: "small",
                  class: "mr-1"
                }),
                _cache[26] || (_cache[26] = _createTextVNode(" 刷新 ", -1))
              ]),
              _: 1
            })
          ]),
          _: 1
        }),
        _createVNode(_component_v_card_text, { class: "px-3 py-2" }, {
          default: _withCtx(() => [
            (error.value)
              ? (_openBlock(), _createBlock(_component_v_alert, {
                  key: 0,
                  type: "error",
                  density: "compact",
                  variant: "tonal",
                  class: "mb-2 text-caption",
                  closable: ""
                }, {
                  default: _withCtx(() => [
                    _createTextVNode(_toDisplayString(error.value), 1)
                  ]),
                  _: 1
                }))
              : _createCommentVNode("", true),
            (message.value)
              ? (_openBlock(), _createBlock(_component_v_alert, {
                  key: 1,
                  type: "success",
                  density: "compact",
                  variant: "tonal",
                  class: "mb-2 text-caption",
                  closable: ""
                }, {
                  default: _withCtx(() => [
                    _createTextVNode(_toDisplayString(message.value), 1)
                  ]),
                  _: 1
                }))
              : _createCommentVNode("", true),
            _createElementVNode("div", _hoisted_5, [
              _createVNode(_component_v_btn, {
                size: "small",
                variant: "tonal",
                onClick: openQrcodeTelegram
              }, {
                default: _withCtx(() => [
                  _createVNode(_component_v_icon, {
                    icon: "mdi-send",
                    size: "small",
                    class: "mr-1"
                  }),
                  _cache[28] || (_cache[28] = _createTextVNode(" Telegram 扫码授权 ", -1))
                ]),
                _: 1
              }),
              _createVNode(_component_v_chip, {
                size: "small",
                variant: "tonal",
                color: status.value.telegram?.authorized ? 'success' : 'warning'
              }, {
                default: _withCtx(() => [
                  _createTextVNode(" TG " + _toDisplayString(status.value.telegram?.authorized ? '已授权' : '未授权'), 1)
                ]),
                _: 1
              }, 8, ["color"])
            ]),
            _createElementVNode("div", _hoisted_6, [
              _createVNode(_component_v_text_field, {
                modelValue: keyword.value,
                "onUpdate:modelValue": _cache[1] || (_cache[1] = $event => ((keyword).value = $event)),
                label: "搜索关键词（影片名或资源名）",
                variant: "outlined",
                density: "compact",
                "hide-details": "",
                style: {"min-width":"260px"},
                onKeyup: _withKeys(doSearch, ["enter"])
              }, null, 8, ["modelValue"]),
              _createVNode(_component_v_select, {
                modelValue: selectedSources.value,
                "onUpdate:modelValue": _cache[2] || (_cache[2] = $event => ((selectedSources).value = $event)),
                items: sourceItems.value,
                "item-title": "title",
                "item-value": "value",
                label: "搜索渠道",
                variant: "outlined",
                density: "compact",
                multiple: "",
                chips: "",
                "hide-details": "",
                style: {"min-width":"240px"}
              }, null, 8, ["modelValue", "items"]),
              _createVNode(_component_v_btn, {
                color: "primary",
                variant: "flat",
                loading: searching.value,
                onClick: doSearch
              }, {
                default: _withCtx(() => [
                  _createVNode(_component_v_icon, {
                    icon: "mdi-magnify",
                    size: "small",
                    class: "mr-1"
                  }),
                  _cache[29] || (_cache[29] = _createTextVNode(" 搜索 ", -1))
                ]),
                _: 1
              }, 8, ["loading"])
            ])
          ]),
          _: 1
        })
      ]),
      _: 1
    }),
    _createVNode(_component_v_card, {
      flat: "",
      class: "rounded border mb-3"
    }, {
      default: _withCtx(() => [
        _createVNode(_component_v_card_title, { class: "text-subtitle-2 d-flex align-center px-3 py-2 bg-primary-lighten-5" }, {
          default: _withCtx(() => [
            _createVNode(_component_v_icon, {
              icon: "mdi-link-variant",
              class: "mr-2",
              color: "primary",
              size: "small"
            }),
            _cache[30] || (_cache[30] = _createElementVNode("span", null, "115 分享链接", -1))
          ]),
          _: 1
        }),
        _createVNode(_component_v_card_text, { class: "px-3 py-2" }, {
          default: _withCtx(() => [
            _createVNode(_component_v_text_field, {
              modelValue: linkUrl.value,
              "onUpdate:modelValue": _cache[3] || (_cache[3] = $event => ((linkUrl).value = $event)),
              label: "粘贴 115 分享链接（支持带提取码）",
              placeholder: "https://115.com/s/xxxxxxx?password=xxxx",
              variant: "outlined",
              density: "compact",
              "hide-details": "",
              onKeyup: _withKeys(previewLink, ["enter"])
            }, null, 8, ["modelValue"]),
            _createElementVNode("div", _hoisted_7, [
              _createVNode(_component_v_btn, {
                size: "small",
                color: "primary",
                variant: "tonal",
                loading: linkBusy.value === 'preview',
                onClick: previewLink
              }, {
                default: _withCtx(() => [
                  _createVNode(_component_v_icon, {
                    icon: "mdi-file-search-outline",
                    size: "small",
                    class: "mr-1"
                  }),
                  _cache[31] || (_cache[31] = _createTextVNode(" 解析链接 ", -1))
                ]),
                _: 1
              }, 8, ["loading"]),
              _createVNode(_component_v_btn, {
                size: "small",
                color: "primary",
                variant: "tonal",
                loading: linkBusy.value === 'browse',
                onClick: openLinkList
              }, {
                default: _withCtx(() => [
                  _createVNode(_component_v_icon, {
                    icon: "mdi-format-list-bulleted",
                    size: "small",
                    class: "mr-1"
                  }),
                  _cache[32] || (_cache[32] = _createTextVNode(" 文件列表 ", -1))
                ]),
                _: 1
              }, 8, ["loading"]),
              _createVNode(_component_v_btn, {
                size: "small",
                color: "primary",
                variant: "flat",
                loading: linkBusy.value === 'transfer',
                onClick: transferLink
              }, {
                default: _withCtx(() => [
                  _createVNode(_component_v_icon, {
                    icon: "mdi-cloud-download",
                    size: "small",
                    class: "mr-1"
                  }),
                  _cache[33] || (_cache[33] = _createTextVNode(" 转存 ", -1))
                ]),
                _: 1
              }, 8, ["loading"]),
              _createVNode(_component_v_btn, {
                size: "small",
                color: "primary",
                variant: "flat",
                loading: linkBusy.value === 'strm',
                onClick: strmLink
              }, {
                default: _withCtx(() => [
                  _createVNode(_component_v_icon, {
                    icon: "mdi-file-link",
                    size: "small",
                    class: "mr-1"
                  }),
                  _cache[34] || (_cache[34] = _createTextVNode(" 生成 STRM ", -1))
                ]),
                _: 1
              }, 8, ["loading"]),
              (selectedFids.value.length)
                ? (_openBlock(), _createBlock(_component_v_chip, {
                    key: 0,
                    size: "small",
                    variant: "tonal",
                    closable: "",
                    "onClick:close": _cache[4] || (_cache[4] = $event => (selectedFids.value = []))
                  }, {
                    default: _withCtx(() => [
                      _createTextVNode(" 已选 " + _toDisplayString(selectedFids.value.length) + " 项 ", 1)
                    ]),
                    _: 1
                  }))
                : _createCommentVNode("", true)
            ]),
            (linkPreview.value)
              ? (_openBlock(), _createBlock(_component_v_card, {
                  key: 0,
                  flat: "",
                  class: "rounded border mt-3"
                }, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_card_text, { class: "px-3 py-2" }, {
                      default: _withCtx(() => [
                        _createElementVNode("div", _hoisted_8, _toDisplayString(linkPreview.value.title || linkPreview.value.share_code), 1),
                        _createElementVNode("div", _hoisted_9, " 文件数：" + _toDisplayString(linkPreview.value.count) + " · 总大小：" + _toDisplayString(linkPreview.value.size_text || '未知'), 1),
                        (linkPreview.value.entries?.length)
                          ? (_openBlock(), _createElementBlock("div", _hoisted_10, [
                              (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(linkPreview.value.entries, (entry) => {
                                return (_openBlock(), _createElementBlock("div", {
                                  key: entry.fid,
                                  class: "d-flex align-center text-caption py-1"
                                }, [
                                  _createVNode(_component_v_icon, {
                                    icon: entry.is_dir ? 'mdi-folder' : 'mdi-file-video-outline',
                                    size: "x-small",
                                    class: "mr-2",
                                    color: entry.is_dir ? 'amber' : 'primary'
                                  }, null, 8, ["icon", "color"]),
                                  _createElementVNode("span", _hoisted_11, _toDisplayString(entry.name), 1),
                                  _createElementVNode("span", _hoisted_12, _toDisplayString(entry.size_text), 1)
                                ]))
                              }), 128))
                            ]))
                          : _createCommentVNode("", true)
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                }))
              : _createCommentVNode("", true)
          ]),
          _: 1
        })
      ]),
      _: 1
    }),
    _createVNode(_component_v_card, {
      flat: "",
      class: "rounded border"
    }, {
      default: _withCtx(() => [
        _createVNode(_component_v_card_title, { class: "text-subtitle-2 d-flex align-center px-3 py-2 bg-primary-lighten-5" }, {
          default: _withCtx(() => [
            _createVNode(_component_v_icon, {
              icon: "mdi-link-box-variant",
              class: "mr-2",
              color: "primary",
              size: "small"
            }),
            _cache[36] || (_cache[36] = _createElementVNode("span", null, "链接管理", -1)),
            _createVNode(_component_v_spacer),
            _createVNode(_component_v_btn, {
              size: "small",
              variant: "text",
              color: "primary",
              loading: loadingRecords.value,
              onClick: loadRecords
            }, {
              default: _withCtx(() => [
                _createVNode(_component_v_icon, {
                  icon: "mdi-refresh",
                  size: "small",
                  class: "mr-1"
                }),
                _cache[35] || (_cache[35] = _createTextVNode(" 刷新 ", -1))
              ]),
              _: 1
            }, 8, ["loading"])
          ]),
          _: 1
        }),
        _createVNode(_component_v_card_text, { class: "px-3 py-2" }, {
          default: _withCtx(() => [
            (!records.value.length)
              ? (_openBlock(), _createBlock(_component_v_alert, {
                  key: 0,
                  type: "info",
                  density: "compact",
                  variant: "tonal",
                  class: "text-caption"
                }, {
                  default: _withCtx(() => [...(_cache[37] || (_cache[37] = [
                    _createTextVNode(" 暂无记录。粘贴 115 分享链接后执行「转存」或「生成 STRM」，记录会显示在这里。 ", -1)
                  ]))]),
                  _: 1
                }))
              : _createCommentVNode("", true),
            (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(records.value, (record, index) => {
              return (_openBlock(), _createBlock(_component_v_card, {
                key: index,
                flat: "",
                class: "rounded border mb-2"
              }, {
                default: _withCtx(() => [
                  _createVNode(_component_v_card_text, { class: "px-3 py-2" }, {
                    default: _withCtx(() => [
                      _createElementVNode("div", _hoisted_13, [
                        _createElementVNode("span", _hoisted_14, _toDisplayString(record.title || record.share_url), 1),
                        _createVNode(_component_v_chip, {
                          size: "x-small",
                          variant: "tonal",
                          class: "ml-2"
                        }, {
                          default: _withCtx(() => [
                            _createTextVNode(_toDisplayString(record.source === 'link' ? '手动链接' : record.source), 1)
                          ]),
                          _: 2
                        }, 1024),
                        (record.result?.total)
                          ? (_openBlock(), _createBlock(_component_v_chip, {
                              key: 0,
                              size: "x-small",
                              variant: "tonal",
                              color: "primary",
                              class: "ml-2"
                            }, {
                              default: _withCtx(() => [
                                _createTextVNode(" STRM " + _toDisplayString(record.result.total) + " 个 ", 1)
                              ]),
                              _: 2
                            }, 1024))
                          : _createCommentVNode("", true),
                        (isPermanent(record))
                          ? (_openBlock(), _createBlock(_component_v_chip, {
                              key: 1,
                              size: "x-small",
                              variant: "tonal",
                              color: "success",
                              class: "ml-2"
                            }, {
                              default: _withCtx(() => [...(_cache[38] || (_cache[38] = [
                                _createTextVNode(" 长期有效 ", -1)
                              ]))]),
                              _: 1
                            }))
                          : _createCommentVNode("", true)
                      ]),
                      _createElementVNode("div", _hoisted_15, _toDisplayString(record.result?.share_link || record.share_url), 1),
                      (record.result?.output_path)
                        ? (_openBlock(), _createElementBlock("div", _hoisted_16, " 输出目录：" + _toDisplayString(record.result.output_path), 1))
                        : _createCommentVNode("", true),
                      _createElementVNode("div", _hoisted_17, [
                        _createVNode(_component_v_btn, {
                          size: "x-small",
                          variant: "tonal",
                          onClick: $event => (copyText(record.result?.share_link || record.share_url))
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_v_icon, {
                              icon: "mdi-content-copy",
                              size: "x-small",
                              class: "mr-1"
                            }),
                            _cache[39] || (_cache[39] = _createTextVNode(" 复制链接 ", -1))
                          ]),
                          _: 1
                        }, 8, ["onClick"]),
                        _createVNode(_component_v_btn, {
                          size: "x-small",
                          variant: "tonal",
                          onClick: $event => (useRecord(record))
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_v_icon, {
                              icon: "mdi-arrow-up-bold-box-outline",
                              size: "x-small",
                              class: "mr-1"
                            }),
                            _cache[40] || (_cache[40] = _createTextVNode(" 填入链接 ", -1))
                          ]),
                          _: 1
                        }, 8, ["onClick"]),
                        _createVNode(_component_v_btn, {
                          size: "x-small",
                          variant: "tonal",
                          loading: recordBusy.value === index,
                          onClick: $event => (regenerate(record, index))
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_v_icon, {
                              icon: "mdi-file-link",
                              size: "x-small",
                              class: "mr-1"
                            }),
                            _cache[41] || (_cache[41] = _createTextVNode(" 生成 STRM ", -1))
                          ]),
                          _: 1
                        }, 8, ["loading", "onClick"]),
                        _createVNode(_component_v_btn, {
                          size: "x-small",
                          variant: "text",
                          color: "error",
                          onClick: $event => (removeRecord(index))
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_v_icon, {
                              icon: "mdi-delete-outline",
                              size: "x-small",
                              class: "mr-1"
                            }),
                            _cache[42] || (_cache[42] = _createTextVNode(" 移除记录 ", -1))
                          ]),
                          _: 1
                        }, 8, ["onClick"])
                      ])
                    ]),
                    _: 2
                  }, 1024)
                ]),
                _: 2
              }, 1024))
            }), 128))
          ]),
          _: 1
        })
      ]),
      _: 1
    }),
    (results.value.length)
      ? (_openBlock(), _createBlock(_component_v_card, {
          key: 0,
          flat: "",
          class: "rounded border mt-3"
        }, {
          default: _withCtx(() => [
            _createVNode(_component_v_card_title, { class: "text-subtitle-2 px-3 py-2 bg-primary-lighten-5" }, {
              default: _withCtx(() => [
                _createTextVNode(" 搜索结果（" + _toDisplayString(results.value.length) + "） ", 1)
              ]),
              _: 1
            }),
            _createVNode(_component_v_card_text, { class: "px-3 py-2" }, {
              default: _withCtx(() => [
                (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(results.value, (item, index) => {
                  return (_openBlock(), _createBlock(_component_v_card, {
                    key: index,
                    flat: "",
                    class: "rounded border mb-2"
                  }, {
                    default: _withCtx(() => [
                      _createVNode(_component_v_card_text, { class: "px-3 py-2" }, {
                        default: _withCtx(() => [
                          _createElementVNode("div", _hoisted_18, _toDisplayString(item.title || item.share_url), 1),
                          _createElementVNode("div", _hoisted_19, [
                            _createTextVNode(" 来源：" + _toDisplayString(item.source) + " · 网盘：" + _toDisplayString(item.resource_type || '未知') + " ", 1),
                            (item.size_text)
                              ? (_openBlock(), _createElementBlock("span", _hoisted_20, " · 大小：" + _toDisplayString(item.size_text), 1))
                              : _createCommentVNode("", true),
                            (item.access_code)
                              ? (_openBlock(), _createElementBlock("span", _hoisted_21, " · 提取码：" + _toDisplayString(item.access_code), 1))
                              : _createCommentVNode("", true),
                            (item.channel)
                              ? (_openBlock(), _createElementBlock("span", _hoisted_22, " · 频道：" + _toDisplayString(item.channel), 1))
                              : _createCommentVNode("", true)
                          ]),
                          _createElementVNode("div", _hoisted_23, [
                            _createVNode(_component_v_btn, {
                              size: "small",
                              variant: "text",
                              onClick: $event => (useLink(item))
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_v_icon, {
                                  icon: "mdi-arrow-up-bold-box-outline",
                                  size: "small",
                                  class: "mr-1"
                                }),
                                _cache[43] || (_cache[43] = _createTextVNode(" 填入链接 ", -1))
                              ]),
                              _: 1
                            }, 8, ["onClick"]),
                            _createVNode(_component_v_btn, {
                              size: "small",
                              color: "primary",
                              variant: "tonal",
                              loading: transferringIndex.value === index,
                              onClick: $event => (transfer(item, index))
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_v_icon, {
                                  icon: "mdi-cloud-download",
                                  size: "small",
                                  class: "mr-1"
                                }),
                                _cache[44] || (_cache[44] = _createTextVNode(" 转存并生成 STRM ", -1))
                              ]),
                              _: 1
                            }, 8, ["loading", "onClick"])
                          ])
                        ]),
                        _: 2
                      }, 1024)
                    ]),
                    _: 2
                  }, 1024))
                }), 128))
              ]),
              _: 1
            })
          ]),
          _: 1
        }))
      : _createCommentVNode("", true),
    _createVNode(_component_v_dialog, {
      modelValue: qrcodeDialog.value,
      "onUpdate:modelValue": _cache[6] || (_cache[6] = $event => ((qrcodeDialog).value = $event)),
      "max-width": "420"
    }, {
      default: _withCtx(() => [
        _createVNode(_component_v_card, null, {
          default: _withCtx(() => [
            _createVNode(_component_v_card_title, { class: "text-subtitle-2 d-flex align-center" }, {
              default: _withCtx(() => [
                _createVNode(_component_v_icon, {
                  icon: "mdi-qrcode-scan",
                  class: "mr-2",
                  size: "small",
                  color: "primary"
                }),
                _createTextVNode(" " + _toDisplayString(qrcodeTitle.value) + " ", 1),
                _createVNode(_component_v_spacer),
                _createVNode(_component_v_btn, {
                  icon: "mdi-close",
                  variant: "text",
                  size: "small",
                  onClick: closeQrcode
                })
              ]),
              _: 1
            }),
            _createVNode(_component_v_card_text, { class: "text-center" }, {
              default: _withCtx(() => [
                (qrcodeImage.value)
                  ? (_openBlock(), _createBlock(_component_v_img, {
                      key: 0,
                      src: qrcodeImage.value,
                      width: "280",
                      height: "280",
                      class: "mx-auto my-2",
                      contain: ""
                    }, null, 8, ["src"]))
                  : (_openBlock(), _createElementBlock("div", _hoisted_24, " 二维码未加载：" + _toDisplayString(qrcodeHint.value || '请点击刷新'), 1)),
                _createElementVNode("div", _hoisted_25, _toDisplayString(qrcodeHint.value), 1),
                _createVNode(_component_v_btn, {
                  size: "small",
                  variant: "tonal",
                  loading: qrcodeLoading.value,
                  onClick: refreshQrcode
                }, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_icon, {
                      icon: "mdi-refresh",
                      size: "small",
                      class: "mr-1"
                    }),
                    _cache[45] || (_cache[45] = _createTextVNode(" 刷新二维码 ", -1))
                  ]),
                  _: 1
                }, 8, ["loading"]),
                (qrcodeContent.value)
                  ? (_openBlock(), _createBlock(_component_v_text_field, {
                      key: 2,
                      "model-value": qrcodeContent.value,
                      label: 
              qrcodeMode.value === 'telegram'
                ? '登录链接（可在 Telegram App 内打开）'
                : '二维码内容（扫码不可用时可在 115 App 内打开）'
            ,
                      variant: "outlined",
                      density: "compact",
                      readonly: "",
                      "hide-details": "",
                      class: "mt-3 text-left"
                    }, null, 8, ["model-value", "label"]))
                  : _createCommentVNode("", true),
                (telegramPasswordRequired.value)
                  ? (_openBlock(), _createBlock(_component_v_text_field, {
                      key: 3,
                      modelValue: telegramPassword.value,
                      "onUpdate:modelValue": _cache[5] || (_cache[5] = $event => ((telegramPassword).value = $event)),
                      label: "两步验证密码",
                      type: "password",
                      variant: "outlined",
                      density: "compact",
                      class: "mt-3 text-left"
                    }, null, 8, ["modelValue"]))
                  : _createCommentVNode("", true)
              ]),
              _: 1
            }),
            _createVNode(_component_v_card_actions, null, {
              default: _withCtx(() => [
                _createVNode(_component_v_btn, {
                  variant: "text",
                  onClick: closeQrcode
                }, {
                  default: _withCtx(() => [...(_cache[46] || (_cache[46] = [
                    _createTextVNode("关闭", -1)
                  ]))]),
                  _: 1
                }),
                _createVNode(_component_v_spacer),
                _createVNode(_component_v_btn, {
                  color: "primary",
                  variant: "flat",
                  loading: polling.value,
                  onClick: pollQrcode
                }, {
                  default: _withCtx(() => [
                    _createTextVNode(_toDisplayString(qrcodeMode.value === 'telegram' ? '我已扫码' : '检查状态'), 1)
                  ]),
                  _: 1
                }, 8, ["loading"])
              ]),
              _: 1
            })
          ]),
          _: 1
        })
      ]),
      _: 1
    }, 8, ["modelValue"]),
    _createVNode(_component_v_dialog, {
      modelValue: listDialog.value,
      "onUpdate:modelValue": _cache[10] || (_cache[10] = $event => ((listDialog).value = $event)),
      "max-width": "720"
    }, {
      default: _withCtx(() => [
        _createVNode(_component_v_card, null, {
          default: _withCtx(() => [
            _createVNode(_component_v_card_title, { class: "text-subtitle-2 d-flex align-center" }, {
              default: _withCtx(() => [
                _createVNode(_component_v_icon, {
                  icon: "mdi-folder-open",
                  class: "mr-2",
                  size: "small",
                  color: "primary"
                }),
                _cache[48] || (_cache[48] = _createElementVNode("span", null, "文件列表", -1)),
                _createVNode(_component_v_spacer),
                (browseStack.value.length > 1)
                  ? (_openBlock(), _createBlock(_component_v_btn, {
                      key: 0,
                      size: "small",
                      variant: "text",
                      onClick: browseUp
                    }, {
                      default: _withCtx(() => [...(_cache[47] || (_cache[47] = [
                        _createTextVNode("上级", -1)
                      ]))]),
                      _: 1
                    }))
                  : _createCommentVNode("", true),
                _createVNode(_component_v_btn, {
                  icon: "mdi-close",
                  variant: "text",
                  size: "small",
                  onClick: _cache[7] || (_cache[7] = $event => (listDialog.value = false))
                })
              ]),
              _: 1
            }),
            _createVNode(_component_v_card_text, { style: {"max-height":"60vh","overflow-y":"auto"} }, {
              default: _withCtx(() => [
                _createElementVNode("div", _hoisted_26, [
                  _createTextVNode(" 当前目录：" + _toDisplayString(browseStack.value.length ? browseStack.value[browseStack.value.length - 1].name : '根目录') + " ", 1),
                  (listSizeText.value)
                    ? (_openBlock(), _createElementBlock("span", _hoisted_27, " · 本层大小 " + _toDisplayString(listSizeText.value), 1))
                    : _createCommentVNode("", true)
                ]),
                (!listEntries.value.length)
                  ? (_openBlock(), _createBlock(_component_v_alert, {
                      key: 0,
                      type: "info",
                      density: "compact",
                      variant: "tonal",
                      class: "text-caption"
                    }, {
                      default: _withCtx(() => [...(_cache[49] || (_cache[49] = [
                        _createTextVNode(" 该目录为空 ", -1)
                      ]))]),
                      _: 1
                    }))
                  : _createCommentVNode("", true),
                (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(listEntries.value, (entry) => {
                  return (_openBlock(), _createElementBlock("div", {
                    key: entry.fid,
                    class: "d-flex align-center py-1"
                  }, [
                    (!entry.is_dir)
                      ? (_openBlock(), _createBlock(_component_v_checkbox_btn, {
                          key: 0,
                          "model-value": selectedFids.value.includes(entry.fid),
                          density: "compact",
                          "hide-details": "",
                          class: "mr-1",
                          "onUpdate:modelValue": (v) => toggleFid(entry.fid, v)
                        }, null, 8, ["model-value", "onUpdate:modelValue"]))
                      : _createCommentVNode("", true),
                    _createVNode(_component_v_icon, {
                      icon: entry.is_dir ? 'mdi-folder' : 'mdi-file-video-outline',
                      size: "small",
                      class: "mr-2",
                      color: entry.is_dir ? 'amber' : 'primary'
                    }, null, 8, ["icon", "color"]),
                    _createElementVNode("span", _hoisted_28, _toDisplayString(entry.name), 1),
                    _createElementVNode("span", _hoisted_29, _toDisplayString(entry.size_text), 1),
                    (entry.is_dir)
                      ? (_openBlock(), _createBlock(_component_v_btn, {
                          key: 1,
                          size: "x-small",
                          variant: "text",
                          onClick: $event => (browseInto(entry))
                        }, {
                          default: _withCtx(() => [...(_cache[50] || (_cache[50] = [
                            _createTextVNode("进入", -1)
                          ]))]),
                          _: 1
                        }, 8, ["onClick"]))
                      : _createCommentVNode("", true)
                  ]))
                }), 128))
              ]),
              _: 1
            }),
            _createVNode(_component_v_card_actions, null, {
              default: _withCtx(() => [
                _createVNode(_component_v_btn, {
                  variant: "text",
                  onClick: _cache[8] || (_cache[8] = $event => (listDialog.value = false))
                }, {
                  default: _withCtx(() => [...(_cache[51] || (_cache[51] = [
                    _createTextVNode("关闭", -1)
                  ]))]),
                  _: 1
                }),
                _createVNode(_component_v_spacer),
                _createVNode(_component_v_btn, {
                  variant: "text",
                  onClick: _cache[9] || (_cache[9] = $event => (selectedFids.value = []))
                }, {
                  default: _withCtx(() => [...(_cache[52] || (_cache[52] = [
                    _createTextVNode("清空选择", -1)
                  ]))]),
                  _: 1
                }),
                _createVNode(_component_v_btn, {
                  color: "primary",
                  variant: "flat",
                  loading: linkBusy.value === 'transfer',
                  onClick: transferLink
                }, {
                  default: _withCtx(() => [...(_cache[53] || (_cache[53] = [
                    _createTextVNode("转存选中", -1)
                  ]))]),
                  _: 1
                }, 8, ["loading"]),
                _createVNode(_component_v_btn, {
                  color: "primary",
                  variant: "flat",
                  loading: linkBusy.value === 'strm',
                  onClick: strmLink
                }, {
                  default: _withCtx(() => [...(_cache[54] || (_cache[54] = [
                    _createTextVNode("生成 STRM", -1)
                  ]))]),
                  _: 1
                }, 8, ["loading"])
              ]),
              _: 1
            })
          ]),
          _: 1
        })
      ]),
      _: 1
    }, 8, ["modelValue"]),
    _createVNode(_component_v_dialog, {
      modelValue: browseDialog.value,
      "onUpdate:modelValue": _cache[15] || (_cache[15] = $event => ((browseDialog).value = $event)),
      "max-width": "620"
    }, {
      default: _withCtx(() => [
        _createVNode(_component_v_card, null, {
          default: _withCtx(() => [
            _createVNode(_component_v_card_title, { class: "text-subtitle-2 d-flex align-center" }, {
              default: _withCtx(() => [
                _createVNode(_component_v_icon, {
                  icon: "mdi-folder-search-outline",
                  class: "mr-2",
                  size: "small",
                  color: "primary"
                }),
                _cache[55] || (_cache[55] = _createElementVNode("span", null, "选择 115 转存目录", -1)),
                _createVNode(_component_v_spacer),
                _createVNode(_component_v_btn, {
                  icon: "mdi-close",
                  variant: "text",
                  size: "small",
                  onClick: _cache[11] || (_cache[11] = $event => (browseDialog.value = false))
                })
              ]),
              _: 1
            }),
            _createVNode(_component_v_card_text, { style: {"max-height":"55vh","overflow-y":"auto"} }, {
              default: _withCtx(() => [
                _createElementVNode("div", _hoisted_30, " 当前路径：" + _toDisplayString(drivePath.value || '/'), 1),
                (drivePath.value)
                  ? (_openBlock(), _createBlock(_component_v_btn, {
                      key: 0,
                      size: "small",
                      variant: "text",
                      class: "mb-2",
                      onClick: _cache[12] || (_cache[12] = $event => (browseDrive('', 0)))
                    }, {
                      default: _withCtx(() => [...(_cache[56] || (_cache[56] = [
                        _createTextVNode(" 返回根目录 ", -1)
                      ]))]),
                      _: 1
                    }))
                  : _createCommentVNode("", true),
                (!driveFolders.value.length)
                  ? (_openBlock(), _createBlock(_component_v_alert, {
                      key: 1,
                      type: "info",
                      density: "compact",
                      variant: "tonal",
                      class: "text-caption"
                    }, {
                      default: _withCtx(() => [...(_cache[57] || (_cache[57] = [
                        _createTextVNode(" 没有子目录 ", -1)
                      ]))]),
                      _: 1
                    }))
                  : _createCommentVNode("", true),
                (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(driveFolders.value, (folder) => {
                  return (_openBlock(), _createElementBlock("div", {
                    key: folder.fid,
                    class: "d-flex align-center py-1"
                  }, [
                    _createVNode(_component_v_icon, {
                      icon: "mdi-folder",
                      size: "small",
                      color: "amber",
                      class: "mr-2"
                    }),
                    _createElementVNode("span", _hoisted_31, _toDisplayString(folder.name), 1),
                    _createVNode(_component_v_btn, {
                      size: "x-small",
                      variant: "text",
                      onClick: $event => (browseDrive(joinPath(drivePath.value, folder.name), Number(folder.fid)))
                    }, {
                      default: _withCtx(() => [...(_cache[58] || (_cache[58] = [
                        _createTextVNode("进入", -1)
                      ]))]),
                      _: 1
                    }, 8, ["onClick"]),
                    _createVNode(_component_v_btn, {
                      size: "x-small",
                      variant: "text",
                      color: "primary",
                      onClick: $event => (pickDriveFolder(joinPath(drivePath.value, folder.name)))
                    }, {
                      default: _withCtx(() => [...(_cache[59] || (_cache[59] = [
                        _createTextVNode("选择", -1)
                      ]))]),
                      _: 1
                    }, 8, ["onClick"])
                  ]))
                }), 128))
              ]),
              _: 1
            }),
            _createVNode(_component_v_card_actions, null, {
              default: _withCtx(() => [
                _createVNode(_component_v_btn, {
                  variant: "text",
                  onClick: _cache[13] || (_cache[13] = $event => (browseDialog.value = false))
                }, {
                  default: _withCtx(() => [...(_cache[60] || (_cache[60] = [
                    _createTextVNode("关闭", -1)
                  ]))]),
                  _: 1
                }),
                _createVNode(_component_v_spacer),
                _createVNode(_component_v_btn, {
                  color: "primary",
                  variant: "flat",
                  onClick: _cache[14] || (_cache[14] = $event => (pickDriveFolder(drivePath.value || '/')))
                }, {
                  default: _withCtx(() => [...(_cache[61] || (_cache[61] = [
                    _createTextVNode("选择当前目录", -1)
                  ]))]),
                  _: 1
                })
              ]),
              _: 1
            })
          ]),
          _: 1
        })
      ]),
      _: 1
    }, 8, ["modelValue"]),
    _createVNode(_component_v_dialog, {
      modelValue: cookieDialog.value,
      "onUpdate:modelValue": _cache[19] || (_cache[19] = $event => ((cookieDialog).value = $event)),
      "max-width": "560"
    }, {
      default: _withCtx(() => [
        _createVNode(_component_v_card, null, {
          default: _withCtx(() => [
            _createVNode(_component_v_card_title, { class: "text-subtitle-2 d-flex align-center" }, {
              default: _withCtx(() => [
                _createVNode(_component_v_icon, {
                  icon: "mdi-key-variant",
                  class: "mr-2",
                  size: "small",
                  color: "primary"
                }),
                _cache[62] || (_cache[62] = _createTextVNode(" 115 Cookie ", -1)),
                _createVNode(_component_v_spacer),
                _createVNode(_component_v_btn, {
                  icon: "mdi-close",
                  variant: "text",
                  size: "small",
                  onClick: _cache[16] || (_cache[16] = $event => (cookieDialog.value = false))
                })
              ]),
              _: 1
            }),
            _createVNode(_component_v_card_text, null, {
              default: _withCtx(() => [
                _createElementVNode("div", _hoisted_32, " 当前状态：" + _toDisplayString(cookieInfo.value.authorized ? `已授权（${cookieInfo.value.account || '账号信息不可用'}）` : '未授权'), 1),
                _createVNode(_component_v_text_field, {
                  "model-value": cookieInfo.value.cookie_masked || '未设置',
                  label: "当前 Cookie（脱敏）",
                  variant: "outlined",
                  density: "compact",
                  readonly: "",
                  "hide-details": ""
                }, null, 8, ["model-value"]),
                _createVNode(_component_v_textarea, {
                  modelValue: cookieInput.value,
                  "onUpdate:modelValue": _cache[17] || (_cache[17] = $event => ((cookieInput).value = $event)),
                  label: "粘贴新的 Cookie",
                  variant: "outlined",
                  density: "compact",
                  rows: "4",
                  class: "mt-3",
                  placeholder: "UID=...; CID=...; SEID=...; KID=..."
                }, null, 8, ["modelValue"])
              ]),
              _: 1
            }),
            _createVNode(_component_v_card_actions, null, {
              default: _withCtx(() => [
                _createVNode(_component_v_btn, {
                  variant: "text",
                  onClick: _cache[18] || (_cache[18] = $event => (cookieDialog.value = false))
                }, {
                  default: _withCtx(() => [...(_cache[63] || (_cache[63] = [
                    _createTextVNode("关闭", -1)
                  ]))]),
                  _: 1
                }),
                _createVNode(_component_v_spacer),
                _createVNode(_component_v_btn, {
                  color: "primary",
                  variant: "flat",
                  loading: cookieSaving.value,
                  onClick: saveCookie
                }, {
                  default: _withCtx(() => [...(_cache[64] || (_cache[64] = [
                    _createTextVNode("保存并校验", -1)
                  ]))]),
                  _: 1
                }, 8, ["loading"])
              ]),
              _: 1
            })
          ]),
          _: 1
        })
      ]),
      _: 1
    }, 8, ["modelValue"])
  ]))
}
}

};

export { _sfc_main as _ };
